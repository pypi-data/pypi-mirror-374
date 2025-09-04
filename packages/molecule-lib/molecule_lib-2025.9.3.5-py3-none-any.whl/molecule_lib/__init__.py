#!/usr/bin/env python
# """TTMolE Developed by: Jeremy Schroeder 2025.9.3.5"""
from __future__ import annotations

# Header style from https://gist.github.com/NicolasBizzozzero/6d4ca63f8482a1af99b0ed022c13b041
__author__ = "Jeremy Schroeder"
__contact__ = "jeremynschroeder@gmail.com"
__date__ = "9-3-2025"
__email__ = __contact__
__license__ = "GPL-3.0-or-later"
__status__ = "Development"
__version__ = "2025.9.3.5"
__version_tuple__ = (2025, 9, 3, 5)

import copy
import os
from math import cos, pi, sin, sqrt, tan, ceil
import re
import numpy as np
from .cif2pos import symmetry, atominfo, lattice, p1atom, readfile
try:
    from rdkit.Chem import MolFromXYZBlock
    from rdkit.Chem.rdchem import Mol as rdkit_Chem_rdchem_Mol
except ImportError:
    MolFromXYZBlock = None
    rdkit_Chem_rdchem_Mol = None
# import ase
# ========================================================
#
#               GLOBALs Definitions SECTION
#  ACCEPTED_ELEMENTS, Lx, Fx, La, Fa, Sa, Lc, Fc,
#    UC_90_ANGLE_MAX, UC_90_ANGLE_MIN, MolIndex, MOLARMASS
# ========================================================


class GLOBALS_DOCSTRINGS:
    """
    Attributes
    ----------
    ACCEPTED_ELEMENTS
        List of string of species types
    Lx
        total length of float str. Will add spaces to left to get to length
    Fx
        amount of digits shown after decimal
    La
        same as Lx but for ABCMolecules
    Fa
        same as Fx but for ABCMolecules
    Sa
        space in between selective coords for formatting
    Lc
        the c is used in coord strings, for formatting in editor scrollable
    Fc
        # same as Fx but for ABCMolecules
    UC_90_ANGLE_MAX (float in degrees)
        Globals needed for ABCMolecule.rotate() trigonal aka rectangular unitcell box cutoff
    UC_90_ANGLE_MIN (float in degrees)
        Globals needed for ABCMolecule.rotate() trigonal aka rectangular unitcell box cutoff
    MolIndex
        custom data type for indexing ABCMolecule and XYZMolecule classes
    MOLAR_MASS
        Molar Mass of each species
    Fl
        format for float strings for lammps
    """
    pass


# yapf: disable

ACCEPTED_ELEMENTS: list[str] = [
    "n", #to be able to index ACCEPTED_ELEMENTS by periodic table number
    "H" ,                                                                                "He",
    "Li","Be",                                                  "B" ,"C" ,"N" ,"O" ,"F" ,"Ne",
    "Na","Mg",                                                  "Al","Si","P" ,"S" ,"Cl","Ar",
    "K" ,"Ca","Sc","Ti","V" ,"Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr",
    "Rb","Sr","Y" ,"Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I" ,"Xe",
    "Cs","Ba",     "Hf","Ta","W" ,"Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn",
    "Fr","Ra",     "Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg","Cn","Nh","Fl","Mc","Lv","Ts","Og",

    "La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu",
    "Ac","Th","Pa","U" ,"Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr",

    "Zz",'Xx',"Z","X",  #non element placeholders, must be below for xsf files
]


MOLAR_MASS: dict[str, float] = {
    "Zz": 0, 'Xx': 0, "Z": 0, "X": 0, #needed to not have KeyError
    # generated from periodictable python package {pt.elements.list('symbol','mass')}
    # *Wang. M., Huang. W. J., Kondev. F. G., Audi. G., Naimi. S., The AME 2020 atomic mass evaluation (II). Tables, graphs and references *
    # https://periodictable.readthedocs.io/en/latest/api/core.html#periodictable.core.Element

    # "n": 1.00866491597, #electron molar mass commenented out for lammps stuff

    "H" :  1.00794,"He":  4.002602,
    "Li":  6.941,  "Be": 9.012182,                                                                                                                                            "B": 10.811,    "C": 12.0107,"N": 14.0067,  "O": 15.9994,"F": 18.9984032,"Ne": 20.1797,
    "Na": 22.98977,"Mg": 24.305,                                                                                                                                             "Al": 26.981538,"Si": 28.0855,"P": 30.973761,"S": 32.065,"Cl": 35.453,    "Ar": 39.948,
    "K" : 39.0983, "Ca": 40.078,"Sc":44.95591,"Ti": 47.867, "V": 50.9415, "Cr": 51.9961,"Mn": 54.938049,"Fe": 55.845,"Co": 58.9332,"Ni": 58.6934,"Cu": 63.546,  "Zn": 65.409,"Ga": 69.723,   "Ge": 72.64, "As": 74.9216, "Se": 78.96, "Br": 79.904,    "Kr": 83.798,
    "Rb": 85.4678, "Sr": 87.62,  "Y":88.90585,"Zr": 91.224,"Nb": 92.90638,"Mo": 95.94,  "Tc": 98,       "Ru":101.07, "Rh":102.9055,"Pd":106.42,  "Ag":107.8682, "Cd":112.411,"In":114.818,   "Sn":118.71, "Sb":121.76,   "Te":127.6,   "I": 126.90447, "Xe": 131.293,
    "Cs":132.90545,"Ba":137.327,              "Hf":178.49, "Ta":180.9479,  "W":183.84,  "Re":186.207,   "Os":190.23, "Ir":192.217, "Pt":195.078, "Au":196.96655,"Hg":200.59, "Tl":204.3833,  "Pb":207.2,  "Bi":208.98038,"Po":209,    "At":210,        "Rn": 222,
    "Fr":223,      "Ra":226,                  "Rf":261,    "Db":262,      "Sg":266,     "Bh":264,       "Hs":277,    "Mt":268,     "Ds":281,     "Rg":272,      "Cn":285,    "Nh":286,       "Fl":289,    "Mc":289,      "Lv":293,    "Ts":294,        "Og": 294,

    "La":138.9055,"Ce":140.116, "Pr":140.90765,"Nd":144.24,   "Pm":145,"Sm":150.36,"Eu":151.964,"Gd":157.25,"Tb":158.92534,"Dy":162.5,"Ho":164.93032,"Er":167.259,"Tm":168.93421,"Yb":173.04,"Lu":174.967,
    "Ac":227,     "Th":232.0381,"Pa":231.03588, "U":238.02891,"Np":237,"Pu":244,   "Am":243,    "Cm":247,   "Bk":247,      "Cf":251,  "Es":252,      "Fm":257,    "Md":258,      "No":259,   "Lr":262,

}


# globals for formatting: (up here to find and change easier)
Lx = 10  # total length of float str. Will add spaces to left to get to length
Fx = 6  # amount of digits shown after decimal
La = 15  # same as Lx but for ABCMolecules
Fa = 6  # same as Fx but for ABCMolecules
Sx = "  "
Sa = "  "  # space in between selective coords for formatting
Lc = 11  # the c is used in coord strings, for formatting in editor scrollable
Fc = 6
Fl = ".10f" #format for float strings for lammps
# Globals needed for ABCMolecule.rotate() trigonal aka rectangular unitcell box cutoff
UC_90_ANGLE_MAX = 95  # in deg
UC_90_ANGLE_MIN = 85  # in deg

# yapf: enable

# ========================================================
#
#           Functions needed for later SECTION
#           csc(), sec(), cot() and _isfloatstr()
# ========================================================


def _is_ae(num_list, tolerance_percentage):
    """is_approximately_equal chatgpt idea."""
    average = sum(num_list) / len(num_list)
    tolerance = average * (tolerance_percentage / 100)
    return all(abs(num - average) <= tolerance for num in num_list)


def _isfloatstr(item: str, pos_only: bool = False) -> bool:
    """Return True if item is float string, False otherwise."""
    if not isinstance(item, str):
        return False
    if item.find(".") != -1 and item.find(".", item.find(".") + 1) != -1:
        return False
    # old string methods
    # if pos_only:
    #     return item.replace(".", "").isdecimal()
    # else:
    #     return item.replace(".", "").replace("-", "").isdecimal()
    # new regex methods
    if pos_only:
        if re.match(pattern=r"^[+]?(?=\d|\.\d)*(\.\d+)?", string=item) == True:
            return True
        else:
            return False
    else:
        if re.match(pattern=r"^[+-]?(?=\d|\.\d)*(\.\d+)?",
                    string=item) == True:
            return True
        else:
            return False


def _regex_string_list(string_list: list[str],
                       pattern_list: list[str],
                       strict_on_length: bool = False,
                       debug_print: bool = False) -> bool:
    """Returns True if regex pattern_list matches string_list, False otherwise.

    Parameters
    ----------
    string_list : list[str]
        List of strings to check using regex and pattern_list.
    pattern_list : list[str]
        List of regex expressions.
    strict_on_length : bool, default False.
        If True, if the length of the string_list exceeds the length of pattern_list, False is returned.

    Returns
    -------
    bool
        True if every position of regex pattern_list is True for each position of pattern_list, False otherwise.
    """
    if debug_print:
        print(f"_regex_string_list() {string_list = }")
        print(f"_regex_string_list() {pattern_list = }")
    if len(string_list) < len(pattern_list):
        if debug_print:
            print("_regex_string_list() False")
        return False
    if strict_on_length:
        if len(string_list) != len(pattern_list):
            if debug_print:
                print("_regex_string_list() False")
            return False
    for n in range(len(pattern_list)):
        if pattern_list[n] == "None":
            continue
        if re.fullmatch(pattern=pattern_list[n],
                        string=string_list[n]) == None:
            if debug_print:
                print("_regex_string_list() False")
            return False
    if debug_print:
        print("_regex_string_list() True")
    return True


def _regex_nested_string_list(nested_string_list: list[list[str]],
                              pattern_list: list[str],
                              strict_on_length: bool = False,
                              debug_print: bool = False) -> tuple[bool, int]:
    """Returns (True,index of found list) if regex pattern_list is found. (False, 0) otherwise.

    Parameters
    ----------
    nested_string_list : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.
    pattern_list : list[str]
        List of regex expressions.

    Returns
    -------
    tuple[bool, int]
        (True,index of found list) if regex pattern_list is found. (False, 0) otherwise.
    """
    for n, line in enumerate(nested_string_list):
        if _regex_string_list(string_list=line,
                              pattern_list=pattern_list,
                              strict_on_length=strict_on_length,
                              debug_print=debug_print):
            return True, n
    return False, 0


# ========================================================
#
#
#               ABC MOLECULE SECTION
#
#
# ========================================================
# ========================================================
#
#               ABC classes SECTION
#       ABCCoord, LatticeMatrix and ABCMolecule
# ========================================================


class ABCCoord:
    """Dataclass for atomic coordinates for use in ABCMolecule class.

    Parameters
    ----------
    sp : str
        Species of atom.
    a : float
        a or x coordinate position of atom.
    b : float
        b or y coordinate position of atom.
    c : float
        c or z coordinate position of atom.

    Returns
    -------
    ABCCoord
        ABCCoord object containing data from defined arguments.
    """

    def __init__(self, sp: str, a: float, b: float, c: float) -> None:
        if sp not in ACCEPTED_ELEMENTS:
            raise ValueError(f"ABCCoord.__init__() required argument 'sp' = '{sp}' is not an accepted species string.") # yapf: disable
        if not isinstance(a, (int, float)):
            raise ValueError(f"ABCCoord.__init__() required argument 'a' = {a} is not a number.") # yapf: disable
        if not isinstance(b, (int, float)):
            raise ValueError(f"ABCCoord.__init__() required argument 'b' = {b} is not a number.") # yapf: disable
        if not isinstance(c, (int, float)):
            raise ValueError(f"ABCCoord.__init__() required argument 'c' = {c} is not a number.") # yapf: disable
        self.sp = sp
        self.a = a
        self.b = b
        self.c = c

    def __str__(self) -> str:
        return f"ABCCoord(sp='{self.sp}', x={self.a}, y={self.b}, z={self.c})"

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return 1

    def __getitem__(self, index: int) -> float:
        if index == 1:
            return self.a
        elif index == 2:
            return self.b
        elif index == 3:
            return self.c
        else:
            raise IndexError(f"ABCCoord.__getitem__() index = '{index}'; Index not 1,2, or 3.") # yapf: disable

    def line(self) -> str:
        """Returns string of species line. Used in ABCMolecule._format()"""
        return f"{self.sp:>4} {self.a:>{Lc}.{Fc}f}{self.b:>{Lc}.{Fc}f}{self.c:>{Lc}.{Fc}f}"


class XYZCoord:
    """Dataclass for atomic coordinates for use in XYZMolecule class.

    Parameters
    ----------
    sp : str
        Species of atom.
    x : float
        x coordinate position of atom.
    y : float
        y coordinate position of atom.
    z : float
        z coordinate position of atom.

    Returns
    -------
    XYZCoord
        XYZCoord object containing data from defined arguments.
    """

    def __init__(self, sp: str, x: float, y: float, z: float) -> None:
        if sp not in ACCEPTED_ELEMENTS:
            raise ValueError(f"XYZCoord.__init__() required postional argument 'sp' = '{sp}' is not an accepted species string.") # yapf: disable
        if not isinstance(x, (int, float)):
            raise ValueError(f"XYZCoord.__init__() required positional argument 'x' = {x} is not a number.") # yapf: disable
        if not isinstance(y, (int, float)):
            raise ValueError(f"XYZCoord.__init__() required positional argument 'y' = {y} is not a number.") # yapf: disable
        if not isinstance(z, (int, float)):
            raise ValueError(f"XYZCoord.__init__() required positional argument 'z' = {z} is not a number.") # yapf: disable
        self.sp: str = sp
        self.x: float = x
        self.y: float = y
        self.z: float = z

    def __str__(self) -> str:
        return f"XYZCoord(sp='{self.sp}', x={self.x}, y={self.y}, z={self.z})"

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return 1

    def __getitem__(self, index: int) -> float:
        if index == 1:
            return self.x
        elif index == 2:
            return self.y
        elif index == 3:
            return self.z
        else:
            raise IndexError(f"XYZCoord.__getitem__() index = '{index}'; Index not 1,2, or 3.") # yapf: disable

    def line(self) -> str:
        """Returns string of species line. Used in XYZMolecule._format()"""
        return f"{self.sp:>4} {self.x:>{Lc}.{Fc}f}{self.y:>{Lc}.{Fc}f}{self.z:>{Lc}.{Fc}f}"


# custom data type for indexing ABCMolecule and XYZMolecule classes
MolIndex = int | str | list[int | str]  # one day  = | slice
CoordType = ABCCoord | XYZCoord  #Coord Type combined for better readability


class LatticeMatrix:
    """Dataclass which contains the unit cell information needed for ABCMolecule object.

    Parameters
    ----------
    constant : float
        Lattice constant.
    vector_1 : [float,float,float]
        List of float numbers of length 3 containing the first vector of lattice matrix.
    vector_2 : [float,float,float]
        List of float numbers of length 3 containing the second vector of lattice matrix.
    vector_3 : [float,float,float]
        List of float numbers of length 3 containing the third vector of lattice matrix.

    Fields
    ------
    a: float
        Sidelength a of unitcell.\n
    b: float
        Sidelength b of unitcell.\n
    c: float
        Sidelength c of unitcell.\n
    alp: float
        Angle alpha of unitcell in radians.\n
    bet: float
        Angle beta of unitcell in radians.\n
    gam: float
        Angle gamma of unitcell in radians.\n
    volume: float
        Total Volume of unitcell in Angstroms cubed.\n

    Returns
    -------
    LatticeMatrix
        LatticeMatrix object which contains the unit cell information needed for ABCMolecule object.
    """

    def __init__(self, constant: float, vector_1: list[float],
                 vector_2: list[float], vector_3: list[float]) -> None:
        if not isinstance(constant, (int, float)):
            raise ValueError(f"LatticeMatrix.__init__() required argument 'constant' = {constant} is not a number.") # yapf: disable
        for name, vector in zip(["vector_1", "vector_2", "vector_3"],
                                [vector_1, vector_2, vector_3]):
            if not isinstance(vector, (list, tuple, set)):
                raise ValueError(f"LatticeMatrix.__init__() required argument '{name}' = {vector} is not a list.") # yapf: disable
            if len(vector) != 3:
                raise ValueError(f"LatticeMatrix.__init__() required argument '{name}' = {vector} is not a list of length 3.") # yapf: disable
            for index in range(3):
                if not isinstance(vector[index], (int, float)):
                    raise ValueError(f"LatticeMatrix.__init__() required argument '{name}' index {index} = {vector[index]} is not a number.") # yapf: disable
        self.constant: float = constant
        self.vector_1: list[float] = vector_1
        self.vector_2: list[float] = vector_2
        self.vector_3: list[float] = vector_3
        self.__post_init__()

    def __post_init__(self) -> None:
        self.a: float = (self.vector_1[0]**2 + self.vector_1[1]**2 +
                         self.vector_1[2]**2)**(1 / 2)
        self.b: float = (self.vector_2[0]**2 + self.vector_2[1]**2 +
                         self.vector_2[2]**2)**(1 / 2)
        self.c: float = (self.vector_3[0]**2 + self.vector_3[1]**2 +
                         self.vector_3[2]**2)**(1 / 2)
        self.alp: float = np.arccos(
            np.dot(np.array(self.vector_2), np.array(self.vector_3)) /
            (self.b * self.c))
        self.bet: float = np.arccos(
            np.dot(np.array(self.vector_1), np.array(self.vector_3)) /
            (self.a * self.c))
        self.gam: float = np.arccos(
            np.dot(np.array(self.vector_1), np.array(self.vector_2)) /
            (self.a * self.b))
        self.volume: float = (
            self.a * self.b * self.c *
            (1 + 2 * np.cos(self.alp) * np.cos(self.bet) * np.cos(self.gam) -
             np.cos(self.alp)**2 - np.cos(self.bet)**2 - np.cos(self.gam)**2)
            **(1 / 2))

    def __str__(self) -> str:
        return f"LatticeMatrix(constant={self.constant}, vector_1={self.vector_1}, vector_2={self.vector_2}, vector_3={self.vector_3})"

    def __repr__(self) -> str:
        return self.__str__()

    def getabc(self) -> tuple[float, float, float]:
        """Returns sidelengths (a,b,c) of unitcell."""
        return self.a, self.b, self.c

    def getanglesdeg(self) -> tuple[float, float, float]:
        """Returns (alpha, beta, gamma) of unitcell in degrees."""
        return (self.alp * (180 / pi), self.bet * (180 / pi),
                self.gam * (180 / pi))

    def getanglesrad(self) -> tuple[float, float, float]:
        """Returns (alpha, beta, gamma) of unitcell in radians."""
        return self.alp, self.bet, self.gam

    def getcommentline(self) -> str:
        "Returns string representation"
        return f"  a, b, c (angstrom) = {self.getabc()} alpha, beta, gamma (deg) = {self.getanglesdeg()}"


class ABCMolecule:
    """Class for ABC molecule object.

    Parameters
    ----------
    unitcell : LatticeMatrix
        Instance of LatticeMatrix dataclass needed for ABCMolecule class.
    positional : bool, default True
        If True, given ABCCoords are positional coordinates. If False, given ABCCoords are cartesian coordinates in Angstroms.
    atoms : list[ABCCoord]
        List of Atoms from atomic file.
    comment_line : str, default is " "
        Comment line of atomic file.
    frozen_atoms : optional list[list[str]]
        If there are frozen atoms, indicate them here.
    filetype : str, default is "unitcell"
        The original filetype the object instance was.

    Fields
    ------
    species_line: list[str]
        List of each species in species line. Similar to line 5 in VASP file.\n
    species_amount: list[int]
        List of the amount of each species in species line. Similar to line 6 in VASP file.\n
    total: int
        Total amount of atoms in ABCMolecule object.\n
    amount_dict: dict[str, int]
        Dictionary with keys as species and fields of amount of each species.
        
    Returns
    -------
    ABCMolecule
        ABCMolecule object with defined molecule information. 
    """

    def __init__(self,
                 unitcell: LatticeMatrix,
                 positional: bool,
                 atoms: list[ABCCoord],
                 comment_line: str = " ",
                 frozen_atoms: list[list[str]] = [[""]],
                 filetype: str = "unitcell") -> None:
        if not isinstance(unitcell, LatticeMatrix):
            raise ValueError("ABCMolecule.__init__() required argument 'unitcell' is not an instance of LatticeMatrix.") # yapf: disable
        if not isinstance(positional, bool):
            raise ValueError("ABCMolceule.__init__() required argument 'positional' is not type bool.") # yapf: disable
        if not isinstance(atoms, (list, tuple, set)):
            raise ValueError("ABCMolecule.__init__() required argument 'atoms' not iterable list.") # yapf: disable
        if len(atoms) == 0:
            raise ValueError("ABCMolecule.__init__() require argument 'atoms' contains zero elements.") # yapf: disable
        for n, item in enumerate(atoms):
            if not isinstance(item, ABCCoord):
                raise ValueError(f"ABCMolecule.__init__() index {n} of atoms is not type ABCCoord; item = {item}.") # yapf: disable
        if not isinstance(comment_line, str):
            raise ValueError("ABCMolceule.__init__() required argument 'comment_line' is not type str.") # yapf: disable
        if not isinstance(frozen_atoms, (list, tuple, set)):
            raise ValueError("ABCMolceule.__init__() required argument 'frozen_atoms' is not type list.") # yapf: disable
        if not isinstance(filetype, str):
            raise ValueError("ABCMolceule.__init__() required argument 'filetype' is not type str.") # yapf: disable
        self.unitcell = unitcell
        self.positional = positional
        self.atoms: list[ABCCoord] = atoms
        self.comment_line: str = comment_line
        self.frozen_atoms: list[list[str]] = frozen_atoms
        self.filetype: str = filetype
        self.__post_init__()

    def __post_init__(self):
        self.species_line: list[str] = list()
        self.species_amount: list[str] = list()
        _ = "PL@C3H0LD3R"
        for atom in self.atoms:
            if atom.sp == _:
                self.species_amount[-1] = str(1 + int(self.species_amount[-1]))
            else:
                self.species_line.append(atom.sp)
                self.species_amount.append("1")
                _ = atom.sp
        self.total = sum([int(num) for num in self.species_amount])
        _species_key = [
            x for i, x in enumerate(self.species_line)
            if self.species_line.index(x) == i
        ]
        self.amount_dict: dict[str, int] = {sp: 0 for sp in _species_key}
        for ele, amt in zip(self.species_line, self.species_amount):
            curr_value = self.amount_dict[ele]
            new_value = int(amt) + curr_value
            self.amount_dict[ele] = new_value

    def __str__(self) -> str:
        return f"ABCMolecule(unitcell={self.unitcell}, atoms={self.atoms}, positional={self.positional}, comment_line='{self.comment_line}', filetype='{self.filetype}')"

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, item: ABCMolecule) -> ABCMolecule:
        if isinstance(item, ABCMolecule):
            new_coords = item.atoms
        else:
            raise ValueError("ABCMolecule.__add__() can only add type ABCMolecule.") # yapf: disable
        return self.append(new_coords=new_coords,
                           positional=True if not self.positional else False)

    def __len__(self):
        return len(self.atoms)

    def __getitem__(self, index: MolIndex) -> ABCMolecule:
        if isinstance(index, (int, str)):
            index = str(index)
            if index.replace("-", "").isdecimal():
                if -len(self.atoms) <= int(index) <= -1:
                    return ABCMolecule(unitcell=self.unitcell,
                                       positional=self.positional,
                                       atoms=[self.atoms[int(index)]],
                                       comment_line=self.comment_line,
                                       filetype=self.filetype)
                elif len(self.atoms) >= int(index) >= 1:
                    return ABCMolecule(unitcell=self.unitcell,
                                       positional=self.positional,
                                       atoms=[self.atoms[int(index) - 1]],
                                       comment_line=self.comment_line,
                                       filetype=self.filetype)
                else:
                    raise IndexError(f"ABCMolecule.__getitem__() index = '{index}'; int is out of range of len(self.atoms) or is zero.") # yapf: disable
            elif index in self.species_line:
                return ABCMolecule(
                    unitcell=self.unitcell,
                    positional=self.positional,
                    atoms=[item for item in self.atoms if item.sp == index],
                    comment_line=self.comment_line,
                    filetype=self.filetype)
            else:
                return ABCMolecule(
                    unitcell=self.unitcell,
                    positional=self.positional,
                    atoms=[self.atoms[self._get_molden_index(index)]],
                    comment_line=self.comment_line,
                    filetype=self.filetype)
        elif isinstance(index, (list, tuple, set)):
            return_atoms: list[ABCCoord] = list()
            for item in [str(ele) for ele in index]:
                if item.replace("-", "").isdecimal():
                    if -len(self.atoms) <= int(item) <= -1:
                        return_atoms.append(self.atoms[int(item)])
                    elif len(self.atoms) >= int(item) >= 1:
                        return_atoms.append(self.atoms[int(item) - 1])
                    else:
                        raise IndexError(f"ABCMolecule.__getitem__() index = '{index}'; int is out of range of len(self.atoms).") # yapf: disable
                elif item in self.species_line:
                    return_atoms.extend(
                        [ele for ele in self.atoms if ele.sp == item])
                else:
                    return_atoms.append(
                        self.atoms[self._get_molden_index(item)])
            return ABCMolecule(unitcell=self.unitcell,
                               positional=self.positional,
                               atoms=return_atoms,
                               comment_line=self.comment_line,
                               filetype=self.filetype)
        else:
            raise IndexError(f"ABCMolecule.__getitem__() index = '{index}'; not valid index.") # yapf: disable

    def __setitem__(self, index: int | str, new_item: ABCCoord) -> None:
        if not isinstance(index, (int, str)):
            raise ValueError("ABCMolecule.__setitem__() index must be of type int or str.") # yapf: disable
        if not isinstance(new_item, ABCCoord):
            raise ValueError("ABCMolecule.__setitem__() Value assignment must be type XYZCoord.") # yapf: disable
        self.atoms[self.atoms.index(
            self.__getitem__(index).atoms[0])] = new_item
        self.__post_init__()

    def _format(self, filetype: str, endline: str) -> list[str]:
        """Returns formatted text for textbox or filewrite.

        Parameters
        ----------
        filetype: str
            file format wanted. {.vasp, .lammps}
        endline : str, default " "
            Endline string for each file line.

        Returns
        -------
        list[str]
            list of strings for vasp format with endline str as last character in string.
        """
        if not isinstance(endline, str):
            raise ValueError("ABCMolecule._format() optional argument 'endline' not a str.") # yapf: disable
        text: list[str] = list()
        if filetype == ".vasp":
            _len = len(str(max(self.species_amount))) + 1
            _format_species = [f"{ele:<{_len}}" for ele in self.species_line]
            _format_amount = [f"{ele:<{_len}}" for ele in self.species_amount]
            text.append(self.comment_line + endline)
            text.append(f"{self.unitcell.constant:>{La}.{Fa}f}" + endline)
            for vector in [
                    self.unitcell.vector_1, self.unitcell.vector_2,
                    self.unitcell.vector_3
            ]:
                text.append(
                    f"{vector[0]:>{La}.{Fa}f}{vector[1]:>{La}.{Fa}f}{vector[2]:>{La}.{Fa}f}"
                    + endline)
            text.append("   ".join(_format_species) + endline)
            text.append("   ".join(_format_amount) + endline)
            if self.frozen_atoms != [[""]]:
                text.append("Selective Dynamics \n")
            if self.positional:
                text.append("Direct" + endline)
            else:
                text.append("Cartesian" + endline)
            if self.frozen_atoms != [[""]]:
                for i in range(len(self.atoms)):
                    text.append(
                        f"{self.atoms[i][1]:>{La}.{Fa}f}{self.atoms[i][2]:>{La}.{Fa}f}{self.atoms[i][3]:>{La}.{Fa}f}"
                        f"{Sa}{self.frozen_atoms[i][0]}{Sa}{self.frozen_atoms[i][1]}{Sa}{self.frozen_atoms[i][2]}\n"
                    )
            else:
                for i in range(len(self.atoms)):
                    text.append(
                        f"{self.atoms[i][1]:>{La}.{Fa}f}{self.atoms[i][2]:>{La}.{Fa}f}{self.atoms[i][3]:>{La}.{Fa}f}"
                        + endline)
            return text
        elif filetype == ".lammps":
            species = [
                x for i, x in enumerate(self.species_line)
                if self.species_line.index(x) == i
            ]
            text.append("#" + self.comment_line + endline)
            text.append("" + endline)
            text.append(f"{self.total} atoms" + endline)
            text.append(f"{len(species)} atom types" + endline)
            text.append("" + endline)
            text.append("" + endline)
            car_mol = self.switch_to_cartesian()
            a_min = min([coord.a for coord in car_mol.atoms])
            b_min = min([coord.b for coord in car_mol.atoms])
            c_min = min([coord.c for coord in car_mol.atoms])
            a, b, c = car_mol.unitcell.getabc()
            a_box = (a_min, a + a_min)
            b_box = (b_min, b + b_min)
            c_box = (c_min, c + c_min)
            text.append(f"{a_box[0]:{Fl}} {a_box[1]:{Fl}} xlo xhi" + endline)
            text.append(f"{b_box[0]:{Fl}} {b_box[1]:{Fl}} ylo yhi" + endline)
            text.append(f"{c_box[0]:{Fl}} {c_box[1]:{Fl}} zlo zhi" + endline)
            text.append("" + endline)
            text.append("Masses" + endline)
            for n, sp in enumerate(species):
                text.append(f"{n+1} {MOLAR_MASS[sp]}" + endline)
            text.append("" + endline)
            text.append("Atoms" + endline)
            text.append("" + endline)
            for n, coord in enumerate(car_mol.atoms):
                text.append(
                    f"{n+1} {species.index(coord.sp)+1} 0 {coord.a:{Fl}} {coord.b:{Fl}} {coord.c:{Fl}}"
                    + endline)
            text.append("" + endline)
            return text
        elif filetype == ".qe":
            raise NotImplementedError("ABCMolecule._format() .qe is not implemented yet.") # yapf: disable
        else:
            raise ValueError("ABCMolecule._format() required argument 'filetype' is not type '.vasp'.") # yapf: disable

    def _get_molden_index(self, index: MolIndex) -> int:
        if not isinstance(index, str):
            raise IndexError(f"ABCMolecule._get_molden_index() index = '{index}'; index type not correct.") # yapf: disable
        _n1 = ""
        _a1 = ""
        for item in index[::-1]:
            if item.isdecimal():
                _n1 += item
            else:
                _a1 += item
        _n2 = _n1[::-1]
        if _n2 == "":
            raise IndexError(f"ABCMolecule._get_molden_index() index = '{index}'; no # after.") # yapf: disable
        _a2 = _a1[::-1]
        if index == _a2 + _n2:
            _n3 = int(_n2)
            if _a2 not in self.species_line:
                raise IndexError(f"ABCMolecule._get_molden_index() index = '{index}'; Sp not in self.speciesline.") # yapf: disable
            if int(self.species_amount[self.species_line.index(
                    _a2)]) >= _n3 >= 1:
                return self.atoms.index(
                    [item for item in self.atoms if item.sp == _a2][_n3 - 1])
            else:
                raise IndexError(f"ABCMolecule._get_molden_index() index = '{index}'; # is too large or zero.") # yapf: disable
        else:
            raise IndexError(f"ABCMolecule._get_molden_index() index = '{index}'; Sp# out of order.") # yapf: disable

    def add_coords(self,
                   molecule: ABCMolecule | XYZMolecule,
                   axis: str | int,
                   absorbent_reference: str | CoordType,
                   surface_reference: str | CoordType,
                   dist: float,
                   inplace: bool = False) -> ABCMolecule:
        """Add a new Molecule object to the current ABCMolecule object very precisely.

        Parameters
        ----------
        molecule : ABCMolecule or XYZMolecule
            Molecule object to add to the current ABCMolecule object.
        axis : "{0 or 'x', 1 or 'y', 2 or 'z'}"
            Placement of new molecule will be in direction of axis.
        absorbent_reference : "{'Top' or 'Centroid' or 'Origin' or 'Bottom' or CoordType}"
            Reference on argument 'molecule' where the distance is measured.
        surface_reference : "{'Top' or 'Centroid' or 'Bottom' or 'Most postive Sp' or 'Most negative Sp' or CoordType}"
            Reference on current molecule object where the distance is measured.
        dist : float
            sign of float determines what direction the new molecule is placed.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        ABCMolecule
            ABCMolecule object with new atoms added.
        """
        if isinstance(molecule, ABCMolecule):
            if molecule.positional:
                molecule = molecule.convert()
        elif isinstance(molecule, XYZMolecule):
            pass
        else:
            raise ValueError("ABCMolecule.add_coords() required argument 'molecule' not type ABCMolecule or XYZMolecule.") # yapf: disable
        if axis not in ["x", "y", "z", 0, 1, 2]:
            raise ValueError(f"XYZMolecule.add_coords() required argument 'angle' is not 'x' or 'y' or 'z' or 1 or 2 or 3.") # yapf: disable
        match axis:
            case "x":
                axis_int = 0
            case "y":
                axis_int = 1
            case "z":
                axis_int = 2
            case _:
                axis_int = int(axis)
        if not isinstance(dist, (int, float)):
            raise ValueError("ABCMolecule.add_coords() required argument 'dist' not a number.") # yapf: disable
        if not isinstance(inplace, bool):
            raise ValueError("ABCMolecule.add_coords() optional argument 'inplace' not a bool.") # yapf: disable
        # needed to not append to memory and return only changed object
        combined_atoms = copy.copy(self.atoms)
        # need convert bc operation happens in cartesian coords
        sur_centroids = self.convert().get_centroid()
        sur_mod = [sur_centroids[0], sur_centroids[1], sur_centroids[2]]
        x_import_centroid, y_import_centroid, z_import_centroid = molecule.get_centroid(
        )
        abs_centroids = [
            x_import_centroid, y_import_centroid, z_import_centroid
        ]
        x_import_list = [float(coord[1]) for coord in molecule.atoms]
        y_import_list = [float(coord[2]) for coord in molecule.atoms]
        z_import_list = [float(coord[3]) for coord in molecule.atoms]
        abs_lists = (x_import_list, y_import_list, z_import_list)
        atom_list = self.convert().atoms if self.positional else self.atoms
        x_curr_list = [float(coord[1]) for coord in atom_list]
        y_curr_list = [float(coord[2]) for coord in atom_list]
        z_curr_list = [float(coord[3]) for coord in atom_list]
        sur_lists = (x_curr_list, y_curr_list, z_curr_list)
        # finding absorbent values
        if isinstance(absorbent_reference, (ABCCoord, XYZCoord)):
            abs_mod = [0.0, 0.0, 0.0]
            abs_mod[0] = absorbent_reference[1]
            abs_mod[1] = absorbent_reference[2]
            abs_mod[2] = absorbent_reference[3]
        elif absorbent_reference == "Centroid":
            abs_mod = abs_centroids
        elif absorbent_reference in ["Top", "Bottom"]:
            abs_mod = abs_centroids
            if absorbent_reference == "Top":
                sort_func = max
            else:  # if absorbent_reference == "Bottom":
                sort_func = min
            abs_mod[axis_int] = sort_func(abs_lists[axis_int])
        elif absorbent_reference == "Origin":
            abs_mod = [0.0, 0.0, 0.0]
        else:
            raise ValueError("ABCMolecule.add_coords() required argument 'absorbent_reference' not 'Top','Centroid','Origin', or 'Bottom'.") # yapf: disable
        # finding surface values now
        if isinstance(surface_reference, (ABCCoord, XYZCoord)):
            sur_mod[0] = surface_reference[1]
            sur_mod[1] = surface_reference[2]
            sur_mod[2] = surface_reference[3]
        elif surface_reference == "Centroid":
            sur_mod = sur_centroids
        elif surface_reference == "(0.5,0.5,0.5)":
            sur_mod = [0.5, 0.5, 0.5]
        elif surface_reference in ["Top", "Bottom"]:
            if surface_reference == "Top":
                sort_func = max
            # if surface_reference == ABSORBENT_OPTIONS['starting_surface_list'][1]:
            else:
                sort_func = min
            sur_mod[axis_int] = sort_func(sur_lists[axis_int])
        elif surface_reference in ["Most positive ", "Most negative"]:
            species = surface_reference[14:]
            if "Most positive " in surface_reference:
                sort_func = max
            else:  # if "Most negative" in surface_reference:
                sort_func = min
            species_import_list = [
                float(coord[axis_int + 1]) for coord in self.atoms
                if coord.sp == species
            ]
            sur_mod[axis_int] = sort_func(species_import_list)
        elif surface_reference == "origin":  # necessary for add atom
            sur_mod = [0, 0, 0]
        else:
            raise ValueError("ABCMolecule.add_coords() required argument 'surface_reference' not 'Top','Centroid','Bottom','Most postive Sp','Most negative Sp' or CoordType.") # yapf: disable
        # math for finding displacement distanceance
        distance = [0.0, 0.0, 0.0]
        distance[axis_int] = dist
        # print(f'{sur_mod = }')
        # print(f'{abs_mod = }')
        x_mod = sur_mod[0] - abs_mod[0] + distance[0]
        y_mod = sur_mod[1] - abs_mod[1] + distance[1]
        z_mod = sur_mod[2] - abs_mod[2] + distance[2]
        a, b, c = self.unitcell.getabc()
        for ele in molecule.atoms:
            if self.positional:
                combined_atoms.append(
                    ABCCoord(ele.sp, (float(ele[1]) + x_mod) / a,
                             (float(ele[2]) + y_mod) / b,
                             (float(ele[3]) + z_mod) / c))
            else:
                combined_atoms.append(
                    ABCCoord(ele.sp,
                             float(ele[1]) + x_mod,
                             float(ele[2]) + y_mod,
                             float(ele[3]) + z_mod))
        if inplace:
            self.atoms = combined_atoms
            self.__post_init__()
        return ABCMolecule(
            unitcell=self.unitcell,
            positional=self.positional,
            atoms=combined_atoms,
            comment_line=self.comment_line,
            filetype=self.filetype,
        )

    def append(self,
               new_coords: ABCCoord | list[ABCCoord],
               positional: bool,
               inplace: bool = False) -> ABCMolecule:
        """To add coords to the current ABCMolecule.atoms attribute.

        Parameters
        ----------
        new_coords : ABCCoord or list[ABCCoord]
            List of new coords to add to new object.
        positional : bool
            True if coords are positional coordinates. False if they are cartesian coordinates.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        ABCMolecule
            ABCMolecule object with new atoms.
        """
        if not isinstance(new_coords, (list, tuple, set)):
            new_coords = [new_coords]
        for n, item in enumerate(new_coords):
            if not isinstance(item, ABCCoord):
                raise ValueError(f"ABCMolecule.__init__() index {n} of atoms is not type ABCCoord; item = {item}.") # yapf: disable
        if not isinstance(inplace, bool):
            raise ValueError("ABCMolecule.append() optional argument 'inplace' not a bool.") # yapf: disable
        if positional and not self.positional:
            converted_coords = ABCMolecule(unitcell=self.unitcell,
                                           positional=positional,
                                           atoms=new_coords).convert().atoms
            new_coords = list()
            [
                new_coords.append(ABCCoord(coord.sp, coord.x, coord.y,
                                           coord.z))
                for coord in converted_coords
            ]
        if not positional and self.positional:
            converted_coords = new_coords
            # CONVERTING CARTESIAN TO POSITIONAL COORDS
            [
                new_coords.append(
                    ABCCoord(
                        coord.sp,
                        coord.a / self.unitcell.getabc()[0],
                        coord.b / self.unitcell.getabc()[1],
                        coord.c / self.unitcell.getabc()[2],
                    )) for coord in converted_coords
            ]
        new_atoms = copy.copy(self.atoms)
        new_atoms.extend(new_coords)
        if inplace:
            self.atoms = new_atoms
            self.__post_init__()
        return ABCMolecule(
            unitcell=self.unitcell,
            positional=self.positional,
            atoms=new_atoms,
            comment_line=self.comment_line,
            filetype=self.filetype,
        )

    def convert(self, method: str = "trig") -> XYZMolecule:
        """Converts ABCMolecule to XYZMolecule.

        Parameters
        ----------
        method : str, "{'general' or 'trig' or 'linalg'}" default 'trig'
            Which method you want to use for converting ABCMolecule positional coords to, cartesian coordinates.
                'general' is the general formula.
                'trig' looks most correct and is the default.
                'linalg' is an unfinished method using linear algebra concepts.

        Returns
        -------
        XYZMolecule
            XYZMolecule object generated from converted ABCMolecule object.
        """

        def csc(x: float) -> float:
            """Return the cosecant of x (measured in radians)."""
            return 1 / sin(x)

        # def sec(x: float) -> float:
        #     """Return the secant of x (measured in radians)."""
        #     return 1 / cos(x)
        def cot(x: float) -> float:
            """Return the cotangent of x (measured in radians)."""
            return 1 / tan(x)

        if method not in ["general", "trig", "linalg"]:
            raise ValueError("ABCMolecule.convert() optional argument 'method' is not 'general','trig' or 'linalg'.") # yapf: disable
        if self.positional:
            if method == "general":
                # ====================================
                # former code using wikipedia resource....
                # =====================================
                a, b, c = self.unitcell.getabc()
                alp, bet, gam = self.unitcell.getanglesrad()
                A = np.matrix([
                    [
                        a * sin(bet) *
                        sqrt(1 - ((cot(alp)) * (cot(bet)) - (csc(alp)) *
                                  (csc(bet)) * cos(gam))**2),
                        0,
                        0,
                    ],
                    [
                        a * (csc(alp)) * cos(gam) - a * (cot(alp)) * cos(bet),
                        b * sin(alp),
                        0,
                    ],
                    [a * cos(bet), b * cos(alp), c],
                ])
                convert_atoms = list()
                for atom in self.atoms:
                    f = np.matrix([
                        [atom.a],
                        [atom.b],
                        [atom.c],
                    ])
                    r = np.dot(A, f)
                    convert_atoms.append(
                        XYZCoord(atom.sp, float(r[0]), float(r[1]),
                                 float(r[2])))
                return XYZMolecule(
                    atoms=convert_atoms,
                    comment_line=self.comment_line,
                    filetype=self.filetype,
                )
            elif method == "trig":
                # ====================================
                # created using chatgpt as a resource.
                # quote "correct" method
                # =====================================
                a, b, c = self.unitcell.getabc()
                alp, bet, gam = self.unitcell.getanglesrad()
                convert_atoms: list[XYZCoord] = list()
                for atom in self.atoms:
                    x_car = a * atom.a + b * cos(gam) * atom.b + c * cos(bet)
                    y_car = b * sin(gam) * atom.b + c * (
                        cos(alp) - cos(bet) * cos(gam)) / sin(gam) * atom.c
                    z_car = c * sqrt(1 - cos(alp)**2 - cos(bet)**2 -
                                     cos(gam)**2 + 2 * cos(alp) * cos(bet) *
                                     cos(gam)) * atom.c
                    convert_atoms.append(XYZCoord(atom.sp, x_car, y_car,
                                                  z_car))
                return XYZMolecule(
                    atoms=convert_atoms,
                    comment_line=self.comment_line,
                    filetype=self.filetype,
                )
            else:  # if method == 'linalg'
                # ==================================
                # jerry's method not fully correct
                # ==================================
                L = np.matrix([
                    self.unitcell.vector_1, self.unitcell.vector_2,
                    self.unitcell.vector_3
                ])
                Coord_matrix = np.transpose(
                    np.matrix([[atom[1], atom[2], atom[3]]
                               for atom in self.atoms]))
                transform_matrix = np.transpose(self.unitcell.constant *
                                                (L * Coord_matrix))
                convert_atoms = list()
                for n, row in enumerate(transform_matrix):
                    convert_atoms.append(
                        XYZCoord(self.atoms[n].sp, row[0, 0], row[0, 1],
                                 row[0, 2]))
                return XYZMolecule(
                    atoms=convert_atoms,
                    comment_line=self.comment_line,
                    filetype=self.filetype,
                )
        else:
            return XYZMolecule(
                atoms=[
                    XYZCoord(sp=coord.sp, x=coord.a, y=coord.b, z=coord.c)
                    for coord in self.atoms
                ],
                comment_line=self.comment_line,
                filetype=self.filetype,
            )

    def delete(self, index: MolIndex, inplace: bool = False) -> ABCMolecule:
        """Delete INDEXED atoms in ABCMolecule.

        Parameters
        ----------
        index : MolIndex
            MolIndex can be a list of strings or integers or a single string or int 
            that is either an atom number, species+species number (Molden style), or species.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        ABCMolecule
            ABCMolecule object with selected atoms deleted.
        """
        if not isinstance(inplace, bool):
            raise ValueError("ABCMolecule.delete() optional argument 'inplace' not a bool.") # yapf: disable
        saving_atoms: list[ABCCoord] = list()
        del_ints: list[int] = list()
        if type(index) != list:
            index = [index]  # type: ignore
        for item in index:  # type: ignore
            for ele in self[item].atoms:
                del_ints.append(self.atoms.index(ele))
        saving_atoms = [
            self.atoms[i] for i in range(len(self.atoms)) if not i in del_ints
        ]
        if inplace:
            self.atoms = saving_atoms
            self.__post_init__()
        return ABCMolecule(
            unitcell=self.unitcell,
            positional=self.positional,
            atoms=saving_atoms,
            comment_line=self.comment_line,
            filetype=self.filetype,
        )

    def edit_unitcell(self, new_unitcell: LatticeMatrix, method: str = "positional", inplace: bool = False, debug_print: bool = False) -> ABCMolecule:
        """Edit LatticeMatrix of current ABCMolecule object.

        Parameters
        ----------
        new_unitcell : LatticeMatrix
            A LatticeMatrix object containing the new coordinates. Cartesian coordinates must not extend a, b, or c unitcell lengths.
        method : str, default 'positional'
            method to change unitcell. 'positional' will take a rectangular unitcell and change the positional coordinates.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        ABCMolecule
            ABCMolecule object with unitcell edited.
        """
        if not isinstance(new_unitcell, LatticeMatrix):
            raise ValueError("ABCMolecule.edit_unitcell() required argument 'new_unitcell' not type LatticeMatrix.") # yapf: disable
        if method not in ["positional"]:
            raise ValueError("ABCMolecule.edit_unitcell() optional argument 'method' is not 'positional'.") # yapf: disable
        if not isinstance(inplace, bool):
            raise ValueError("ABCMolecule.edit_unitcell() optional argument 'inplace' not a bool.") # yapf: disable
        
        if not _is_ae([self.unitcell.constant, 1.0], 1e-4):
            raise ValueError("ABCMolecule.edit_unitcell() cannot execute due to self.unitcell.constant not being equal to 1.")
        
        if not _is_ae([new_unitcell.constant, 1.0], 1e-4):
            raise ValueError("ABCMolecule.edit_unitcell() cannot execute due to new_unitcell.constant not being equal to 1.")

        old_alpha, old_beta, old_gamma = self.unitcell.getanglesdeg()
        if not _is_ae([old_alpha, 90.0], 1e-4):
            raise ValueError("ABCMolecule.edit_unitcell() cannot execute due to self.unitcell containing angle X which is not 90.0°.") # yapf: disable
        if not _is_ae([old_beta, 90.0], 1e-4):
            raise ValueError("ABCMolecule.edit_unitcell() cannot execute due to self.unitcell containing angle X which is not 90.0°.") # yapf: disable
        if not _is_ae([old_gamma, 90.0], 1e-4):
            raise ValueError("ABCMolecule.edit_unitcell() cannot execute due to self.unitcell containing angle X which is not 90.0°.") # yapf: disable
        
        new_alpha, new_beta, new_gamma = new_unitcell.getanglesdeg()
        if not _is_ae([new_alpha, 90.0], 1e-4):
            raise ValueError("ABCMolecule.edit_unitcell() cannot execute due to required argument 'new_unitcell' containing angle X which is not 90.0°.") # yapf: disable
        if not _is_ae([new_beta, 90.0], 1e-4):
            raise ValueError("ABCMolecule.edit_unitcell() cannot execute due to required argument 'new_unitcell' containing angle X which is not 90.0°.") # yapf: disable
        if not _is_ae([new_gamma, 90.0], 1e-4):
            raise ValueError("ABCMolecule.edit_unitcell() cannot execute due to required argument 'new_unitcell' containing angle X which is not 90.0°.") # yapf: disable
        #do I need these below. probably not...
        if _is_ae([new_unitcell.vector_1[0], 0.0], 1e-4) or new_unitcell.vector_1[0] <= 0.0:
            raise ValueError("ABCMolecule.edit_unitcell() required argument 'new_unitcell' attribute 'vector_1' index 0 contains a non positive number.") # yapf: disable
        for i in [1, 2]:
            if not _is_ae([new_unitcell.vector_1[i], 0.0], 1e-4):
                raise ValueError(f"ABCMolecule.edit_unitcell() required argument 'new_unitcell' attribute 'vector_1' index {i} is not equal to zero.") # yapf: disable
        if _is_ae([new_unitcell.vector_2[1], 0.0], 1e-4) or new_unitcell.vector_2[1] <= 0.0:
            raise ValueError("ABCMolecule.edit_unitcell() required argument 'new_unitcell' attribute 'vector_2' index 1 contains a non positive number.") # yapf: disable
        for i in [0, 2]:
            if not _is_ae([new_unitcell.vector_2[i], 0.0], 1e-4):
                raise ValueError(f"ABCMolecule.edit_unitcell() required argument 'new_unitcell' attribute 'vector_2' index {i} is not equal to zero.") # yapf: disable
        if _is_ae([new_unitcell.vector_3[2], 0.0], 1e-4) or new_unitcell.vector_3[2] <= 0.0:
            raise ValueError("ABCMolecule.edit_unitcell() required argument 'new_unitcell' attribute 'vector_3' index 2 contains a non positive number.") # yapf: disable
        for i in [0, 1]:
            if not _is_ae([new_unitcell.vector_3[i], 0.0], 1e-4):
                raise ValueError(f"ABCMolecule.edit_unitcell() required argument 'new_unitcell' attribute 'vector_3' index {i} is not equal to zero.") # yapf: disable

        if _is_ae([self.unitcell.vector_1[0], 0.0], 1e-4) or self.unitcell.vector_1[0] <= 0.0:
            raise ValueError("ABCMolecule.edit_unitcell() Current ABCMolecule attribute 'self.unitcell' contains attribute 'vector_1' index 0 which contains a non positive number.") # yapf: disable
        for i in [1, 2]:
            if not _is_ae([self.unitcell.vector_1[i], 0.0], 1e-4):
                raise ValueError(f"ABCMolecule.edit_unitcell() Current ABCMolecule attribute 'self.unitcell' contains attribute 'vector_1' index {i} is not equal to zero.") # yapf: disable
        if _is_ae([self.unitcell.vector_2[1], 0.0], 1e-4) or self.unitcell.vector_2[1] <= 0.0:
            raise ValueError("ABCMolecule.edit_unitcell() Current ABCMolecule attribute 'self.unitcell' contains attribute 'vector_2' index 1 which contains a non positive number.") # yapf: disable
        for i in [0, 2]:
            if not _is_ae([self.unitcell.vector_2[i], 0.0], 1e-4):
                raise ValueError(f"ABCMolecule.edit_unitcell() Current ABCMolecule attribute 'self.unitcell' contains attribute 'vector_2' index {i} is not equal to zero.") # yapf: disable
        if _is_ae([self.unitcell.vector_3[2], 0.0], 1e-4) or self.unitcell.vector_3[2] <= 0.0:
            raise ValueError("ABCMolecule.edit_unitcell() Current ABCMolecule attribute 'self.unitcell' contains attribute 'vector_3' index 2 which contains a non positive number.") # yapf: disable
        for i in [0, 1]:
            if not _is_ae([self.unitcell.vector_3[i], 0.0], 1e-4):
                raise ValueError(f"ABCMolecule.edit_unitcell() Current ABCMolecule attribute 'self.unitcell' contains attribute 'vector_3' index {i} is not equal to zero.") # yapf: disable
        #warning to ensure the functon works correctly
        if self.unitcell == new_unitcell:
            raise Exception("ABCMolecule.edit_unitcell() Warning: self.unitcell is equal to required argument 'new_unitcell'. Ensure you create a new LatticeMatrix object. New ABCMolecule instance will be a copy of self. For some unkown reason to developer, this will not work using the current equations.") # yapf: disable
        
        
        old_a, old_b, old_c = self.unitcell.getabc()
        new_a, new_b, new_c = new_unitcell.getabc()
        converted_atoms: list[ABCCoord] = list()
        if debug_print:
            print(f"{old_a =} {old_b =} {old_c =}")
            print(f"{new_a =} {new_b =} {new_c =}")

        for atom in self.atoms:
            coord_a = atom.a*(old_a/new_a) #works
            if coord_a < 0 or coord_a > 1:
                raise Exception("ABCMolecule.edit_unitcell() error occured where 'a' coordinate is negative or greater than 1.") # yapf: disable
            coord_b = atom.b*(old_b/new_b)
            if coord_b < 0 or coord_b > 1:
                raise Exception("ABCMolecule.edit_unitcell() error occured where 'b' coordinate is negative or greater than 1.") # yapf: disable
            coord_c = atom.c*(old_c/new_c)
            if coord_c < 0 or coord_c > 1:
                raise Exception("ABCMolecule.edit_unitcell() error occured where 'c' coordinate is negative or greater than 1.") # yapf: disable
            converted_atoms.append(ABCCoord(sp=atom.sp, a=coord_a, b=coord_b, c=coord_c))
        
        if inplace:
            self.unitcell = new_unitcell
            self.atoms = converted_atoms
            self.__post_init__()
        return ABCMolecule(
            unitcell=new_unitcell,
            positional=self.positional,
            atoms=converted_atoms,
            comment_line=self.comment_line,
            filetype=self.filetype,
        )


    def freeze_atoms(self,
                     index: MolIndex,
                     freeze_indexed: bool,
                     inplace: bool = False) -> ABCMolecule:
        """Method that generates ABCMolecule.freeze_atoms for VASP based on indexed atoms.

        Parameters
        ----------
        index : MolIndex
            MolIndex can be a list of strings or integers or a single string or int 
            that is either an atom number, species+species number (Molden style), or species.
        freeze_indexed : bool
            If True, the indexed atoms will be frozen, and non indexed atoms will be not frozen.
            If False, operation is vise versa.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        ABCMolecule
            ABCMolecule with freeze_atoms list generated based on method arguments.
        """
        if not isinstance(freeze_indexed, bool):
            raise ValueError("ABCMolecule.freeze_atoms() required argument 'freeze_indexed' not a bool.") # yapf: disable
        if not isinstance(inplace, bool):
            raise ValueError("ABCMolecule.freeze_atoms() optional argument 'inplace' not a bool.") # yapf: disable
        try:
            indexed_mol = self[index]
            false_atoms: list[ABCCoord] = list()
            true_atoms: list[ABCCoord] = list()
            for coord in self.atoms:
                if coord in indexed_mol.atoms:
                    false_atoms.append(
                        coord) if freeze_indexed else true_atoms.append(coord)
                else:
                    true_atoms.append(
                        coord) if freeze_indexed else false_atoms.append(coord)
        except:
            false_atoms = self.atoms if freeze_indexed else []
            true_atoms = [] if freeze_indexed else self.atoms

        frozen_atoms: list[list[str]] = []
        for coord in self.atoms:
            if coord in false_atoms:
                frozen_atoms.append(["F", "F", "F"])
            elif coord in true_atoms:
                frozen_atoms.append(["T", "T", "T"])
            else:
                raise RuntimeError("ABCMolecule.freeze_atoms() runtime error. coord not in false_atoms or true_atoms.") # yapf: disable
        if inplace:
            self.frozen_atoms = frozen_atoms
        return ABCMolecule(
            unitcell=self.unitcell,
            positional=self.positional,
            atoms=self.atoms,
            comment_line=self.comment_line,
            frozen_atoms=frozen_atoms,
            filetype=self.filetype,
        )

    def generate_supercell(self,
                           x: int,
                           y: int,
                           z: int,
                           inplace: bool = False) -> ABCMolecule:
        """Method returns a supercell of the structure.

        Parameters
        ----------
        x : int >= 1
            Amount in the x direction the structure will be multiplied by.
        y : int >= 1
            Amount in the y direction the structure will be multiplied by.
        z : int >= 1
            Amount in the z direction the structure will be multiplied by.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        ABCMolecule
            ABCMolecule object of generated supercell.
        """
        # NOT SURE I NEED THIS ERROR CHECKING
        # for n, vector in enumerate([
        #         self.unitcell.vector_1, self.unitcell.vector_2,
        #         self.unitcell.vector_3
        # ]):
        #     if not _is_ae([vector[n], 0], tolerance_percentage=5):
        #         raise ValueError("ABCMolecule.generate_supercell() vector that is supposed to be nonzero is zero...") # yapf: disable
        #     for i in range(3):
        #         if i != n:
        #             if _is_ae([vector[i], 0], tolerance_percentage=1):
        #                 raise ValueError("ABCMolecule.generate_supercell() vector that is supposed to be zero is nonzero...") # yapf: disable

        ####OLD METHODS CONVERTING USING XYZ
        # xyz_mol = self.convert()
        # xyz_mol.generate_supercell(x=x, y=y, z=z, inplace=True)
        # abc_mol = xyz_mol.convert(
        #     lattice_matrix=LatticeMatrix(constant=1,
        #                                  vector_1=[ele * x for ele in self.unitcell.vector_1],
        #                                  vector_2=[ele * y for ele in self.unitcell.vector_2],
        #                                  vector_3=[ele * z for ele in self.unitcell.vector_3]))
        # if inplace:
        #     self.unitcell = LatticeMatrix(constant=1,
        #                                  vector_1=[ele * x for ele in self.unitcell.vector_1],
        #                                  vector_2=[ele * y for ele in self.unitcell.vector_2],
        #                                  vector_3=[ele * z for ele in self.unitcell.vector_3])
        #     self.atoms = abc_mol.atoms
        #     self.__post_init__()
        # return abc_mol
        if not isinstance(x, int):
            raise ValueError("ABCMolecule.generate_supercell() required argument 'x' not a positive int.") # yapf: disable
        if not isinstance(y, int):
            raise ValueError("ABCMolecule.generate_supercell() required argument 'y' not a positive int.") # yapf: disable
        if not isinstance(z, int):
            raise ValueError("ABCMolecule.generate_supercell() required argument 'z' not a positive int.") # yapf: disable
        if x <= 0 or y <= 0 or z <= 0:
            raise ValueError("ABCMolecule.generate_supercell() x or y or z cannot be input of zero or negative.") # yapf: disable
        if not isinstance(inplace, bool):
            raise ValueError("ABCMolecule.generate_supercell() optional argument 'inplace' not a bool.") # yapf: disable
        a,b,c = self.unitcell.getabc()
        x_mol = copy.deepcopy(self.convert())
        y_mol = copy.deepcopy(self.convert())
        z_mol = copy.deepcopy(self.convert())
        x_atoms = copy.deepcopy(self.convert().atoms)
        for _ in range(1, x):
            x_mol.move(x=a,y=0,z=0,inplace=True)
            x_atoms.extend(x_mol.atoms)
        y_mol = XYZMolecule(atoms=x_atoms)
        y_atoms = copy.deepcopy(y_mol.atoms)
        for _ in range(1, y):
            y_mol.move(x=0,y=b,z=0,inplace=True)
            y_atoms.extend(y_mol.atoms)
        z_mol = XYZMolecule(atoms=y_atoms)
        z_atoms = copy.deepcopy(z_mol.atoms)
        for _ in range(1, z):
            z_mol.move(x=0,y=0,z=c,inplace=True)
            z_atoms.extend(z_mol.atoms)
        big_unitcell = LatticeMatrix(
            constant=1,
            vector_1=[ele*x for ele in self.unitcell.vector_1],
            vector_2=[ele*x for ele in self.unitcell.vector_2],
            vector_3=[ele*x for ele in self.unitcell.vector_3])
        if self.positional:
            abc_atoms = [ABCCoord(coord.sp,
                                  coord.x/big_unitcell.vector_1[0],
                                  coord.y/big_unitcell.vector_2[1],
                                  coord.z/big_unitcell.vector_3[2]) for coord in z_atoms]
        else:
            abc_atoms = [ABCCoord(coord.sp, coord.x, coord.y, coord.z) for coord in z_atoms]
        # mol = XYZMolecule(atoms=z_atoms).convert(lattice_matrix=big_unitcell,positional=False) #NOT NEEDED
        if inplace:
            self.atoms = abc_atoms
            self.unitcell = big_unitcell
            self.__post_init__()
        return ABCMolecule(unitcell=big_unitcell, positional=self.positional, atoms=abc_atoms)

    def generate_cluster(self, normal_axis: str | int, radius: int | float, side_amount: int,  origin : CoordType = XYZCoord("X", 0, 0, 0), angle: float = 0.0, unit: str = "deg") -> XYZMolecule:
        """Generates a cluster model with a polygon cut out of n sides from an ABCMolecule Slab model.

        Parameters
        ----------
        normal_axis : "{0 or 'x', 1 or 'y', 2 or 'z'}"
            Axis normal to the plane that is being cut with the polygon.
        radius : int | float
            Radius of the polygon to be cut.
        side_amount : int {0 or >=3}
            n amount of sides for the polygon. 0 is for circle and 3 is for triangle, 4 for square, 5 for pentagon etc...
        origin : CoordType, default XYZCoord("X", 0, 0, 0)
            Supply if you want to move the slab surface to cut in a seperate spot.
        angle : float, default 0.0
            Angle you want to rotate the polygon by.
        unit : "deg" or "rad", default "deg"
            Unit of angle argument.

        Returns
        -------
        XYZMolecule
            XYZMolecule instance with atoms deleted outside of the polygon boundaries.

        """
        return self.convert().generate_cluster(normal_axis=normal_axis, radius=radius, side_amount=side_amount,  origin=origin, angle=angle, unit=unit,  inplace=False)

    def get(self, index: str | int) -> ABCCoord:
        """Get an ABCCoord indexed

        Parameters
        ----------
        index : str | int
            Either atom number, or species+species number (Molden style),

        Returns
        -------
        ABCCoord
            Indexed ABCCoord from ABCMolecule.atoms .
        """
        mol = self.__getitem__(index)
        if len(mol.atoms) == 1:
            return mol.atoms[0]
        else:
            raise ValueError("ABCMolecule.get() index was a list or species. Use ABCMolecule.get_atoms() to return list of atoms.") # yapf: disable

    def get_atoms(self, index: MolIndex) -> list[ABCCoord]:
        """Get an ABCCoord indexed

        Parameters
        ----------
        index : MolIndex
            MolIndex can be a list of strings or integers or a single string or int 
            that is either an atom number, species+species number (Molden style), or species.

        Returns
        -------
        list[ABCCoord]
            Returns list of indexed atoms from ABCMolecule.atoms .
        """
        return self.__getitem__(index).atoms

    def get_centroid(self) -> tuple[float, float, float]:
        """Returns 3d centroid of ABCMolecule atoms.

        Returns
        -------
        tuple[float,float,float]
            Tuple of (x_centroid,y_centroid,z_centroid) in Angstroms.
        """
        x_list = [coord.a for coord in self.atoms]
        y_list = [coord.b for coord in self.atoms]
        z_list = [coord.c for coord in self.atoms]
        x_centroid = sum(x_list) / len(x_list)
        y_centroid = sum(y_list) / len(y_list)
        z_centroid = sum(z_list) / len(z_list)
        return (x_centroid, y_centroid, z_centroid)

    def head(self, n: int = 10, filetype: str | None = None) -> None:
        """Prints the first n rows.
        
        Parameters
        ----------
        n: int, default 10
            Amount of filelines to select.
        filetype: str {'.vasp', '.lammps'} Default is self.filetype.
            Format of the printed file.
            
        Returns
        -------
            Method prints first n rows of filetype to terminal.
        """
        if not isinstance(n, int):
            raise ValueError("XYZMolecule.head() optional argument 'n' not a int.") # yapf: disable
        if filetype == None:
            format_type = self.filetype
        else:
            format_type = filetype
        for line in self._format(endline=" ", filetype=format_type)[:n]:
            print(line)

    def info(self) -> None:
        """Prints ABCMolecule current attribute information to terminal."""
        species_key = [
            x for i, x in enumerate(self.species_line)
            if self.species_line.index(x) == i
        ]
        amount_dict = {sp: "0" for sp in species_key}
        for ele, amt in zip(self.species_line, self.species_amount):
            curr_value = amount_dict[ele]
            new_value = int(amt) + int(curr_value)
            amount_dict[ele] = str(new_value)
        print(f"type: ABCMolecule\nfiletype: {self.filetype}\ntotal atoms: {self.total}\nspecies info: {amount_dict}\ncomment line: '{self.comment_line}'\nlattice constant: {self.unitcell.constant}\nlattice matrix:\n{self.unitcell.vector_1}\n{self.unitcell.vector_2}\n{self.unitcell.vector_3}\npositional: {self.positional}\n") # yapf: disable

    def manipulate(self, index: MolIndex, func: str, inplace: bool = False, *args, **kwargs) -> ABCMolecule:
        """Rotate or move only INDEXED atoms in ABCMolecule.

        Parameters
        ----------
        index : MolIndex
            MolIndex can be a list of strings or integers or a single string or int 
            that is either an atom number, species+species number (Molden style), or species.
        func : "{'move' or 'rotate'}"
            ABCMolecule method you want to execute on the indexed atoms.
        inplace : bool, default False
            If True, perform operation in-place.
        *args,**kwargs
            Arguments of the chosen function 'move' or 'rotate'.

        Returns
        -------
        ABCMolecule
            ABCMolecule with selected atoms moved or rotated.
        """
        if not isinstance(inplace, bool):
            raise ValueError("ABCMolecule.manipulate() optional argument 'inplace' not a bool.") # yapf: disable
        i_list: list[int] = list()
        moving_atoms: list[ABCCoord] = list()
        if not isinstance(index, (list, tuple)):
            index = [index]  # type: ignore
        for item in index:  # type: ignore
            for ele in self[item].atoms:
                i_list.append(self.atoms.index(ele))
                moving_atoms.append(ele)
        moving_mol = ABCMolecule(unitcell=self.unitcell,
                                 atoms=moving_atoms,
                                 positional=self.positional)
        if func == "move":
            new_mol = moving_mol.move(inplace=inplace, *args, **kwargs)
        elif func == "rotate":
            new_mol = moving_mol.rotate(inplace=inplace, *args, **kwargs)
        else:
            raise ValueError("ABCMolecule.manipulate() required argument 'func' not 'move' or 'rotate'.") # yapf: disable
        new_atoms = self.atoms
        for n, coord in zip(i_list, new_mol.atoms):
            new_atoms[n] = coord
        return ABCMolecule(
            unitcell=self.unitcell,
            positional=self.positional,
            atoms=new_atoms,
            comment_line=self.comment_line,
            filetype=self.filetype,
        )

    def move(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, inplace: bool = False) -> ABCMolecule:
        """Move atoms in designated directions.

        Parameters
        ----------
        x : float, default 0.0
            Move coord in x direction by float amount.
        y : float, default 0.0
            Move coord in y direction by float amount.
        z : float, default 0.0
            Move coord in z direction by float amount.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        ABCMolecule
            ABCMolecule object with all atoms moved.

        """
        if not isinstance(x, (int, float)):
            raise ValueError(f"ABCMolecule.move() optional argument 'x' is not a number.") # yapf: disable
        if not isinstance(y, (int, float)):
            raise ValueError(f"ABCMolecule.move() optional argument 'y' is not a number.") # yapf: disable
        if not isinstance(z, (int, float)):
            raise ValueError(f"ABCMolecule.move() optional argument 'z' is not a number.") # yapf: disable
        if not isinstance(inplace, bool):
            raise ValueError("ABCMolecule.move() optional argument 'inplace' is not a bool.") # yapf: disable
        return_atoms: list[ABCCoord] = list()
        for coord in self.atoms:
            sp = coord.sp
            x_old = coord.a
            y_old = coord.b
            z_old = coord.c
            return_atoms.append(
                ABCCoord(sp=sp, a=x_old + x, b=y_old + y, c=z_old + z))
        if inplace:
            self.atoms = return_atoms
            self.__post_init__()
        return ABCMolecule(
            unitcell=self.unitcell,
            positional=self.positional,
            atoms=return_atoms,
            comment_line=self.comment_line,
            filetype=self.filetype,
        )

    def print(self, filetype: str | None = None) -> None:
        """Prints ALL rows of file to terminal.
        
        Parameters
        ----------
        filetype: str {'.vasp', '.lammps'} Default is self.filetype.
            Format of the printed file.
            
        Returns
        -------
            Method prints ALL rows of filetype to terminal.
        """
        if filetype == None:
            format_type = self.filetype
        else:
            format_type = filetype
        for line in self._format(endline=" ", filetype=format_type):
            print(line)

    def rotate(self, axis: str | int, angle: float, unit: str = "deg", about_centroid: bool = True, inplace: bool = False) -> ABCMolecule:
        """Rotate ALL atoms about designated axis.

        Parameters
        ----------
        axis : "{0 or 'x', 1 or 'y', 2 or 'z'}"
            Parallel axis of rotation.
        angle : float
            Angle of rotation.
        unit : "deg" or "rad", default "deg"
            Unit of angle argument.
        about_centroid : bool, default True
            If True, rotation occurs about the centroid.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        ABCMolecule
            ABCMolecule with all atoms rotated.
        """
        if not isinstance(inplace, bool):
            raise ValueError("ABCMolecule.replace() optional argument 'inplace' not a bool.") # yapf: disable
        rotate_mol = self.convert()
        rotate_mol.rotate(axis=axis,
                          angle=angle,
                          unit=unit,
                          about_centroid=about_centroid,
                          inplace=True)
        convert_mol = rotate_mol.convert(lattice_matrix=self.unitcell,
                                         positional=self.positional)
        convert_mol.comment_line = self.comment_line
        if inplace:
            self.atoms = convert_mol.atoms
            self.__post_init__()
        return convert_mol

    def sort(self, sort_method: str | list[str] | list[list[str]], ascending: bool | list[bool] = True, inplace: bool = False) -> ABCMolecule:
        """Sort the atoms by position, species, alphabetical or atomic number.

        Parameters
        ----------
        sort_method : str | list[str] | list[list[str]]
            Method given by which the atoms will be sorted.\n
                - if sort_method is 'x' the atoms will be sorted by their x coordinate.
                - if sort_method is 'y' the atoms will be sorted by their y coordinate.
                - if sort_method is 'z' the atoms will be sorted by their z coordinate.
                - if sort_method is 'alphabetical' the atoms will be sorted in alphabetical order by their species.
                - if sort_method is 'periodical' the atoms will be sorted by their atomic number.
            You can also supply a list of lists with position 0 being species and position 1 being 'x','y','z', or None.\n
                This will sort the coordinates by species then by the method provided for each species,
                you can also add a list of bool for ascending values that will correspond to each species chosen method.\n
            You can also supply a list of species and it will be reordered to the given order.
        ascending : bool or list of bool, default True
            Sort ascending vs. descending. Specify list for multiple sort orders (as described above). If this is a list of bools, must match the length of sort_method.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        ABCMolecule
            ABCMolecule object with all atoms resorted.
        """
        if not isinstance(inplace, bool):
            raise ValueError("ABCMolecule.sort() optional argument 'inplace' is not type bool.") # yapf: disable
        if isinstance(sort_method, str):
            if sort_method not in ["x", "y", "z", "alphabetical", "periodical", "None", None]:
                raise ValueError("ABCMolecule.sort() required argument 'sort_method' is not one of 'x','y','z','alphabetical','periodical'.") # yapf: disable
            # making individual string so it can work in for loop enumerate below
            sort_method = [sort_method]
        elif isinstance(sort_method, (list, tuple, set)):
            # if len(sort_method) != len(self.species_line):
            if len(sort_method) != len(set(self.species_line)): #need set to resort and regroup atoms if same species multiple times in species line
                raise ValueError("ABCMolecule.sort() required argument 'sort_method' not the same length of amount of species in ABCMolecule.") # yapf: disable
            for item in sort_method:
                if isinstance(item, str):
                    item = [item]
                if not isinstance(item, (list, tuple, set)):
                    raise ValueError("ABCMolecule.sort() required argument 'sort_method' list item not correct type.") # yapf: disable
                if len(item) == 1:
                    if item[0] not in self.species_line:
                        raise ValueError("ABCMolecule.sort() required argument 'sort_method' list item position 0 not species in self.species_line (len(item)=1).") # yapf: disable
                elif len(item) == 2:
                    if item[0] not in self.species_line:
                        raise ValueError("ABCMolecule.sort() required argument 'sort_method' list item position 0 not species in self.species_line.") # yapf: disable
                    if item[1] not in ["x", "y", "z", "None", None]:
                        raise ValueError("ABCMolecule.sort() required argument 'sort_method' list item position 1 is not one of type 'x','y','z','None',None (len(item)=2).") # yapf: disable
                else:
                    raise ValueError("ABCMolecule.sort() required argument 'sort_method' list item length > 2.") # yapf: disable
        else:
            raise ValueError("ABCMolecule.sort() required argument 'sort_method' not correct types.") # yapf: disable
        if isinstance(ascending,(list, tuple, set)):
            if not isinstance(sort_method, (list, tuple, set)):
                raise ValueError("ABCMolecule.sort() ascending is type list but sortmethod is not type list.") # yapf: disable
            if len(sort_method) != len(ascending):
                raise ValueError("ABCMolecule.sort() length of ascending list not equivalent to length of sort method.") # yapf: disable
            if not all([isinstance(item, bool) for item in ascending]):
                raise ValueError("ABCMolecule.sort() ascending list[bool] not all bool type.") # yapf: disable
        elif not isinstance(ascending, bool):
            raise ValueError("ABCMolecule.sort() ascending bool type not bool type.") # yapf: disable
        return_atoms: list[ABCCoord] = list()
        for n, item in enumerate(sort_method):
            if isinstance(ascending, bool):
                reverse_bool = False if ascending else True
            elif isinstance(ascending, (list, tuple, set)) and len(ascending) == 1:
                reverse_bool = False if ascending[0] else True
            elif len(ascending) == len(sort_method):
                reverse_bool = False if ascending[n] else True
            else:
                raise ValueError("ABCMolecule.sort() ascending argument is wrong.") # yapf: disable
            if isinstance(item, (list, tuple, set)):
                if len(item) == 1:
                    tobesorted = self.atoms  # for string
                    method = item[0]
                elif item[0] in self.species_line:
                    tobesorted = self[item[0]].atoms
                    method = item[1]
                else:
                    raise ValueError("ABCMolecule.sort() required argument 'sort_method' is not correct.") # yapf: disable
            else:  #if isinstance(item, str):
                if item in self.species_line:
                    tobesorted = self[item].atoms
                    method = "None"
                elif item in ["x", "y", "z", "alphabetical", "periodical", "None",None]:
                    # raise ValueError("ABCMolecule.sort() required argument 'sort_method' list species index 1 is not one of 'x','y','z','alphabetical','periodical','None',None.") # yapf: disable
                    method = item
                    tobesorted = self.atoms
                else:
                    raise ValueError("ABCMolecule.sort() required argument 'sort_method' list species does not contain species.") # yapf: disable
            if method == "x":
                return_atoms.extend(sorted(tobesorted, key=lambda x: x[1], reverse=reverse_bool))
            elif method == "y":
                return_atoms.extend(sorted(tobesorted, key=lambda x: x[2], reverse=reverse_bool))
            elif method == "z":
                return_atoms.extend(sorted(tobesorted, key=lambda x: x[3], reverse=reverse_bool))
            elif method == "alphabetical":
                return_atoms.extend(sorted(tobesorted, key=lambda x: x.sp, reverse=reverse_bool))
            elif method == "periodical":
                return_atoms.extend(sorted(tobesorted, key=lambda x: ACCEPTED_ELEMENTS.index(x.sp), reverse=reverse_bool))
            else:
                return_atoms.extend(tobesorted)
        if inplace:
            self.atoms = return_atoms
            self.__post_init__()
        return ABCMolecule(
            unitcell=self.unitcell,
            positional=self.positional,
            atoms=return_atoms,
            comment_line=self.comment_line,
            filetype=self.filetype,
        )

    def switch_to_cartesian(self, inplace: bool = False) -> ABCMolecule:
        """Converts ABCMolecule coordinates to cartesian coordinates.

        Parameters
        ----------
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        ABCMolecule
            Returns ABCMolecule object with cartesian coordinates.
        """
        if not isinstance(inplace, bool):
            raise ValueError("ABCMolecule.switch_to_cartesian() optional argument 'inplace' not a bool.") # yapf: disable
        if not self.positional:
            return self
        car_atoms: list[ABCCoord] = list()
        conv_atoms = self.convert().atoms
        for atom in conv_atoms:
            car_atoms.append(ABCCoord(sp=atom.sp,
                                      a=atom.x,
                                      b=atom.y,
                                      c=atom.z))
        if inplace:
            self.atoms = car_atoms
            self.positional = False
            self.__post_init__()
        return ABCMolecule(unitcell=self.unitcell,positional=False,atoms=car_atoms,comment_line=self.comment_line,frozen_atoms=self.frozen_atoms,filetype=self.filetype)

    def switch_to_direct(self, inplace: bool = False) -> ABCMolecule:
        """Converts ABCMolecule coordinates to direct coordinates.

        Parameters
        ----------
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        ABCMolecule
            Returns ABCMolecule object with direct coordinates.
        """
        if not isinstance(inplace, bool):
            raise ValueError("ABCMolecule.direct() optional argument 'inplace' not a bool.") # yapf: disable
        if self.positional:
            return self
        alp, bet, gam = self.unitcell.getanglesdeg()
        if _is_ae([alp,90],1) is False or _is_ae([bet,90],1) is False or _is_ae([gam,90],1) is False :
            raise Exception("ABCMolecule.switch_to_direct() unitcell is not a trigonal unitcell.") # yapf: disable
        direct_atoms: list[ABCCoord] = list()
        a, b, c = self.unitcell.getabc()
        for atom in self.atoms:
            direct_atoms.append(ABCCoord(sp=atom.sp,
                                         a=atom.a/a,
                                         b=atom.b/b,
                                         c=atom.c/c))
        if inplace:
            self.atoms = direct_atoms
            self.positional = True
            self.__post_init__()
        return ABCMolecule(unitcell=self.unitcell,positional=True,atoms=direct_atoms,comment_line=self.comment_line,frozen_atoms=self.frozen_atoms,filetype=self.filetype)

    def tail(self, n: int = 10, filetype: str | None = None) -> None:
        """Prints the last n rows.
        
        Parameters
        ----------
        n: int, default 10
            Amount of filelines to select.
        filetype: str {'.vasp', '.lammps'} Default is self.filetype.
            Format of the printed file.
            
        Returns
        -------
            Method prints last n rows of filetype to terminal.
        """
        if not isinstance(n, int):
            raise ValueError("XYZMolecule.tail() optional argument 'amount' not a int.") # yapf: disable
        if filetype == None:
            format_type = self.filetype
        else:
            format_type = filetype
        for line in self._format(endline=" ", filetype=format_type)[-n:]:
            print(line)

    def to_lammps(self, filename: str) -> None:
        """Write ABCMolecule object to .lammps file.

        Parameters
        ----------
        filename : str
            Name of .lammps file that will be created.

        Returns
        -------
            .lammps file containing ABCMolecule object.
        """
        if not isinstance(filename, str):
            raise ValueError("ABCMolecule.to_vasp() required argument 'filename' is not type str.") # yapf: disable
        with open(os.path.join(os.getcwd(), filename), "w") as openfile:
            for line in self._format(endline="\n",filetype=".vasp"):
                openfile.writelines(line)

    def to_orca(self, filename: str) -> None:
        """Write XYZMolecule object to .orca file.

        Parameters
        ----------
        filename : str
            Name of .orca file that will be created.

        Returns
        -------
            .orca file containing XYZMolecule object.
        """
        if not isinstance(filename, str):
            raise ValueError("ABCMolecule.to_orca() required argument 'filename' is not type str.") # yapf: disable
        self.convert().to_orca(filename=filename)

    def to_qe(self, filename: str, cartesian: bool | None = None) -> None:
        """Write ABCMolecule object to .qe file.

        Parameters
        ----------
        filename : str
            Name of .xyz file that will be created.
        cartesian : bool | None, optional
            If True, .qe file will contain cartesian coordinates.
            If False, .qe file will contain direct coordinates.
            If not provided, .qe file will default to self.positional coordinates.

        Returns
        -------
            .qe file containing ABCMolecule object.
        """
        if not isinstance(filename, str):
            raise ValueError("ABCMolecule.to_qe() required argument 'filename' is not type str.") # yapf: disable
        if not isinstance(cartesian, bool) and cartesian != None:
            raise ValueError("ABCMolecule.to_qe() optional argument 'cartesian' is not type bool or NoneType.") # yapf: disable
        if cartesian:
            save_mol = self.switch_to_cartesian()
        else:
            save_mol = self.switch_to_direct()
        with open(os.path.join(os.getcwd(), filename), "w") as openfile:
            for line in save_mol._format(endline="\n",filetype=".qe"):
                openfile.writelines(line)

    def to_rdkit_mol(self) -> rdkit_Chem_rdchem_Mol:
        """Converts ABCMolecule object to rdkit.Chem.rdchem.Mol object.
        Read rdkit documentation for more informtion.
        
        Returns
        -------
        rdkit.Chem.rdchem.Mol 
            rdkit.Chem.rdchem.Mol object with same coordinates and positions as ABCMolecule instance.
        
        Notes
        -----
        Suggested methods to call after this one.
            - To get bond connectivity information.
                - rdDetermineBonds.DetermineConnectivity(Mol)
                - (from rdkit.Chem import rdDetermineBonds)
                - There are other methods of rdDetermineBonds submodule that may be of interest also.
            - To draw a 2d image of ABCMolecule instance.
                - Mol.Compute2DCoords() & Draw.MolToImage(Mol).show()
                - (from rdkit.Chem import Draw)
        """
        return self.convert().to_rdkit_mol()

    def to_turbomole(self, filename: str) -> None:
        """Write ABCMolecule object to .turbomole file.

        Parameters
        ----------
        filename : str
            Name of .turbomole file that will be created.

        Returns
        -------
            .turbomole file containing ABCMolecule object.
        """
        if not isinstance(filename, str):
            raise ValueError("ABCMolecule.to_turbomole() required argument 'filename' is not type str.") # yapf: disable
        self.convert().to_turbomole(filename=filename)

    def to_vasp(self, filename: str, cartesian: bool | None = None) -> None:
        """Write ABCMolecule object to .vasp file.

        Parameters
        ----------
        filename : str
            Name of .xyz file that will be created.
        cartesian : bool | None, optional
            If True, .vasp file will contain cartesian coordinates.
            If False, .vasp file will contain direct coordinates.
            If not provided, .vasp file will default to self.positional coordinates.

        Returns
        -------
            .vasp file containing ABCMolecule object.
        """
        if not isinstance(filename, str):
            raise ValueError("ABCMolecule.to_vasp() required argument 'filename' is not type str.") # yapf: disable
        if not isinstance(cartesian, bool) and cartesian != None:
            raise ValueError("ABCMolecule.to_vasp() optional argument 'cartesian' is not type bool or NoneType.") # yapf: disable
        if cartesian:
            save_mol = self.switch_to_cartesian()
        else:
            save_mol = self.switch_to_direct()
        with open(os.path.join(os.getcwd(), filename), "w") as openfile:
            for line in save_mol._format(endline="\n",filetype=".vasp"):
                openfile.writelines(line)

    def to_xyz(self, filename: str) -> None:
        """Write XYZMolecule object to .xyz file.

        Parameters
        ----------
        filename : str
            Name of .xyz file that will be created.

        Returns
        -------
            .xyz file containing XYZMolecule object.
        """
        if not isinstance(filename, str):
            raise ValueError("ABCMolecule.to_xyz() required argument 'filename' is not type str.") # yapf: disable
        self.convert().to_xyz(filename=filename)

# ========================================================
#
#
#               XYZ MOLECULE SECTION
#
#
# ========================================================
# ========================================================
#
#               XYZ Classes SECTION
#            XYZCoord and XYZMolecule
# ========================================================


class XYZMolecule:
    """Class for xyz molecule object.

    Parameters
    ----------
    atoms : list[ABCCoord]
        List of Atoms from atomic file.
    comment_line : str, default is " "
        Comment line of atomic file.
    filetype: str
        The original filetype the object instance was.

    Fields
    ------
    species_line
        List of each species in species line. Similar to line 5 in VASP file.\n
    species_amount: list[int]
        List of the amount of each species in species line. Similar to line 6 in VASP file.\n
    total: int
        Total amount of atoms in ABCMolecule object.\n
    amount_dict: dict[str, int]
        Dictionary with keys as species and fields of amount of each species.
                
    Returns
    -------
    XYZMolecule
        XYZMolecule object with defined molecule information.
    """

    def __init__(self, atoms: list[XYZCoord], comment_line: str = " ", filetype: str="") -> None:
        if not isinstance(atoms, (list, tuple, set)):
            raise ValueError("XYZMolecule.__init__() required argument 'atoms' not iterable list.") # yapf: disable
        if len(atoms) == 0:
            raise ValueError("XYZMolecule.__init__() require argument 'atoms' contains zero elements.") # yapf: disable
        for n, item in enumerate(atoms):
            if not isinstance(item, XYZCoord):
                raise ValueError(f"XYZMolecule.__init__() index {n} of atoms is not type XYZCoord; item = {item}.") # yapf: disable
        if not isinstance(comment_line, str):
            raise ValueError("XYZMolceule.__init__() required argument 'comment_line' is not type str.") # yapf: disable
        if not isinstance(filetype, str):
            raise ValueError("XYZMolceule.__init__() required argument 'filetype' is not type str.") # yapf: disable
        self.atoms: list[XYZCoord] = atoms
        self.comment_line: str = comment_line
        self.filetype: str = filetype
        self.__post_init__()

    def __post_init__(self) -> None:
        self.species_line: list[str] = list()
        self.species_amount: list[str] = list()
        _ = "PL@C3H0LD3R"
        for atom in self.atoms:
            if atom.sp == _:
                self.species_amount[-1] = str(1 + int(self.species_amount[-1]))
            else:
                self.species_line.append(atom.sp)
                self.species_amount.append("1")
                _ = atom.sp
        self.total = sum([int(num) for num in self.species_amount])
        _species_key = [x for i, x in enumerate(
            self.species_line) if self.species_line.index(x) == i]
        self.amount_dict: dict[str, int] = {sp: 0 for sp in _species_key}
        for ele, amt in zip(self.species_line, self.species_amount):
            curr_value = self.amount_dict[ele]
            new_value = int(amt) + curr_value
            self.amount_dict[ele] = new_value

    def __str__(self) -> str:
        return f"XYZMolecule(atoms={self.atoms}, comment_line='{self.comment_line}')"

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, item: XYZMolecule) -> XYZMolecule:
        if not isinstance(item, XYZMolecule):
            raise ValueError("XYZMolecule.__add__() can only add type XYZMolecule.") # yapf: disable
        return self.append(new_coords=item.atoms)

    def __len__(self) -> int:
        return len(self.atoms)

    def __getitem__(self, index: MolIndex) -> XYZMolecule:
        if isinstance(index, (int, str)):
            index = str(index)
            if index.replace("-", "").isdecimal():
                if -len(self.atoms) <= int(index) <= -1:
                    return XYZMolecule(atoms=[self.atoms[int(index)]], comment_line=self.comment_line, filetype=self.filetype,)
                elif len(self.atoms) >= int(index) >= 1:
                    return XYZMolecule(atoms=[self.atoms[int(index) - 1]], comment_line=self.comment_line, filetype=self.filetype,)
                else:
                    raise IndexError(f"XYZMolecule.__getitem__() index = '{index}'; int is out of range of len(self.atoms) or is zero.") # yapf: disable
            elif index in self.species_line:
                return XYZMolecule(
                    atoms=[item for item in self.atoms if item.sp == index],
                    comment_line=self.comment_line,
                    filetype=self.filetype,
                )
            else:
                return XYZMolecule(
                    atoms=[self.atoms[self._get_molden_index(index)]],
                    comment_line=self.comment_line,
                    filetype=self.filetype,
                )
        elif isinstance(index, (list, tuple, set)):
            return_atoms: list[XYZCoord] = list()
            for item in [str(ele) for ele in index]:
                if item.replace("-", "").isdecimal():
                    if -len(self.atoms) <= int(item) <= -1:
                        return_atoms.append(self.atoms[int(item)])
                    elif len(self.atoms) >= int(item) >= 1:
                        return_atoms.append(self.atoms[int(item) - 1])
                    else:
                        raise IndexError(f"XYZMolecule.__getitem__() index = '{index}'; int is out of range of len(self.atoms).") # yapf: disable
                elif item in self.species_line:
                    return_atoms.extend(
                        [ele for ele in self.atoms if ele.sp == item])
                else:
                    return_atoms.append(
                        self.atoms[self._get_molden_index(item)])
            return XYZMolecule(atoms=return_atoms, comment_line=self.comment_line, filetype=self.filetype,)
        else:
            raise IndexError(f"XYZMolecule.__getitem__() index = '{index}'; not valid index.") # yapf: disable

    def __setitem__(self, index: int | str, new_item: XYZCoord) -> None:
        if not isinstance(index, (int, str)):
            raise ValueError("XYZMolecule.__setitem__() index must be of type int or str.") # yapf: disable
        if not isinstance(new_item, XYZCoord):
            raise ValueError("XYZMolecule.__setitem__() Value assignment must be type XYZCoord.") # yapf: disable
        self.atoms[self.atoms.index(
            self.__getitem__(index).atoms[0])] = new_item
        self.__post_init__()

    def _format(self, filetype: str, endline: str) -> list[str]:
        """Returns formatted text for textbox or filewrite.

        Parameters
        ----------
        filetype: str
            file format wanted. {.xyz, .turbomole}
        endline : str, default " "
            Endline string for each file line.

        Returns
        -------
        list[str]
            list of strings for xyz format with endline str as last character in string.        
        """
        if not isinstance(endline, str):
            raise ValueError("XYZMolecule._format() optional argument 'endline' not a str.") # yapf: disable
        text: list[str] = list()
        if filetype == ".xyz":
            text.append(f"{self.total}" + endline)
            text.append(f"{self.comment_line}" + endline)
            for i in range(len(self.atoms)):
                text.append(f"{self.atoms[i].sp:2}{Sx}{self.atoms[i].x:>{Lx}.{Fx}f}{Sx}{self.atoms[i].y:>{Lx}.{Fx}f}{Sx}{self.atoms[i].z:>{Lx}.{Fx}f}" + endline)
            return text
        elif filetype == ".orca":
            text.append("!" + endline)
            text.append("*xyz 0 1 #Charge and multiplicity (2S+1). Here charge is 0 (neutral),multiplicity=1 (singlet, S=0)." + endline)
            for i in range(len(self.atoms)):
                text.append(f"{self.atoms[i].sp:2}{Sx}{self.atoms[i].x:>{Lx}.{Fx}f}{Sx}{self.atoms[i].y:>{Lx}.{Fx}f}{Sx}{self.atoms[i].z:>{Lx}.{Fx}f}" + endline)
            text.append("*" + endline)
            return text
        elif filetype == ".turbomole":
            text.append("$coord" + endline)
            for i in range(len(self.atoms)):
                text.append(f"{'': <8}{self.atoms[i].x:>{Lx}.{Fx}f}{self.atoms[i].y:>{Lx}.{Fx}f}{self.atoms[i].z:>{Lx}.{Fx}f}{'': <4}{self.atoms[i].sp.lower():2}" + endline)
            text.append("$end" + endline)
            return text
        else:
            raise ValueError("XYZMolecule._format() optional argument 'filetype' is not '.xyz' or '.turbomole'.") # yapf: disable

    def _get_molden_index(self, index: MolIndex) -> int:
        if not isinstance(index, str):
            raise IndexError(f"XYZMolecule._get_molden_index() index = '{index}'; index type not correct.") # yapf: disable
        _n1 = ""
        _a1 = ""
        for item in index[::-1]:
            if item.isdecimal():
                _n1 += item
            else:
                _a1 += item
        _n2 = _n1[::-1]
        if _n2 == "":
            raise IndexError(f"XYZMolecule._get_molden_index() index = '{index}'; no # after.") # yapf: disable
        _a2 = _a1[::-1]
        if index == _a2 + _n2:
            _n3 = int(_n2)
            if _a2 not in self.species_line:
                raise IndexError(f"XYZMolecule._get_molden_index() index = '{index}'; Sp not in self.speciesline.") # yapf: disable
            if self.amount_dict[_a2] >= _n3 >= 1:
                return self.atoms.index([item for item in self.atoms if item.sp == _a2][_n3 - 1])
            else:
                raise IndexError(f"XYZMolecule._get_molden_index() index = '{index}'; # is too large or zero.") # yapf: disable
        else:
            raise IndexError(f"XYZMolecule._get_molden_index() index = '{index}'; Sp# out of order.") # yapf: disable

    def _get_unitcell_sidelengths(self) -> tuple[float,float,float]:
        x_min = min([coord.x for coord in self.atoms])
        y_min = min([coord.y for coord in self.atoms])
        z_min = min([coord.z for coord in self.atoms])
        x_max = max([coord.x for coord in self.atoms])
        y_max = max([coord.y for coord in self.atoms])
        z_max = max([coord.z for coord in self.atoms])
        a = abs(x_max-x_min)
        b = abs(y_max-y_min)
        c = abs(z_max-z_min)
        return (a,b,c)

    """ def _get_unitcell_lattice_matrix(self) -> LatticeMatrix:
    #     a,b,c = self._get_unitcell_sidelengths()
    #     return LatticeMatrix(constant=1,
    #                          vector_1=[a,0,0],
    #                          vector_2=[0,b,0],
    #                          vector_3=[0,0,c])
    """

    def add_coords(self,molecule: XYZMolecule, axis: str | int, absorbent_reference: str | CoordType, surface_reference: str | CoordType, dist: float,inplace: bool = False) -> XYZMolecule:
        """Add a new Molecule object to the current XYZMolecule object very precisely.

        Parameters
        ----------
        molecule : XYZMolecule
            Molecule object to add to the current XYZMolecule object.
        axis : "{0 or 'x', 1 or 'y', 2 or 'z'}"
            Placement of new molecule will be in direction of axis.
        absorbent_reference : "{'Top' or 'Centroid' or 'Bottom' or 'Most postive Sp' or 'Most negative Sp' or CoordType}"
            Reference on argument 'molecule' where the distance is measured.
        surface_reference : "{'Top' or 'Centroid' or 'Bottom' or 'Most postive Sp' or 'Most negative Sp' or CoordType}"
            Reference on current molecule object where the distance is measured.
        dist : float
            sign of float determines what direction the new molecule is placed.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        XYZMolecule
            XYZMolecule with new atoms added.
        """
        if axis not in ["x", "y", "z", 0, 1, 2]:
            raise ValueError(f"XYZMolecule.add_coords() required argument 'axis' is not 'x' or 'y' or 'z' or 1 or 2 or 3.") # yapf: disable
        match axis:
            case "x":
                axis_int = 0
            case "y":
                axis_int = 1
            case "z":
                axis_int = 2
            case _:
                axis_int = int(axis)
        if not isinstance(dist, (int, float)):
            raise ValueError("XYZMolecule.add_coords() required argument 'dist' not a number.") # yapf: disable
        if not isinstance(inplace, bool):
            raise ValueError("XYZMolecule.add_coords() optional argument 'inplace' not a bool.") # yapf: disable
        # needed to not append to memory and return only changed object
        combined_atoms = copy.copy(self.atoms)
        sur_centroids = self.get_centroid()
        sur_mod = [sur_centroids[0], sur_centroids[1], sur_centroids[2]]
        x_import_centroid, y_import_centroid, z_import_centroid = molecule.get_centroid()
        abs_centroids = [x_import_centroid,
                         y_import_centroid, z_import_centroid]
        x_import_list = [float(coord[1]) for coord in molecule.atoms]
        y_import_list = [float(coord[2]) for coord in molecule.atoms]
        z_import_list = [float(coord[3]) for coord in molecule.atoms]
        abs_lists = (x_import_list, y_import_list, z_import_list)
        x_curr_list = [float(coord[1]) for coord in self.atoms]
        y_curr_list = [float(coord[2]) for coord in self.atoms]
        z_curr_list = [float(coord[3]) for coord in self.atoms]
        sur_lists = (x_curr_list, y_curr_list, z_curr_list)
        # finding absorbent values
        if isinstance(absorbent_reference, (ABCCoord, XYZCoord)):
            abs_mod = [0.0,0.0,0.0]
            abs_mod[0] = absorbent_reference[1]
            abs_mod[1] = absorbent_reference[2]
            abs_mod[2] = absorbent_reference[3]
        elif absorbent_reference == "Centroid":
            abs_mod = abs_centroids
        elif absorbent_reference in ["Top","Bottom"]:
            abs_mod = abs_centroids
            if absorbent_reference == "Top":
                sort_func = max
            else:  # if absorbent_reference == "Bottom":
                sort_func = min
            abs_mod[axis_int] = sort_func(abs_lists[axis_int])
        elif absorbent_reference == "Origin":
            abs_mod = [0.0, 0.0, 0.0]
        else:
            raise ValueError("XYZMolecule.add_coords() required argument 'absorbent_reference' not 'Top','Centroid','Origin', or 'Bottom'.") # yapf: disable

        # finding surface values now
        if isinstance(surface_reference, (ABCCoord, XYZCoord)):
            sur_mod[0] = surface_reference[1]
            sur_mod[1] = surface_reference[2]
            sur_mod[2] = surface_reference[3]
        elif surface_reference == "Centroid":
            sur_mod = sur_centroids
        elif surface_reference == "(0.5,0.5,0.5)":
            sur_mod = [0.5, 0.5, 0.5]
        elif surface_reference in ["Top", "Bottom"]:
            if surface_reference == "Top":
                sort_func = max
            # if surface_reference == ABSORBENT_OPTIONS['starting_surface_list'][1]:
            else:
                sort_func = min
            sur_mod[axis_int] = sort_func(sur_lists[axis_int])
        elif surface_reference in ["Most positive ", "Most negative"]:
            species = surface_reference[14:]
            if "Most positive " in surface_reference:
                sort_func = max
            else:  # if "Most negative" in surface_reference:
                sort_func = min
            species_import_list = [float(coord[axis_int + 1])
                                   for coord in self.atoms if coord.sp == species]
            sur_mod[axis_int] = sort_func(species_import_list)
        elif surface_reference == "origin":  # necessary for add atom
            sur_mod = [0, 0, 0]  # if surface_reference == 'origin'
        else:
            raise ValueError("XYZMolecule.add_coords() required argument 'surface_reference' not 'Top','Centroid','Bottom','Most postive Sp','Most negative Sp' or CoordType.") # yapf: disable

        # math for finding displacement distanceance
        distance = [0.0, 0.0, 0.0]
        distance[axis_int] = dist
        x_mod = sur_mod[0] - abs_mod[0] + distance[0]
        y_mod = sur_mod[1] - abs_mod[1] + distance[1]
        z_mod = sur_mod[2] - abs_mod[2] + distance[2]
        for ele in molecule.atoms:
            combined_atoms.append(XYZCoord(ele.sp, float(
                ele[1]) + x_mod, float(ele[2]) + y_mod, float(ele[3]) + z_mod))
        if inplace:
            self.atoms = combined_atoms
            self.__post_init__()
        return XYZMolecule(atoms=combined_atoms, comment_line=self.comment_line, filetype=self.filetype,)

    def append(self, new_coords: XYZCoord | list[XYZCoord], inplace: bool = False) -> XYZMolecule:
        """To add coords to the current XYZMolecule.atoms attribute.

        Parameters
        ----------
        new_coords : XYZCoord or list[XYZCoord]
            List of new coords to add to new object.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        XYZMolecule
            XYZMolecule object with new atoms.
        """
        if not isinstance(new_coords, list):
            new_coords = [new_coords]
        for n, item in enumerate(new_coords):
            if not isinstance(item, XYZCoord):
                raise ValueError(f"XYZMolecule.__init__() index {n} of atoms is not type XYZCoord; item = {item}.") # yapf: disable
        if not isinstance(inplace, bool):
            raise ValueError("XYZMolecule.append() optional argument 'inplace' not a bool.") # yapf: disable
        new_atoms = copy.copy(self.atoms)
        new_atoms.extend(new_coords)
        if inplace:
            self.atoms = new_atoms
            self.__post_init__()
        return XYZMolecule(atoms=new_atoms, comment_line=self.comment_line, filetype=self.filetype,)

    def convert(self, lattice_matrix: LatticeMatrix, positional: bool = True) -> ABCMolecule:
        """Converts XYZMolecule instance to ABCMolecule.

        Parameters
        ----------
        lattice_matrix : LatticeMatrix
            Instance of LatticeMatrix dataclass needed for ABCMolecule class.
        positional : bool, default True
            If True, XYZ cartesian coordinates will convert to positional coordinates. If False, ABCMolecule will contain cartesian coordinates.

        Returns
        -------
        ABCMolecule
            ABCMolecule object generated from converted XYZMolecule object.
        """
        def csc(x: float) -> float:
            """Return the cosecant of x (measured in radians)."""
            return 1 / sin(x)
        # def sec(x: float) -> float:
        #     """Return the secant of x (measured in radians)."""
        #     return 1 / cos(x)
        def cot(x: float) -> float:
            """Return the cotangent of x (measured in radians)."""
            return 1 / tan(x)
        if not isinstance(lattice_matrix, LatticeMatrix):
            raise ValueError("XYZMolecule.convert() required argument 'lattice_matrix' not type LatticeMatrix.") # yapf: disable
        if not isinstance(positional, bool):
            raise ValueError("XYZMolecule.convert() optional argument 'positional' not type bool.") # yapf: disable
        if positional:
            alp, bet, gam = lattice_matrix.getanglesrad()
            a, b, c = lattice_matrix.getabc()
            A = [
                [
                    csc(bet) / (a * np.sqrt(1 - (cot(alp) * cot(bet) - csc(alp) * csc(bet) * cos(gam)) ** 2)),
                    0,
                    0,
                ],
                [
                    ((csc(alp) ** 2) * csc(bet) * (cos(alp) * cos(bet) - cos(gam))) / (b * np.sqrt(1 - (cot(alp) * cot(bet) - csc(alp) * csc(bet) * cos(gam)) ** 2)),
                    csc(alp) / b,
                    0,
                ],
                [
                    (csc(alp) * ((cot(alp) * csc(bet) * cos(gam)) - (csc(alp) * cot(bet)))) / (c * np.sqrt(1 - (cot(alp) * cot(bet) - csc(alp) * csc(bet) * cos(gam)) ** 2)),
                    (-cot(alp)) / c,
                    1 / c,
                ],
            ]
            convert_atoms: list[ABCCoord] = list()
            for atom in self.atoms:
                f = np.matrix([[atom.x], [atom.y], [atom.z]])
                r = np.dot(A, f)
                convert_atoms.append(
                    ABCCoord(atom.sp, float(r[0]), float(r[1]), float(r[2])))
            return ABCMolecule(
                comment_line=self.comment_line,
                atoms=convert_atoms,
                unitcell=lattice_matrix,
                positional=positional,
                filetype=self.filetype,
            )
        else:
            return ABCMolecule(
                comment_line=self.comment_line,
                atoms=[ABCCoord(coord.sp, coord.x, coord.y, coord.z) for coord in self.atoms],
                unitcell=lattice_matrix,
                positional=positional,
                filetype=self.filetype,
            )

    def create_unitcell(self, a: float, b: float, c: float, alpha: float, beta: float, gamma: float, unit: str = "deg") -> ABCMolecule:
        """Create Unitcell from .xyz model.

        Parameters
        ----------
        a : float
            Sidelength a, in Angstroms.
        b : float
            Sidelength b, in Angstroms.
        c : float
            Sidelength c, in Angstroms.
        alpha : float
            Angle alpha in units of argument units.
        beta : float
            Angle beta in units of argument units.
        gamma : float
            Angle gamma in units of argument units.
        unit : "deg" or "rad", default "deg"
            Units of alpha, beta, and gamma.

        Returns
        -------
        ABCMolecule
            ABCMolecule instance with .xyz model contained within the Unit Cell specified.
        """
        for ele, name in zip([a, b, c, alpha, beta, gamma],["a", "b", "c", "alpha", "beta", "gamma"]):
            if not isinstance(ele, (int, float)):
                raise ValueError(f"XYZMolecule.create_unitcell() required argument '{name}' not a number.") # yapf: disable
            if ele <= 0:
                raise ValueError(f"XYZMolecule.create_unitcell() required argument '{name}' cannot be less than zero.") # yapf: disable
        if unit not in ["deg", "rad"]:
            raise ValueError(f"XYZMolecule.rotate() required argument 'unit' is not 'deg' or 'rad'.") # yapf: disable
        raise NotImplementedError("XYZMolecule.create_unitcell() not finished.") # yapf: disable
        for ele, name, minimum in zip([a, b, c],["a", "b", "c"],self._get_unitcell_sidelengths()):
            pass

    def cut_polygon(self, normal_axis: str | int, radius: int | float, side_amount: int,  origin : CoordType = XYZCoord("X", 0, 0, 0), angle: float = 0.0, unit: str = "deg",  inplace: bool = False):
        """Cuts out a n-sided polygon on a specifc axis plane.

        Parameters
        ----------
        normal_axis : "{0 or 'x', 1 or 'y', 2 or 'z'}"
            Axis normal to the plane that is being cut with the polygon.
        radius : int | float
            Radius of the polygon to be cut.
        side_amount : int {0 or >=3}
            n amount of sides for the polygon. 0 is for circle and 3 is for triangle, 4 for square, 5 for pentagon etc...
        origin : CoordType, default XYZCoord("X", 0, 0, 0)
            Supply if you want to move the slab surface to cut in a seperate spot.
        angle : float, default 0.0
            Angle you want to rotate the polygon by.
        unit : "deg" or "rad", default "deg"
            Unit of angle argument.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        XYZMolecule
            XYZMolecule instance with atoms deleted outside of the polygon boundaries.

        """
        if normal_axis not in ["x", "y", "z", 0, 1, 2]:
            raise ValueError(f"XYZMolecule.cut_polygon() required argument 'angle' is not 'x' or 'y' or 'z' or 1 or 2 or 3.") # yapf: disable
        match normal_axis:
            case "x":
                normal_axis_int = 0
            case "y":
                normal_axis_int = 1
            case "z":
                normal_axis_int = 2
            case _:
                normal_axis_int = int(normal_axis)
        if not isinstance(radius, (int, float)):
            raise ValueError("XYZMolecule.cut_polygon() required argument 'radius' not a number.") # yapf: disable
        if radius <= 0:
            raise ValueError("XYZMolecule.cut_polygon() required argument 'radius' is not a positive non zero number.") # yapf: disable
        if not isinstance(side_amount, int):
            raise ValueError("XYZMolecule.cut_polygon() required argument 'side_amount' not an integer.") # yapf: disable
        if side_amount != 0 and side_amount < 3:
            raise ValueError("XYZMolecule.cut_polygon() required argument 'side_amount' needs to be 0 or greater than 2.") # yapf: disable
        if not isinstance(origin, (ABCCoord, XYZCoord)):
            raise ValueError("XYZMolecule.cut_polygon() required argument 'origin' not a CoordType instance.") # yapf: disable
        if not isinstance(inplace, bool):
            raise ValueError("XYZMolecule.cut_polygon() optional argument 'inplace' not a bool.") # yapf: disable

        sc_mol = XYZMolecule(atoms=self.atoms, comment_line=self.comment_line, filetype=self.filetype)

        sc_mol.rotate(axis=normal_axis_int, angle=angle, unit=unit, inplace=True)

        match normal_axis_int:
            case 0:
                plane_1 = 2
                plane_2 = 3
            case 1:
                plane_1 = 1
                plane_2 = 3
            case _:
                plane_1 = 1
                plane_2 = 2

        if side_amount == 0:
            def is_coord_in_polygon(coord) -> bool:
                if coord[plane_1]**2 + coord[plane_2]**2 <= radius**2:
                    return True
                else:
                    return False
        else:
            angle_for_polygon = 2 * pi / side_amount
            vertices = list()
            h = 0.0
            k = 0.0
            for i in range(side_amount):
                vertex_x = h + radius * cos(i*angle_for_polygon)
                vertex_y = k + radius * sin(i*angle_for_polygon)
                vertices.append((vertex_x, vertex_y))
            def is_coord_in_polygon(coord) -> bool:
                intersections = 0
                for i in range(side_amount):
                    v1 = vertices[i]
                    v2 = vertices[(i+1) % side_amount]

                    if (v1[1] > coord[plane_2]) != (v2[1] > coord[plane_2]):
                        intersect_x = v1[0] + (coord[plane_2] - v1[1]) * (v2[0] - v1[0])/(v2[1] - v1[1])
                        if coord[plane_1] < intersect_x:
                            intersections += 1
                return intersections % 2 == 1

        needs_to_be_deleted = list()
        for i in range(1, len(sc_mol)+1):
            if not is_coord_in_polygon(sc_mol.get(i)):
                needs_to_be_deleted.append(i)

        sc_mol.delete(index=needs_to_be_deleted, inplace=True)
        if inplace:
            self.atoms = sc_mol.atoms
            self.__post_init__()
        return XYZMolecule(atoms=sc_mol.atoms, comment_line=sc_mol.comment_line, filetype=sc_mol.filetype)

    def delete(self, index: MolIndex, inplace: bool = False) -> XYZMolecule:
        """Delete INDEXED atoms in XYZMolecule.

        Parameters
        ----------
        index : MolIndex
            MolIndex can be a list of strings or integers or a single string or int 
            that is either an atom number, species+species number (Molden style), or species.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        XYZMolecule
            XYZMolecule object with selected atoms deleted.
        """
        if not isinstance(inplace, bool):
            raise ValueError("XYZMolecule.delete() optional argument 'inplace' not a bool.") # yapf: disable
        saving_atoms: list[XYZCoord] = list()
        del_ints: list[int] = list()
        if type(index) != list:
            # not exactly sure why but good theres a small amount of type ignores for each molecule class
            index = [index]  # type: ignore s
        for item in index:  # type: ignore
            for ele in self[item].atoms:
                del_ints.append(self.atoms.index(ele))
        saving_atoms = [self.atoms[i]
                        for i in range(len(self.atoms)) if not i in del_ints]
        if inplace:
            self.atoms = saving_atoms
            self.__post_init__()
        return XYZMolecule(atoms=saving_atoms, comment_line=self.comment_line, filetype=self.filetype,)

    def generate_supercell(self, x: int, y: int, z: int, inplace: bool = False) -> XYZMolecule:
        """Method returns a supercell of the structure.

        Parameters
        ----------
        x : int >= 1
            Amount in the x direction the structure will be multiplied by.
        y : int >= 1
            Amount in the y direction the structure will be multiplied by.
        z : int >= 1
            Amount in the z direction the structure will be multiplied by.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        XYZMolecule
            XYZMolecule object of generated supercell.
        """
        if not isinstance(x, int):
            raise ValueError("XYZMolecule.generate_supercell() required argument 'x' not a positive int.") # yapf: disable
        if not isinstance(y, int):
            raise ValueError("XYZMolecule.generate_supercell() required argument 'y' not a positive int.") # yapf: disable
        if not isinstance(z, int):
            raise ValueError("XYZMolecule.generate_supercell() required argument 'z' not a positive int.") # yapf: disable
        if x <= 0 or y <= 0 or z <= 0:
            raise ValueError("XYZMolecule.generate_supercell() x or y or z cannot be input of zero or negative.") # yapf: disable
        if not isinstance(inplace, bool):
            raise ValueError("XYZMolecule.generate_supercell() optional argument 'inplace' not a bool.") # yapf: disable
        a,b,c = self._get_unitcell_sidelengths()
        x_mol = copy.deepcopy(self)
        y_mol = copy.deepcopy(self)
        z_mol = copy.deepcopy(self)
        x_atoms = copy.deepcopy(self.atoms)
        for _ in range(1, x):
            x_mol.move(x=a,y=0,z=0,inplace=True)
            x_atoms.extend(x_mol.atoms)
        y_mol = XYZMolecule(atoms=x_atoms)
        y_atoms = copy.deepcopy(y_mol.atoms)
        for _ in range(1, y):
            y_mol.move(x=0,y=b,z=0,inplace=True)
            y_atoms.extend(y_mol.atoms)
        z_mol = XYZMolecule(atoms=y_atoms)
        z_atoms = copy.deepcopy(z_mol.atoms)
        for _ in range(1, z):
            z_mol.move(x=0,y=0,z=c,inplace=True)
            z_atoms.extend(z_mol.atoms)
        if inplace:
            self.atoms = z_atoms
            self.__post_init__()
        return XYZMolecule(atoms=z_atoms)

    def generate_cluster(self, normal_axis: str | int, radius: int | float, side_amount: int,  origin : CoordType = XYZCoord("X", 0, 0, 0), angle: float = 0.0, unit: str = "deg",  inplace: bool = False) -> XYZMolecule:
        """Generates a cluster model with a polygon cut out of n sides. Used in ABCMolecule.generate_cluster() .

        Parameters
        ----------
        normal_axis : "{0 or 'x', 1 or 'y', 2 or 'z'}"
            Axis normal to the plane that is being cut with the polygon.
        radius : int | float
            Radius of the polygon to be cut.
        side_amount : int {0 or >=3}
            n amount of sides for the polygon. 0 is for circle and 3 is for triangle, 4 for square, 5 for pentagon etc...
        origin : CoordType, default XYZCoord("X", 0, 0, 0)
            Supply if you want to move the slab surface to cut in a seperate spot.
        angle : float, default 0.0
            Angle you want to rotate the polygon by.
        unit : "deg" or "rad", default "deg"
            Unit of angle argument.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        XYZMolecule
            XYZMolecule instance with atoms deleted outside of the polygon boundaries.

        """
        if normal_axis not in ["x", "y", "z", 0, 1, 2]:
            raise ValueError(f"XYZMolecule.cut_polygon() required argument 'angle' is not 'x' or 'y' or 'z' or 1 or 2 or 3.") # yapf: disable
        match normal_axis:
            case "x":
                normal_axis_int = 0
            case "y":
                normal_axis_int = 1
            case "z":
                normal_axis_int = 2
            case _:
                normal_axis_int = int(normal_axis)

        match normal_axis_int:
            case 0:
                sc_x = 1
                sc_y = sc_z = 1
            case 1:
                sc_x = sc_z = 1
                sc_y = 1
            case _:
                sc_x = sc_y = 1
                sc_z = 1


        while True:
            # print(sc_x, sc_y, sc_z, "sc parameters")
            sc_mol = XYZMolecule(atoms=self.atoms, comment_line=self.comment_line, filetype=self.filetype)
            sc_mol = sc_mol.generate_supercell(x=sc_x, y=sc_y, z=sc_z, inplace=True)

            match normal_axis_int:
                case 0:
                    x_adjust = 0.0
                    y_adjust = sc_mol.sort("y").get(-1)[1] - sc_mol.sort("y").get(1)[1]
                    z_adjust = sc_mol.sort("z").get(-1)[1] - sc_mol.sort("z").get(1)[1]
                case 1:
                    x_adjust = sc_mol.sort("x").get(-1)[1] - sc_mol.sort("x").get(1)[1]
                    y_adjust = 0.0
                    z_adjust = sc_mol.sort("z").get(-1)[1] - sc_mol.sort("z").get(1)[1]
                case _:
                    x_adjust = sc_mol.sort("x").get(-1)[1] - sc_mol.sort("x").get(1)[1]
                    y_adjust = sc_mol.sort("y").get(-1)[1] - sc_mol.sort("y").get(1)[1]
                    z_adjust = 0.0

            sc_mol.move(x=-origin[1]-x_adjust/2, y=-origin[2]-y_adjust/2, z=-origin[3]-z_adjust/2, inplace=True)

            if normal_axis_int != 0:
                is_x_axis_large_enough = False
                x_mol = sc_mol.sort("x")
                for coord in x_mol.atoms:
                    if coord[1] > radius:
                        for coord in x_mol.atoms:
                            if coord[1] < -radius:
                                is_x_axis_large_enough = True
                                # print("x large", sc_x)
                                break
                    if is_x_axis_large_enough:
                        break
            else:
                is_x_axis_large_enough = True
            if normal_axis_int != 1:
                is_y_axis_large_enough = False
                y_mol = sc_mol.sort("y")
                for coord in y_mol.atoms:
                    if coord[2] > radius:
                        for coord in y_mol.atoms:
                            if coord[2] < -radius:
                                is_y_axis_large_enough = True
                                # print("y large", sc_y)
                                break
                    if is_y_axis_large_enough:
                        break
            else:
                is_y_axis_large_enough = True
            if normal_axis_int != 2:
                is_z_axis_large_enough = False
                z_mol = sc_mol.sort("z")
                for coord in z_mol.atoms:
                    if coord[3] > radius:
                        for coord in z_mol.atoms:
                            if coord[3] < -radius:
                                is_z_axis_large_enough = True
                                # print("z large", sc_z)
                                break
                    if is_z_axis_large_enough:
                        break
            else:
                is_z_axis_large_enough = True


            if is_x_axis_large_enough and is_y_axis_large_enough and is_z_axis_large_enough:
                # print(sc_x, sc_y, sc_z, "all axis large enough, continuing")
                break

            for i in range(3):
                if i == 0 and i != normal_axis_int:
                    sc_x += 1
                    # print("adding 1 x")
                if i == 1 and i != normal_axis_int:
                    sc_y += 1
                    # print("adding 1 y")
                if i == 2 and i != normal_axis_int:
                    sc_z += 1
                    # print("adding 1 z")

        return sc_mol.cut_polygon(normal_axis=normal_axis, radius=radius, side_amount=side_amount, origin=origin, angle=angle, unit=unit, inplace=inplace)

    def get(self, index: str | int) -> XYZCoord:
        """Get an XYZCoord indexed

        Parameters
        ----------
        index : str | int
            Either atom number, or species+species number (Molden style),

        Returns
        -------
        XYZCoord
            Indexed XYZCoord from XYZMolecule.atoms .
        """
        mol = self.__getitem__(index)
        if len(mol.atoms) == 1:
            return mol.atoms[0]
        else:
            raise ValueError("XYZMolecule.get() index was a list or species. Use XYZMolecule.get_atoms() to return list of atoms.") # yapf: disable

    def get_atoms(self, index: MolIndex) -> list[XYZCoord]:
        """Get an XYZCoord indexed

        Parameters
        ----------
        index : MolIndex
            MolIndex can be a list of strings or integers or a single string or int 
            that is either an atom number, species+species number (Molden style), or species.

        Returns
        -------
        list[XYZCoord]
            Returns list of indexed atoms from XYZMolecule.atoms .
        """
        return self.__getitem__(index).atoms

    def get_centroid(self) -> tuple[float, float, float]:
        """Returns 3d centroid of XYZMolecule atoms.

        Returns
        -------
        tuple[float,float,float]
            Tuple of (x_centroid,y_centroid,z_centroid) in Angstroms.
        """
        x_list = [coord.x for coord in self.atoms]
        y_list = [coord.y for coord in self.atoms]
        z_list = [coord.z for coord in self.atoms]
        x_centroid = sum(x_list) / len(x_list)
        y_centroid = sum(y_list) / len(y_list)
        z_centroid = sum(z_list) / len(z_list)
        return (x_centroid, y_centroid, z_centroid)

    def head(self, n: int = 10, filetype: str | None = None) -> None:
        """Prints the first n rows.
        
        Parameters
        ----------
        n: int, default 10
            Amount of filelines to select.
        filetype: str {'.xyz', '.turbomole'} Default is self.filetype.
            Format of the printed file.
            
        Returns
        -------
            Method prints first n rows of filetype to terminal.
        """
        if not isinstance(n, int):
            raise ValueError("XYZMolecule.head() optional argument 'n' not a int.") # yapf: disable
        if filetype == None:
            format_type = self.filetype
        else:
            format_type = filetype
        for line in self._format(endline=" ", filetype=format_type)[:n]:
            print(line)

    def info(self) -> None:
        """Prints XYZMolecule current attribute information to terminal."""
        print(f"type: XYZMolecule\nfiletype: {self.filetype}\ntotal atoms: {self.total}\nspecies info: {self.amount_dict}\ncomment line: '{self.comment_line}'") # yapf: disable

    def manipulate(self, index: MolIndex, func: str, inplace: bool = False, *args, **kwargs) -> XYZMolecule:
        """Rotate or move only INDEXED atoms in XYZMolecule.

        Parameters
        ----------
        index : MolIndex
            MolIndex can be a list of strings or integers or a single string or int 
            that is either an atom number, species+species number (Molden style), or species.
        func : "{'move' or 'rotate'}"
            XYZMolecule method you want to execute on the indexed atoms.
        inplace : bool, default False
            If True, perform operation in-place.
        *args,**kwargs
            Arguments of the chosen function 'move' or 'rotate'.

        Returns
        -------
        XYZMolecule
            XYZMolecule with all atoms moved or rotated.
        """
        if not isinstance(inplace, bool):
            raise ValueError("ABCMolecule.manipulate() optional argument 'inplace' not a bool.") # yapf: disable
        i_list: list[int] = list()
        moving_atoms: list[XYZCoord] = list()
        if type(index) != list:
            index = [index]  # type: ignore
        for item in index:  # type: ignore
            for ele in self[item].atoms:
                i_list.append(self.atoms.index(ele))
                moving_atoms.append(ele)
        moving_mol = XYZMolecule(atoms=moving_atoms)
        if func == "move":
            new_mol = moving_mol.move(*args, **kwargs)
        elif func == "rotate":
            new_mol = moving_mol.rotate(*args, **kwargs)
        else:
            raise ValueError("XYZMolecule.manipulate() required argument 'func' not 'move' or 'rotate'.") # yapf: disable
        new_atoms = self.atoms
        for n, ele in zip(i_list, new_mol.atoms):
            new_atoms[n] = ele
        if inplace:
            self.atoms = new_atoms
            self.__post_init__()
        return XYZMolecule(atoms=new_atoms, comment_line=self.comment_line, filetype=self.filetype,)

    def move(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, inplace: bool = False) -> XYZMolecule:
        """Move ALL atoms in designated directions.

        Parameters
        ----------
        x : float, default 0.0
            Move coord in x direction by float amount.
        y : float, default 0.0
            Move coord in y direction by float amount.
        z : float, default 0.0
            Move coord in z direction by float amount.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        XYZMolecule
            XYZMolecule object with all atoms moved.
        """
        if not isinstance(x, (int, float)):
            raise ValueError(f"XYZMolecule.move() optional argument 'x' is not a number.") # yapf: disable
        if not isinstance(y, (int, float)):
            raise ValueError(f"XYZMolecule.move() optional argument 'y' is not a number.") # yapf: disable
        if not isinstance(z, (int, float)):
            raise ValueError(f"XYZMolecule.move() optional argument 'z' is not a number.") # yapf: disable
        if not isinstance(inplace, bool):
            raise ValueError("XYZMolecule.move() optional argument 'inplace' is not a bool.") # yapf: disable
        return_atoms: list[XYZCoord] = list()
        for coord in self.atoms:
            sp = coord.sp
            x_old = coord.x
            y_old = coord.y
            z_old = coord.z
            return_atoms.append(
                XYZCoord(sp=sp, x=x_old + x, y=y_old + y, z=z_old + z))
        if inplace:
            self.atoms = return_atoms
            self.__post_init__()
        return XYZMolecule(atoms=return_atoms, comment_line=self.comment_line, filetype=self.filetype,)

    def print(self, filetype: str | None = None) -> None:
        """Prints ALL rows of file to terminal.
        
        Parameters
        ----------
        filetype: str {'.xyz', '.turbomole'} Default is self.filetype.
            Format of the printed file.
            
        Returns
        -------
            Method prints ALL rows of filetype to terminal.
        """
        if filetype == None:
            format_type = self.filetype
        else:
            format_type = filetype
        for line in self._format(endline=" ", filetype=format_type):
            print(line)

    def rotate(self, axis: str | int, angle: float,unit: str = "deg", about_centroid: bool = True, inplace: bool = False) -> XYZMolecule:
        """Rotate ALL atoms about designated axis.

        Parameters
        ----------
        axis : "{0 or 'x', 1 or 'y', 2 or 'z'}"
            Parallel axis of rotation.
        angle : float
            Angle of rotation.
        unit : "deg" or "rad", default "deg"
            Unit of angle argument.
        about_centroid : bool, default True
            If True, rotation occurs about the centroid.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        XYZMolecule
            XYZMolecule with all atoms rotated.
        """
        if axis in ["x", 0]:
            def rotation(x: float, y: float, z: float) -> tuple[float, float, float]:
                return x, y * cos(angle) - z * sin(angle), y * sin(angle) + z * cos(angle)
        elif axis in ["y", 1]:
            def rotation(x: float, y: float, z: float) -> tuple[float, float, float]:
                return x * cos(angle) + z * sin(angle), y, z * cos(angle) - x * sin(angle)
        elif axis in ["z", 2]:
            def rotation(x: float, y: float, z: float) -> tuple[float, float, float]:
                return x * cos(angle) - y * sin(angle), x * sin(angle) + y * cos(angle), z
        else:
            raise Exception("XYZMolecule.rotate() required argument 'axis' is not 'x','y','z',0,1, or 2.") # yapf: disable
        if not isinstance(angle, (int, float)):
            raise ValueError(f"XYZMolecule.rotate() required argument 'angle' is not a number.") # yapf: disable
        if unit not in ["deg", "rad"]:
            raise ValueError(f"XYZMolecule.rotate() required argument 'unit' is not 'deg' or 'rad'.") # yapf: disable
        if not isinstance(about_centroid, bool):
            raise ValueError("XYZMolecule.rotate() optional argument 'about_centroid' is not a bool.") # yapf: disable
        if not isinstance(inplace, bool):
            raise ValueError("XYZMolecule.rotate() optional argument 'inplace' is not a bool.") # yapf: disable
        if unit == "deg":
            angle *= pi / 180
        return_atoms: list[XYZCoord] = list()
        if about_centroid:
            x_cent, y_cent, z_cent = self.get_centroid()
        else:
            x_cent = y_cent = z_cent = 0.0
        for coord in self.atoms:
            rot_x, rot_y, rot_z = rotation(float(coord.x) - x_cent, float(coord.y) - y_cent, float(coord.z) - z_cent)
            return_atoms.append(XYZCoord(sp=coord.sp, x=rot_x + x_cent, y=rot_y + y_cent, z=rot_z + z_cent))
        if inplace:
            self.atoms = return_atoms
            self.__post_init__()
        return XYZMolecule(atoms=return_atoms, comment_line=self.comment_line, filetype=self.filetype)

    def sort(self, sort_method: str | list[str] | list[list[str]], ascending: bool | list[bool] = True, inplace: bool = False) -> XYZMolecule:
        """Sort the atoms in Molecule instance by position, species, alphabetical or atomic number.

        Parameters
        ----------
        sort_method : str | list[str] | list[list[str]]
            Method given by which the atoms will be sorted.\n
                - if sort_method is 'x' the atoms will be sorted by their x coordinate.
                - if sort_method is 'y' the atoms will be sorted by their y coordinate.
                - if sort_method is 'z' the atoms will be sorted by their z coordinate.
                - if sort_method is 'alphabetical' the atoms will be sorted in alphabetical order by their species.
                - if sort_method is 'periodical' the atoms will be sorted by their atomic number.
            You can also supply a list of lists with position 0 being species and position 1 being 'x','y','z', or None.\n
                This will sort the coordinates by species then by the method provided for each species,
                you can also add a list of bool for ascending values that will correspond to each species chosen method.\n
            You can also supply a list of species and it will be reordered to the given order.\n
        ascending : bool or list of bool, default True
            Sort ascending vs. descending. Specify list for multiple sort orders (as described above). If this is a list of bools, must match the length of sort_method.
        inplace : bool, default False
            If True, perform operation in-place.

        Returns
        -------
        XYZMolecule
            XYZMolecule with all atoms resorted.
        """
        if isinstance(sort_method, str):
            if sort_method not in ["x", "y", "z", "alphabetical", "periodical", "None", None]:
                raise ValueError("XYZMolecule.sort() required argument 'sort_method' is not one of 'x','y','z','alphabetical','periodical'.") # yapf: disable
            # making individual string so it can work in for loop enumerate below
            sort_method = [sort_method]
        elif isinstance(sort_method, (list, tuple, set)):
            # if len(sort_method) != len(self.species_line):
            if len(sort_method) != len(set(self.species_line)): #need set to resort and regroup atoms if same species multiple times in species line
                raise ValueError("XYZMolecule.sort() required argument 'sort_method' not the same length of amount of species in XYZMolecule.") # yapf: disable
            for item in sort_method:
                if isinstance(item, str):
                    item = [item]
                if not isinstance(item, (list, tuple, set)):
                    raise ValueError("XYZMolecule.sort() required argument 'sort_method' list item not correct type.") # yapf: disable
                if len(item) == 1:
                    if item[0] not in self.species_line:
                        raise ValueError("XYZMolecule.sort() required argument 'sort_method' list item position 0 not species in self.species_line (len(item)=1).") # yapf: disable
                elif len(item) == 2:
                    if item[0] not in self.species_line:
                        raise ValueError("XYZMolecule.sort() required argument 'sort_method' list item position 0 not species in self.species_line.") # yapf: disable
                    if item[1] not in ["x", "y", "z", "None", None]:
                        raise ValueError("XYZMolecule.sort() required argument 'sort_method' list item position 1 is not one of type 'x','y','z','None',None (len(item)=2).") # yapf: disable
                else:
                    raise ValueError("XYZMolecule.sort() required argument 'sort_method' list item length > 2.") # yapf: disable
        else:
            raise ValueError("XYZMolecule.sort() required argument 'sort_method' not correct types.") # yapf: disable
        if isinstance(ascending, (list, tuple, set)):
            if not isinstance(sort_method, (list, tuple, set)):
                raise ValueError("XYZMolecule.sort() ascending is type list but sortmethod is not type list.") # yapf: disable
            if len(sort_method) != len(ascending):
                raise ValueError("XYZMolecule.sort() length of ascending list not equivalent to length of sort method.") # yapf: disable
            if not all([isinstance(item, bool) for item in ascending]):
                raise ValueError("XYZMolecule.sort() ascending list[bool] not all bool type.") # yapf: disable
        elif not isinstance(ascending, bool):
            raise ValueError("XYZMolecule.sort() ascending bool type not bool type.") # yapf: disable
        return_atoms: list[XYZCoord] = list()
        for n, item in enumerate(sort_method):
            if isinstance(ascending, bool):
                reverse_bool = False if ascending else True
            elif isinstance(ascending, (list, tuple, set)) and len(ascending) == 1:
                reverse_bool = False if ascending[0] else True
            elif len(ascending) == len(sort_method):
                reverse_bool = False if ascending[n] else True
            else:
                raise ValueError("XYZMolecule.sort() ascending argument is wrong.") # yapf: disable
            if isinstance(item, (list, tuple, set)):
                if len(item) == 1:
                    tobesorted = self.atoms  # for string
                    method = item[0]
                elif item[0] in self.species_line:
                    tobesorted = self[item[0]].atoms
                    method = item[1]
                else:
                    raise ValueError("XYZMolecule.sort() required argument 'sort_method' is not correct.") # yapf: disable
            else: #if isinstance(item, str):
                if item in self.species_line:
                    tobesorted = self[item].atoms
                    method = "None"
                elif item in ["x", "y", "z", "alphabetical", "periodical", "None", None]:
                    # raise ValueError("XYZMolecule.sort() required argument 'sort_method' list species index 1 is not one of 'x','y','z','alphabetical','periodical','None',None.") # yapf: disable
                    method = item
                    tobesorted = self.atoms
                else:
                    raise ValueError("XYZMolecule.sort() required argument 'sort_method' list species does not contain species.") # yapf: disable
            if method == "x":
                return_atoms.extend(sorted(tobesorted, key=lambda x: x[1], reverse=reverse_bool))
            elif method == "y":
                return_atoms.extend(sorted(tobesorted, key=lambda x: x[2], reverse=reverse_bool))
            elif method == "z":
                return_atoms.extend(sorted(tobesorted, key=lambda x: x[3], reverse=reverse_bool))
            elif method == "alphabetical":
                return_atoms.extend(sorted(tobesorted, key=lambda x: x.sp, reverse=reverse_bool))
            elif method == "periodical":
                return_atoms.extend(sorted(tobesorted, key=lambda x: ACCEPTED_ELEMENTS.index(x.sp), reverse=reverse_bool))
            else:
                return_atoms.extend(tobesorted)
        if inplace:
            self.atoms = return_atoms
            self.__post_init__()
        return XYZMolecule(atoms=return_atoms, comment_line=self.comment_line, filetype=self.filetype,)

    def tail(self, n: int = 10, filetype: str | None = None) -> None:
        """Prints the last n rows.
        
        Parameters
        ----------
        n: int, default 10
            Amount of filelines to select.
        filetype: str {'.xyz', '.turbomole'} Default is self.filetype.
            Format of the printed file.
            
        Returns
        -------
            Method prints last n rows of filetype to terminal.
        """
        if not isinstance(n, int):
            raise ValueError("XYZMolecule.tail() optional argument 'n' not a int.") # yapf: disable
        if filetype == None:
            format_type = self.filetype
        else:
            format_type = filetype
        for line in self._format(endline=" ", filetype=format_type)[-n:]:
            print(line)

    def to_lammps(self, filename: str, lattice_matrix: LatticeMatrix) -> None:
        """Write XYZMolecule object to .lammps file.

        Parameters
        ----------
        filename : str
            Name of .lammps file that will be created.
        lattice_matrix : LatticeMatrix
            LatticeMatrix object for unitcell box.

        Returns
        -------
            .lammps file containing XYZMolecule object.
        """
        if not isinstance(filename, str):
            raise ValueError("XYZMolecule.to_lammps() required argument 'filename' is not type str.") # yapf: disable
        self.convert(lattice_matrix=lattice_matrix).to_lammps(filename=filename)

    def to_orca(self, filename: str) -> None:
        """Write XYZMolecule object to .orca file.

        Parameters
        ----------
        filename : str
            Name of .orca file that will be created.

        Returns
        -------
            .orca file containing XYZMolecule object.
        """
        if not isinstance(filename, str):
            raise ValueError("XYZMolecule.to_orca() required argument 'filename' is not type str.") # yapf: disable
        with open(os.path.join(os.getcwd(), filename), "w") as openfile:
            for line in self._format(filetype=".orca",endline="\n"):
                openfile.writelines(line)

    def to_qe(self, filename: str, lattice_matrix: LatticeMatrix, cartesian: bool | None = None) -> None:
        """Write XYZMolecule object to .qe file.

        Parameters
        ----------
        filename : str
            Name of .xyz file that will be created.
        lattice_matrix : LatticeMatrix
            LatticeMatrix object for unitcell box.
        cartesian : bool | None, optional
            If True, .qe file will contain cartesian coordinates.
            If False, .qe file will contain direct coordinates.
            If not provided, .qe file will contain direct coordinates.

        Returns
        -------
            .qe file containing XYZMolecule object.
        """
        if not isinstance(filename, str):
            raise ValueError("XYZMolecule.to_qe() required argument 'filename' is not type str.") # yapf: disable
        if isinstance(cartesian, bool):
            format_type = cartesian
        else:
            format_type = False
        self.convert(lattice_matrix=lattice_matrix).to_qe(filename=filename, cartesian=format_type)

    def to_rdkit_mol(self) -> rdkit_Chem_rdchem_Mol:
        """Converts XYZMolecule object to rdkit.Chem.rdchem.Mol object.
        Read rdkit documentation for more informtion.
        
        Returns
        -------
        rdkit.Chem.rdchem.Mol 
            rdkit.Chem.rdchem.Mol object with same coordinates and positions as XYZMolecule instance.
        
        Notes
        -----
        Suggested methods to call after this one.
            - To get bond connectivity information.
                - rdDetermineBonds.DetermineConnectivity(Mol)
                - (from rdkit.Chem import rdDetermineBonds)
                - There are other methods of rdDetermineBonds submodule that may be of interest also.
            - To draw a 2d image of XYZMolecule instance.
                - Mol.Compute2DCoords() & Draw.MolToImage(Mol).show()
                - (from rdkit.Chem import Draw)
        """
        if MolFromXYZBlock is None:
            raise RuntimeError(
                "XYZMolecule.to_rdkit_mol()"
                "RDKit is required to convert ABCMolecule or XYZMolecule to rdkit_Chem_rdchem_Mol Object. "
                "Install it via conda: 'conda install -c conda-forge rdkit' "
                "or pip: 'pip install rdkit'."
            )
        return MolFromXYZBlock(self._format(filetype=".xyz",endline=""))

    def to_turbomole(self, filename: str) -> None:
        """Write XYZMolecule object to .turbomole file.

        Parameters
        ----------
        filename : str
            Name of .turbomole file that will be created.

        Returns
        -------
            .turbomole file containing XYZMolecule object.
        """
        if not isinstance(filename, str):
            raise ValueError("XYZMolecule.to_turbomole() required argument 'filename' is not type str.") # yapf: disable
        x,y,z = self.get_centroid()
        save_mol = self.move(x=-x,y=-y,z=-z)
        with open(os.path.join(os.getcwd(), filename), "w") as openfile:
            for line in save_mol._format(filetype=".turbomole",endline="\n"):
                openfile.writelines(line)

    def to_vasp(self, filename: str, lattice_matrix: LatticeMatrix, cartesian: bool | None = None) -> None:
        """Write XYZMolecule object to .vasp file.

        Parameters
        ----------
        filename : str
            Name of .xyz file that will be created.
        lattice_matrix : LatticeMatrix
            LatticeMatrix object for unitcell box.
        cartesian : bool | None, optional
            If True, .vasp file will contain cartesian coordinates.
            If False, .vasp file will contain direct coordinates.
            If not provided, .vasp file will contain direct coordinates.

        Returns
        -------
            .vasp file containing XYZMolecule object.
        """
        if not isinstance(filename, str):
            raise ValueError("XYZMolecule.to_vasp() required argument 'filename' is not type str.") # yapf: disable
        if isinstance(cartesian, bool):
            format_type = cartesian
        else:
            format_type = False
        self.convert(lattice_matrix=lattice_matrix).to_vasp(filename=filename, cartesian=format_type)

    def to_xyz(self, filename: str) -> None:
        """Write XYZMolecule object to .xyz file.

        Parameters
        ----------
        filename : str
            Name of .xyz file that will be created.

        Returns
        -------
            .xyz file containing XYZMolecule object.
        """
        if not isinstance(filename, str):
            raise ValueError("XYZMolecule.to_xyz() required argument 'filename' is not type str.") # yapf: disable
        with open(os.path.join(os.getcwd(), filename), "w") as openfile:
            for line in self._format(filetype=".xyz",endline="\n"):
                openfile.writelines(line)


# ========================================================
#
#         Animation Class Section
#
#
# ========================================================



class ABCAnimation:
    def __init__(self, animation_dict: dict[int, ABCMolecule], repeating_unitcell: bool) -> None:
        """Contains an atomic simulation position with data from .xyz animation file.

        Parameters
        ----------
        animation_dict : dict[int, ABCMolecule]
            Dictionary that contains xyz animation information. First image is key of 0 
            and keys are in order from 0-> # of images.
        repeating_unitcell: bool
            True if the unitcell is constant between the images.
            False if the unitcell is changes between the images.
            
        Returns
        -------
        ABCAnimation
            ABCAnimation object that contains xyz animation information for dft calculation.
        """
        self.animation_dict: dict[int, ABCMolecule] = animation_dict
        self.repeating_unitcell: bool = repeating_unitcell
        if not isinstance(self.repeating_unitcell, bool):
            raise ValueError("ABCAnimation.__init__() required argument 'repeating_unitcell' is not type bool.") # yapf: disable
        for n in range(len(self.animation_dict)):
            if n not in self.animation_dict:
                raise ValueError("ABCAnimation.__init__() required argument 'animation_dict' does not contain necessary key.") # yapf: disable
            if not isinstance(self.animation_dict[n], ABCMolecule):
                raise ValueError("ABCAnimation.__init__() required argument 'animation_dict' does not contain type ABCMolecule.") # yapf: disable

    def __getitem__(self, index: int) -> ABCMolecule:
        if isinstance(index,int):
            return self.animation_dict[index]
        else:
            raise IndexError(f"ABCAnimation.__getitem__() index = '{index}'; index is not type slice or int.") # yapf: disable

    def __len__(self) -> int:
        return len(self.animation_dict)

    def _format(self, endline: str =" ") -> list[str]:
        text: list[str] = list()
        if self.repeating_unitcell:
            text.extend(self.animation_dict[0]._format(filetype=".vasp",endline=endline))
            for n in range(1, len(self.animation_dict)):
                text.append(self.animation_dict[n].comment_line+endline)
                for i in range(len(self.animation_dict[n].atoms)):
                    text.append(
                        f"{self.animation_dict[n].atoms[i][1]:>{La}.{Fa}f}{self.animation_dict[n].atoms[i][2]:>{La}.{Fa}f}{self.animation_dict[n].atoms[i][3]:>{La}.{Fa}f}"
                        + endline)
            return text
        else:
            for n in self.animation_dict:
                text.extend(self.animation_dict[n]._format(filetype=".vasp",endline=endline))
            return text

    def convert(self) -> XYZAnimation:
        """Convert ABCAnimation object to XYZAnimation object."""
        convert_dict: dict[int, XYZMolecule] = dict()
        for i in range(len(self.animation_dict)):
            convert_dict[i] = self.animation_dict[i].convert()
            convert_dict[i].filetype = ".xyz"
        return XYZAnimation(animation_dict=convert_dict)

    def get(self, index: int) -> ABCMolecule:
        """Returns INDEXED ABCMolecule image.

        Parameters
        ----------
        index : int
            integer range between 0 and len(ABCAnimation)-1

        Returns
        -------
        ABCMolecule
            ABCMolecule object of iteration # index of ABCAnimation.
        """
        return self.__getitem__(index=index)

    def get_range(self, index: tuple[int, int] | slice) -> ABCAnimation:
        """Returns ABCAnimation object of selected range of images.

        Parameters
        ----------
        index : tuple[int, int] | slice
            [start, stop] similar to indexing list by list[start:stop].
            Does not accept step argument in slice object.
        
        Returns
        -------
        ABCAnimation
            ABCAnimation object of the selected range of images.
        """
        if isinstance(index, slice):
            start = index.start
            stop = index.stop
            step = index.step
            if step != None:
                raise IndexError(f"ABCAnimation.__getitem__() index = '{index}'; slice step is not implemented.") # yapf: disable
            if step == None:
                step = 0
            if stop == None:
                stop = len(self)
        elif isinstance(index, (list, tuple, set)):
            if len(index) != 2:
                raise IndexError(f"ABCAnimation.__getitem__() index = '{index}'; list is greater than 2.") # yapf: disable
            if not isinstance(index[0], int) or not isinstance(index[1], int):
                raise IndexError(f"ABCAnimation.__getitem__() index = '{index}'; list value is not int.") # yapf: disable
            start = index[0]
            stop = index[1]
        else:
            raise ValueError(f"ABCAnimation.__getitem__() index = '{index}'; index is not type list or slice.") # yapf: disable
        if stop < 0:
            stop =+ len(self)
        index_dict = dict()
        i = 0
        for n in range(start, stop):
            index_dict[i] = self.__getitem__(index=n)
            i += 1
        return ABCAnimation(animation_dict=index_dict,repeating_unitcell=self.repeating_unitcell)

    def head(self, n: int = 10) -> None:
        """Prints the first n rows.
        
        Parameters
        ----------
        n: int, default 10
            Amount of filelines to select.
            
        Returns
        -------
            Method prints first n rows of .xyz animation file to terminal.
        """
        if not isinstance(n, int):
            raise ValueError("ABCMolecule.head() optional argument 'n' not a int.") # yapf: disable
        for line in self._format(endline=" ")[:n]:
            print(line)

    def info(self) -> None:
        """Prints initial image of ABCAnimation current attribute information to terminal."""
        print("ABCAnimation Object")
        print(f"Total # of images {len(self.animation_dict)}")
        print(f"repeating_unitcell = {self.repeating_unitcell}")
        print("Initial image info:")
        self.animation_dict[0].info()

    def print(self) -> None:
        """Prints ALL rows of file to terminal."""
        for line in self._format(endline=" "):
            print(line)

    def tail(self, n: int = 10) -> None:
        """Prints the last n rows.
        
        Parameters
        ----------
        n: int, default 10
            Amount of filelines to select.
            
        Returns
        -------
            Method prints last n rows of .xyz animation file to terminal.
        """
        if not isinstance(n, int):
            raise ValueError("ABCAnimation.tail() optional argument 'n' not a int.") # yapf: disable
        for line in self._format(endline=" ")[-n:]:
            print(line)

    def to_xdatcar(self, filename: str) -> None:
        """Write ABCAnimation object to .xdatcar file.

        Parameters
        ----------
        filename : str
            Name of .xdatcar file that will be created.

        Returns
        -------
            .xdatcar file containing ABCAnimation object.
        """
        if not isinstance(filename, str):
            raise ValueError("ABCMolecule.to_xyz() required argument 'filename' is not type str.") # yapf: disable
        with open(os.path.join(os.getcwd(), filename), "w") as openfile:
            for line in self._format(endline="\n"):
                openfile.writelines(line)

    def to_xyz_animation(self, filename: str) -> None:
        """Write ABCAnimation object to .xyz animation file.

        Parameters
        ----------
        filename : str
            Name of .xyz animation file that will be created.

        Returns
        -------
            .xyz animation file containing ABCAnimation object.
        """
        if not isinstance(filename, str):
            raise ValueError("ABCMolecule.to_xyz() required argument 'filename' is not type str.") # yapf: disable
        with open(os.path.join(os.getcwd(), filename), "w") as openfile:
            for line in self.convert()._format(endline="\n"):
                openfile.writelines(line)


class XYZAnimation:
    def __init__(self, animation_dict: dict[int, XYZMolecule]) -> None:
        """Contains an atomic simulation position with data from .xyz animation file.

        Parameters
        ----------
        animation_dict : dict[int, XYZMolecule]
            Dictionary that contains xyz animation information. First image is key of 0 
            and keys are in order from 0-> # of images.

        Returns
        -------
        XYZAnimation
            XYZAnimation object that contains xyz animation information for dft calculation.
        """
        self.animation_dict: dict[int, XYZMolecule] = animation_dict
        for n in range(len(self.animation_dict)):
            if n not in self.animation_dict:
                raise ValueError("XYZAnimation.__init__() required argument 'animation_dict' does not contain necessary key.") # yapf: disable
            if not isinstance(self.animation_dict[n], XYZMolecule):
                raise ValueError("XYZAnimation.__init__() required argument 'animation_dict' does not contain type XYZMolecule.") # yapf: disable

    def __getitem__(self, index: int) -> XYZMolecule:
        if isinstance(index,int):
            return self.animation_dict[index]
        else:
            raise IndexError(f"XYZAnimation.__getitem__() index = '{index}'; index is not type slice or int.") # yapf: disable

    def __len__(self) -> int:
        return len(self.animation_dict)

    def _format(self, endline: str =" ") -> list[str]:
        text: list[str] = list()
        for n in self.animation_dict:
            text.extend(self.animation_dict[n]._format(filetype=".xyz",endline=endline))
        return text

    def convert(self, lattice_matrix: LatticeMatrix | list[LatticeMatrix]) -> ABCAnimation:
        """Convert XYZAnimation object to ABCAnimation object.

        Parameters
        ----------
        lattice_matrix : LatticeMatrix | list[LatticeMatrix]
            Either singular latticematrix or list the same length
            of animation_dict with a LatticeMatrix for every image
            of animation.

        Returns
        -------
        ABCAnimation
            Converted images with a unitcell from the XYZMolecule information.
        """
        if isinstance(lattice_matrix, LatticeMatrix):
            repeating_unitcell = True
            convert_dict: dict[int, ABCMolecule] = dict()
            for i in range(len(self.animation_dict)):
                convert_dict[i] = self.animation_dict[i].convert(lattice_matrix=lattice_matrix)
                convert_dict[i].filetype = ".vasp"
            return ABCAnimation(animation_dict=convert_dict, repeating_unitcell=repeating_unitcell)
        elif isinstance(lattice_matrix, (list, tuple, set)):
            if len(lattice_matrix) != len(self.animation_dict):
                raise ValueError("XYZAnimation.convert() required argument 'lattice_matrix' is not the same length as amount of images in animation_dict.") # yapf: disable
            for ele in lattice_matrix:
                if not isinstance(ele, LatticeMatrix):
                    raise ValueError("XYZAnimation.convert() required argument 'lattice_matrix' does not contain a LatticeMatrix object.")   # yapf: disable
            repeating_unitcell = False
            convert_dict: dict[int, ABCMolecule] = dict()
            for i in range(len(self.animation_dict)):
                convert_dict[i] = self.animation_dict[i].convert(lattice_matrix=lattice_matrix[i])
                convert_dict[i].filetype = ".vasp"
            return ABCAnimation(animation_dict=convert_dict, repeating_unitcell=repeating_unitcell)
        else:
            raise ValueError("XYZAnimation.convert() required argument 'lattice_matrix' is not type LatticeMatrix or list[LatticeMatrix].") # yapf: disable

    def get(self, index: int) -> XYZMolecule:
        """Returns INDEXED XYZMolecule image.

        Parameters
        ----------
        index : int
            integer range between 0 and len(XYZAnimation)-1

        Returns
        -------
        XYZMolecule
            XYZMolecule object of iteration # index of XYZAnimation.
        """
        return self.__getitem__(index=index)

    def get_range(self, index: tuple[int, int] | slice) -> XYZAnimation:
        """Returns XYZAnimation object of selected range of images.

        Parameters
        ----------
        index : tuple[int, int] | slice
            [start, stop] similar to indexing list by list[start:stop].
            Does not accept step argument in slice object.
        
        Returns
        -------
        XYZAnimation
            XYZAnimation object of the selected range of images.
        """
        if isinstance(index, slice):
            start = index.start
            stop = index.stop
            step = index.step
            if step != None:
                raise IndexError(f"XYZAnimation.__getitem__() index = '{index}'; slice step is not implemented.") # yapf: disable
            if step == None:
                step = 0
            if stop == None:
                stop = len(self)
        elif isinstance(index, (list, tuple, set)):
            if len(index) != 2:
                raise IndexError(f"XYZAnimation.__getitem__() index = '{index}'; list is greater than 2.") # yapf: disable
            if not isinstance(index[0], int) or not isinstance(index[1], int):
                raise IndexError(f"XYZAnimation.__getitem__() index = '{index}'; list value is not int.") # yapf: disable
            start = index[0]
            stop = index[1]
        else:
            raise ValueError("XYZAnimation.__getitem__() index is not type list or slice.") # yapf: disable
        if stop < 0:
            stop =+ len(self)
        index_dict = dict()
        i = 0
        for n in range(start, stop):
            index_dict[i] = self.__getitem__(index=n)
            i += 1
        return XYZAnimation(animation_dict=index_dict)

    def head(self, n: int = 10) -> None:
        """Prints the first n rows.
        
        Parameters
        ----------
        n: int, default 10
            Amount of filelines to select.
            
        Returns
        -------
            Method prints first n rows of .xyz animation file to terminal.
        """
        if not isinstance(n, int):
            raise ValueError("XYZMolecule.head() optional argument 'n' not a int.") # yapf: disable
        for line in self._format(endline=" ")[:n]:
            print(line)

    def info(self) -> None:
        """Prints initial image of XYZAnimation current attribute information to terminal."""
        print("XYZAnimation Object")
        print(f"Total # of images {len(self.animation_dict)}")
        print("Initial image info:")
        self.animation_dict[0].info()

    def print(self) -> None:
        """Prints ALL rows of file to terminal."""
        for line in self._format(endline=" "):
            print(line)

    def tail(self, n: int = 10) -> None:
        """Prints the last n rows.
        
        Parameters
        ----------
        n: int, default 10
            Amount of filelines to select.
            
        Returns
        -------
            Method prints last n rows of .xyz animation file to terminal.
        """
        if not isinstance(n, int):
            raise ValueError("XYZAnimation.tail() optional argument 'n' not a int.") # yapf: disable
        for line in self._format(endline=" ")[-n:]:
            print(line)

    def to_xdatcar(self, filename: str,  lattice_matrix: LatticeMatrix | list[LatticeMatrix]) -> None:
        """Write XYZAnimation object to .xdatcar file.

        Parameters
        ----------
        filename : str
            Name of .xdatcar file that will be created.
        lattice_matrix : LatticeMatrix | list[LatticeMatrix]
            Either singular latticematrix or list the same length
            of animation_dict with a LatticeMatrix for every image
            of animation.

        Returns
        -------
            .xdatcar file containing XYZAnimation object.
        """
        if not isinstance(filename, str):
            raise ValueError("ABCMolecule.to_xyz() required argument 'filename' is not type str.") # yapf: disable
        with open(os.path.join(os.getcwd(), filename), "w") as openfile:
            for line in self.convert(lattice_matrix=lattice_matrix)._format(endline="\n"):
                openfile.writelines(line)

    def to_xyz_animation(self, filename: str) -> None:
        """Write XYZAnimation object to .xyz animation file.

        Parameters
        ----------
        filename : str
            Name of .xyz animation file that will be created.

        Returns
        -------
            .xyz animation file containing XYZAnimation object.
        """
        if not isinstance(filename, str):
            raise ValueError("XYZMolecule.to_xyz() required argument 'filename' is not type str.") # yapf: disable
        with open(os.path.join(os.getcwd(), filename), "w") as openfile:
            for line in self._format(endline="\n"):
                openfile.writelines(line)

# ========================================================
#
#         File Reading Functions
#
#
# ========================================================
# ========================================================
#
#               Vasp
#
# ========================================================


def _isvasplist(data_list: list[list[str]], debug_print: bool = False) -> bool:
    """Return True if data list fufills .vasp file standards, False otherwise.

    Parameters
    ----------
    data_list : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    bool
        True if data_list fufills .vasp file standards.

    Notes
    -----
    .vasp file standards:
        -there is a positive float value for lattice constant
        -there is a 3x3 float matrix for lattice matrix
        -there is correct species line
        -there is list of integers below species line
        -there is Selective Dynamics with dynamics info after coord info
        -there is Cartesian or Direct with correct coord matrix below
    """
    if _regex_string_list(string_list=data_list[1],
                          pattern_list=[r"^[0-9]*\.?[0-9]+$"],
                          strict_on_length=True) is False:
        if debug_print:
            print("False 1")
        return False
    if _regex_string_list(string_list=data_list[2],
                          pattern_list=[r"^[-+]?[0-9]*\.?[0-9]+$",
                                        r"^[-+]?[0-9]*\.?[0-9]+$",
                                        r"^[-+]?[0-9]*\.?[0-9]+$"],
                          strict_on_length=True) is False:
        if debug_print:
            print("False 2")
        return False
    if _regex_string_list(string_list=data_list[3],
                          pattern_list=[r"^[-+]?[0-9]*\.?[0-9]+$",
                                        r"^[-+]?[0-9]*\.?[0-9]+$",
                                        r"^[-+]?[0-9]*\.?[0-9]+$"],
                          strict_on_length=True) is False:
        if debug_print:
            print("False 3")
        return False
    if _regex_string_list(string_list=data_list[4],
                          pattern_list=[r"^[-+]?[0-9]*\.?[0-9]+$",
                                        r"^[-+]?[0-9]*\.?[0-9]+$",
                                        r"^[-+]?[0-9]*\.?[0-9]+$"],
                          strict_on_length=True) is False:
        if debug_print:
            print("False 4")
        return False
    if all(ele in ACCEPTED_ELEMENTS for ele in data_list[5]) is False:
        if debug_print:
            print("False 5")
        return False
    if _regex_string_list(string_list=data_list[5],
                          pattern_list=["^("+"|".join(ACCEPTED_ELEMENTS)+")$"]*len(data_list[5])) is False:
        if debug_print:
            print("False 12")
        return False
    if _regex_string_list(string_list=data_list[6],
                        pattern_list=[r"^\d+$"]*len(data_list[5]),
                        strict_on_length=True) is False: #"^[0-9]*$"
        if debug_print:
            print("False 6")
        return False
    tot_atom = sum([int(i) for i in data_list[6]])
    if (_regex_string_list(string_list=data_list[7],
                          pattern_list=["^C.*"])
    or _regex_string_list(string_list=data_list[7],
                          pattern_list=["^D.*"])):
        if len(data_list) < 8+tot_atom:
            if debug_print:
                print("False 7")
            return False
        for line in data_list[8:8+tot_atom]:
            if _regex_string_list(string_list=line,
                                pattern_list=[r"^[-+]?[0-9]*\.?[0-9]+$",
                                        r"^[-+]?[0-9]*\.?[0-9]+$",
                                        r"^[-+]?[0-9]*\.?[0-9]+$"]) is False:
                if debug_print:
                    print("False 8")
                return False
    elif (_regex_string_list(string_list=data_list[7],
                          pattern_list=["^S.*"],)
    and (_regex_string_list(string_list=data_list[8],
                          pattern_list=["^C.*"])
    or _regex_string_list(string_list=data_list[8],
                          pattern_list=["^D.*"]))):
        if len(data_list) < 9+tot_atom:
            if debug_print:
                print("False 9")
            return False
        for line in data_list[9:9+tot_atom]:
            if _regex_string_list(string_list=line,
                                pattern_list=[r"^[-+]?[0-9]*\.?[0-9]+$",
                                        r"^[-+]?[0-9]*\.?[0-9]+$",
                                        r"^[-+]?[0-9]*\.?[0-9]+$",
                                        "^[TF]$",
                                        "^[TF]$",
                                        "^[TF]$"]) is False:
                if debug_print:
                    print("False 10")
                return False
    else:
        if debug_print:
            print("False 11")
        return False
    if debug_print:
        print("True 1")
    return True

def _create_from_vasp_file_data(file_data: list[list[str]], debug_print: bool = False) -> ABCMolecule:
    """Creates ABCMolecule object from POSCAR file_data.

    Parameters
    ----------
    file_data : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    ABCMolecule
        ABCMolecule object with structure data from VASP file.
    """
    if not _isvasplist(data_list=file_data, debug_print=debug_print):
        raise RuntimeError("_create_from_vasp_file_data() required argument 'file_data' is not a vasp file.") # yapf: disable
    total = int(sum([int(file_data[6][i]) for i in range(len(file_data[6]))]))
    if "S" == file_data[7][0]:
        init_data = file_data[9:total+9]
        frozen_atoms = [[line[3],line[4],line[5]] for line in init_data]
    else:
        init_data = file_data[8:total+8]
        frozen_atoms = [[""]]
    sp = [file_data[5][i] for i in range(len(file_data[5])) for _ in range(int(file_data[6][i]))]
    if "C" in file_data[7][0] or "C" in file_data[8][0]:
        positional = False
    else:
        positional = True
    atoms = [
        ABCCoord(
            sp[i],
            float(init_data[i][0]),
            float(init_data[i][1]),
            float(init_data[i][2])
        )
        for i in range(total)
    ]
    return ABCMolecule(
        comment_line=" ".join(file_data[0]),
        unitcell=LatticeMatrix(
            constant=float(file_data[1][0]),
            vector_1=[float(file_data[2][i]) for i in range(3)],
            vector_2=[float(file_data[3][i]) for i in range(3)],
            vector_3=[float(file_data[4][i]) for i in range(3)],
        ),
        positional=positional,
        atoms=atoms,
        frozen_atoms=frozen_atoms,
        filetype=".vasp")

def read_vasp(filepath: str, debug_print: bool = False) -> ABCMolecule:
    """Reads .vasp or POSCAR file and returns ABCMolecule instance.

    Parameters
    ----------
    filepath : str
        Filename (if in current working directory)
        or absolute path or os.path.join(os.getcwd(),'filename.xyz')

    Returns
    -------
    ABCMolecule
        ABCMolecule object with structure data from VASP file.
    """
    if not isinstance(filepath, str):
        raise ValueError("read_vasp() required argument 'filepath' is not type string.") # yapf: disable
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError("read_vasp() required argument 'filepath' file does not exist.") # yapf: disable
    with open(filepath, "r") as openfile:
        file_data = [line.split() for line in openfile]
    return _create_from_vasp_file_data(file_data=file_data, debug_print=debug_print)


# ========================================================
#
#         TURBOMOLE
#
# ========================================================


def _isturbomolelist(data_list: list[list[str]], debug_print: bool = False) -> bool:
    """Return True if datalist fufills turbomole file standards, False otherwise.

    Parameters
    ----------
    data_list : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    bool
        True if turbomole file standards are met, False otherwise.
    
    Notes
    -----
    Turbomole File Standards
        - First line has "$coord"
        - Last line has "$end"
        - atom information consists as
            " x_coord y_coord z_coord species_lowercase optional_f_for_freeze"
        - "$user-defined-bonds" sometimes in line above "$end"
    """
    ACCEPTED_ELEMENTS_lower_case = [ele.lower() for ele in ACCEPTED_ELEMENTS]
    if _regex_nested_string_list(nested_string_list=data_list,pattern_list=[r"^\$coord$"])[0] is False:
        if debug_print:
            print("False 1")
        return False
    has_end, final_atom_index = _regex_nested_string_list(nested_string_list=data_list,pattern_list=[r"^\$end$"])
    if not has_end:
        if debug_print:
            print("False 2")
        return False
    has_user, user_index = _regex_nested_string_list(nested_string_list=data_list,pattern_list=[r"^\$end$"])
    if has_user:
        final_atom_index = user_index
    for line in data_list[1:final_atom_index-1]:
        pattern_list = [r"^[-+]?[0-9]*\.?[0-9]+$",
                        r"^[-+]?[0-9]*\.?[0-9]+$",
                        r"^[-+]?[0-9]*\.?[0-9]+$",
                        "^("+"|".join(ACCEPTED_ELEMENTS_lower_case)+")$"]
        if len(line) == 5:
            pattern_list.append("^f$")
        if _regex_string_list(string_list=line,
                              pattern_list=pattern_list,
                              strict_on_length=True) is False:
            if debug_print:
                print("False 3")
            return False
    return True

def _create_from_turbomole_file_data(file_data: list[list[str]], debug_print: bool = False) -> XYZMolecule:
    """Creates XYZMolecule object from turbomole file_data

    Parameters
    ----------
    file_data : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    XYZMolecule
        XYZMolecule object containing structure data from turbomole file.
    """
    if not _isturbomolelist(data_list=file_data):
        raise RuntimeError("_create_from_turbomole_file_data() required argument 'file_data' is not a turbomole file.") # yapf: disable
    atoms: list[XYZCoord] = list()
    if ["$user-defined bonds"] in file_data:
        final_atom_index = file_data.index(["$user-defined bonds"])
    else: #if ["$end"] in file_data:
        final_atom_index = file_data.index(["$end"])
    for line in file_data[1:final_atom_index-1]:
        atoms.append(XYZCoord(sp=line[3].capitalize(),x=float(line[0]),y=float(line[1]),z=float(line[2])))
    return XYZMolecule(atoms=atoms, comment_line="originally turbomole file", filetype=".turbomole")

def read_turbomole(filepath: str, debug_print: bool = False) -> XYZMolecule:
    """Reads .turbomole file and returns XYZMolecule instance.

    Parameters
    ----------
    filepath : str
        Filename (if in current working directory)
        or absolute path or os.path.join(os.getcwd(),'filename.xyz').

    Returns
    -------
    XYZMolecule
        XYZMolecule object containing structure data from turbomole file.
    """
    if not isinstance(filepath, str):
        raise ValueError("read_turbomole() required argument 'filepath' is not type string.") # yapf: disable
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError("read_turbomole() required argument 'filepath' file does not exist.") # yapf: disable
    with open(filepath, "r") as openfile:
        file_data = [line.split() for line in openfile]
    return _create_from_turbomole_file_data(file_data=file_data, debug_print=debug_print)


# ========================================================
#
#         .xyz file format
#
# ========================================================


def _isxyzlist(data_list: list[list[str]], debug_print: bool = False) -> bool:
    """Return True if datalist fufills .xyz file standards, False otherwise.

    Parameters
    ----------
    data_list : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    bool
        True if .xyz file standards are met, False otherwise.

    Notes
    -----
    .xyz file standards:
        - first line contains a integer (total amount of atoms in file).
        - third line to last line of file contains only this information,
            'Element   float(x coord)   float(y coord)   float(z coord)'.
    """
    if _regex_string_list(string_list=data_list[0],
                          pattern_list=[r"^\d+$"],
                          strict_on_length=True) is False:
        if debug_print:
            print("False 1")
        return False
    total_atoms = int(data_list[0][0])
    if len(data_list) < total_atoms+2:
        if debug_print:
            print("False 2")
        return False
    for line in data_list[2:total_atoms+2]:
        if _regex_string_list(string_list=line,
                              pattern_list=["^("+"|".join(ACCEPTED_ELEMENTS)+")$",
                                            r"^[-+]?[0-9]*\.?[0-9]+$",
                                            r"^[-+]?[0-9]*\.?[0-9]+$",
                                            r"^[-+]?[0-9]*\.?[0-9]+$"],
                              strict_on_length=True) is False:
            if debug_print:
                print("False 3")
            return False
    if debug_print:
        print("True")
    return True

def _create_from_xyz_file_data(file_data: list[list[str]], debug_print: bool = False) -> XYZMolecule:
    """Creates XYZMolecule object from .xyz file_data.

    Parameters
    ----------
    file_data : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    XYZMolecule
        XYZMolecule object containing structure data from .xyz file.
    """
    if not _isxyzlist(data_list=file_data, debug_print=debug_print):
        raise RuntimeError("_create_from_xyz_file_data() required argument 'file_data' is not an xyz file.") # yapf: disable
    return XYZMolecule(
        comment_line=" ".join(file_data[1]),
        atoms=[
            XYZCoord(
                file_data[i][0],
                float(file_data[i][1]),
                float(file_data[i][2]),
                float(file_data[i][3])
            )
            for i in range(2, int(file_data[0][0]) + 2)
        ],
        filetype=".xyz"
    )

def read_xyz(filepath: str, debug_print: bool = False) -> XYZMolecule:
    """Reads .xyz file and returns XYZMolecule instance.

    Parameters
    ----------
    filepath : str
        Filename (if in current working directory)
        or absolute path or os.path.join(os.getcwd(),'filename.xyz').

    Returns
    -------
    XYZMolecule
        XYZMolecule object containing structure data from .xyz file.
    """
    if not isinstance(filepath, str):
        raise ValueError("read_xyz() required argument 'filepath' is not type string.") # yapf: disable
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError("read_xyz() required argument 'filepath' file does not exist.") # yapf: disable
    with open(filepath, "r") as openfile:
        file_data = [line.split() for line in openfile]
    return _create_from_xyz_file_data(file_data=file_data, debug_print=debug_print)


# ========================================================
#
#         .xsf file format
#
# ========================================================


def _is_xsf_coord_line(line:list[str]) -> bool:
    """Returns True if xsf coord line is true."""
    if line == []:
        return False
    if len(line) == 0:
        return False
    if not line[0].isdecimal():
        return False
    if 1 > int(line[0]) and int(line[0]) > 118:
        return False
    if len(line) < 4:
        return False
    if not _isfloatstr(line[1]) or not _isfloatstr(line[2]) or not _isfloatstr(line[3]):
        return False
    return True

def _determine_rest_of_xsf_file(rest_of_file: list[list[str]]) -> tuple[bool, int]:
    """Returns True if xsf file has ended."""
    n = 0
    for line in rest_of_file:
        if _is_xsf_coord_line(line) is False:
            break
        n += 1
    for line in rest_of_file[n+1:]:
        if _is_xsf_coord_line(line):
            return (False, 0)
    return (True, n)

def _isxsflist(data_list: list[list[str]]) -> bool:
    """Return True if datalist fufills .xsf file standards, False otherwise.

    Parameters
    ----------
    data_list : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    bool
        True if .xsf file standards are met, False otherwise.
    """
    if ["PRIMVEC"] in data_list and ["PRIMCOORD"] in data_list:
        if not _regex_nested_string_list(nested_string_list=data_list[data_list.index(["PRIMVEC"])+1:data_list.index(["PRIMVEC"])+3],
                                         pattern_list=[r"^[-+]?[0-9]*\.?[0-9]+$",
                                                       r"^[-+]?[0-9]*\.?[0-9]+$",
                                                       r"^[-+]?[0-9]*\.?[0-9]+$"]):
            return False
        if not data_list[data_list.index(["PRIMCOORD"])+1][0].isdecimal() or data_list[data_list.index(["PRIMCOORD"])+1][1] != "1":
            return False
        if not _determine_rest_of_xsf_file(rest_of_file=data_list[data_list.index(["PRIMCOORD"])+2:])[0]:
            return False
        if int(data_list[data_list.index(["PRIMCOORD"])+1][0]) == _determine_rest_of_xsf_file(rest_of_file=data_list[data_list.index(["PRIMCOORD"])+2:])[1]:
            return True
        return False
    elif ["ATOMS"] in data_list:
        if not _determine_rest_of_xsf_file(rest_of_file=data_list[data_list.index(["ATOMS"])+1:])[0]:
            return False
        return True
    else:
        return False

def _create_from_xsf_file_data(file_data: list[list[str]]) -> ABCMolecule | XYZMolecule:
    """Creates ABCMolecule object or XYZMolecule object from .xsf file_data.

    Parameters
    ----------
    file_data : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    ABCMolecule | XYZMolecule
        ABCMolecule object or XYZMolecule object containing structure data from .xsf file.
    """
    if not _isxsflist(data_list=file_data):
        raise RuntimeError("_create_from_xsf_file_data() required argument 'file_data' is not a xsf file.") # yapf: disable
    if ["CONVVEC"] in file_data:
        # pass #abc format
        raise NotImplementedError("read_xsf(): DEPRECATION WARNING: Not currently supported to save CONVVEC Information.") # yapf: disable
    if ["ATOMS"] in file_data:
        xyz_atoms: list[XYZCoord] = list()
        tot = _determine_rest_of_xsf_file(rest_of_file=file_data[file_data.index(["ATOMS"])+1:])[1]
        for line in file_data[file_data.index(["ATOMS"])+1:file_data.index(["ATOMS"])+tot]:
            xyz_atoms.append(XYZCoord(sp=ACCEPTED_ELEMENTS[int(line[0])],x=float(line[1]),y=float(line[2]),z=float(line[3])))
        return XYZMolecule(atoms=xyz_atoms, comment_line="from .xsf format",filetype=".xsf")
    else:
        abc_atoms: list[ABCCoord] = list()
        tot = int(file_data[file_data.index(["PRIMCOORD"])+1][0])
        for line in file_data[file_data.index(["PRIMCOORD"])+2:file_data.index(["PRIMCOORD"])+2+tot]:
            abc_atoms.append(ABCCoord(sp=ACCEPTED_ELEMENTS[int(line[0])],a=float(line[1]),b=float(line[2]),c=float(line[3])))
        uc_ind = file_data.index(["PRIMVEC"])
        unitcell = LatticeMatrix(constant=1,
                                 vector_1=[float(file_data[uc_ind+1][0]),float(file_data[uc_ind+1][1]),float(file_data[uc_ind+1][2])],
                                 vector_2=[float(file_data[uc_ind+2][0]),float(file_data[uc_ind+2][1]),float(file_data[uc_ind+2][2])],
                                 vector_3=[float(file_data[uc_ind+3][0]),float(file_data[uc_ind+3][1]),float(file_data[uc_ind+3][2])])
        return ABCMolecule(unitcell=unitcell,positional=False,atoms=abc_atoms,comment_line="from xsf file",filetype=".xsf",)

def read_xsf(filepath: str) -> ABCMolecule | XYZMolecule:
    """Reads .turbomole file and returns XYZMolecule instance.

    Parameters
    ----------
    filepath : str
        Filename (if in current working directory)
        or absolute path or os.path.join(os.getcwd(),'filename.xyz').

    Returns
    -------
    ABCMolecule | XYZMolecule
        ABCMolecule object or XYZMolecule object containing structure data from .xsf file.
    
    """
    if not isinstance(filepath, str):
        raise ValueError("read_vasp() required argument 'filepath' is not type string.") # yapf: disable
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError("read_vasp() required argument 'filepath' file does not exist.") # yapf: disable
    with open(filepath, "r") as openfile:
        file_data = [line.split() for line in openfile]
    return _create_from_xsf_file_data(file_data=file_data)


# ========================================================
#
#         siesta
#
# ========================================================


def _issiestalist(data_list: list[list[str]]) -> bool:
    """Return True if datalist fufills .siesta file standards, False otherwise.

    Parameters
    ----------
    data_list : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    bool
        True if .siesta file standards are met, False otherwise.
    """
    for line in data_list:
        if "LatticeConstant" in line:
            if not _isfloatstr(line[1]):
                return False
            if ['%block', 'LatticeVectors'] in data_list and ['%endblock', 'LatticeVectors'] in data_list:
                print(data_list[data_list.index(['%block', 'LatticeVectors'])+1:data_list.index(['%endblock', 'LatticeVectors'])]) # yapf: disable
                if not _regex_nested_string_list(nested_string_list=data_list[data_list.index(['%block', 'LatticeVectors'])+1:data_list.index(['%endblock', 'LatticeVectors'])],
                                                 pattern_list=[r"^[-+]?[0-9]*\.?[0-9]+$",
                                                               r"^[-+]?[0-9]*\.?[0-9]+$",
                                                               r"^[-+]?[0-9]*\.?[0-9]+$"]):
                    return False
                break
            else:
                return False
    if ['%block', 'AtomicCoordinatesAndAtomicSpecies'] not in data_list or ['%endblock', 'AtomicCoordinatesAndAtomicSpecies'] not in data_list:
        return False
    for line in data_list[data_list.index(['%block', 'AtomicCoordinatesAndAtomicSpecies'])+1:data_list.index(['%endblock', 'AtomicCoordinatesAndAtomicSpecies'])]:
        if len(line) < 4:
            return False
        if not _isfloatstr(line[0]) or not _isfloatstr(line[1]) or not _isfloatstr(line[2]):
            return False
        if not line[3].isdecimal():
            return False
    return True

def _create_from_siesta_file_data(file_data: list[list[str]]) -> ABCMolecule:
    """Creates ABCMolecule object from siesta file_data.

    Parameters
    ----------
    file_data : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    ABCMolecule
        ABCMolecule object with structure data from siesta file.
    """
    if not _issiestalist(data_list=file_data):
        raise RuntimeError("_create_from_siesta_file_data() required argument 'file_data' is not a siesta file.") # yapf: disable
    for line in file_data:
        if "LatticeConstant" in line:
            constant = float(line[1])
    lattice = file_data[file_data.index(['%block', 'LatticeVectors'])+1:file_data.index(['%endblock', 'LatticeVectors'])]
    unitcell = LatticeMatrix(
        constant=constant,
        vector_1=[float(lattice[0][0]),float(lattice[0][1]),float(lattice[0][2])],
        vector_2=[float(lattice[1][0]),float(lattice[1][1]),float(lattice[1][2])],
        vector_3=[float(lattice[2][0]),float(lattice[2][1]),float(lattice[2][2])])
    abc_atoms: list[ABCCoord] = list()
    for line in file_data[file_data.index(['%block', 'AtomicCoordinatesAndAtomicSpecies'])+1:file_data.index(['%endblock', 'AtomicCoordinatesAndAtomicSpecies'])]:
        abc_atoms.append(ABCCoord(sp=ACCEPTED_ELEMENTS[int(line[3])],a=float(line[0]),b=float(line[1]),c=float(line[2])))
    return ABCMolecule(unitcell=unitcell, positional=True, atoms=abc_atoms,comment_line="from siesta input deck",filetype=".fdf",)

def read_siesta(filepath: str) -> ABCMolecule:
    """Reads .siesta file and returns ABCMolecule instance.

    Parameters
    ----------
    filepath : str
        Filename (if in current working directory)
        or absolute path or os.path.join(os.getcwd(),'filename.xyz').

    Returns
    -------
    ABCMolecule
        ABCMolecule object with structure data from siesta file.
    """
    if not isinstance(filepath, str):
        raise ValueError("read_siesta() required argument 'filepath' is not type string.") # yapf: disable
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError("read_siesta() required argument 'filepath' file does not exist.") # yapf: disable
    with open(filepath, "r") as openfile:
        file_data = [line.split() for line in openfile]
    return _create_from_siesta_file_data(file_data=file_data)


# ========================================================
#
#         LAMMPS
#
# ========================================================


def _islammpslist(data_list: list[list[str]], debug_print: bool = False) -> bool:
    """Return True if data list fufills LAMMPS file standards, False otherwise.

    Parameters
    ----------
    data_list : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    bool
        True if data_list fufills LAMMPS file standards.
    """
    regex_pos_float = r"^[0-9]*\.?[0-9]+$"
    regex_float_with_e = r"^[-+]?[0-9]+[.]?[0-9]*([eE][-+]?[0-9]+)?$"
    regex_pos_int = "^[0-9]+$"
    has_atoms, atom_index = _regex_nested_string_list(
        nested_string_list=data_list, pattern_list=[regex_pos_int, "^atoms$"])
    if has_atoms is False:
        if debug_print:
            print("False 1")
        return False
    atom_total = int(data_list[atom_index][0])
    has_atom_types, atom_types_index = _regex_nested_string_list(
        nested_string_list=data_list,
        pattern_list=[regex_pos_int, "^atom$", "^types$"])
    if has_atom_types is False:
        if debug_print:
            print("False 2")
        return False
    atom_types = int(data_list[atom_types_index][0])
    if _regex_nested_string_list(nested_string_list=data_list,
                                 pattern_list=[
                                     regex_float_with_e,
                                     regex_float_with_e, "^xlo$",
                                     "^xhi$"
                                 ])[0] is False:
        if debug_print:
            print("False 3")
        return False
    if _regex_nested_string_list(nested_string_list=data_list,
                                 pattern_list=[
                                     regex_float_with_e,
                                     regex_float_with_e, "^ylo$",
                                     "^yhi$"
                                 ])[0] is False:
        if debug_print:
            print("False 4")
        return False
    if _regex_nested_string_list(nested_string_list=data_list,
                                 pattern_list=[
                                     regex_float_with_e,
                                     regex_float_with_e, "^zlo$",
                                     "^zhi$"
                                 ])[0] is False:
        if debug_print:
            print("False 5")
        return False
    has_masses, masses_index = _regex_nested_string_list(
        nested_string_list=data_list, pattern_list=["^Masses$"])
    if has_masses is False:
        if debug_print:
            print("False 6")
        return False
    has_first_mass, first_mass_line_index_return = _regex_nested_string_list(
        nested_string_list=data_list[masses_index:],
          pattern_list=[f"^1$", regex_pos_float],
            strict_on_length=True)
    first_mass_line_index = masses_index + first_mass_line_index_return
    if has_first_mass is False:
        if debug_print:
            print("False 13")
        return False
    for n, line in enumerate(data_list[first_mass_line_index:first_mass_line_index + atom_types]):
        if _regex_string_list(
                string_list=line,
                pattern_list=[f"^{n+1}$", regex_pos_float], strict_on_length=True) is False:
            if debug_print:
                print("False 7")
            return False
    if _regex_nested_string_list(nested_string_list=data_list,
                                 pattern_list=["^Atoms$"])[0] is False:
        if debug_print:
            print("False 8")
        return False
    has_first_atom_line, first_atom_line_index = _regex_nested_string_list(
        nested_string_list=data_list,
        pattern_list=[
            regex_pos_int, regex_pos_int, regex_pos_int, regex_float_with_e,
            regex_float_with_e, regex_float_with_e
        ])
    if has_first_atom_line is False:
        if debug_print:
            print("False 9")
        return False
    for line in data_list[first_atom_line_index:first_atom_line_index +
                          atom_total]:
        if _regex_string_list(string_list=line,
                              pattern_list=[
                                  regex_pos_int, regex_pos_int, regex_pos_int,
                                  regex_float_with_e,
                                  regex_float_with_e,
                                  regex_float_with_e
                              ]) is False:
            if debug_print:
                print("False 10")
            return False
    return True

def _create_from_lammps_file_data(file_data: list[list[str]], mol_type: str, debug_print: bool = False) -> ABCMolecule:
    """Creates ABCMolecule object or XYZMolecule object from LAMMPS file_data.

    Parameters
    ----------
    file_data : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.
    mol_type : "{'XYZMolecule' or 'ABCMolecule-direct' or 'ABCMolecule-cartesian'}"
        Type of Molecule object function will return.

    Returns
    -------
    ABCMolecule | XYZMolecule
        ABCMolecule object or XYZMolecule object containing structure data from LAMMPS file depending on argument 'mol_type'.
    """
    regex_pos_float = r"^[0-9]*\.?[0-9]+$"
    regex_float_with_e = r"^[-+]?[0-9]+[.]?[0-9]*([eE][-+]?[0-9]+)?$"
    regex_pos_int = "^[0-9]+$"
    if not _islammpslist(data_list=file_data, debug_print=debug_print):
        raise RuntimeError("_create_from_lammps_file_data() required argument 'file_data' is not a lammps file.") # yapf: disable
    if mol_type not in ["ABCMolecule-direct", "ABCMolecule-cartesian"]:
        raise ValueError("_create_from_lammps_file_data() mol_type not in 'XYZMolecule','ABCMolecule-direct' or 'ABCMolecule-cartesian'.") # yapf: disable
    _, atom_index = _regex_nested_string_list(
        nested_string_list=file_data, pattern_list=["^[0-9]+$", "^atoms$"])
    atom_total = int(file_data[atom_index][0])
    _, atom_types_index = _regex_nested_string_list(
        nested_string_list=file_data,
        pattern_list=["^[0-9]+$", "^atom$", "^types$"])
    atom_types = int(file_data[atom_types_index][0])
    _, xbox_index = _regex_nested_string_list(nested_string_list=file_data,
                                              pattern_list=[
                                                  regex_float_with_e,
                                                  regex_float_with_e,
                                                  "^xlo$", "^xhi$"
                                              ])
    x_range = abs(
        float(file_data[xbox_index][1]) - float(file_data[xbox_index][0]))
    _, ybox_index = _regex_nested_string_list(nested_string_list=file_data,
                                              pattern_list=[
                                                  regex_float_with_e,
                                                  regex_float_with_e,
                                                  "^ylo$", "^yhi$"
                                              ])
    y_range = abs(
        float(file_data[ybox_index][1]) - float(file_data[ybox_index][0]))
    _, zbox_index = _regex_nested_string_list(nested_string_list=file_data,
                                              pattern_list=[
                                                  regex_float_with_e,
                                                  regex_float_with_e,
                                                  "^zlo$", "^zhi$"
                                              ])
    z_range = abs(
        float(file_data[zbox_index][1]) - float(file_data[zbox_index][0]))
    _, masses_index = _regex_nested_string_list(nested_string_list=file_data,
                                                pattern_list=["^Masses$"])
    _, first_mass_line_index_return = _regex_nested_string_list(
        nested_string_list=file_data[masses_index:], pattern_list=[f"^1$", regex_pos_float])
    _, first_atom_line_index = _regex_nested_string_list(
        nested_string_list=file_data,
        pattern_list=[
            regex_pos_int, regex_pos_int, regex_pos_int, regex_float_with_e,
            regex_float_with_e, regex_float_with_e
        ])
    masses_dict: dict[str, str] = dict()
    first_mass_line_index = masses_index + first_mass_line_index_return
    for line in file_data[first_mass_line_index:first_mass_line_index + atom_types]:
        for sp in MOLAR_MASS:
            if _is_ae([MOLAR_MASS[sp], float(line[1])],
                      tolerance_percentage=0.5):
                masses_dict[line[0]] = sp
    unitcell = LatticeMatrix(constant=1,
                             vector_1=[x_range, 0, 0],
                             vector_2=[0, y_range, 0],
                             vector_3=[0, 0, z_range])
    atoms = list()
    for line in file_data[first_atom_line_index:first_atom_line_index +
                          atom_total]:
        if mol_type == "ABCMolecule-direct":
            atoms.append(
                ABCCoord(sp=masses_dict[line[1]],
                         a=float(line[3]) / x_range,
                         b=float(line[4]) / y_range,
                         c=float(line[5]) / z_range))
        elif mol_type == "ABCMolecule-cartesian":
            atoms.append(
                ABCCoord(sp=masses_dict[line[1]],
                         a=float(line[3]),
                         b=float(line[4]),
                         c=float(line[5])))
        else:
            atoms.append(
                XYZCoord(sp=masses_dict[line[1]],
                         x=float(line[3]),
                         y=float(line[4]),
                         z=float(line[5])))
    # if mol_type == "XYZMolecule":
    #     return XYZMolecule(atoms=atoms,
    #                        comment_line="from lammps",
    #                        filetype=".lammps")
    if mol_type == "ABCMolecule-direct":
        return ABCMolecule(unitcell=unitcell,
                           positional=True,
                           atoms=atoms,
                           comment_line="from lammps input deck",
                           filetype=".lammps")
    else: #if mol_type == "ABCMolecule-cartesian":
        return ABCMolecule(unitcell=unitcell,
                           positional=False,
                           atoms=atoms,
                           comment_line="from lammps input deck",
                           filetype=".lammps")

def read_lammps(filepath: str, mol_type: str, debug_print: bool = False) -> ABCMolecule:
    """Read Lammps file and creates a Molecule object based on mol_type argument.

    Parameters
    ----------
    filepath : str
        Filename (if in current working directory)
        or absolute path or os.path.join(os.getcwd(),'filename.xyz')
    mol_type : "{'XYZMolecule' or 'ABCMolecule-direct' or 'ABCMolecule-cartesian'}"
        What kind of molecule object you want it to save as.

    Returns
    -------
    ABCMolecule | XYZMolecule
        ABCMolecule object if mol_type = 'ABCMolecule-direct' or 'ABCMolecule-cartesian' and XYZMoelcule object if mol_type = 'XYZMolecule'.
    """
    if not isinstance(filepath, str):
        raise ValueError("read_vasp() required argument 'filepath' is not type string.") # yapf: disable
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError("read_vasp() required argument 'filepath' file does not exist.") # yapf: disable
    with open(filepath, "r") as openfile:
        file_data = [line.split() for line in openfile]
    return _create_from_lammps_file_data(file_data=file_data, mol_type=mol_type, debug_print=debug_print)

def generate_lammps(filepath: str, x: int, y: int, z: int, mol_type: str, compress_species_line: bool = False) -> ABCMolecule:
    """Reads POSCAR file and generates a supercell for a lammps input file.

    Parameters
    ----------
    filepath : str
        Filename (if in current working directory)
        or absolute path or os.path.join(os.getcwd(),'filename.xyz')
    x : int >= 1
        Amount in the x direction the structure will be multiplied by.
    y : int >= 1
        Amount in the y direction the structure will be multiplied by.
    z : int >= 1
        Amount in the z direction the structure will be multiplied by.
    mol_type : "{'XYZMolecule' or 'ABCMolecule-direct' or 'ABCMolecule-cartesian'}"
        What kinda of molecule object you want it to save as.
    compress_species_line : bool default False
        If you want to decompress the species line into smallest length possible.

    Returns
    -------
    ABCMolecule | XYZMolecule
        ABCMolecule object if mol_type = 'ABCMolecule-direct' or 'ABCMolecule-cartesian' and XYZMoelcule object if mol_type = 'XYZMolecule'.
    """
    if not isinstance(filepath, str):
        raise ValueError("generate_lammps() required argument 'filepath' is not type string.") # yapf: disable
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError("generate_lammps() required argument 'filepath' file does not exist.") # yapf: disable
    with open(filepath, "r") as openfile:
        file_data = [line.split() for line in openfile]
    #commented out because I only want to have a vasp file input to keep unitcell information
    # if _isxyzlist(file_data):
    #     read_file = _create_from_xyz_file_data(file_data=file_data)
    if _isvasplist(file_data):
        read_file = _create_from_vasp_file_data(file_data=file_data)
    new_file = read_file.generate_supercell(x=x, y=y, z=z)
    if mol_type not in ["ABCMolecule-direct", "ABCMolecule-cartesian"]:
        raise ValueError("generate_lammps() required argument 'mol_type' not in 'XYZMolecule','ABCMolecule-direct' or 'ABCMolecule-cartesian'.") # yapf: disable
    if compress_species_line:
        sort_method: list[str] = set(new_file.species_line) # type: ignore
        new_file.sort(sort_method, inplace=True)
    if new_file.positional:
        if mol_type == "ABCMolecule-direct":
            return new_file
        else: #if mol_type == "ABCMolecule-cartesian":
            return new_file.convert().convert(lattice_matrix=new_file.unitcell,positional=False)
    else:
        if mol_type == "ABCMolecule-cartesian":
            return new_file
        else: #if mol_type == "ABCMolecule-direct":
            return new_file.convert().convert(lattice_matrix=new_file.unitcell,positional=True)
    # # new_file.comment_line = f"lammps box dimensions:  a, b, c (angstrom) = {new_file.unitcell.getabc()} alpha, beta, gamma (deg) = {new_file.unitcell.getanglesdeg()}"
    # new_file.comment_line = "lammps box dimensions:  " + new_file.unitcell.getcommentline()
    # return new_file.convert()



# ========================================================
#
#         read_xyz_animation
#
# ========================================================


def _isxyzanimationlist(data_list: list[list[str]], debug_print: bool = False) -> bool:
    """Return True if datalist fufills .xyz animation file standards, False otherwise.

    Parameters
    ----------
    data_list : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    bool
        True if .xyz animation file standards are met, False otherwise.

    Notes
    -----
    .xyz animation file standards:
        - different iterations are .xyz file appended to eachother.
    """
    if _regex_string_list(string_list=data_list[0],
                          pattern_list=[r"^\d+$"],
                          strict_on_length=True) is False:
        if debug_print:
            print("False 1")
        return False
    total_atoms = int(data_list[0][0])
    if debug_print:
        print(f"{len(data_list)/(total_atoms+2)=}")
    for n in range(ceil(len(data_list)/(total_atoms+2))):
        iteration_list = data_list[n*(total_atoms+2):n*(total_atoms+2) + (total_atoms+2)]
        if debug_print:
            print(f"iteration {n}")
            print(f"{n} = {n*(total_atoms+2)} : {n*(total_atoms+2) + (total_atoms+2)}") # yapf: disable
        if _regex_string_list(string_list=iteration_list[0],
                          pattern_list=[r"^\d+$"],
                          strict_on_length=True) is False:
            if debug_print:
                print(f"False 1-{n}")
            return False
        if len(iteration_list) < total_atoms+2:
            if debug_print:
                print(f"False 2-{n}")
            return False
        for line in iteration_list[2:total_atoms+2]:
            if _regex_string_list(string_list=line,
                                pattern_list=["^("+"|".join(ACCEPTED_ELEMENTS)+")$",
                                                r"^[-+]?[0-9]*\.?[0-9]+$",
                                                r"^[-+]?[0-9]*\.?[0-9]+$",
                                                r"^[-+]?[0-9]*\.?[0-9]+$"],
                                strict_on_length=False) is False:
                if debug_print:
                    print(f"False 3-{n}")
                    print(f"false line = {line}")
                return False
    if debug_print:
        print("True")
    return True


def _create_from_xyz_animation_file_data(file_data: list[list[str]], debug_print: bool = False) -> XYZAnimation:
    """Creates XYZAnimation object from .xyz animation file_data.

    Parameters
    ----------
    file_data : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    XYZAnimation
        XYZAnimation object containing structure data from .xyz animation file.
    """
    if not _isxyzanimationlist(data_list=file_data, debug_print=debug_print):
        raise RuntimeError("_create_from_xyz_animation_file_data() required argument 'file_data' is not an xyz animation file.") # yapf: disable
    animation_dict: dict[int, XYZMolecule] = dict()
    total_atoms = int(file_data[0][0])
    for n in range(int(len(file_data)/(total_atoms+2))):
        atoms = list()
        for line in file_data[n*(total_atoms+2)+2:n*(total_atoms+2) + (total_atoms+2)]:
            atoms.append(XYZCoord(sp=line[0],
                                  x=float(line[1]),
                                  y=float(line[2]),
                                  z=float(line[3])))
        animation_dict[n] = XYZMolecule(atoms=atoms,
                                        comment_line=f"Iteration {n} "+" ".join(file_data[n*(total_atoms+2)+1]),
                                        filetype=".xyz")
    return XYZAnimation(animation_dict=animation_dict)


def read_xyz_animation(filepath: str, debug_print: bool = False) -> XYZAnimation:
    """Reads .xyz animation file and returns XYZAnimation instance.

    Parameters
    ----------
    filepath : str
        Filename (if in current working directory)
        or absolute path or os.path.join(os.getcwd(),'filename.xyz').

    Returns
    -------
    XYZAnimation
        XYZAnimation object containing structure data from .xyz animation file.
    """
    if not isinstance(filepath, str):
        raise ValueError("read_xyz_animation() required argument 'filepath' is not type string.") # yapf: disable
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError("read_xyz_animation() required argument 'filepath' file does not exist.") # yapf: disable
    with open(filepath, "r") as openfile:
        file_data = [line.split() for line in openfile]
    return _create_from_xyz_animation_file_data(file_data=file_data, debug_print=debug_print)


# ========================================================
#
#         read_xyz_animation
#
# ========================================================


def _isxdatcarlist(data_list: list[list[str]], debug_print: bool = False) -> tuple[bool,bool]:
    """Return True if datalist fufills .xdatcar file standards, False otherwise.

    Parameters
    ----------
    data_list : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    bool,bool
        1st bool True if .xdatcar file standards are met, False otherwise.
        2nd bool True if repeating unit cell is True, False if repeating unitcell is false.
    Notes
    -----
    .xdatcar file standards:
        - 
    """
    if _isvasplist(data_list=data_list) is False:
        if debug_print:
            print("False 1")
        return False, False
    total_atoms = sum([int(i) for i in data_list[6]])
    if _regex_string_list(string_list=data_list[7],
                          pattern_list=["^S.*"]):
        top_lines = 9
    else:
        top_lines = 8
        if _regex_string_list(string_list=data_list[7],
                          pattern_list=["^D.*"]):
            direct_car_regex = ["^D.*","None",r"^\d+$"]
        else:
            direct_car_regex = ["^S.*","None",r"^\d+$"]
    rest_of_file = data_list[(total_atoms+top_lines):]
    not_repeating_cell = list()
    repeating_cell = list()
    if debug_print:
        print(rest_of_file[:5])
        print(f"{ceil(len(rest_of_file)/(total_atoms+1))=}")
        print(f"{(len(data_list)-(total_atoms+top_lines))/(total_atoms+1)=}")
    for n in range(1,int(len(data_list)/(total_atoms+top_lines))):
        iteration_text = rest_of_file[n*(total_atoms+top_lines):n*(total_atoms+top_lines)+(total_atoms+top_lines)]
        if debug_print:
            pass
            print(iteration_text)
        if _isvasplist(iteration_text):
            not_repeating_cell.append(True)
        else:
            not_repeating_cell.append(False)
    for n in range(ceil(len(rest_of_file)/(total_atoms+1))):
        iteration_text = rest_of_file[n*(total_atoms+1):n*(total_atoms+1)+(total_atoms+1)]
        if debug_print:
            print(f"{n}")
            print(f"head{iteration_text[:3]}")
            print(f"tail{iteration_text[-1]}")
        if _regex_string_list(string_list=iteration_text[0],
                          pattern_list=direct_car_regex) is False:
            if debug_print:
                print(f"{n}False direct_car")
            repeating_cell.append(False)
            break
        if len(iteration_text) < (total_atoms+1):
            if debug_print:
                print(f"{n} False len")
                print(f"{len(iteration_text) < (total_atoms+1) = }")
            repeating_cell.append(False)
            break
        for line in iteration_text[1:]:
            if _regex_string_list(string_list=line,
                pattern_list=[r"^[-+]?[0-9]*\.?[0-9]+$",
                        r"^[-+]?[0-9]*\.?[0-9]+$",
                        r"^[-+]?[0-9]*\.?[0-9]+$"]) is False:
                if debug_print:
                    print(f"False = {line}")
                repeating_cell.append(False)
                break
        repeating_cell.append(True)

    if all(not_repeating_cell):
        if debug_print:
            print("True not repeating")
        return True, False
    elif all(repeating_cell):
        if debug_print:
            print("True repeating")
        return True, True
    else:
        if debug_print:
            print("False 2")
        return False, False


def _create_from_xdatcar_file_data(file_data: list[list[str]], debug_print: bool = False) -> ABCAnimation:
    """Creates ABCAnimation object from .xdatcar file_data.

    Parameters
    ----------
    file_data : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    ABCAnimation
        ABCAnimation object containing structure data from .xdatcar file.
    """
    is_xdatcar, repeating_unitcell = _isxdatcarlist(data_list=file_data, debug_print=debug_print)
    if not is_xdatcar:
        raise RuntimeError("_create_from_xyz_animation_file_data() required argument 'file_data' is not an xdatcar file.") # yapf: disable
    if repeating_unitcell:
        animation_dict: dict[int, ABCMolecule] = dict()
        total_atoms = sum([int(i) for i in file_data[6]])
        if _regex_string_list(string_list=file_data[7],
                            pattern_list=["^S.*"]):
            raise NotImplementedError("_create_from_xdatcar_file_data() cannot read xdatcar file that has selective coords.") # yapf: disable
        else:
            top_lines = 8
        total = int(sum([int(file_data[6][i]) for i in range(len(file_data[6]))]))
        init_data = file_data[8:total+8]
        sp = [file_data[5][i] for i in range(len(file_data[5])) for _ in range(int(file_data[6][i]))]
        if "C" in file_data[7][0] or "C" in file_data[8][0]:
            positional = False
        else:
            positional = True
        atoms = [
        ABCCoord(
            sp[i],
            float(init_data[i][0]),
            float(init_data[i][1]),
            float(init_data[i][2])
        )
        for i in range(total)
        ]
        unitcell = LatticeMatrix(
            constant=float(file_data[1][0]),
            vector_1=[float(file_data[2][i]) for i in range(3)],
            vector_2=[float(file_data[3][i]) for i in range(3)],
            vector_3=[float(file_data[4][i]) for i in range(3)],
        )
        animation_dict[0] = ABCMolecule(unitcell=unitcell,
                                        positional=positional,
                                        atoms=atoms,
                                        comment_line=" ".join(file_data[7]),
                                        filetype=".vasp")
        rest_of_file = file_data[(total_atoms+top_lines):]
        for n in range(ceil(len(rest_of_file)/(total_atoms+1))):
            iteration_text = rest_of_file[n*(total_atoms+1):n*(total_atoms+1)+(total_atoms+1)]
            iteration_atoms: list[ABCCoord]  = [
                                                ABCCoord(
                                                    sp[i-1],
                                                    float(iteration_text[i][0]),
                                                    float(iteration_text[i][1]),
                                                    float(iteration_text[i][2])
                                                )
                                                for i in range(1,total+1)
                                            ]
            animation_dict[n+1] = ABCMolecule(unitcell=unitcell,
                                              positional=positional,
                                              atoms=iteration_atoms,
                                              comment_line=" ".join(iteration_text[0]),
                                              filetype=".vasp")
        return ABCAnimation(animation_dict=animation_dict,repeating_unitcell=repeating_unitcell)
    else:
        raise NotImplementedError("_create_from_xdatcar_file_data() not reapeating unit cell not implemented yet.") # yapf: disable



def read_xdatcar(filepath: str, debug_print: bool = False) -> ABCAnimation:
    """Reads .xdatcar file and returns ABCAnimation instance.

    Parameters
    ----------
    filepath : str
        Filename (if in current working directory)
        or absolute path or os.path.join(os.getcwd(),'filename.xyz').

    Returns
    -------
    ABCAnimation
        ABCAnimation object containing structure data from .xdatcar file.
    """
    if not isinstance(filepath, str):
        raise ValueError("read_xdatcar() required argument 'filepath' is not type string.") # yapf: disable
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError("read_xdatcar() required argument 'filepath' file does not exist.") # yapf: disable
    with open(filepath, "r") as openfile:
        file_data = [line.split() for line in openfile]
    return _create_from_xdatcar_file_data(file_data=file_data, debug_print=debug_print)


# ========================================================
#
#         Reading cif file using cif2pos
# #https://github.com/tamaswells/VASP_script/blob/master/cif2poscar/cif2pos.py
# ========================================================



def _create_from_cif_file_data(filepath:str) -> ABCMolecule:
    """Creates ABCMolecule object from .cif file_data.

    Parameters
    ----------
    file_data : (list of filelines.split())
        Is a list of list of filelines
        where each string in the file line seperated by a space is its own
        element in the list. data_list[0] is the contains the first line
        information of the file and data_list[-1] contains the last line
        0 information of the file.

    Returns
    -------
    ABCMolecule
        ABCMolecule object containing structure data from .cif file.
    
    Notes
    -----
    ABCMolecule object created using cif2pos 
        https://github.com/tamaswells/VASP_script/blob/master/cif2poscar/cif2pos.py 
        Copyright 2011 Li Zhu <zhulipresent@gmail.com> 
        Licensed under the GPL V3 
        Version: 1.0.1
        Modified by NXU <tamas@zju.edu.cn>
        update: 2019.3.1
        using symmetry data from cif2cell package
        Modified bu IMU
        update:2020.08.18
    """
    try:
        cif = readfile(filepath)
        s = symmetry(cif)
        a,labels = atominfo(cif)
        l =  lattice(cif)
        order = a.keys()
        (p, t) = p1atom(order, a, s[0], s[1],labels)
        unitcell = LatticeMatrix(constant=1.0, vector_1=l[0],vector_2=l[1],vector_3=l[2])
        sp_list = list()
        for sp, num in zip(order, t):
            sp_list.extend([sp]*num)
        atoms: list[ABCCoord] = list()
        for sp, coord in zip(sp_list, p):
            atoms.append(ABCCoord(sp=sp,
                                a=coord[0],
                                b=coord[1],
                                c=coord[2]))
        return ABCMolecule(unitcell=unitcell,
                        positional=True,
                        atoms=atoms,
                        comment_line="ABCMolecule object created by using cif2pos https://github.com/tamaswells/VASP_script/blob/master/cif2poscar/cif2pos.py Copyright 2011 Li Zhu <zhulipresent@gmail.com> Licensed under the GPL V3 Version: 1.0.1",
                        filetype=".cif")
    except:
        raise RuntimeError("_create_from_cif_file_data() Error occured with reading supposed .cif file. Try again or convert .cif file to POSCAR format using an external program and use read_vasp() function.") # yapf: disable


def read_cif(filepath: str) -> ABCMolecule:
    """Reads .cif file and returns ABCMolecule instance.

    Parameters
    ----------
    filepath : str
        Filename (if in current working directory)
        or absolute path or os.path.join(os.getcwd(),'filename.xyz').

    Returns
    -------
    ABCMolecule
        ABCMolecule object containing structure data from .cif file.
    
    Notes
    -----
    ABCMolecule object created using cif2pos 
        https://github.com/tamaswells/VASP_script/blob/master/cif2poscar/cif2pos.py 
        Copyright 2011 Li Zhu <zhulipresent@gmail.com> 
        Licensed under the GPL V3 
        Version: 1.0.1
        Modified by NXU <tamas@zju.edu.cn>
        update: 2019.3.1
        using symmetry data from cif2cell package
        Modified bu IMU
        update:2020.08.18
    """
    if not isinstance(filepath, str):
        raise ValueError("read_xdatcar() required argument 'filepath' is not type string.") # yapf: disable
    if os.path.isfile(filepath) is False:
        raise FileNotFoundError("read_xdatcar() required argument 'filepath' file does not exist.") # yapf: disable
    return _create_from_cif_file_data(filepath=filepath)




# ========================================================
#
#        implementing rdkit and ase modules
#
# ========================================================

# def from_rdkit_mol(rdkit_mol: rdkit_Chem_rdchem_Mol) -> XYZMolecule:
#     if not isinstance(rdkit_mol, rdkit_Chem_rdchem_Mol):
#         print()




# ========================================================
#
#         END OF new_molecule library SECTION
#               yay you made it!!!
#
# ========================================================
