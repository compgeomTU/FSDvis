# Author:
#   Will Rodman - Tulane University
#   wrodman@tulane.edu
#
# -----------------------------------------------------------------------------
#
# Source Repository:
#   GitHub.com compgeomTU/mapmatching GraphByCurve.py
#

import logging
import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from Cells import Cells
from FreeSpace import FreeSpace
from NodeDistribution import curve_node_distribution, graph_node_distribution
try:
    from traversal_distance import compute_traversal_distances as _compute_traversal_distances
except ImportError:
    _compute_traversal_distances = None


class GraphByCurve:
    def __init__(self, G, C, n_approximation=None):
        self.__G, self.__C = G, C
        if n_approximation is None:
            self.__sigma_G, self.__sigma_C = self.__G, self.__C
        else:
            self.__sigma_G = graph_node_distribution(G, n_approximation)
            self.__sigma_C = curve_node_distribution(C, n_approximation)

        self.__cells = None
        self.__freespace = None
        self.__merge_events = None

        logging.info("--------------- Graph Structure ---------------")
        for edge_id, edge in self.__G.edges.items():
            n1_id, n2_id = edge
            n1, n2 = self.__G.nodes[n1_id], self.__G.nodes[n2_id]
            logging.info("   E: %s   V1: %s -> %s   V2: %s -> %s", edge_id, n1_id, n1, n2_id, n2)

        logging.info("--------------- Curve Structure ---------------")
        for edge_id, edge in self.__C.edges.items():
            n1_id, n2_id = edge
            n1, n2 = self.__C.nodes[n1_id], self.__C.nodes[n2_id]
            logging.info("   E: %s   V1: %s -> %s   V2: %s -> %s", edge_id, n1_id, n1, n2_id, n2)

    @property
    def freespace(self):
        """Expose free-space metadata, including component IDs, read-only by convention."""
        return self.__freespace

    def buildCells(self):
        self.__cells = Cells(self.__G, self.__C)

    def buildFreeSpace(self, epsilon):
        self.__freespace = FreeSpace(self.__sigma_G, self.__sigma_C, epsilon)

    def calculateArea(self):
        if self.__freespace is None:
            raise RuntimeError("buildFreeSpace(epsilon) must be called before calculateArea().")
        return self.__freespace.calculateArea()

    @staticmethod
    def traversalDistanceAvailable():
        """Return whether the optional traversal-distance backend is installed."""
        return _compute_traversal_distances is not None

    def computeTraversalDistances(self, tolerance=1e-6):
        """Compute directed, symmetric, and complete traversal distances.

        This feature is optional.  FSDvis visualization works without the
        ``traversal-distance`` package installed.
        """
        if _compute_traversal_distances is None:
            raise RuntimeError(
                "Traversal-distance support is unavailable. Install the optional "
                "traversal-distance package, or run FSDvis with --no-distances."
            )
        return _compute_traversal_distances(self.__G, self.__C, tolerance=tolerance)

    @staticmethod
    def _closest_point_on_segment(point, A, B):
        """Return closest segment parameter, point, and distance."""
        point = np.asarray(point, dtype=float)
        A = np.asarray(A, dtype=float)
        B = np.asarray(B, dtype=float)
        direction = B - A
        denom = float(np.dot(direction, direction))
        if denom <= 1e-15:
            t = 0.0
        else:
            t = float(np.dot(point - A, direction) / denom)
            t = min(1.0, max(0.0, t))
        closest = A + t * direction
        return t, closest, float(np.linalg.norm(point - closest))

    def _build_connectivity_merge_events(self):
        """Precompute epsilon values/locations where components actually merge.

        Product cells are born at their segment-segment distance.  Adjacency
        across a shared product-cell boundary is born at the corresponding
        point-to-segment distance.  Sweeping these critical values with a
        union-find gives the connectivity-changing events exactly at the cell
        complex level, including point-only tangencies.
        """
        if self.__merge_events is not None:
            return self.__merge_events

        graph = self.__sigma_G
        curve = self.__sigma_C
        cell_births = {}
        for graph_edge_id, graph_edge in graph.edges.items():
            A = graph.nodes[graph_edge[0]]
            B = graph.nodes[graph_edge[1]]
            for curve_edge_id, curve_edge in curve.edges.items():
                P = curve.nodes[curve_edge[0]]
                Q = curve.nodes[curve_edge[1]]
                _, _, dist2 = FreeSpace._closest_parameters(A, B, P, Q)
                cell_births[(graph_edge_id, curve_edge_id)] = math.sqrt(max(0.0, dist2))

        boundary_events = []

        # graph vertex x curve edge
        for graph_vertex_id, graph_vertex in graph.nodes.items():
            incident_graph_edges = [
                edge_id for edge_id, edge in graph.edges.items()
                if graph_vertex_id in edge
            ]
            if len(incident_graph_edges) < 2:
                continue
            gx, gy = graph_vertex
            for curve_edge_id, curve_edge in curve.edges.items():
                P = curve.nodes[curve_edge[0]]
                Q = curve.nodes[curve_edge[1]]
                s, _, epsilon = self._closest_point_on_segment(graph_vertex, P, Q)
                z0 = float(curve.vertex_dists[curve_edge[0]])
                z1 = float(curve.vertex_dists[curve_edge[1]])
                boundary_events.append({
                    "epsilon": epsilon,
                    "point": (float(gx), float(gy), z0 + s * (z1 - z0)),
                    "adjacent_cells": [
                        (graph_edge_id, curve_edge_id)
                        for graph_edge_id in incident_graph_edges
                    ],
                    "boundary_type": "graph-vertex/curve-edge",
                    "ids": (graph_vertex_id, curve_edge_id),
                })

        # curve vertex x graph edge
        for curve_vertex_id, curve_vertex in curve.nodes.items():
            incident_curve_edges = [
                edge_id for edge_id, edge in curve.edges.items()
                if curve_vertex_id in edge
            ]
            if len(incident_curve_edges) < 2:
                continue
            z = float(curve.vertex_dists[curve_vertex_id])
            for graph_edge_id, graph_edge in graph.edges.items():
                A = graph.nodes[graph_edge[0]]
                B = graph.nodes[graph_edge[1]]
                t, closest, epsilon = self._closest_point_on_segment(curve_vertex, A, B)
                boundary_events.append({
                    "epsilon": epsilon,
                    "point": (float(closest[0]), float(closest[1]), z),
                    "adjacent_cells": [
                        (graph_edge_id, curve_edge_id)
                        for curve_edge_id in incident_curve_edges
                    ],
                    "boundary_type": "curve-vertex/graph-edge",
                    "ids": (curve_vertex_id, graph_edge_id),
                })

        # Group numerically identical critical values.  Ten decimal places is
        # substantially tighter than the display/slider precision while still
        # coalescing roundoff copies of the same geometric event.
        births_by_key = {}
        events_by_key = {}
        epsilon_for_key = {}
        for cell, epsilon in cell_births.items():
            key = round(float(epsilon), 10)
            births_by_key.setdefault(key, []).append(cell)
            epsilon_for_key.setdefault(key, float(epsilon))
        for event in boundary_events:
            key = round(float(event["epsilon"]), 10)
            events_by_key.setdefault(key, []).append(event)
            epsilon_for_key.setdefault(key, float(event["epsilon"]))

        parent = {}
        rank = {}
        active = set()

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra == rb:
                return ra
            if rank[ra] < rank[rb]:
                ra, rb = rb, ra
            parent[rb] = ra
            if rank[ra] == rank[rb]:
                rank[ra] += 1
            return ra

        merge_events = []
        all_keys = sorted(set(births_by_key) | set(events_by_key))
        for key in all_keys:
            # Label components that existed immediately below this threshold.
            old_labels = {}
            for cell in active:
                root = find(cell)
                old_labels.setdefault(root, set()).add(root)

            for cell in births_by_key.get(key, []):
                if cell not in active:
                    active.add(cell)
                    parent[cell] = cell
                    rank[cell] = 0

            # Convert labels to the current roots; newly born cells carry no
            # old-component label.
            labels = {}
            for cell in active:
                root = find(cell)
                labels.setdefault(root, set())
            for old_root, label_set in old_labels.items():
                if old_root in parent:
                    labels.setdefault(find(old_root), set()).update(label_set)

            for event in events_by_key.get(key, []):
                adjacent = [cell for cell in event["adjacent_cells"] if cell in active]
                event_merged = False
                for i in range(1, len(adjacent)):
                    a, b = adjacent[0], adjacent[i]
                    ra, rb = find(a), find(b)
                    if ra == rb:
                        continue
                    la = set(labels.get(ra, set()))
                    lb = set(labels.get(rb, set()))
                    if la and lb and la != lb:
                        event_merged = True
                    new_root = union(ra, rb)
                    labels.pop(ra, None)
                    labels.pop(rb, None)
                    labels[new_root] = la | lb

                if event_merged:
                    merge_events.append(dict(event))

        # Deduplicate the same geometric point reported through equivalent
        # incident-cell descriptions at the same epsilon.
        deduped = []
        seen = set()
        for event in sorted(merge_events, key=lambda e: (e["epsilon"], e["point"])):
            dedupe_key = (
                round(float(event["epsilon"]), 9),
                tuple(round(float(v), 8) for v in event["point"]),
            )
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            deduped.append(event)

        self.__merge_events = deduped
        return self.__merge_events

    def _most_recent_merge_events(self, epsilon, tolerance=1e-9):
        """Return all markers at the latest merge threshold <= epsilon."""
        eligible = [
            event for event in self._build_connectivity_merge_events()
            if event["epsilon"] <= float(epsilon) + tolerance
        ]
        if not eligible:
            return []
        latest = max(event["epsilon"] for event in eligible)
        scale = max(1.0, abs(latest))
        return [
            event for event in eligible
            if abs(event["epsilon"] - latest) <= tolerance * scale
        ]

    @staticmethod
    def _component_colors(num_components):
        if num_components <= 0:
            return {}
        if num_components <= 20:
            cmap = plt.get_cmap("tab20")
            return {
                component_id: cmap(component_id - 1)
                for component_id in range(1, num_components + 1)
            }

        # Viridis remains perceptually uniform/colorblind-friendly when more
        # than 20 distinct categorical slots are required.
        cmap = plt.get_cmap("viridis")
        return {
            component_id: cmap((component_id - 1) / max(1, num_components - 1))
            for component_id in range(1, num_components + 1)
        }

    def _set_display_scale_3d(
        self,
        ax,
        graph_scale=1.0,
        curve_scale=1.0,
        equal_data_scale=False,
    ):
        """Set readable 3-D proportions without changing any computation.

        The x/y coordinates come from the graph, while z is arc length along
        the curve.  In balanced mode (the default), the full curve-height range
        is displayed with roughly the same visual extent as the larger x/y
        graph range.  ``graph_scale`` and ``curve_scale`` then independently
        enlarge/shrink those two visual dimensions.

        ``equal_data_scale=True`` restores the old convention that one data unit
        has the same displayed size in x, y, and z.
        """
        xs = [node[0] for node in self.__G.nodes.values()]
        ys = [node[1] for node in self.__G.nodes.values()]
        zs = list(self.__C.vertex_dists)
        if not xs or not ys or not zs:
            return

        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        z_min, z_max = min(zs), max(zs)

        ax.set_xlim(x_min, x_max if x_max != x_min else x_min + 1.0)
        ax.set_ylim(y_min, y_max if y_max != y_min else y_min + 1.0)
        ax.set_zlim(z_min, z_max if z_max != z_min else z_min + 1.0)

        x_range = max(x_max - x_min, 1e-12)
        y_range = max(y_max - y_min, 1e-12)
        z_range = max(z_max - z_min, 1e-12)

        if equal_data_scale:
            aspect = np.array(
                [x_range * graph_scale, y_range * graph_scale, z_range * curve_scale],
                dtype=float,
            )
        else:
            # Preserve the graph's x/y geometry, but normalize the independent
            # curve (z) extent so a long curve does not make the plot a tower.
            graph_reference = max(x_range, y_range)
            aspect = np.array(
                [
                    (x_range / graph_reference) * graph_scale,
                    (y_range / graph_reference) * graph_scale,
                    curve_scale,
                ],
                dtype=float,
            )

        # Matplotlib dislikes exactly zero box dimensions.  Axes3D itself uses
        # a square viewport even when the application window is wide.  A box
        # zoom greater than 1 therefore makes projected geometry run into that
        # square viewport and look artificially chopped.  Keep a small fitting
        # margin instead; users can still zoom interactively, and that manual
        # zoom is preserved by the epsilon slider.
        aspect = np.maximum(aspect, 1e-3)
        try:
            ax.set_box_aspect(aspect, zoom=0.92)
        except TypeError:
            ax.set_box_aspect(aspect)

    def _set_equal_data_scale_3d(self, ax):
        """Backward-compatible wrapper for the previous display convention."""
        self._set_display_scale_3d(ax, equal_data_scale=True)

    @staticmethod
    def _farthest_pair(vertices):
        if len(vertices) <= 1:
            return vertices
        best = (vertices[0], vertices[1])
        best_dist = -1.0
        for i in range(len(vertices)):
            a = np.asarray(vertices[i], dtype=float)
            for j in range(i + 1, len(vertices)):
                b = np.asarray(vertices[j], dtype=float)
                dist = float(np.dot(a - b, a - b))
                if dist > best_dist:
                    best_dist = dist
                    best = (vertices[i], vertices[j])
        return list(best)

    @staticmethod
    def _capture_view_3d(ax):
        """Capture camera orientation *and* zoom/data limits.

        Matplotlib's interactive 3-D zoom changes axis limits on recent
        versions and ``_dist`` on some older versions.  Keeping both makes the
        epsilon slider preserve the user's current view across redraws.
        """
        return {
            "elev": ax.elev,
            "azim": ax.azim,
            "roll": getattr(ax, "roll", 0.0),
            "xlim": ax.get_xlim3d(),
            "ylim": ax.get_ylim3d(),
            "zlim": ax.get_zlim3d(),
            "dist": getattr(ax, "_dist", None),
        }

    @staticmethod
    def _restore_view_3d(ax, state):
        if not state:
            return
        try:
            ax.view_init(
                elev=state["elev"],
                azim=state["azim"],
                roll=state.get("roll", 0.0),
            )
        except TypeError:
            ax.view_init(elev=state["elev"], azim=state["azim"])
        ax.set_xlim3d(state["xlim"])
        ax.set_ylim3d(state["ylim"])
        ax.set_zlim3d(state["zlim"])
        if state.get("dist") is not None and hasattr(ax, "_dist"):
            ax._dist = state["dist"]

    @staticmethod
    def _distance_text(distances):
        if distances is None:
            return None
        return (
            "Traversal distances\n"
            f"Graph → Curve: {distances.graph_to_curve:.7g}\n"
            f"Curve → Graph: {distances.curve_to_graph:.7g}\n"
            f"Symmetric:     {distances.symmetric:.7g}\n"
            f"Complete:      {distances.complete:.7g}"
        )

    @classmethod
    def _add_distance_panel(cls, fig, distances):
        text = cls._distance_text(distances)
        if text is None:
            return None
        return fig.text(
            0.985,
            0.985,
            text,
            ha="right",
            va="top",
            fontsize="small",
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.88),
        )

    def _draw_free_space_3d(
        self,
        ax,
        show_cells=True,
        show_labels=True,
        show_legend=True,
        show_critical_contacts=True,
        highlight_component=None,
        highlight_point=None,
        graph_scale=1.0,
        curve_scale=1.0,
        equal_data_scale=False,
        component_colors=None,
        rebuild_free_space=True,
        strict_highlight=True,
        print_summary=True,
        show_title=False,
    ):
        """Draw the current free space into an existing 3-D axes.

        This helper is shared by the static plot and the interactive epsilon
        slider.  Keeping the drawing code in one place ensures that both views
        use the same component colors, labels, scaling, and highlighting rules.
        """
        if self.__freespace is None:
            raise RuntimeError("buildFreeSpace(epsilon) must be called before plotting.")
        if self.__cells is None:
            self.buildCells()

        ax.clear()
        ax.grid(False)
        ax._axis3don = False

        if show_cells:
            for cell in self.__cells.cells.values():
                ax.plot_surface(
                    cell.x_proj,
                    cell.y_proj,
                    cell.z_proj,
                    alpha=0.12,
                    color="lightgray",
                    edgecolor="black",
                    linewidth=0.5,
                )

        if rebuild_free_space:
            self.__freespace.build_cell_boundaries_3D()

        if print_summary:
            print(f"Free-space connected components: {self.__freespace.num_components}")

        effective_highlight = highlight_component
        if highlight_point is not None:
            effective_highlight = self.__freespace.find_component_containing_point(highlight_point)
            if print_summary:
                if effective_highlight is None:
                    print(
                        "Highlight point is not contained in the free space: "
                        f"({highlight_point[0]}, {highlight_point[1]}, {highlight_point[2]})"
                    )
                else:
                    print(
                        "Highlight point belongs to free-space component "
                        f"{effective_highlight}."
                    )

        if (
            effective_highlight is not None
            and effective_highlight not in self.__freespace.components
        ):
            if strict_highlight:
                raise ValueError(
                    f"Component {effective_highlight} does not exist; "
                    f"valid component IDs are 1..{self.__freespace.num_components}."
                )
            effective_highlight = None

        if component_colors is None:
            component_colors = self._component_colors(self.__freespace.num_components)

        # Keep the rendered artists associated with their free-space component.
        # Interactive plots use these tags to let the user click a component and
        # inspect only its graph/curve projection coverage.
        component_artists = {}

        for record in self.__freespace.free_space_cells.values():
            component_id = record["component_id"]
            vertices = record["vertices_3d"]
            geometry_type = record.get("geometry_type", "polygon")
            is_highlighted = (
                effective_highlight is None or component_id == effective_highlight
            )
            alpha = 0.95 if is_highlighted else 0.16
            linewidth = 1.4 if effective_highlight == component_id else 0.55
            color = component_colors[component_id]

            if geometry_type == "polygon" and len(vertices) >= 3:
                edgecolor = "black" if is_highlighted else "none"
                poly_cell = Poly3DCollection(
                    [vertices],
                    alpha=alpha,
                    facecolor=color,
                    edgecolor=edgecolor,
                    linewidth=linewidth,
                )
                poly_cell.set_picker(True)
                poly_cell._fsd_component_id = component_id
                ax.add_collection3d(poly_cell)
                component_artists.setdefault(component_id, []).append(poly_cell)
            elif geometry_type == "segment" and len(vertices) >= 2:
                endpoints = self._farthest_pair(vertices)
                us, vs, ws = zip(*endpoints)
                line = ax.plot(
                    us,
                    vs,
                    ws,
                    color=color,
                    alpha=alpha,
                    linewidth=max(2.0, 2.0 * linewidth),
                    picker=5,
                )[0]
                line._fsd_component_id = component_id
                component_artists.setdefault(component_id, []).append(line)
            elif vertices:
                u, v, w = vertices[0]
                point_artist = ax.scatter(
                    [u],
                    [v],
                    [w],
                    color=[color],
                    alpha=alpha,
                    s=28 if is_highlighted else 16,
                    depthshade=False,
                    picker=True,
                )
                point_artist._fsd_component_id = component_id
                component_artists.setdefault(component_id, []).append(point_artist)

        # Point-only shared boundaries are topologically real connections but
        # can be nearly invisible inside opaque polygons.  Exact contacts are
        # shown as white bullseyes.  In addition, the *most recent actual merge*
        # at or below the current epsilon is kept visible as a large gold star,
        # so sliding slightly past a critical value does not make the important
        # merge location disappear.
        recent_merge_events = (
            self._most_recent_merge_events(self.__freespace.epsilon)
            if show_critical_contacts else []
        )
        recent_points = [np.asarray(event["point"], dtype=float) for event in recent_merge_events]

        if show_critical_contacts:
            for contact in self.__freespace.critical_contacts:
                point = np.asarray(contact["point"], dtype=float)
                if any(np.linalg.norm(point - p) <= 1e-7 for p in recent_points):
                    continue
                x, y, z = point
                ax.scatter(
                    [x], [y], [z],
                    marker="o",
                    s=125,
                    facecolors="white",
                    edgecolors="black",
                    linewidths=2.0,
                    depthshade=False,
                    zorder=30,
                )
                ax.scatter(
                    [x], [y], [z],
                    marker="x",
                    s=48,
                    color="black",
                    linewidths=1.7,
                    depthshade=False,
                    zorder=31,
                )

            for event in recent_merge_events:
                x, y, z = event["point"]
                ax.scatter(
                    [x], [y], [z],
                    marker="*",
                    s=280,
                    facecolors="gold",
                    edgecolors="black",
                    linewidths=1.5,
                    depthshade=False,
                    zorder=40,
                )
                ax.text(
                    x, y, z,
                    rf"  merge $\varepsilon^*={event['epsilon']:.4g}$",
                    fontsize=8,
                    color="black",
                    zorder=41,
                    bbox=dict(
                        boxstyle="round,pad=0.18",
                        facecolor="white",
                        edgecolor="0.45",
                        alpha=0.90,
                    ),
                )

        if show_labels:
            for edge_id, edge in self.__G.edges.items():
                n1_id, n2_id = edge
                n1, n2 = self.__G.nodes[n1_id], self.__G.nodes[n2_id]
                z_label = 0.02 * max(self.__C.vertex_dists[-1], 1.0)
                ax.text(
                    (n2[0] + n1[0]) / 2,
                    (n2[1] + n1[1]) / 2,
                    z_label,
                    str(edge_id),
                    color="black",
                    size=10,
                )

        coverage = self.__freespace.component_coverage()

        if show_legend and self.__freespace.num_components > 0:
            handles = []
            for component_id in self.__freespace.components:
                component_coverage = coverage.get(component_id, {})
                graph_pct = 100.0 * component_coverage.get("graph_fraction", 0.0)
                curve_pct = 100.0 * component_coverage.get("curve_fraction", 0.0)
                handles.append(
                    Line2D(
                        [0], [0],
                        marker="s", linestyle="",
                        markerfacecolor=component_colors[component_id],
                        markeredgecolor="black", markersize=8,
                        label=(
                            f"Component {component_id}  "
                            f"G {graph_pct:.0f}%  C {curve_pct:.0f}%"
                        ),
                    )
                )
            if show_critical_contacts and self.__freespace.critical_contacts:
                handles.append(
                    Line2D(
                        [0], [0], marker="o", linestyle="",
                        markerfacecolor="white", markeredgecolor="black",
                        markeredgewidth=1.5, markersize=8,
                        label="Point-only contact at current epsilon",
                    )
                )
            if show_critical_contacts and recent_merge_events:
                merge_epsilon = max(event["epsilon"] for event in recent_merge_events)
                handles.append(
                    Line2D(
                        [0], [0], marker="*", linestyle="",
                        markerfacecolor="gold", markeredgecolor="black",
                        markeredgewidth=1.2, markersize=11,
                        label=f"Most recent merge (epsilon*={merge_epsilon:.4g})",
                    )
                )
            ncols = min(3, max(1, int(np.ceil(len(handles) / 7))))
            ax.legend(
                handles=handles,
                loc="upper left",
                bbox_to_anchor=(0.0, 1.0),
                fontsize="small",
                ncol=ncols,
                framealpha=0.9,
            )

        self._set_display_scale_3d(
            ax,
            graph_scale=graph_scale,
            curve_scale=curve_scale,
            equal_data_scale=equal_data_scale,
        )

        if show_title:
            n = self.__freespace.num_components
            word = "component" if n == 1 else "components"
            contacts = len(self.__freespace.critical_contacts)
            contact_text = (
                f"   |   {contacts} point-only contact"
                + ("" if contacts == 1 else "s")
                if contacts
                else ""
            )
            merge_text = ""
            if recent_merge_events:
                latest = max(event["epsilon"] for event in recent_merge_events)
                merge_text = rf"   |   last merge $\varepsilon^*={latest:.4g}$"
            ax.set_title(
                rf"$\varepsilon = {self.__freespace.epsilon:.4g}$   |   {n} {word}"
                + contact_text + merge_text,
                pad=12,
            )

        return {
            "component_colors": component_colors,
            "coverage": coverage,
            "recent_merge_events": recent_merge_events,
            "effective_highlight": effective_highlight,
            "component_artists": component_artists,
        }

    @staticmethod
    def _draw_projection_coverage_axis(
        ax,
        structure,
        coverage,
        component_colors,
        interval_key,
        fraction_key,
        title,
    ):
        """Draw one input geometry with per-component projection coverage.

        Coverage from different free-space components may overlap on the same
        input edge.  Small perpendicular offsets turn those overlaps into
        parallel colored tracks rather than hiding one component underneath
        another.
        """
        ax.clear()
        ax.set_facecolor((1.0, 1.0, 1.0, 0.92))
        ax.set_title(title, fontsize=9, pad=3)
        ax.axis("off")

        if not structure.nodes:
            return

        coords = np.asarray(list(structure.nodes.values()), dtype=float)
        x_range = float(np.ptp(coords[:, 0])) if len(coords) else 1.0
        y_range = float(np.ptp(coords[:, 1])) if len(coords) else 1.0
        extent = max(x_range, y_range, 1.0)

        # Base geometry.
        for edge in structure.edges.values():
            a = np.asarray(structure.nodes[edge[0]], dtype=float)
            b = np.asarray(structure.nodes[edge[1]], dtype=float)
            ax.plot(
                [a[0], b[0]], [a[1], b[1]],
                color="0.72", linewidth=4.5, solid_capstyle="round", zorder=1,
            )
        ax.scatter(coords[:, 0], coords[:, 1], s=9, color="0.30", zorder=2)

        component_ids = sorted(component_colors)
        # One percent of the geometry extent is enough to separate coincident
        # tracks without visually changing the underlying shape.
        track_step = 0.010 * extent
        center = 0.5 * (len(component_ids) - 1)

        for index, component_id in enumerate(component_ids):
            component_data = coverage.get(component_id, {})
            intervals_by_edge = component_data.get(interval_key, {})
            offset_amount = (index - center) * track_step
            color = component_colors[component_id]

            for edge_id, intervals in intervals_by_edge.items():
                if edge_id not in structure.edges:
                    continue
                edge = structure.edges[edge_id]
                a = np.asarray(structure.nodes[edge[0]], dtype=float)
                b = np.asarray(structure.nodes[edge[1]], dtype=float)
                direction = b - a
                length = float(np.linalg.norm(direction))
                if length > 1e-15:
                    normal = np.array([-direction[1], direction[0]]) / length
                else:
                    normal = np.zeros(2)
                shift = offset_amount * normal

                for start, end in intervals:
                    p0 = a + float(start) * direction + shift
                    p1 = a + float(end) * direction + shift
                    ax.plot(
                        [p0[0], p1[0]], [p0[1], p1[1]],
                        color=color, linewidth=4.0, solid_capstyle="round", zorder=5,
                    )

        # Compact percentage key inside the inset.
        y = 0.02
        for component_id in component_ids[:8]:
            fraction = coverage.get(component_id, {}).get(fraction_key, 0.0)
            ax.text(
                0.02, y, f"C{component_id}: {100.0 * fraction:.0f}%",
                transform=ax.transAxes, ha="left", va="bottom", fontsize=7,
                color=component_colors[component_id],
                bbox=dict(boxstyle="round,pad=0.12", facecolor="white",
                          edgecolor="none", alpha=0.78),
                zorder=10,
            )
            y += 0.085

        ax.set_aspect("equal", adjustable="datalim")
        ax.margins(0.12)

    def _draw_coverage_insets(
        self, graph_ax, curve_ax, draw_state, highlight_component=None
    ):
        if graph_ax is None or curve_ax is None:
            return
        coverage = draw_state["coverage"]
        colors = draw_state["component_colors"]
        if highlight_component in colors:
            colors = {highlight_component: colors[highlight_component]}
        self._draw_projection_coverage_axis(
            graph_ax, self.__freespace.g1, coverage, colors,
            "graph_intervals", "graph_fraction", "Graph coverage",
        )
        self._draw_projection_coverage_axis(
            curve_ax, self.__freespace.g2, coverage, colors,
            "curve_intervals", "curve_fraction", "Curve coverage",
        )

    def _component_id_for_cell(self, cell_key):
        """Return the current component containing a product cell, if any."""
        if cell_key is None or self.__freespace is None:
            return None
        for component_id, cells in self.__freespace.components.items():
            if cell_key in cells:
                return component_id
        return None

    def _install_component_click_handler(
        self, fig, ax, state_holder, selection, redraw
    ):
        """Make rendered free-space components clickable.

        Clicking a component selects it.  The main view fades the other
        components and the coverage insets show only the selected component's
        projections.  Clicking the selected component again, or pressing
        Escape, restores the full component/coverage view.
        """
        def clear_selection():
            selection["component_id"] = None
            selection["representative"] = None
            selection["user_selected"] = True

        def on_pick(event):
            component_id = getattr(event.artist, "_fsd_component_id", None)
            if component_id not in self.__freespace.components:
                return

            if selection.get("component_id") == component_id:
                clear_selection()
            else:
                selection["component_id"] = component_id
                selection["representative"] = min(
                    self.__freespace.components[component_id]
                )
                selection["user_selected"] = True

            redraw(preserve_view=True)
            fig.canvas.draw_idle()

        def on_key_press(event):
            if event.key != "escape":
                return
            if (
                selection.get("component_id") is None
                and selection.get("representative") is None
            ):
                return
            clear_selection()
            redraw(preserve_view=True)
            fig.canvas.draw_idle()

        pick_cid = fig.canvas.mpl_connect("pick_event", on_pick)
        key_cid = fig.canvas.mpl_connect("key_press_event", on_key_press)

        # Keep strong references to the closures for the life of the window.
        fig._fsdvis_component_click_callbacks = (
            on_pick, on_key_press, pick_cid, key_cid
        )

    def plotFreeSpace(
        self,
        figure_filename=None,
        show_cells=True,
        show_labels=True,
        show_legend=True,
        show_critical_contacts=True,
        highlight_component=None,
        highlight_point=None,
        graph_scale=1.0,
        curve_scale=1.0,
        equal_data_scale=False,
        traversal_distances=None,
        show_coverage_inset=True,
    ):
        if self.__freespace is None:
            raise RuntimeError("buildFreeSpace(epsilon) must be called before plotFreeSpace().")

        if show_coverage_inset:
            # Wide layout: a near-square 3-D viewport plus a genuine side panel
            # for the two input geometries.  This uses the wide desktop window
            # instead of shrinking/clipping the 3-D box inside a square figure.
            fig = plt.figure(figsize=(13.0, 9.5))
            ax = fig.add_axes([0.01, 0.02, 0.73, 0.96], projection="3d")
            graph_cov_ax = fig.add_axes([0.765, 0.42, 0.215, 0.23])
            curve_cov_ax = fig.add_axes([0.765, 0.14, 0.215, 0.23])
        else:
            fig = plt.figure(figsize=(9.5, 9.5))
            ax = fig.add_axes([0.01, 0.01, 0.98, 0.98], projection="3d")
            graph_cov_ax = curve_cov_ax = None
        ax.set_anchor("C")
        draw_state = self._draw_free_space_3d(
            ax,
            show_cells=show_cells,
            show_labels=show_labels,
            show_legend=show_legend,
            show_critical_contacts=show_critical_contacts,
            highlight_component=highlight_component,
            highlight_point=highlight_point,
            graph_scale=graph_scale,
            curve_scale=curve_scale,
            equal_data_scale=equal_data_scale,
            print_summary=True,
        )

        selection = {
            "component_id": draw_state["effective_highlight"],
            "representative": None,
            "user_selected": False,
        }
        if selection["component_id"] in self.__freespace.components:
            selection["representative"] = min(
                self.__freespace.components[selection["component_id"]]
            )
        state_holder = {"draw_state": draw_state}
        fixed_colors = dict(draw_state["component_colors"])

        if show_coverage_inset:
            self._draw_coverage_insets(
                graph_cov_ax, curve_cov_ax, draw_state,
                highlight_component=selection["component_id"],
            )
        self._add_distance_panel(fig, traversal_distances)

        def redraw_selection(preserve_view=False):
            view_state = self._capture_view_3d(ax) if preserve_view else None
            component_id = selection.get("component_id")
            if selection.get("representative") is not None:
                component_id = self._component_id_for_cell(
                    selection["representative"]
                )
                selection["component_id"] = component_id

            new_state = self._draw_free_space_3d(
                ax,
                show_cells=show_cells,
                show_labels=show_labels,
                show_legend=show_legend,
                show_critical_contacts=show_critical_contacts,
                highlight_component=component_id,
                highlight_point=None,
                graph_scale=graph_scale,
                curve_scale=curve_scale,
                equal_data_scale=equal_data_scale,
                component_colors=fixed_colors,
                rebuild_free_space=False,
                strict_highlight=False,
                print_summary=False,
            )
            state_holder["draw_state"] = new_state
            if show_coverage_inset:
                self._draw_coverage_insets(
                    graph_cov_ax, curve_cov_ax, new_state,
                    highlight_component=component_id,
                )
            if preserve_view:
                self._restore_view_3d(ax, view_state)
            return new_state

        if figure_filename is None:
            self._install_component_click_handler(
                fig, ax, state_holder, selection, redraw_selection
            )
            plt.show()
        else:
            fig.savefig(figure_filename, bbox_inches="tight")
            plt.close(fig)

    def _default_epsilon_slider_max(self):
        """Return an epsilon large enough to make every cell feasible.

        The distance between a point on one segment and a point on another is
        convex over the product parameter square, so its maximum is attained at
        a corner.  Therefore the maximum distance between an input graph vertex
        and an input curve vertex is a natural upper end for the slider.
        """
        if not self.__G.nodes or not self.__C.nodes:
            return 1.0

        max_distance = 0.0
        for graph_point in self.__G.nodes.values():
            g = np.asarray(graph_point, dtype=float)
            for curve_point in self.__C.nodes.values():
                c = np.asarray(curve_point, dtype=float)
                max_distance = max(max_distance, float(np.linalg.norm(g - c)))
        return max(max_distance, 1e-9)

    def plotFreeSpaceSlider(
        self,
        epsilon,
        epsilon_min=0.0,
        epsilon_max=None,
        slider_step=None,
        show_cells=True,
        show_labels=True,
        show_legend=True,
        show_critical_contacts=True,
        highlight_component=None,
        highlight_point=None,
        graph_scale=1.0,
        curve_scale=1.0,
        equal_data_scale=False,
        traversal_distances=None,
        show_coverage_inset=True,
    ):
        """Show an interactive 3-D free-space plot with an epsilon slider.

        Moving the slider rebuilds the exact cell free spaces and connected
        components.  The current camera orientation and interactive zoom are retained across updates.
        Component colors are also kept as stable as possible: a component whose
        lexicographically smallest product cell persists keeps its previous
        color.
        """
        epsilon = float(epsilon)
        epsilon_min = float(epsilon_min)
        if epsilon_max is None:
            epsilon_max = max(self._default_epsilon_slider_max(), epsilon)
        epsilon_max = float(epsilon_max)

        if epsilon_min < 0.0:
            raise ValueError("epsilon_min must be nonnegative")
        if epsilon_max <= epsilon_min:
            raise ValueError("epsilon_max must be larger than epsilon_min")
        if not epsilon_min <= epsilon <= epsilon_max:
            raise ValueError(
                f"initial epsilon {epsilon} must lie in [{epsilon_min}, {epsilon_max}]"
            )
        if slider_step is not None and slider_step <= 0:
            raise ValueError("slider_step must be positive")

        if self.__cells is None:
            self.buildCells()

        if show_coverage_inset:
            fig = plt.figure(figsize=(13.0, 9.5))
            ax = fig.add_axes([0.01, 0.105, 0.73, 0.885], projection="3d")
            graph_cov_ax = fig.add_axes([0.765, 0.44, 0.215, 0.22])
            curve_cov_ax = fig.add_axes([0.765, 0.17, 0.215, 0.22])
            slider_ax = fig.add_axes([0.10, 0.035, 0.60, 0.035])
        else:
            fig = plt.figure(figsize=(9.5, 9.5))
            ax = fig.add_axes([0.01, 0.105, 0.98, 0.885], projection="3d")
            graph_cov_ax = curve_cov_ax = None
            slider_ax = fig.add_axes([0.12, 0.035, 0.76, 0.035])
        ax.set_anchor("C")
        self._add_distance_panel(fig, traversal_distances)

        # Color registry survives epsilon changes.  When components split or
        # merge, the child/merged component containing the same minimum cell
        # keeps the same color.
        color_registry = {}
        next_color_index = 0
        tab20 = plt.get_cmap("tab20")
        fallback = plt.get_cmap("hsv")

        def current_component_colors():
            nonlocal next_color_index
            colors = {}
            for component_id, cells in sorted(self.__freespace.components.items()):
                representative = min(cells)
                if representative not in color_registry:
                    if next_color_index < 20:
                        color = tab20(next_color_index)
                    else:
                        # Golden-ratio spacing avoids repeatedly choosing nearby
                        # hues when more than 20 colors are needed.
                        hue = (next_color_index * 0.6180339887498949) % 1.0
                        color = fallback(hue)
                    color_registry[representative] = color
                    next_color_index += 1
                colors[component_id] = color_registry[representative]
            return colors

        selection = {
            "component_id": highlight_component,
            "representative": None,
            "user_selected": False,
        }
        state_holder = {"draw_state": {}}

        def rebuild_and_draw(value=None, preserve_view=False):
            view_state = self._capture_view_3d(ax) if preserve_view else None

            if value is not None:
                self.buildFreeSpace(float(value))
                self.__freespace.build_cell_boundaries_3D()

            component_id = selection.get("component_id")
            if selection.get("representative") is not None:
                component_id = self._component_id_for_cell(
                    selection["representative"]
                )
                selection["component_id"] = component_id

            colors = current_component_colors()
            use_highlight_point = (
                highlight_point
                if not selection.get("user_selected")
                and selection.get("representative") is None
                and component_id is None
                else None
            )
            draw_state = self._draw_free_space_3d(
                ax,
                show_cells=show_cells,
                show_labels=show_labels,
                show_legend=show_legend,
                show_critical_contacts=show_critical_contacts,
                highlight_component=component_id,
                highlight_point=use_highlight_point,
                graph_scale=graph_scale,
                curve_scale=curve_scale,
                equal_data_scale=equal_data_scale,
                component_colors=colors,
                rebuild_free_space=False,
                strict_highlight=False,
                print_summary=False,
                show_title=True,
            )
            selected_now = draw_state["effective_highlight"]
            selection["component_id"] = selected_now
            if (
                selection.get("representative") is None
                and selected_now in self.__freespace.components
            ):
                selection["representative"] = min(
                    self.__freespace.components[selected_now]
                )

            state_holder["draw_state"] = draw_state
            if show_coverage_inset:
                self._draw_coverage_insets(
                    graph_cov_ax, curve_cov_ax, draw_state,
                    highlight_component=selected_now,
                )

            if preserve_view:
                self._restore_view_3d(ax, view_state)
            return draw_state

        rebuild_and_draw(epsilon)
        self._install_component_click_handler(
            fig, ax, state_holder, selection,
            lambda preserve_view=False: rebuild_and_draw(
                value=None, preserve_view=preserve_view
            ),
        )

        slider = Slider(
            ax=slider_ax,
            label=r"$\varepsilon$",
            valmin=epsilon_min,
            valmax=epsilon_max,
            valinit=epsilon,
            valstep=slider_step,
            valfmt="%1.4g",
        )

        # Small ticks on the epsilon axis show connectivity-changing thresholds.
        # They make it easy to stop exactly where components merge.
        merge_thresholds = sorted({
            round(float(event["epsilon"]), 10)
            for event in self._build_connectivity_merge_events()
            if epsilon_min <= event["epsilon"] <= epsilon_max
        })
        for threshold in merge_thresholds:
            slider_ax.axvline(
                threshold, color="goldenrod", linewidth=1.1, alpha=0.85, zorder=8
            )

        def on_epsilon_changed(value):
            rebuild_and_draw(value, preserve_view=True)
            fig.canvas.draw_idle()

        slider.on_changed(on_epsilon_changed)

        # Keep a live reference so the widget is not garbage-collected while
        # the Matplotlib window is open.
        fig._epsilon_slider = slider
        plt.show()

    def plot(self, figure_filename=None, show_labels=True):
        fig, ax = plt.subplots()
        ax.set_aspect(1.0)
        graph_nodes = []

        for edge_id, edge in self.__G.edges.items():
            n1_id, n2_id = edge
            n1, n2 = self.__G.nodes[n1_id], self.__G.nodes[n2_id]

            if n1 not in graph_nodes:
                graph_nodes.append(n1)
            if n2 not in graph_nodes:
                graph_nodes.append(n2)

            ax.plot([n1[0], n2[0]], [n1[1], n2[1]], color="black", linewidth=2)
            if show_labels:
                ax.text(
                    (n2[0] + n1[0]) / 2,
                    ((n2[1] + n1[1]) / 2) + 0.25,
                    str(edge_id),
                    color="black",
                    size=12,
                )

        if graph_nodes:
            lons, lats = map(list, zip(*graph_nodes))
            ax.scatter(lons, lats, s=35, c="black")

        for edge in self.__C.edges.values():
            n1_id, n2_id = edge
            n1, n2 = self.__C.nodes[n1_id], self.__C.nodes[n2_id]
            ax.plot([n1[0], n2[0]], [n1[1], n2[1]], "--", color="dimgray", linewidth=3)

        fig.tight_layout()
        if figure_filename is None:
            plt.show()
        else:
            fig.savefig(figure_filename, bbox_inches="tight")
            plt.close(fig)

    def set_graph(self, G):
        self.__G = G
        self.__sigma_G = G
        self.__merge_events = None

    def set_curve(self, C):
        self.__C = C
        self.__sigma_C = C
        self.__merge_events = None
