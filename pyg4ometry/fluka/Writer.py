from pyg4ometry.fluka import material as _material

class Writer :

    def __init__(self):
        pass

    def addDetector(self, flukaRegistry):
        self.flukaRegistry = flukaRegistry

    def write(self, fileName):
        f = open(fileName,"w")

        # actually used rot-defi directives
        rotdefi = {}

        f.write("GEOBEGIN                                                              COMBNAME\n")
        f.write("    0    0                                                                    \n")
        # loop over bodies
        for bk in self.flukaRegistry.bodyDict.keys() :
            #f.write("$Start_translat {} {} {}\n".format(self.flukaRegistry.bodyDict[bk].translation[0],
            #                                            self.flukaRegistry.bodyDict[bk].translation[1],
            #                                            self.flukaRegistry.bodyDict[bk].translation[2]))
            transform = self.flukaRegistry.bodyDict[bk].transform


            if len(transform) != 0 :
                if transform.flukaFreeString() != '' :
                    f.write("$Start_transform "+transform.name+"\n")
                    try :
                        rotdefi[transform.name] = transform
                    except KeyError :
                        pass

            f.write(self.flukaRegistry.bodyDict[bk].flukaFreeString()+"\n")

            if len(transform) != 0 :
                if transform.flukaFreeString() != '' :
                    f.write("$End_transform\n")
        f.write("END\n")

        # loop over regions
        for rk in self.flukaRegistry.regionDict.keys() :
            f.write(self.flukaRegistry.regionDict[rk].flukaFreeString()+"\n")
        f.write("END\n")
        f.write("GEOEND\n")

        # loop over materials
        f.write("FREE\n")

        predefinedNames = _material.predefinedMaterialNames()
        for mk in self.flukaRegistry.materials.keys() :
            # check if material/compound is already defined
            if mk in predefinedNames :
                pass
            else :
                f.write(self.flukaRegistry.materials[mk].flukaFreeString()+"\n")

        # loop over rotdefis
        for rotdefi in rotdefi.values():
            rotstr = rotdefi.flukaFreeString()
            f.write(f"{rotstr}\n")
        f.write("END\n")
        f.close()

