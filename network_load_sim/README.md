# Network Load Simulation — Telecom Base Stations

## Overview
Simulates 24-hour traffic load dynamics across a city grid of base stations
using ODE modeling and FuncAnimation.

## Methods
- ODE: dL/dt = λ(t) - μ·L per base station
- scipy odeint: numerical solver
- matplotlib FuncAnimation: live animated heatmap

## Architecture (Durán 2020)
| File | Layer | Role |
|------|-------|------|
| models/load_model.py | M_i | ODE + demand function |
| kernel/solver.py | KS_i | odeint solver |
| integration/animator.py | IM_k | Animation |

## Install
```
pip install -r requirements.txt
conda install conda-forge::ffmpeg
```

## Run
```
python main.py              # show animation
python main.py --save       # save as .mp4
python main.py --fast       # faster playback
python main.py --summary    # summary plot only
python main.py --small      # quick test (10x10)
```

## Test
```
pytest tests/
```

## References
- Durán, J.M. (2020). What is a Simulation Model?
- Course: System Simulation, HSRW, Schwind & Zimmer
