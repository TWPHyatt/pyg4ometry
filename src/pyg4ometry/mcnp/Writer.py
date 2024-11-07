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
        f.write("c ********** CELLS **********\n")
        for cell in self.registry.cellDict:
            f.write(f"")
            f.write(f"{self.registry.cellDict[cell].toOutputString()}")
            f.write(f" ")
            f.write(
                f"{self.registry.materialDict[self.registry.cellDict[cell].materialNumber][self.registry.cellDict[cell].materialIndex].toOutputString()}"
            )
            f.write(f" ")
            f.write(f"{self.registry.cellDict[cell].geometry.toOutputString()}")
            f.write(f" ")
            for imp in self.registry.cellDict[cell].importance:
                f.write(f"{imp.toOutputString()} ")
            # todo maybe check if multiple importances then can only be of form 1
            # todo form 2 is specified in the data card only so can't be added to a cell...
            f.write("\n")

        # loop over surface dictionary
        f.write("\nc ********** SURFACES **********\n")
        for surface in self.registry.surfaceDict:
            f.write(f"")
            f.write(f"{self.registry.surfaceDict[surface].toOutputString()}")
            f.write(f" ")
            f.write(f"{self.registry.surfaceDict[surface].__repr__()}")
            f.write("\n")

        # todo transformations

        # loop over the data card dictionaries
        f.write("\nc ********** DATA **********\n")
        # todo replace temp data card with materialDict loop etc.
        f.write("mode p\n")
        f.write("c\n")
        f.write("c NIST dry air\n")
        f.write("m1 6000 -0.000124 7000 -0.755267\n")
        f.write("   8000 -0.231782 18000 -0.012827\n")
        f.write("m6 79000 -1.0\n")
        f.write("c --- SOURCE ---\n")
        f.write("c point source 14.0 MeV\n")
        f.write("sdef     pos 7. 0 0. erg=14. par=p\n")
        f.write("c --- DETECTOR ---\n")
        f.write("F2:p 2\n")
        f.write("NPS 2e5\n")

        # close file
        f.close()
