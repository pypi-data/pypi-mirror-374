# This program is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

__author__ = "Deborah Paradis"
__copyright__ = "Copyright 2025, The CADE/IRAP Project"
__credits__ = ["Deborah Paradis", "Jean-Michel Glorian"]
__license__ = "GPL v3"
__version__ = "1.3"
__maintainer__ = "Deborah Paradis"
__email__ = "cade at irap.omp.eu"
__status__ = "beta"

import math
import time

import astropy.coordinates
import astropy_healpix
import healpy as hp
import matplotlib.pyplot as plt
import numpy
import reproject
import scipy.sparse as sp
from astropy import units as u
from astropy.coordinates import SkyCoord, Longitude, Latitude
from astropy.io import fits
from astropy.wcs import WCS
from cdshealpix import elliptical_cone_search, polygon_search
from drizzlib.fitsfuncdrizzlib import read_map, _get_hdu
from drizzlib.healpix2wcs import healpix2wcs
from numpy import ndarray
from regions import CircleSkyRegion, PixCoord, EllipseSkyRegion, RectangleSkyRegion, \
    CircleAnnulusSkyRegion, EllipseAnnulusSkyRegion, SkyRegion

from enum import Enum
from functools import reduce
from reproject import reproject_exact

ST_EXTRACTION_BCKGD_FITS = 'map_st_extraction_bckgd.fits'
MAP_ST_EXTRACTION_FITS = 'map_st_extraction.fits'


class ImageFormat(int, Enum):
    HEALPIX = 1
    WCS = 2


class Ordering(int, Enum):
    NESTED = 1
    RING = 2


class Method(int, Enum):
    MEAN = 1
    SUM = 2
    MEDIAN = 3


class ShapeRegion(int, Enum):
    POINT = 1  # defined by coord1 and coord2 only
    CIRCLE = 2  # defined by the radius in vals_to_define_region = []
    ELLIPSE = 3  # defined by the width, height, angle = < Quantity 0. deg > in vals_to_define_region = []
    RECTANGLE = 4  # defined by the width, height, angle=<Quantity 0. deg> in vals_to_define_region=[]
    # in the case of WCS files defined by the width, height, in degrees in the case of Healpix files.
    # With Healpix files it is recommended to give coordinates in Galactic frame.
    # Not sure it works correctly with other frames.
    CIRCLE_ANNULUS = 5  # defined by the inner_radius and the outer_radius in vals_to_define_bckgd = []
    ELLISPE_ANNULUS = 6  # defined by the inner_width, outer_width, inner_height,
    # outer_height and the angle = < Quantity 0. deg > in vals_to_define_bckgd = []'
    PERCENTILE = 7  # available only with WCS files (or when using at least one WCS fits file),
    # defined by percentile_bckgd=[]


class Mask():
    def __init__(self, min: float | None = None, max: float | None = None,
                 image_file: str | None = None, image_file_format: ImageFormat | None = None):
        self.min: float | None = min
        self.max: float | None = max
        self.image_file: str = image_file
        self.image_file_format: ImageFormat = image_file_format


class Region:
    def __init__(self, mask: Mask | None, shape: ShapeRegion, param: list[float], coord: list[float | None],
                 coordsys: str = 'galactic', method: Method = Method.MEAN):
        self.mask: Mask = mask
        self.shape: ShapeRegion = shape
        self.coord: list[float] = coord if coord[0] is not None and coord[1] is not None else [0.0, 0.0]
        self.coordsys: str = coordsys  # see astropy
        self.param: list[float] = param if param else []  # depend on the type of region
        self.method: Method = method

    def have_mask(self):
        return self.mask is not None

    def have_full_mask(self):
        return self.mask is not None and self.shape is None

    def have_specific_mask(self):
        return self.mask is not None and self.shape is not None

    def have_wcs_mask(self):
        return self.mask is not None and self.mask.image_file_format == ImageFormat.WCS


class MapInput:
    def __init__(self, map_file: str, nside: int, ordering: Ordering,
                 hdu: int, files_format: ImageFormat, wav: float, blank_value: int = -32768) -> None:
        self.map_file: str = map_file
        self.nside: int = nside
        self.ordering: Ordering = ordering
        self.hdu: int = hdu
        self.files_format: ImageFormat = files_format
        self.wav: float = wav
        self.blank_value: int = blank_value


def filtered_pix(data, indices, indptr, shape_map, mask):
    # Filtrer les données et les indices
    filtered_data = data[mask]
    filtered_indices = indices[mask]

    # Recalculer les pointeurs de lignes pour la nouvelle matrice éparse
    new_indptr = numpy.zeros_like(indptr)

    # Parcourir chaque ligne pour ajuster les pointeurs
    current_index = 0
    for row in range(len(indptr) - 1):
        start = indptr[row]
        end = indptr[row + 1]

        # Comptage des éléments qui satisfont la condition
        count = numpy.sum(mask[start:end])

        # Ajustement du pointeur pour la nouvelle ligne
        new_indptr[row + 1] = new_indptr[row] + count

        # Création de la nouvelle matrice CSR avec les valeurs filtrées
    pix_out = sp.csr_matrix((filtered_data, filtered_indices, new_indptr), shape=shape_map)
    return pix_out


def sed_extract(maps_input: dict, region_input: dict, rm_bckgd_input: dict | None = None, hdr_ref: str | None = None,
                plot: bool = False, save: bool = True, output_path: str = '.'):
    """
    Extract a SED from Healpix, WCS or mixture of Healpix and WCS files, in a specific region of the sky,
    with the exact same pixels in all files.
    If all files are in the Healpix format, mixing Allsky and Partial Healpix, use the 'mask' keyword if possible
    (with the file having the less observed pixels) in order to restrict the area to find the common pixels and
    to significantly reduce time computing.

    @param maps_input: dict with entries
        'maps' :[File1, File2, ..],
        'nside_input' : int, Required if using Healpix files
        'ordering' :  can be Ordering.NESTED or Ordering.RING
        'hdu' : int, The id of the Header Data Unit to read in the header of the template WCS FITS file.
            Defaults to 0.
        'wav' : list of float represent the wavelength of the maps
            Same length of the list of maps
        'files_format' : list of ImageFormat represent the format of the image
            Each element can be ImageFormat.HEALPIX or ImageFormat.WCS
            Same length of the list of maps

        'blank_value' : int, The BLANK value to use if it is not specified in the HEALPix header.Defaults to -32768.

    @param region_input: dict with entries
        'coord1': float
            First central coordinates of the region to extract the SED
        'coord2': float
            Second central coordinates of the region to extract the SED
        'coordsys': str
            Coordinate System. Accepted 'icrs', 'fk5', 'fk4', 'galactic',...
        'region' :  str
            Type of region you want to extract the SED. Accepted :
                'point': defined by coord1 and coord2 only
                'circle': defined by the radius in vals_to_define_region=[]
                'ellipse': defined by the width, height, angle=<Quantity 0. deg> in vals_to_define_region=[]
                'rectangle': defined by the width, height, angle=<Quantity 0. deg> in vals_to_define_region=[]
                            in the case of WCS files
                            defined by the width, height, in degrees in the case of Healpix files.
                            With Healpix files it is recommended to give coordinates in Galactic frame.
                            Not sure it works correctly with other frames.
                'mask': defined by the min and/or max value(s) with mask_min and mask_max
                        of the referenced image file_for_mask=''
                'circle-mask' or 'mask-circle': combination of the circle and mask values to define the region
                'ellipse-mask' or 'mask-ellipse': combination of the ellipse and mask values to define the region
                'rectangle-mask' or 'mask-rectangle': combination of the rectangle and mask values to define the region
        'vals_to_define_region' :  list of float
            Values to define the region. See the description of the 'region' entries.
            You don't need this parameter when using 'mask' as 'region'.
        'method' : Method
            Method to compute the SED. Accepted: Method.MEAN, Method.SUM, Method.MEDIAN
        'file_for_mask' :  str optional
            The path of the file used as a mask to extract the SED. Can be a WCS or Healpix image,
            or an image generated by the user (for instance values of 0 and 1).
            The mask can be used to extract the SED with flux limits (if a real image).
            If the user wants to extract the SED with coord1/coord2 limits,
            the mask could be values at 0 outside the coord1/coord2 limits and values at 1 inside, for instance.
        'file_format_for_mask' : ImageFormat optional
            ImageFormat.HEALPIX or ImageFormat.WCS, to characterize the type of the file mask ImageFormat.HEALPIX,
        'mask_min' : float  optional.
            Minimal value of the mask.
            Default None (the mask will be applied and the undefined values will be removed from the selected region)
        'mask_max' : float  optional.
            Maximal value of the mask.
            Default None (the mask will be applied and the undefined values will be removed from the selected region)

    @param rm_bckgd_input: dict with entries optional
        'method_bckgd': str
            Method to compute the Background. Accepted: Method.MEDIAN, Method.SUM or Method.MEAN
        'coord1_bckgd': float
            First central coordinate of the region to compute the background
        'coord2_bckgd': float
            Second central coordinate of the region to compute the background
        'rm_bckgd':  str
            Define the type of region you want to subtract a background. Accepted:
                'circle', 'ellipse', 'rectangle'
                'circle_annulus': defined by the inner_radius and the outer_radius in vals_to_define_bckgd=[]
                'ellipse_annulus": defined by the inner_width, outer_width, inner_height, outer_height
                                   and the angle=<Quantity 0. deg> in vals_to_define_bckgd entries =[]
                'mask': defined by the min and/or max value(s) with mask_min_bckgd and mask_max_bckgd
                        of the referenced image file_for_mask_bckgd=''
                'circle-mask' or 'mask-circle': combination of the circle and mask values
                                                to define the background region
                'ellipse-mask' or 'mask-ellipse': combination of the ellipse and mask values
                                                  to define the background region
                'rectangle-mask' or 'mask-rectangle': combination of the rectangle and mask values
                                                      to define the background region
                'circle_annulus-mask' or 'mask-circle_annulus': combination of the circle_annulus and mask values
                                                                to define the background region
                'ellipse_annulus-mask' or 'mask-ellipse_annulus': combination of the ellipse_annulus and mask values
                                                                to define the background region
                'percentile': available only with WCS files (or when using at least one WCS fits file),
                              defined by percentile_bckgd=[]
        'vals_to_define_bckgd': list of float
            Values to define the background region. See the description of the 'rm_bckgd' keyword.
            You don't need this parameter when using 'mask' or 'percentile' as 'rm_bckgd'.
        'mask_min_bckgd': float, optional
            Minimal value of the mask background.
        'mask_max_bckgd': float, optional
            Maximal value of the mask background.
        'percentile_bckgd': float
            Value between 0 and 100 required if rm_bckgd='percentile'
        'file_for_mask_bckgd': str, optional
            The path of the file used as a mask to compute the background, if rm_bckgd includes 'mask' and this worth
            None or is undefined, region mask we'll be used instead
         'file_format_for_mask': ImageFormat.HEALPIX, optional
    @param hdr_ref: str, optional
        The path to the file used as header of reference.
        All files (if not all Healpix files) will be reprojected on this header.
    @param plot: bool
        Set to True to plot the image and pixels used for the extraction.
        Default is False
    @param save: bool
        Set to True to save the SED
        Defualt is True
    @param output_path: str
        path of the output values
    """

    maps_list: list[MapInput] = []
    for i, map_file in enumerate(maps_input['maps']):
        map_input = MapInput(map_file=map_file, nside=maps_input['nside_input'],
                             ordering=maps_input['ordering'], hdu=maps_input['hdu'],
                             files_format=maps_input['files_format'][i], wav=maps_input['wav'][i],
                             blank_value=maps_input['blank_value'])
        maps_list.append(map_input)

    shape: ShapeRegion | None = None
    mask: Mask | None = None
    region = region_input['region']
    if 'mask' in region:
        mask = Mask(min=region_input.get('mask_min'), max=region_input.get('mask_max'),
                    image_file=region_input['file_for_mask'],
                    image_file_format=region_input['file_format_for_mask'])
        region = region.replace('mask', '').replace('-', '')

    if region == 'point':
        shape = ShapeRegion.POINT
    elif region == 'circle':
        shape = ShapeRegion.CIRCLE
    elif region == 'ellipse':
        shape = ShapeRegion.ELLIPSE
    elif region == 'rectangle':
        shape = ShapeRegion.RECTANGLE

    the_region = Region(mask=mask, shape=shape, coord=[region_input.get('coord1'), region_input.get('coord2')],
                        coordsys=region_input['coordsys'], param=region_input.get('vals_to_define_region'),
                        method=region_input['method'])

    shape_bckgd: ShapeRegion | None = None
    mask_bckgd: Mask | None = None
    rm_bckgd = rm_bckgd_input['rm_bckgd'] if rm_bckgd_input is not None else None

    full_mask_backg: bool = rm_bckgd == 'mask'
    if rm_bckgd is not None and 'mask' in rm_bckgd:
        mask_bckgd = Mask(min=rm_bckgd_input.get('mask_min_bckgd'), max=rm_bckgd_input.get('mask_max_bckgd'),
                          image_file=rm_bckgd_input.get('file_for_mask_bckgd'),
                          image_file_format=rm_bckgd_input.get('file_format_for_mask'))
        rm_bckgd = rm_bckgd.replace('mask', '').replace('-', '')

    the_rm_bckgd: Region | None = None

    if rm_bckgd is not None:
        if rm_bckgd != '' or full_mask_backg:
            vals_to_define_bckgd: list[float] | None = None
            if not full_mask_backg:
                vals_to_define_bckgd = rm_bckgd_input.get('vals_to_define_bckgd')
                if rm_bckgd == 'circle':
                    shape_bckgd = ShapeRegion.CIRCLE
                elif rm_bckgd == 'ellipse':
                    shape_bckgd = ShapeRegion.ELLIPSE
                elif rm_bckgd == 'rectangle':
                    shape_bckgd = ShapeRegion.RECTANGLE
                elif rm_bckgd == 'circle_annulus':
                    shape_bckgd = ShapeRegion.CIRCLE_ANNULUS
                elif rm_bckgd == 'ellipse_annulus':
                    shape_bckgd = ShapeRegion.ELLISPE_ANNULUS
                elif rm_bckgd == 'percentile':
                    shape_bckgd = ShapeRegion.PERCENTILE
                    vals_to_define_bckgd = [rm_bckgd_input['percentile_bckgd']]

            the_rm_bckgd = Region(mask=mask_bckgd,
                                  shape=shape_bckgd,
                                  coord=[rm_bckgd_input.get('coord1_bckgd'), rm_bckgd_input.get('coord2_bckgd')],
                                  coordsys=region_input['coordsys'],
                                  param=vals_to_define_bckgd,
                                  method=rm_bckgd_input['method_bckgd'])

    return sed_extract2(maps_list, hdr_ref, the_region,
                        the_rm_bckgd, plot=plot, save_sed=save,
                        save_sed_output_path=output_path + 'save_sed',
                        save_image_output_path=output_path + 'save_image',
                        save_plotsed_output_path=output_path + 'save_plotsed')


def check_parameters(maps_input: list[MapInput], region: Region, background_region: Region):
    res: bool = True
    nside: int | None = None
    for i in range(len(maps_input)):
        map_input: MapInput = maps_input[i]
        if map_input.files_format == ImageFormat.HEALPIX:
            if nside is None:
                nside = map_input.nside
            elif map_input.nside != nside:
                res = False
    return res


def sed_extract2(maps_input: list[MapInput],
                 hdr_ref: str = None,  # only if one wcs
                 region: Region | None = None,
                 rm_bckgd: Region | None = None,
                 plot=False,
                 save_sed=False,
                 save_sed_output_path='save_sed',
                 save_image_output_path="",
                 save_plotsed_output_path=""):
    param_checked: bool = check_parameters(maps_input, region, rm_bckgd)

    if not param_checked:
        raise ValueError(
            'You have different nside for healpix maps input'
        )

    if region.have_mask() and region.mask.min is not None and region.mask.min == 0:
        region.mask.min = 1e-8

    if rm_bckgd is not None and rm_bckgd.have_mask() and rm_bckgd.mask.min is not None and rm_bckgd.mask.min == 0:
        rm_bckgd.mask.min = 1e-8

    blank_value: float = maps_input[0].blank_value  # -32768
    nestt: bool = maps_input[0].ordering == Ordering.NESTED
    nside_input: int = maps_input[0].nside

    bckgd_val_ind = None
    res_list = None
    res_list_bckgd = None
    sed_val_ind = None

    sed_val = []
    rms_val = []
    bckgd_val = []
    valid_pix = []
    map_st = dict()
    bckgd_st = dict()
    index = []
    index2 = []
    index2_bckgd = []
    index_bckgd = []

    sky: SkyCoord = astropy.coordinates.SkyCoord(region.coord[0], region.coord[1], unit=u.degree, frame=region.coordsys)
    if rm_bckgd is not None:
        sky_bckgd = astropy.coordinates.SkyCoord(
            rm_bckgd.coord[0], rm_bckgd.coord[1], unit=u.degree, frame=rm_bckgd.coordsys)

    maps_healp: list[str] = []
    maps_wcs: list[str] = []
    wav: list[float] = []
    for i in range(len(maps_input)):
        map_input: MapInput = maps_input[i]
        if map_input.files_format == ImageFormat.HEALPIX:
            maps_healp.append(map_input.map_file)
        else:  # 'WCS'
            maps_wcs.append(map_input.map_file)
        wav.append(map_input.wav)

    have_wcs: bool = len(maps_wcs) > 0

    if have_wcs or (region.have_mask() and region.mask.image_file_format == ImageFormat.WCS):
        wcs_header_ref = fits.getheader(hdr_ref)
        wcs_data = fits.getdata(hdr_ref)

        x_dim_ref = int(wcs_header_ref['NAXIS1'])
        y_dim_ref = int(wcs_header_ref['NAXIS2'])

        wcs_ref = WCS(header=hdr_ref, naxis=2)

        if region.have_mask():
            nside, obj, wcs_data = compte_wcs_data(hdr_ref, nestt, region, wcs_header_ref)
        if rm_bckgd is not None:
            if rm_bckgd.have_mask():
                if rm_bckgd.mask.image_file is None or rm_bckgd.mask.image_file == region.mask.image_file:
                    wcs_data_bckgd = wcs_data
                else:
                    nside, obj, wcs_data_bckgd = compte_wcs_data(hdr_ref, nestt, rm_bckgd, wcs_header_ref)

        if region.have_full_mask():
            res = filter_wcs_data(region.mask.max, region.mask.min, wcs_data, x_dim_ref, y_dim_ref)
        if rm_bckgd is not None and rm_bckgd.have_full_mask():
            res_bckgd = filter_wcs_data(rm_bckgd.mask.max, rm_bckgd.mask.min, wcs_data_bckgd, x_dim_ref, y_dim_ref)

        region_pix = extract_region_pix(region, sky, wcs_ref)

        if not region.have_mask() and region.shape != ShapeRegion.POINT:
            res = ([(i, j) for i in range(y_dim_ref) for j in range(x_dim_ref) if PixCoord(j, i) in region_pix])
        elif region.have_specific_mask():
            res = filter_wcs_data_region(region.mask.max, region.mask.min, wcs_data, x_dim_ref, y_dim_ref, region_pix)
            print(res)

        reg_pix_bckgd = []
        if rm_bckgd is not None and not rm_bckgd.have_full_mask() and rm_bckgd.shape != ShapeRegion.PERCENTILE:
            if rm_bckgd.shape == ShapeRegion.CIRCLE:
                reg_bckgd = CircleSkyRegion(sky_bckgd, rm_bckgd.param[0] * u.degree)
            elif rm_bckgd.shape == ShapeRegion.ELLIPSE:
                reg_bckgd = EllipseSkyRegion(sky_bckgd, rm_bckgd.param[0] * u.degree,
                                             rm_bckgd.param[1] * u.degree,
                                             rm_bckgd.param[2] * u.degree)
            elif rm_bckgd.shape == ShapeRegion.RECTANGLE:
                reg_bckgd = RectangleSkyRegion(sky_bckgd, rm_bckgd.param[0] * u.degree,
                                               rm_bckgd.param[1] * u.degree,
                                               rm_bckgd.param[2] * u.degree)
            elif rm_bckgd.shape == ShapeRegion.CIRCLE_ANNULUS:
                reg_bckgd = CircleAnnulusSkyRegion(sky_bckgd, inner_radius=rm_bckgd.param[0] * u.degree,
                                                   outer_radius=rm_bckgd.param[1] * u.deg)
            elif rm_bckgd.shape == ShapeRegion.ELLISPE_ANNULUS:
                reg_bckgd = EllipseAnnulusSkyRegion(sky_bckgd, rm_bckgd.param[0] * u.degree,
                                                    rm_bckgd.param[1] * u.degree,
                                                    rm_bckgd.param[2] * u.degree,
                                                    rm_bckgd.param[3] * u.degree,
                                                    rm_bckgd.param[4] * u.degree)

            reg_pix_bckgd = reg_bckgd.to_pixel(wcs_ref)

            if rm_bckgd is not None:
                if not rm_bckgd.have_mask() and rm_bckgd.shape != ShapeRegion.PERCENTILE:
                    res_bckgd = ([(i, j) for i in range(y_dim_ref) for j in range(x_dim_ref) if
                                  PixCoord(j, i) in reg_pix_bckgd])
                else:
                    res_bckgd = filter_wcs_data_region(rm_bckgd.mask.max, rm_bckgd.mask.min, wcs_data, x_dim_ref,
                                                       y_dim_ref, reg_pix_bckgd)
                    print(res_bckgd)

        if plot:
            fig, ax = plt.subplots()
            plt.subplot(projection=wcs_ref)
            test_plot = wcs_data

            if region.shape != ShapeRegion.POINT:
                for jj in range(numpy.size(res, 0)):
                    test_plot[res[jj]] = -200
                plt.imshow(test_plot, vmin=-10., vmax=60, origin='lower', cmap='jet')
                plt.colorbar()
            else:  # region == 'point':
                plt.imshow(wcs_data, vmin=0., vmax=100, origin='lower', cmap='jet')
                plt.colorbar()
            ax.imshow(wcs_data)
            plt.grid(color='white', ls='solid')
            plt.xlabel('Ra')
            plt.ylabel('Dec')
            if not region.have_full_mask() and region.shape is not None and region.shape != ShapeRegion.POINT:
                region_pix.plot(color='red', lw=2.0)
            if rm_bckgd is not None and rm_bckgd.shape != ShapeRegion.PERCENTILE:
                for tt in range(len(res_bckgd)):
                    test_plot[res_bckgd[tt]] = -200
                if reg_pix_bckgd != []:
                    reg_pix_bckgd.plot(color='green', lw=1.0)
                plt.imshow(test_plot, vmin=-10, vmax=60, origin='lower', cmap='jet')
                # plt.colorbar()
            path_image = save_image_output_path
            plt.savefig(path_image)
            plt.close()
        for gg in range(len(maps_input)):
            bckgd = []
            ind_res_bckgd = []
            current_map_file = maps_input[gg].map_file
            if maps_input[gg].files_format == ImageFormat.WCS:
                wcs_header = fits.getheader(current_map_file)
                wcs_data = fits.getdata(current_map_file)

                if len(numpy.shape(wcs_data)) == 3:
                    wcs_data = wcs_data[0]
                    nans = numpy.array(numpy.isnan(wcs_data)).tolist()
                    count_nans = nans[0].count(True)
                    if count_nans != 0:
                        wcs_data = numpy.nan_to_num(wcs_data, nan=-32768)
                if wcs_header[gg] != wcs_header_ref:
                    wcs_data, footprint = reproject_exact((wcs_data, wcs_header), wcs_header_ref)  # ,
                    nans = numpy.array(numpy.isnan(wcs_data)).tolist()
                    count_nans = nans[0].count(True)
                    if count_nans != 0:
                        wcs_data = numpy.nan_to_num(wcs_data, nan=-32768)
            else:  # 'Healpix':
                im, header = read_map((current_map_file), field=0, dtype=numpy.float64, nest=nestt,
                                      partial=False,
                                      hdu=1, h=True,
                                      verbose=True, memmap=False, offset=0)
                im = 0.
                fits_hdu = _get_hdu(current_map_file, hdu=1, memmap=None)

                nside = fits_hdu.header.get('NSIDE')
                obj = fits_hdu.header.get('OBJECT', 'UNDEF')
                if nside >= 8192:
                    print('The extraction from Healpix to WCS might take some time, especially '
                          'if the Healpix is partial ... Please be patient!')
                healpix2wcs(current_map_file, field=1, header=hdr_ref, header_hdu=0,
                            output=MAP_ST_EXTRACTION_FITS, crpix=None,
                            cdelt=None,
                            pixel_size=None, crval=None, ctype=None, image_size=None, equinox=None, is_sigma=False,
                            ignore_blank=True, blank_value=-32768, clobber=True, col_ids=None)
                wcs_data = fits.getdata(MAP_ST_EXTRACTION_FITS)
                nans = numpy.array(numpy.isnan(wcs_data)).tolist()
                count_nans = nans[0].count(True)
                if count_nans != 0:
                    wcs_data = numpy.nan_to_num(wcs_data, nan=-32768)
            mm = []
            ind_res = []
            if region.shape != ShapeRegion.POINT:
                for m in range(len(res)):
                    if wcs_data[res[m]] != blank_value:
                        ind_res += [res[m]]
                        mm += [wcs_data[res[m]]]
                if ind_res == []:
                    raise RuntimeError('No pixels in your region ... please change your preferences')
                map_st[current_map_file] = (mm, ind_res)

            else:  # region == 'point':
                inddd = (numpy.around(SkyCoord.to_pixel(sky, wcs_ref))).tolist()
                map_st[current_map_file] = (
                    wcs_data[(int(inddd[1]), int(inddd[0]))], [(int(inddd[1]), int(inddd[0]))])

            if rm_bckgd is not None:
                if rm_bckgd.shape != ShapeRegion.PERCENTILE:
                    mm_bckgd = []

                    for m in range(len(res_bckgd)):
                        if wcs_data[res_bckgd[m]] != blank_value and wcs_data[res_bckgd[m]] != numpy.nan:
                            ind_res_bckgd += [res_bckgd[m]]
                            mm_bckgd += [wcs_data[res_bckgd[m]]]
                    bckgd_st[current_map_file] = (mm_bckgd, ind_res_bckgd)
                    if ind_res_bckgd == []:
                        raise RuntimeError('No pixels in your  background region ... please change your preferences')

                if rm_bckgd.shape == ShapeRegion.PERCENTILE:
                    aa = numpy.where(wcs_data > -1000)
                    numpy.ravel_multi_index(aa, wcs_data.shape)
                    data_ordered = numpy.sort(wcs_data[aa], axis=None)
                    perc = rm_bckgd.param[0] / 100. * numpy.size(aa[0])
                    res_bckgd = ([(i, j) for i in range(y_dim_ref) for j in range(x_dim_ref) if
                                  wcs_data[i, j] <= data_ordered[round(perc)]])

                    for m in range(numpy.size(res_bckgd, 0)):
                        if wcs_data[res_bckgd[m]] != numpy.nan and wcs_data[res_bckgd[m]] != blank_value:
                            ind_res_bckgd += [res_bckgd[m]]
                            bckgd += [wcs_data[res_bckgd[m]]]

                    bckgd_st[current_map_file] = (bckgd, ind_res_bckgd)
                    if ind_res_bckgd == []:
                        raise RuntimeError(
                            'No pixels in your  background region ... please change your preferences')

        if region.shape is not None and region.shape == ShapeRegion.POINT:
            for k in range(len(maps_input)):
                image = map_st[maps_input[k].map_file][0]
                sed = image
                print(sed)
                sed_val += [sed]
                print(sed_val)
        else:  # region != 'point':
            for kk in range(len(maps_input)):
                index += map_st[maps_input[kk].map_file][1]
                if rm_bckgd is not None:
                    index_bckgd += bckgd_st[maps_input[kk].map_file][1]
            new_pix_unique = numpy.unique(index, axis=0).tolist()
            ind_uniq: list = []
            ind_uniq_old: list = []
            if rm_bckgd is not None:
                new_pix_unique_bckgd = numpy.unique(index_bckgd, axis=0).tolist()

            ind_uniq_bckgd: list = []
            index_list: list = numpy.array(index).tolist()
            for jj in range(len(new_pix_unique)):
                n = new_pix_unique[jj]
                count = index_list.count(n)
                if count == len(maps_input):
                    ind_uniq_old += [index_list.index(n)]
                    ind_uniq += [n]

            if rm_bckgd is not None:
                for tt in range(len(new_pix_unique_bckgd)):
                    index_list_bckgd: list = numpy.array(index_bckgd).tolist()
                    n_bckgd = new_pix_unique_bckgd[tt]
                    count_bckgd = index_list_bckgd.count(n_bckgd)
                    if count_bckgd == len(maps_input):
                        # ind_uniq_bckgd += [index_list_bckgd.index(n_bckgd)]
                        ind_uniq_bckgd += [n_bckgd]

            for l in range(len(maps_input)):
                image = [map_st[maps_input[l].map_file][0]]
                index_good = [map_st[maps_input[l].map_file][1]]
                index_goodd = numpy.array(index_good[0])
                ind_uniqq = numpy.array(ind_uniq)
                # index_good=numpy.array(index_good[0])
                # if (numpy.max(ind_uniq) < numpy.size(image[0])):
                # res_list = [(image[0])[i] for i in ind_uniq]
                # testt = numpy.isin(index_good,ind_uniq)
                aa = (index_goodd[:, None] == ind_uniqq).all(2).any(1)
                rr = numpy.where(aa)
                res_list = [(image[0])[i] for i in list(rr[0])]
                # else:
                #    res_list=image[0]
                # for mm in range(len(ind_uniq)):
                #    res_list += [(image[0])[ind_uniq[mm]]]
                if rm_bckgd is not None:
                    bckgd = [bckgd_st[maps_input[l].map_file][0]]
                    index_good_bckgd = [bckgd_st[maps_input[l].map_file][1]]
                    index_goodd_bckgd = numpy.array(index_good_bckgd[0])
                    ind_uniqq_bckgd = numpy.array(ind_uniq_bckgd)
                    aa_bckgd = (index_goodd_bckgd[:, None] == ind_uniqq_bckgd).all(2).any(1)
                    rr_bckgd = numpy.where(aa_bckgd)
                    res_list_bckgd = [(bckgd[0])[ii] for ii in list(rr_bckgd[0])]
                    # res_list_bckgd = [(bckgd[0])[ii] for ii in ind_uniq_bckgd]
                    if res_list_bckgd == []:
                        raise RuntimeError('No pixel in your background region, please choose another region or '
                                           'do not use any background')
                    if rm_bckgd.shape == ShapeRegion.PERCENTILE:
                        new_data_ordered = numpy.sort(res_list_bckgd)
                        new_bckgd = numpy.max(new_data_ordered)

                if region.method == Method.MEAN:
                    sed = numpy.mean(res_list, axis=0)
                elif region.method == Method.MEDIAN:
                    sed = numpy.median(res_list, axis=0)
                elif region.method == Method.SUM:
                    sed = numpy.sum(res_list, axis=0)

                if rm_bckgd is not None:
                    rms = numpy.std(res_list_bckgd, axis=0)
                    if rm_bckgd.shape != ShapeRegion.PERCENTILE:
                        if rm_bckgd.method == Method.MEAN:
                            backgd = numpy.mean(res_list_bckgd, axis=0)
                        elif rm_bckgd.method == Method.MEDIAN:
                            backgd = numpy.median(res_list_bckgd, axis=0)
                        elif rm_bckgd.method == Method.SUM:
                            backgd = numpy.sum(res_list_bckgd, axis=0)

                    else:  # 'percentile':
                        backgd = new_bckgd

                    sed = sed - backgd

                    rms_val += [rms]
                    bckgd_val += [backgd]

                sed_val += [sed]

        sky = 0.
        sky_bckgd = 0.

    if not have_wcs and (not region.have_mask() or region.mask.image_file_format != ImageFormat.WCS):
        ipix: ndarray
        healp = astropy_healpix.HEALPix(nside=nside_input, order='nested')
        ind = healp.lonlat_to_healpix([sky.galactic.l] * u.deg, [sky.galactic.b] * u.deg)
        vecc2 = hp.pix2vec(nside_input, ind, nest=nestt)
        if rm_bckgd is not None:
            ind_bckgd = healp.lonlat_to_healpix([sky_bckgd.galactic.l] * u.deg, [sky_bckgd.galactic.b] * u.deg)
            vecc2_bckgd = hp.pix2vec(nside_input, ind_bckgd, nest=nestt)

        depth_value = int(math.log2(nside_input))

        if region.have_mask() and region.mask.image_file_format == ImageFormat.HEALPIX:
            im, h = read_map(region.mask.image_file, field=0, dtype=numpy.float64, nest=nestt, partial=False,
                             hdu=1, h=True, verbose=True, memmap=False, offset=0)
            fits_hdu = _get_hdu(region.mask.image_file, hdu=1, memmap=None)
            im = numpy.nan_to_num(im, nan=-32768)
            obj = [fits_hdu.header.get('OBJECT', 'UNDEF')]
            if obj == 'FULLSKY':
                if region.mask.min is None and region.mask.max is None:
                    ipix = (numpy.where((im != -32768)))[0]
                elif region.mask.min is not None and region.mask.max is None:
                    ipix = (numpy.where((im >= region.mask.min) & (im != -32768)))[0]
                elif region.mask.max is not None and region.mask.min is None:
                    ipix = (numpy.where((im <= region.mask.max) & (im != -32768)))[0]
                elif region.mask.max is not None and region.mask.min is not None:
                    ipix = (numpy.where((im <= region.mask.max) & (im >= region.mask.min) & (im != -32768)))[0]
            else:
                if region.mask.min is None and region.mask.max is None:
                    pix = (im.data != 0.) & (im.data != -32768)
                    pix_out = filtered_pix(im.data, im.indices, im.indptr, im.shape, pix)
                    ipix = (sp.find(pix_out))[1]
                elif region.mask.min is not None and region.mask.max is None:
                    pix = im >= region.mask.min
                    ipix = (sp.find(pix))[1]
                elif region.mask.max is not None and region.mask.min is None:
                    pix = (im.data <= region.mask.max) & (im.data != 0.) & (im.data != -32768)
                    pix_out = filtered_pix(im.data, im.indices, im.indptr, im.shape, pix)
                    ipix = (sp.find(pix_out))[1]
                elif region.mask.max is not None and region.mask.min is not None:
                    pix = (im.data <= region.mask.max) & (im.data >= region.mask.min) & (im.data != 0.)
                    pix_out = filtered_pix(im.data, im.indices, im.indptr, im.shape, pix)
                    ipix = (sp.find(pix_out))[1]
            if region.have_specific_mask():
                ipix_combined_mask = ipix  # [0]

        if region.shape == ShapeRegion.POINT:
            ipix = ind[0]
        elif region.shape == ShapeRegion.CIRCLE:
            ipix = hp.query_disc(nside=nside_input, vec=vecc2, radius=numpy.radians(region.param[0]),
                                 nest=nestt,
                                 inclusive=False)
            print(ipix)
        elif region.shape == ShapeRegion.ELLIPSE:
            a = astropy.coordinates.Angle(region.param[0], unit="deg")
            b = astropy.coordinates.Angle(region.param[1], unit="deg")
            pa = astropy.coordinates.Angle(region.param[2], unit="deg")

            ipix, depth, fully_covered = elliptical_cone_search(sky.galactic.l, sky.galactic.b, a, b, pa,
                                                                depth=depth_value, flat=True)
        elif region.shape == ShapeRegion.RECTANGLE:
            print(region.coordsys)
            if region.coordsys != 'galactic' and region.coordsys != 'Galactic':
                print('<°)))))< <°)))))< <°)))))< <°)))))< <°)))))< <°)))))<')
                print('The rectangular region will be performed in the Galactic frame.')
                print('<°)))))< <°)))))< <°)))))< <°)))))< <°)))))< <°)))))<')
                time.sleep(5)
            long = Longitude([sky.galactic.l + Longitude(region.param[0] / 2., u.deg),
                              sky.galactic.l - Longitude(region.param[0] / 2., u.deg),
                              sky.galactic.l - Longitude(region.param[0] / 2., u.deg),
                              sky.galactic.l + Longitude(region.param[0] / 2., u.deg)], u.deg,
                             wrap_angle=180 * u.deg)
            lati = Latitude([sky.galactic.b + Longitude(region.param[1] / 2., u.deg),
                             sky.galactic.b + Longitude(region.param[1] / 2., u.deg),
                             sky.galactic.b - Longitude(region.param[1] / 2., u.deg),
                             sky.galactic.b - Longitude(region.param[1] / 2., u.deg)], u.deg)

            if (region.coord[0] + region.param[0] / 2. - (region.coord[0] - region.param[0] / 2.)) >= 180.:
                if region.param[0] == 360. or region.param[0] == 360:
                    region.param[0] = 359.99999999

                long1 = Longitude([sky.galactic.l + Longitude(region.param[0] / 2., u.deg), 0., 0.,
                                   sky.galactic.l + Longitude(region.param[0] / 2., u.deg)], u.deg,
                                  wrap_angle=180 * u.deg)
                long2 = Longitude([0., sky.galactic.l - Longitude(region.param[0] / 2., u.deg),
                                   sky.galactic.l - Longitude(region.param[0] / 2., u.deg), 0.], u.deg,
                                  wrap_angle=180 * u.deg)

                ipix1, depth1, fully_covered1 = polygon_search(long1, lati, depth=depth_value, flat=True)
                ipix2, depth2, fully_covered2 = polygon_search(long2, lati, depth=depth_value, flat=True)
                ipix = numpy.concatenate([ipix1, ipix2])
                print(ipix)
            else:
                ipix, depth, fully_covered = polygon_search(long, lati, depth=depth_value, flat=True)

        if region.have_specific_mask():
            ipix_mask = numpy.asarray(list(set(ipix_combined_mask) & set(ipix)))
            ipix = ipix_mask

        if rm_bckgd is not None and rm_bckgd.have_mask() and (
                rm_bckgd.mask.image_file_format == ImageFormat.HEALPIX or (
                rm_bckgd.mask.image_file_format is None and region.mask.image_file_format == ImageFormat.HEALPIX)):
            if region.have_mask() and \
                    (rm_bckgd.mask.image_file is None or rm_bckgd.mask.image_file == region.mask.image_file):
                im_bckgd = im
            else:
                im_bckgd, h = read_map(rm_bckgd.mask.image_file, field=0, dtype=numpy.float64, nest=nestt,
                                       partial=False,
                                       hdu=1,
                                       h=True,
                                       verbose=True, memmap=False, offset=0)
                fits_hdu = _get_hdu(rm_bckgd.mask.image_file, hdu=1, memmap=None)
                nside = fits_hdu.header.get('NSIDE')
                if nside != nside_input:
                    raise RuntimeError('Wrong NSIDE ... Please check NSIDE = \'\' and NSIDE in your files ...')
                    # sys.exit()
                im_bckgd = numpy.nan_to_num(im_bckgd, nan=-32768)
                obj = fits_hdu.header.get('OBJECT', 'UNDEF')

            if obj == 'FULLSKY':
                if rm_bckgd.mask.min is None and rm_bckgd.mask.max is None:
                    ipix_bckgd = (numpy.where((im_bckgd != -32768)))[0]
                elif rm_bckgd.mask.min is not None and rm_bckgd.mask.max is None:
                    ipix_bckgd = (numpy.where((im_bckgd >= rm_bckgd.mask.min) & (im_bckgd != -32768)))[0]
                    # ipix = numpy.where((im >= region.mask.min) & (im != -32768)[0])
                elif rm_bckgd.mask.max is not None and rm_bckgd.mask.min is None:
                    ipix_bckgd = (numpy.where((im_bckgd <= rm_bckgd.mask.max) & (im_bckgd != -32768)))[0]
                elif rm_bckgd.mask.max is not None and rm_bckgd.mask.min is not None:
                    ipix_bckgd = (numpy.where(
                        (im_bckgd <= rm_bckgd.mask.max) & (im_bckgd >= rm_bckgd.mask.min) & (im_bckgd != -32768)))[0]
            else:
                if rm_bckgd.mask.min is None and rm_bckgd.mask.max is None:
                    pix_bckgd = (im_bckgd.data != -32768) & (im_bckgd.data != 0)
                    pix_bckgd_out = filtered_pix(im_bckgd.data, im_bckgd.indices, im_bckgd.indptr, im_bckgd.shape,
                                                 pix_bckgd)
                    ipix_bckgd = (sp.find(pix_bckgd_out))[1]
                elif rm_bckgd.mask.min is not None and rm_bckgd.mask.max is None:
                    pix_bckgd = (im_bckgd.data >= rm_bckgd.mask.min) & (im_bckgd.data != 0)
                    pix_bckgd_out = filtered_pix(im_bckgd.data, im_bckgd.indices, im_bckgd.indptr, im_bckgd.shape,
                                                 pix_bckgd)
                    ipix_bckgd = (sp.find(pix_bckgd_out))[1]
                elif rm_bckgd.mask.max is not None and rm_bckgd.mask.min is None:
                    pix_bckgd = (im_bckgd.data <= rm_bckgd.mask.max) & (im_bckgd.data != 0) & (im_bckgd.data != -32768)
                    pix_bckgd_out = filtered_pix(im_bckgd.data, im_bckgd.indices, im_bckgd.indptr, im_bckgd.shape,
                                                 pix_bckgd)
                    ipix_bckgd = (sp.find(pix_bckgd_out))[1]
                elif rm_bckgd.mask.max is not None and rm_bckgd.mask.min is not None:
                    pix_bckgd = (im_bckgd.data <= rm_bckgd.mask.max) & (im_bckgd.data >= rm_bckgd.mask.min) & (
                            im_bckgd.data != 0.)
                    pix_bckgd_out = filtered_pix(im_bckgd.data, im_bckgd.indices, im_bckgd.indptr, im_bckgd.shape,
                                                 pix_bckgd)
                    ipix_bckgd = (sp.find(pix_bckgd_out))[1]

            if rm_bckgd.shape is not None:
                ipix_combined_mask_bckgd = ipix_bckgd  # [0]
        obj = []

        if rm_bckgd is not None:
            if rm_bckgd.shape == ShapeRegion.CIRCLE:
                ipix_bckgd = hp.query_disc(nside=nside_input,
                                           vec=vecc2_bckgd,
                                           radius=numpy.radians(rm_bckgd.param[0]),
                                           nest=nestt,
                                           inclusive=False)
            elif rm_bckgd.shape == ShapeRegion.ELLIPSE:
                # if method != 'sum':
                a = astropy.coordinates.Angle(rm_bckgd.param[0], unit="deg")
                b = astropy.coordinates.Angle(rm_bckgd.param[1], unit="deg")
                pa = astropy.coordinates.Angle(rm_bckgd.param[2], unit="deg")

                ipix_bckgd, depth, fully_covered = elliptical_cone_search(sky_bckgd.galactic.l, sky_bckgd.galactic.b,
                                                                          a, b, pa, depth=depth_value, flat=True)
            elif rm_bckgd.shape == ShapeRegion.RECTANGLE:
                long = Longitude([sky_bckgd.galactic.l + Longitude(rm_bckgd.param[0] / 2., u.deg),
                                  sky_bckgd.galactic.l - Longitude(rm_bckgd.param[0] / 2., u.deg),
                                  sky_bckgd.galactic.l - Longitude(rm_bckgd.param[0] / 2., u.deg),
                                  sky_bckgd.galactic.l + Longitude(rm_bckgd.param[0] / 2., u.deg)], u.deg,
                                 wrap_angle=180 * u.deg)
                lati = Latitude([sky_bckgd.galactic.b + Longitude(rm_bckgd.param[1] / 2., u.deg),
                                 sky_bckgd.galactic.b + Longitude(rm_bckgd.param[1] / 2., u.deg),
                                 sky_bckgd.galactic.b - Longitude(rm_bckgd.param[1] / 2., u.deg),
                                 sky_bckgd.galactic.b - Longitude(rm_bckgd.param[1] / 2., u.deg)], u.deg)

                if (rm_bckgd.coord[0] + rm_bckgd.param[0] / 2. - (
                        rm_bckgd.coord[0] - rm_bckgd.param[0] / 2.)) >= 180.:
                    if rm_bckgd.param[0] == 360. or rm_bckgd.param[0] == 360:
                        rm_bckgd.param[0] = 359.99999999

                    long1 = Longitude([sky_bckgd.galactic.l + Longitude(rm_bckgd.param[0] / 2., u.deg), 0., 0.,
                                       sky_bckgd.galactic.l + Longitude(rm_bckgd.param[0] / 2., u.deg)], u.deg,
                                      wrap_angle=180 * u.deg)
                    long2 = Longitude([0., sky_bckgd.galactic.l - Longitude(rm_bckgd.param[0] / 2., u.deg),
                                       sky_bckgd.galactic.l - Longitude(rm_bckgd.param[0] / 2., u.deg), 0.],
                                      u.deg,
                                      wrap_angle=180 * u.deg)

                    ipix1_bckgd, depth1, fully_covered1 = polygon_search(long1, lati, depth=depth_value, flat=True)
                    ipix2_bckgd, depth2, fully_covered2 = polygon_search(long2, lati, depth=depth_value, flat=True)
                    ipix_bckgd = numpy.concatenate([ipix1_bckgd, ipix2_bckgd])
                    print(ipix_bckgd)
                else:
                    ipix_bckgd, depth, fully_covered = polygon_search(long, lati, depth=depth_value, flat=True)

            elif rm_bckgd.shape == ShapeRegion.CIRCLE_ANNULUS:
                i_disc = hp.query_disc(nside=nside_input, vec=vecc2_bckgd,
                                       radius=numpy.radians(rm_bckgd.param[0]), nest=nestt,
                                       inclusive=False)
                o_disc = hp.query_disc(nside=nside_input, vec=vecc2_bckgd,
                                       radius=numpy.radians(rm_bckgd.param[1]), nest=nestt,
                                       inclusive=False)  # grabs all the indices within the o_rad input
                ipix_bckgd = numpy.setxor1d(i_disc, o_disc)

            elif rm_bckgd.shape == ShapeRegion.ELLISPE_ANNULUS:
                a_i = astropy.coordinates.Angle(rm_bckgd.param[0], unit="deg")
                a_o = astropy.coordinates.Angle(rm_bckgd.param[1], unit="deg")
                b_i = astropy.coordinates.Angle(rm_bckgd.param[2], unit="deg")
                b_o = astropy.coordinates.Angle(rm_bckgd.param[3], unit="deg")
                pa = astropy.coordinates.Angle(rm_bckgd.param[4], unit="deg")

                ipix_i, depth, fully_covered = elliptical_cone_search(sky_bckgd.galactic.l, sky_bckgd.galactic.b,
                                                                      a_i, b_i, pa, depth=depth_value, flat=True)
                ipix_o, depth, fully_covered = elliptical_cone_search(sky_bckgd.galactic.l, sky_bckgd.galactic.b,
                                                                      a_o, b_o, pa, depth=depth_value, flat=True)
                ipix_bckgd = numpy.setxor1d(ipix_i, ipix_o)

                print(ipix_bckgd)

            if rm_bckgd.have_specific_mask():
                ipix_mask_bckgd = numpy.asarray(list(set(ipix_combined_mask_bckgd) & set(ipix_bckgd)))
                ipix_bckgd = ipix_mask_bckgd

        for i in range(len(maps_healp)):
            bckgd = []
            im, h = read_map(maps_healp[i], field=0, dtype=numpy.float64, nest=nestt, partial=False, hdu=1,
                             h=True,
                             verbose=True, memmap=False, offset=0)
            fits_hdu = _get_hdu(maps_healp[i], hdu=1, memmap=None)
            nside = fits_hdu.header.get('NSIDE')
            if nside != nside_input:
                raise RuntimeError('Wrong NSIDE ... Please check NSIDE = \'\' and Nside in your files ...')
            im = numpy.nan_to_num(im, nan=-32768)
            obj += [fits_hdu.header.get('OBJECT', 'UNDEF')]
            if obj[i] == 'UNDEF':
                print('Missing OBJECT keyword in the header of the file, assuming FULLSKY')
                obj[i] = 'FULLSKY'

            if region.shape != ShapeRegion.POINT and not region.have_full_mask() and region.shape is not None:
                if obj[i] == 'PARTIAL':
                    iiipix = (sp.find(im[0, ipix] != blank_value))[1]
                else:
                    iiipix = (sp.find(im[ipix] != blank_value))[1]

                if iiipix != []:
                    iipix = ipix[iiipix]
                else:
                    iipix = ipix
                iiipix = 0
                print(iipix)
            if region.shape == ShapeRegion.POINT or region.have_full_mask():
                new_ipix = ipix
                print(ipix)
            else:
                new_ipix = iipix

            vvalid_pix = [new_ipix]

            if obj[i] == 'PARTIAL' and region.shape != ShapeRegion.POINT:
                test = numpy.isin(vvalid_pix[0], im.indices)
                rr = numpy.where(test)

                valid_pix = [(vvalid_pix[0])[rr[0]]]
            else:
                valid_pix = vvalid_pix

            if rm_bckgd is not None and region.shape != ShapeRegion.POINT:
                if obj[i] == 'PARTIAL':
                    pixx1 = im[0, ipix_bckgd] != blank_value
                    pixx2 = im[0, ipix_bckgd] != numpy.nan
                    ipixx1 = (sp.find(pixx1))[1]
                    ipixx2 = (sp.find(pixx2))[1]
                    iiipix_bckgd = numpy.asarray(list(set(ipixx1) & set(ipixx2)))

                else:
                    iiipix_bckgd = numpy.where((im[ipix_bckgd] != blank_value) & (im[ipix_bckgd] != numpy.nan))

                iipix_bckgd = ipix_bckgd[iiipix_bckgd]
                print(iipix_bckgd)

                new_ipix_bckgd = iipix_bckgd
                vvalid_pix_bckgd = [new_ipix_bckgd]

                if obj[i] == 'PARTIAL':
                    test = numpy.isin(vvalid_pix_bckgd[0], im.indices)
                    rr = numpy.where(test)

                    valid_pix_bckgd = [(vvalid_pix_bckgd[0])[rr]]
                else:
                    valid_pix_bckgd = vvalid_pix_bckgd

            if obj[i] == 'PARTIAL':
                map_st[maps_healp[i]] = (im[0, valid_pix[0]], valid_pix, vvalid_pix)
            else:
                map_st[maps_healp[i]] = (im[valid_pix], valid_pix, vvalid_pix)
            if rm_bckgd is not None and region.shape != ShapeRegion.POINT:
                if obj[i] == 'PARTIAL':
                    bckgd_st[maps_healp[i]] = (im[0, valid_pix_bckgd[0]], valid_pix_bckgd, vvalid_pix_bckgd)
                else:
                    bckgd_st[maps_healp[i]] = (im[valid_pix_bckgd], valid_pix_bckgd, vvalid_pix_bckgd)
            im = 0

        if region.shape == ShapeRegion.POINT:
            for k in range(len(maps_healp)):
                image = map_st[maps_healp[k]][0]
                sed = image
                sed_val += [sed]
            path_image = ''
        else:  # region != 'point':
            for k in range(len(maps_healp)):
                index += map_st[maps_healp[k]][1]
                index2 += map_st[maps_healp[k]][2]
                if rm_bckgd is not None:
                    index_bckgd += bckgd_st[maps_healp[k]][1]
                    index2_bckgd += bckgd_st[maps_healp[k]][2]

            intersection = find_intersection(index)
            valid_pix = numpy.asarray(intersection)
            if rm_bckgd is not None:
                intersection_bckgd = find_intersection(index_bckgd)
                valid_pix_bckgd = intersection_bckgd

            conc_index = numpy.concatenate(index)
            new_pix_unique = numpy.unique(conc_index)

            if rm_bckgd is not None:
                new_pix_unique_bckgd = numpy.unique(numpy.concatenate(index_bckgd))

            # for j in range(int(numpy.size(new_pix_unique))):
            #    ind_uniq = numpy.where(index == new_pix_unique[j])
            #    if numpy.size(ind_uniq) == len(maps_healp):
            #        valid_pix += [ind_uniq]

            # if rm_bckgd is not None:
            #    for j in range(int(numpy.size(new_pix_unique_bckgd))):
            #        ind_uniq_bckgd = numpy.where(index_bckgd == new_pix_unique_bckgd[j])
            #        if numpy.size(ind_uniq_bckgd) == len(maps_healp):
            #            valid_pix_bckgd += ind_uniq_bckgd

            for l in range(len(maps_healp)):
                image = ((map_st[maps_healp[l]])[0])[0]
                sed_val_ind = numpy.isin(new_pix_unique, valid_pix)
                ee_new = numpy.where(sed_val_ind == False)
                if ee_new != [] and obj[l] == 'PARTIAL':
                    new_test = numpy.isin(index2[l], valid_pix)
                    sed_val_ind = numpy.isin((index2[l])[numpy.where(new_test)], valid_pix)
                    new_im = image[0, sed_val_ind]

                if rm_bckgd is not None:
                    bckgd = ((bckgd_st[maps_healp[l]])[0])[0]
                    bckgd_val_ind = numpy.isin(new_pix_unique_bckgd, valid_pix_bckgd)
                    ee_new_bckgd = numpy.where(bckgd_val_ind == False)
                    if ee_new_bckgd != [] and obj[l] == 'PARTIAL':
                        new_test_bckgd = numpy.isin(index2_bckgd[l], valid_pix_bckgd)
                        bckgd_val_ind = numpy.isin((index2_bckgd[l])[numpy.where(new_test_bckgd)],
                                                   valid_pix_bckgd)
                        new_bckgd = bckgd[0, bckgd_val_ind]

                if plot and l == 0 and nside < 8192:
                    # hp.mollview(im, nest=True)
                    map_val = numpy.zeros(hp.nside2npix(nside))
                    map_val[valid_pix] = 1
                    if rm_bckgd is not None and numpy.size(valid_pix_bckgd) != 0:
                        map_val[valid_pix_bckgd] = 2
                    hp.mollview(map_val, nest=True)
                    hp.graticule()
                    # seems that hp uses matplotlib to create figures, so we can call matplotlib to save the figure
                    path_image = save_image_output_path
                    plt.savefig(path_image)
                    plt.close()

                val = None
                if obj[l] == 'PARTIAL':
                    val = new_im.data
                else:  # obj[k] == 'FULLSKY'
                    val = image[sed_val_ind]
                sed = None
                if region.method == Method.MEAN:
                    sed = numpy.mean(val)
                elif region.method == Method.MEDIAN:
                    sed = numpy.median(val)
                elif region.method == Method.SUM:
                    sed = numpy.sum(val)

                if rm_bckgd is not None:
                    val = None
                    rms = None
                    if obj[l] == 'PARTIAL':
                        val = new_bckgd.data
                        rms = numpy.std(new_bckgd.data)
                    else:  # obj[k] == 'FULLSKY'
                        val = bckgd[bckgd_val_ind]
                        rms = numpy.std(bckgd[bckgd_val_ind])

                    if rm_bckgd.method == Method.MEAN:
                        backgd = numpy.mean(val)
                    elif rm_bckgd.method == Method.MEDIAN:
                        backgd = numpy.median(val)
                    elif rm_bckgd.method == Method.SUM:
                        backgd = numpy.sum(val)

                    sed = sed - backgd
                    rms_val += [rms]
                    bckgd_val += [backgd]

                sed_val += [sed]

    if plot:
        plot_res(bckgd_val, bckgd_val_ind, have_wcs, region.mask, res_list, res_list_bckgd, rm_bckgd,
                 rms_val, sed_val, sed_val_ind, wav)

        path_sed = save_plotsed_output_path
        plt.savefig(path_sed)
        plt.close()

    if save_sed:
        path_sed_result = save_res(save_sed_output_path, bckgd_val, rm_bckgd, rms_val, sed_val, wav)

    print('GOODBYE !!! And please, do not forget to acknowledge the CADE service in your publications :)')

    return path_image, path_sed, path_sed_result


def compte_wcs_data(hdr_ref, nestt, region, wcs_header_ref):
    wcs_data = None
    nside = None
    obj = None

    if region.mask.image_file_format == ImageFormat.WCS:
        wcs_header = fits.getheader(region.mask.image_file)
        wcs_data = fits.getdata(region.mask.image_file)
        if wcs_header != wcs_header_ref:
            wcs_data, footprint = reproject.reproject_exact((wcs_data, wcs_header), wcs_header_ref)
    else:  # region.mask.image_file_format == ImageFormat.HEALPIX:
        im, header = read_map(region.mask.image_file, field=0, dtype=numpy.float64, nest=nestt, partial=False,
                              hdu=1, h=True, verbose=True, memmap=False, offset=0)
        im = 0.  # TODO why ?
        fits_hdu = _get_hdu(region.mask.image_file, hdu=1, memmap=None)

        nside = fits_hdu.header.get('NSIDE')
        obj = fits_hdu.header.get('OBJECT', 'UNDEF')

        healpix2wcs(region.mask.image_file, field=1, header=hdr_ref, header_hdu=0,
                    output=MAP_ST_EXTRACTION_FITS, crpix=None,
                    cdelt=None,
                    pixel_size=None, crval=None, ctype=None, image_size=None, equinox=None, is_sigma=False,
                    ignore_blank=True, blank_value=-32768, clobber=True, col_ids=None)
        wcs_data = fits.getdata(MAP_ST_EXTRACTION_FITS)
    nans = numpy.array(numpy.isnan(wcs_data)).tolist()
    count_nans = nans[0].count(True)
    if count_nans != 0:
        wcs_data = numpy.nan_to_num(wcs_data, nan=-32768)
    return nside, obj, wcs_data


def filter_wcs_data_region(mask_max, mask_min, wcs_data, x_dim_ref, y_dim_ref, region_pix):
    res = None
    if mask_max is None and mask_min is None:
        res = ([(i, j) for i in range(y_dim_ref) for j in range(x_dim_ref) if
                (wcs_data[i, j] != numpy.nan and wcs_data[i, j] != -32768 and PixCoord(j, i) in region_pix)])
    elif mask_max is not None and mask_min is None:
        res = ([(i, j) for i in range(y_dim_ref) for j in range(x_dim_ref) if (
                wcs_data[i, j] <= mask_max and wcs_data[i, j] != numpy.nan and wcs_data[i, j] != -32768
                and PixCoord(j, i) in region_pix)])
    elif mask_min is not None and mask_max is None:
        res = ([(i, j) for i in range(y_dim_ref) for j in range(x_dim_ref) if (
                wcs_data[i, j] >= mask_min and wcs_data[i, j] != numpy.nan and wcs_data[i, j] != -32768
                and PixCoord(j, i) in region_pix)])
    elif mask_min is not None and mask_max is not None:
        res = ([(i, j) for i in range(y_dim_ref) for j in range(x_dim_ref) if (
                wcs_data[i, j] >= mask_min and wcs_data[i, j] <= mask_max and wcs_data[i, j] != numpy.nan
                and wcs_data[i, j] != -32768 and PixCoord(j, i) in region_pix)])
    return res


def filter_wcs_data(mask_max, mask_min, wcs_data, x_dim_ref, y_dim_ref):
    if mask_max is None and mask_min is None:
        res = ([(i, j) for i in range(y_dim_ref) for j in range(x_dim_ref) if
                (wcs_data[i, j] != numpy.nan and wcs_data[i, j] != -32768)])
    elif mask_max is not None and mask_min is None:
        res = ([(i, j) for i in range(y_dim_ref) for j in range(x_dim_ref) if
                (wcs_data[i, j] <= mask_max and wcs_data[i, j] != numpy.nan and wcs_data[i, j] != -32768)])
    elif mask_min is not None and mask_max is None:
        res = ([(i, j) for i in range(y_dim_ref) for j in range(x_dim_ref) if
                (wcs_data[i, j] >= mask_min and wcs_data[i, j] != numpy.nan and wcs_data[i, j] != -32768)])
    elif mask_min is not None and mask_max is not None:
        res = ([(i, j) for i in range(y_dim_ref) for j in range(x_dim_ref) if (
                mask_min <= wcs_data[i, j] <= mask_max
                and wcs_data[i, j] != numpy.nan and wcs_data[i, j] != -32768)])
        print(res)
    return res


def extract_region_pix(region: Region, sky, wcs_ref):
    '''

    '''
    region_pix: SkyRegion | None = None

    if region.shape is not None and region.shape != ShapeRegion.POINT:
        if region.shape == ShapeRegion.CIRCLE:
            reg = CircleSkyRegion(sky, region.param[0] * u.degree)

        elif region.shape == ShapeRegion.ELLIPSE:
            reg = EllipseSkyRegion(sky, region.param[0] * u.degree,
                                   region.param[1] * u.degree, region.param[2] * u.degree)
        elif region.shape == ShapeRegion.RECTANGLE:
            reg = RectangleSkyRegion(sky, region.param[0] * u.degree,
                                     region.param[1] * u.degree, region.param[2] * u.degree)
        region_pix = reg.to_pixel(wcs_ref)
    return region_pix


def save_res(sed_res_path, bckgd_val, rm_bckgd, rms_val, sed_val, wav):
    path_save_sed = sed_res_path
    with open(path_save_sed, 'w') as file:
        if rm_bckgd is None:
            file.write("Wavelengths SED")
            file.write("\n")
            file.write("\n")
            for index in range(len(wav)):
                file.write("%f %f \n" % (wav[index], sed_val[index]))
        else:
            file.write("Wavelengths  SED  Bckgd_values RMS_in_Bckgd ")
            file.write("\n")
            file.write("\n")
            for index in range(len(wav)):
                file.write("%f %f %f %f \n" % (wav[index], sed_val[index], bckgd_val[index], rms_val[index]))
    return path_save_sed


def plot_res(bckgd_val, bckgd_val_ind, have_wcs: bool, mask: Mask, res_list, res_list_bckgd, background_region,
             rms_val, sed_val, sed_val_ind, wav):
    wn = [x for x in range(14)]
    wnum = wn[0]
    plt.figure(wnum, figsize=(9, 6))
    man = plt.get_current_fig_manager()
    man.set_window_title(' SED ' + str(wnum))
    # man.canvas.set_window_title(' SED ' + str(wnum))
    xtit = r'Wavelength ($\mu$m)'
    plt.xscale('log')
    plt.xlabel(xtit)
    plt.yscale('log')
    if background_region is not None:
        print('SED Values after background subtraction : ', sed_val)
        print('Background Values : ', bckgd_val)
        print('RMS in Background : ', rms_val)
    else:
        print('SED values :', sed_val)

    print('Wavelengths :', wav)

    if have_wcs or (mask is not None and mask.image_file_format == ImageFormat.WCS):
        print('Nb of valid pixels in the region:', numpy.size(res_list))
        if background_region is not None:
            print('Nb of valid pixels in the background:', numpy.size(res_list_bckgd))
    if not have_wcs and (mask is not None and mask.image_file_format == ImageFormat.WCS):
        print('Nb of valid pixels in the region:', numpy.size(sed_val_ind))
        if background_region is not None:
            print('Nb of valid pixels in the background:', numpy.size(bckgd_val_ind))
    plt.plot(wav, sed_val, marker='o', color='red', label='')

    error = rms_val
    if not rms_val:
        error = []
        for zz in range(len(wav)):
            error += [numpy.sqrt((0.07 * sed_val[zz]) ** 2)]  # +(rms_val[zz])**2)]
    plt.errorbar(wav, sed_val, yerr=error)


def find_intersection(lists):
    """
    This function takes in a list of lists as input and returns their intersection as a numpy array
    """
    # Use reduce() to find the intersection of all the lists
    intersection = reduce(lambda x, y: set(x) & set(y), lists)
    # Convert the intersection to a numpy array
    intersection_array = numpy.array(list(intersection))
    return intersection_array
