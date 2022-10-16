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
    testFreeSpaceGraph()
    # PlotGraph()
