import antlr4

from .CellExpression import (
    CellVisitor,
    CellParser,
    CellLexer,
)

from .Registry import Registry

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
        print(self.cardStack)

    def _processFile(self, filein):
        with open(filein) as f:
            lines = f.readlines()

        lines.pop(0)  # remove title line
        lineStack = list(reversed(lines))  # a stack of lines
        tempStack = []

        while lineStack:
            line = lineStack.pop()

            line = line.split("$")[0]  # "$" in line comments
            line = line.strip()  # Leading and trailing whitespace

            if line.startswith("c"):  # "c" comment lines
                continue

            if not line.split():  # line of whitespace
                print("WHITE SPACE LINE")
                self.cardStack.append(tempStack)
                tempStack = []  # on whitespace line, start stacking new card (cell, surface, data)

            print(" > ", line)
            self.cardStack.append(line)

        self.cardStack.append(tempStack)

        return

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
