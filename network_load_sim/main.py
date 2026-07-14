"""
Entry point for the network load simulation.
Run modes:
  python main.py               → slider-controlled panel (default)
  python main.py --animate     → classic animation (no sliders)
  python main.py --save        → animate + save as .mp4
  python main.py --fast        → fast animation (interval=50ms)
  python main.py --summary     → show summary plot only
  python main.py --small       → use 10x10 grid (faster)
"""

import argparse
import time

from kernel.solver import solve_city
from integration.animator import create_animation, plot_summary
from integration.interactive import run_interactive


def main() -> None:
    parser = argparse.ArgumentParser(description="Network Load Simulation")
    parser.add_argument("--animate", action="store_true",
                         help="Classic animation without sliders")
    parser.add_argument("--save", action="store_true",
                         help="Save animation as network_load.mp4")
    parser.add_argument("--fast", action="store_true",
                         help="Fast playback (50ms per frame)")
    parser.add_argument("--summary", action="store_true",
                         help="Show summary plot only")
    parser.add_argument("--small", action="store_true",
                         help="Use 10x10 grid for quick testing")
    args = parser.parse_args()

    grid = 10 if args.small else 20

    if args.summary:
        print(f"Solving ODE for {grid}x{grid} grid...")
        result = solve_city(grid_size=grid, mu=1.2)
        plot_summary(result)
        return

    if args.animate or args.save:
        interval = 50 if args.fast else 100
        save_path = "network_load.mp4" if args.save else None
        print(f"Solving ODE for {grid}x{grid} = {grid * grid} base stations...")
        start = time.time()
        result = solve_city(grid_size=grid, mu=1.2)
        print(f"Solved in {time.time() - start:.1f}s")
        print(f"Peak load at hour: {result['peak_load_time']:.1f}")
        print(f"Max overloaded: {result['max_overloaded']} stations")
        create_animation(result, interval=interval, save_path=save_path, show=True)
        plot_summary(result)
        return

    # Default: interactive slider panel
    print(f"Launching interactive panel for {grid}x{grid} grid...")
    print("Sliders: Hour | Capacity (mu) | City Density | Day of Week")
    run_interactive(grid_size=grid)


if __name__ == "__main__":
    main()