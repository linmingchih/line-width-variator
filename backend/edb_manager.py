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
        self.generated_data = {} # Map of original_id -> {points, width, layer, net, type}

    def load_edb(self, path):
        if self.edb:
            try:
                self.edb.close_edb()
            except:
                pass
        
        self.edb_path = path
        self.generated_data = {}
        self.variation_data = {}
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
                    
                    # Check if we have generated data for this primitive
                    if p.id in self.generated_data:
                        gen_data = self.generated_data[p.id]
                        prim_data = {
                            "id": p.id,
                            "type": "Polygon", # It's now a polygon
                            "layer": p.layer_name,
                            "width": 0, # Polygons don't have a single width
                            "points": gen_data["points"], 
                        }
                    else:
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
        print(f"DEBUG: EdbManager.save_edb called with path: {path}")
        if not self.edb:
            print("DEBUG: self.edb is None")
            return False

        try:
            # Capture original path
            original_path = self.edb_path
            
            # 1. Save As to the new path
            print(f"DEBUG: Calling self.edb.save_edb_as({path})")
            self.edb.save_edb_as(path)
            
            # 2. Close the current session (which is now pointing to the new file)
            print("DEBUG: Closing EDB session (new file)")
            self.edb.close_edb()
            
            # 3. Open the NEW file to apply changes
            print(f"DEBUG: Opening new EDB from {path}")
            temp_edb = Edb(path, edbversion="2024.1")
            
            # 4. Apply variations to the NEW file
            print(f"DEBUG: Applying {len(self.generated_data)} variations to saved file")
            
            for orig_id, data in self.generated_data.items():
                found = False
                for net_name, net in temp_edb.nets.nets.items():
                    for p in net.primitives:
                        if p.id == orig_id:
                            # Found it!
                            poly_points = data["points"]
                            temp_edb.modeler.create_polygon_from_points(poly_points, p.layer_name, net_name)
                            p.delete()
                            found = True
                            break
                    if found:
                        break
                
                if not found:
                    print(f"WARNING: Could not find primitive {orig_id} to apply variation")

            # 5. Save again to persist changes
            temp_edb.save_edb()
            temp_edb.close_edb()
            print("DEBUG: save_edb completed on new file")
            
            # 6. Re-open the ORIGINAL file to restore session
            print(f"DEBUG: Re-opening original EDB from {original_path}")
            self.edb = Edb(original_path, edbversion="2024.1")
            self.edb_path = original_path # Ensure path is consistent
            
            return True
        except Exception as e:
            print(f"DEBUG: Error in save_edb: {e}")
            return False

    def apply_variation(self, settings):
        if not self.edb:
            return False

        # Clear previous generation
        self.generated_data = {}
        self.variation_data = {}

        # Only apply to signal nets (those shown in the right panel)
        for net_name, net in self.edb.nets.signal_nets.items():
            for p in net.primitives:
                if p.type != "Path":
                    continue
                
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
                
                # Store in generated_data
                # We convert poly to list of lists
                poly_list = [list(pt) for pt in poly]
                
                self.generated_data[p.id] = {
                    "points": poly_list,
                    "width": current_width, # Original width
                    "layer": p.layer_name,
                    "net": net_name
                }
                
                # Store stats
                self.variation_data[p.id] = {
                    "s": s.tolist(),
                    "w_s": w_s.tolist(),
                    "mu_w": current_width
                }
        
        return True

    def get_primitive_stats(self, primitive_id):
        return self.variation_data.get(primitive_id, None)
