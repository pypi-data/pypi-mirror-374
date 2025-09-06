import math
import random
import warnings

from .common import *
from .geometry import *
from .msg import *
from .road import *
from .gridSurface import *

def rndLocs(
    N: int, 
    distr = 'UniformSquareXY', 
    **kwargs) -> list:

    """Randomly create a list of N locations

    Parameters
    ----------

    N: integer, required
        Number of locations/vertices/customers to be randomly created
    distr: string, optional, default as 'UniformSquareXY'
        Spatial distribution of locations, options and required additional inputs are as follows:

        1) (default) 'UniformSquareXY', uniformly sample from a square on the Euclidean space
            - xRange: 2-tuple, with minimum/maximum range of x, default as (0, 100)
            - yRange: 2-tuple, with minimum/maximum range of y, default as (0, 100)
        2) 'UniformPolyXY', uniformly sample from a given polygon
            - polyXY: poly, the polygon of the area, (no holes)
            - polyXYs: list of polys, alternative option for `polyXY`
        3) 'UniformAvoidPolyXY', uniformly sample from a square avoiding some polygons
            - xRange: 2-tuple, with minimum/maximum range of x, default as (0, 100)
            - yRange: 2-tuple, with minimum/maximum range of y, default as (0, 100)
            - polyXY: poly, the polygon of the area, (no holes)
            - polyXYs: list of polys, alternative option for `polyXY`
        4) 'UniformCircleXY', uniformly sample from a circle on the Euclidean space
            - centerXY: 2-tuple, the center of circle
            - radius: float, the radius of the circle
        5) 'UniformPolyLatLon', uniformly sample from a polygon by lat/lon
            - polyLatLon: poly, the polygon of the area, (no holes)
            - polyLatLons: list of polys, alternative option for `polyLatLon`
        6) 'UniformCircleLatLon', uniformly sample from a circle by lat/lon
            - centerLatLon: 2-tuple, the (lat, lon) for the center
            - radiusInMeters: float, the radius of the circle in meters
        7) 'RoadNetworkPolyLatLon', uniformly generate within a given polygon on a road network
            - roads: dict, the road network dictionary
            - polyLatLon: poly, optional, the polygon on the map to sample from
            - polyLatLons: list of polys, optional, alternative for `polyLatLon`
            - roadClass: list[str], the road classes that allows to sample from
        8) 'RoadNetworkCircleLatLon', uniformly generate within a circle on a road network
            - roads: dict, the road network dictionary
            - centerLatLon: 2-tuple, the (lat, lon) for the center
            - radiusInMeters: float, the radius of the circle in meters
            - roadClass: list[str], the road classes that allows to sample from
    **kwargs: optional
        Provide additional inputs for different `distr` options

    Returns
    -------
    list
        A list of randomly created locations

    Raises
    ------
    MissingParameterError
        Missing required inputs in `**kwargs`.
    UnsupportedInputError
        Option is not supported for `distr`
    NotAvailableError
        Functions/options that are not ready yet.
    EmptyError
        The sample area is empty.
    """

    nodeLocs = []
    # Uniformly sample from a square on the Euclidean space
    if (distr == 'UniformSquareXY'):
        xRange = None
        yRange = None
        if ('xRange' not in kwargs or 'yRange' not in kwargs):
            xRange = [0, 100]
            yRange = [0, 100]
            warnings.warn("WARNING: Set sampled area to be default as a (0, 100) x (0, 100) square")
        else:
            xRange = [float(kwargs['xRange'][0]), float(kwargs['xRange'][1])]
            yRange = [float(kwargs['yRange'][0]), float(kwargs['yRange'][1])]
        for n in range(N):
            nodeLocs.append(_rndPtUniformSquareXY(xRange, yRange))

    elif (distr == 'UniformCubeXYZ'):
        xRange = None
        yRange = None
        zRange = None
        if ('xRange' not in kwargs or 'yRange' not in kwargs or 'zRange' not in kwargs):
            xRange = [0, 100]
            yRange = [0, 100]
            zRange = [0, 100]
            warnings.warn("WARNING: Set sampled area to be default as a (0, 100) x (0, 100) x (0, 100) cube")
        else:
            xRange = [float(kwargs['xRange'][0]), float(kwargs['xRange'][1])]
            yRange = [float(kwargs['yRange'][0]), float(kwargs['yRange'][1])]
            zRange = [float(kwargs['zRange'][0]), float(kwargs['zRange'][1])]
        for n in range(N):
            nodeLocs.append(_rndPtUniformCubeXYZ(xRange, yRange, zRange))

    # Uniformly sample from a polygon/a list of polygons on the Euclidean space
    elif (distr == 'UniformPolyXY'):
        if ('polyXY' not in kwargs and 'polyXYs' not in kwargs):
            raise MissingParameterError("ERROR: Missing required args 'polyXY' or 'polyXYs', which indicates a polygon / a list of polygons in the Euclidean space")
        if ('polyXY' in kwargs):
            for n in range(N):
                nodeLocs.append(_rndPtUniformPolyXY(kwargs['polyXY']))
        elif ('polyXYs' in kwargs):
            for n in range(N):
                nodeLocs.append(_rndPtUniformPolyXYs(kwargs['polyXY']))

    # Uniformly sample from the Euclidean space avoiding polygons
    elif (distr == 'UniformAvoidPolyXY'):
        if ('polyXY' not in kwargs and 'polyXYs' not in kwargs):
            raise MissingParameterError("ERROR: Missing required args 'polyXY' or 'polyXYs', which indicates a polygon / a list of polygons in the Euclidean space")
        xRange = None
        yRange = None
        if ('xRange' not in kwargs or 'yRange' not in kwargs):
            xRange = [0, 100]
            yRange = [0, 100]
            warnings.warn("WARNING: Set sampled area to be default as a (0, 100) x (0, 100) square")
        else:
            xRange = [float(kwargs['xRange'][0]), float(kwargs['xRange'][1])]
            yRange = [float(kwargs['yRange'][0]), float(kwargs['yRange'][1])]
        if ('polyXY' in kwargs):
            for n in range(N):
                nodeLocs.append(_rndPtUniformAvoidPolyXY(kwargs['polyXY'], xRange, yRange))
        elif ('polyXYs' in kwargs):
            for n in range(N):
                nodeLocs.append(_rndPtUniformAvoidPolyXYs(kwargs['polyXYs'], xRange, yRange))

    # Uniformly sample from a circle on the Euclidean space
    elif (distr == 'UniformCircleXY'):
        centerXY = None
        radius = None
        if ('centerXY' not in kwargs or 'radius' not in kwargs):
            centerXY = (0, 0)
            radius = 100
            warnings.warn("WARNING: Set sample area to be default as a circle with radius of 100 centering at (0, 0)")
        else:
            centerXY = kwargs['centerXY']
            radius = kwargs['radius']
        for n in range(N):
            nodeLocs.append(_rndPtUniformCircleXY(radius, centerXY))

    # Uniformly sample from a polygon by lat/lon
    elif (distr == 'UniformPolyLatLon'):
        if ('polyLatLon' not in kwargs and 'polyLatLons' not in kwargs):
            raise MissingParameterError("ERROR: Missing required args 'polyXY' or 'polyXYs', which indicates a polygon / a list of polygons in the Euclidean space")
        # TODO: Mercator projection
        raise VrpSolverNotAvailableError("ERROR: 'UniformPolyLatLon' is not available yet, please stay tune.")

    # Uniformly sample from a circle by lat/lon
    elif (distr == 'UniformCircleLatLon'):
        if ('centerLatLon' not in kwargs or 'radiusInMeters' not in kwargs):
            raise MissingParameterError("ERROR: Missing required args 'centerLatLon' or 'radiusInMeters'.")
        for n in range(N):
            nodeLocs.append(_rndPtUniformCircleLatLon(kwargs['radiusInMeters'], kwargs['centerLatLon']))

    # Uniformly sample from the roads/streets within a polygon/a list of polygons from given road networks
    elif (distr == 'RoadNetworkPolyLatLon'):
        if ('polyLatLon' not in kwargs and 'polyLatLons' not in kwargs):
            raise MissingParameterError("ERROR: Missing required args 'polyLatLon' or 'polyLatLons', which indicates a polygon / a list of polygons in the Euclidean space")
        elif ('roads' not in kwargs):
            raise MissingParameterError("ERROR: Missing required args 'RoadNetwork'. Need to provide the road network where the nodes are generated.")
        elif ('roadClass' not in kwargs):
            warnings.warn("WARNING: Set 'roadClass' to be default as ['residential']")
        if ('polyLatLon' in kwargs):
            nodeLocs = _rndPtRoadNetworkPolyLatLon(
                N if N != None else len(nodeIDs),
                kwargs['roads'], 
                kwargs['polyLatLon'],
                kwargs['roadClass'] if 'roadClass' in kwargs else ['residential'])
        elif ('polyLatLons' in kwargs):
            nodeLocs = _rndPtRoadNetworkPolyLatLons(
                N if N != None else len(nodeIDs),
                kwargs['roads'], 
                kwargs['polyLatLons'],
                kwargs['roadClass'] if 'roadClass' in kwargs else ['residential'])

    # Uniformly sample from the roads/streets within a circle from given road network
    elif (distr == 'RoadNetworkCircleLatLon'):
        if ('centerLatLon' not in kwargs or 'radiusInMeters' not in kwargs):
            raise MissingParameterError("ERROR: Missing required args 'centerLatLon' or 'radiusInMeters'.")
        elif ('roads' not in kwargs):
            raise MissingParameterError("ERROR: Missing required args 'RoadNetwork'. Need to provide the road network where the nodes are generated.")
        elif ('roadClass' not in kwargs):
            warnings.warn("WARNING: Set 'roadClass' to be default as ['residential']")
        nodeLocs = _rndPtRoadNetworkCircleLatLon(
            N if N != None else len(nodeIDs),
            kwargs['roads'], 
            kwargs['radiusInMeters'],
            kwargs['centerLatLon'],
            kwargs['roadClass'] if 'roadClass' in kwargs else ['residential'])
    
    else:
        raise UnsupportedInputError(ERROR_MISSING_NODES_DISTR)

    return nodeLocs

def _rndPtUniformSquareXY(xRange: list[int]|list[float], yRange: list[int]|list[float]) -> pt:
    x = random.uniform(xRange[0], xRange[1])
    y = random.uniform(yRange[0], yRange[1])
    return (x, y)

def _rndPtUniformCubeXYZ(xRange: list[int]|list[float], yRange: list[int]|list[float], zRange: list[int]|list[float]) -> pt3D:
    x = random.uniform(xRange[0], xRange[1])
    y = random.uniform(yRange[0], yRange[1])
    z = random.uniform(zRange[0], zRange[1])
    return (x, y, z)

def _rndPtUniformTriangleXY(triangle: poly) -> pt:
    
    # Get three extreme points ================================================
    [x1, y1] = triangle[0]
    [x2, y2] = triangle[1]
    [x3, y3] = triangle[2]

    # Generate random points ==================================================
    rndR1 = random.uniform(0, 1)
    rndR2 = random.uniform(0, 1)
    x = (1 - math.sqrt(rndR1)) * x1 + math.sqrt(rndR1) * (1 - rndR2) * x2 + math.sqrt(rndR1) * rndR2 * x3
    y = (1 - math.sqrt(rndR1)) * y1 + math.sqrt(rndR1) * (1 - rndR2) * y2 + math.sqrt(rndR1) * rndR2 * y3

    return (x, y)

def _rndPtUniformPolyXY(poly: poly) -> pt:
    # Get list of triangles ===================================================
    # TODO: polyTriangulation() to be replaced
    lstTriangle = polyTriangulation(poly)

    # Weight them and make draws ==============================================
    lstWeight = []
    for i in range(len(lstTriangle)):
        lstWeight.append(calTriangleAreaXY(lstTriangle[i][0], lstTriangle[i][1], lstTriangle[i][2]))

    # Select a triangle and randomize a point in the triangle =================
    idx = rndPick(lstWeight)
    (x, y) = _rndPtUniformTriangleXY(lstTriangle[idx])

    return (x, y)

def _rndPtUniformPolyXYs(polys: polys) -> pt:
    # Get all triangulated triangles ==========================================
    # TODO: polyTriangulation() to be replaced
    lstTriangle = []
    for p in polys:
        lstTriangle.extend(polyTriangulation(p))

    # Weight them and make draws ==============================================
    lstWeight = []
    for i in range(len(lstTriangle)):
        lstWeight.append(calTriangleAreaXY(lstTriangle[i][0], lstTriangle[i][1], lstTriangle[i][2]))

    # Select a triangle and randomize a point in the triangle =================
    idx = rndPick(lstWeight)
    (x, y) = _rndPtUniformTriangleXY(lstTriangle[idx])

    return (x, y)

def _rndPtUniformAvoidPolyXY(poly: poly, xRange: list[int]|list[float], yRange: list[int]|list[float]) -> pt:
    # Use the low efficient accept-denial approach
    while (True):
        x = random.uniform(xRange[0], xRange[1])
        y = random.uniform(yRange[0], yRange[1])
        if (not isPtInPoly((x, y), poly)):
            return (x, y)

def _rndPtUniformAvoidPolyXYs(polys: polys, xRange: list[int]|list[float], yRange: list[int]|list[float]) -> pt:
    while (True):
        x = random.uniform(xRange[0], xRange[1])
        y = random.uniform(yRange[0], yRange[1])
        notInPolys = True
        for p in polys:
            if (isPtInPoly((x, y), p)):
                notInPolys = False
                break
        if (notInPolys):
            return (x, y)

def _rndPtUniformCircleXY(radius: float, center: pt) -> pt:
    theta = random.uniform(0, 2 * math.pi)
    r = math.sqrt(random.uniform(0, radius ** 2))
    x = center[0] + r * math.cos(theta)
    y = center[1] + r * math.sin(theta)

    return (x, y)

def _rndPtUniformCircleLatLon(radius: float, center: pt) -> pt:
    theta = random.uniform(0, 2 * math.pi)
    r = math.sqrt(random.uniform(0, radius ** 2))
    (lat, lon) = ptInDistLatLon(center, theta, r)

    return (lat, lon)

def _rndPtRoadNetworkPolyLatLon(N: int, roads: dict, poly: poly, roadClass: str | list[str]) -> list[pt]:
    # If poly is given, clip road networks by poly ============================
    clipRoad = {}
    if (poly != None):
        clipRoad = clipRoadsByPoly(roads, poly)
    else:
        clipRoad = roads

    # Calculate the length of each edge =======================================
    lengths = []
    roadIDs = []
    for rID in clipRoad:
        roadLength = 0
        includedFlag = False
        if ('class' in clipRoad[rID] and clipRoad[rID]['class'] in roadClass):
            for i in range(len(clipRoad[rID]['shape']) - 1):
                roadLength += distLatLon(clipRoad[rID]['shape'][i], clipRoad[rID]['shape'][i + 1])
            lengths.append(roadLength)
            roadIDs.append(rID)

    # Check if there are roads included =======================================
    if (sum(lengths) == 0):
        raise EmptyError("ERROR: No road is found.")

    # Use accept-denial to test if the node is within poly ====================
    # FIXME: Inefficient approach, will need to be rewritten
    # TODO: Truncate the roads that partially inside polygon
    nodeLocs = []
    for i in range(N):
        lat = None
        lon = None
        idx = rndPick(lengths)
        edgeLength = lengths[idx]
        edgeDist = random.uniform(0, 1) * edgeLength
        (lat, lon) = ptInSeqMileage(clipRoad[roadIDs[idx]]['shape'], edgeDist, 'LatLon')
        nodeLocs.append((lat, lon))

    return nodeLocs

def _rndPtRoadNetworkPolyLatLons(N: int, roads: dict, polys: polys, roadClass: str | list[str]) -> list[pt]:
    # If poly is given, clip road networks by poly ============================
    clipRoad = {}
    if (poly != None):
        clipRoad = clipRoadsByPolys(roads, polys)
    else:
        clipRoad = roads

    # Calculate the length of each edge =======================================
    lengths = []
    roadIDs = []
    for rID in clipRoad:
        roadLength = 0
        includedFlag = False
        if ('class' in clipRoad[rID] and clipRoad[rID]['class'] in roadClass):
            for i in range(len(clipRoad[rID]['shape']) - 1):
                roadLength += distLatLon(clipRoad[rID]['shape'][i], clipRoad[rID]['shape'][i + 1])
            lengths.append(roadLength)
            roadIDs.append(rID)

    # Check if there are roads included =======================================
    if (sum(lengths) == 0):
        raise EmptyError("ERROR: No road is found.")

    # Use accept-denial to test if the node is within poly ====================
    # FIXME: Inefficient approach, will need to be rewritten
    # TODO: Truncate the roads that partially inside polygon
    nodeLocs = []
    for i in range(N):
        lat = None
        lon = None
        idx = rndPick(lengths)
        edgeLength = lengths[idx]
        edgeDist = random.uniform(0, 1) * edgeLength
        (lat, lon) = ptInSeqMileage(clipRoad[roadIDs[idx]]['shape'], edgeDist, 'LatLon')
        nodeLocs.append((lat, lon))

    return nodeLocs

def _rndPtRoadNetworkCircleLatLon(N: int, roads: dict, radius: float, center: pt, roadClass: str | list[str]) -> list[pt]:
    # Calculate the length of each edge =======================================
    lengths = []
    roadIDs = []
    for rID in roads:
        roadLength = 0
        includedFlag = False
        for i in range(len(roads[rID]['shape'])):
            if ('class' in roads[rID] and roads[rID]['class'] in roadClass and distLatLon(roads[rID]['shape'][i], center) <= radius):
                includedFlag = True
                break

        # Check if this road is inside polygon
        if (includedFlag):
            for i in range(len(roads[rID]['shape']) - 1):
                roadLength += distLatLon(roads[rID]['shape'][i], roads[rID]['shape'][i + 1])
            lengths.append(roadLength)            
        else:
            lengths.append(0)

        roadIDs.append(rID)


    # Check if there are roads included =======================================
    if (sum(lengths) == 0):
        raise EmptyError("ERROR: No road is found.")

    # Use accept-denial to test if the node is within poly ====================
    # FIXME: Inefficient approach, will need to be rewritten
    nodeLocs = []
    for i in range(N):
        lat = None
        lon = None
        insideFlag = False
        while (not insideFlag):
            idx = rndPick(lengths)
            edgeLength = lengths[idx]
            edgeDist = random.uniform(0, 1) * edgeLength
            (lat, lon) = ptInSeqMileage(roads[roadIDs[idx]]['shape'], edgeDist, 'LatLon')
            if (distLatLon([lat, lon], center) <= radius):
                insideFlag = True
        nodeLocs.append((lat, lon))

    return nodeLocs

def rndNodes(
    N: int|None = None, 
    nodeIDs: list[int|str] = [], 
    nodes: dict|None = None,
    distr = 'UniformSquareXY',
    **kwargs
    ) -> dict:

    """Randomly create a nodes dictionary

    Parameters
    ----------

    N: integer, optional
        Number of locations/vertices/customers to be randomly created
    nodeIDs: list of int|str, optional
        A list of ids for the locations to be created, an alternative option for `N`
    nodes: dict, optional
        A nodes dictionary, if given, new locations will be append into this dictionary
    distr: string, optional, default as 'UniformSquareXY'
        See `distr` docstring in :func:`~geoVeRoPy.instance.rndLocs()`
    locFieldName: str, optional, default as 'loc'
        The key in nodes dictionary to indicate the locations
    **kwargs: optional
        Provide additional inputs for different `distr` options

    Returns
    -------
    list
        A list of randomly created locations
    """

    # Sanity checks ===========================================================
    if (nodes == None):
        nodes = {}
    
    if (nodeIDs == [] and N == None):
        raise MissingParameterError(ERROR_MISSING_N)
    elif (nodeIDs == [] and N != None):
        nodeIDs = [i for i in range(N)]

    # Field names =============================================================
    locFieldName = 'loc' if 'locFieldName' not in kwargs else kwargs['locFieldName']

    # Generate instance =======================================================
    nodeLocs = rndLocs(
        N = len(nodeIDs), 
        distr = distr,
        **kwargs)
    for n in range(len(nodeIDs)):
        if (nodeIDs[n] in nodes):
            warnings.warn("WARNING: %s already exists, will be replaced" % n)
        nodes[nodeIDs[n]] = {
            locFieldName: nodeLocs[n]
        }

    return nodes

def rndNodeNeighbors(
    nodes: dict,
    nodeIDs: list[int|str]|str = 'All', 
    shape: str = 'Circle',
    **kwargs
    ) -> dict:

    """Given a node dictionary, create neighborhood to selected nodes

    WARNING
    -------    
    This function will modify the input dictionary `nodes`

    Parameters
    ----------
    nodes: dictionary, required
        A plain nodes dictionary to add neighborhoods.
    nodeIDs: string|list[int|str], optional, default 'All'
        A list of node IDs to add neighborhood, leave it as 'All' to indicate adding such information to all nodes.
    shape: str, optional, default as 'Circle'
        The shape of neighborhoods, options and required additional inputs are as follows:

        1) (default) 'Circle', add circle surrounding nodes
            - 'radius': The radius, default as 1
            - 'lod': The level of details, circle will be approximated as a x-gon polygon, default as 30
        2) 'Poly', add polygon surrounding nodes
            - 'poly': In relative axis where node locates in [0, 0]
        3) 'Egg', add egg shape to nodes. The curve function: :math:`\\frac{x^2}{(a - b)x + ab} + \\frac{y^2}{c^2} = 1`
            - 'a': required
            - 'b': required
            - 'c': required
            - 'direction': default as 0
            - 'lod': default as 30
        4) 'RndSquare', add random size squares around nodes
            - 'minLen': required, minimum length
            - 'maxLen': required, maximum length
        4) 'RndCurvy', add random curvy shapes around nodes
            - 'maxRadius': default as 1.2
            - 'minRadius': default as 0.8
            - 'N': default as 5
            - 'w': default as 3
            - 'lod': default as 30
        5) 'RndConvexPoly', add convex polygons with random size around nodes
            - 'maxNumSide': maximum number of sides
            - 'maxDiag': maximum length of the diagonal
            - 'minDiag': minimum length of the diagonal
    **kwargs: optional
        Provide additional inputs for different `distr` options

    Returns
    -------
    dict
        Changes will apply to the original `nodes` dictionary

    """

    # Sanity check ============================================================
    if (type(nodeIDs) is not list):
        if (nodeIDs == 'All'):
            nodeIDs = [i for i in nodes]
        else:
            for i in nodeIDs:
                if (i not in nodes):
                    raise OutOfRangeError("ERROR: Node %s is not in `nodes`." % i)
    
    # Field names =============================================================
    locFieldName = 'loc' if 'locFieldName' not in kwargs else kwargs['locFieldName']
    neighborFieldName = 'neighbor' if 'neighborFieldName' not in kwargs else kwargs['neighborFieldName']

    # Add neighborhood by 'shape' =============================================
    if (shape == 'Poly'):
        for n in nodeIDs:
            if ('poly' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'poly'")
            
            nodes[n]['neiShape'] = 'Poly'
            poly = [[i[0] + nodes[n][locFieldName][0], i[1] + nodes[n][locFieldName][1]] for i in kwargs['poly']]
            nodes[n][neighborFieldName] = [poly[i] for i in range(len(poly)) if distEuclideanXY(poly[i], poly[i - 1]) > ERRTOL['distPt2Pt']]
            
    elif (shape == 'Circle'):
        for n in nodeIDs:
            if ('radius' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'radius'")
            # By default, a circle is plotted by a 30-gon
            lod = 30
            if ('lod' in kwargs and type(kwargs['lod']) == int):
                lod = kwargs['lod']

            nodes[n]['neiShape'] = 'Circle'
            nodes[n]['radius'] = kwargs['radius']

            poly = [[
                nodes[n][locFieldName][0] + kwargs['radius'] * math.sin(2 * d * math.pi / lod),
                nodes[n][locFieldName][1] + kwargs['radius'] * math.cos(2 * d * math.pi / lod),
            ] for d in range(lod + 1)]
            nodes[n][neighborFieldName] = [poly[i] for i in range(len(poly)) if distEuclideanXY(poly[i], poly[i - 1]) > ERRTOL['distPt2Pt']]

    elif (shape == 'RndCircle'):
        for n in nodeIDs:
            if ('minRadius' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'minRadius'")
            if ('maxRadius' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'maxRadius'")
            # By default, a circle is plotted by a 30-gon
            lod = 30
            if ('lod' in kwargs and type(kwargs['lod']) == int):
                lod = kwargs['lod']

            radius = random.uniform(kwargs['minRadius'], kwargs['maxRadius'])

            nodes[n]['neiShape'] = 'Circle'
            nodes[n]['radius'] = radius

            poly = [[
                nodes[n][locFieldName][0] + radius * math.sin(2 * d * math.pi / lod),
                nodes[n][locFieldName][1] + radius * math.cos(2 * d * math.pi / lod),
            ] for d in range(lod + 1)]
            nodes[n][neighborFieldName] = [poly[i] for i in range(len(poly)) if distEuclideanXY(poly[i], poly[i - 1]) > ERRTOL['distPt2Pt']]

    elif (shape == 'Egg'):
        for n in nodeIDs:
            if ('a' not in kwargs or 'b' not in kwargs or 'c' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'a', 'b', and/or 'c'.")
            direction = 0
            if ('direction' in kwargs):
                direction = kwargs['direction']
            lod = 30
            if ('lod' in kwargs and type(kwargs['lod']) == int):
                lod = kwargs['lod']
            
            nodes[n]['neiShape'] = 'Poly'
            # Formulation:
            # \frac{x^2}{(a - b)x + ab} + \frac{y^2}{c^2} = 1
            a = kwargs['a']
            b = kwargs['b']
            c = kwargs['c']
            nodes[n]['parameter'] = {
                'a': a,
                'b': b,
                'c': c
            }
            
            vHLod = math.ceil(lod * 2 / 9)
            vTLod = math.ceil(lod / 9)
            hLod = math.ceil(lod * 2 / 3)

            polyL = []
            polyM = []
            polyR = []
            for d in range(vHLod + 1):
                y = c * 0.75 * d / vHLod
                A = 1
                B = (y ** 2 / c ** 2 - 1) * (a - b)
                C = (y ** 2 / c ** 2 - 1) * a * b
                X = (-B - math.sqrt(B ** 2 - 4 * A * C)) / (2 * A)
                polyL.append((X, y))
                xStart = X
            for d in range(vTLod + 1):
                y = c * 0.4 * d / vHLod
                A = 1
                B = (y ** 2 / c ** 2 - 1) * (a - b)
                C = (y ** 2 / c ** 2 - 1) * a * b
                X = (-B + math.sqrt(B ** 2 - 4 * A * C)) / (2 * A)
                polyR.insert(0, (X, y))
                xEnd = X
            for d in range(hLod + 1):
                x = xStart + (xEnd - xStart) * d / hLod
                Y = math.sqrt(c * c * (1 - (x * x) / ((a - b) * x + a * b)))
                polyM.append((x, Y))
            polyHf = []
            polyHf.extend(polyL)
            polyHf.extend(polyM)
            polyHf.extend(polyR)

            polyB4Rot = [i for i in polyHf]
            polyB4Rot.extend([(polyHf[len(polyHf) - 1 - k][0], - polyHf[len(polyHf) - 1 - k][1]) for k in range(len(polyHf))])
            
            u = math.cos(math.radians(direction))
            v = math.sin(math.radians(direction))
            poly = [(nodes[n][locFieldName][0] + u * pt[0] + v * pt[1], nodes[n][locFieldName][1] + -v * pt[0] + u * pt[1]) for pt in polyB4Rot]
            nodes[n][neighborFieldName] = [poly[i] for i in range(len(poly)) if distEuclideanXY(poly[i], poly[i - 1]) > ERRTOL['distPt2Pt']]
            
    elif (shape == 'RndSquare'):
        for n in nodeIDs:
            if ('maxLen' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'maxLen'")
            if ('minLen' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'minLen'")
            if (kwargs['minLen'] > kwargs['maxLen']):
                warnings.warn("WARNING: 'minLen' is greater than 'maxLen', will be swapped")
                kwargs['maxLen'], kwargs['minLen'] = kwargs['minLen'], kwargs['maxLen']
            
            nodes[n]['neiShape'] = 'Poly'            
            length = random.uniform(kwargs['minLen'], kwargs['maxLen'])

            nodes[n]['parameter'] = {
                'length': length
            }

            nodes[n][neighborFieldName] = [
                [nodes[n][locFieldName][0] - length / 2, nodes[n][locFieldName][1] - length / 2], 
                [nodes[n][locFieldName][0] + length / 2, nodes[n][locFieldName][1] - length / 2], 
                [nodes[n][locFieldName][0] + length / 2, nodes[n][locFieldName][1] + length / 2], 
                [nodes[n][locFieldName][0] - length / 2, nodes[n][locFieldName][1] + length / 2]
            ]

    elif (shape == 'RndRectangle'):
        for n in nodeIDs:
            if ('minWidth' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'minWidth'")
            if ('maxWidth' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'maxWidth'")
            if ('minLength' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'minLength'")
            if ('maxLength' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'maxLength'")
            if (kwargs['minWidth'] > kwargs['maxWidth']):
                warnings.warn("WARNING: 'minWidth' is greater than 'maxWidth', will be swapped")
                kwargs['maxWidth'], kwargs['minWidth'] = kwargs['minWidth'], kwargs['maxWidth']
            if (kwargs['minLength'] > kwargs['maxLength']):
                warnings.warn("WARNING: 'minLength' is greater than 'maxLength', will be swapped")
                kwargs['maxLength'], kwargs['minLength'] = kwargs['minLength'], kwargs['maxLength']

            nodes[n]['neiShape'] = 'Poly'
            width = random.uniform(kwargs['minWidth'], kwargs['maxWidth'])
            height = random.uniform(kwargs['minLength'], kwargs['maxLength'])

            nodes[n]['parameter'] = {
                'width': width,
                'height': height
            }

            nodes[n][neighborFieldName] = [
                [nodes[n][locFieldName][0] - width / 2, nodes[n][locFieldName][1] - height / 2], 
                [nodes[n][locFieldName][0] + width / 2, nodes[n][locFieldName][1] - height / 2], 
                [nodes[n][locFieldName][0] + width / 2, nodes[n][locFieldName][1] + height / 2], 
                [nodes[n][locFieldName][0] - width / 2, nodes[n][locFieldName][1] + height / 2]
            ]

    elif (shape == 'RndRectangleBounded'):
        for n in nodeIDs:
            if ('minWidth' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'minWidth'")
            if ('maxWidth' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'maxWidth'")
            if ('minLength' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'minLength'")
            if ('maxLength' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'maxLength'")
            if (kwargs['minWidth'] > kwargs['maxWidth']):
                warnings.warn("WARNING: 'minWidth' is greater than 'maxWidth', will be swapped")
                kwargs['maxWidth'], kwargs['minWidth'] = kwargs['minWidth'], kwargs['maxWidth']
            if (kwargs['minLength'] > kwargs['maxLength']):
                warnings.warn("WARNING: 'minLength' is greater than 'maxLength', will be swapped")
                kwargs['maxLength'], kwargs['minLength'] = kwargs['minLength'], kwargs['maxLength']
            # 在矩形的边缘上和内部随机取点
            if ('numIntePt' not in kwargs):
                kwargs['numIntePt'] = 10
            if ('numEdgePt' not in kwargs):
                kwargs['numEdgePt'] = 5

            nodes[n]['neiShape'] = 'Poly'
            width = random.uniform(kwargs['minWidth'], kwargs['maxWidth'])
            height = random.uniform(kwargs['minLength'], kwargs['maxLength'])
            
            nodes[n]['parameter'] = {
                'width': width,
                'height': height
            }

            # 先生成bounding的矩形
            bounding = [
                [-width / 2, -height / 2], 
                [+width / 2, -height / 2], 
                [+width / 2, +height / 2], 
                [-width / 2, +height / 2]
            ]

            polyPts = []
            # Interior
            for i in range(kwargs['numIntePt']):
                polyPts.append(_rndPtUniformPolyXY(bounding))
            # Edge
            edge = [
                [-width / 2, -height / 2], 
                [+width / 2, -height / 2], 
                [+width / 2, +height / 2], 
                [-width / 2, +height / 2],
                [-width / 2, -height / 2]
            ]
            totalMileage = 2 * width + 2 * height
            for i in range(kwargs['numEdgePt']):
                polyPts.append(ptInSeqMileage(edge, random.random() * totalMileage))

            # 取Convex hull
            polyShapely = shapely.convex_hull(shapely.MultiPoint(points = polyPts))
            polyB4Rot = [i for i in mapping(polyShapely)['coordinates'][0]]

            direction = random.random() * 180
            u = math.cos(math.radians(direction))
            v = math.sin(math.radians(direction))
            poly = [(nodes[n][locFieldName][0] + u * pt[0] + v * pt[1], nodes[n][locFieldName][1] + -v * pt[0] + u * pt[1]) for pt in polyB4Rot]
            nodes[n][neighborFieldName] = [poly[i] for i in range(len(poly)) if distEuclideanXY(poly[i], poly[i - 1]) > ERRTOL['distPt2Pt']]

    elif (shape == 'RndCurvy'):
        for n in nodeIDs:
            if ('maxRadius' not in kwargs or 'minRadius' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'maxRadius' or 'minRadius'")
            lod = 30
            if ('lod' in kwargs and type(kwargs['lod']) == int):
                lod = kwargs['lod']

            r = []
            for i in range(lod + 1):
                r.append(kwargs['minRadius'])
            N = 4
            if ('N' in kwargs and type(kwargs['N']) == int):
                N = kwargs['N']
            w = 3
            if ('w' in kwargs and type(kwargs['w']) == int):
                w = kwargs['w']

            for k in range(N):
                a = random.uniform(0, 1)
                b = random.randint(1, w)
                c = random.uniform(0, 2)
                for i in range(lod + 1):
                    r[i] += a * math.sin(b * 2 * i * math.pi / lod + math.pi * c)

            nodes[n]['neiShape'] = 'Poly'

            nodes[n]['parameter'] = {
                'N': N,
                'w': w
            }

            maxRI = max(r)
            for i in range(len(r)):
                r[i] = r[i] * (kwargs['maxRadius'] - kwargs['minRadius']) / maxRI

            poly = [[
                nodes[n][locFieldName][0] + (r[d] + kwargs['minRadius']) * math.sin(2 * d * math.pi / lod),
                nodes[n][locFieldName][1] + (r[d] + kwargs['minRadius']) * math.cos(2 * d * math.pi / lod),
            ] for d in range(lod + 1)]
            nodes[n][neighborFieldName] = [poly[i] for i in range(len(poly)) if distEuclideanXY(poly[i], poly[i - 1]) > ERRTOL['distPt2Pt']]
    
    elif (shape == 'RndConvexPoly'):
        for n in nodeIDs:
            if ('maxNumSide' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'maxNumSide'")
            if ('maxDiag' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'maxDiag'")
            if ('minDiag' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'minDiag'")
            
            nodes[n]['neiShape'] = 'Poly'
            polyPts = []
            for i in range(kwargs['maxNumSide']):
                deg = random.uniform(0, 1) * 360
                r = kwargs['minDiag'] / 2 + random.uniform(0, 1) * (kwargs['maxDiag'] - kwargs['minDiag']) / 2
                polyPts.append(ptInDistXY(
                    pt = nodes[n][locFieldName], direction = deg, dist = r))

            nodes[n]['parameter'] = {
                'numSide': kwargs['maxNumSide'],
                'minDiag': kwargs['minDiag'],
                'maxDiag': kwargs['maxDiag']
            }

            polyShapely = shapely.convex_hull(shapely.MultiPoint(points = polyPts))
            poly = [i for i in mapping(polyShapely)['coordinates'][0]]
            nodes[n][neighborFieldName] = [poly[i] for i in range(len(poly)) if distEuclideanXY(poly[i], poly[i - 1]) > ERRTOL['distPt2Pt']]

    elif (shape == 'RndStar'):
        for n in nodeIDs:
            if ('maxNumSide' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'maxNumSide'")
            if ('maxDiag' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'maxDiag'")
            if ('minDiag' not in kwargs):
                raise MissingParameterError("ERROR: Missing required args 'minDiag'")

            nodes[n]['neiShape'] = 'Poly'
            degs = []
            for i in range(kwargs['maxNumSide']):
                degs.append(random.uniform(0, 1) * 360)
            degs.sort()

            nodes[n]['parameter'] = {
                'numSide': kwargs['maxNumSide'],
                'minDiag': kwargs['minDiag'],
                'maxDiag': kwargs['maxDiag']
            }

            polyPts = []
            for i in range(kwargs['maxNumSide']):
                r = kwargs['minDiag'] / 2 + random.uniform(0, 1) * (kwargs['maxDiag'] - kwargs['minDiag']) / 2
                polyPts.append(ptInDistXY(
                    pt = nodes[n][locFieldName], direction = degs[i], dist = r))
            nodes[n][neighborFieldName] = [polyPts[i] for i in range(len(polyPts)) if distEuclideanXY(polyPts[i], polyPts[i - 1]) > ERRTOL['distPt2Pt']]

    else:
        raise UnsupportedInputError("ERROR: Unsupported option for `kwargs`. Supported 'shape' includes: 'Poly', 'Circle', 'Egg', 'RndSquare', 'RndConvexPoly' and 'RndCurvy'.")

    return nodes

def rndNodeIsoNeighbors(
    nodes: dict,
    nodeIDs: list[int|str]|str = 'All', 
    **kwargs
    ) -> dict:

    # Field names =============================================================
    locFieldName = 'loc' if 'locFieldName' not in kwargs else kwargs['locFieldName']
    neighborFieldName = 'neighbor' if 'neighborFieldName' not in kwargs else kwargs['neighborFieldName']

    # Sanity check ============================================================
    if (type(nodeIDs) is not list):
        if (nodeIDs == 'All'):
            nodeIDs = [i for i in nodes]
        else:
            for i in nodeIDs:
                if (i not in nodes):
                    raise OutOfRangeError("ERROR: Node %s is not in `nodes`." % i)

    for n in nodeIDs:
        # By default, a circle is plotted by a 30-gon
        lod = 30
        if ('lod' in kwargs and type(kwargs['lod']) == int):
            lod = kwargs['lod']

        nodes[n][neighborFieldName] = []
        nodes[n]['neiShape'] = 'Isochrone'
        nodes[n]['radiusList'] = kwargs['radiusList']
        for r in kwargs['radiusList']:
            poly = [[
                nodes[n][locFieldName][0] + r * math.sin(2 * d * math.pi / lod),
                nodes[n][locFieldName][1] + r * math.cos(2 * d * math.pi / lod),
            ] for d in range(lod + 1)]
            nodes[n][neighborFieldName].append([poly[i] for i in range(len(poly)) if distEuclideanXY(poly[i], poly[i - 1]) > ERRTOL['distPt2Pt']])

    return nodes

def rndNodeTimedNeighbors(
    nodes: dict,
    nodeIDs: list[int|str]|str = 'All', 
    shape: str = 'Egg',
    **kwargs
    ) -> dict:

    # Sanity check ============================================================
    if (type(nodeIDs) is not list):
        if (nodeIDs == 'All'):
            nodeIDs = [i for i in nodes]
        else:
            for i in nodeIDs:
                if (i not in nodes):
                    raise OutOfRangeError("ERROR: Node %s is not in `nodes`." % i)

    # Field names =============================================================
    locFieldName = 'loc' if 'locFieldName' not in kwargs else kwargs['locFieldName']
    neighborFieldName = 'neighbor' if 'neighborFieldName' not in kwargs else kwargs['neighborFieldName']

    if (shape == 'Egg'):
        for n in nodeIDs:
            if ('T' not in kwargs):
                raise MissingParameterError("ERROR: Missing required arg 'T'.")
            T = kwargs['T']
            if ('dirT' not in kwargs):
                raise MissingParameterError("ERROR: Missing required arg 'dirT'.")
            dirT = kwargs['dirT']

            aT = None
            bT = None
            cT = None
            if ('aT' not in kwargs or 'bT' not in kwargs or 'cT' not in kwargs):
                if ('a' in kwargs and 'b' in kwargs and 'c' in kwargs):
                    aT = [kwargs['a'] for k in range(len(T))]
                    bT = [kwargs['b'] for k in range(len(T))]
                    cT = [kwargs['c'] for k in range(len(T))]
                else:
                    raise MissingParameterError("ERROR: Missing required args 'a', 'b', and/or 'c'.")
            else:        
                # 先给出不同时刻的各个参数
                aT = kwargs['aT']
                bT = kwargs['bT']
                cT = kwargs['cT']

            lod = 30
            if ('lod' in kwargs and type(kwargs['lod']) == int):
                lod = kwargs['lod']

            timedPoly = []

            for k in range(len(T)):
                # Formulation:
                # \frac{x^2}{(a - b)x + ab} + \frac{y^2}{c^2} = 1
                direction = dirT[k]
                a = aT[k]
                b = bT[k]
                c = cT[k]
                
                vHLod = math.ceil(lod * 2 / 9)
                vTLod = math.ceil(lod / 3)
                hLod = math.ceil(lod * 2 / 3)

                polyL = []
                polyM = []
                polyR = []
                for d in range(vHLod + 1):
                    y = c * 0.75 * d / vHLod
                    A = 1
                    B = (y ** 2 / c ** 2 - 1) * (a - b)
                    C = (y ** 2 / c ** 2 - 1) * a * b
                    X = (-B - math.sqrt(B ** 2 - 4 * A * C)) / (2 * A)
                    polyL.append((X, y))
                    xStart = X
                for d in range(vTLod + 1):
                    y = c * 0.4 * d / vHLod
                    A = 1
                    B = (y ** 2 / c ** 2 - 1) * (a - b)
                    C = (y ** 2 / c ** 2 - 1) * a * b
                    X = (-B + math.sqrt(B ** 2 - 4 * A * C)) / (2 * A)
                    polyR.insert(0, (X, y))
                    xEnd = X
                for d in range(hLod + 1):
                    x = xStart + (xEnd - xStart) * d / hLod
                    Y = math.sqrt(c * c * (1 - (x * x) / ((a - b) * x + a * b)))
                    polyM.append((x, Y))
                polyHf = []
                polyHf.extend(polyL)
                polyHf.extend(polyM)
                polyHf.extend(polyR)

                polyB4Rot = [i for i in polyHf]
                polyB4Rot.extend([(polyHf[len(polyHf) - 1 - k][0], - polyHf[len(polyHf) - 1 - k][1]) for k in range(len(polyHf))])
                
                u = math.cos(math.radians(direction))
                v = math.sin(math.radians(direction))
                poly = [(nodes[n][locFieldName][0] + u * pt[0] + v * pt[1], nodes[n][locFieldName][1] + -v * pt[0] + u * pt[1]) for pt in polyB4Rot]
                timedPoly.append([[poly[i] for i in range(len(poly)) if not is2PtsSame(poly[i], poly[i - 1])], T[k]])

            nodes[n][neighborFieldName] = TriGridSurface(timedPoly)

    elif (shape == 'Circle'):
        pass

    else:
        raise UnsupportedInputError("ERROR: Unsupported option for `shape`.")

    return nodes

def rndNodeRingNeighbors(
    nodes: dict,
    innerRadius: float,
    outerRadius: float,
    barriers: polys = [],
    nodeIDs: list[int|str]|str = 'All',
    **kwargs
    ) -> dict:
    # Field names =============================================================
    if (innerRadius >= outerRadius):
        raise UnsupportedInputError("ERROR: innerRadius should be smaller than outerRadius.")

    locFieldName = 'loc' if 'locFieldName' not in kwargs else kwargs['locFieldName']
    neighborFieldName = 'neighbor' if 'neighborFieldName' not in kwargs else kwargs['neighborFieldName']
    lod = 30 if 'lod' not in kwargs else kwargs['lod']

    # Sanity check ============================================================
    if (type(nodeIDs) is not list):
        if (nodeIDs == 'All'):
            nodeIDs = [i for i in nodes]
        else:
            for i in nodeIDs:
                if (i not in nodes):
                    raise OutOfRangeError("ERROR: Node %s is not in `nodes`." % i)

    # Create ring =============================================================
    for n in nodes:
        nodes[n]['neiShape'] = 'Ring'
        nodes[n]['innerRadius'] = innerRadius
        nodes[n]['outerRadius'] = outerRadius
   
    # Create all no-fly =======================================================
    nofly = []
    for p in barriers:
        nofly.append(shapely.Polygon(p))
    for n in nodes:
        inner = [[
            nodes[n][locFieldName][0] + (innerRadius - ERRTOL['distPt2Poly'] * 10) * math.sin(2 * d * math.pi / lod),
            nodes[n][locFieldName][1] + (innerRadius - ERRTOL['distPt2Poly'] * 10) * math.cos(2 * d * math.pi / lod),
        ] for d in range(lod + 1)]
        nofly.append(shapely.Polygon(inner))
    allNoFly = shapely.union_all(nofly)

    # Create neighborhoods ====================================================
    for n in nodes:
        # nodes[n]['neiShell'] => list[poly]
        nodes[n]['neiShell'] = []
        # nodes[n]['neiHoles'] => list[poly]
        nodes[n]['neiHoles'] = None

        # Ring, before cutting nofly
        outerCircle = [[
            nodes[n][locFieldName][0] + outerRadius * math.sin(2 * d * math.pi / lod),
            nodes[n][locFieldName][1] + outerRadius * math.cos(2 * d * math.pi / lod),
        ] for d in range(lod + 1)]
        innerCircle = [[
            nodes[n][locFieldName][0] + innerRadius * math.sin(2 * d * math.pi / lod),
            nodes[n][locFieldName][1] + innerRadius * math.cos(2 * d * math.pi / lod),
        ] for d in range(lod + 1)]
        ring = shapely.Polygon(
            shell = outerCircle,
            holes = [innerCircle])

        nei = shapely.difference(ring, allNoFly)
        if (type(nei) == shapely.Polygon):
            shl = [i for i in nei.exterior.coords]
            shl = [shl[i] for i in range(len(shl)) if distEuclideanXY(shl[i], shl[i - 1]) > ERRTOL['distPt2Pt']]
            nodes[n]['neiShell'] = [shl]
            if (len(nei.interiors) > 0):
                nodes[n]['neiHoles'] = []
                for p in nei.interiors:
                    itr = [i for i in p.coords]
                    itr = [itr[i] for i in range(len(itr)) if distEuclideanXY(itr[i], itr[i - 1]) > ERRTOL['distPt2Pt']]
                    nodes[n]['neiHoles'].append(itr)
        elif (type(nei) == shapely.MultiPolygon):
            for g in nei.geoms:
                if (type(g) == shapely.Polygon):
                    shl = [i for i in g.exterior.coords]
                    shl = [shl[i] for i in range(len(shl)) if distEuclideanXY(shl[i], shl[i - 1]) > ERRTOL['distPt2Pt']]
                    nodes[n]['neiShell'].append(shl)

    # Check if all neighborhoods are accessible ===============================
    noFlyShell = []
    if (type(allNoFly) == shapely.Polygon):
        shl = [i for i in allNoFly.exterior.coords]
        shl = [shl[i] for i in range(len(shl)) if distEuclideanXY(shl[i], shl[i - 1]) > ERRTOL['distPt2Pt']]
        noFlyShell = [shl]
    elif (type(allNoFly) == shapely.MultiPolygon):
        for g in allNoFly.geoms:
            shl = [i for i in g.exterior.coords]
            shl = [shl[i] for i in range(len(shl)) if distEuclideanXY(shl[i], shl[i - 1]) > ERRTOL['distPt2Pt']]
            if (type(g) == shapely.Polygon):
                noFlyShell.append(shl)

    # Find a point that is ``outside'' the area ===============================
    corner = []
    allX = []
    allY = []
    for n in nodes:
        allX.append(nodes[n][locFieldName][0])
        allY.append(nodes[n][locFieldName][1])
    corner = [min(allX) - outerRadius, min(allY) - outerRadius]

    # Check accessibility =====================================================
    polyVG = polysVisibleGraph(noFlyShell)
    for n in nodes:
        reachable = False
        for k in range(len(nodes[n]['neiShell'])):
            try:
                d = distBtwPolysXY(corner, nodes[n]['neiShell'][k][0], noFlyShell, polyVG = polyVG)
                if (d != None):
                    reachable = True
                    break
            except:
                pass

        if (reachable == False):
            print("ERROR: Include inaccessible region.")
            return None

    return nodes

def rndArcs(
    A: int|None = None,
    arcIDs: list[int|str] = [],
    distr = 'UniformLengthInSquareXY',
    **kwargs
    ) -> dict:

    """Randomly create a set of arcs 

    Parameters
    ----------

    A: integer, optional, default as None
        Number of arcs to be visited
    arcIDs: list, optional, default as None
        Alternative input parameter of `A`. A list of arc IDs, `A` will be overwritten if `arcIDs` is given
    distr: str, optional, default as 'UniformLengthInSquareXY'
        The distribution of arcs. Options and required additional inputs are as follows:

        1) (default) 'UniformLengthInSquareXY', uniformly sample from a square on the Euclidean space, with uniformly selected length
            - xRange: 2-tuple, with minimum/maximum range of x, default as (0, 100)
            - yRange: 2-tuple, with minimum/maximum range of y, default as (0, 100)
            - minLen: float, minimum length of the arcs
            - maxLen: float, maximum length of the arcs
    **kwargs: optional
        Provide additional inputs for different `distr` options

    Returns
    -------
    dict
        A dictionary of randomly created arcs.

    """

    # Sanity check ============================================================
    arcs = {}
    if (arcIDs == [] and A == None):
        raise MissingParameterError(ERROR_MISSING_N)
    elif (arcIDs == [] and A != None):
        arcIDs = [i for i in range(A)]

    # Field names =============================================================
    arcFieldName = 'arc' if 'arcFieldName' not in kwargs else kwargs['arcFieldName']

    # Generate instance =======================================================
    if (distr == 'UniformLengthInSquareXY'):
        if ('minLen' not in kwargs or 'maxLen' not in kwargs):
            raise MissingParameterError("ERROR: Missing required field 'minLen' and/or 'maxLen'")
        if ('minDeg' not in kwargs):
            kwargs['minDeg'] = 0
        if ('maxDeg' not in kwargs):
            kwargs['maxDeg'] = 360
        xRange = None
        yRange = None
        if ('xRange' not in kwargs or 'yRange' not in kwargs):
            xRange = [0, 100]
            yRange = [0, 100]
            warnings.warn("WARNING: Set sample area to be default as a (0, 100) x (0, 100) square")
        else:
            xRange = [float(kwargs['xRange'][0]), float(kwargs['xRange'][1])]
            yRange = [float(kwargs['yRange'][0]), float(kwargs['yRange'][1])]
        for n in arcIDs:
            arcs[n] = {
                arcFieldName : _rndArcUniformSquareXY(xRange, yRange, kwargs['minLen'], kwargs['maxLen'], kwargs['minDeg'], kwargs['maxDeg'])
            }
    else:
        raise UnsupportedInputError(ERROR_MISSING_ARCS_DISTR)

    return arcs

def rndArcNeighbors(
    arcs: dict,
    arcIDs: list[int|str]|str = 'All',
    shape: str = 'FixedRadius',
    **kwargs
    ) -> dict:

    """Given an arc dictionary, add neighborhood to selected arcs

    WARNING
    -------

    This function will modify the input dictionary `arcs`

    Parameters
    ----------

    arcs: dictionary, required
        A plain arcs dictionary to add neighborhoods.
    arcIDs: string|list[int|str], optional, default 'All'
        A list of arc IDs to add neighborhood, leave it as 'All' to indicate adding such information to all arcs.
    method: dictionary, optional, default {'shape': 'FixedRadius', 'radius': 1, 'lod': 30}       
        The shape of dictionary. Options includes
        1) Adding fixed radius neighborhoods to a given arc
            >>> method = {
            ...     'shape': 'FixedRadius',
            ...     'radius': 1,
            ...     'lod': 30
            ... }

    Returns
    -------

    dictionary
        Changes will apply to the original `nodes` dictionary

    """
    
    # Sanity check ============================================================
    if (type(arcIDs) is not list):
        if (arcIDs == 'All'):
            arcIDs = [i for i in arcs]
        else:
            for i in arcIDs:
                if (i not in arcs):
                    raise OutOfRangeError("ERROR: Node %s is not in `arcs`." % i)
    
    # Field names =============================================================
    arcFieldName = 'arc' if 'arcFieldName' not in kwargs else kwargs['arcFieldName']
    neiBtwFieldName = 'neiBtw' if 'neiBtwFieldName' not in kwargs else kwargs['neiBtwFieldName'] 
    neiAFieldName = 'neiA' if 'neiAFieldName' not in kwargs else kwargs['neiAFieldName']
    neiBFieldName = 'neiB' if 'neiBFieldName' not in kwargs else kwargs['neiBFieldName']
    neiAllFieldName = 'neiAll' if 'neiAllFieldName' not in kwargs else kwargs['neiAllFieldName']

    # Add neighborhood ========================================================
    for i in arcIDs:
        if (shape == 'FixedRadius'):
            if ('radius' not in kwargs):
                raise MissingParameterError("ERROR: Missing required key 'radius' in `kwargs`")
            
            # By default, a circle is plotted by a 30-gon
            lod = 30
            if ('lod' in kwargs and type(kwargs['lod']) == int):
                lod = kwargs['lod']
            startLoc = arcs[i][arcFieldName][0]
            endLoc = arcs[i][arcFieldName][1]

            heading = headingXY(startLoc, endLoc)

            radius = kwargs['radius']
            arcs[i][neiBtwFieldName] = [[
                startLoc[0] + radius * math.sin(2 * d * math.pi / lod + (heading - 90) * math.pi / 180),
                startLoc[1] + radius * math.cos(2 * d * math.pi / lod + (heading - 90) * math.pi / 180),
            ] for d in range(int(lod / 2 + 1))]
            arcs[i][neiBtwFieldName].extend([[
                endLoc[0] + radius * math.sin(2 * d * math.pi / lod + (heading + 90) * math.pi / 180),
                endLoc[1] + radius * math.cos(2 * d * math.pi / lod + (heading + 90) * math.pi / 180),
            ] for d in range(int(lod / 2 + 1))])

            arcs[i][neiAFieldName] = [[
                    startLoc[0] + radius * math.sin(2 * d * math.pi / lod + (heading + 90) * math.pi / 180),
                    startLoc[1] + radius * math.cos(2 * d * math.pi / lod + (heading + 90) * math.pi / 180),
                ] for d in range(int(lod))]
            arcs[i][neiBFieldName] = [[
                    endLoc[0] + radius * math.sin(2 * d * math.pi / lod + (heading - 90) * math.pi / 180),
                    endLoc[1] + radius * math.cos(2 * d * math.pi / lod + (heading - 90) * math.pi / 180),
                ] for d in range(int(lod))]

            arcs[i][neiAllFieldName] = [[
                startLoc[0] + radius * math.sin(2 * d * math.pi / lod + (heading + 90) * math.pi / 180),
                startLoc[1] + radius * math.cos(2 * d * math.pi / lod + (heading + 90) * math.pi / 180),
            ] for d in range(int(lod / 2 + 1))]
            arcs[i][neiAllFieldName].extend([[
                endLoc[0] + radius * math.sin(2 * d * math.pi / lod + (heading - 90) * math.pi / 180),
                endLoc[1] + radius * math.cos(2 * d * math.pi / lod + (heading - 90) * math.pi / 180),
            ] for d in range(int(lod / 2 + 1))])
        
        else:
            raise UnsupportedInputError("ERROR: Unsupported option for `shape`. Supported 'shape' includes: 'FixedRadius'.")
    return arcs

def _rndArcUniformSquareXY(xRange, yRange, minLen, maxLen, minDeg, maxDeg) -> tuple[pt, pt]:
    length = random.uniform(minLen, maxLen)
    direction = random.uniform(minDeg, maxDeg)
    xStart = random.uniform(xRange[0], xRange[1])
    yStart = random.uniform(yRange[0], yRange[1])
    (xEnd, yEnd) = ptInDistXY((xStart, yStart), direction, length)
    return ((xStart, yStart), (xEnd, yEnd))

def rndPolys(
    P: int|None = None,
    polyIDs: list[int|str]|None = None,
    distr = 'UniformSquareXY',
    shape = 'RndConvexPoly',    
    allowOverlapFlag = True,
    returnAsListFlag = True,
    **kwargs
    ) -> dict:

    """
    Randomly create polygons

    Parameters
    ----------

    P: int|str, optional, default as None
        Number of polygons to create
    polyIDs: list[int|str]|None, optional, default as None
        A list of ids for the polygons to be created, an alternative option for `P`
    distr: str, optional, default as 'UniformSquareXY'
        Anchor locations of each polygon. Options and required additional information are referred to :func:`~geoVeRoPy.instance.rndLocs()`.
    shape: str, optional, default as 'Circle',
        Shape of the polygons. Options and required additional information are referred to :func:`~geoVeRoPy.instance.rndNodeNeighbors()`.
    anchorFieldName: str, optional, default as 'anchor'
        The key value of the anchor location
    polyFieldName: str, optional, default as 'poly',
        The key value of the polygons
    allowOverlapFlag: bool, optional, default as True
        True if allows the polygons to overlap
    returnAsListFlag: bool, optional, default as True
        True if returns a list of polygons instead of a dictionary

    Returns
    -------
    dict
        A dictionary with polygon information
    """

    # Sanity check ============================================================
    if (polyIDs == None and P == None):
        raise MissingParameterError("ERROR: Missing required field `P` and `polyIDs`.")
    elif (polyIDs == None and P != None):
        polyIDs = [i for i in range(P)]

    if (shape == 'RndConvexPoly'):
        if ('maxNumSide' not in kwargs):
            kwargs['maxNumSide'] = 7
            warnings.warn("WARNING: Missing `maxNumSide`, set to be default as 7")
        if ('maxDiag' not in kwargs):
            kwargs['maxDiag'] = 12
            warnings.warn("WARNING: Missing `maxDiag`, set to be default as 12")
        if ('minDiag' not in kwargs):
            kwargs['minDiag'] = 7
            warnings.warn("WARNING: Missing `minDiag`, set to be default as 7")

    # Field names =============================================================
    anchorFieldName = 'anchor' if 'anchorFieldName' not in kwargs else kwargs['anchorFieldName']
    polyFieldName = 'poly' if 'polyFieldName' not in kwargs else kwargs['polyFieldName']

    # If overlapping is allowed ===============================================
    if (allowOverlapFlag):
        polygons = rndNodes(
            N = P,
            nodeIDs = polyIDs,
            distr = distr,
            locFieldName = anchorFieldName,
            **kwargs)

        # Next, create P polygons relative to anchor points ===================
        polygons = rndNodeNeighbors(
            nodes = polygons,
            shape = shape,
            locFieldName = anchorFieldName,
            neighborFieldName = polyFieldName,
            **kwargs)

        if (not returnAsListFlag):
            return polygons
        else:
            return [polygons[i][polyFieldName] for i in polygons]
    
    # If overlapping is not allowed ===========================================
    maxNumOfFailedTrial = 20
    anchor = []
    polys = []

    numOfFailedTrial = 0
    while (len(polys) < len(polyIDs)):
        addedFlag = True
        p = rndNodes(
            N = 1,
            distr = distr,
            locFieldName = anchorFieldName,
            **kwargs)
        p = rndNodeNeighbors(
            nodes = p,
            shape = shape,
            locFieldName = anchorFieldName,
            neighborFieldName = polyFieldName,
            **kwargs)
        newPoly = p[0][polyFieldName]
        for poly in polys:
            if (isPolyIntPoly(poly, newPoly) == True):
                numOfFailedTrial += 1
                addedFlag = False
                break

        if (addedFlag == True):
            polys.append(newPoly)
            anchor.append(p[0][anchorFieldName])
            numOfFailedTrial = 0
        else:
            if (numOfFailedTrial >= maxNumOfFailedTrial):
                break
    if (len(polys) < len(polyIDs)):
        warnings.warn("WARNING: Space is too limited, only %s of polygons are created." % len(polys))

    if (returnAsListFlag):        
        return polys
    else:
        polygons = {}
        for p in range(len(polys)):
            polygons[polyIDs[p]] = {
                anchorFieldName: anchor[p],
                polyFieldName: polys[p]
            }
        return polygons

