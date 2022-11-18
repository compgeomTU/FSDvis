"""
Author:
    Carola Wenk
    cwenk@tulane.edu
    
Contributors:
    Rena Repenning
    renarepenning@gmail.com, www.renarepenning.com

    Emily Powers
    epowers3@tulane.edu
    
    Will Rodman
    wrodman@tulane.edu
"""

import geojson
import logging
from geojson import LineString, Feature, FeatureCollection
from Graph import Graph
from CalFreeSpace import calfreespace
from FreeSpaceGraph import FreeSpaceGraph


def testFreeSpaceGraph():
    print("\n -- TESTING FreeSpaceGraph.py -- ")
    g = Graph("sample_graphs/G")
    g.Plot2MatPlotLib()
    h = Graph("sample_graphs/H")
    h.Plot2MatPlotLib()
    #epsilon: 3
    e = 3
    # print("-- G: ", g, " -- H: ", h, " -- eps ", e, "")

    for vertex in g.nodes.keys():
        logging.info("G nodeID " + str(vertex) + " x " + str(g.nodes[vertex][0]) + " y " + str(g.nodes[vertex][1]))
    for edge in g.edges.keys():
        logging.info("G edgeID " + str(edge) + " v1 " + str(g.edges[edge][0]) + " v2 " + str(g.edges[edge][1]))

    for vertex in h.nodes.keys():
        logging.info("H nodeID " + str(vertex) + " x " + str(h.nodes[vertex][0]) + " y " + str(h.nodes[vertex][1]))
    for edge in h.edges.keys():
        logging.info("H edgeID " + str(edge) + " v1 " + str(h.edges[edge][0]) + " v2 " + str(h.edges[edge][1]))
    
    
    fsg = FreeSpaceGraph(g, h, e)
    # print("-- created FSG")

    cb = fsg.cell_boundaries[(g, 0, h, 0)]
    # print("-- take test cell bound:   ", end="")
    # cb.print_cellboundary()

    fsg.DFSTraversalDist(cb)
    # print("-- END -- \n")

    print("G edges: ", g.edges)
    print("H edges: ", h.edges)


def PlotGraph():
    # plots graph to matplotlib
    g = Graph("sample_graphs/G")
    g.Plot2MatPlotLib()
    h = Graph("sample_graphs/H")
    h.Plot2MatPlotLib()
    print("-- Graph Plotted --")


if __name__ == "__main__":
    logging.basicConfig(filename='dfs.log', encoding='utf-8', level=logging.INFO)
    testFreeSpaceGraph()
    # PlotGraph()
