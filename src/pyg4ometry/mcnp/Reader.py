import antlr4

from .CellExpression import (
    CellVisitor,
    CellParser,
    CellLexer,
)

from .Registry import Registry
from . import Surfaces
import os.path


class Reader:
    """
    Class to read a MCNP file.
    """

    def __init__(self, filename):
        self.filename = filename
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
                # todo add TR to reg, or bake in?
            else:
                mnemonicIndex = 1

            surfaceMnemonic = parts[mnemonicIndex].upper().replace("/", "_")
            if surfaceMnemonic == "RHP" or surfaceMnemonic == "HEX":
                surfaceMnemonic = "RHP_HEX"

            surfaceDef = [float(value) for value in parts[mnemonicIndex + 1 :]]
            print(f" S = |{surfaceNum}| |{TRn}| |{surfaceMnemonic}| |{surfaceDef}|")

            s = self._makeSurface(
                surfaceMnemonic, *surfaceDef, reg=self.registry, surfaceNumber=int(surfaceNum)
            )
            self.registry.addSurface(s)

        # deal with cell card
        # todo cellNum1 LIKE cellNum2 BUT list
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
                            toRemove.append(part)  # Mark part for removal
            cellParams.append(cellDict)

            # Remove processed parts
            remainingParts = [part for part in partsUpper if part not in toRemove]

            cellNum = int(remainingParts[0])
            materialNum = int(remainingParts[1])
            density = None

            if materialNum != 0:
                density = remainingParts[2]
                defIndex = 2
            else:  # zero material is void
                defIndex = 1

            geometry = " ".join(remainingParts[defIndex + 1 :])

            params = "TBD"

            print(f" C = |{cellNum}| |{materialNum}| |{density}| |{geometry}| |{params}|")

            print(f" params = {cellDict}")

            # c = self._makeCell()
            # self.registry.addCell(c)

            # todo if TRCL following line add to reg or bake-in

        for dataline in self.cardStack[2]:
            dummy = True
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

    def _makeCell(self):
        c = 2
        return c

    def _injectWhitespace(self, line):
        line = line
        return line
        # give this line to the parser
        # that parser-visitor then returns you a cell object
        # cell object added to registry

    # if surface, make the surface object, put it into the registry
    # if cell, make the cell object, put it into the registry
    # ...
    # the output of the reader is the registry
    # the registry can just be passed to the visuliser
    # the visulisation goes though and loops though all cells and says, give me a mesh
