class Material:
    """
    Material-focused CELL Card
    """

    def __init__(self, materialNumber, density=None, reg=None):
        self.materialNumber = materialNumber
        if reg:
            reg.addMaterial(self)
            self.reg = reg
        self.density = density

    def __itter__(self, lis):
        for el in range(len(lis)):
            yield lis[el]

    def toOutputString(self):  # used in cell card
        return str(self.materialNumber)


#  the rest of the classes are Material-focused DATA Cards


class M(Material):
    """
    Material Card
    """

    def __init__(
        self,
        *entries,
        GAS=None,
        ESTEP=None,
        HSTEP=None,
        NLIB=None,
        PLIB=None,
        PNLIB=None,
        ELIB=None,
        HLIB=None,
        ALIB=None,
        SLIB=None,
        TLIB=None,
        DLIB=None,
        COND=None,
        REFI=None,
        REFS=None,
    ):

        self.zk = []  # ZAID
        self.fk = []  # fraction
        for k in entries:
            if not isinstance(k, tuple):
                errorString = "every material constituent should be specified in a tuple: (z1,f1), (z2,f2), ..."
                raise TypeError(errorString)
            if not len(k) == 2:
                errorString = "every material constituent tuple needs zk and fk: (zk,fk)"
                raise TypeError(errorString)
            self.zk.append(k[0])
            self.fk.append(k[1])

        self.GAS = GAS
        self.ESTEP = ESTEP
        self.HSTEP = HSTEP
        self.NLIB = NLIB
        self.PLIB = PLIB
        self.PNLIB = PNLIB
        self.ELIB = ELIB
        self.HLIB = HLIB
        self.ALIB = ALIB
        self.SLIB = SLIB
        self.TLIB = TLIB
        self.DLIB = DLIB
        self.COND = COND
        self.REFI = REFI  # todo - can be a single REFI or list of REFI
        self.REFS = REFS  # todo - entries
        if REFS is not None:
            if not isinstance(REFS, list):
                errorString = "REFS is not a list"
                raise TypeError(errorString)

        if self.materialNumber not in self.reg.materialDict.keys():
            errorString = "the material number does not exist"
            raise TypeError(errorString)


class MT(Material):
    """
    Thermal Neutron Scattering
    """

    def __init__(self, materialNumber, *entry):
        if materialNumber not in self.reg.materialDict.keys():
            errorString = "the material number does not exist"
            raise TypeError(errorString)
        self.sabid = []
        for k in entry:
            self.sabid.append(k)

    def __repr__(self):
        return f"MT{self.materialNumber} {self.sabid}"


class MT0(MT):
    """
    Thermal Neutron Scattering
    """

    def __init__(self, *entries):
        self.identifier = []
        sabidTemp = []
        for k in entries:
            if not isinstance(k, tuple):
                errorString = "every MT0 constituent should be specified in a tuple: (sabid1,identifier_1), (sabid2,identifier_2), ..."
                raise TypeError(errorString)
            if not len(k) == 2:
                errorString = "every material constituent tuple needs zk and fk: (zk,fk)"
                raise TypeError(errorString)
            sabidTemp.append(k[0])
            self.identifier.append(k[1])

        super().__init__(0, *sabidTemp)

    def __repr__(self):
        return f'MT{self.materialNumber} {" ".join(str(x)+" "+str(y) for x, y in zip(self.sabid, self.identifier))}'


class MX(Material):
    """
    Material Card Nuclide Substitution
    """

    def __init__(self, materialNumber, p, *entry):
        self.p = p
        self.zk = []
        for k in entry:
            self.zk.append(k)

    def __repr__(self):
        return f"MX{self.materialNumber}:{self.p} {self.zk}"


class MPN:
    """
    Photonuclear Nuclide Selector
    """

    def __init__(self):
        errorString = "This feature has been replaced by the material card nuclide substitution (MX) capability in MCNP. To control the selection of photonuclear nuclide data, use the MX card."
        raise TypeError(errorString)


class OTFDB:
    """
    On-the-fly-Doppler Broadening
    """

    def __init__(self, *entry):
        self.zk = []
        for k in entry:
            self.zk.append(k)


class TOTNU:
    """
    Total Fission
    """

    def __init__(self, value=None):
        self.value = value


class NONU:
    """
    Disable Fission
    """

    def __init__(self, *entry):
        self.aj = []
        for j in entry:
            self.aj.append(j)


class AWTAB:
    """
    Atomic Weight
    """

    def __init__(self, *entries):
        self.zk = []
        self.ak = []
        for k in entries:
            if not isinstance(k, tuple):
                errorString = "every entry should be specified in a tuple: (z1,a1), (z2,a2), ..."
                raise TypeError(errorString)
            if not len(k) == 2:
                errorString = "every entry tuple needs zk and ak: (zk,ak)"
                raise TypeError(errorString)
            self.zk.append(k[0])
            self.ak.append(k[1])


class XS:
    """
    Cross-Section File
    """

    def __init(self, xNumber, *entries, remaining_xsdir=None):
        self.xNumber = xNumber
        self.zk = []
        self.ak = []
        self.remaining_xsdir = remaining_xsdir  # ?
        for k in entries:
            if not isinstance(k, tuple):
                errorString = "every entry should be specified in a tuple: (z1,a1), (z2,a2), ..."
                raise TypeError(errorString)
            if not len(k) == 2:
                errorString = "every entry tuple needs zk and ak: (zk,ak)"
                raise TypeError(errorString)
            self.zk.append(k[0])
            self.ak.append(k[1])


class VOID:
    """
    Material Void
    """

    def __init__(self, *entry):
        self.cj = []
        for j in entry:
            self.cj.append(j)


class MGOPT:
    """
    Multigroup Adjoint Transport Option
    """

    def __init__(self, mcal, igm, iplt=0, isb=0, icw=0, fnw=1, rim=1000):
        self.mcal = mcal
        self.igm = igm
        self.iplt = iplt
        self.isb = isb
        self.icw = icw
        self.fnw = fnw
        self.rim = rim


class DRXS:
    """
    Discrete-Reaction Cross Section
    """

    def __init__(self, *entry):
        self.zk = []
        for k in entry:
            self.zk.append(k)
