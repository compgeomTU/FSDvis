"""
Author:
Rena Repenning
renarepenning@gmail.com

Contributor:
Emily Powers
epowers3@tulane.edu
"""

# TODO: need to take union of all intervals
# compare these two with the items we have in the list
# [(mycb.start_p, mycb.end_p)]

from operator import invert


def compute_union_old(intervals, mycb):
    print("--my cbs: ", mycb, "  --intervals: ", intervals)
    Sx, Ex = mycb
    flag = ""
    if len(intervals) == 0:
        intervals += [(mycb)]
        return intervals
    # entirely before
    if Sx > intervals[len(intervals)-1][1]:
        intervals += [(mycb)]
        return intervals
    # entirely after
    elif Ex < intervals[0][0]:
        intervals = [(mycb)] + intervals
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
    
    return new

'''we will start with an empty list of tuples beacuse initializing one doesn't run properly
we will add in at least one? tuple cell boundary at a time?? 
    if it's just one we can just add an if statement for the intervals being empty
    it would need to get called for each cb we look at while tracking the same intervals list
    
    if its more than one im confused i think'''

"""assume current intervals are sorted"""
# Have empty set and try to insert several intervals to merge together (recursively)
case1 = [(0, .1), (.2, .5), (.8, 1)], (.6, .7)
case2 = [(0, .1), (.2, .5), (.7, .9)], (.6, .8)
case5 = [(.2, .5), (.7, .9)], (.1, .3)
case3 = [(0, .1), (.2, .5)], (.6, .8)
case4 = [(.3, .4), (.6, .8)], (0, .1)
case6 = [(.2, .7),  (.8, .9)], (.6, .75)  # works but not with -1 step
case7 = [(.1, .19), (.2, .5), (.7, .9), (.91, .93)
         ], (.15, .22)  # (.3, .8)  # needs to drop none -- spans two
case9 = [(.01, .1), (.2, .5), (.7, .9)
         ], (.3, .9)
# fails
case8 = [(.01, .1), (.2, .5), (.7, .9)
         ], (.03, .8)  # spans multiple --> needs to drop one smaller

case10 = [], (.25, .65)


c = case10
print("final = ", compute_union_old(c[0], c[1]))
