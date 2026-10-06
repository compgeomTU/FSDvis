"""Visualize the U-path / immersed-tree example used in the README.

Run from the repository root, for example:

    python3 examples/u_path_immersed_tree.py --output u_tree_eps12.png

With the optional ``traversal_distance`` package installed, the script also
prints the two directed, symmetric, and complete traversal distances.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Curve import Curve
from Graph import Graph
from GraphByCurve import GraphByCurve

GRAPH_PREFIX = ROOT / "samples" / "U_gap_H"
CURVE_PREFIX = ROOT / "samples" / "U_gap_P"


def load_instance():
    """Return the graph H and curve P used throughout the README and tests."""
    return Graph(str(GRAPH_PREFIX)), Curve(str(CURVE_PREFIX))


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run the FSDvis U-path / immersed-tree example."
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=12.0,
        help="free-space threshold to display (default: 12)",
    )
    parser.add_argument(
        "--output",
        help="save a static figure instead of opening an interactive window",
    )
    parser.add_argument(
        "--slider",
        action="store_true",
        help="open the epsilon slider (cannot be combined with --output)",
    )
    parser.add_argument(
        "--no-distances",
        action="store_true",
        help="skip traversal-distance computation even when the optional package is installed",
    )
    return parser


def main():
    args = build_parser().parse_args()
    if args.epsilon < 0:
        raise SystemExit("--epsilon must be nonnegative")
    if args.slider and args.output:
        raise SystemExit("--slider cannot be combined with --output")

    graph, curve = load_instance()
    visualizer = GraphByCurve(graph, curve)
    visualizer.buildCells()

    distances = None
    if not args.no_distances and visualizer.traversalDistanceAvailable():
        distances = visualizer.computeTraversalDistances()
        print("Traversal distances:")
        print(f"  Graph H -> Curve P: {distances.graph_to_curve:.7g}")
        print(f"  Curve P -> Graph H: {distances.curve_to_graph:.7g}")
        print(f"  Symmetric:          {distances.symmetric:.7g}")
        print(f"  Complete:           {distances.complete:.7g}")
    elif not args.no_distances:
        print("Traversal-distance package not installed; showing the free space only.")

    visualizer.buildFreeSpace(args.epsilon)
    visualizer.freespace.build_cell_boundaries_3D()
    coverage = visualizer.freespace.component_coverage()

    print(f"epsilon = {args.epsilon:g}")
    print(f"connected components = {visualizer.freespace.num_components}")
    for component_id in sorted(coverage):
        item = coverage[component_id]
        print(
            f"  component {component_id}: "
            f"graph {100 * item['graph_fraction']:.2f}%  "
            f"curve {100 * item['curve_fraction']:.2f}%"
        )

    if args.slider:
        visualizer.plotFreeSpaceSlider(
            args.epsilon,
            epsilon_min=10.5,
            epsilon_max=13.0,
            show_cells=False,
            show_labels=False,
            traversal_distances=distances,
        )
    else:
        visualizer.plotFreeSpace(
            args.output,
            show_cells=False,
            show_labels=False,
            traversal_distances=distances,
        )
        if args.output:
            print(f"saved figure to {args.output}")


if __name__ == "__main__":
    main()
