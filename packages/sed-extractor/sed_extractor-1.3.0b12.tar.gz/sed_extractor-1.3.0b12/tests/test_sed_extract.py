import os
import unittest

import pandas as pd

from src.sed_extractor.sed_extract import Method, sed_extract, Ordering, ImageFormat

DATA_PATH = os.getenv('DATA_PATH', '/home/lbertin/sed-extractor-volumes/sed-extractor/')
OUTPUT_PATH = os.getenv('OUTPUT_PATH', '/home/lbertin/sed-extractor-volumes/OUT/')


class MyTestCase(unittest.TestCase):

    def test_sed_extract1(self):
        maps_input = {'maps': [
            ('%sIRIS_NOHOLES_1_2048.fits' % DATA_PATH),
            ('%sIRIS_NOHOLES_2_2048.fits' % DATA_PATH),
            ('%sIRIS_NOHOLES_3_2048.fits' % DATA_PATH),
            ('%sIRIS_NOHOLES_4_2048.fits' % DATA_PATH),
            ('%sCC_250_4arcm_1_2048_partial.fits' % DATA_PATH),
            ('%sCC_350_4arcm_1_2048_partial.fits' % DATA_PATH),
            ('%sHFI_SkyMap_857_2048_R3.01_full.fits' % DATA_PATH),
            ('%sCC_500_4arcm_1_2048_partial.fits' % DATA_PATH)],
            'nside_input': 2048,
            'ordering': Ordering.NESTED,
            'hdu': 0,
            'wav': [12., 25., 60., 100., 250., 350., 350., 500.],
            'files_format': [ImageFormat.HEALPIX, ImageFormat.HEALPIX, ImageFormat.HEALPIX, ImageFormat.HEALPIX,
                             ImageFormat.HEALPIX, ImageFormat.HEALPIX, ImageFormat.HEALPIX, ImageFormat.HEALPIX],
            'blank_value': -32768,
        }

        region_input = {
            'coord1': 0.,
            'coord2': -0,
            'coordsys': 'galactic',
            'region': 'rectangle-mask',
            'vals_to_define_region': [360., 180., 0],
            'method': Method.MEAN,
            'file_for_mask': ('%sCC_250_4arcm_1_2048_partial.fits' % DATA_PATH),
            'file_format_for_mask': ImageFormat.HEALPIX,
        }

        rm_bckgd_input = {
            'method_bckgd': Method.MEDIAN,
            'coord1_bckgd': 316.1,
            'coord2_bckgd': -21.5,
            'rm_bckgd': 'circle',
            'vals_to_define_bckgd': [1],
        }

        path_image, path_plot, res = sed_extract(
            maps_input, region_input, rm_bckgd_input,
            hdr_ref=('%sCADE_Higal_250_4arcm_0.0_0.0_70x50_0.0286_GAL_TAN_20220704_155908.fits' % DATA_PATH), plot=True,
            save=True, output_path=OUTPUT_PATH)

        with open(res, 'r') as file:
            file2_lines = file.readlines()
            self.assertEqual(['Wavelengths  SED  Bckgd_values RMS_in_Bckgd \n', '\n',
                              '12.000000 1.359608 0.937463 0.152433 \n',
                              '25.000000 1.490538 1.642537 0.070033 \n',
                              '60.000000 7.916607 2.137801 0.206881 \n',
                              '100.000000 28.120640 9.502067 1.923906 \n',
                              '250.000000 46.781139 13.545638 6.425067 \n',
                              '350.000000 27.685974 8.040612 3.711312 \n',
                              '350.000000 28.852501 7.845233 3.966218 \n',
                              '500.000000 12.056801 3.217683 1.628227 \n']
                             , file2_lines)  # add assertion here

    def test_sed_extract2(self):
        maps_input = {'maps': [  # ('%sIRIS_NOHOLES_4_2048.fits' % DATA_PATH),
            ('%sCADE_AKARI_WideS_0.0_0.0_50x50_0.0143_GAL_TAN_20230209_100829.fits' % DATA_PATH),
            ('%sCADE_AKARI_160_0.0_0.0_50x50_0.0143_GAL_TAN_20220421_140923.fits' % DATA_PATH),
            ('%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH),
            ('%sCADE_Higal_350_4arcm_0.0_0.0_50x70_0.0286_GAL_TAN_20230213_095440.fits' % DATA_PATH),
            ('%sCADE_Higal_500_4arcm_0.0_0.0_50x70_0.0286_GAL_TAN_20230213_095620.fits' % DATA_PATH)],
            'nside_input': 2048,
            'ordering': Ordering.NESTED,
            'hdu': 0,
            'wav': [90., 160., 250., 350., 500.],
            'files_format': [ImageFormat.WCS, ImageFormat.WCS, ImageFormat.WCS,
                             ImageFormat.WCS, ImageFormat.WCS],
            'blank_value': -32768,
        }

        region_input = {
            'coord1': 0.2,
            'coord2': -0,
            'coordsys': 'galactic',
            'region': 'circle',
            'vals_to_define_region': [0.2],
            'method': Method.MEDIAN,
        }

        rm_bckgd_input = {
            'method_bckgd': Method.MEDIAN,
            'coord1_bckgd': 359.6,
            'coord2_bckgd': 0.3,
            'rm_bckgd': 'circle',
            'vals_to_define_bckgd': [0.1],
        }

        path_image, path_plot, res = sed_extract(
            maps_input, region_input, rm_bckgd_input,
            hdr_ref=('%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH), plot=True,
            save=True, output_path=OUTPUT_PATH)

        values_expected = pd.DataFrame([[90.000000, 12079.289849, 1815.433827, 441.540313],
                                        [160.000000, 13275.842092, 3188.455539, 538.650532],
                                        [250.000000, 6429.974687, 1498.298768, 185.127955],
                                        [350.000000, 2530.076295, 633.711059, 67.207094],
                                        [500.000000, 843.620445, 216.468707, 20.287100]],
                                       columns=['Wavelengths', 'SED', 'Bckgd_values', 'RMS_in_Bckgd'])
        precision = 1e-4

        value_res = pd.read_csv(res, delim_whitespace=True, header=0, index_col=False, keep_default_na=False)
        value_res.dropna(how='all', inplace=True)

        pd.testing.assert_frame_equal(value_res, values_expected, atol=precision)

    def test_sed_extract3(self):
        maps_input = {'maps': [
            ('%sIRIS_NOHOLES_1_2048.fits' % DATA_PATH),
            ('%sIRIS_NOHOLES_2_2048.fits' % DATA_PATH),
            ('%sIRIS_NOHOLES_3_2048.fits' % DATA_PATH),
            ('%sHigal_70_HPDP_4arcm_1_2048_partial.fits' % DATA_PATH),
            ('%sIRIS_NOHOLES_4_2048.fits' % DATA_PATH),
            ('%sHigal_160_HPDP_4arcm_1_2048_partial.fits' % DATA_PATH),
            ('%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH),
            ('%sHigal_350_4arcm_1_2048_partial.fits' % DATA_PATH),
            ('%sHigal_500_4arcm_1_2048_partial.fits' % DATA_PATH)],
            'nside_input': 2048,
            'ordering': Ordering.NESTED,
            'hdu': 0,
            'wav': [12., 25., 60., 70., 100., 160., 250., 350., 500.],
            'files_format': [ImageFormat.HEALPIX, ImageFormat.HEALPIX, ImageFormat.HEALPIX, ImageFormat.HEALPIX,
                             ImageFormat.HEALPIX, ImageFormat.HEALPIX, ImageFormat.WCS, ImageFormat.HEALPIX,
                             ImageFormat.HEALPIX],
            'blank_value': -32768,
        }
        region_input = {
            'coord1': 0.2,
            'coord2': 0.2,
            'coordsys': 'galactic',
            'region': 'ellipse-mask',
            'vals_to_define_region': [0.5, 0.1, 10.],
            'method': Method.MEDIAN,
            'file_for_mask': ('%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH),
            'file_format_for_mask': ImageFormat.WCS,
            'mask_min': 2000,
        }

        rm_bckgd_input = {
            'method_bckgd': Method.MEAN,
            'coord1_bckgd': 359.6,
            'coord2_bckgd': 0.3,
            'rm_bckgd': 'circle',
            'vals_to_define_bckgd': [0.1],
        }

        path_image, path_plot, res = sed_extract(
            maps_input, region_input, rm_bckgd_input,
            hdr_ref=('%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH), plot=True,
            save=True, output_path=OUTPUT_PATH)

        values_expected = pd.DataFrame([
            [12.000000, 28.033831, 49.372322, 3.656554],
            [25.000000, 27.364024, 92.643569, 22.114225],
            [60.000000, 1054.323093, 960.267459, 197.700200],
            [70.000000, 1814.133842, 1765.708170, 311.509483],
            [100.000000, 2291.981773, 2106.622444, 360.521836],
            [160.000000, 3052.809409, 3694.789520, 463.277523],
            [250.000000, 1301.402212, 1650.178993, 184.291797],
            [350.000000, 522.930178, 692.859761, 69.554752],
            [500.000000, 163.801606, 235.507506, 21.956879]],
            columns=['Wavelengths', 'SED', 'Bckgd_values', 'RMS_in_Bckgd'])
        precision = 1e-4

        value_res = pd.read_csv(res, delim_whitespace=True, header=0, index_col=False, keep_default_na=False)
        value_res.dropna(how='all', inplace=True)

        pd.testing.assert_frame_equal(value_res, values_expected, atol=precision)

    def test_sed_extract4(self):
        maps_input = {'maps': [
            ('%sCADE_AKARI_WideS_0.0_0.0_50x50_0.0143_GAL_TAN_20230209_100829.fits' % DATA_PATH),
            ('%sCADE_AKARI_160_0.0_0.0_50x50_0.0143_GAL_TAN_20220421_140923.fits' % DATA_PATH),
            ('%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH),
            ('%sCADE_Higal_350_4arcm_0.0_0.0_50x70_0.0286_GAL_TAN_20230213_095440.fits' % DATA_PATH),
            ('%sHigal_500_4arcm_1_2048_partial.fits' % DATA_PATH)],
            'nside_input': 2048,
            'ordering': Ordering.NESTED,
            'hdu': 0,
            'wav': [90., 160., 250., 350., 500.],
            'blank_value': -32768,
            'files_format': [ImageFormat.WCS, ImageFormat.WCS, ImageFormat.WCS,
                             ImageFormat.WCS, ImageFormat.HEALPIX],
        }
        region_input = {
            'coord1': 0.2,
            'coord2': 0.1,
            'coordsys': 'galactic',
            'region': 'rectangle-mask',
            'vals_to_define_region': [0.3, 0.5, 0],
            'method': Method.SUM,
            'file_for_mask': ('%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH),
            'file_format_for_mask': ImageFormat.WCS,
            'mask_min': 10,
            'mask_max': 10000,
        }
        rm_bckgd_input = {
            'coord1_bckgd': 359.6,
            'coord2_bckgd': 0.3,
            'method_bckgd': Method.MEAN,
            'rm_bckgd': 'rectangle-mask',
            'vals_to_define_bckgd': [0.1, 0.1, 10],
            'mask_min_bckgd': 100,
            'mask_max_bckgd': 10000,
        }

        path_image, path_plot, res = sed_extract(
            maps_input, region_input, rm_bckgd_input,
            hdr_ref=('%sCADE_AKARI_160_0.0_0.0_50x50_0.0143_GAL_TAN_20220421_140923.fits' % DATA_PATH), plot=True,
            save=True, output_path=OUTPUT_PATH)

        values_expected = pd.DataFrame([[90.000000, 5020623.074525, 1873.397602, 251.440978],
                                        [160.000000, 6659654.473878, 2926.781130, 422.331063],
                                        [250.000000, 3024001.221952, 1534.626150, 108.340378],
                                        [350.000000, 1216875.058689, 645.855844, 39.691996],
                                        [500.000000, 402845.292053, 218.744689, 13.427533]],
                                       columns=['Wavelengths', 'SED', 'Bckgd_values', 'RMS_in_Bckgd'])
        precision = 1e-4

        value_res = pd.read_csv(res, delim_whitespace=True, header=0, index_col=False, keep_default_na=False)
        value_res.dropna(how='all', inplace=True)

        pd.testing.assert_frame_equal(value_res, values_expected, atol=precision)

    def test_sed_extract5(self):
        maps_input = {
            'maps': [
                ('%sIRIS_NOHOLES_1_2048.fits' % DATA_PATH),
                ('%sIRIS_NOHOLES_2_2048.fits' % DATA_PATH),
                ('%sIRIS_NOHOLES_3_2048.fits' % DATA_PATH),
                ('%sIRIS_NOHOLES_4_2048.fits' % DATA_PATH)],
            'nside_input': 2048,
            'ordering': Ordering.NESTED,
            'hdu': 0,
            'wav': [12., 25., 60., 100.],
            'blank_value': -32768,
            'files_format': [ImageFormat.HEALPIX, ImageFormat.HEALPIX, ImageFormat.HEALPIX, ImageFormat.HEALPIX],
        }
        region_input = {
            'coord1': 254.,
            'coord2': -30,
            'coordsys': 'fk5',
            'region': 'rectangle',
            'vals_to_define_region': [5., 2., 30],
            'method': Method.MEDIAN,
        }

        rm_bckgd_input = {
            'coord1_bckgd': -10,
            'coord2_bckgd': -10,
            'coordsys': 'fk5',
            'method_bckgd': Method.MEAN,
            'rm_bckgd': 'rectangle-mask',
            'vals_to_define_bckgd': [2, 3, 10],
            'mask_max_bckgd': 10.,
            'file_format_for_mask': ImageFormat.HEALPIX,
            'file_for_mask_bckgd': ('%sIRIS_NOHOLES_4_2048.fits' % DATA_PATH),
        }

        path_image, path_plot, res = sed_extract(maps_input=maps_input, region_input=region_input,
                                                 rm_bckgd_input=rm_bckgd_input, plot=True,
                                                 hdr_ref=(
                                                             '%sCADE_Higal_250_4arcm_0.0_0.0_70x50_0.0286_GAL_TAN_20220704_155908.fits' % DATA_PATH),
                                                 save=True, output_path=OUTPUT_PATH)

        values_expected = pd.DataFrame([[12.000000, 0.586788, 1.523684, 1.151836],
                                        [25.000000, 0.445383, 2.122681, 0.524009],
                                        [60.000000, 6.031580, 0.830664, 0.116876],
                                        [100.000000, 21.335019, 3.025914, 0.180005]],
                                       columns=['Wavelengths', 'SED', 'Bckgd_values', 'RMS_in_Bckgd'])
        precision = 1e-4

        value_res = pd.read_csv(res, delim_whitespace=True, header=0, index_col=False, keep_default_na=False)
        value_res.dropna(how='all', inplace=True)

        pd.testing.assert_frame_equal(value_res, values_expected, atol=precision)

    def test_sed_extract6(self):
        maps_input = {
            'maps': [
                ('%sCADE_AKARI_WideS_0.0_0.0_50x50_0.0143_GAL_TAN_20230209_100829.fits' % DATA_PATH),
                ('%sCADE_AKARI_160_0.0_0.0_50x50_0.0143_GAL_TAN_20220421_140923.fits' % DATA_PATH),
                ('%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH),
                ('%sCADE_Higal_350_4arcm_0.0_0.0_50x70_0.0286_GAL_TAN_20230213_095440.fits' % DATA_PATH),
                ('%sCADE_Higal_500_4arcm_0.0_0.0_50x70_0.0286_GAL_TAN_20230213_095620.fits' % DATA_PATH)],
            'nside_input': 2048,
            'ordering': Ordering.NESTED,
            'hdu': 0,
            'wav': [90., 160., 250., 350., 500.],
            'blank_value': -32768,
            'files_format': [ImageFormat.WCS, ImageFormat.WCS, ImageFormat.WCS, ImageFormat.WCS, ImageFormat.WCS],
        }

        region_input = {
            'coord1': 0.2,
            'coord2': -0,
            'coordsys': 'galactic',
            'region': 'circle',
            'vals_to_define_region': [0.2],
            'method': Method.MEDIAN,
        }

        rm_bckgd_input = {
            'method_bckgd': Method.MEDIAN,
            'rm_bckgd': 'percentile',
            'percentile_bckgd': 30,
        }

        path_image, path_plot, res = sed_extract(maps_input=maps_input, region_input=region_input,
                                                 rm_bckgd_input=rm_bckgd_input, plot=True,
                                                 hdr_ref=(
                                                             '%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH),
                                                 save=True, output_path=OUTPUT_PATH)

        values_expected = pd.DataFrame([[90.000000, 11512.857933, 2381.865743, 330.275894],
                                        [160.000000, 12110.182027, 4354.115604, 453.048817],
                                        [250.000000, 6536.971645, 1391.301809, 68.861390],
                                        [350.000000, 2567.482062, 596.305292, 29.439183],
                                        [500.000000, 854.690556, 205.398596, 10.585567]],
                                       columns=['Wavelengths', 'SED', 'Bckgd_values', 'RMS_in_Bckgd'])
        precision = 1e-4

        value_res = pd.read_csv(res, delim_whitespace=True, header=0, index_col=False, keep_default_na=False)
        value_res.dropna(how='all', inplace=True)

        pd.testing.assert_frame_equal(value_res, values_expected, atol=precision)

    def test_sed_extract7(self):
        maps_input = {
            'maps': [
                ('%sCADE_AKARI_WideS_0.0_0.0_50x50_0.0143_GAL_TAN_20230209_100829.fits' % DATA_PATH),
                ('%sCADE_AKARI_160_0.0_0.0_50x50_0.0143_GAL_TAN_20220421_140923.fits' % DATA_PATH),
                ('%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH),
                ('%sCADE_Higal_350_4arcm_0.0_0.0_50x70_0.0286_GAL_TAN_20230213_095440.fits' % DATA_PATH),
                ('%sCADE_Higal_500_4arcm_0.0_0.0_50x70_0.0286_GAL_TAN_20230213_095620.fits' % DATA_PATH)],
            'nside_input': 2048,
            'ordering': Ordering.NESTED,
            'hdu': 0,
            'wav': [90., 160., 250., 350., 500.],
            'blank_value': -32768,
            'files_format': [ImageFormat.WCS, ImageFormat.WCS, ImageFormat.WCS, ImageFormat.WCS, ImageFormat.WCS],
        }

        region_input = {
            'region': 'mask',
            'method': Method.MEDIAN,
            'coordsys': 'galactic',
            'file_for_mask': ('%sCADE_Higal_500_4arcm_0.0_0.0_50x70_0.0286_GAL_TAN_20230213_095620.fits' % DATA_PATH),
            'file_format_for_mask': ImageFormat.WCS,
        }

        rm_bckgd_input = {
            'rm_bckgd': 'mask',
            'method_bckgd': Method.MEDIAN,
            'mask_min_bckgd': 0,
            'mask_max_bckgd': 500,
        }

        path_image, path_plot, res = sed_extract(maps_input=maps_input, region_input=region_input,
                                                 rm_bckgd_input=rm_bckgd_input, plot=True,
                                                 hdr_ref=(
                                                             '%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH),
                                                 save=True, output_path=OUTPUT_PATH)

        values_expected = pd.DataFrame([[90.000000, 2245.989215, 3180.537247, 1831.582874],
                                        [160.000000, 2687.364980, 5146.961164, 1630.753201],
                                        [250.000000, 1326.670438, 2342.628346, 663.819376],
                                        [350.000000, 513.210570, 957.646308, 254.527259],
                                        [500.000000, 172.533064, 320.451361, 82.540190]],
                                       columns=['Wavelengths', 'SED', 'Bckgd_values', 'RMS_in_Bckgd'])
        precision = 1e-4

        value_res = pd.read_csv(res, delim_whitespace=True, header=0, index_col=False, keep_default_na=False)
        value_res.dropna(how='all', inplace=True)

        pd.testing.assert_frame_equal(value_res, values_expected, atol=precision)

    def test_sed_extract8(self):
        maps_input = {
            'maps': [
                ('%sIRIS_NOHOLES_1_2048.fits' % DATA_PATH),
                ('%sIRIS_NOHOLES_2_2048.fits' % DATA_PATH)],
            'nside_input': 2048,
            'ordering': Ordering.NESTED,
            'hdu': 0,
            'wav': [12., 25.],
            'blank_value': -32768,
            'files_format': [ImageFormat.HEALPIX, ImageFormat.HEALPIX],
        }

        region_input = {
            'coordsys': 'galactic',
            'region': 'mask',
            'method': Method.SUM,
            'file_for_mask': ('%sCC_250_4arcm_1_2048_partial.fits' % DATA_PATH),
            'file_format_for_mask': ImageFormat.HEALPIX,
            'mask_max': 100,
        }

        rm_bckgd_input = {
            'coord1_bckgd': 358.7,
            'coord2_bckgd': 37.2,
            'method_bckgd': Method.SUM,
            'rm_bckgd': 'ellipse-mask',
            'vals_to_define_bckgd': [5, 2, 10],
            'mask_max_bckgd': 25,
            'mask_min_bckgd': 0,
        }

        path_image, path_plot, res = sed_extract(maps_input=maps_input, region_input=region_input,
                                                 rm_bckgd_input=rm_bckgd_input, plot=True,
                                                 hdr_ref='',
                                                 save=True,
                                                 output_path=OUTPUT_PATH)

        values_expected = pd.DataFrame([[12.000000, 137072.267922, 468.028812, 0.242784],
                                        [25.000000, 186747.185682, 662.742724, 0.277642]],
                                       columns=['Wavelengths', 'SED', 'Bckgd_values', 'RMS_in_Bckgd'])
        precision = 1e-4

        value_res = pd.read_csv(res, delim_whitespace=True, header=0, index_col=False, keep_default_na=False)
        value_res.dropna(how='all', inplace=True)

        pd.testing.assert_frame_equal(value_res, values_expected, atol=precision)

    def test_sed_extract9(self):
        maps_input = {
            'maps': [
                ('%sCADE_AKARI_WideS_0.0_0.0_50x50_0.0143_GAL_TAN_20230209_100829.fits' % DATA_PATH),
                ('%sCADE_AKARI_160_0.0_0.0_50x50_0.0143_GAL_TAN_20220421_140923.fits' % DATA_PATH),
                ('%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH),
                ('%sCADE_Higal_350_4arcm_0.0_0.0_50x70_0.0286_GAL_TAN_20230213_095440.fits' % DATA_PATH),
                ('%sCADE_Higal_500_4arcm_0.0_0.0_50x70_0.0286_GAL_TAN_20230213_095620.fits' % DATA_PATH)],
            'nside_input': 2048,
            'ordering': Ordering.NESTED,
            'hdu': 0,
            'wav': [90., 160., 250., 350., 500.],
            'blank_value': -32768,
            'files_format': [ImageFormat.WCS, ImageFormat.WCS, ImageFormat.WCS, ImageFormat.WCS, ImageFormat.WCS],
        }

        region_input = {
            'coord1': 0.2,
            'coord2': -0,
            'coordsys': 'galactic',
            'region': 'point',
            'vals_to_define_region': [0.2],
            'method': Method.MEDIAN,
        }

        rm_bckgd_input = {
            'coord1_bckgd': 0,
            'coord2_bckgd': 0.1,
            'method_bckgd': Method.MEDIAN,
            'rm_bckgd': '',
            'vals_to_define_bckgd': [1, 1, 10],
            'percentile_bckgd': 30,
        }

        path_image, path_plot, res = sed_extract(maps_input=maps_input, region_input=region_input,
                                                 rm_bckgd_input=rm_bckgd_input,
                                                 hdr_ref=(
                                                             '%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH),
                                                 plot=True,
                                                 save=True, output_path=OUTPUT_PATH)

        values_expected = pd.DataFrame([[90.000000, 19033.144820],
                                        [160.000000, 26214.414789],
                                        [250.000000, 11190.810835],
                                        [350.000000, 4547.446130],
                                        [500.000000, 1516.385445]],
                                       columns=['Wavelengths', 'SED'])
        precision = 1e-4

        value_res = pd.read_csv(res, delim_whitespace=True, header=0, index_col=False, keep_default_na=False)
        value_res.dropna(how='all', inplace=True)

        pd.testing.assert_frame_equal(value_res, values_expected, atol=precision)

    def test_sed_extract10(self):
        maps_input = {
            'maps': [
                ('%sHigal_160_HPDP_4arcm_1_2048_partial.fits' % DATA_PATH),
                ('%sHigal_350_4arcm_1_2048_partial.fits' % DATA_PATH),
                ('%sHigal_500_4arcm_1_2048_partial.fits' % DATA_PATH)],
            'nside_input': 2048,
            'ordering': Ordering.NESTED,
            'hdu': 0,
            'wav': [160., 350., 500.],
            'blank_value': -32768,
            'files_format': [ImageFormat.HEALPIX, ImageFormat.HEALPIX, ImageFormat.HEALPIX],
        }

        region_input = {
            'coord1': 0.2,
            'coord2': -0,
            'coordsys': 'galactic',
            'region': 'point',
            'method': Method.MEDIAN,
        }

        path_image, path_plot, res = sed_extract(maps_input=maps_input, region_input=region_input,
                                                 plot=True,
                                                 save=True, output_path=OUTPUT_PATH)

        values_expected = pd.DataFrame([[160.000000, 26380.658203],
                                        [350.000000, 4539.180176],
                                        [500.000000, 1513.793579]],
                                       columns=['Wavelengths', 'SED'])
        precision = 1e-4

        value_res = pd.read_csv(res, delim_whitespace=True, header=0, index_col=False, keep_default_na=False)
        value_res.dropna(how='all', inplace=True)

        pd.testing.assert_frame_equal(value_res, values_expected, atol=precision)

    def test_sed_extract11(self):
        maps_input = {
            'maps': [
                ('%sCADE_AKARI_WideS_0.0_0.0_50x50_0.0143_GAL_TAN_20230209_100829.fits' % DATA_PATH),
                ('%sCADE_AKARI_160_0.0_0.0_50x50_0.0143_GAL_TAN_20220421_140923.fits' % DATA_PATH)],

            'nside_input': 2048,
            'ordering': Ordering.NESTED,
            'hdu': 0,
            'wav': [90., 160.],
            'blank_value': -32768,
            'files_format': [ImageFormat.WCS, ImageFormat.WCS],
        }

        region_input = {
            'coord1': 0.2,
            'coord2': -0,
            'coordsys': 'galactic',
            'region': 'circle-mask',
            'vals_to_define_region': [0.2],
            'method': Method.MEDIAN,
            'vals_to_define_bckgd': [1, 1, 10],
            'file_for_mask': ('%sHigal_350_4arcm_1_2048_partial.fits' % DATA_PATH),
            'file_format_for_mask': ImageFormat.HEALPIX,
        }

        rm_bckgd_input = {
            'method_bckgd': Method.MEDIAN,
            'rm_bckgd': 'mask',
        }

        path_image, path_plot, res = sed_extract(maps_input=maps_input, region_input=region_input,
                                                 rm_bckgd_input=rm_bckgd_input,
                                                 hdr_ref=(
                                                         '%sCADE_Higal_250_4arcm_0.0_0.0_50x50_0.0286_GAL_TAN_20220516_102840.fits' % DATA_PATH),
                                                 plot=True,
                                                 save=True, output_path=OUTPUT_PATH)

        values_expected = pd.DataFrame([[90.000000, 8468.197214, 5426.526462, 6355.071272],
                                        [160.000000, 8629.971505, 7834.326145, 8504.508399]],
                                       columns=['Wavelengths', 'SED', 'Bckgd_values', 'RMS_in_Bckgd'])
        precision = 1e-4

        value_res = pd.read_csv(res, delim_whitespace=True, header=0, index_col=False, keep_default_na=False)
        value_res.dropna(how='all', inplace=True)

        pd.testing.assert_frame_equal(value_res, values_expected, atol=precision)


if __name__ == '__main__':
    unittest.main()
