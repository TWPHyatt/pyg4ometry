# Generated from Cell.g4 by ANTLR 4.13.2
from antlr4 import *
from io import StringIO
import sys
from typing import Optional
from typing import TextIO


def serializedATN():
    return [
        4,
        1,
        8,
        42,
        2,
        0,
        7,
        0,
        2,
        1,
        7,
        1,
        2,
        2,
        7,
        2,
        2,
        3,
        7,
        3,
        1,
        0,
        1,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        5,
        1,
        14,
        8,
        1,
        10,
        1,
        12,
        1,
        17,
        9,
        1,
        1,
        2,
        1,
        2,
        1,
        2,
        5,
        2,
        22,
        8,
        2,
        10,
        2,
        12,
        2,
        25,
        9,
        2,
        1,
        3,
        1,
        3,
        1,
        3,
        1,
        3,
        1,
        3,
        1,
        3,
        1,
        3,
        1,
        3,
        1,
        3,
        1,
        3,
        1,
        3,
        1,
        3,
        1,
        3,
        3,
        3,
        40,
        8,
        3,
        1,
        3,
        0,
        0,
        4,
        0,
        2,
        4,
        6,
        0,
        0,
        43,
        0,
        8,
        1,
        0,
        0,
        0,
        2,
        10,
        1,
        0,
        0,
        0,
        4,
        18,
        1,
        0,
        0,
        0,
        6,
        39,
        1,
        0,
        0,
        0,
        8,
        9,
        3,
        2,
        1,
        0,
        9,
        1,
        1,
        0,
        0,
        0,
        10,
        15,
        3,
        4,
        2,
        0,
        11,
        12,
        5,
        2,
        0,
        0,
        12,
        14,
        3,
        4,
        2,
        0,
        13,
        11,
        1,
        0,
        0,
        0,
        14,
        17,
        1,
        0,
        0,
        0,
        15,
        13,
        1,
        0,
        0,
        0,
        15,
        16,
        1,
        0,
        0,
        0,
        16,
        3,
        1,
        0,
        0,
        0,
        17,
        15,
        1,
        0,
        0,
        0,
        18,
        23,
        3,
        6,
        3,
        0,
        19,
        20,
        5,
        3,
        0,
        0,
        20,
        22,
        3,
        6,
        3,
        0,
        21,
        19,
        1,
        0,
        0,
        0,
        22,
        25,
        1,
        0,
        0,
        0,
        23,
        21,
        1,
        0,
        0,
        0,
        23,
        24,
        1,
        0,
        0,
        0,
        24,
        5,
        1,
        0,
        0,
        0,
        25,
        23,
        1,
        0,
        0,
        0,
        26,
        40,
        5,
        8,
        0,
        0,
        27,
        28,
        5,
        4,
        0,
        0,
        28,
        29,
        3,
        0,
        0,
        0,
        29,
        30,
        5,
        5,
        0,
        0,
        30,
        40,
        1,
        0,
        0,
        0,
        31,
        32,
        5,
        7,
        0,
        0,
        32,
        40,
        5,
        8,
        0,
        0,
        33,
        40,
        5,
        1,
        0,
        0,
        34,
        35,
        5,
        6,
        0,
        0,
        35,
        36,
        5,
        4,
        0,
        0,
        36,
        37,
        3,
        0,
        0,
        0,
        37,
        38,
        5,
        5,
        0,
        0,
        38,
        40,
        1,
        0,
        0,
        0,
        39,
        26,
        1,
        0,
        0,
        0,
        39,
        27,
        1,
        0,
        0,
        0,
        39,
        31,
        1,
        0,
        0,
        0,
        39,
        33,
        1,
        0,
        0,
        0,
        39,
        34,
        1,
        0,
        0,
        0,
        40,
        7,
        1,
        0,
        0,
        0,
        3,
        15,
        23,
        39,
    ]


class CellParser(Parser):

    grammarFileName = "Cell.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [DFA(ds, i) for i, ds in enumerate(atn.decisionToState)]

    sharedContextCache = PredictionContextCache()

    literalNames = ["<INVALID>", "<INVALID>", "':'", "' '", "'('", "')'", "'#'", "'-'"]

    symbolicNames = [
        "<INVALID>",
        "COMPLEMENT_CELLNUM",
        "UNION",
        "INTERSECTION",
        "LParen",
        "RParen",
        "COMPLEMENT",
        "SENSE",
        "SURFACENUM",
    ]

    RULE_expr = 0
    RULE_expressionUnion = 1
    RULE_expressionIntersection = 2
    RULE_expressionAtom = 3

    ruleNames = ["expr", "expressionUnion", "expressionIntersection", "expressionAtom"]

    EOF = Token.EOF
    COMPLEMENT_CELLNUM = 1
    UNION = 2
    INTERSECTION = 3
    LParen = 4
    RParen = 5
    COMPLEMENT = 6
    SENSE = 7
    SURFACENUM = 8

    def __init__(self, input: TokenStream, output: TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(
            self, self.atn, self.decisionsToDFA, self.sharedContextCache
        )
        self._predicates = None

    class ExprContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(self, parser, parent: ParserRuleContext = None, invokingState: int = -1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expressionUnion(self):
            return self.getTypedRuleContext(CellParser.ExpressionUnionContext, 0)

        def getRuleIndex(self):
            return CellParser.RULE_expr

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterExpr"):
                listener.enterExpr(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitExpr"):
                listener.exitExpr(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitExpr"):
                return visitor.visitExpr(self)
            else:
                return visitor.visitChildren(self)

    def expr(self):

        localctx = CellParser.ExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_expr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 8
            self.expressionUnion()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ExpressionUnionContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(self, parser, parent: ParserRuleContext = None, invokingState: int = -1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expressionIntersection(self, i: Optional[int] = None):
            if i is None:
                return self.getTypedRuleContexts(CellParser.ExpressionIntersectionContext)
            else:
                return self.getTypedRuleContext(CellParser.ExpressionIntersectionContext, i)

        def UNION(self, i: Optional[int] = None):
            if i is None:
                return self.getTokens(CellParser.UNION)
            else:
                return self.getToken(CellParser.UNION, i)

        def getRuleIndex(self):
            return CellParser.RULE_expressionUnion

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterExpressionUnion"):
                listener.enterExpressionUnion(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitExpressionUnion"):
                listener.exitExpressionUnion(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitExpressionUnion"):
                return visitor.visitExpressionUnion(self)
            else:
                return visitor.visitChildren(self)

    def expressionUnion(self):

        localctx = CellParser.ExpressionUnionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_expressionUnion)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 10
            self.expressionIntersection()
            self.state = 15
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la == 2:
                self.state = 11
                self.match(CellParser.UNION)
                self.state = 12
                self.expressionIntersection()
                self.state = 17
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ExpressionIntersectionContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(self, parser, parent: ParserRuleContext = None, invokingState: int = -1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expressionAtom(self, i: Optional[int] = None):
            if i is None:
                return self.getTypedRuleContexts(CellParser.ExpressionAtomContext)
            else:
                return self.getTypedRuleContext(CellParser.ExpressionAtomContext, i)

        def INTERSECTION(self, i: Optional[int] = None):
            if i is None:
                return self.getTokens(CellParser.INTERSECTION)
            else:
                return self.getToken(CellParser.INTERSECTION, i)

        def getRuleIndex(self):
            return CellParser.RULE_expressionIntersection

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterExpressionIntersection"):
                listener.enterExpressionIntersection(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitExpressionIntersection"):
                listener.exitExpressionIntersection(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitExpressionIntersection"):
                return visitor.visitExpressionIntersection(self)
            else:
                return visitor.visitChildren(self)

    def expressionIntersection(self):

        localctx = CellParser.ExpressionIntersectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_expressionIntersection)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 18
            self.expressionAtom()
            self.state = 23
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la == 3:
                self.state = 19
                self.match(CellParser.INTERSECTION)
                self.state = 20
                self.expressionAtom()
                self.state = 25
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ExpressionAtomContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(self, parser, parent: ParserRuleContext = None, invokingState: int = -1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SURFACENUM(self):
            return self.getToken(CellParser.SURFACENUM, 0)

        def LParen(self):
            return self.getToken(CellParser.LParen, 0)

        def expr(self):
            return self.getTypedRuleContext(CellParser.ExprContext, 0)

        def RParen(self):
            return self.getToken(CellParser.RParen, 0)

        def SENSE(self):
            return self.getToken(CellParser.SENSE, 0)

        def COMPLEMENT_CELLNUM(self):
            return self.getToken(CellParser.COMPLEMENT_CELLNUM, 0)

        def COMPLEMENT(self):
            return self.getToken(CellParser.COMPLEMENT, 0)

        def getRuleIndex(self):
            return CellParser.RULE_expressionAtom

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterExpressionAtom"):
                listener.enterExpressionAtom(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitExpressionAtom"):
                listener.exitExpressionAtom(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitExpressionAtom"):
                return visitor.visitExpressionAtom(self)
            else:
                return visitor.visitChildren(self)

    def expressionAtom(self):

        localctx = CellParser.ExpressionAtomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_expressionAtom)
        try:
            self.state = 39
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [8]:
                self.enterOuterAlt(localctx, 1)
                self.state = 26
                self.match(CellParser.SURFACENUM)
            elif token in [4]:
                self.enterOuterAlt(localctx, 2)
                self.state = 27
                self.match(CellParser.LParen)
                self.state = 28
                self.expr()
                self.state = 29
                self.match(CellParser.RParen)
            elif token in [7]:
                self.enterOuterAlt(localctx, 3)
                self.state = 31
                self.match(CellParser.SENSE)
                self.state = 32
                self.match(CellParser.SURFACENUM)
            elif token in [1]:
                self.enterOuterAlt(localctx, 4)
                self.state = 33
                self.match(CellParser.COMPLEMENT_CELLNUM)
            elif token in [6]:
                self.enterOuterAlt(localctx, 5)
                self.state = 34
                self.match(CellParser.COMPLEMENT)
                self.state = 35
                self.match(CellParser.LParen)
                self.state = 36
                self.expr()
                self.state = 37
                self.match(CellParser.RParen)
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx
