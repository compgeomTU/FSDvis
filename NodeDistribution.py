
from traversalDistance.Graph import Graph
from Curve import Curve
from GraphByCurve import GraphByCurve
import numpy as np

def graph_node_distribution(graph, n_distributions):
    sigma_graph = Graph()

    node_id_gen = lambda i, n0id, n1id: int(f"{i+1}000{n0id}000{n1id}")
    edge_id_gen = lambda i, eid: int(f"{i}000{eid}")

    for edge_id, edge in graph.edges.items():

        # declaring edge informaion
        node_id_0, node_id_1 = edge[0], edge[1]
        node_0, node_1 = graph.nodes[node_id_0], graph.nodes[node_id_1]

        # adding node 1 to new graph
        node_id_init = node_id_gen(0, node_id_0, node_id_1)
        sigma_graph.addNode(node_id_init, node_0[0], node_0[1])

        # functions for new nodes across edge
        denominator = node_1[0] - node_0[0]
        if denominator == 0.0: denominator = 1
        slope = (node_1[1] - node_0[1]) / denominator
        step = (node_1[0] - node_0[0]) / (n_distributions - 1)
        x = lambda i: step * i + node_0[0]
        y = lambda i: slope * step * i + node_0[1]

        # adding nodes across old edge for n_distributions:
        for i in range(1, n_distributions):
            u, v = x(i), y(i)

            node_id_i = node_id_gen(i, node_id_0, node_id_1)
            node_id_im1 = node_id_gen(i-1, node_id_0, node_id_1)
            edge_id_i = edge_id_gen(i, edge_id)

            sigma_graph.addNode(node_id_i, u, v)
            sigma_graph.connectTwoNodes(edge_id_i, node_id_im1, node_id_i)

    return sigma_graph

def curve_node_distribution(curve, n_distributions):
    sigma_curve = Curve()

    node_id_idx = 0
    edge_id_idx = 0

    # adding node 1 to new graph
    sigma_curve.addNode(node_id_idx, curve.nodes[0][0], curve.nodes[0][1])
    node_id_idx += 1;

    for edge_id, edge in curve.edges.items():

        # declaring edge informaion
        node_id_0, node_id_1 = edge[0], edge[1]
        node_0, node_1 = curve.nodes[node_id_0], curve.nodes[node_id_1]

        # functions for new nodes across edge
        denominator = node_1[0] - node_0[0]
        if denominator == 0.0: denominator = 1
        slope = (node_1[1] - node_0[1]) / denominator
        step = (node_1[0] - node_0[0]) / (n_distributions - 1)
        x = lambda i: step * i + node_0[0]
        y = lambda i: slope * step * i + node_0[1]

        # adding nodes across old edge for n_distributions:
        for i in range(0, n_distributions):
            u, v = x(i), y(i)

            sigma_curve.addNode(node_id_idx, u, v)
            sigma_curve.connectTwoNodes(edge_id_idx, node_id_idx-1, node_id_idx)
            node_id_idx += 1;
            edge_id_idx += 1;

    sigma_curve.compute_vertex_dists()

    return sigma_curve

graph = graph_node_distribution(Graph("samples/P"), 10)
curve = curve_node_distribution(Curve("samples/Q"), 10)
ctg = GraphByCurve(graph, curve)
ctg.buildCells()
ctg.buildFreeSpace(1)
ctg.plotFreeSpace()
