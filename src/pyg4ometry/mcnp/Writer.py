class Writer:
    """
    Class to write MCNP input files from an MCNP registry object

    >> f = Writer()
    >> f.addGeometry(reg=reg)
    >> f.write("i-example.txt")
    """

    def __init__(self, columnMax=128):
        self.title = "TITLE"
        self.col = columnMax
        if 80 < self.col < 128:
            msg = "For MCNP6.2 the column limit was increased to 128 from 80 in previous versions"
            # print(msg)
        if self.col > 128:
            msg = "For MCNP6.2 the column limit is 128"
            raise TypeError(msg)

    def addGeometry(self, reg):
        """
        Set the mcnp registry for this writer instance
        """
        self.reg = reg

    def write(self, fileName):
        """
        Write the output to a given filename. e.g. "model.inp"
        """

        writerSurfaceDict = {}

        f = open(fileName, "w")

        self.reg.updateRegistry()
        # self.reg.hashTransformations()
        # self.reg.hashMaterials()

        f.write(f"{self.title}\n")

        f.write("c ********** CELLS **********\n")

        for cell in self.reg.cellDict:
            parts = []

            # cell numbers
            parts.append(self.reg.cellDict[cell].toOutputString())

            # material output
            parts.append(self.reg.cellDict[cell].material.toOutputString())

            # geometry output
            parts.append(self.reg.cellDict[cell].geometry.toOutputString())

            # keywords output
            for imp in self.reg.cellDict[cell].importance:
                parts.append(imp.toOutputString())
                # todo maybe check if multiple importances then can only be of form 1
                # todo form 2 is specified in the data card only so can't be added to a cell...

            if self.reg.cellDict[cell].transformation:
                parts.append(f"TRCL={self.reg.cellDict[cell].transformation.transformationNumber}")

            # join all parts with spaces
            fullLine = " ".join(parts)

            # wrap line by column max
            line = self._splitByMaxColumn(fullLine)
            f.write(line + "\n")

        f.write("\nc ********** SURFACES **********\n")

        surfacesToWrite = []
        for cell in self.reg.cellDict.values():
            for surface in cell.surfaceList(cell.geometry):
                if surface not in surfacesToWrite:
                    surfacesToWrite.append(surface)

        for surface in surfacesToWrite:
            parts = []

            # surface number
            parts.append(surface.toOutputString())
            # surface mnemonic and input parameters
            parts.append(surface.__repr__())

            if cell.transformation is not None:
                parts.insert(1, str(cell.transformation.transformationNumber))

            # join all parts with spaces
            fullLine = " ".join(parts)

            # round surface input parameters
            cleanLine = self._roundInputValues(fullLine)

            # wrap line by column max
            # line = self._splitByMaxColumn(cleanLine)
            line = cleanLine
            f.write(line + "\n")

        f.write("\nc ********** DATA **********\n")
        f.write("c --- TRANSFORMATIONS ---\n")
        # TRCL
        transformationsToWrite = []
        for cell in self.reg.cellDict.values():
            if cell.transformation not in transformationsToWrite:
                transformationsToWrite.append(cell.transformation)
                if cell.transformation is not None:
                    fullLine = cell.transformation.toOutputString()
                    cleanLine = self._roundInputValues(fullLine)
                    line = self._splitByMaxColumn(cleanLine)
                    f.write(line + "\n")

        # TR
        transformationsToWrite = []
        for surface in surfacesToWrite:
            if surface.transformation not in transformationsToWrite:
                transformationsToWrite.append(surface.transformation)
                if surface.transformation is not None:
                    fullLine = surface.transformation.toOutputString()
                    cleanLine = self._roundInputValues(fullLine)
                    line = self._splitByMaxColumn(cleanLine)
                    f.write(line + "\n")

        # ToDo data cards and keywords

        # TEMP WRITING DATA STRING SO FILE RUNS WITHOUT ALTERATION
        f.write("c\nmode p\nc\n")
        f.write(
            "m1 6000 -0.000124 7000 -0.755267 8000 -0.231782 18000 -0.012827\nm2 79000 -1.0\nm3 18000 -1.0\n"
        )
        f.write("c --- SOURCE ---\nc point source 14.0 MeV\n")
        f.write("sdef     pos 45. 0. 0. erg=14. par=p\n")
        f.write("c --- DETECTOR ---\n")
        f.write("F5:p 0 -40 0 0\nNPS 2e5\n")

        # close file
        f.close()

    def setTitle(self, title):
        if isinstance(title, str):
            msg = "title must be a string"
            if 1 > len(title) > 128:
                msg = "title must be between 1 and 128 characters long"
        self.title = title

    def _roundInputValues(self, fullLine, precision=6, zeroThreshold=1e-12):
        lineElements = fullLine.strip().split()
        formattedLine = []

        for element in lineElements:
            try:
                # try converting element to float
                number = float(element)
                # apply rounding
                if abs(number) < zeroThreshold:
                    # format numerical elements close to zero as zero
                    formattedLine.append("0")
                else:
                    # format other numerical elements with a precision
                    formattedLine.append(f"{number:.{precision}g}")
            except ValueError:
                # string (surface mnemonic) so do not apply precision
                formattedLine.append(element)

        return " ".join(formattedLine)

    def _splitByMaxColumn(self, fullLine):
        """
        edit file so all input lines are limited to the maximum number of columns
        split lines finish with an ampersand and the new line starts with a space
        """
        lineElements = fullLine.strip().split()
        resultLines = []
        currentLine = ""

        for element in lineElements:
            # Check if adding the word would exceed the column limit
            if len(currentLine) + len(element) + 1 > self.col:
                # Add current line to result with continuation
                resultLines.append(currentLine + "&")
                currentLine = " " + element  # Start new line with a space
            else:
                if currentLine:
                    currentLine += " " + element
                else:
                    currentLine = element

        # Add the final line
        resultLines.append(currentLine)
        return "\n".join(resultLines)
