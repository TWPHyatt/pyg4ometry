# Generated from Cell.g4 by ANTLR 4.13.2
from antlr4 import *

if "." in __name__:
    from .CellParser import CellParser
else:
    from CellParser import CellParser


# This class defines a complete listener for a parse tree produced by CellParser.
class CellListener(ParseTreeListener):

    # Enter a parse tree produced by CellParser#expr.
    def enterExpr(self, ctx: CellParser.ExprContext):
        pass

    # Exit a parse tree produced by CellParser#expr.
    def exitExpr(self, ctx: CellParser.ExprContext):
        pass

    # Enter a parse tree produced by CellParser#expressionUnion.
    def enterExpressionUnion(self, ctx: CellParser.ExpressionUnionContext):
        pass

    # Exit a parse tree produced by CellParser#expressionUnion.
    def exitExpressionUnion(self, ctx: CellParser.ExpressionUnionContext):
        pass

    # Enter a parse tree produced by CellParser#expressionIntersection.
    def enterExpressionIntersection(self, ctx: CellParser.ExpressionIntersectionContext):
        pass

    # Exit a parse tree produced by CellParser#expressionIntersection.
    def exitExpressionIntersection(self, ctx: CellParser.ExpressionIntersectionContext):
        pass

    # Enter a parse tree produced by CellParser#expressionAtom.
    def enterExpressionAtom(self, ctx: CellParser.ExpressionAtomContext):
        pass

    # Exit a parse tree produced by CellParser#expressionAtom.
    def exitExpressionAtom(self, ctx: CellParser.ExpressionAtomContext):
        pass


del CellParser
