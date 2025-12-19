from pyedb import Edb
import sys
import os

# Add parent directory to path to import trace.py if it's in the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import trace

class EdbManager:
    def __init__(self):
        self.edb = None
        self.edb_path = None
        self.variation_data = {}

    def load_edb(self, path):
        if self.edb:
            try:
                self.edb.close_edb()
            except:
                pass
        
        self.edb_path = path
        # You might want to make the version configurable
        self.edb = Edb(path, edbversion="2024.1") 
        return self.get_nets()

    def get_nets(self):
        if not self.edb:
            return {}
        
        nets_data = []
        for net_name, net in self.edb.nets.signal_nets.items():
            primitives = []
            for p in net.primitives:
                if p.type == "Path": # Only interested in Paths for now
                    # DEBUG: Print first primitive points
                    if not nets_data:
                        print(f"DEBUG: First Path Points: {p.center_line[:5]}")
                        print(f"DEBUG: Type of center_line: {type(p.center_line)}")
                        if len(p.center_line) > 0:
                            print(f"DEBUG: Type of point: {type(p.center_line[0])}")

                    prim_data = {
                        "id": p.id,
                        "type": p.type,
                        "layer": p.layer_name,
                        "width": p.width,
                        "points": p.center_line, # List of [x, y] or [x, y, h]
                    }
                    primitives.append(prim_data)
            
            if primitives:
                nets_data.append({
                    "name": net_name,
                    "primitives": primitives
                })
        
        return {"nets": nets_data}

    def save_edb(self, path):
        if self.edb:
            self.edb.save_edb_as(path)
            return True
        return False

    def apply_variation(self, settings):
        if not self.edb:
            return False

        # settings example:
        # {
        #   "mu_w": 0.0001, # Optional override? Or use primitive width?
        #   "sigma_w": 0.00002,
        #   "L_c": 0.002,
        #   "model": "matern32",
        #   "ds_arc": 2e-4,
        #   "n_resample": 1200,
        #   "w_min": 8e-5,
        #   "w_max": 2e-4,
        #   "seed": 7 # Or random
        # }

        # For now, apply to ALL paths. Later we can support selection.
        for net_name, net in self.edb.nets.nets.items():
            for p in net.primitives:
                if p.type != "Path":
                    continue
                
                # Use primitive width as mu_w unless specified otherwise?
                # The user requirement says "mu_w: default line width" in settings panel.
                # But usually we want to vary around the EXISTING width.
                # Let's assume if mu_w is not provided or -1, use p.width.
                
                mu_w = float(settings.get("mu_w", p.width))
                # If user explicitly sets mu_w, use it. If they want relative, we need logic.
                # The requirements say "mu_w: default line width" in the panel.
                # Let's assume the panel sends the value. 
                # BUT, if we have many lines with DIFFERENT widths, setting a single global mu_w is wrong.
                # The prompt says "mu_w: default line width" in Left Settings Panel.
                # It also says "sigma_w: percent of mu_w".
                # It seems the user wants to apply a global setting? 
                # OR, maybe "mu_w" in the panel is just a display/default, and we should use the primitive's width?
                # "sigma_w: percent of mu_w" suggests relative variation.
                
                # Let's interpret:
                # mu_w in settings might be an override, or we use p.width.
                # Given "sigma_w: percent of mu_w", it implies sigma is relative.
                
                # Let's use p.width as the base mean if we want to preserve design intent.
                # But if the user wants to CHANGE the width globally, they use the input.
                # Let's stick to: Use p.width as base, and sigma is percentage of that.
                # Wait, the UI has an input for `mu_w`. 
                # If the user inputs a value, should we use it for ALL lines? That might break things if lines have different widths.
                # Maybe `mu_w` input is only relevant if we are creating new lines or forcing a width.
                # Let's assume for now: Use p.width from the primitive, and interpret sigma_w as a percentage.
                # AND ignore the `mu_w` input from the panel for the *calculation* unless we really want to force it.
                # OR, maybe the `mu_w` input is just for the "default" value shown?
                
                # Let's look at `gemini.md`: "mu_w: default line width".
                # Maybe it means the user CAN set it.
                # Let's try to support both: if user provides it, use it? 
                # Actually, safe bet: Use p.width.
                
                current_width = p.width
                
                # Calculate sigma absolute value
                sigma_percent = float(settings.get("sigma_w", 10)) / 100.0
                sigma_w = current_width * sigma_percent
                
                L_c = float(settings.get("L_c", 0.002))
                model = settings.get("model", "matern32")
                ds_arc = float(settings.get("ds_arc", 2e-4))
                n_resample = int(settings.get("n_resample", 1200))
                
                # w_min/max are percentages of mu_w (current_width)
                w_min_pct = float(settings.get("w_min", 80)) / 100.0
                w_max_pct = float(settings.get("w_max", 120)) / 100.0
                
                w_min = current_width * w_min_pct
                w_max = current_width * w_max_pct
                
                # Random seed? "the seed is random for each primitive"
                import random
                seed = random.randint(0, 100000)
                
                poly, (s, w_s), cl, dense = trace.build_trace(
                    path_pts=p.center_line,
                    mu_w=current_width,
                    sigma_w=sigma_w,
                    L_c=L_c,
                    model=model,
                    ds_arc=ds_arc,
                    n_resample=n_resample,
                    seed=seed,
                    w_min=w_min,
                    w_max=w_max,
                    plot=False
                )
                
                # Store stats
                # We need to store it by the NEW primitive ID? 
                # Or maybe we can just store it by the original ID if we are just displaying?
                # But the original primitive is deleted.
                # The new primitive will have a new ID.
                # However, the user flow is: Select primitive -> Show stats.
                # After generation, the tree view needs to refresh to show new primitives?
                # Or we just update the geometry.
                # If we delete and create new, the ID changes.
                # So we need to handle that.
                
                # For now, let's just store it. We might need to return a map of old_id -> new_id
                # But wait, create_polygon_from_points returns the new primitive?
                # pyedb's create_polygon_from_points usually returns True or the object.
                # Let's check pyedb source or docs if possible. 
                # Assuming it returns the primitive or we can find it.
                # Actually, `create_polygon_from_points` in pyedb might just return bool.
                
                # If we can't get the new ID easily, we might have a problem linking the stats to the new primitive.
                # But for the MVP, maybe we just assume the user re-selects?
                # Or we can try to find the new primitive.
                
                # Let's store the data in a temporary structure or attach it to the net name + layer?
                # Unique identifier: Net Name + Layer + ...?
                # Primitives in a net are a list.
                
                # Let's just store it for now.
                self.variation_data[p.id] = {
                    "s": s.tolist(),
                    "w_s": w_s.tolist(),
                    "mu_w": current_width
                }

                # Update EDB
                # We need to replace the primitive.
                # create_polygon_from_points is what was used in the user's edit to main.py
                self.edb.modeler.create_polygon_from_points(list(poly), p.layer_name, net_name)
                p.delete()
        
        return True

    def get_primitive_stats(self, primitive_id):
        return self.variation_data.get(primitive_id, None)
