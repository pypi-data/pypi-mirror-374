import networkx as nx
import gurobipy as grb
import datetime
import warnings

from .geometry import *
from .ring import *
from .curveArc import *
from .gridSurface import *
from .common import *
# from .plot import *

# obj2ObjPath =================================================================
def multiPoly2MultiPolyPath(startPt: pt, endPt: pt, multiPolys: list[polys], holes: list[polys]|None, **kwargs):
    outputFlag = False if 'outputFlag' not in kwargs else kwargs['outputFlag']
    gapTol = None if 'gapTol' not in kwargs else kwargs['gapTol']
    timeLimit = None if 'timeLimit' not in kwargs else kwargs['timeLimit']
    
    res = _multiPoly2MultiPolyPathGurobi(startPt, endPt, multiPolys, holes, outputFlag, gapTol, timeLimit)
    return {
        'path': res['path'],
        'dist': res['dist']
    }

def poly2PolyPath(startPt: pt, endPt: pt, polys: polys, algo: str = 'SOCP', **kwargs):
    
    """Given a starting point, a list of polys, and an ending point, returns a shortest route that starts from startPt, visits every polys in given order, and returns to the ending point.

    Parameters
    ----------
    startPt: pt, required, default None
        The coordinate which starts the path.
    endPt: pt, required, default None
        The coordinate which ends the path.
    polys: polys, required
        A list of polys to be visited in given sequence
    algo: str, optional, default as 'SOCP'
        Select the algorithm for calculating the shortest path. Options and required additional inputs are as follows:
            
        1) (default) 'SOCP', use Second-order Cone Programing method.
            - solver: str, optional, now only supports 'Gurobi'
            - timeLimit: int|float, additional stopping criteria
            - gapTolerance: int|float, additional stopping criteria
            - outputFlag: bool, True if turn on the log output from solver. Default to be False
        2) 'AdaptIter', use adapt iteration algorithm
            - errorTol: float, optional, error tolerance
    **kwargs: optional
        Provide additional inputs for different `edges` options and `algo` options

    Returns
    -------
    dict
        Two fields in the dictionary, 'dist' indicates the distance of the path, 'path' indicates the travel path.
    """

    # Sanity check ============================================================
    if (algo == 'AdaptIter'):
        adaptErr = ERRTOL['deltaDist']
        if ('adaptErr' in kwargs):
            adaptErr = kwargs['adaptErr']
        res = _poly2PolyPathAdaptIter(startPt, endPt, polys, adaptErr)
    elif (algo == 'SOCP'):
        outputFlag = False
        if ('outputFlag' in kwargs):
            outputFlag = kwargs['outputFlag']
        gapTol = None
        if ('gapTol' in kwargs):
            gapTol = kwargs['gapTol']
        timeLimit = None
        if ('timeLimit' in kwargs):
            timeLimit = kwargs['timeLimit']
        res = _poly2PolyPathGurobi(startPt, endPt, polys, outputFlag, gapTol, timeLimit)
    else:
        raise UnsupportedInputError("ERROR: Not support by vrpSolver for now.")

    return {
        'path': res['path'],
        'dist': res['dist']
    }

def _poly2PolyPathAdaptIter(startPt: pt, endPt: pt, polys: polys, adaptErr):

    """Given a list of points, each belongs to a neighborhood of a node, find the shortest path between each steps

    Parameters
    ----------

    polys: list of polygons, required
        A list of polygons to be visited
    solver: string, optional, default AVAIL_SOLVER
        The commercial solver used to solve the minimum cost flow problem

    """

    # First, create a ring, to help keying each extreme points of polygons
    tau = {}

    # Initialize
    G = nx.Graph()
    polyRings = []

    for poly in polys:
        polyRing = Ring()
        for i in range(len(poly)):
            polyRing.append(RingNode(i, poly[i]))
        polyRings.append(polyRing)

    # startPt to the first polygon
    cur = polyRings[0].head
    while (True):
        d = distEuclideanXY(startPt, cur.value)
        tau['s', (0, cur.key)] = d
        G.add_edge('s', (0, cur.key), weight = d)
        cur = cur.next
        if (cur.key == polyRings[0].head.key):
            break

    # If more than one polygon btw startPt and endPt
    for i in range(len(polys) - 1):
        curI = polyRings[i].head
        while (True):
            curJ = polyRings[i + 1].head
            while (True):
                d = distEuclideanXY(curI.value, curJ.value)
                tau[(i, curI.key), (i + 1, curJ.key)] = d
                G.add_edge((i, curI.key), (i + 1, curJ.key), weight = d)
                curJ = curJ.next
                if (curJ.key == polyRings[i + 1].head.key):
                    break
            curI = curI.next
            if (curI.key == polyRings[i].head.key):
                break

    # last polygon to endPt
    cur = polyRings[-1].head
    while (True):
        d = distEuclideanXY(cur.value, endPt)
        tau[(len(polys) - 1, cur.key), 'e'] = d
        G.add_edge((len(polys) - 1, cur.key), 'e', weight = d)
        cur = cur.next
        if (cur.key == polyRings[len(polys) - 1].head.key):
            break

    sp = nx.dijkstra_path(G, 's', 'e')

    dist = distEuclideanXY(startPt, polyRings[sp[1][0]].query(sp[1][1]).value)
    for i in range(1, len(sp) - 2):
        dist += tau[(sp[i][0], sp[i][1]), (sp[i + 1][0], sp[i + 1][1])]
    dist += distEuclideanXY(polyRings[sp[-2][0]].query(sp[-2][1]).value, endPt)
    
    # Find detailed location
    refineFlag = True
    iterNum = 0
    while (refineFlag):
        for i in range(1, len(sp) - 1):
            # Find current shortest intersecting point
            polyIdx = sp[i][0]
            exPtIdx = sp[i][1]

            # Insert two new points before and after this point
            p = polyRings[polyIdx].query(exPtIdx)
            pPrev = p.prev
            pNext = p.next

            pPrevMidLoc = [(pPrev.value[0] + (p.value[0] - pPrev.value[0]) / 2), (pPrev.value[1] + (p.value[1] - pPrev.value[1]) / 2)]
            pPrevMid = RingNode(polyRings[polyIdx].count, pPrevMidLoc)
            pNextMidLoc = [(p.value[0] + (pNext.value[0] - p.value[0]) / 2), (p.value[1] + (pNext.value[1] - p.value[1]) / 2)]
            pNextMid = RingNode(polyRings[polyIdx].count + 1, pNextMidLoc)

            polyRings[polyIdx].insert(p, pNextMid)
            polyRings[polyIdx].insert(pPrev, pPrevMid)

        # Simplify the graph
        G = nx.Graph()

        # New start
        startPolyPt = polyRings[sp[1][0]].query(sp[1][1])
        startNearPt = [startPolyPt.prev.prev, startPolyPt.prev, startPolyPt, startPolyPt.next, startPolyPt.next.next]
        for p in startNearPt:
            d = distEuclideanXY(startPt, p.value)
            G.add_edge('s', (0, p.key), weight = d)

        # In between
        for i in range(1, len(sp) - 2):
            polyIdx = sp[i][0]
            polyNextIdx = sp[i + 1][0]
            exPtIdx = sp[i][1]
            exPtNextIdx = sp[i + 1][1]

            ptI = polyRings[polyIdx].query(exPtIdx)
            ptNearI = [ptI.prev.prev, ptI.prev, ptI, ptI.next, ptI.next.next]
            ptJ = polyRings[polyNextIdx].query(exPtNextIdx)
            ptNearJ = [ptJ.prev.prev, ptJ.prev, ptJ, ptJ.next, ptJ.next.next]
            for kI in ptNearI:
                for kJ in ptNearJ:
                    d = None
                    if (((polyIdx, kI.key), (polyNextIdx, kJ.key)) in tau):
                        d = tau[((polyIdx, kI.key), (polyNextIdx, kJ.key))]
                    else:
                        d = distEuclideanXY(kI.value, kJ.value)
                        tau[((polyIdx, kI.key), (polyNextIdx, kJ.key))] = d
                    G.add_edge((polyIdx, kI.key), (polyNextIdx, kJ.key), weight = d)

        # New end
        endPolyPt = polyRings[sp[-2][0]].query(sp[-2][1])
        endNearPt = [endPolyPt.prev.prev, endPolyPt.prev, endPolyPt, endPolyPt.next, endPolyPt.next.next]
        for p in endNearPt:
            d = distEuclideanXY(p.value, endPt)
            G.add_edge((len(polys) - 1, p.key), 'e', weight = d)

        sp = nx.dijkstra_path(G, 's', 'e')

        newDist = distEuclideanXY(startPt, polyRings[sp[1][0]].query(sp[1][1]).value)
        for i in range(1, len(sp) - 2):
            newDist += tau[(sp[i][0], sp[i][1]), (sp[i + 1][0], sp[i + 1][1])]
        newDist += distEuclideanXY(polyRings[sp[-2][0]].query(sp[-2][1]).value, endPt)

        if (abs(newDist - dist) <= adaptErr):
            refineFlag = False

        dist = newDist

    path = [startPt]
    for p in sp:
        if (p != 's' and p != 'e'):
            path.append(polyRings[p[0]].query(p[1]).value)
    path.append(endPt)

    return {
        'path': path,
        'dist': dist
    }

def _poly2PolyPathGurobi(startPt: pt, endPt: pt, polys: polys, outputFlag = False, gapTol = None, timeLimit = None):
    segs = []
    for i in range(len(polys)):
        segs.append([])
        for k in range(-1, len(polys[i]) - 1):
            segs[i].append([polys[i][k], polys[i][k + 1]])
            
    return _seg2SegPathGurobi(
        startPt = startPt, 
        endPt = endPt, 
        segs = segs, 
        outputFlag = outputFlag, 
        gapTol = gapTol, 
        timeLimit = timeLimit)

def _multiPoly2MultiPolyPathGurobi(startPt: pt, endPt: pt, multiPolys: list[polys], holes: list[polys]|None = None, outputFlag = False, gapTol = None, timeLimit = None):
    segs = []
    if (holes != None):
        if (len(multiPolys) != len(holes)):
            raise UnsupportedInputError("ERROR: `multiPolys` should have the same length as `holes`.")

    for i in range(len(multiPolys)):
        segs.append([])
        # Multipolys
        for j in range(len(multiPolys[i])):
            for k in range(-1, len(multiPolys[i][j]) - 1):
                segs[i].append([multiPolys[i][j][k], multiPolys[i][j][k + 1]])
        # Holes
        # holes => list[polys]
        if (holes != None and holes[i] != None and len(holes[i]) > 0):
            # hole => polys
            for hole in holes[i]:
                # print("hole", hole)
                # h => poly
                for h in hole:
                    for k in range(-1, len(h) - 1):
                        segs[i].append([h[k], h[k + 1]])
    # print("seg", segs)
    return _seg2SegPathGurobi(
        startPt = startPt, 
        endPt = endPt, 
        segs = segs, 
        outputFlag = outputFlag, 
        gapTol = gapTol, 
        timeLimit = timeLimit)

def _seg2SegPathGurobi(startPt: pt, endPt: pt, segs: list[line], outputFlag = False, gapTol = None, timeLimit = None):
    try:
        import gurobipy as grb
    except(ImportError):
        raise ImportError("ERROR: Cannot find Gurobi")
        return

    model = grb.Model("SOCP")
    model.setParam('OutputFlag', 0 if outputFlag == False else 1)

    if (gapTol != None):
        model.setParam('MIPGap', gapTol)
    if (timeLimit != None):
        model.setParam(grb.GRB.Param.TimeLimit, timeLimit)

    # Parameters ==============================================================
    allX = [startPt[0], endPt[0]]
    allY = [startPt[1], endPt[1]]
    for i in range(len(segs)):
        for j in range(len(segs[i])):
            allX.append(segs[i][j][0][0])
            allY.append(segs[i][j][0][1])
            allX.append(segs[i][j][1][0])
            allY.append(segs[i][j][1][1])
    lbX = min(allX) - 1
    lbY = min(allY) - 1
    ubX = max(allX) + 1
    ubY = max(allY) + 1

    # Decision variables ======================================================
    # (xi, yi) 为第i个seg上的坐标
    # index = 1, 2, ..., len(segs)
    x = {}
    y = {}
    for i in range(len(segs)):
        x[i] = model.addVar(vtype=grb.GRB.CONTINUOUS, name = "x_%s" % i, lb=lbX, ub=ubX)
        y[i] = model.addVar(vtype=grb.GRB.CONTINUOUS, name = "y_%s" % i, lb=lbY, ub=ubY)

    # e[i, j] 为binary，表示(xi, yi)处于第i个seg上的第j段
    # index i = 1, 2, ..., len(segs)
    # index j = 0, ..., len(segs[i]) - 1
    # lam[i, j] 为[0, 1]之间的值，表示第i段是处于对应e[i, j]上的位置，若e[i, j] = 0，则lam[i, j] = 0
    e = {}
    lam = {}    
    for i in range(len(segs)):
        for j in range(len(segs[i])):
            e[i, j] = model.addVar(vtype=grb.GRB.BINARY, name="e_%s_%s" % (i, j))
            lam[i, j] = model.addVar(vtype=grb.GRB.CONTINUOUS, name="lam_%s_%s" % (i, j))

    # d[i] 为第i个到第i+1个坐标的距离, dx[i], dy[i] 为对应辅助变量
    # Distance from ((xi, yi)) to (x[i + 1], y[i + 1]), 
    # where startPt = (x[0], y[0]) and endPt = (x[len(circles) + 1], y[len(circles) + 1])
    d = {}
    for i in range(len(segs) + 1):
        d[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'd_%s' % i)
    model.setObjective(grb.quicksum(d[i] for i in range(len(segs) + 1)), grb.GRB.MINIMIZE)

    # Aux vars - distance between (x, y)
    dx = {}
    dy = {}
    for i in range(len(segs) + 1):
        dx[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'dx_%s' % i, lb = -float('inf'), ub = float('inf'))
        dy[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'dy_%s' % i, lb = -float('inf'), ub = float('inf'))

    # Constraints =============================================================
    # (xi, yi)必须在其中一段上
    for i in range(len(segs)):
        model.addConstr(grb.quicksum(e[i, j] for j in range(len(segs[i]))) == 1)

    # 具体(xi, yi)的位置，lam[i, j]在e[i, j] = 0的段上不激活
    for i in range(len(segs)):
        model.addConstr(x[i] == grb.quicksum(
            e[i, j] * segs[i][j][0][0] + lam[i, j] * (segs[i][j][1][0] - segs[i][j][0][0])
            for j in range(len(segs[i]))))
        model.addConstr(y[i] == grb.quicksum(
            e[i, j] * segs[i][j][0][1] + lam[i, j] * (segs[i][j][1][1] - segs[i][j][0][1])
            for j in range(len(segs[i]))))
    for i in range(len(segs)):
        for j in range(len(segs[i])):
            model.addConstr(lam[i, j] <= e[i, j])

    # Aux constr - dx dy
    model.addConstr(dx[0] == x[0] - startPt[0])
    model.addConstr(dy[0] == y[0] - startPt[1])
    for i in range(len(segs) - 1):
        model.addConstr(dx[i + 1] == x[i + 1] - x[i])
        model.addConstr(dy[i + 1] == y[i + 1] - y[i])
    model.addConstr(dx[len(segs)] == endPt[0] - x[len(segs) - 1])
    model.addConstr(dy[len(segs)] == endPt[1] - y[len(segs) - 1])

    # Distance btw visits
    for i in range(len(segs) + 1):
        model.addQConstr(d[i] ** 2 >= dx[i] ** 2 + dy[i] ** 2)

    # model.write("SOCP.lp")
    model.optimize()

    # Post-processing =========================================================
    ofv = None
    path = [startPt]
    if (model.status == grb.GRB.status.OPTIMAL):
        solType = 'IP_Optimal'
        ofv = model.getObjective().getValue()
        for i in x:
            path.append((x[i].x, y[i].x))
        path.append(endPt)
        gap = 0
        lb = ofv
        ub = ofv
        runtime = model.Runtime
    elif (model.status == grb.GRB.status.TIME_LIMIT):
        solType = 'IP_TimeLimit'
        ofv = model.ObjVal
        for i in x:
            path.append((x[i].x, y[i].x))
        path.append(endPt)
        gap = model.MIPGap
        lb = model.ObjBoundC
        ub = model.ObjVal
        runtime = model.Runtime
    return {
        'path': path,
        'dist': ofv,
        'runtime': runtime
    }

def circle2CirclePath(startPt: pt, endPt: pt, circles: list[dict], algo: str = 'SOCP', **kwargs):
    
    """Given a starting point, a list of circles, and an ending point, returns a shortest route that starts from startPt, visits every polys in given order, and returns to the ending point.

    Parameters
    ----------
    startPt: pt, required, default None
        The coordinate which starts the path.
    endPt: pt, required, default None
        The coordinate which ends the path.
    circles: dict, required
        A list of circles modeled by dictionaries to be visited in given sequence. Each circle is dictionary with two fields: 'radius' and 'center'.
    algo: str, optional, default as 'SOCP'
        Select the algorithm for calculating the shortest path. Options and required additional inputs are as follows:
            
        1) (default) 'SOCP', use Second-order Cone Programing method.
            - solver: str, optional, now supports 'Gurobi' and 'COPT'
            - timeLimit: int|float, additional stopping criteria
            - gapTolerance: int|float, additional stopping criteria
            - outputFlag: bool, True if turn on the log output from solver. Default to be False
    **kwargs: optional
        Provide additional inputs for different `edges` options and `algo` options

    Returns
    -------
    dict
        Two fields in the dictionary, 'dist' indicates the distance of the path, 'path' indicates the travel path.
    """

    # Sanity check ============================================================
    if (algo == None):
        raise MissingParameterError("ERROR: Missing required field `algo`.")

    if (algo == 'AdaptIter'):
        adaptErr = ERRTOL['deltaDist']
        if ('adaptErr' in kwargs):
            adaptErr = kwargs['adaptErr']
        initLod = 12
        if ('initLod' in kwargs):
            initLod = kwargs['initLod']
        res = _circle2CirclePathAdaptIter(startPt, endPt, circles, adaptErr, initLod)
    elif (algo == 'SOCP'):
        if ('solver' not in kwargs or kwargs['solver'] == 'Gurobi'):
            outputFlag = False
            if ('outputFlag' in kwargs):
                outputFlag = kwargs['outputFlag']
            # print(circles)
            res = _circle2CirclePathGurobi(startPt, endPt, circles, outputFlag)
        elif (kwargs['solver'] == 'COPT'):
            outputFlag = False
            if ('outputFlag' in kwargs):
                outputFlag = kwargs['outputFlag']
            res = _circle2CirclePathCOPT(startPt, endPt, circles, outputFlag)
    else:
        raise UnsupportedInputError("ERROR: Not support by vrpSolver for now.")

    return {
        'path': res['path'],
        'dist': res['dist']
    }

def _circle2CirclePathAdaptIter(startPt: pt, endPt: pt, circles: list[dict], adaptErr, initLod: int = 4):

    def getLocByDeg(circle, deg):
        return (
            circle['center'][0] + circle['radius'] * math.cos(math.radians(deg)),
            circle['center'][1] + circle['radius'] * math.sin(math.radians(deg))
        )

    G = nx.Graph()
    circleRings = []

    # circleRing is keyed by index, valued by [degree, loc]
    for c in circles:
        circleRing = Ring()
        for i in range(initLod):
            deg = i * 360 / initLod
            circleRing.append(RingNode(
                key = i, 
                deg = deg, 
                loc = getLocByDeg(c, deg)))
        circleRings.append(circleRing)

    # startPt to the first polygon
    cur = circleRings[0].head
    while (True):
        d = distEuclideanXY(startPt, cur.loc)
        G.add_edge('s', (0, cur.key), weight = d)
        cur = cur.next
        if (cur.key == circleRings[0].head.key):
            break

    # If more than one polygon btw startPt and endPt
    for i in range(len(circles) - 1):
        curI = circleRings[i].head
        while (True):
            curJ = circleRings[i + 1].head
            while (True):
                d = distEuclideanXY(curI.loc, curJ.loc)
                G.add_edge((i, curI.key), (i + 1, curJ.key), weight = d)
                curJ = curJ.next
                if (curJ.key == circleRings[i + 1].head.key):
                    break
            curI = curI.next
            if (curI.key == circleRings[i].head.key):
                break

    # last polygon to endPt
    cur = circleRings[-1].head
    while (True):
        d = distEuclideanXY(cur.loc, endPt)
        G.add_edge((len(circles) - 1, cur.key), 'e', weight = d)
        cur = cur.next
        if (cur.key == circleRings[len(circles) - 1].head.key):
            break

    sp = nx.dijkstra_path(G, 's', 'e')

    # sp[i] => (circleIdx, curKey)

    dist = distEuclideanXY(startPt, circleRings[sp[1][0]].query(sp[1][1]).loc)
    for i in range(1, len(sp) - 2):
        dist += distEuclideanXY(
            circleRings[sp[i][0]].query(sp[i][1]).loc,
            circleRings[sp[i + 1][0]].query(sp[i + 1][1]).loc)
    dist += distEuclideanXY(circleRings[sp[-2][0]].query(sp[-2][1]).loc, endPt)
    
    iterNum = 0

    # Find detailed location
    refineFlag = True
    iterNum = 0
    # while (iterNum <= 10):
    while(refineFlag):
        # sp[0] is startLoc
        # sp[-1] is endLoc
        for i in range(1, len(sp) - 1):
            # Find current shortest intersecting point
            circIdx = sp[i][0]
            inteKey = sp[i][1]

            # Insert two new points before and after this point
            p = circleRings[circIdx].query(inteKey)
            pPrev = p.prev
            pNext = p.next

            # Get deg before and after current deg
            pPrevMidDeg = None
            pNextMidDeg = None

            # If p.prev.deg > p.deg => p.prev -= 360
            # If p.next.deg < p.deg => p.next += 360

            pPrevDeg = p.prev.deg if (p.prev.deg < p.deg) else p.prev.deg - 360
            pNextDeg = p.next.deg if (p.next.deg > p.deg) else p.next.deg + 360
            pPrevMidDeg = p.prev.deg + (p.deg - p.prev.deg) / 2
            pNextMidDeg = p.deg + (p.next.deg - p.deg) / 2
            if (pPrevMidDeg < 0):
                pPrevMidDeg += 360
            if (pNextMidDeg > 360):
                pNextMidDeg -= 360

            pPrevMidLoc = getLocByDeg(circles[circIdx], pPrevMidDeg)
            pNextMidLoc = getLocByDeg(circles[circIdx], pNextMidDeg)

            pPrevMid = RingNode(circleRings[circIdx].count, deg = pPrevMidDeg, loc = pPrevMidLoc)
            pNextMid = RingNode(circleRings[circIdx].count + 1, deg = pNextMidDeg, loc = pNextMidLoc)

            circleRings[circIdx].insert(p, pNextMid)
            circleRings[circIdx].insert(pPrev, pPrevMid)

        # New start
        for p in circleRings[sp[1][0]].traverse():
            if (('s', (0, p.key)) not in G.edges):
                d = distEuclideanXY(startPt, p.loc)
                G.add_edge('s', (0, p.key), weight = d)
        # In between
        for i in range(1, len(sp) - 2):
            circIdx = sp[i][0]
            circNextIdx = sp[i + 1][0]
            for kI in circleRings[circIdx].traverse():
                for kJ in circleRings[circNextIdx].traverse():
                    if (((circIdx, kI.key), (circNextIdx, kJ.key)) not in G.edges):
                        d = distEuclideanXY(kI.loc, kJ.loc)
                        G.add_edge((circIdx, kI.key), (circNextIdx, kJ.key), weight = d)
        for p in circleRings[sp[-2][0]].traverse():
            if (((len(circles) - 1, p.key), 'e') not in G.edges):
                d = distEuclideanXY(p.loc, endPt)
                G.add_edge((len(circles) - 1, p.key), 'e', weight = d)

        sp = nx.dijkstra_path(G, 's', 'e')

        newDist = distEuclideanXY(startPt, circleRings[sp[1][0]].query(sp[1][1]).loc)
        for i in range(1, len(sp) - 2):
            newDist += distEuclideanXY(
                circleRings[sp[i][0]].query(sp[i][1]).loc,
                circleRings[sp[i + 1][0]].query(sp[i + 1][1]).loc)
        newDist += distEuclideanXY(circleRings[sp[-2][0]].query(sp[-2][1]).loc, endPt)

        if (abs(newDist - dist) <= adaptErr):
            refineFlag = False

        dist = newDist

        # 测试
        # fig, ax = None, None
        # for i in circles:
        #     fig, ax = plotCircle(
        #         fig = fig,
        #         ax = ax,
        #         center = i['center'],
        #         radius = i['radius'],
        #         edgeColor = 'black',
        #         fillColor = 'gray',
        #         boundingBox = (-10, 110, -10, 110))
        # locs = [startPt, endPt]
        # for i in circleRings:
        #     for c in i.traverse():
        #         locs.append(c.loc)
        # fig, ax = plotLocs(
        #     fig = fig,
        #     ax = ax,
        #     locs = locs,
        #     locColor = 'red',
        #     locMarkerSize = 3)
        # locSeq = [startPt]
        # for i in range(1, len(sp) - 1):
        #     locSeq.append(circleRings[sp[i][0]].query(sp[i][1]).loc)
        # locSeq.append(endPt)
        # fig, ax = plotLocSeq(
        #     fig = fig,
        #     ax = ax,
        #     locSeq = locSeq,
        #     lineColor = 'blue')
        # fig.savefig(f"Iter_{iterNum}.png")
        iterNum += 1

    path = [startPt]
    for p in sp:
        if (p != 's' and p != 'e'):
            path.append(circleRings[p[0]].query(p[1]).loc)
    path.append(endPt)
    # print("Num of iter: ", iterNum)

    return {
        'path': path,
        'dist': dist
    }

def _circle2CirclePathGurobi(startPt: pt, endPt: pt, circles: list[dict], outputFlag: bool = False):
    try:
        import gurobipy as grb
    except(ImportError):
        print("ERROR: Cannot find Gurobi")
        return

    model = grb.Model("SOCP")
    model.setParam('OutputFlag', 1 if outputFlag else 0)

    # Parameters ==============================================================
    # anchor starts from startPt, in between are a list of circles, ends with endPt
    anchor = [startPt]
    for i in range(len(circles)):
        anchor.append(circles[i]['center'])
    anchor.append(endPt)

    allX = [startPt[0], endPt[0]]
    allY = [startPt[1], endPt[1]]
    for i in range(len(circles)):
        allX.append(circles[i]['center'][0] - circles[i]['radius'])
        allX.append(circles[i]['center'][0] + circles[i]['radius'])
        allY.append(circles[i]['center'][1] - circles[i]['radius'])
        allY.append(circles[i]['center'][1] + circles[i]['radius'])
    lbX = min(allX) - 1
    lbY = min(allY) - 1
    ubX = max(allX) + 1
    ubY = max(allY) + 1

    # Decision variables ======================================================
    # NOTE: x, y index starts by 1
    x = {}
    y = {}
    for i in range(1, len(circles) + 1):
        x[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = "x_%s" % i, lb = lbX, ub = ubX)
        y[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = "y_%s" % i, lb = lbY, ub = ubY)
    # Distance from ((xi, yi)) to (x[i + 1], y[i + 1]), 
    # where startPt = (x[0], y[0]) and endPt = (x[len(circles) + 1], y[len(circles) + 1])
    d = {}
    for i in range(len(circles) + 1):
        d[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'd_%s' % i)
    model.setObjective(grb.quicksum(d[i] for i in range(len(circles) + 1)), grb.GRB.MINIMIZE)

    # Aux vars - distance between (x, y)
    dx = {}
    dy = {}
    for i in range(len(circles) + 1):
        dx[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'dx_%s' % i, lb = -float('inf'), ub = float('inf'))
        dy[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'dy_%s' % i, lb = -float('inf'), ub = float('inf'))
    # Aux vars - distance from (x, y) to the center
    rx = {}
    ry = {}
    for i in range(1, len(circles) + 1):
        rx[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'rx_%s' % i, lb = -float('inf'), ub = float('inf'))
        ry[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'ry_%s' % i, lb = -float('inf'), ub = float('inf'))

    # Constraints =============================================================
    # Aux constr - dx dy
    model.addConstr(dx[0] == x[1] - anchor[0][0])
    model.addConstr(dy[0] == y[1] - anchor[0][1])
    for i in range(1, len(circles)):
        model.addConstr(dx[i] == x[i + 1] - x[i])
        model.addConstr(dy[i] == y[i + 1] - y[i])
    model.addConstr(dx[len(circles)] == anchor[-1][0] - x[len(circles)])
    model.addConstr(dy[len(circles)] == anchor[-1][1] - y[len(circles)])

    # Aux constr - rx ry
    for i in range(1, len(circles) + 1):
        model.addConstr(rx[i] == x[i] - anchor[i][0])
        model.addConstr(ry[i] == y[i] - anchor[i][1])

    # Distance btw visits
    for i in range(len(circles) + 1):
        model.addQConstr(d[i] ** 2 >= dx[i] ** 2 + dy[i] ** 2)
        # model.addQConstr(dx[i] ** 2 + dy[i] ** 2 >= 0.1)

    for i in range(1, len(circles) + 1):
        model.addQConstr(rx[i] ** 2 + ry[i] ** 2 <= circles[i - 1]['radius'] ** 2)

    model.modelSense = grb.GRB.MINIMIZE
    # model.write("SOCP.lp")
    model.optimize()

    # Post-processing =========================================================
    ofv = None
    path = [startPt]
    if (model.status == grb.GRB.status.OPTIMAL):
        solType = 'IP_Optimal'
        ofv = model.getObjective().getValue()
        for i in x:
            path.append((x[i].x, y[i].x))
        path.append(endPt)
        gap = 0
        lb = ofv
        ub = ofv
    elif (model.status == grb.GRB.status.TIME_LIMIT):
        solType = 'IP_TimeLimit'
        ofv = model.ObjVal
        for i in x:
            path.append((x[i].x, y[i].x))
        path.append(endPt)
        gap = model.MIPGap
        lb = model.ObjBoundC
        ub = model.ObjVal
    else:
        print(model.status)
        
    return {
        'path': path,
        'dist': ofv,
        'runtime': model.Runtime
    }
 
def _circle2CirclePathCOPT(startPt: pt, endPt: pt, circles: dict, outputFlag: bool = False):
    env = None
    try:
        import coptpy as cp
        envconfig = cp.EnvrConfig()
        envconfig.set('nobanner', '1')
        AVAIL_SOLVER = 'COPT'
        if (env == None):
            env = cp.Envr(envconfig)
    except(ImportError):
        print("ERROR: Cannot find COPT")
        return

    model = env.createModel("SOCP")
    model.setParam(cp.COPT.Param.Logging, 1 if outputFlag else 0)
    model.setParam(cp.COPT.Param.LogToConsole, 1 if outputFlag else 0)

    # Decision variables ======================================================
    # anchor starts from startPt, in between are a list of circles, ends with endPt
    anchor = [startPt]
    for i in range(len(circles)):
        anchor.append(circles[i]['center'])
    anchor.append(endPt)

    allX = [startPt[0], endPt[0]]
    allY = [startPt[1], endPt[1]]
    for i in range(len(circles)):
        allX.append(circles[i]['center'][0] - circles[i]['radius'])
        allX.append(circles[i]['center'][0] + circles[i]['radius'])
        allY.append(circles[i]['center'][1] - circles[i]['radius'])
        allY.append(circles[i]['center'][1] + circles[i]['radius'])
    lbX = min(allX) - 1
    lbY = min(allY) - 1
    ubX = max(allX) + 1
    ubY = max(allY) + 1

    # Decision variables ======================================================
    # NOTE: x, y index starts by 1
    x = {}
    y = {}
    for i in range(1, len(circles) + 1):
        x[i] = model.addVar(vtype = cp.COPT.CONTINUOUS, name = "x_%s" % i, lb = lbX, ub = ubX)
        y[i] = model.addVar(vtype = cp.COPT.CONTINUOUS, name = "y_%s" % i, lb = lbY, ub = ubY)
    # Distance from ((xi, yi)) to (x[i + 1], y[i + 1]), 
    # where startPt = (x[0], y[0]) and endPt = (x[len(circles) + 1], y[len(circles) + 1])
    d = {}
    for i in range(len(circles) + 1):
        d[i] = model.addVar(vtype = cp.COPT.CONTINUOUS, name = 'd_%s' % i)
    # Aux vars - distance between (x, y)
    dx = {}
    dy = {}
    for i in range(len(circles) + 1):
        dx[i] = model.addVar(vtype = cp.COPT.CONTINUOUS, name = 'dx_%s' % i, lb = -float('inf'), ub = float('inf'))
        dy[i] = model.addVar(vtype = cp.COPT.CONTINUOUS, name = 'dy_%s' % i, lb = -float('inf'), ub = float('inf'))
    # Aux vars - distance from (x, y) to the center
    rx = {}
    ry = {}
    for i in range(1, len(circles) + 1):
        rx[i] = model.addVar(vtype = cp.COPT.CONTINUOUS, name = 'rx_%s' % i, lb = -float('inf'), ub = float('inf'))
        ry[i] = model.addVar(vtype = cp.COPT.CONTINUOUS, name = 'ry_%s' % i, lb = -float('inf'), ub = float('inf'))

    model.setObjective(cp.quicksum(d[i] for i in range(len(circles) + 1)), cp.COPT.MINIMIZE)

    # Distance constraints ====================================================
    # Aux constr - dx dy
    model.addConstr(dx[0] == x[1] - anchor[0][0])
    model.addConstr(dy[0] == y[1] - anchor[0][1])
    for i in range(1, len(circles)):
        model.addConstr(dx[i] == x[i] - x[i + 1])
        model.addConstr(dy[i] == y[i] - y[i + 1])
    model.addConstr(dx[len(circles)] == anchor[-1][0] - x[len(circles)])
    model.addConstr(dy[len(circles)] == anchor[-1][1] - y[len(circles)])
    # Aux constr - rx ry
    for i in range(1, len(circles) + 1):
        model.addConstr(rx[i] == x[i] - anchor[i][0])
        model.addConstr(ry[i] == y[i] - anchor[i][1])

    # Distance btw visits
    for i in range(len(circles) + 1):
        model.addQConstr(d[i] ** 2 >= dx[i] ** 2 + dy[i] ** 2)

    for i in range(1, len(circles) + 1):
        model.addQConstr(rx[i] ** 2 + ry[i] ** 2 <= circles[i - 1]['radius'] ** 2)

    # model.write("SOCP.lp")
    model.solve()

    # Post-processing =========================================================
    ofv = None
    path = [startPt]
    if (model.status == cp.COPT.OPTIMAL):
        solType = 'IP_Optimal'
        ofv = model.getObjective().getValue()
        for i in x:
            path.append((x[i].x, y[i].x))
        path.append(endPt)
        gap = 0
        lb = ofv
        ub = ofv
        runtime = model.SolvingTime
    elif (model.status == cp.COPT.TIMEOUT):
        solType = 'IP_TimeLimit'
        ofv = model.ObjVal
        for i in x:
            path.append((x[i].x, y[i].x))
        path.append(endPt)
        gap = model.BestGap
        lb = model.BestBnd
        ub = model.BestObj
        runtime = model.SolvingTime
    realDist = 0

    return {
        'path': path,
        'dist': ofv
    }

# @runtime('curveArc2CurveArcPath')
def curveArc2CurveArcPath(startPt: pt, endPt: pt, curveArcs: list[CurveArc], adaptErr = 0.01, atLeastTimeBtw = None, speed = 1):
    tau = {}

    G = nx.Graph()

    if (atLeastTimeBtw == None):
        atLeastTimeBtw = [0 for i in range(len(curveArcs) + 1)]

    # Initial iteration =======================================================
    # startPt to the first curveArc
    cur = curveArcs[0].head
    while (not cur.isNil):
        d = None
        if (('s', (0, cur.key)) not in tau):
            d = distEuclideanXY(startPt, cur.loc)
            tau['s', (0, cur.key)] = d
        else:
            d = tau['s', (0, cur.key)]
        G.add_edge('s', (0, cur.key), weight = max(d / speed, atLeastTimeBtw[0]))

        cur = cur.next
        if (cur == curveArcs[0].head):
            break

    # Between startPt and endPt
    for i in range(len(curveArcs) - 1):
        curI = curveArcs[i].head
        while (not curI.isNil):
            curJ = curveArcs[i + 1].head
            while (not curJ.isNil):
                d = None
                if (((i, curI.key), (i + 1, curJ.key)) not in tau):
                    d = distEuclideanXY(curI.loc, curJ.loc)
                    tau[(i, curI.key), (i + 1, curJ.key)] = d
                else:
                    d = tau[(i, curI.key), (i + 1, curJ.key)]

                if (d > 0.005):
                    G.add_edge((i, curI.key), (i + 1, curJ.key), weight = max(d / speed, atLeastTimeBtw[i + 1]))

                curJ = curJ.next
                if (curJ == curveArcs[i + 1].head):
                    break
            curI = curI.next
            if (curI == curveArcs[i].head):
                break

    # last curveArc to endPt
    cur = curveArcs[-1].head
    while (not cur.isNil):
        d = None
        if (((len(curveArcs) - 1, cur.key), 'e') not in tau):
            d = distEuclideanXY(cur.loc, endPt)
            tau[(len(curveArcs) - 1, cur.key), 'e'] = d
        else:
            d = tau[(len(curveArcs) - 1, cur.key), 'e']
        G.add_edge((len(curveArcs) - 1, cur.key), 'e', weight = max(d / speed, atLeastTimeBtw[-1]))

        cur = cur.next
        if (cur == curveArcs[-1].head):
            break

    sp = nx.dijkstra_path(G, 's', 'e')
    # print(sp)

    dist = 0
    for i in range(1, len(sp)):
        dist += G[sp[i - 1]][sp[i]]['weight']

    # Refine ==================================================================
    iterNum = 0
    refineFlag = True
    while (refineFlag):
        iterNum += 1

        # 重新起图
        G = nx.Graph()

        byStage = []

        # sp[0] is startLoc
        # sp[-1] is endLoc
        for i in range(1, len(sp) - 1):
            cvIdx = sp[i][0]
            cvKey = sp[i][1]

            # Insert two pts before and after this cvNode
            n = curveArcs[cvIdx].query(cvKey)
            curveArcs[cvIdx].insertAround(n)

            thisStage = []

            # prev.prev
            if (not n.prev.isNil and not n.prev.prev.isNil):
                thisStage.append(n.prev.prev)
            if (not n.prev.isNil):
                thisStage.append(n.prev)
            thisStage.append(n)
            if (not n.next.isNil):
                thisStage.append(n.next)
            if (not n.next.isNil and not n.next.next.isNil):
                thisStage.append(n.next.next)

            byStage.append(thisStage)

        # StartPt => byStage
        for k in byStage[0]:
            d = None
            if (('s', (0, k.key)) not in tau):
                d = distEuclideanXY(startPt, k.loc)
                tau['s', (0, k.key)] = d
            else:
                d = tau['s', (0, k.key)]
            G.add_edge('s', (0, k.key), weight = max(d / speed, atLeastTimeBtw[0]))

        # Between byStages
        if (len(byStage) > 2):
            for i in range(1, len(byStage)):
                for k1 in byStage[i - 1]:
                    for k2 in byStage[i]:
                        d = None
                        if (((i - 1, k1.key), (i, k2.key)) not in tau):
                            d = distEuclideanXY(k1.loc, k2.loc)
                            tau[(i - 1, k1.key), (i, k2.key)] = d
                        else:
                            d = tau[(i - 1, k1.key), (i, k2.key)]
                        G.add_edge((i - 1, k1.key), (i, k2.key), weight = max(d / speed, atLeastTimeBtw[i]))

        # byStage => EndPt
        for k in byStage[-1]:
            d = None
            if ((((len(curveArcs) - 1, k.key), 'e')) not in tau):
                d = distEuclideanXY(k.loc, endPt)
                tau[(len(curveArcs) - 1, k.key), 'e'] = d
            else:
                d = tau[(len(curveArcs) - 1, k.key), 'e']
            G.add_edge((len(curveArcs) - 1, k.key), 'e', weight = max(d / speed, atLeastTimeBtw[-1]))

        newSp = nx.dijkstra_path(G, 's', 'e')

        # print(newSp)

        newDist = 0
        for i in range(1, len(newSp)):
            newDist += G[newSp[i - 1]][newSp[i]]['weight']

        if (abs(newDist - dist) <= adaptErr):
            refineFlag = False

        dist = newDist
        sp = newSp

    # Collect results =========================================================
    path = [startPt]
    for p in sp:
        if (p != 's' and p != 'e'):
            path.append(curveArcs[p[0]].query(p[1]).loc)
    path.append(endPt)

    # print("New dist: ", dist)
    # print("Adapt Iter Time: ", (datetime.datetime.now() - startTime).total_seconds())
    # print("Adapt Iter Num: ", iterNum)

    return {
        'path': path,
        'dist': dist
    }

def curveArc2CurveArcPathBak(startPt: pt, endPt: pt, curveArcs: list[CurveArc], adaptErr = 0.002, atLeastTimeBtw = None, speed = 1):
    tau = {}

    G = nx.Graph()

    if (atLeastTimeBtw == None):
        atLeastTimeBtw = [0 for i in range(len(curveArcs) + 1)]

    # Initial iteration =======================================================
    # startPt to the first curveArc
    cur = curveArcs[0].head
    while (not cur.isNil):
        d = distEuclideanXY(startPt, cur.loc)
        tau['s', (0, cur.key)] = d
        G.add_edge('s', (0, cur.key), weight = max(d / speed, atLeastTimeBtw[0]))

        cur = cur.next
        if (cur == curveArcs[0].head):
            break

    # Between startPt and endPt
    for i in range(len(curveArcs) - 1):
        curI = curveArcs[i].head
        while (not curI.isNil):
            curJ = curveArcs[i + 1].head
            while (not curJ.isNil):
                d = distEuclideanXY(curI.loc, curJ.loc)
                if (d > 0.005):
                    tau[(i, curI.key), (i + 1, curJ.key)] = d
                    G.add_edge((i, curI.key), (i + 1, curJ.key), weight = max(d / speed, atLeastTimeBtw[i + 1]))

                curJ = curJ.next
                if (curJ == curveArcs[i + 1].head):
                    break
            curI = curI.next
            if (curI == curveArcs[i].head):
                break

    # last curveArc to endPt
    cur = curveArcs[-1].head
    while (not cur.isNil):
        d = distEuclideanXY(cur.loc, endPt)
        tau[(len(curveArcs) - 1, cur.key), 'e'] = d
        G.add_edge((len(curveArcs) - 1, cur.key), 'e', weight = max(d / speed, atLeastTimeBtw[-1]))

        cur = cur.next
        if (cur == curveArcs[-1].head):
            break

    sp = nx.dijkstra_path(G, 's', 'e')
    # print(sp)

    dist = 0
    for i in range(1, len(sp)):
        dist += G[sp[i - 1]][sp[i]]['weight']

    # Refine ==================================================================
    iterNum = 0
    refineFlag = True
    while (refineFlag):
        iterNum += 1
        # sp[0] is startLoc
        # sp[-1] is endLoc
        for i in range(1, len(sp) - 1):
            cvIdx = sp[i][0]
            cvKey = sp[i][1]

            # Insert two pts before and after this cvNode
            n = curveArcs[cvIdx].query(cvKey)
            curveArcs[cvIdx].insertAround(n)

        # Update graph
        # startPt to the first curveArc
        cur = curveArcs[0].head
        while (not cur.isNil):
            if (('s', (0, cur.key)) not in G.edges):
                d = distEuclideanXY(startPt, cur.loc)
                tau['s', (0, cur.key)] = d
                G.add_edge('s', (0, cur.key), weight = max(d / speed, atLeastTimeBtw[0]))

            cur = cur.next
            if (cur == curveArcs[0].head):
                break

        # Between startPt and endPt
        for i in range(len(curveArcs) - 1):
            curI = curveArcs[i].head
            while (not curI.isNil):
                curJ = curveArcs[i + 1].head
                while (not curJ.isNil):
                    if (((i, curI.key), (i + 1, curJ.key)) not in G.edges):
                        d = distEuclideanXY(curI.loc, curJ.loc)
                        tau[(i, curI.key), (i + 1, curJ.key)] = d
                        G.add_edge((i, curI.key), (i + 1, curJ.key), weight = max(d / speed, atLeastTimeBtw[i + 1]))

                    curJ = curJ.next
                    if (curJ == curveArcs[i + 1].head):
                        break
                curI = curI.next
                if (curI == curveArcs[i].head):
                    break

        # last curveArc to endPt
        cur = curveArcs[-1].head
        while (not cur.isNil):
            if (((len(curveArcs) - 1, cur.key), 'e') not in G.edges):
                d = distEuclideanXY(cur.loc, endPt)
                tau[(len(curveArcs) - 1, cur.key), 'e'] = d
                G.add_edge((len(curveArcs) - 1, cur.key), 'e', weight = max(d / speed, atLeastTimeBtw[-1]))

            cur = cur.next
            if (cur == curveArcs[-1].head):
                break
        newSp = nx.dijkstra_path(G, 's', 'e')

        # print(newSp)

        newDist = 0
        for i in range(1, len(newSp)):
            newDist += G[newSp[i - 1]][newSp[i]]['weight']

        if (abs(newDist - dist) <= adaptErr):
            refineFlag = False

        dist = newDist
        sp = newSp

    # Collect results =========================================================
    path = [startPt]
    for p in sp:
        if (p != 's' and p != 'e'):
            path.append(curveArcs[p[0]].query(p[1]).loc)
    path.append(endPt)

    # print("New dist: ", dist)
    # print("Adapt Iter Time: ", (datetime.datetime.now() - startTime).total_seconds())
    # print("Adapt Iter Num: ", iterNum)

    return {
        'path': path,
        'dist': dist
    }

def cone2ConePath(startPt: pt, endPt: pt, cones: dict, repSeq: list, tanAlpha: float, config = None):
    try:
        import gurobipy as grb
    except(ImportError):
        print("ERROR: Cannot find Gurobi")
        return

    model = grb.Model("SOCP")
    if (config == None or 'outputFlag' not in config or config['outputFlag'] == False):
        model.setParam('OutputFlag', 0)
    else:
        model.setParam('OutputFlag', 1)
    model.setParam('NonConvex', 2)

    # Parameters ==============================================================
    # anchor starts from startPt, in between are a list of cones, ends with endPt
    anchor = [startPt]
    for i in range(len(cones)):
        anchor.append(cones[i]['center'])
    anchor.append(endPt)

    allX = [startPt[0], endPt[0]]
    allY = [startPt[1], endPt[1]]
    for i in range(len(cones)):
        allX.append(cones[i]['center'][0] - cones[i]['maxHeight'] * tanAlpha)
        allX.append(cones[i]['center'][0] + cones[i]['maxHeight'] * tanAlpha)
        allY.append(cones[i]['center'][1] - cones[i]['maxHeight'] * tanAlpha)
        allY.append(cones[i]['center'][1] + cones[i]['maxHeight'] * tanAlpha)
    lbX = min(allX) - 1
    lbY = min(allY) - 1
    ubX = max(allX) + 1
    ubY = max(allY) + 1

    # Decision variables ======================================================
    # NOTE: x, y index starts by 1
    x = {}
    y = {}
    z = {}
    for i in range(1, len(cones) + 1):
        x[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = "x_%s" % i, lb = lbX, ub = ubX)
        y[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = "y_%s" % i, lb = lbY, ub = ubY)
        z[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = "z_%s" % i, lb = 0, ub = cones[repSeq[i - 1]]['maxHeight'])
    # Distance from ((xi, yi)) to (x[i + 1], y[i + 1]), 
    # where startPt = (x[0], y[0]) and endPt = (x[len(cones) + 1], y[len(cones) + 1])
    d = {}
    for i in range(len(cones) + 1):
        d[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'd_%s' % i)
    model.setObjective(grb.quicksum(d[i] for i in range(len(cones) + 1)), grb.GRB.MINIMIZE)

    # Aux vars - distance between (x, y)
    dx = {}
    dy = {}
    dz = {}
    for i in range(len(cones) + 1):
        dx[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'dx_%s' % i, lb = -float('inf'), ub = float('inf'))
        dy[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'dy_%s' % i, lb = -float('inf'), ub = float('inf'))
        dz[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'dz_%s' % i, lb = -float('inf'), ub = float('inf'))
    # Aux vars - distance from (x, y) to the center
    rx = {}
    ry = {}
    for i in range(1, len(cones) + 1):
        rx[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'rx_%s' % i, lb = -float('inf'), ub = float('inf'))
        ry[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'ry_%s' % i, lb = -float('inf'), ub = float('inf'))

    # Constraints =============================================================
    # Aux constr - dx dy
    model.addConstr(dx[0] == x[1] - anchor[0][0])
    model.addConstr(dy[0] == y[1] - anchor[0][1])
    model.addConstr(dz[0] == z[1] - anchor[0][2])
    for i in range(1, len(cones)):
        model.addConstr(dx[i] == x[i + 1] - x[i])
        model.addConstr(dy[i] == y[i + 1] - y[i])
        model.addConstr(dz[i] == z[i + 1] - z[i])
    model.addConstr(dx[len(cones)] == anchor[-1][0] - x[len(cones)])
    model.addConstr(dy[len(cones)] == anchor[-1][1] - y[len(cones)])
    model.addConstr(dz[len(cones)] == anchor[-1][2] - z[len(cones)])

    # Aux constr - rx ry
    for i in range(1, len(cones) + 1):
        model.addConstr(rx[i] == x[i] - anchor[i][0])
        model.addConstr(ry[i] == y[i] - anchor[i][1])

    # Distance btw visits
    for i in range(len(cones) + 1):
        model.addQConstr(d[i] ** 2 >= dx[i] ** 2 + dy[i] ** 2 + dz[i] ** 2)
    for i in range(1, len(cones) + 1):
        model.addQConstr(rx[i] ** 2 + ry[i] ** 2 <= (tanAlpha * z[i]) ** 2)

    model.modelSense = grb.GRB.MINIMIZE
    # model.write("SOCP.lp")
    model.optimize()

    # Post-processing =========================================================
    ofv = None
    path = [startPt]
    if (model.status == grb.GRB.status.OPTIMAL):
        solType = 'IP_Optimal'
        ofv = model.getObjective().getValue()
        for i in x:
            path.append((x[i].x, y[i].x, z[i].x))
        path.append(endPt)
        gap = 0
        lb = ofv
        ub = ofv
    elif (model.status == grb.GRB.status.TIME_LIMIT):
        solType = 'IP_TimeLimit'
        ofv = model.ObjVal
        for i in x:
            path.append((x[i].x, y[i].x, z[i].x))
        path.append(endPt)
        gap = model.MIPGap
        lb = model.ObjBoundC
        ub = model.ObjVal
    return {
        'path': path,
        'dist': ofv,
        'runtime': model.Runtime
    }

def vec2VecPath(startPt: pt, endPt: pt, vecs: list[dict], vehSpeed: float, config: dict = {'outputFlag': False}, closedFlag = False):
    try:
        import gurobipy as grb
    except(ImportError):
        raise ImportError("ERROR: Cannot find Gurobi")

    model = grb.Model("SOCP")
    if (config == None or 'outputFlag' not in config or config['outputFlag'] == False):
        model.setParam('OutputFlag', 0)
    else:
        model.setParam('OutputFlag', 1)

    if (config != None and 'gapTol' in config):
        model.setParam('MIPGap', config['gapTol'])

    model.setParam(grb.GRB.Param.TimeLimit, 15)

    # Parameters ==============================================================
    sx = {}
    sy = {}
    vx = {}
    vy = {}
    for i in range(1, len(vecs) + 1):
        sx[i] = vecs[i - 1]['loc'][0]
        sy[i] = vecs[i - 1]['loc'][1]
        vx[i] = vecs[i - 1]['vec'][0]
        vy[i] = vecs[i - 1]['vec'][1]

    # Decision variables ======================================================
    # (x[i], y[i]) 为第i个vec上相遇时的坐标
    # NOTE: 只有vec上的是决策变量
    # index = 1, 2, ..., len(vecs)
    x = {}
    y = {}
    for i in range(1, len(vecs) + 1):
        x[i] = model.addVar(vtype=grb.GRB.CONTINUOUS, name = "x_%s" % i, lb=-float('inf'), ub=float('inf'))
        y[i] = model.addVar(vtype=grb.GRB.CONTINUOUS, name = "y_%s" % i, lb=-float('inf'), ub=float('inf'))

    # d[i] 是 (x[i], y[i]) 到 (x[i + 1], y[i + 1])之间的距离
    d = {}
    for i in range(len(vecs) + 1):
        d[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'd_%s' % i)
    model.setObjective(grb.quicksum(d[i] for i in range(len(vecs) + 1)), grb.GRB.MINIMIZE)

    # Aux vars - distance between (x, y)
    dx = {}
    dy = {}
    for i in range(len(vecs) + 1):
        dx[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'dx_%s' % i, lb = -float('inf'), ub = float('inf'))
        dy[i] = model.addVar(vtype = grb.GRB.CONTINUOUS, name = 'dy_%s' % i, lb = -float('inf'), ub = float('inf'))

    t = {}
    for i in range(len(vecs) + 2):
        t[i] = model.addVar(vtype=grb.GRB.CONTINUOUS, name = "t_%s" % i, lb=0, ub=float('inf'))

    # Constraints =============================================================
    constr = {}
    # Aux constr - dx dy
    constr['dx_0'] = model.addConstr(dx[0] == x[1] - startPt[0])
    constr['dy_0'] = model.addConstr(dy[0] == y[1] - startPt[1])
    for i in range(1, len(vecs)):
        constr[f'dx_{i}'] = model.addConstr(dx[i] == x[i + 1] - x[i])
        constr[f'dy_{i}'] = model.addConstr(dy[i] == y[i + 1] - y[i])
    constr[f'dx_{len(vecs)}'] = model.addConstr(dx[len(vecs)] == endPt[0] - x[len(vecs)])
    constr[f'dy_{len(vecs)}'] = model.addConstr(dy[len(vecs)] == endPt[1] - y[len(vecs)])

    # 相遇时的位置
    for i in range(1, len(vecs) + 1):
        constr[f'sx_{i}'] = model.addConstr(x[i] == sx[i] + t[i] * vx[i])
        constr[f'sy_{i}'] = model.addConstr(y[i] == sy[i] + t[i] * vy[i])

    # Distance btw visits
    for i in range(len(vecs) + 1):
        constr[f'd_{i}'] = model.addQConstr(d[i] ** 2 >= dx[i] ** 2 + dy[i] ** 2)

    # 相遇点之间的距离
    constr['t_0'] = model.addConstr(t[0] == 0)
    for i in range(len(vecs) + 1):
        constr[f't_{i}'] = model.addConstr(t[i + 1] == t[i] + d[i] * (1 / vehSpeed))

    model.modelSense = grb.GRB.MINIMIZE
    # model.write("SOCP.lp")
    model.optimize()

    # Post-processing =========================================================
    ofv = None
    path = [startPt]
    timedSeq = [(startPt, 0)]
    if (model.status == grb.GRB.status.OPTIMAL):
        solType = 'IP_Optimal'
        ofv = model.getObjective().getValue()
        for i in x:
            path.append((x[i].x, y[i].x))
            timedSeq.append(((x[i].x, y[i].x), t[i].x))
        path.append(endPt)
        timedSeq.append((endPt, t[len(vecs) + 1].x))
        for c in constr:
            print(c, constr[c].Pi)
        gap = 0
        lb = ofv
        ub = ofv
        runtime = model.Runtime
    elif (model.status == grb.GRB.status.TIME_LIMIT):
        solType = 'IP_TimeLimit'
        ofv = model.ObjVal
        for i in x:
            path.append((x[i].x, y[i].x))
            timedSeq.append(((x[i].x, y[i].x), t[i].x))
        path.append(endPt)
        timedSeq.append((endPt, t[len(vecs) + 1].x))
        gap = model.MIPGap
        lb = model.ObjBoundC
        ub = model.ObjVal
        runtime = model.Runtime

    return {
        'dist': ofv,
        'time': t[len(vecs)].x,
        'path': path,
        'timedSeq': timedSeq,
        'runtime': runtime
    }

def triGridSurface2TriGridSurfacePath(startPt: pt, endPt: pt, triGridSurfaces:list[TriGridSurface], vehSpeed, startTime: float = 0):
    
    # 前向Greedy，给定一个初始的path3D，保留前startImpFrom项，从第s+1开始用最短距离计算
    def forwardPureGreedy():
        # 先用贪婪的方法，找到由一个点出发最短的到下一个surface的
        curPt = startPt  # 开始总是不变的
        curZ = startTime # 开始总是不变的
        newPath3D = [(curPt, curZ)]
        # print((curPt, curZ))
        for i in range(len(triGridSurfaces)):
            (curPt, curZ) = newPath3D[-1]
            p2F = triGridSurfaces[i].fastestPt2Facet(curPt, curZ, vehSpeed)
            curPt = p2F['pt']
            curZ = p2F['zVeh']
            newPath3D.append((curPt, curZ))
            # print((curPt, curZ))
        distLast = distEuclideanXY(curPt, endPt)
        timeLast = distLast / vehSpeed
        newPath3D.append((endPt, curZ + timeLast))
        # print((endPt, curZ + timeLast))
        return newPath3D

    # NOTE: len(triGridSurface) >= 2
    def forwardAdjustment(path3D):
        # 初始化
        curPt = startPt
        curZ = startTime
        curIdx = 0
        newPath3D = [(curPt, curZ)]

        for i in range(len(triGridSurfaces)):
            # NOTE: 根据第i+1个triGridSurface的pt，更新第i个triGridSurface的pt和z
            # 第i+1个的pt
            ptIPlus = path3D[i + 2][0]
            # try:
            pt2F2P = triGridSurfaces[i].fastestPt2Facet2Pt(pt1 = curPt, z1 = curZ, pt2 = ptIPlus, vehSpeed = vehSpeed)
            # except:
                # print(i, curPt, curZ, ptIPlus)

            curPt = pt2F2P['pt']
            curZ = pt2F2P['zVeh1']
            newPath3D.append((curPt, curZ))

        # 最后两个
        distLast = distEuclideanXY(curPt, endPt)
        timeLast = distLast / vehSpeed
        newPath3D.append((endPt, curZ + timeLast))
        return newPath3D

    path3D = forwardPureGreedy()

    oldT = path3D[-1][1]
    # print(oldT)
    stopFlag = False

    c = 0
    while (not stopFlag):
        # Update
        path3D = forwardAdjustment(path3D)
        newT = path3D[-1][1]
        # print(newT)
        if (abs(oldT - newT) < 0.01):
            stopFlag = True
        
        c += 1
        if (c > 10):
            warnings.warn("WARNING: Too many iterations for triGridSurfaces2TridGridSurfaces. Current dt = %s" % (newT - oldT))
            break

        oldT = newT

    dist = 0
    for i in range(len(path3D) - 1):
        dist += distEuclideanXY(path3D[i][0], path3D[i + 1][0])

    time = path3D[-1][1] - path3D[0][1]

    return {
        'dist': dist,
        'time': time,
        'path': [i[0] for i in path3D],
        'path3D': path3D,
    }

def ring2RingPath(startPt: pt, endPt: pt, seq: list, nodes: dict, noFlyShell: list[poly], polyVG: dict, **kwargs):

    # NOTE: 迭代的方法
    # Step 1: 先使用multiPoly2MultiPoly生成一个路径
    # Step 2: 固定所有的转折点，由于已经可以保证转折点不在禁飞区内，只要路上不经过就行了
    # Step 3: 固定转折点前后的点，局部搜索转折点新的位置，如果总长变化很小，结束，否则转到Step 2

    # 先构造multiPolys
    multiPolys = []
    for i in range(len(seq)):
        multiPoly = []
        for k in nodes[seq[i]]['neiShell']:
            multiPoly.append(k)
        multiPolys.append(multiPoly)

    # 然后构造holes
    holes = None
    hasHoleFlag = False
    for i in range(len(seq)):
        if (nodes[seq[i]]['neiHoles'] != None):
            hasHoleFlag = True
    if (hasHoleFlag):
        holes = []
        for i in range(len(seq)):
            holes.append([])
            if (nodes[seq[i]]['neiHoles'] != None):
                holes[i].append(nodes[seq[i]]['neiHoles'])

    # 构造初始路径
    m2m = multiPoly2MultiPolyPath(startPt, endPt, multiPolys, holes, **kwargs)
    
    # 记录seq对应的每一个点
    # len(visitLocs) == len(seq)
    visitLocs = [{
        'nodeID': 0,
        'loc': startPt,
        'needUpdate': False
    }]
    for i in range(1, len(m2m['path']) - 1):
        visitLocs.append({
            'nodeID': seq[i - 1],
            'loc': m2m['path'][i],
            'needUpdate': True
        })
    visitLocs.append({
        'nodeID': -1,
        'loc': endPt,
        'needUpdate': False
    })

    # len(sps) == len(seq) - 1
    sps = []
    for i in range(len(m2m['path']) - 1):
        if (is2PtsSame(m2m['path'][i], m2m['path'][i + 1])):
            sps.append([])
        else:
            path = distBtwPolysXY(
                pt1 = m2m['path'][i], 
                pt2 = m2m['path'][i + 1], 
                polys = noFlyShell,
                polyVG = polyVG, 
                detailFlag = True)
            if (len(path['path']) > 2):
                sps.append(path['path'][1:-1])
            else:
                sps.append([])

    oldDist = 0
    oldPath = []
    for k in range(len(visitLocs) - 1):
        oldPath.append(visitLocs[k]['loc'])
        oldPath.extend(sps[k])
    oldPath.append(visitLocs[-1]['loc'])
    for k in range(len(oldPath) - 1):
        oldDist += distEuclideanXY(oldPath[k], oldPath[k + 1])
    newPath = []
    
    # 迭代调整visitLocs和sps，直到不能改进为止
    iterNum = 0
    contFlag = True
    while (contFlag):
        contFlag = False
        iterNum += 1

        # 每个visit point更新一轮
        for i in range(1, len(visitLocs) - 1):
            if (visitLocs[i]['needUpdate']):
                # 旧位置
                oldLoc = visitLocs[i]['loc']
                
                prevLoc = None
                if (len(sps[i - 1]) > 0):
                    prevLoc = sps[i - 1][-1]
                else:
                    prevLoc = visitLocs[i - 1]['loc']
                nextLoc = None
                if (len(sps[i]) > 0):
                    nextLoc = sps[i][0]
                else:
                    nextLoc = visitLocs[i + 1]['loc']

                s2sHole = None
                if (holes != None and holes[i - 1] != None and len(holes[i - 1]) > 0):
                    s2sHole = [holes[i - 1]]

                s2s = multiPoly2MultiPolyPath(
                    startPt = prevLoc, 
                    endPt = nextLoc, 
                    multiPolys = [multiPolys[i - 1]],
                    holes = s2sHole)
                
                # 新位置
                # print(s2s['path'])
                newLoc = s2s['path'][1]
                visitLocs[i]['loc'] = newLoc
               
                if (not is2PtsSame(oldLoc, newLoc)):
                    contFlag = True
                    # print(i)
                    # print(visitLocs)
                    if (is2PtsSame(visitLocs[i - 1]['loc'], newLoc)):
                        sps[i - 1] = []
                    else:
                        prevSP = distBtwPolysXY(
                            pt1 = visitLocs[i - 1]['loc'], 
                            pt2 = newLoc, 
                            polys = noFlyShell,
                            polyVG = polyVG, 
                            detailFlag = True)
                        if (len(prevSP['path']) > 2):
                            sps[i - 1] = prevSP['path'][1:-1]
                        else:
                            sps[i - 1] = []

                    if (is2PtsSame(visitLocs[i + 1]['loc'], newLoc)):
                        sps[i - 1] = []
                    else:
                        nextSP = distBtwPolysXY(
                            pt1 = newLoc, 
                            pt2 = visitLocs[i + 1]['loc'], 
                            polys = noFlyShell,
                            polyVG = polyVG, 
                            detailFlag = True)
                        if (len(nextSP['path']) > 2):
                            sps[i] = nextSP['path'][1:-1]
                        else:
                            sps[i] = []

                    # Update necessary
                    visitLocs[i]['needUpdate'] = True
                    if (i > 1):
                        visitLocs[i - 1]['needUpdate'] = True
                    if (i < len(visitLocs) - 1):
                        visitLocs[i + 1]['needUpdate'] = True
                else:
                    visitLocs[i]['needUpdate'] = False

        newDist = 0
        newPath = []
        for k in range(len(visitLocs) - 1):
            newPath.append(visitLocs[k]['loc'])
            newPath.extend(sps[k])
        newPath.append(visitLocs[-1]['loc'])
        for k in range(len(newPath) - 1):
            newDist += distEuclideanXY(newPath[k], newPath[k + 1])

        print(iterNum, "oldDist => newDist: ", oldDist, newDist)

        if (oldDist - newDist < 0.0001):
            contFlag = False

        oldDist = newDist

    return {
        'dist': newDist,
        'visitLocs': visitLocs,
        'sps': sps,
        'path': newPath
    }

