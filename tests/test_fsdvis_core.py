import math
from types import SimpleNamespace

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from Curve import Curve
from FreeSpace import FreeSpace
from Graph import Graph
from GraphByCurve import GraphByCurve
from examples.u_path_immersed_tree import load_instance


def make_graph(nodes, edges):
    graph = Graph()
    for nid, point in nodes.items():
        graph.addNode(nid, point[0], point[1])
    for eid, edge in edges.items():
        graph.connectTwoNodes(eid, edge[0], edge[1])
    return graph


def make_curve(points):
    curve = Curve()
    curve.nodes.clear()
    curve.edges.clear()
    curve.nodeLink.clear()
    curve.edgeHash.clear()
    curve.numberOfNodes = 0
    curve.numberOfEdges = 0
    curve.largestEdgeID = -1
    for i, point in enumerate(points):
        curve.addNode(i, point[0], point[1])
    for i in range(len(points) - 1):
        curve.connectTwoNodes(i, i, i + 1)
    curve.compute_vertex_dists()
    return curve


def _coverage_flags(free_space, tolerance=1e-8):
    coverage = free_space.component_coverage()
    covers_graph = {
        cid for cid, item in coverage.items()
        if item["graph_fraction"] >= 1.0 - tolerance
    }
    covers_curve = {
        cid for cid, item in coverage.items()
        if item["curve_fraction"] >= 1.0 - tolerance
    }
    return coverage, covers_graph, covers_curve


def test_readme_example_has_two_separate_covering_components_at_epsilon_12():
    graph, curve = load_instance()
    free_space = FreeSpace(graph, curve, 12.0)
    free_space.build_cell_boundaries_3D()

    assert free_space.num_components == 2
    coverage, covers_graph, covers_curve = _coverage_flags(free_space)
    assert covers_graph
    assert covers_curve
    assert covers_graph.isdisjoint(covers_curve)
    assert len(coverage) == 2


def test_readme_example_has_one_component_covering_both_at_epsilon_12_3():
    graph, curve = load_instance()
    free_space = FreeSpace(graph, curve, 12.3)
    free_space.build_cell_boundaries_3D()

    _, covers_graph, covers_curve = _coverage_flags(free_space)
    assert covers_graph & covers_curve


def test_readme_example_distances_when_backend_is_installed():
    if not GraphByCurve.traversalDistanceAvailable():
        pytest.skip("optional traversal_distance package is not installed")

    graph, curve = load_instance()
    distances = GraphByCurve(graph, curve).computeTraversalDistances(tolerance=1e-6)

    assert abs(distances.graph_to_curve - 12.0) <= 2e-6
    assert abs(distances.curve_to_graph - 8 * math.sqrt(2)) <= 2e-6
    assert abs(distances.symmetric - 12.0) <= 2e-6
    assert abs(distances.complete - math.sqrt(149)) <= 2e-6


def test_area_is_idempotent():
    graph = make_graph({0: (0, 0), 1: (2, 0)}, {0: (0, 1)})
    curve = make_curve([(0, 1), (2, 1)])
    free_space = FreeSpace(graph, curve, 1.5)
    a1 = free_space.calculateArea()
    a2 = free_space.calculateArea()
    assert a1 > 0
    assert math.isclose(a1, a2, rel_tol=0, abs_tol=1e-12)


def test_interior_free_space_is_not_lost():
    graph = make_graph({0: (-1, 0), 1: (1, 0)}, {0: (0, 1)})
    curve = make_curve([(0, -1), (0, 1)])
    free_space = FreeSpace(graph, curve, 0.1)
    cells = free_space.build_cell_boundaries_3D()
    assert (0, 0) in cells
    assert cells[(0, 0)]["geometry_type"] == "polygon"


def test_component_click_selects_and_toggles_coverage_component():
    graph, curve = load_instance()
    visualizer = GraphByCurve(graph, curve)
    visualizer.buildCells()
    visualizer.buildFreeSpace(12.0)
    visualizer.freespace.build_cell_boundaries_3D()

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    draw_state = visualizer._draw_free_space_3d(
        ax, show_cells=False, show_labels=False, print_summary=False,
        rebuild_free_space=False,
    )
    state_holder = {"draw_state": draw_state}
    selection = {
        "component_id": None,
        "representative": None,
        "user_selected": False,
    }
    redraw_calls = []

    def redraw(preserve_view=False):
        redraw_calls.append(preserve_view)

    visualizer._install_component_click_handler(
        fig, ax, state_holder, selection, redraw
    )
    on_pick, on_key, _, _ = fig._fsdvis_component_click_callbacks

    component_id = sorted(draw_state["component_artists"])[0]
    artist = draw_state["component_artists"][component_id][0]
    assert getattr(artist, "_fsd_component_id") == component_id
    assert artist.get_picker()

    on_pick(SimpleNamespace(artist=artist))
    assert selection["component_id"] == component_id
    assert selection["representative"] in visualizer.freespace.components[component_id]
    assert redraw_calls[-1] is True

    # Clicking the selected component again restores the all-component view.
    on_pick(SimpleNamespace(artist=artist))
    assert selection["component_id"] is None
    assert selection["representative"] is None

    # Escape also clears an active selection.
    on_pick(SimpleNamespace(artist=artist))
    on_key(SimpleNamespace(key="escape"))
    assert selection["component_id"] is None
    assert selection["representative"] is None

    plt.close(fig)


def test_coverage_insets_can_show_only_selected_component():
    graph, curve = load_instance()
    visualizer = GraphByCurve(graph, curve)
    visualizer.buildCells()
    visualizer.buildFreeSpace(12.0)
    visualizer.freespace.build_cell_boundaries_3D()

    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(121, projection="3d")
    graph_ax = fig.add_subplot(222)
    curve_ax = fig.add_subplot(224)
    draw_state = visualizer._draw_free_space_3d(
        ax, show_cells=False, show_labels=False, print_summary=False,
        rebuild_free_space=False,
    )
    selected = sorted(visualizer.freespace.components)[0]
    visualizer._draw_coverage_insets(
        graph_ax, curve_ax, draw_state, highlight_component=selected
    )

    graph_labels = [text.get_text() for text in graph_ax.texts]
    curve_labels = [text.get_text() for text in curve_ax.texts]
    assert any(label.startswith(f"C{selected}:") for label in graph_labels)
    assert any(label.startswith(f"C{selected}:") for label in curve_labels)
    assert all(
        not label.startswith("C") or label.startswith(f"C{selected}:")
        for label in graph_labels + curve_labels
    )
    plt.close(fig)
