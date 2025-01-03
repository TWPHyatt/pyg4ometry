from . import CellVisitor
from ..Cell import *


class CellEvalVisitor(CellVisitor):
    def __init__(self, reg):
        self.registry = reg

    def visitExpr(self, ctx):
        return self.visit(ctx.expressionUnion())

    def visitExpressionUnion(self, ctx):
        left = self.visit(ctx.expressionIntersection(0))
        for i in range(len(ctx.expressionIntersection()) - 1):
            right = self.visit(ctx.expressionIntersection(i + 1))
            if ctx.UNION(i):
                print(" > UNION")
                left = Union(left, right)
        return left

    def visitExpressionIntersection(self, ctx):
        left = self.visit(ctx.expressionAtom(0))
        for i in range(len(ctx.expressionAtom()) - 1):
            right = self.visit(ctx.expressionAtom(i + 1))
            if ctx.INTERSECTION(i):
                print(" > INTERSECTION ")
                left = Intersection(left, right)
        return left

    def visitExpressionAtom(self, ctx):
        if ctx.SENSE():
            atom = self.registry.surfaceDict[int(ctx.SURFACENUM().getText())]
            atom = Complement(atom)
            print(" > COMPLEMENT")
            print(" >> SURFACE ", ctx.SURFACENUM().getText(), atom)
            return atom
        elif ctx.COMPLEMENT_CELLNUM():
            atom = self.registry.surfaceDict[int(ctx.COMPLEMENT_CELLNUM().getText()[1:])]
            atom = Complement(atom)
            print(" > COMPLEMENT")
            print(" >> CELL ", ctx.COMPLEMENT_CELLNUM().getText()[1:], atom)
            return atom
        elif ctx.COMPLEMENT():
            atom = self.visit(ctx.expr())
            atom = Complement(atom)
            print(" > COMPLEMENT")
            return atom
        elif ctx.SURFACENUM():  # integer
            atom = self.registry.surfaceDict[int(ctx.SURFACENUM().getText())]
            print(" >> SURFACE ", ctx.SURFACENUM().getText(), atom)
            return atom
        elif ctx.expr():  # parentheses
            atom = self.visit(ctx.expr())
            return atom
        else:
            msg = "Invalid atom"
            raise SystemExit(msg)
