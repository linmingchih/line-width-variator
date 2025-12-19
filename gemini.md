line width variator
---

## objective
user can open a edb file and generate a new edb file with line width variation.

## layout
pywebview GUI with typescript and React in development mode, and python in production mode.

### menu
FILE: open, save, save_as, close and exit.
Help: about.

Left Settings Panel:
- mu_w: default line width
- sigma_w: percent of mu_w
- L_c: line width variation length
- model: exponential|gaussian|matern32|band_limited combobox
- ds_arc: default is 2e-4
- n_resample: default is 1200
- w_min: percentage of mu_w, defalut is 80%
- w_max: percentage of mu_w, defalut is 120%
- the seed is random for each primitive.
- there is button to generate line width variation with current settings in random seed for each primitive.

Main Canvas:
- fit all to show all primitives with largest scale.
- can zoom, pan with mouse wheel
- allow user to select a primitive to view the width vs path length in bottom statistics panel.
- hover the primitive will show the net name in tooltip.


Right Nets Panel:
- A tree structure showing all nets and primitives in the edb file.
- provide regex search for net name.
- user can select a net or primitive to view the width vs path length in bottom statistics panel.

bottom statistics panel:
- show the width vs path length of the line width variation for each primitive.
- hover the location will highlight points in canvas.


## User Story
1. user can open a edb file and see all nets and primitives in the edb file.
2. user can input the settings and generate line width variation.
3. user can select a net or primitive to view the width vs path length in bottom statistics panel.
4. user can save/save_as the edb file.

## Technical Details
1. pywebview is used to create the GUI.
2. pyedb is used to read and write edb file.
3. main.py is verified and can be used as reference.