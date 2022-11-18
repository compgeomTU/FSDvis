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
from tracemalloc import start
from turtle import end_fill, up

def compute_union_old(intervals, mycb):
    sx = mycb.start_p
    ex = mycb.end_p
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
        
'''we will start with an empty list of tuples beacuse initializing one doesn't run properly
we will add in at least one? tuple cell boundary at a time?? 
    if it's just one we can just add an if statement for the intervals being empty
    it would need to get called for each cb we look at while tracking the same intervals list
    
    if its more than one im confused i think'''

"""assume current intervals are sorted"""
#TODO: fix second input for case (should be a cb object that accesses the start_p, end_p in the list)
# Takes in sorted interval list and list with start_p, end_p
case1 = [0, .1, .2, .5, .8, 1], [.6, .7] # in between intervals --> [0, .1, .2, .5, .6, .7, .8, 1] remove: []
case2 = [0, .1, .2, .5, .7, .9], [.6, .8] # reassign start --> [0, .1, .2, .5, .6, .9] remove:[.7, .8]
case5 = [.2, .5, .7, .9], [.1, .3] # reassign start and end --> [.1, .5, .7, .9] remove:[.2, .3]
case3 = [0, .1, .2, .5], [.6, .8] # add end interval --> [0, .1, .2, .5, .6, .8] remove:[]
case4 = [.3, .4, .6, .8], [0, .1] # add start interval --> [0, .1, .3, .4, .6, .8] remove:[]
case6 = [.2, .7,  .8, .9], [.6, .75] # reassign start and end --> [.2, .75, .8, .9] remove:[.6, .7]
case7 = [.1, .19, .2, .5, .7, .9, .91, .93], [.15, .22] # reassign start and take out middle interval --> [.1, .22, .5, .7, .9, .91, .93] remove: [.15, .19, .2]
case8 = [.01, .1, .2, .5, .7, .9], [.03, .8] # --> [.01, .9] remove: [.03, .1, .2, .5, .7, .8]
case9 = [.01, .1, .2, .5, .7, .9], [.3, .91] # --> [.01, .1, .2, .91] remove: [.3, .5, .7, .9]
case10 = [], [.25, .65] # --> [.25, .65] remove: []


c = case1
print("final = ", compute_union_old(c[0], c[1]))
'''
sorted set of list items not tuples just know index being odd or even has significance
ALWAYS ADD SX FIRST
{a, sx, b, c, d, ex, e, f}
evens are all start
odds are all end
if end is even round up
if start is odd round down
insert function python
sx even and ex odd -->
sx odd and ex even --> remove [sxi]
sx even and ex even --> remove [sxi+1...exi+1]
sx odd and ex odd -->
'''