#
# Copyright (C) 2017-2025  Leo Singer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Support for HEALPix UNIQ pixel indexing [1]_ and multi-order coverage (MOC)
maps [2]_.

References
----------
.. [1] Reinecke & Hivon, 2015. "Efficient data structures for masks on 2D
       grids." AA 580, A132. :doi:`10.1051/0004-6361/201526549`
.. [2] Boch et al., 2014. "MOC - HEALPix Multi-Order Coverage map." IVOA
       Recommendation <http://ivoa.net/documents/MOC/>.

"""

import astropy_healpix as ah
import numpy as np
from astropy import table
from astropy import units as u
from numpy.lib.recfunctions import repack_fields
from tqdm.auto import tqdm

from .core import nest2uniq, uniq2ang, uniq2nest, uniq2order, uniq2pixarea
from .core import rasterize as _rasterize
from .util.numpy import add_newdoc_ufunc

__all__ = (
    "nest2uniq",
    "uniq2nest",
    "uniq2order",
    "uniq2pixarea",
    "uniq2ang",
    "rasterize",
    "bayestar_adaptive_grid",
)


add_newdoc_ufunc(
    nest2uniq,
    """\
Convert a pixel index from NESTED to NUNIQ ordering.

Parameters
----------
order : `numpy.ndarray`
    HEALPix resolution order, the logarithm base 2 of `nside`
ipix : `numpy.ndarray`
    NESTED pixel index

Returns
-------
uniq : `numpy.ndarray`
    NUNIQ pixel index

""",
)


add_newdoc_ufunc(
    uniq2order,
    """\
Determine the HEALPix resolution order of a HEALPix NESTED index.

Parameters
----------
uniq : `numpy.ndarray`
    NUNIQ pixel index

Returns
-------
order : `numpy.ndarray`
    HEALPix resolution order, the logarithm base 2 of `nside`

""",
)


add_newdoc_ufunc(
    uniq2pixarea,
    """\
Determine the area of a HEALPix NESTED index.

Parameters
----------
uniq : `numpy.ndarray`
    NUNIQ pixel index

Returns
-------
area : `numpy.ndarray`
    The pixel's area in steradians

""",
)


add_newdoc_ufunc(
    uniq2nest,
    """\
Convert a pixel index from NUNIQ to NESTED ordering.

Parameters
----------
uniq : `numpy.ndarray`
    NUNIQ pixel index

Returns
-------
order : `numpy.ndarray`
    HEALPix resolution order (logarithm base 2 of `nside`)
ipix : `numpy.ndarray`
    NESTED pixel index

""",
)


def rasterize(moc_data, order=None):
    """Convert a multi-order HEALPix dataset to fixed-order NESTED ordering.

    Parameters
    ----------
    moc_data : `numpy.ndarray`
        A multi-order HEALPix dataset stored as a Numpy record array whose
        first column is called UNIQ and contains the NUNIQ pixel index. Every
        point on the unit sphere must be contained in exactly one pixel in the
        dataset.
    order : int, optional
        The desired output resolution order, or :obj:`None` for the maximum
        resolution present in the dataset.

    Returns
    -------
    nested_data : `numpy.ndarray`
        A fixed-order, NESTED-ordering HEALPix dataset with all of the columns
        that were in moc_data, with the exception of the UNIQ column.

    """
    if np.ndim(moc_data) != 1:
        raise ValueError("expected 1D structured array or Astropy table")
    elif order is None or order < 0:
        order = -1
    else:
        orig_order, orig_nest = uniq2nest(moc_data["UNIQ"])
        to_downsample = order < orig_order
        if np.any(to_downsample):
            to_keep = table.Table(moc_data[~to_downsample], copy=False)
            orig_order = orig_order[to_downsample]
            orig_nest = orig_nest[to_downsample]
            to_downsample = table.Table(moc_data[to_downsample], copy=False)

            ratio = 1 << (2 * np.int64(orig_order - order))
            weights = 1.0 / ratio
            for colname, column in to_downsample.columns.items():
                if colname != "UNIQ":
                    column *= weights
            to_downsample["UNIQ"] = nest2uniq(np.int8(order), orig_nest // ratio)
            to_downsample = to_downsample.group_by("UNIQ").groups.aggregate(np.sum)

            moc_data = table.vstack((to_keep, to_downsample))

    # Ensure that moc_data has appropriate padding for each of its columns to
    # be properly aligned in order to avoid undefined behavior.
    moc_data = repack_fields(np.asarray(moc_data), align=True)

    return _rasterize(moc_data, order=order)


def bayestar_adaptive_grid(probdensity_func, *args, top_nside=16, rounds=8, **kwargs):
    """Create a sky map by evaluating a function on an adaptive grid.

    Perform the BAYESTAR adaptive mesh refinement scheme as described in
    Section VI of Singer & Price 2016, PRD, 93, 024013
    :doi:`10.1103/PhysRevD.93.024013`. This computes the sky map
    using a provided analytic function and refines the grid, dividing the
    highest 25% into subpixels and then recalculating their values. The extra
    given args and kwargs will be passed to the given probdensity function.

    Parameters
    ----------
    probdensity_func : callable
        Probability density function. The first argument consists of
        column-stacked array of right ascension and declination in radians.
        The return value must be a 1D array of the probability density in
        inverse steradians with the same length as the argument.
    top_nside : int
        HEALPix NSIDE resolution of initial evaluation of the sky map
    rounds : int
        Number of refinement rounds, including the initial sky map evaluation

    Returns
    -------
    skymap : astropy.table.Table
        An astropy Table with UNIQ and PROBDENSITY columns, representing
        a multi-ordered sky map
    """

    def func(nside, ipix):
        ra, dec = ah.healpix_to_lonlat(ipix, nside, order="nested")
        probdensity = probdensity_func(
            np.column_stack((ra.rad, dec.rad)), *args, **kwargs
        )
        prob = probdensity / np.square(nside)
        return probdensity, prob

    end = ah.nside_to_npix(top_nside)
    nrefine = end // 4
    begin = end - nrefine

    # Allocate full-sized output arrays
    length_per_round = 3 * nrefine
    length = end + length_per_round * rounds
    probdensity = np.empty(length)
    prob = np.empty(length)
    nside = np.empty(length, dtype=np.intp)
    ipix = np.empty(length, dtype=np.intp)

    with tqdm(total=rounds + 1) as progress:
        # Evaluate at top resolution
        nside[:end] = new_nside = top_nside
        ipix[:end] = new_ipix = np.arange(end)
        probdensity[:end], prob[:end] = func(new_nside, new_ipix)
        progress.update()

        # Perform adaptive refinement rounds
        for _ in range(rounds):
            i = prob[:end].argpartition(begin - 1)
            for array in nside, ipix, probdensity, prob:
                array[:end] = array[i]
            new_nside = np.tile(nside[begin:end] * 2, 4)
            new_ipix = (ipix[begin:end] * 4 + np.arange(4)[:, np.newaxis]).ravel()
            new_probdensity, new_prob = func(new_nside, new_ipix)
            end += length_per_round
            nside[begin:end] = new_nside
            ipix[begin:end] = new_ipix
            probdensity[begin:end] = new_probdensity
            prob[begin:end] = new_prob
            begin += length_per_round
            progress.update()

    # Make sure that sky map is normalized (it should be already)
    probdensity /= np.sum(probdensity * ah.nside_to_pixel_area(nside).to_value(u.sr))

    # Convert from NESTED to UNIQ pixel indices
    order = np.log2(nside).astype(int)
    uniq = nest2uniq(order.astype(np.int8), ipix)

    # Done!
    return table.Table([uniq, probdensity], names=["UNIQ", "PROBDENSITY"], copy=False)


del add_newdoc_ufunc
