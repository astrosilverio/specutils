# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Tests for extinction curve."""

import numpy as np
from specutils.extinction import extinction
import pytest

extinction_models = ['ccm89', 'od94', 'gcc09', 'f99', 'fm07']

def test_extinction_shapes():

    for model in extinction_models:

        # single value should work
        extinction(1.e4, a_v=1., model=model)

        # multiple values should return appropriate shape
        assert extinction([1.e4], a_v=1., model=model).shape == (1,) 
        assert extinction([1.e4, 2.e4], a_v=1., model=model).shape == (2,)

# TODO: resolve discrepancy here (see notes below)
def test_extinction_ccm89():

    # U, B, V, R, I, J, H, K band effective wavelengths from CCM '89 table 3
    x_inv_microns = np.array([2.78, 2.27, 1.82, 1.43, 1.11, 0.80, 0.63, 0.46])

    # A(lambda)/A(V) for R_V = 3.1 from Table 3 of CCM '89
    ratio_true = np.array([1.569, 1.337, 1.000, 0.751, 0.479, 0.282,
                           0.190, 0.114])

    wave = 1.e4 / x_inv_microns  # wavelengths in Angstroms
    a_lambda_over_a_v = extinction(wave, a_v=1., r_v=3.1, model='ccm89')

    # So far, these are close but not exact.
    # I get: [ 1.56880904  1.32257836  1. 0.75125994  0.4780346   0.28206957
    #          0.19200814  0.11572348]

    # At the sigfigs of Table 3, the differences are:
    # [ None, 0.014, None, None, 0.001, None, 0.002, 0.002 ]
    # with B band being the most significant difference.

    # a and b can be obtained with:
    # b = extinction(wave, ebv=1., r_v=0., model='ccm89')
    # a = extinction(wave, ebv=1., r_v=1., model='ccm89') - b
    #
    # b = [ 1.90899552  0.99999783  0.         -0.36499617 -0.62299483
    #      -0.36794719 -0.25046607 -0.15095612]
    # a = [ 0.95300404  0.99999842  1.          0.86900064  0.67900067
    #       0.40076222  0.27280365  0.164419  ]
    #

    # Could be due to floating point errors in original paper?
    # Should compare to IDL routines.

@pytest.mark.xfail
def test_extinction_od94():
    """
    Tests the broadband extinction estimates from O'Donnell 1998
    at Rv = 3.1 against the widely used values tabulated in 
    Schlegel, Finkbeiner and Davis (1998)
    http://adsabs.harvard.edu/abs/1998ApJ...500..525S

    This is tested by evaluating the extinction curve at a (given)
    effective wavelength, since these effective wavelengths:
    "... represent(s) that wavelength on the extinction curve 
    with the same extinction as the full passband."

    The test does not include UKIRT L' (which, at 3.8 microns) is 
    beyond the range of wavelengths currently in specutils
    or the APM b_J filter which is defined in a non-standard way. 

    Precision is tested to the significance of the SFD98 
    tabulated values (1e-3).
    """
    sfd_eff_waves = np.array([3372.,4404.,5428.,
                    6509.,8090.,
                    3683.,4393.,5519.,6602.,8046.,
                    12660.,16732.,22152.,
                    5244.,6707.,7985.,9055.,
                    6993.,
                    3502.,4676.,4127.,
                    4861.,5479.,
                    3546.,4925.,6335.,7799.,9294.,
                    3047.,4711.,5498.,
                    6042.,7068.,8066.,
                    4814.,6571.,8183.])
    sfd_filter_names = np.array(['Landolt_U', 'Landolt_B','Landolt_V',
                        'Landolt_R','Landolt_I',
                        'CTIO_U','CTIO_B','CTIO_V','CTIO_R','CTIO_I',
                        'UKIRT_J','UKIRT_H','UKIRT_K',
                        'Gunn_g','Gunn_r','Gunn_i','Gunn_z',
                        'Spinard_R',
                        'Stromgren_u','Stromgren_b','Stromgren_v',
                        'Stromgren_beta','Stromgren_y',
                        'Sloan_u','Sloan_g','Sloan_r','Sloan_i','Sloan_z',
                        'WFPC2_F300W','WFPC2_F450W','WFPC2_F555W',
                        'WFPC2_F606W','WFPC2_F702W','WFPC2_F814W',
                        'DSSII_g','DSSII_r','DSSII_i'])
    sfd_table_alambda = np.array([1.664,1.321,1.015,
                        0.819,0.594,
                        1.521,1.324,0.992,0.807,0.601,
                        0.276,0.176,0.112,
                        1.065,0.793,0.610,0.472,
                        0.755,
                        1.602,1.240,1.394,
                        1.182,1.004,
                        1.579,1.161,0.843,0.639,0.453,
                        1.791,1.229,0.996,
                        0.885,0.746,0.597,
                        1.197,0.811,0.580])
    od94_alambda = extinction(sfd_eff_waves,a_v=1.,r_v=3.1,model='od94')
    #print(sfd_table_alambda-od94_alambda)
    np.testing.assert_allclose(sfd_table_alambda,od94_alambda,atol=1e-3)