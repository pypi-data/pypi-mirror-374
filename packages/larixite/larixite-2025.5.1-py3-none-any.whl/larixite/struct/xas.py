#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Atomic structure with an absorber element
==========================================
"""

import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import Union, List, Literal
from random import Random
from pymatgen.core import Molecule, Structure, Element, Site
from larixite.utils import fcompact, get_logger, pprint

TOIMPLEMENT = "To implement as subclass, depending on the input structure file format"
logger = get_logger("larixite.struct")
rng = Random()


def site_label(site: Site) -> str:
    """
    return a string label for a pymatgen Site object,
    using the species string and fractional coordinates

    Parameters
    ----------
    site : pymatgen Site object

    Returns
    -------
    str
    """
    try:
        site_coords = site.frac_coords
    except AttributeError:
        site_coords = site.coords
    coords = ",".join([fcompact(s) for s in site_coords])
    return f"{site.species_string}[{coords}]"


@dataclass
class XasStructure:
    """Data model for an atomic structure with an absorber element

    .. note::

        This class is agnostic of the file format for the atomic structure.
        Specific handling for different formats should be implemented in
        subclasses. The goal of this class is to provide a common API
        for manipulating atomic structures with an absorber element.

    """

    name: str  #: unique name, usually the input filename
    label: str  #: a short label, usually the input filename without extension
    filepath: Path  #: Path object to the input file
    structure: Structure  #: pymatgen Structure
    molecule: Molecule  #: pymatgen Molecule
    absorber: Element  #: pymatgen Element for the absorber
    radius: float = 7  #: radius of the absorption sphere from the absorbing atom
    radius_ext: float = 2.5  #: radius extension of the absorption sphere => cluster_size = radius + radius_ext
    struct_type: str = Literal["crystal", "molecule"]  #: type of the structure

    def __post_init__(self):
        self._absorber_idx = self.get_absorber_indexes()[0]
        self.build_sites()

    @property
    def absorber_idx(self):
        assert self._absorber_idx is not None, "Absorber index not set!"
        return self._absorber_idx

    @absorber_idx.setter
    def absorber_idx(self, value: int):
        idxerr = f"Absorber index {value} not valid -> cannot set absorber_idx"
        try:
            site = self.get_site(value)
        except IndexError:
            logger.error(idxerr)
            raise IndexError(idxerr)
        #: check absorber symbol is on selected site
        if self.absorber.symbol not in site.species_string:
            errmsg = f"Absorber {self.absorber.symbol} not in site {site.species_string} -> cannot set absorber_idx"
            logger.error(errmsg)
            raise IndexError(errmsg)
        idx_in_struct = self.get_absorber_indexes()
        if value in idx_in_struct:
            self._absorber_idx = value
        else:
            try:
                self._absorber_idx = self.get_absorber_indexes()[value]
            except IndexError:
                logger.error(idxerr)
                raise IndexError(idxerr)

    @property
    def cluster_size(self):
        """The size of the cluster is larger than the radius"""
        return self.radius + self.radius_ext

    @cluster_size.setter
    def cluster_size(self, value: float):
        self.radius = value - self.radius_ext

    @property
    def site_labels(self):
        """List all sites, e.g. `Fe[0.125,0.125,0.125]`"""
        return [site_label(site) for site in self.struct.sites]

    @property
    def formula(self):
        return self.struct.composition.reduced_formula

    @property
    def absorber_site(self):
        if self.absorber_idx is None:
            errmsg = "Absorber site index not set!"
            logger.error(errmsg)
            return IndexError(errmsg)
        return self.struct[self.absorber_idx]

    @property
    def cluster(self):
        # return self.struct.get_sites_in_sphere(
        #    self.absorber_site.coords, self.cluster_size
        # )
        # return self.struct.get_neighbors(self.absorber_site, self.cluster_size)
        return self.build_cluster()

    @property
    def struct(self):
        raise NotImplementedError(TOIMPLEMENT)

    @property
    def sga(self):
        raise NotImplementedError(TOIMPLEMENT)

    @property
    def space_group(self):
        raise NotImplementedError(TOIMPLEMENT)

    @property
    def sym_struct(self):
        raise NotImplementedError(TOIMPLEMENT)

    @property
    def wyckoff_symbols(self):
        raise NotImplementedError(TOIMPLEMENT)

    @property
    def sites(self):
        raise NotImplementedError(TOIMPLEMENT)

    @property
    def equivalent_sites(self):
        raise NotImplementedError(TOIMPLEMENT)

    def get_site(self, site_index: int):
        return self.struct[site_index]

    def get_occupancy(self, site: Site, elem: Union[Element, None] = None) -> float:
        """Get the occupancy of a given element on a site

        Parameters
        ==========

        site: pymatgen.core.Site object
        elem: pymatgen.core.Element object or None
            if None: uses self.absorber

        Returns
        =======

        occupancy: float
        """
        if len(site.species.elements) == 1:
            return 1
        zelems = [el.Z for el in site.species.elements]
        if elem is None:
            elem = self.absorber
        if elem.Z not in zelems:
            logger.debug(f"Element {elem.name} not in site {site}")
            return 1
        ats_occ = site.species_string.split(",")
        at_occ = [at for at in ats_occ if elem.name in at][0]
        return float(at_occ.split(":")[1])

    def get_idx_in_struct(self, atom_coords):
        """Get the index corresponding to the given atomic coordinates (cartesian)"""
        for idx, atom in enumerate(self.struct.sites):
            if np.allclose(atom.coords, atom_coords, atol=0.001) is True:
                return idx
        errmsg = f"atomic coordinates {atom_coords} not found in self.struct.sites"
        logger.error(errmsg)
        # raise IndexError(errmsg)
        return None

    def get_absorber_indexes(self) -> List[int]:
        """Get the unique indexes of the absorbing element in the pymatgen structure (self.struct)"""
        absorber_indexes = []
        for sites in self.equivalent_sites:
            site = sites[0]
            if self.absorber.symbol in site.species_string:
                occupancy = self.get_occupancy(site)
                site_index = self.get_idx_in_struct(site.coords)
                if occupancy != 1:
                    logger.debug(
                        f"[{self.label}] absorber {self.absorber.symbol} has occupancy of {occupancy} on site {site_index}"
                    )
                absorber_indexes.append(site_index)
        if len(absorber_indexes) == 0:
            errmsg = (
                f"Absorber {self.absorber.symbol} not found in structure {self.name}"
            )
            logger.error(errmsg)
            raise AttributeError(errmsg)
        return absorber_indexes

    def build_sites(self):
        """Parse the symmetrized structure to set the following attributes

        unique_sites:   list of non equivalent sites
        absorber_sites: sublist of unique_sites with the absorber

        .. note::

            content of the lists: (i, site, site_index_in_struct, site_occupancy, len(sites), self.wyckoff_symbols[i], species_string)

        """
        self.unique_sites = []
        self.absorber_sites = []
        self.unique_map = {}
        absname = self.absorber.symbol
        for idx, sites in enumerate(self.equivalent_sites):
            site = sites[0]
            site_index = self.get_idx_in_struct(site.coords)
            site_occupancy = self.get_occupancy(site)
            site_tuple = (
                idx,
                site,
                site_index,
                site_occupancy,
                len(sites),
                self.wyckoff_symbols[idx],
            )
            self.unique_sites.append(site_tuple)
            for site in sites:
                self.unique_map[site_label(site)] = idx + 1
            if absname in site.species_string:
                self.absorber_sites.append(site_tuple)

        if len(self.absorber_sites) == 0:
            errmsg = (
                f"Absorber {self.absorber.symbol} not found in structure {self.name}"
            )
            logger.error(errmsg)
            raise AttributeError(errmsg)

    def build_cluster(self, radius: Union[float, None] = None):
        """Build a cluster around the absorber as pymatgen Molecule"""
        if radius is None:
            radius = self.cluster_size

        csize2 = radius**2

        cluster = {}
        site_atoms = {}  # map xtal site with list of atoms occupying that site
        site_tags = {}

        for i, site in enumerate(self.struct.sites):
            label = site_label(site)
            s_unique = self.unique_map.get(label, 0)
            site_species = [e.symbol for e in site.species]
            #: handle partial occupancy
            if len(site_species) > 1:
                s_els = [s.symbol for s in site.species.keys()]

                s_wts = [s for s in site.species.values()]
                site_atoms[i] = rng.choices(s_els, weights=s_wts, k=1000)
                site_tags[i] = f"({site.species_string:s})_{s_unique:d}"
            else:
                site_atoms[i] = [site_species[0]] * 1000
                site_tags[i] = f"{site.species_string:s}_{s_unique:d}"

        # atom0 = self.struct[a_index]
        atom0 = self.absorber_site
        sphere = self.struct.get_neighbors(atom0, radius)

        cluster["symbols"] = [self.absorber.symbol]
        cluster["coords"] = [np.array([0, 0, 0])]
        site0_species = [e.symbol for e in atom0.species]
        if len(site0_species) > 1:
            cluster["tags"] = [f"({atom0.species_string})_{self.absorber_idx:d}"]
        else:
            cluster["tags"] = [f"{atom0.species_string}_{self.absorber_idx:d}"]

        for i, site_dist in enumerate(sphere):
            s_index = site_dist[0].index
            site_symbol = site_atoms[s_index].pop()

            coords = site_dist[0].coords - atom0.coords
            if (coords[0] ** 2 + coords[1] ** 2 + coords[2] ** 2) < csize2:
                cluster["tags"].append(site_tags[s_index])
                cluster["symbols"].append(site_symbol)
                cluster["coords"].append(coords)

        return Molecule(cluster["symbols"], cluster["coords"], labels=cluster["tags"])

    def show_unique_sites(self):
        """Show a tabular print for self.unique_sites"""
        header = [
            "iunique",
            "istruct",
            "label",
            "frac_coords",
            "occu",
            "cart_coords",
            "nsites",
            "wyckoff",
            "species_string",
        ]
        infos = []
        for idx, site, istruct, occupancy, len_sites, wyckoff in self.unique_sites:
            try:
                frac_coords = site.frac_coords
            except AttributeError:
                frac_coords = [None, None, None]
            if istruct == self.absorber_idx:
                idx = f"{idx} (abs)"
            infos.append(
                [
                    idx,
                    istruct,
                    site.label,
                    frac_coords,
                    occupancy,
                    site.coords,
                    len_sites,
                    wyckoff,
                    site.species_string,
                ]
            )
        matrix = [header]
        matrix.extend(infos)
        print(f"Unique sites for {self.name}")
        pprint(matrix)
