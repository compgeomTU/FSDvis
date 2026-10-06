# Author:
#   Will Rodman - Tulane University
#   wrodman@tulane.edu
#
# -----------------------------------------------------------------------------
#
# Source Repository:
#   GitHub.com compgeomTU/mapmatching FreeSpace.py
#

import logging
import math
from itertools import combinations

import numpy as np

class FreeSpace:
    """Free-space diagram plus visualization/component metadata.

    ``cell_boundaries_3D`` is kept for backwards compatibility.  The richer
    ``free_space_cells`` dictionary stores, for every non-empty free-space cell,
    its 2-D cell coordinates, mapped 3-D polygon, and connected-component ID.
    """

    def __init__(self, G, C, epsilon):
        self.g1 = G
        self.g2 = C
        self.epsilon = float(epsilon)
        self.cell_boundaries = {}
        self.cell_boundaries_3D = []
        self.free_space_area = 0.0

        # Number of radial samples used to draw the curved boundary of the
        # exact free-space region inside one parameter cell.  Emptiness is
        # decided analytically, so an interior component cannot be missed even
        # if it is much smaller than this display resolution.
        self.free_space_boundary_samples = 128

        # (graph_edge_id, curve_edge_id) -> metadata dictionary
        self.free_space_cells = {}
        # (graph_edge_id, curve_edge_id) -> 1-based component ID
        self.cell_component_ids = {}
        # component ID -> sorted list of cell keys
        self.components = {}
        self.num_components = 0
        # Degenerate shared free-space boundaries that consist of a single
        # point and connect two or more non-empty cells.
        self.critical_contacts = []

    @staticmethod
    def _boundary_nonempty(cb):
        return cb.start_fs != -1.0 and cb.end_fs != -1.0

    def build_cell_boundaries_3D(self):
        """Build mapped free-space polygons and their connected components.

        This method is safe to call repeatedly: all derived visualization data
        are rebuilt from scratch each time.
        """
        self.cell_boundaries_3D.clear()
        self.free_space_cells.clear()
        self.cell_component_ids.clear()
        self.components.clear()
        self.num_components = 0
        self.critical_contacts.clear()

        logging.info("--------------- Cell Boundary Structure ---------------")
        for k, cb in self.cell_boundaries.items():
            is_log = False
            if k[0] == "g1":
                is_log = True
            elif k[0] == "g2":
                is_log = True
            if is_log and self._boundary_nonempty(cb):
                logging.info(
                    "   CB Key: %s   Boundary: |%s --- %s|",
                    k,
                    cb.start_fs,
                    cb.end_fs,
                )

        logging.info("--------------- FreeSpace Structure ---------------")
        for G_id, G_edge in self.g1.edges.items():
            for C_id, C_edge in self.g2.edges.items():
                xs, ys = self.buildFreeSpaceCell(G_id, C_id, G_edge, C_edge)
                logging.info(
                    "   Cell:   GEID: %s   CEID: %s   GE: %s   CE: %s",
                    G_id,
                    C_id,
                    G_edge,
                    C_edge,
                )

                if xs and ys:
                    G_n1_id, G_n2_id = G_edge
                    G_n1_x, G_n2_x = self.g1.nodes[G_n1_id][0], self.g1.nodes[G_n2_id][0]
                    G_n1_y, G_n2_y = self.g1.nodes[G_n1_id][1], self.g1.nodes[G_n2_id][1]
                    C_n1_id, C_n2_id = C_edge
                    C_l_z = self.g2.vertex_dists[C_n1_id]
                    C_u_z = self.g2.vertex_dists[C_n2_id]

                    us, vs, ws = self.map_(
                        G_n1_x,
                        G_n2_x,
                        G_n1_y,
                        G_n2_y,
                        C_l_z,
                        C_u_z,
                        xs,
                        ys,
                    )
                    vertices_3d = list(zip(us, vs, ws))
                    cell_key = (G_id, C_id)
                    geometry_type = self._geometry_type(xs, ys)

                    self.cell_boundaries_3D.append((us, vs, ws))
                    self.free_space_cells[cell_key] = {
                        "graph_edge_id": G_id,
                        "curve_edge_id": C_id,
                        "graph_edge": tuple(G_edge),
                        "curve_edge": tuple(C_edge),
                        "xs": xs,
                        "ys": ys,
                        "vertices_3d": vertices_3d,
                        "geometry_type": geometry_type,
                        "component_id": None,
                    }

                    logging.info("      FS (%s)    x:    %s", geometry_type, xs)
                    logging.info("                  y:    %s", ys)
                    logging.info("      Mapped FS   u(x): %s", us)
                    logging.info("                  v(y): %s", vs)
                    logging.info("                  w(z): %s", ws)
                else:
                    logging.info("      EMPTY       x:    %s", xs)
                    logging.info("                  y:    %s", ys)

        self._compute_connected_components()
        self._compute_critical_contacts()
        return self.free_space_cells

    def _compute_connected_components(self):
        """Assign components to non-empty free-space cells.

        Each cell free-space patch is convex.  Two patches are joined exactly
        when their product cells share a non-empty free-space boundary.  This is
        the same connectivity relation used by the traversal-distance DFS, but
        we evaluate the point-to-segment boundary interval directly so tangency
        (a one-point interval) is handled robustly.
        """
        cell_keys = set(self.free_space_cells.keys())
        if not cell_keys:
            return

        parent = {key: key for key in cell_keys}
        rank = {key: 0 for key in cell_keys}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            if rank[ra] < rank[rb]:
                ra, rb = rb, ra
            parent[rb] = ra
            if rank[ra] == rank[rb]:
                rank[ra] += 1

        # Vertical product boundaries: a graph vertex paired with a curve edge.
        for graph_vertex_id, graph_vertex in self.g1.nodes.items():
            incident_graph_edges = [
                edge_id
                for edge_id, edge in self.g1.edges.items()
                if graph_vertex_id in edge
            ]
            if len(incident_graph_edges) < 2:
                continue

            for curve_edge_id, curve_edge in self.g2.edges.items():
                interval = self._point_segment_free_interval(
                    graph_vertex,
                    self.g2.nodes[curve_edge[0]],
                    self.g2.nodes[curve_edge[1]],
                )
                if interval is None:
                    continue
                adjacent = [
                    (graph_edge_id, curve_edge_id)
                    for graph_edge_id in incident_graph_edges
                    if (graph_edge_id, curve_edge_id) in cell_keys
                ]
                for a, b in combinations(adjacent, 2):
                    union(a, b)

        # Horizontal product boundaries: a curve vertex paired with a graph edge.
        for curve_vertex_id, curve_vertex in self.g2.nodes.items():
            incident_curve_edges = [
                edge_id
                for edge_id, edge in self.g2.edges.items()
                if curve_vertex_id in edge
            ]
            if len(incident_curve_edges) < 2:
                continue

            for graph_edge_id, graph_edge in self.g1.edges.items():
                interval = self._point_segment_free_interval(
                    curve_vertex,
                    self.g1.nodes[graph_edge[0]],
                    self.g1.nodes[graph_edge[1]],
                )
                if interval is None:
                    continue
                adjacent = [
                    (graph_edge_id, curve_edge_id)
                    for curve_edge_id in incident_curve_edges
                    if (graph_edge_id, curve_edge_id) in cell_keys
                ]
                for a, b in combinations(adjacent, 2):
                    union(a, b)

        grouped = {}
        for cell_key in sorted(cell_keys):
            grouped.setdefault(find(cell_key), []).append(cell_key)

        # Deterministic 1-based IDs, ordered by the lexicographically smallest
        # cell in each component.  This keeps colors stable across runs.
        ordered_groups = sorted(grouped.values(), key=lambda group: min(group))
        for component_id, group in enumerate(ordered_groups, start=1):
            group = sorted(group)
            self.components[component_id] = group
            for cell_key in group:
                self.cell_component_ids[cell_key] = component_id
                self.free_space_cells[cell_key]["component_id"] = component_id

        self.num_components = len(self.components)
        logging.info("Free-space connected components: %s", self.num_components)

    def _compute_critical_contacts(self, tolerance=1e-9):
        """Record point-only shared boundaries that glue free-space patches.

        These are visually easy to miss, but topologically important: at a
        critical epsilon, two patches may meet in exactly one point and hence
        already belong to the same connected component.
        """
        self.critical_contacts.clear()
        cell_keys = set(self.free_space_cells.keys())
        seen = set()

        def add_contact(point, adjacent, boundary_type, ids):
            if len(adjacent) < 2:
                return
            component_ids = {
                self.cell_component_ids[cell]
                for cell in adjacent
                if cell in self.cell_component_ids
            }
            if not component_ids:
                return
            key = tuple(round(float(x), 10) for x in point)
            if key in seen:
                return
            seen.add(key)
            self.critical_contacts.append(
                {
                    "point": tuple(float(x) for x in point),
                    "component_id": min(component_ids),
                    "adjacent_cells": sorted(adjacent),
                    "boundary_type": boundary_type,
                    "ids": ids,
                }
            )

        # Graph vertex x curve edge.
        for graph_vertex_id, graph_vertex in self.g1.nodes.items():
            incident_graph_edges = [
                edge_id
                for edge_id, edge in self.g1.edges.items()
                if graph_vertex_id in edge
            ]
            if len(incident_graph_edges) < 2:
                continue
            gx, gy = graph_vertex
            for curve_edge_id, curve_edge in self.g2.edges.items():
                interval = self._point_segment_free_interval(
                    graph_vertex,
                    self.g2.nodes[curve_edge[0]],
                    self.g2.nodes[curve_edge[1]],
                )
                if interval is None or abs(interval[1] - interval[0]) > tolerance:
                    continue
                adjacent = [
                    (graph_edge_id, curve_edge_id)
                    for graph_edge_id in incident_graph_edges
                    if (graph_edge_id, curve_edge_id) in cell_keys
                ]
                s = 0.5 * (interval[0] + interval[1])
                z0 = float(self.g2.vertex_dists[curve_edge[0]])
                z1 = float(self.g2.vertex_dists[curve_edge[1]])
                z = z0 + s * (z1 - z0)
                add_contact(
                    (gx, gy, z),
                    adjacent,
                    "graph-vertex/curve-edge",
                    (graph_vertex_id, curve_edge_id),
                )

        # Curve vertex x graph edge.
        for curve_vertex_id, curve_vertex in self.g2.nodes.items():
            incident_curve_edges = [
                edge_id
                for edge_id, edge in self.g2.edges.items()
                if curve_vertex_id in edge
            ]
            if len(incident_curve_edges) < 2:
                continue
            z = float(self.g2.vertex_dists[curve_vertex_id])
            for graph_edge_id, graph_edge in self.g1.edges.items():
                interval = self._point_segment_free_interval(
                    curve_vertex,
                    self.g1.nodes[graph_edge[0]],
                    self.g1.nodes[graph_edge[1]],
                )
                if interval is None or abs(interval[1] - interval[0]) > tolerance:
                    continue
                adjacent = [
                    (graph_edge_id, curve_edge_id)
                    for curve_edge_id in incident_curve_edges
                    if (graph_edge_id, curve_edge_id) in cell_keys
                ]
                t = 0.5 * (interval[0] + interval[1])
                a = np.asarray(self.g1.nodes[graph_edge[0]], dtype=float)
                b = np.asarray(self.g1.nodes[graph_edge[1]], dtype=float)
                point = a + t * (b - a)
                add_contact(
                    (point[0], point[1], z),
                    adjacent,
                    "curve-vertex/graph-edge",
                    (curve_vertex_id, graph_edge_id),
                )

    @staticmethod
    def _merge_intervals(intervals, tolerance=1e-10):
        """Merge overlapping/adjacent intervals in [0,1]."""
        if not intervals:
            return []
        ordered = sorted((float(a), float(b)) for a, b in intervals)
        merged = [list(ordered[0])]
        for start, end in ordered[1:]:
            if start <= merged[-1][1] + tolerance:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        return [tuple(interval) for interval in merged]

    def component_coverage(self):
        """Return exact projection coverage of each free-space component.

        For every component, this reports the covered parameter intervals on
        each graph edge and each curve edge, together with covered Euclidean
        length and fraction of the total input length.  The interval endpoints
        are computed analytically from point-to-segment distance, not from the
        sampled display polygon.
        """
        if not self.free_space_cells:
            self.build_cell_boundaries_3D()

        graph_edge_lengths = {
            edge_id: math.dist(self.g1.nodes[edge[0]], self.g1.nodes[edge[1]])
            for edge_id, edge in self.g1.edges.items()
        }
        curve_edge_lengths = {
            edge_id: math.dist(self.g2.nodes[edge[0]], self.g2.nodes[edge[1]])
            for edge_id, edge in self.g2.edges.items()
        }
        graph_total = sum(graph_edge_lengths.values())
        curve_total = sum(curve_edge_lengths.values())

        result = {}
        for component_id, cells in self.components.items():
            graph_intervals = {edge_id: [] for edge_id in self.g1.edges}
            curve_intervals = {edge_id: [] for edge_id in self.g2.edges}

            for graph_edge_id, curve_edge_id in cells:
                graph_edge = self.g1.edges[graph_edge_id]
                curve_edge = self.g2.edges[curve_edge_id]
                A = self.g1.nodes[graph_edge[0]]
                B = self.g1.nodes[graph_edge[1]]
                P = self.g2.nodes[curve_edge[0]]
                Q = self.g2.nodes[curve_edge[1]]

                graph_interval = self._projection_interval_on_first_segment(
                    A, B, P, Q, self.epsilon
                )
                curve_interval = self._projection_interval_on_first_segment(
                    P, Q, A, B, self.epsilon
                )
                if graph_interval is not None:
                    graph_intervals[graph_edge_id].append(graph_interval)
                if curve_interval is not None:
                    curve_intervals[curve_edge_id].append(curve_interval)

            graph_intervals = {
                edge_id: self._merge_intervals(intervals)
                for edge_id, intervals in graph_intervals.items()
                if intervals
            }
            curve_intervals = {
                edge_id: self._merge_intervals(intervals)
                for edge_id, intervals in curve_intervals.items()
                if intervals
            }

            graph_covered = sum(
                graph_edge_lengths[edge_id] * sum(b - a for a, b in intervals)
                for edge_id, intervals in graph_intervals.items()
            )
            curve_covered = sum(
                curve_edge_lengths[edge_id] * sum(b - a for a, b in intervals)
                for edge_id, intervals in curve_intervals.items()
            )

            result[component_id] = {
                "graph_intervals": graph_intervals,
                "curve_intervals": curve_intervals,
                "graph_covered_length": graph_covered,
                "curve_covered_length": curve_covered,
                "graph_total_length": graph_total,
                "curve_total_length": curve_total,
                "graph_fraction": (graph_covered / graph_total) if graph_total > 0 else 0.0,
                "curve_fraction": (curve_covered / curve_total) if curve_total > 0 else 0.0,
            }

        return result

    def component_summary(self):
        """Return component IDs and the free-space cells belonging to each."""
        if not self.free_space_cells:
            self.build_cell_boundaries_3D()
        return {component_id: list(cells) for component_id, cells in self.components.items()}

    def calculateArea(self):
        """Calculate free-space area; safe to call repeatedly."""
        self.free_space_area = 0.0

        for G_id, G_edge in self.g1.edges.items():
            for C_id, C_edge in self.g2.edges.items():
                xs, ys = self.buildFreeSpaceCell(G_id, C_id, G_edge, C_edge)
                if len(xs) > 2 and len(ys) > 2:
                    cb_area = 0.5 * np.abs(
                        np.dot(xs, np.roll(ys, 1)) - np.dot(ys, np.roll(xs, 1))
                    )

                    G_n1_id, G_n2_id = G_edge
                    G_n1_x, G_n2_x = self.g1.nodes[G_n1_id][0], self.g1.nodes[G_n2_id][0]
                    G_n1_y, G_n2_y = self.g1.nodes[G_n1_id][1], self.g1.nodes[G_n2_id][1]
                    C_n1_id, C_n2_id = C_edge
                    C_l_z = self.g2.vertex_dists[C_n1_id]
                    C_u_z = self.g2.vertex_dists[C_n2_id]

                    scale = math.dist(
                        [G_n1_x, G_n1_y], [G_n2_x, G_n2_y]
                    ) * abs(C_u_z - C_l_z)
                    self.free_space_area += cb_area * scale

        return self.free_space_area

    @staticmethod
    def _clip01(value):
        return min(1.0, max(0.0, float(value)))

    @classmethod
    def _closest_parameters(cls, A, B, P, Q):
        """Return parameters (t,s) minimizing |(A+t(B-A))-(P+s(Q-P))|.

        The objective is a convex quadratic on the unit square.  We test the
        unconstrained stationary point (when it exists) and the exact minimum
        on each of the four sides.
        """
        A = np.asarray(A, dtype=float)
        B = np.asarray(B, dtype=float)
        P = np.asarray(P, dtype=float)
        Q = np.asarray(Q, dtype=float)
        u = B - A
        v = Q - P
        w = A - P

        uu = float(np.dot(u, u))
        vv = float(np.dot(v, v))
        uv = float(np.dot(u, v))
        uw = float(np.dot(u, w))
        vw = float(np.dot(v, w))

        candidates = []

        def add(t, s):
            t, s = cls._clip01(t), cls._clip01(s)
            d = w + t * u - s * v
            candidates.append((float(np.dot(d, d)), t, s))

        det = uu * vv - uv * uv
        scale = max(1.0, uu * vv)
        if det > 1e-14 * scale:
            t = (-uw * vv + uv * vw) / det
            s = (uu * vw - uv * uw) / det
            if -1e-12 <= t <= 1.0 + 1e-12 and -1e-12 <= s <= 1.0 + 1e-12:
                add(t, s)

        # t fixed, optimize s.
        for t in (0.0, 1.0):
            if vv > 1e-15:
                s = float(np.dot(v, w + t * u) / vv)
            else:
                s = 0.0
            add(t, s)

        # s fixed, optimize t.
        for s in (0.0, 1.0):
            if uu > 1e-15:
                t = float(-np.dot(u, w - s * v) / uu)
            else:
                t = 0.0
            add(t, s)

        # Explicit corners also cover the case of two zero-length segments.
        for t in (0.0, 1.0):
            for s in (0.0, 1.0):
                add(t, s)

        _, t, s = min(candidates, key=lambda item: item[0])
        d = w + t * u - s * v
        return t, s, float(np.dot(d, d))

    @staticmethod
    def _quadratic_roots_unit(a, b, c, tolerance=1e-12):
        """Roots of a*x^2+b*x+c=0 that lie in [0,1]."""
        roots = []
        scale = max(1.0, abs(a), abs(b), abs(c))
        tol = tolerance * scale

        if abs(a) <= tol:
            if abs(b) <= tol:
                return roots
            x = -c / b
            if -tolerance <= x <= 1.0 + tolerance:
                roots.append(min(1.0, max(0.0, float(x))))
            return roots

        disc = b * b - 4.0 * a * c
        if disc < -tol:
            return roots
        disc = max(0.0, disc)
        sqrt_disc = math.sqrt(disc)
        for x in ((-b - sqrt_disc) / (2.0 * a), (-b + sqrt_disc) / (2.0 * a)):
            if -tolerance <= x <= 1.0 + tolerance:
                x = min(1.0, max(0.0, float(x)))
                if not any(abs(x - old) <= 1e-10 for old in roots):
                    roots.append(x)
        return roots

    def _point_segment_free_interval(self, point, A, B):
        """Return the parameter interval on segment AB within epsilon of point."""
        point = np.asarray(point, dtype=float)
        A = np.asarray(A, dtype=float)
        B = np.asarray(B, dtype=float)
        direction = B - A
        offset = A - point
        a = float(np.dot(direction, direction))
        b = 2.0 * float(np.dot(direction, offset))
        c = float(np.dot(offset, offset) - self.epsilon * self.epsilon)

        tol = 1e-11 * max(1.0, abs(a), abs(b), abs(c), self.epsilon * self.epsilon)
        if a <= tol:
            return (0.0, 1.0) if c <= tol else None

        roots = self._quadratic_roots_unit(a, b, c, tolerance=1e-12)
        candidates = [0.0, 1.0] + roots
        candidates = sorted(set(self._clip01(x) for x in candidates))

        def q(x):
            return a * x * x + b * x + c

        feasible = []
        for x in candidates:
            if q(x) <= tol:
                feasible.append(x)
        for x0, x1 in zip(candidates, candidates[1:]):
            midpoint = 0.5 * (x0 + x1)
            if q(midpoint) <= tol:
                feasible.extend((x0, x1))

        if not feasible:
            return None
        return min(feasible), max(feasible)

    @classmethod
    def _projection_interval_on_first_segment(cls, A, B, P, Q, epsilon):
        """Exact projection of one cell's free space onto segment AB.

        The function t -> dist(A+t(B-A), segment(P,Q)) is convex and
        piecewise quadratic, so the feasible parameter set is an interval.
        """
        A = np.asarray(A, dtype=float)
        B = np.asarray(B, dtype=float)
        P = np.asarray(P, dtype=float)
        Q = np.asarray(Q, dtype=float)
        u = B - A
        v = Q - P
        w = A - P
        uu = float(np.dot(u, u))
        vv = float(np.dot(v, v))
        uv = float(np.dot(u, v))
        uw = float(np.dot(u, w))
        vw = float(np.dot(v, w))
        ww = float(np.dot(w, w))
        eps2 = float(epsilon) * float(epsilon)

        if uu <= 1e-15:
            _, _, min_dist2 = cls._closest_parameters(A, B, P, Q)
            return (0.0, 1.0) if min_dist2 <= eps2 + 1e-10 else None

        breaks = [0.0, 1.0]
        if vv > 1e-15 and abs(uv) > 1e-15:
            for t in (-vw / uv, (vv - vw) / uv):
                if 0.0 < t < 1.0:
                    breaks.append(float(t))
        breaks = sorted(set(breaks))

        feasible = []
        for left, right in zip(breaks, breaks[1:]):
            mid = 0.5 * (left + right)
            if vv <= 1e-15:
                branch = 0
            else:
                s_star = (vw + uv * mid) / vv
                branch = 0 if s_star <= 0.0 else (1 if s_star >= 1.0 else 2)

            if branch == 0:
                a, b, c = uu, 2.0 * uw, ww - eps2
            elif branch == 1:
                wm = w - v
                a = uu
                b = 2.0 * float(np.dot(u, wm))
                c = float(np.dot(wm, wm)) - eps2
            else:
                a = uu - uv * uv / vv
                b = 2.0 * (uw - vw * uv / vv)
                c = ww - vw * vw / vv - eps2

            roots = cls._quadratic_roots_unit(a, b, c, tolerance=1e-12)
            candidates = [left, right] + [r for r in roots if left - 1e-10 <= r <= right + 1e-10]
            candidates = sorted(set(max(left, min(right, float(x))) for x in candidates))
            tol = 1e-10 * max(1.0, abs(a), abs(b), abs(c), eps2)
            vals = []
            for x in candidates:
                if a*x*x + b*x + c <= tol:
                    vals.append(x)
            for x0, x1 in zip(candidates, candidates[1:]):
                x = 0.5 * (x0 + x1)
                if a*x*x + b*x + c <= tol:
                    vals.extend((x0, x1))
            if vals:
                feasible.append((min(vals), max(vals)))

        for t in breaks:
            X = A + t * u
            if vv <= 1e-15:
                s = 0.0
            else:
                s = cls._clip01(float(np.dot(v, X - P) / vv))
            d = X - (P + s * v)
            if float(np.dot(d, d)) <= eps2 + 1e-10:
                feasible.append((t, t))

        if not feasible:
            return None
        return min(a for a, _ in feasible), max(b for _, b in feasible)

    @staticmethod
    def _local_polygon_area(xs, ys):
        if len(xs) < 3:
            return 0.0
        return 0.5 * abs(
            float(np.dot(xs, np.roll(ys, 1)) - np.dot(ys, np.roll(xs, 1)))
        )

    @classmethod
    def _geometry_type(cls, xs, ys):
        if not xs:
            return "empty"
        if len(xs) == 1:
            return "point"
        if cls._local_polygon_area(xs, ys) > 1e-12:
            return "polygon"
        points = np.column_stack([xs, ys])
        diameter = 0.0
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                diameter = max(diameter, float(np.linalg.norm(points[i] - points[j])))
        return "segment" if diameter > 1e-10 else "point"

    def buildFreeSpaceCell(self, G_id, C_id, G_edge, C_edge):
        """Return the free-space region in one unit parameter cell.

        Unlike the old implementation, this does *not* infer the cell interior
        from its four boundary intervals.  It evaluates the actual quadratic

            ||G(t) - C(s)||^2 <= epsilon^2,   (t,s) in [0,1]^2.

        The closest pair of points on the two segments decides emptiness
        analytically.  If the cell is non-empty, its convex boundary is drawn
        by radial sampling from that closest feasible point, augmented by the
        exact intersections with the four sides of the unit square.  Hence a
        small component entirely inside a cell is retained rather than lost.
        """
        A = np.asarray(self.g1.nodes[G_edge[0]], dtype=float)
        B = np.asarray(self.g1.nodes[G_edge[1]], dtype=float)
        P = np.asarray(self.g2.nodes[C_edge[0]], dtype=float)
        Q = np.asarray(self.g2.nodes[C_edge[1]], dtype=float)
        u = B - A
        v = Q - P
        w = A - P
        eps2 = self.epsilon * self.epsilon

        t0, s0, min_dist2 = self._closest_parameters(A, B, P, Q)
        numeric_tol = 1e-11 * max(1.0, eps2, min_dist2)
        if min_dist2 > eps2 + numeric_tol:
            return [], []

        def q(t, s):
            d = w + t * u - s * v
            return float(np.dot(d, d) - eps2)

        points = []

        def add_point(t, s):
            t, s = self._clip01(t), self._clip01(s)
            if q(t, s) > 10.0 * numeric_tol:
                return
            for old_t, old_s in points:
                if abs(t - old_t) <= 1e-9 and abs(s - old_s) <= 1e-9:
                    return
            points.append((t, s))

        # Feasible corners are true vertices of the clipped region.
        for t, s in ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)):
            if q(t, s) <= numeric_tol:
                add_point(t, s)

        # Exact conic/square-boundary intersections.
        uu = float(np.dot(u, u))
        vv = float(np.dot(v, v))

        for s in (0.0, 1.0):
            d0 = w - s * v
            a = uu
            b = 2.0 * float(np.dot(d0, u))
            c = float(np.dot(d0, d0) - eps2)
            for t in self._quadratic_roots_unit(a, b, c):
                add_point(t, s)

        for t in (0.0, 1.0):
            d0 = w + t * u
            a = vv
            b = -2.0 * float(np.dot(d0, v))
            c = float(np.dot(d0, d0) - eps2)
            for s in self._quadratic_roots_unit(a, b, c):
                add_point(t, s)

        # The closest point is always feasible and gives a center from which
        # every ray meets the boundary exactly once because the cell free space
        # is convex.  Analytic roots avoid any grid-resolution emptiness bug.
        center_t, center_s = t0, s0
        D0 = w + center_t * u - center_s * v
        c0 = min(0.0, float(np.dot(D0, D0) - eps2))

        sample_count = max(32, int(self.free_space_boundary_samples))
        for k in range(sample_count):
            theta = 2.0 * math.pi * k / sample_count
            dt, ds = math.cos(theta), math.sin(theta)

            r_box = float("inf")
            if dt > 1e-15:
                r_box = min(r_box, (1.0 - center_t) / dt)
            elif dt < -1e-15:
                r_box = min(r_box, -center_t / dt)
            if ds > 1e-15:
                r_box = min(r_box, (1.0 - center_s) / ds)
            elif ds < -1e-15:
                r_box = min(r_box, -center_s / ds)

            if not math.isfinite(r_box) or r_box < -1e-12:
                continue
            r_box = max(0.0, r_box)

            end_t = center_t + r_box * dt
            end_s = center_s + r_box * ds
            if q(end_t, end_s) <= numeric_tol:
                r = r_box
            else:
                W = dt * u - ds * v
                a = float(np.dot(W, W))
                b = 2.0 * float(np.dot(D0, W))
                if a <= 1e-16:
                    if b > 1e-16:
                        r = -c0 / b
                    else:
                        r = 0.0
                else:
                    disc = max(0.0, b * b - 4.0 * a * c0)
                    r = (-b + math.sqrt(disc)) / (2.0 * a)
                r = min(r_box, max(0.0, r))

            add_point(center_t + r * dt, center_s + r * ds)

        if not points:
            # This can only happen through extreme floating-point degeneracy.
            add_point(center_t, center_s)

        # Order boundary points cyclically.  For a non-degenerate convex region
        # the closest feasible point is inside or on its boundary; angle sorting
        # therefore gives a valid polygonal approximation.
        points.sort(key=lambda p: math.atan2(p[1] - center_s, p[0] - center_t))

        # Remove collinear/duplicate clutter along square sides while preserving
        # the sampled curved portions.
        cleaned = []
        for point in points:
            if not cleaned or math.dist(point, cleaned[-1]) > 1e-9:
                cleaned.append(point)
        if len(cleaned) > 1 and math.dist(cleaned[0], cleaned[-1]) <= 1e-9:
            cleaned.pop()

        xs = [p[0] for p in cleaned]
        ys = [p[1] for p in cleaned]
        return xs, ys

    @staticmethod
    def _point_on_segment(px, py, ax, ay, bx, by, tolerance=1e-9):
        cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax)
        scale = max(1.0, abs(bx - ax), abs(by - ay))
        if abs(cross) > tolerance * scale:
            return False
        dot = (px - ax) * (bx - ax) + (py - ay) * (by - ay)
        if dot < -tolerance:
            return False
        squared_length = (bx - ax) ** 2 + (by - ay) ** 2
        return dot <= squared_length + tolerance

    @classmethod
    def _point_in_polygon(cls, x, y, xs, ys, tolerance=1e-9):
        """Boundary-inclusive point-in-polygon test for a local free-space cell."""
        n = len(xs)
        if n < 3:
            return False

        for i in range(n):
            j = (i + 1) % n
            if cls._point_on_segment(
                x, y, xs[i], ys[i], xs[j], ys[j], tolerance=tolerance
            ):
                return True

        inside = False
        j = n - 1
        for i in range(n):
            yi, yj = ys[i], ys[j]
            xi, xj = xs[i], xs[j]
            if (yi > y) != (yj > y):
                x_intersection = (xj - xi) * (y - yi) / (yj - yi) + xi
                if x < x_intersection:
                    inside = not inside
            j = i
        return inside

    def find_component_containing_point(self, point, tolerance=1e-7):
        """Return the component containing a 3-D free-space point.

        ``point`` is ``(x, y, z)`` in the plotted coordinate system: ``(x,y)``
        lies on the graph and ``z`` is arc length along the curve.  Membership
        is checked against the exact distance inequality, not against the
        polygon used only for rendering.
        """
        if not self.free_space_cells:
            self.build_cell_boundaries_3D()

        px, py, pz = point
        matching_components = set()
        pxy = np.asarray([px, py], dtype=float)

        for cell_key, record in self.free_space_cells.items():
            graph_edge_id, curve_edge_id = cell_key
            graph_edge = self.g1.edges[graph_edge_id]
            g0 = np.asarray(self.g1.nodes[graph_edge[0]], dtype=float)
            g1 = np.asarray(self.g1.nodes[graph_edge[1]], dtype=float)
            direction = g1 - g0
            squared_length = float(np.dot(direction, direction))
            if squared_length == 0.0:
                if float(np.linalg.norm(pxy - g0)) > tolerance:
                    continue
                t = 0.0
            else:
                t = float(np.dot(pxy - g0, direction) / squared_length)
                if t < -tolerance or t > 1.0 + tolerance:
                    continue
                projection = g0 + t * direction
                if float(np.linalg.norm(pxy - projection)) > tolerance:
                    continue
                t = self._clip01(t)

            curve_edge = self.g2.edges[curve_edge_id]
            z0 = float(self.g2.vertex_dists[curve_edge[0]])
            z1 = float(self.g2.vertex_dists[curve_edge[1]])
            dz = z1 - z0
            if abs(dz) <= tolerance:
                if abs(pz - z0) > tolerance:
                    continue
                s = 0.0
            else:
                s = (pz - z0) / dz
                if s < -tolerance or s > 1.0 + tolerance:
                    continue
                s = self._clip01(s)

            curve_p0 = np.asarray(self.g2.nodes[curve_edge[0]], dtype=float)
            curve_p1 = np.asarray(self.g2.nodes[curve_edge[1]], dtype=float)
            graph_point = g0 + t * direction
            curve_point = curve_p0 + s * (curve_p1 - curve_p0)
            if float(np.linalg.norm(graph_point - curve_point)) <= self.epsilon + tolerance:
                matching_components.add(record["component_id"])

        if not matching_components:
            return None
        # Shared-boundary matches should all have the same component ID.
        return min(matching_components)

    @staticmethod
    def map_(G_n1_x, G_n2_x, G_n1_y, G_n2_y, C_l_z, C_u_z, xs, ys):
        # <x, y> => <u, v, w> linear map
        u = lambda x: (G_n2_x - G_n1_x) * x + G_n1_x
        v = lambda x: (G_n2_y - G_n1_y) * x + G_n1_y
        w = lambda y: (C_u_z - C_l_z) * y + C_l_z

        us = list(map(u, xs))
        vs = list(map(v, xs))
        ws = list(map(w, ys))
        return us, vs, ws
