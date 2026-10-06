# Author:
#   Will Rodman - Tulane University
#   wrodman@tulane.edu
#
# -----------------------------------------------------------------------------
#
# Source Repository:
#   GitHub.com compgeomTU/mapmatching main.py
#

import argparse
import logging

from Curve import Curve
from GraphByCurve import GraphByCurve
from Graph import Graph


def build_parser():
    parser = argparse.ArgumentParser(
        description="Visualize a graph-by-curve free-space diagram."
    )
    parser.add_argument("graph_filename", help="graph input filename prefix")
    parser.add_argument("curve_filename", help="curve input filename prefix")

    parser.add_argument(
        "-e",
        "--epsilon",
        type=float,
        help="epsilon value for the 3-D free-space diagram",
    )
    parser.add_argument(
        "-a",
        "--area",
        type=float,
        metavar="EPSILON",
        help="compute and print free-space area at this epsilon",
    )
    parser.add_argument(
        "-n",
        "--approximation",
        type=int,
        dest="n_approximation",
        help="number of subdivision/approximation terms",
    )
    parser.add_argument(
        "-f",
        "--figure",
        dest="figure_filename",
        help="save the generated plot to this file instead of displaying it",
    )
    parser.add_argument(
        "-l",
        "--log",
        dest="log_filename",
        help="write computation details to this log file",
    )
    parser.add_argument(
        "-p",
        "--plot-2d",
        action="store_true",
        help="plot the input graph and curve in 2-D",
    )

    display = parser.add_argument_group("3-D display options")
    display.add_argument(
        "--no-cells",
        action="store_true",
        help="hide the light-gray cell surfaces",
    )
    display.add_argument(
        "--no-labels",
        action="store_true",
        help="hide graph edge labels",
    )
    display.add_argument(
        "--no-legend",
        action="store_true",
        help="hide the connected-component legend",
    )
    display.add_argument(
        "--no-critical-contacts",
        action="store_true",
        help="hide point-only critical contacts that connect free-space patches",
    )
    display.add_argument(
        "--no-coverage-inset",
        action="store_true",
        help="hide the graph/curve component-coverage side views",
    )
    display.add_argument(
        "--no-distances",
        action="store_true",
        help="skip traversal-distance computation/display",
    )
    display.add_argument(
        "--distance-tolerance",
        type=float,
        default=1e-6,
        metavar="TOL",
        help="absolute tolerance for traversal-distance computation (default: 1e-6)",
    )

    display.add_argument(
        "--graph-scale",
        type=float,
        default=1.0,
        metavar="S",
        help=(
            "visual scale of the graph x/y plane in the 3-D plot "
            "(default: 1.0)"
        ),
    )
    display.add_argument(
        "--curve-scale",
        type=float,
        default=1.0,
        metavar="S",
        help=(
            "visual scale of the curve/arc-length z direction in the 3-D plot "
            "(default: 1.0)"
        ),
    )
    display.add_argument(
        "--equal-data-scale",
        action="store_true",
        help=(
            "use one displayed unit per data unit in x, y, and z; by default "
            "the graph plane and curve-height range are balanced for readability"
        ),
    )

    display.add_argument(
        "--slider",
        "--epsilon-slider",
        dest="epsilon_slider",
        action="store_true",
        help="show an interactive epsilon slider below the 3-D plot",
    )
    display.add_argument(
        "--epsilon-range",
        type=float,
        nargs=2,
        metavar=("MIN", "MAX"),
        help=(
            "epsilon range for --slider; by default MIN=0 and MAX is chosen "
            "large enough for the full free space"
        ),
    )
    display.add_argument(
        "--slider-step",
        type=float,
        metavar="STEP",
        help="optional epsilon increment for the interactive slider",
    )

    highlight = display.add_mutually_exclusive_group()
    highlight.add_argument(
        "--highlight-component",
        type=int,
        metavar="ID",
        help="emphasize one 1-based free-space component ID",
    )
    highlight.add_argument(
        "--highlight-point",
        type=float,
        nargs=3,
        metavar=("X", "Y", "Z"),
        help=(
            "emphasize the component containing the 3-D free-space point (X,Y,Z); "
            "Z is curve arc length"
        ),
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.n_approximation is not None and args.n_approximation < 2:
        parser.error("--approximation/-n must be at least 2")

    if args.epsilon is not None and args.epsilon < 0:
        parser.error("--epsilon/-e must be nonnegative")
    if args.area is not None and args.area < 0:
        parser.error("--area/-a epsilon must be nonnegative")
    if args.graph_scale <= 0 or args.curve_scale <= 0:
        parser.error("--graph-scale and --curve-scale must be positive")
    if args.distance_tolerance <= 0:
        parser.error("--distance-tolerance must be positive")

    if args.epsilon_slider and args.epsilon is None:
        parser.error("--slider requires --epsilon/-e for the initial value")
    if args.epsilon_slider and args.figure_filename is not None:
        parser.error("--slider is interactive and cannot be combined with --figure/-f")
    if args.epsilon_range is not None and not args.epsilon_slider:
        parser.error("--epsilon-range is only used with --slider")
    if args.slider_step is not None and not args.epsilon_slider:
        parser.error("--slider-step is only used with --slider")
    if args.slider_step is not None and args.slider_step <= 0:
        parser.error("--slider-step must be positive")
    if args.epsilon_range is not None:
        slider_min, slider_max = args.epsilon_range
        if slider_min < 0:
            parser.error("--epsilon-range MIN must be nonnegative")
        if slider_max <= slider_min:
            parser.error("--epsilon-range requires MAX > MIN")
        if args.epsilon is not None and not slider_min <= args.epsilon <= slider_max:
            parser.error("the initial --epsilon/-e must lie inside --epsilon-range")

    if (args.highlight_component is not None or args.highlight_point is not None) and args.epsilon is None:
        parser.error("--highlight-component/--highlight-point require --epsilon/-e")

    if args.epsilon is None and args.area is None and not args.plot_2d:
        parser.error("choose at least one of --epsilon/-e, --area/-a, or --plot-2d/-p")

    if args.log_filename:
        logging.basicConfig(
            filename=args.log_filename,
            format="%(asctime)s %(message)s",
            level=logging.INFO,
            filemode="w",
            force=True,
        )
        logging.info(
            "Graph: %s Curve: %s", args.graph_filename, args.curve_filename
        )

    graph = Graph(args.graph_filename)
    curve = Curve(args.curve_filename)
    ctg = GraphByCurve(graph, curve, args.n_approximation)

    if args.area is not None:
        logging.info("Area epsilon: %s", args.area)
        ctg.buildFreeSpace(args.area)
        area = ctg.calculateArea()
        print("Free Space Area:", area)

    if args.epsilon is not None:
        logging.info("Epsilon: %s", args.epsilon)
        ctg.buildCells()

        traversal_distances = None
        if not args.no_distances:
            if ctg.traversalDistanceAvailable():
                print("Computing traversal distances...")
                traversal_distances = ctg.computeTraversalDistances(
                    tolerance=args.distance_tolerance
                )
                print("Traversal distances:")
                print(f"  Graph -> Curve: {traversal_distances.graph_to_curve:.10g}")
                print(f"  Curve -> Graph: {traversal_distances.curve_to_graph:.10g}")
                print(f"  Symmetric:      {traversal_distances.symmetric:.10g}")
                print(f"  Complete:       {traversal_distances.complete:.10g}")
            else:
                print(
                    "Traversal distances unavailable (optional traversal-distance "
                    "package not installed). Continuing with visualization only."
                )

        if args.epsilon_slider:
            if args.epsilon_range is None:
                slider_min, slider_max = 0.0, None
            else:
                slider_min, slider_max = args.epsilon_range
            ctg.plotFreeSpaceSlider(
                args.epsilon,
                epsilon_min=slider_min,
                epsilon_max=slider_max,
                slider_step=args.slider_step,
                show_cells=not args.no_cells,
                show_labels=not args.no_labels,
                show_legend=not args.no_legend,
                show_critical_contacts=not args.no_critical_contacts,
                highlight_component=args.highlight_component,
                highlight_point=args.highlight_point,
                graph_scale=args.graph_scale,
                curve_scale=args.curve_scale,
                equal_data_scale=args.equal_data_scale,
                traversal_distances=traversal_distances,
                show_coverage_inset=not args.no_coverage_inset,
            )
        else:
            ctg.buildFreeSpace(args.epsilon)
            ctg.plotFreeSpace(
                args.figure_filename,
                show_cells=not args.no_cells,
                show_labels=not args.no_labels,
                show_legend=not args.no_legend,
                show_critical_contacts=not args.no_critical_contacts,
                highlight_component=args.highlight_component,
                highlight_point=args.highlight_point,
                graph_scale=args.graph_scale,
                curve_scale=args.curve_scale,
                equal_data_scale=args.equal_data_scale,
                traversal_distances=traversal_distances,
                show_coverage_inset=not args.no_coverage_inset,
            )

    if args.plot_2d:
        ctg.plot(args.figure_filename, show_labels=not args.no_labels)


if __name__ == "__main__":
    main()
