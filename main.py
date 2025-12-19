from pyedb import Edb
from trace import build_trace

edb_path = "../examples/pcb.aedb"

edb = Edb(edb_path, version='2024.1')

x = edb.nets.nets['D85_LEOPARD_PCIE_TX_DP3'].primitives[0]

pts = x.center_line
w=x.width

poly, (s, w_s), cl, dense = build_trace(
    path_pts=pts,          # 你貼的那串 list
    mu_w=w,
    sigma_w=0.00002,
    L_c=0.002,
    model="matern32",           # or exponential/gaussian/band_limited
    ds_arc=2e-4,                # 弧不夠圓就改小：1e-4、5e-5...
    n_resample=1200,
    seed=7,
    w_min=8e-5,                 # 可選：製程下限
    w_max=2e-4,                 # 可選：製程上限
    plot=True
)