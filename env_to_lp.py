import pandas as pd

lp_file = "env/env.lp"

### TEST-EINGABE
tracks = [
    [16386,1025,17411,1025,5633,1025,4608],
    [32800,0,32800,0,32800,0,32800],
    [72,1025,2064,0,72,1025,2064]
    ]
trains = pd.DataFrame({
    "id": [0,1],
    "x": [4,6],
    "y": [1,1],
    "dir": ['s','n'],
    "x_end": [1,0],
    "y_end": [2,1],
    "e_dep": [1,1],
    "l_arr": [20,20]
})
###

with open(lp_file, 'w') as lp:
    for i, row in trains.iterrows():
        lp.write(f"train({row['id']}).\n")
        lp.write(f"start({row['id']},({row['x']},{row['y']}),{row['e_dep']},{row['dir']}).\n")
        lp.write(f"end({row['id']},({row['x_end']},{row['y_end']}),{row['l_arr']}).\n\n")
    for i, row in enumerate(tracks):
        for j, track in enumerate(row):
            lp.write(f"cell({i},{j},{track}).\n")
        lp.write(f'\n')
