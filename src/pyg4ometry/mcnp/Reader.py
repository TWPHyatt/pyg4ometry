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

        for s in self.cardStack[1]:
            surfaceNum = None
            TRn = None
            mnemonic = None
            surfaceDef = None
            mnemonicBool = False
            x = s.split()
            for c in x:
                if mnemonicBool is True:
                    surfaceDef += " " + c
            else:
                surfaceNum = x[0]
            if x[1].isnumeric():
                TRn = x[1]
            if not c.isnumeric():
                print(c, "N")
            mnemonicBool = True
            mnemonic = c
            surfaceDef = ""
            surfaceDef = surfaceDef.strip()
            print(x)
            print(f"|{surfaceNum}| |{TRn}| |{mnemonic}| |{surfaceDef}|")
            # todo WHY IS MNEMONIC NONE?

            # todo change "/" to "_"

            s = self._makeSurface(mnemonic.capitalize(), 10, reg=self.registry)
            self.registry.addSurface(s)
            # todo if TR following line add to reg or bake-in

        for cellLine in self.cardStack[0]:
            print("cell: ", cellLine)
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

    def injectWhitespace(self, line):
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
