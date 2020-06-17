import sympy
import antlr4

from . import vector
from . import region
from . import reader
from .RegionExpression import RegionParserVisitor, RegionParser, RegionLexer
from . import fluka_registry

def expressionToZone(zone, zoneExpr):
    zoneExpr = str(zoneExpr)
    zoneExpr = zoneExpr.replace("& ~", "-")
    zoneExpr = zoneExpr.replace("& ", "+")

    # Hack to use the existing region parser...  fix this.
    expr = f"dummy 5 {zoneExpr}"

    istream = antlr4.InputStream(expr)
    lexed_input = RegionLexer(istream)
    tokens = antlr4.CommonTokenStream(lexed_input)
    parser = RegionParser(tokens)
    tree = parser.region()
    freg = fluka_registry.FlukaRegistry()
    zone.allBodiesToRegistry(freg)
    vis = reader.RegionVisitor(freg)
    vis.visit(tree)

    return freg.regionDict["dummy"].zones[0]


def zoneToDNFZones(zone):
    dnf = sympy.to_dnf(zoneToAlgebraicExpression(zone))

    zones = []
    for arg in dnf.args:
        arg = sympy.simplify_logic(arg) # trivially solve a & ~a, etc..
        if not arg:
            continue
        zones.append(expressionToZone(zone, arg))

    return zones

def regionToAlgebraicExpression(region): # region or zone
    result = []
    for z in region.zones:
        result.append(zoneToAlgebraicExpression(z))
    return sympy.Or(*result)

def zoneToAlgebraicExpression(zone):
    s = zone.dumps()
    s = s.strip()
    s = s.lstrip("+")
    s = s.replace("-", "& ~")
    s = s.replace("( +", "(")
    s = s.replace(" +", " & ")
    bodyNames = set(b.name for b in zone.bodies())
    namespace = {name: sympy.Symbol(name) for name in bodyNames}
    return sympy.sympify(s, locals=namespace)

def _getaabb(body, aabb=None):
    mesh = body.mesh(aabb=aabb)
    return vector.AABB.fromMesh(mesh)

def _getMeshAndAABB(body, aabb=None):
    mesh = body.mesh(aabb=aabb)
    return mesh, vector.AABB.fromMesh(mesh)


def pruneRegion(reg, aabb=None):
    result = region.Region(reg.name)
    for zone in reg.zones:
        prunedZone = pruneZone(zone)
        if prunedZone.intersections: # and not prunedZone.isNull(aabb=aabb):
            result.addZone(prunedZone)
    return result


def pruneZone(zone, aabb0=None, aabb=None):
    intersections = zone.intersections

    result = region.Zone()
    if aabb0 is None:
        first = intersections[0].body
        aabb0 = vector.AABB.fromMesh(first.mesh())
        intersections = intersections[1:]
        result.addIntersection(first)

    for intersect in intersections:
        contents = intersect.body
        if isinstance(contents, region.Zone):
            prunedSubZone = pruneZone(contents, aabb0=aabb0, aabb=aabb)
            result.addIntersection(prunedSubZone)
        else:
            thisAABB = _getaabb(contents, aabb=aabb)
            if thisAABB.intersects(aabb0):
                aabb0 = thisAABB.intersect(aabb0)
                result.addIntersection(contents)
            else:
                result.intersections = []
                return result

    for sub in zone.subtractions:
        contents = sub.body
        if isinstance(contents, region.Zone):
            prunedSubZone = pruneZone(contents, aabb0=aabb0, aabb=aabb)
            if not prunedSubZone.isNull():
                result.addSubtraction(prunedSubZone)
        else: # it's a body
            thisAABB = _getaabb(contents)
            if thisAABB.intersects(aabb0):
                result.addSubtraction(contents)

    return result

def squashDegenerateBodies(zone, bodystore=None):
    if bodystore is None:
        bodystore = fluka_registry.FlukaBodyStore()
    result = region.Zone()
    for b in zone.intersections:
        body = b.body
        if isinstance(body, region.Zone):
            result.addIntersection(
                squashDegenerateBodies(body, bodystore=bodystore)
            )
        else:
            result.addIntersection(bodystore.getDegenerateBody(body))

    for b in zone.subtractions:
        body = b.body
        if isinstance(body, region.Zone):
            result.addSubtraction(
                squashDegenerateBodies(body, bodystore=bodystore)
            )
        else:
            result.addSubtraction(bodystore.getDegenerateBody(body))

    return result
