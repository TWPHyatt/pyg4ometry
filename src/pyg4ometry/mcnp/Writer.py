class Writer:
    """
    Class to write MCNP input files from a fluka registry object.

    >> f = Writer()
    >> f.addGeometry(reg=reg)
    >> f.write("i-example.txt")
    """

    def __init__(self):
        pass

    def addGeometry(self, registry):
        """
        Set the mcnp registry for this writer instance.
        """
        self.registry = registry

    def write(self, fileName):
        """
        Write the output to a given filename. e.g. "model.inp".
        """

        f = open(fileName, "w")

        f.write("TITLE\n")

        # loop over cell dictionary
        f.write("********** CELLS **********\n")
        for cell in self.registry.cellDict:
            f.write(f"{cell} ")
            f.write(f" ")
            f.write(f"{self.registry.cellDict[cell].toOutputString()}")
            f.write(f" ")
            f.write(f"{self.registry.materialDict[cell].toOutputString()}")
            # write the special material cards (MT, MT0, MX MPN, ...) ?
            f.write("\n")

        # loop over surface dictionary
        f.write("\n********** SURFACES **********\n")
        for surface in self.registry.surfaceDict:
            f.write(f"{surface} ")
            f.write(f"{self.registry.surfaceDict[surface].__repr__()}")
            f.write("\n")

        # todo transformations

        # loop over the data card dictionaries
        f.write("\n********** DATA **********\n")
        # todo replace temp data card with materialDict loop etc.
        f.write("mode p\n")
        f.write("m1   6000 -0.00124  7000 -0.755267\n")
        f.write("     8000 -0.23178  1800 -0.012827\n")
        f.write("m6   26000 -1.0\n")
        f.write("c --- SOURCE ---\n")
        f.write("sdef   pos 12. 0. 0. erg=14. par=p\n")
        f.write("c --- DETECTOR ---\n")
        f.write("F2:p 6\n")
        f.write("NPS 2e5")

        # close file
        f.close()
