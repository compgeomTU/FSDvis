"""
Author:
    Carola Wenk
    cwenk@tulane.edu

Contributors:
    Rena Repenning
    www.renarepenning.com

    Emily Powers
    epowers3@tulane.edu
"""


from traversalDistance.CalFreeSpace import calfreespace
from traversalDistance.LineIntersection import find_ellipse_max_min_points


class FreeSpaceGraph:
    def __init__(self, g1, g2, epsilon):
        self.g1 = g1  # g1, g2 are Graph objects
        self.g2 = g2
        self.e = epsilon
        self.cell_boundaries = {}
        '''get these dynamically, for each --> given one fsbound print the adjacent'''
        # Horizontal boundaries
        for v in self.g2.nodes.keys():
            for e in self.g1.edges.keys():
                self.cell_boundaries[(g2, v, g1, e)] = CellBoundary(g2, v, g1, e, self.e)
        # Verticle boundaries
        for v in self.g1.nodes.keys():
            for e in self.g2.edges.keys():
                self.cell_boundaries[(g1, v, g2, e)] = CellBoundary(g1, v, g2, e, self.e)

    def print_cbs(self):
        print("-- Cell Boundaries --\n", print(self.cell_boundaries), "\n")


    """ DFS Diagram: for all neighbors--> for 2 horizontals and one vertical
        boundaries are lined, vertices are in (), the ellipse boundaries are shown without outlining ellipse

            G2 g_edges
                .
                .
                .
 (right vertex) .________________
                |         |  __ .
                |               .
            cb  |   (ellipse)   .
         edge 2 | __            .
                |    |          .
                |_______________..  .  .  .  . G1 g_verts
              (V)     edge 1    (neighbor)
    (left vertex)

    """
    def DFS(self, cb, f, p, paths, curr_path): # f is written to a file, p is written for the path
        #new line in f is a new dfs call
        f.write("\n")
        cb.visited = True
        # go thru neighboring edges from given vertexID
        for neighbor in cb.g_verts.nodeLink[cb.vertexID]:
            # Find max/min coords of cb's ellipse
            G1, G2 = cb.g_verts, cb.g_edges
            edge1 = [G1.nodes[cb.vertexID], G1.nodes[neighbor]]
            x, y = G2.edges[cb.edgeID] # pair of vertex ids
            edge2 = [G2.nodes[x], G2.nodes[y]]
            f.write("edge1=" + str(edge1) + "   edge2=" + str(edge2)+"\n")
            min1, max1, min2, max2 = find_ellipse_max_min_points(line1=edge1, line2=edge2, epsilon=self.e)

            # get neighboring edge nodes
            left_vertexID, right_vertexID = cb.g_edges.edges[cb.edgeID]
            for V in [left_vertexID, right_vertexID]:
                """ HORIZONTAL Boundaries --> left_vertex:bottom, right_vertex:top """
                if (cb.vertexID, neighbor) in cb.g_verts.edgeHash:
                    new_edgeID = cb.g_verts.edgeHash[(cb.vertexID, neighbor)]
                    newCB = self.cell_boundaries[(cb.g_verts, V, cb.g_edges, new_edgeID)] # creating new cell boundary from "flipping" horiz --> vertical
                    f.write("start + end values: " +
                            str(newCB.start_fs) + " " + str(newCB.end_fs)+"\n")
                    if newCB.visited == False and newCB.start_fs < newCB.end_fs:
                        p.write("DFS -- add "+str(newCB.print_cellboundary())+"\n")
                        newCB.start_p = min1  # from block calling ellipse
                        newCB.end_p = max1
                        self.DFS(newCB, f, p, paths,
                                 curr_path+(newCB.add_cd_str()))
                    else:
                        #p.write("DFS -- basecase -> dont return path\n")
                        paths += [curr_path]
            # end for thru L,R
            """ VERTICAL Boundary"""
            newCB = self.cell_boundaries[(cb.g_verts, neighbor, cb.g_edges, cb.edgeID)] # connect v's of same type
            f.write("start + end values: " + str(newCB.start_fs) + " " + str(newCB.end_fs)+"\n")
            if newCB.visited == False and newCB.start_fs < newCB.end_fs:
                f.write("DFS -- add "+str(newCB.print_cellboundary())+"\n")
                newCB.start_p = min2  # from block calling ellipse
                newCB.end_p = max2
                # recursive call on the edge that hasn't been called yet
                self.DFS(newCB, f, p, paths, curr_path+(newCB.add_cd_str()))
            else:
                #p.write("DFS -- basecase -> dont return path\n")
                paths += [curr_path]
        # end for iterating thru Vi
        f.write("\nDFS success!!!\n")
        p.write("paths: "+str(paths)+"\n")

    # TODO: FIX TO TEST INSERTING IN EMPTY SET
    # STEP 1: print mycb's w function to figure out start and end intervals
    def compute_union(self, intervals, mycb):
        Sx, Ex = mycb.start_p, mycb.end_p
        mycb.print_cellboundary()
        #print("--start: ", Sx, "--end: ", Ex, "  --intervals: ", intervals)
        flag = ""
        if len(intervals) == 0:
            intervals += [(mycb)]
            print("WAS EMPTY", intervals)
            return intervals
        # entirely before
        if Sx > intervals[len(intervals)-1][1]:
            intervals += [(Sx, Ex)]
            print("BEFORE" , intervals)
            return intervals
        # entirely after
        elif Ex < intervals[0][0]:
            intervals = [(Sx, Ex)] + intervals
            print("AFTER" , intervals)
            return intervals

        #to remove
        inside_intervals = []

        for i in range(len(intervals)):
            if Sx <= intervals[i][0]:
                #add smaller interval to list to remove
                inside_intervals.append(intervals[i])
                #check if Ex covers more than current interval
                if Ex <= intervals[i][1]:
                    #readjust the new interval to include Sx
                    new_interval = (Sx, intervals[i][1])
                    break
            elif Sx <= intervals[i][1]:
                #reset starting index to be min in interval
                Sx = intervals[i][0]
                inside_intervals.append(intervals[i])

        print("to remove:", inside_intervals)
        print("new interval=", new_interval)

        new = [i for i in intervals if i not in inside_intervals]
        new.append(new_interval)
        print("THIS ONE" , new)
        return new

    # TODO:
    # STEP 2: check with compute union to track cbs, print what you are inputting into calls
    def check_projection(self):
        # assumes g1 is horiz and g2 is vert
        f = open("outputs/check_projection.txt", "w")
        # all_cbs = { edgeID : output of compute_union }
        all_cbs = {}
        f.write("self.cell_boundaries:\n ")
        f.write(str(self.cell_boundaries)+"\n")
        f.write("self.G1="+str(self.g1)+"\n")
        f.write("\nfor cb in self.cell_boundaries")
        #pick an edge id and only look at contents of that edge id just for a single edge
        for cb in self.cell_boundaries:
            mycb = self.cell_boundaries[cb]
            f.write("\nmycb="+str(mycb))
            f.write("\n   g_edges="+str(mycb.g_edges))
            if mycb.g_edges == self.g1:
                if mycb.edgeID in all_cbs:
                    f.write("\n   mycb:   edgeID="+str(mycb.edgeID) +
                            "   start_p="+str(mycb.start_p)+"   end_p="+str(mycb.end_p))
                    #FIX BELOW
                    print(all_cbs[mycb.edgeID])
                    print(mycb)
                    all_cbs[mycb.edgeID] = self.compute_union(all_cbs[mycb.edgeID], mycb)
                else:
                    # adds first (single white interval)
                    # map --> [pairs] --- sorted list of (s,e) pairs will be the val
                    all_cbs[mycb.edgeID] = [(mycb.start_p, mycb.end_p)]
        f.write("\n\n for pairs in union:")
        for key in all_cbs:
            intervals = all_cbs[key]
            f.write("\n intervals="+str(intervals))
            # we want intervals to be start=0 and end=1
            if len(intervals) == 1:
                if intervals[0][0] != 0 or intervals[0][1] != 1:
                    f.write(" --> is false")
                    return False
            else:
                return False
        # if intervals cover all edges
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
    def __init__(self, g_verts, vertexID, g_edges, edgeID, eps):
        # use ID's consistant with Erfan's code
        self.vertexID = vertexID
        self.edgeID = edgeID
        self.g_edges = g_edges
        self.g_verts = g_verts
        self.visited = False
        self.start_p = 0
        self.end_p = 0

        edge = g_edges.edges[self.edgeID]
        # inputs for CFS
        x1 = g_edges.nodes[edge[0]][1]  # --> id of vertex, x-coord
        y1 = g_edges.nodes[edge[0]][0]
        x2 = g_edges.nodes[edge[1]][1]
        y2 = g_edges.nodes[edge[1]][0]
        xa = g_verts.nodes[vertexID][0]
        ya = g_verts.nodes[vertexID][1]

        # call CFS and return tuple --> compute from free space by traversing the free space
        self.start_fs, self.end_fs = calfreespace(
            x1, y1, x2, y2, xa, ya, eps)  # start/end of freespace


    def print_cellboundary(self):
        print("V: " + str(self.vertexID) + " E: " + str(self.edgeID) + " start: " + str(self.start_p) + " end: " + str(self.end_p))


    def add_cd_str(self):
        if self.g_verts.nodes[0][0] == 0 and self.g_verts.nodes[0][1] == -3:
            isRectangleGraph = "v"
        else:
            isRectangleGraph = "u"
        return isRectangleGraph+str(self.vertexID) + "," + str(self.edgeID)+" -> "
