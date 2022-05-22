# Author:
#    Carola Wenk
#    cwenk@tulane.edu
# Contributors:
#    Rena Repenning
#    www.renarepenning.com
#    Emily Powers
#    epowers3@tulane.edu
#
# -----------------------------------------------------------------------------
#
# Source Repository:
#   GitHub.com compgeomTU/traversalDistance GraphFreeSpace.py
#                                           CalFreeSpace.py

import math

class FreeSpaceGraph:
    def __init__(self, g1, g2, epsilon):
        self.g1 = g1  # g1, g2 are Graph objects
        self.g2 = g2
        self.e = epsilon
        self.cell_boundaries = {}

        # get these dynamically, for each --> given one fsbound print the adjacent
        # Horizontal boundaries
        for v in self.g2.nodes.keys():
            for e in self.g1.edges.keys():
                cb = CellBoundary(v, e, g1, g2, self.e)
                self.cell_boundaries[(v, e, str(g1), str(g2))] = cb
        # Verticle boundaries
        for v in self.g1.nodes.keys():
            for e in self.g2.edges.keys():
                cb = CellBoundary(v, e, g2, g1, self.e)
                self.cell_boundaries[(v, e, str(g2), str(g1))] = cb

    def print_cbs(self):
        print("-- Cell Boundaries --\n", print(self.cell_boundaries), "\n")

    def DFS(self, cb, f, p, paths, curr_path):
        f.write("\n")  # new line means new dfs call
        cb.visited = True
        # go thru neighboring edges from given vertexID
        for neighbor in cb.g_verts.nodeLink[cb.vertexID]:
            # Find max/min coords of cb's ellipse
            G1, G2 = cb.g_verts, cb.g_edges
            edge1 = [G1.nodes[cb.vertexID],
                     G1.nodes[neighbor]]
            x, y = G2.edges[cb.edgeID]  # pair of vertex ids
            edge2 = [G2.nodes[x], G2.nodes[y]]
            f.write("edge1=" + str(edge1) + "   edge2=" + str(edge2)+"\n")
            min1, max1, min2, max2 = find_ellipse_max_min_points(
                line1=edge1, line2=edge2, epsilon=self.e)

            # get neighboring edge nodes
            left_vertexID, right_vertexID = cb.g_edges.edges[cb.edgeID]
            for V in [left_vertexID, right_vertexID]:
                # CASE 1
                if (cb.vertexID, neighbor) in cb.g_verts.edgeHash:
                    new_edgeID = cb.g_verts.edgeHash[(cb.vertexID, neighbor)]
                    newCB = self.cell_boundaries[(
                        V, new_edgeID, cb.g_verts, cb.g_edges)]  # creating new cell boundary from "flipping" horiz --> vertical
                    f.write("start + end values: " +
                            str(newCB.start_fs) + " " + str(newCB.end_fs)+"\n")

                    if newCB.visited == False and newCB.start_fs < newCB.end_fs:
                        p.write("DFS -- add "+newCB.print_cellboundary()+"\n")
                        newCB.start_p = min1  # from block calling ellipse
                        newCB.end_p = max1
                        self.DFS(newCB, f, p, paths,
                                 curr_path+(newCB.add_cd_str()))
                    else:
                        #p.write("DFS -- basecase -> dont return path\n")
                        paths += [curr_path]

                newCB = self.cell_boundaries[(
                    neighbor, cb.edgeID, cb.g_edges, cb.g_verts)]  # connect v's of same type

                f.write("start + end values: " +
                        str(newCB.start_fs) + " " + str(newCB.end_fs)+"\n")
                if newCB.visited == False and newCB.start_fs < newCB.end_fs:
                    f.write("DFS -- add "+newCB.print_cellboundary()+"\n")
                    newCB.start_p = min2  # from block calling ellipse
                    newCB.end_p = max2
                    # recursive call on the edge that hasn't been called yet
                    self.DFS(newCB, f, p, paths,
                             curr_path+(newCB.add_cd_str()))
                else:
                    #p.write("DFS -- basecase -> dont return path\n")
                    paths += [curr_path]
            # end for thru L,R
        # end for iterating thru Vi
        f.write("\nDFS success!!!\n")
        p.write("returned: "+str(paths)+"\n")
        return "DFS success!!!"

    def check_projection(self):
        # assumes g1 is horiz and g2 is vert
        f = open("outputs/check_projection.txt", "w")
        all_cbs = {}
        f.write("self.cell_boundaries:\n ")
        f.write(str(self.cell_boundaries)+"\n")
        f.write("self.G1="+str(self.g1)+"\n")
        f.write("\nfor cb in self.cell_boundaries")
        for cb in self.cell_boundaries:
            mycb = self.cell_boundaries[cb]
            f.write("\nmycb="+str(mycb))
            f.write("\n   g_edges="+str(mycb.g_edges))
            if mycb.g_edges == self.g1:
                if mycb.edgeID in all_cbs:
                    f.write("\n   mycb:   edgeID="+str(mycb.edgeID) +
                            "   start_p="+str(mycb.start_p)+"   end_p="+str(mycb.end_p))
                    # TODO: INSERT COMPUTE UNION FXN
                    """all_cbs[mycb.edgeID] = self.compute_union(
                        all_cbs[mycb.edgeID], mycb)"""
                else:
                    # adds first (single white interval)
                    # map --> [pairs] --- sorted list of (s,e) pairs will be the val
                    all_cbs[mycb.edgeID] = [(mycb.start_p, mycb.end_p)]
        f.write("\n\n for pairs in union:")
        for pairs in all_cbs:
            edge_ids = all_cbs[pairs]
            f.write("\n edge_ids="+str(edge_ids))
            if edge_ids[0] != 0 or edge_ids[1] != 1:
                """ should this be > or < ?? """
                f.write(" --> is false")
                return False
        return True

    def DFSTraversalDist(self, cb):
        # given one free space boundary, compute all adjacent free space boundaries
        f = open("outputs/fsg_dfs.txt", "w")
        p = open("outputs/fsg_path.txt", "w")
        for i in self.cell_boundaries.values():  # mark all bounds in graph false --> incase this has been ran before
            i.visited = False
        print(self.DFS(cb, f, p, [], ""))
        C = self.check_projection()
        print("Projection check: ", C)

class CellBoundary:
    def __init__(self, vertexID, edgeID, g_edges, g_verts, eps):
        # use ID's consistant with Erfan's code
        self.vertexID = vertexID
        self.edgeID = edgeID
        self.g_edges = g_edges
        self.g_verts = g_verts
        self.visited = False
        self.start_p = -1
        self.end_p = -1

        edge = g_edges.edges[self.edgeID]
        # inputs for CFS
        x1 = g_edges.nodes[edge[0]][1]  # --> id of vertex, x-coord
        y1 = g_edges.nodes[edge[0]][0]
        x2 = g_edges.nodes[edge[1]][1]
        y2 = g_edges.nodes[edge[1]][0]
        xa = g_verts.nodes[vertexID][0]
        ya = g_verts.nodes[vertexID][1]

        # call CFS and return tuple --> compute from free space by traversing the free space
        self.start_fs, self.end_fs = self.calfreespace(x1, y1, x2, y2, xa, ya, eps)  # start/end of freespace

    def __str__(self):
        return "| Start = {:04.2f} |--| End = {:04.2f} |".format(self.start_fs, self.end_fs)

    def __repr__(self):
        return self.__str__()

    #easier to rewrite calfreespace than to worry about the import since it's in C
    #(x1, y1) is starting point of edge of G1 (x2, y2) is ending point of edge of G1 (xa, ya) is vertex of G2
    #(start, end) will start as (0,1) and will return as the reachable boundary of free space on that edge as a value between 0-1
    @staticmethod
    def calfreespace(x1, y1, x2, y2, xa, ya, Epsilon):
        xdiff = x2-x1
        ydiff = y2-y1
        divisor = xdiff * xdiff + ydiff * ydiff
        if divisor == 0:
            print("divisor =", divisor, "x1 =", x1, "x2 =", x2, "y1 =", y1, "y2 =", y2)
        b = (xa-x1) * xdiff + (ya-y1) * ydiff
        q = (x1 * x1 + y1 * y1 + xa * xa + ya * ya - 2 * x1 * xa - 2 * y1 * ya - Epsilon * Epsilon) * divisor
        root = b * b - q
        if root < 0:
            start = end = -1
            return (start, end)
        root = math.sqrt(root)
        t2 = (b + root) / divisor
        t1 = (b - root) / divisor
        if t1 < 0:
            t1=0
        if t2 < 0:
            t2=0
        if t1 > 1:
            t1=1
        if t2 > 1:
            t2=1
        start = t1
        end = t2
        if start == end:
            start = -1
            end = -1
        return (start, end)

    def print_cellboundary(self):
        # print("Cell Boundary: ", self.vertexID, self.edgeID)
        return "Cell Boundary: (" + str(self.vertexID)+", " + str(self.edgeID)+")"
        # print("Start: ", self.start)
        # print("End: ", self.end)

    def add_cd_str(self):
        if self.g_verts.nodes[0][0] == 0 and self.g_verts.nodes[0][1] == -3:
            isRectangleGraph = "v"
        else:
            isRectangleGraph = "u"
        return isRectangleGraph+str(self.vertexID) + "," + str(self.edgeID)+" -> "
