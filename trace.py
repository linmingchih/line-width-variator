import numpy as np
import matplotlib.pyplot as plt

SENTINEL_Y = 1.7976931348623157e+308

# -----------------------------
# 1) Arc-height -> dense polyline (arc as many segments)
# -----------------------------
def _wrap_to_pi(x):
    return (x + np.pi) % (2*np.pi) - np.pi

def _arc_points_from_sagitta(p0, p1, h, ds_target=2e-4, max_pts=2000):
    """
    Generate dense points approximating the circular arc defined by endpoints p0,p1 and sagitta h.
    Output: polyline points along that arc (includes endpoints).
    """
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    h  = float(h)

    chord = p1 - p0
    L = np.linalg.norm(chord)
    if L == 0:
        return np.array([p0])
    if abs(h) < 1e-20:
        return np.array([p0, p1])

    t = chord / L
    n_left = np.array([-t[1], t[0]])  # left normal of chord
    sgn = 1.0 if h > 0 else -1.0
    h0 = abs(h)

    # radius from sagitta
    R = (L * L) / (8.0 * h0) + (h0 / 2.0)

    mid = 0.5 * (p0 + p1)
    a = R - h0  # center offset from chord midpoint
    c = mid + sgn * a * n_left

    v0 = p0 - c
    v1 = p1 - c
    ang0 = np.arctan2(v0[1], v0[0])
    ang1 = np.arctan2(v1[1], v1[0])

    d = _wrap_to_pi(ang1 - ang0)
    # choose correct sweep direction so that arc bulges to correct side
    candidates = [d, d + 2*np.pi, d - 2*np.pi]
    best_dd, best_err = None, None
    for dd in candidates:
        angm = ang0 + 0.5*dd
        pm = c + R*np.array([np.cos(angm), np.sin(angm)])
        side = np.dot(pm - mid, n_left)  # left positive
        err = abs(side - sgn*h0)
        if best_err is None or err < best_err:
            best_err = err
            best_dd = dd

    dtheta = best_dd
    arc_len = abs(dtheta) * R
    nseg = int(np.clip(np.ceil(arc_len / ds_target), 8, max_pts))
    thetas = np.linspace(ang0, ang0 + dtheta, nseg)
    return c + R*np.column_stack([np.cos(thetas), np.sin(thetas)])

def densify_path_with_arc_height(raw_pts, ds_arc=2e-4):
    """
    Parse your mixed format:
      - normal point: [x, y]
      - arc marker : [h, SENTINEL_Y]  (h is signed sagitta)
    Return: dense centerline points (polyline).
    """
    pts = np.asarray(raw_pts, float)
    out = []

    def prev_normal(i):
        j = i - 1
        while j >= 0 and pts[j,1] == SENTINEL_Y:
            j -= 1
        return j

    def next_normal(i):
        j = i + 1
        while j < len(pts) and pts[j,1] == SENTINEL_Y:
            j += 1
        return j

    for i, (x, y) in enumerate(pts):
        if y != SENTINEL_Y:
            if (not out) or (np.linalg.norm(np.asarray(out[-1]) - pts[i]) > 1e-15):
                out.append(pts[i].tolist())
            continue

        ip, inx = prev_normal(i), next_normal(i)
        if ip < 0 or inx >= len(pts):
            continue

        arc_pts = _arc_points_from_sagitta(pts[ip], pts[inx], x, ds_target=ds_arc)
        for p in arc_pts:
            if out and np.linalg.norm(np.asarray(out[-1]) - p) < 1e-15:
                continue
            out.append(p.tolist())

    return np.asarray(out, float)

# -----------------------------
# 2) Arc-length resample (uniform s)
# -----------------------------
def arc_length(points):
    ds = np.linalg.norm(np.diff(points, axis=0), axis=1)
    return np.concatenate([[0.0], np.cumsum(ds)])

def resample_by_arclength(points, n_samples=1200):
    pts = np.asarray(points, float)
    s = arc_length(pts)
    s_new = np.linspace(0, s[-1], n_samples)
    x_new = np.interp(s_new, s, pts[:,0])
    y_new = np.interp(s_new, s, pts[:,1])
    return np.column_stack([x_new, y_new]), s_new

# -----------------------------
# 3) Fast spatial random width field (FFT method)
#    (same μ, σ, Lc; different "model" shapes)
# -----------------------------
def width_random_field_fft(s, mu, sigma, Lc, model="exponential", seed=0):
    """
    Generate w(s) on uniform grid s using spectral shaping.
    This is fast: O(N log N). Good for large N.
    """
    rng = np.random.default_rng(seed)
    s = np.asarray(s, float)
    n = len(s)
    ds = s[1] - s[0]  # assume uniform
    k = np.fft.rfftfreq(n, d=ds)  # cycles per unit length

    # characteristic cutoff ~ 1/Lc
    kc = 1.0 / max(Lc, 1e-30)

    # Shape function H(k) (amplitude shaping)
    # Note: these are practical engineering shapes that yield the intended "smoothness" differences.
    if model == "band_limited":
        H = (np.abs(k) <= kc).astype(float)

    elif model == "gaussian":
        # very smooth
        H = np.exp(-(k / kc)**2)

    elif model == "exponential":
        # rougher than gaussian
        H = 1.0 / np.sqrt(1.0 + (k / kc)**2)

    elif model == "matern32":
        # between exponential and gaussian
        H = 1.0 / (1.0 + (k / kc)**2)

    else:
        raise ValueError("model must be: exponential|gaussian|matern32|band_limited")

    # White noise in frequency (complex), shape, then iFFT
    re = rng.standard_normal(len(k))
    im = rng.standard_normal(len(k))
    X = (re + 1j * im) * H
    x = np.fft.irfft(X, n=n)

    # normalize to target mean/std
    x = x - np.mean(x)
    x = x / (np.std(x) + 1e-30)
    w = mu + sigma * x
    return w

# -----------------------------
# 4) Build trace polygon from centerline + width(s)
# -----------------------------
def trace_polygon(centerline, width):
    centerline = np.asarray(centerline, float)
    width = np.asarray(width, float)

    tang = np.gradient(centerline, axis=0)
    tang = tang / np.linalg.norm(tang, axis=1)[:,None]
    normal = np.column_stack([-tang[:,1], tang[:,0]])

    left  = centerline + normal*(width[:,None]/2)
    right = centerline - normal*(width[:,None]/2)

    polygon = np.vstack([left, right[::-1]])
    return polygon, left, right

# -----------------------------
# 5) Main function you asked for
# -----------------------------
def build_trace(
    path_pts,
    mu_w,
    sigma_w,
    L_c,
    model="matern32",
    ds_arc=2e-4,        # smaller => arc looks smoother (more points)
    n_resample=1200,    # larger => smoother width mapping + polygon
    seed=0,
    w_min=None,
    w_max=None,
    plot=True,
):
    """
    Inputs:
      1) path_pts: list[[x,y], ...] with sentinel arc-height points
      2) μ_w, σ_w, L_c
      3) model: exponential|gaussian|matern32|band_limited
    Outputs:
      1) polygon points (Mx2)
      2) (s, w_s) width variation with distance
      3) centerline (Nx2) resampled
      4) dense_centerline (Kx2) (arc already densified)
    """

    # A) arc-height -> dense polyline
    dense_centerline = densify_path_with_arc_height(path_pts, ds_arc=ds_arc)

    # B) uniform resample by arc-length
    centerline, s = resample_by_arclength(dense_centerline, n_samples=n_resample)

    # C) width field on uniform s (FAST)
    w_s = width_random_field_fft(s, mu_w, sigma_w, L_c, model=model, seed=seed)

    # optional clamp (process limits)
    if (w_min is not None) or (w_max is not None):
        lo = -np.inf if w_min is None else w_min
        hi =  np.inf if w_max is None else w_max
        w_s = np.clip(w_s, lo, hi)

    # D) polygon
    polygon, left, right = trace_polygon(centerline, w_s)

    # E) plots
    if plot:
        fig, ax = plt.subplots(figsize=(6,8))
        ax.plot(dense_centerline[:,0], dense_centerline[:,1], lw=1.0, label="Dense centerline (arc≈segments)")
        ax.plot(polygon[:,0], polygon[:,1], lw=1.1, label="Trace polygon")
        ax.set_aspect("equal", adjustable="box")  # same x,y scale
        ax.set_title(f"Trace polygon (model={model})")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True)
        ax.legend()
        plt.show()

        plt.figure(figsize=(8,3))
        plt.plot(s, w_s)
        plt.title("Width variation vs distance")
        plt.xlabel("Arc-length s")
        plt.ylabel("w(s)")
        plt.grid(True)
        plt.show()

    return polygon, (s, w_s), centerline, dense_centerline
