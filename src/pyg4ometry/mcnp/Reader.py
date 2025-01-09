from antlr4 import *

from .CellExpression import (
    CellParser,
    CellLexer,
    CellEvalVisitor,
)

from .CellExpression.CellEvalVisitor import CellEvalVisitor
from .Registry import Registry
from . import Surfaces
from . import Cell


class Reader:
    """
    Class to read a MCNP file.
    """

    def __init__(self, filename, reg=None):
        self.filename = filename
        if reg:
            self.registry = reg
        else:
            self.registry = Registry()
        self._load()

    def getRegistry(self):
        """Get the MCNP registry"""
        return self.registry

    def _load(self):
        """Load the MCNP input file"""
        self.cardStack = []
        self._processFile(self.filename)

        if len(self.cardStack) != 3:
            msg = "There was a problem reading the input file with an unrecognised number of input cards"
            raise RuntimeError(msg)

        # deal with surface card
        for s in self.cardStack[1]:
            print("--------------")
            parts = s.split()
            surfaceNum = int(parts[0])
            TRn = None

            # if the second element is numeric then it is the transformation number
            # and handle negative
            if len(parts) > 1 and parts[1].lstrip("-").isnumeric():
                TRn = parts[1]
                mnemonicIndex = 2
            else:
                mnemonicIndex = 1

            surfaceMnemonic = parts[mnemonicIndex].upper().replace("/", "_")
            if surfaceMnemonic == "RHP" or surfaceMnemonic == "HEX":
                surfaceMnemonic = "RHP_HEX"

            surfaceDef = [float(value) for value in parts[mnemonicIndex + 1 :]]

            print(f" S = |{surfaceNum}| |{TRn}| |{surfaceMnemonic}| |{surfaceDef}|")

            # todo add TR to reg, or bake-in then pass to _makeSurface?
            # make the surface and with the reg kwarg will auto add to registry
            s = self._makeSurface(
                surfaceMnemonic, *surfaceDef, reg=self.registry, surfaceNumber=int(surfaceNum)
            )

        # deal with cell card
        # todo input can be "cellNum1 LIKE cellNum2 BUT list"
        cellParams = []  # List to store dictionaries for each cell line
        for s in self.cardStack[0]:
            print("--------------")
            parts = s.split()
            partsUpper = [part.upper() for part in parts]
            cellDict = {}
            toRemove = []

            paramKeywords = [
                "IMP",
                "VOL",
                "PWT",
                "EXT",
                "FCL",
                "WWN",
                "DXC",
                "NONU",
                "PD",
                "TMP",
                "U",
                "TRCL",
                "LAT",
                "FILL",
                "ELPT",
                "COSY",
                "BFLCL",
                "UNC",
            ]

            # Extract keyword-value pairs
            for part in partsUpper:
                for keyword in paramKeywords:
                    if keyword in part:  # Check if the keyword exists in the part
                        if "=" in part:  # Split the string on an '='
                            key, value = part.split("=", 1)
                            try:
                                value = float(value)
                            except ValueError:
                                pass
                            cellDict[key] = value
                            toRemove.append(part)  # Mark for removal from string
            cellParams.append(cellDict)

            # Remove processed parts
            remainingParts = [part for part in partsUpper if part not in toRemove]

            cellNum = int(remainingParts[0])
            materialNum = int(remainingParts[1])
            density = None

            if materialNum != 0:
                density = float(remainingParts[2])
                defIndex = 2
            else:  # zero material is void
                defIndex = 1

            geometryStr = " ".join(remainingParts[defIndex + 1 :])

            geometryStr = self._adjustWhitespace(geometryStr)

            geometryObj = self._makeGeometry(geometryStr)

            print(f" C = |{cellNum}| |{materialNum}| |{density}| |{geometryStr}| |{cellDict}|")

            # todo if TRCL following line add to reg or bake-in, then pass to _makeSurface?

            surfaceList = []
            IMP = []
            for key, value in cellDict.items():
                if key.startswith("IMP"):  # Check if the key starts with "IMP"
                    IMP.append(value)  # Append the value to the list
                    print(f" {key} = {value}")

            # make the cell and with the reg kwarg will auto add to registry
            c = self._makeCell(
                geometry=geometryObj,
                surfaces=surfaceList,
                reg=self.registry,
                cellNumber=int(cellNum),
                materialNumber=int(materialNum),
                density=density,
                importance=IMP,
            )

        # todo there is a dictionary of the cell keywords parameters and values (add to reg?)
        print("--------------")
        for x in cellParams:
            print(x)

        # deal with data card
        for dataline in self.cardStack[2]:
            print("--------------")
            print(f" D = |{dataline}|")
            # todo

    def _processFile(self, filein):
        """process the input file lines into cardStack"""
        with open(filein) as f:
            lines = f.readlines()

        lineStack = list(reversed(lines))  # a stack of lines
        tempStack = []

        while lineStack:
            line = lineStack.pop()
            line = line.split("$")[0]  # "$" in line comments
            line = line.strip()  # Leading and trailing whitespace

            if line.startswith("c"):  # "c" comment lines
                continue

            if not line.split():  # line of whitespace
                self.cardStack.append(tempStack)
                tempStack = []  # on whitespace line, start stacking new card (cell, surface, data)
            else:
                tempStack.append(line)

        self.cardStack.append(tempStack)

        if self.cardStack[0][0].startswith("MESSAGE:"):
            self.cardStack.pop(0)  # remove message block

        self.cardStack[0].pop(0)  # remove title

        return

    def _makeSurface(self, surfaceName, *args, **kwargs):
        s = getattr(Surfaces, surfaceName, None)
        if s is None:
            msg = "Surface class " + surfaceName + " is not found in Surfaces module."
            raise ValueError(msg)
        return s(*args, **kwargs)

    def _makeCell(self, *args, **kwargs):
        c = Cell
        if c is None:
            msg = "Cell class is not found in Cell module."
            raise ValueError(msg)
        return c(*args, **kwargs)

    def _adjustWhitespace(self, geometryStr):
        # if an open parenthesis does not have a space before it, insert it (unless it is a hash)
        # if an open parenthesis has a space after it, remove it
        # if a close parenthesis does not have a space after it, insert it
        # if a close parenthesis has a space before it, remove it
        # if a colon (union) has a space before it, remove it
        # if a colon (union) has a space after it, remove it

        # print(f" > IN = |{geometryStr}|")

        if "(" in geometryStr:
            index = geometryStr.find("(")
            if index > 0 and geometryStr[index - 1] != " " and geometryStr[index - 1] != "#":
                # print(" > 1")
                geometryStr = (
                    geometryStr[:index] + " " + geometryStr[index:]
                )  # no space before, so add it
                # print(f" > ... |{geometryStr}|")
        if "(" in geometryStr:
            index = geometryStr.find("(")
            if len(geometryStr) > index + 1 and geometryStr[index + 1] == " ":
                # print(" > 2")
                geometryStr = (
                    geometryStr[: index + 1] + geometryStr[index + 2 :]
                )  # space found after, so remove it
                # print(f" > ... |{geometryStr}|")

        if ")" in geometryStr:
            index = geometryStr.find(")")
            if index > 0 and geometryStr[index - 1] == " ":
                # print(" > 3")
                geometryStr = (
                    geometryStr[: index - 1] + geometryStr[index:]
                )  # space found before, so remove it
                # print(f" > ... |{geometryStr}|")
        if ")" in geometryStr:
            index = geometryStr.find(")")
            if len(geometryStr) > index + 1 and geometryStr[index + 1] != " ":
                # print(" > 4")
                geometryStr = (
                    geometryStr[: index + 1] + " " + geometryStr[index + 1 :]
                )  # no space after, so add it
                # print(f" > ... |{geometryStr}|")

        if ":" in geometryStr:
            index = geometryStr.find(":")
            if index > 0 and geometryStr[index - 1] == " ":
                # print(" > 5")
                geometryStr = (
                    geometryStr[: index - 1] + geometryStr[index:]
                )  # space before, so remove it
                # print(f" > ... |{geometryStr}|")
        if ":" in geometryStr:
            index = geometryStr.find(":")
            if len(geometryStr) > index + 1 and geometryStr[index + 1] == " ":
                # print(" > 6")
                geometryStr = (
                    geometryStr[: index + 1] + geometryStr[index + 2 :]
                )  # space after, so remove it
                # print(f" > ... |{geometryStr}|")

        # print(f" > OUT = |{geometryStr}|")

        return geometryStr

    def _makeGeometry(self, expression):

        print("EXPRESSION", expression)

        # read the input expression
        inputStream = InputStream(expression)

        # initialise lexer
        lexer = CellLexer(inputStream)
        # initialise TokenStream
        tokenStream = CommonTokenStream(lexer)

        # initialise parser
        parser = CellParser(tokenStream)

        # parse the expression
        tree = parser.expr()

        # toStringTree
        treeView = tree.toStringTree(recog=parser)
        # print("Parse Tree: ", treeView)

        visitor = CellEvalVisitor(self.registry)
        result = visitor.visitExpr(tree)
        print("RESULT ", result)
        return result
