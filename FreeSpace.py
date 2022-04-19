import math

#easier to rewrite calfreespace than to worry about the import since it's in C
#(x1, y1) is starting point of edge of G1 (x2, y2) is ending point of edge of G1 (xa, ya) is vertex of G2
#(start, end) will start as (0,1) and will return as the reachable boundary of free space on that edge as a value between 0-1
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
    start=end=-1 
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
    start=-1
    end=-1
  return (start, end)
