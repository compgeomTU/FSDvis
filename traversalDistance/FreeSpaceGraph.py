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
import logging

class FreeSpaceGraph:
    def __init__(self, g1, g2, epsilon):
        self.g1 = g1  # g1, g2 are Graph objects
        self.g2 = g2
        self.e = epsilon
        self.cell_boundaries = {}
        '''get these dynamically, for each --> given one fsbound print the adjacent'''
        # Horizontal boundaries
        logging.info("Horizontal: vertices from H, edges from G")
        for v in self.g2.nodes.keys():
            for e in self.g1.edges.keys():
                self.cell_boundaries[("g2", v, "g1", e)] = CellBoundary(g2, v, g1, e, self.e)
                logging.info("v: " + str(v) + " e: " + str(e) + " mycb: " + str(self.cell_boundaries[("g2", v, "g1", e)]))
        # Verticle boundaries
        logging.info("Vertical: vertices from G, edges from H")
        for v in self.g1.nodes.keys():
            for e in self.g2.edges.keys():
                self.cell_boundaries[("g1", v, "g2", e)] = CellBoundary(g1, v, g2, e, self.e)
                logging.info("v: " + str(v) + " e: " + str(e) + " mycb: " + str(self.cell_boundaries[("g1", v, "g2", e)]))

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
                    new_edgeID = cb.g_verts.edgeHash[(cb.vertexID, neighbor)] #on vertex graph
                    #newCB doesn't find the key
                    newCB = self.cell_boundaries[(cb.g_edges, V, cb.g_verts, new_edgeID)] # creating new cell boundary from "flipping" horiz --> vertical
                    f.write("start + end values: " +
                            str(newCB.start_fs) + " " + str(newCB.end_fs)+"\n")
                    #SHOULD THIS BE <= OR STRICTLY <
                    if newCB.visited == False and newCB.start_fs <= newCB.end_fs:
                        p.write("DFS -- add "+str(newCB.print_cellboundary())+"\n")
                        print("horizontal start_p min1", min1)
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
            #SHOULD THIS BE <= OR STRICTLY <
            if newCB.visited == False and newCB.start_fs <= newCB.end_fs:
                f.write("DFS -- add "+str(newCB.print_cellboundary())+"\n")
                print("vertical start_p min2", min2)
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


    def compute_union(self, intervals, mycb):
        sx = int(mycb.start_p)
        ex = int(mycb.end_p)
        i = 0
        sxi = -1
        exi = -1
        while i < len(intervals) + 2:
            if sxi == -1:
                if sx < intervals[i]:
                    intervals.insert(i,sx)
                    sxi = i
                    i +=1
                    flag = 1
            elif exi == -1:
                if ex < intervals[i]:
                    intervals.insert(i,ex)
                    exi = i
                    i +=1
                    flag = 2
            i+=1
        if sxi == -1 and exi == -1:
            intervals.append(sx)
            intervals.append(ex)
        if sxi != -1 and exi == -1:
            intervals.append(ex)

        if sxi % 2 == 0 and exi % 2 == 1:
            intervals = intervals[0:sxi+1] + intervals[exi:]
        elif sxi % 2 == 0 and exi % 2 == 0:
            intervals = intervals[0:sxi+1] + intervals[exi+1:]
        elif sxi % 2 == 1 and exi % 2 == 0:
            intervals = intervals[0:sxi] + intervals[exi+1:]
        elif sxi % 2 == 1 and exi % 2 == 1:
            intervals = intervals[0:sxi] + intervals[exi:]

        return intervals


    ''' OLD COMPUTE UNION
    def compute_union(self, intervals, mycb):
        Sx, Ex = mycb.start_p, mycb.end_p
        mycb.print_cellboundary()
        #print("--start: ", Sx, "--end: ", Ex, "  --intervals: ", intervals)
        flag = ""
        #print("INTERVAL", intervals[len(intervals)-1])
        if len(intervals) == 0:
            intervals = [(Sx, Ex)] + intervals
            logging.info("WAS EMPTY"+ str(intervals))
            return intervals
        # entirely before
        if Sx > intervals[len(intervals)-1][1]:
            intervals += [(Sx, Ex)]
            logging.info("BEFORE"+ str(intervals))
            return intervals
        # entirely after
        elif Ex < intervals[0][0]:
            intervals = [(Sx, Ex)] + intervals
            logging.info("AFTER"+ str(intervals))
            return intervals

        #to remove
        inside_intervals = []
        #to keep
        new = []

        for i in range(len(intervals)):
            if Sx <= intervals[i][0]:
                #add smaller interval to list to remove
                inside_intervals.append(intervals[i])
                #check if Ex covers more than current interval
                if Ex <= intervals[i][1]:
                    #readjust the new interval to include Sx
                    new_interval = (Sx, intervals[i][1])
                    new.append(new_interval)
                    return new
                    #NEST BELOW LOGIC INTO HERE JUST RETURN DON'T BREAK AND A RETURN IN THE END
                else:
                    new += (i for i in intervals if i not in inside_intervals)
                    #THIS MIGHT NOT BE THE RIGHT LINE
                    new += [(Sx, Ex)]
                    return new
            #less than the end and greater than start (inside)
            elif Sx <= intervals[i][1]:
                #reset starting index to be min in interval
                Sx = intervals[i][0]
                inside_intervals.append(intervals[i])
                new += (i for i in intervals if i not in inside_intervals)
                #need to add in new interval or check for the end
                return new
            else:
                return new


        #print("to remove:", inside_intervals)
        #print("new interval=", new_interval)

        new = [i for i in intervals if i not in inside_intervals]
        new.append(new_interval)
        #print("NEW INTERVAL" , new)
        return new
    '''

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
            #if mycb.g_edges == self.g1:
            if mycb.edgeID in all_cbs:
                f.write("\n   mycb:   edgeID="+str(mycb.edgeID) +
                        "   start_p="+str(mycb.start_p)+"   end_p="+str(mycb.end_p))
                #FIX BELOW
                logging.info("ALL CBS"+ str(all_cbs[mycb.edgeID]))
                logging.info("MY CB"+ str(mycb))
                logging.info("EDGEID"+ str(mycb.edgeID))
                all_cbs[mycb.edgeID]
                #temp is generator object here
                temp = self.compute_union(all_cbs[mycb.edgeID], mycb)
                logging.info("INTERVAL: " + str(temp))
                all_cbs[mycb.edgeID] = temp
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
        print("DFS", self.DFS(cb, f, p, [], ""))
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
        x1 = g_edges.nodes[edge[0]][0]  # --> id of vertex, x-coord
        y1 = g_edges.nodes[edge[0]][1]
        x2 = g_edges.nodes[edge[1]][0]
        y2 = g_edges.nodes[edge[1]][1]
        xa = g_verts.nodes[vertexID][0]
        ya = g_verts.nodes[vertexID][1]

        # call CFS and return tuple --> compute from free space by traversing the free space
        self.start_fs, self.end_fs = calfreespace(
            x1, y1, x2, y2, xa, ya, eps)  # start/end of freespace


    def print_cellboundary(self):
        print("V_ID: " + str(self.vertexID) + " E_ID: " + str(self.edgeID) + " start: " + str(self.start_p) + " end: " + str(self.end_p))


    def add_cd_str(self):
        if self.g_verts.nodes[0][0] == 0 and self.g_verts.nodes[0][1] == -3:
            isRectangleGraph = "v"
        else:
            isRectangleGraph = "u"
        return isRectangleGraph+str(self.vertexID) + "," + str(self.edgeID)+" -> "
