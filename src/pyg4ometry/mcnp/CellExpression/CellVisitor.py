# Generated from Cell.g4 by ANTLR 4.13.2
from antlr4 import *

if "." in __name__:
    from .CellParser import CellParser
else:
    from CellParser import CellParser

# This class defines a complete generic visitor for a parse tree produced by CellParser.


class CellVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CellParser#expr.
    def visitExpr(self, ctx: CellParser.ExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CellParser#expressionUnion.
    def visitExpressionUnion(self, ctx: CellParser.ExpressionUnionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CellParser#expressionIntersection.
    def visitExpressionIntersection(self, ctx: CellParser.ExpressionIntersectionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by CellParser#expressionAtom.
    def visitExpressionAtom(self, ctx: CellParser.ExpressionAtomContext):
        return self.visitChildren(ctx)


del CellParser
