import numpy as np
from scipy.optimize import least_squares

from brighteyes_ism.analysis.APR_lib import ShiftVectors
from .shift_vectors_minimizer import rotation_matrix, find_parameters

def gaussian_2d(params, x, y):
    """
    Compute a 2D Gaussian.

    Parameters
    ----------
    params : array-like
        [amplitude, x0, y0, sigma, offset]
    x : np.ndarray
        X-coordinates
    y : np.ndarray
        Y-coordinates

    Returns
    -------
    np.ndarray
        2D Gaussian evaluated at (x, y)
    """

    a, x0, y0, sigma, b = params
    return a * np.exp(-((x - x0)**2 + (y - y0)**2) / (2 * sigma**2)) + b

def residuals(params, x, y, data):
    """
    Compute residuals between data and 2D Gaussian model.

    Parameters
    ----------
    params : array-like
        Gaussian parameters
    x : np.ndarray
        X-coordinates
    y : np.ndarray
        Y-coordinates
    data : np.ndarray
        Observed data

    Returns
    -------
    np.ndarray
        Flattened residuals
    """

    model = gaussian_2d(params, x, y)
    return (model - data).ravel()

def gaussian_fit(image):
    """
    Fit a 2D Gaussian to an image.

    Parameters
    ----------
    image : np.ndarray
        2D input image

    Returns
    -------
    tuple or None
        (x shift, y shift, fitted parameters, fitted Gaussian) if successful, else None
    """

    image = image / image.max()  # Normalize

    h, w = image.shape
    y, x = np.mgrid[0:h, 0:w]

    # Initial guess
    a0 = image.max() - image.min()
    x0_0 = (w-1) / 2
    y0_0 = (h-1) / 2
    sigma0 = min(h, w) / 4
    b0 = image.min()
    p0 = [a0, x0_0, y0_0, sigma0, b0]

    # Parameter bounds
    bounds = (
        [0,        0,     0,     0.5,    0],  # lower bounds
        [image.max(),   w,     h,     w,      image.min()]    # upper bounds
    )

    result = least_squares(
        residuals,
        p0,
        args=(x, y, image),
        bounds=bounds,
        method='trf',
        loss='cauchy',
        f_scale=0.1     # sensitivity to outliers
    )

    gfit = gaussian_2d(result.x, x, y)

    if result.success:
        _, x0, y0, _, _ = result.x
        return x0 - x0_0, y0 - y0_0, result.x, gfit
    else:
        return None  # fitting failed
    
def find_misalignment(dset, pxpitch, mag, na, wl):
    """
    Estimate tip and tilt misalignment from a PSF dataset.

    Parameters
    ----------
    dset : np.ndarray
        Input PSF dataset
    pxpitch : float
        Pixel pitch
    mag : float
        Magnification
    na : float
        Numerical aperture
    wl : float
        Wavelength

    Returns
    -------
    tuple
        (tip, tilt) misalignment values
    """

    nch = int(np.sqrt(dset.shape[-1]))

    axis_to_sum = tuple(np.arange(dset.ndim-1)) # It automatically takes into account time, if present

    fingerprint = dset.sum(axis_to_sum).reshape(nch, nch)

    gauss = gaussian_fit(fingerprint)
    
    if gauss is None:
        print('\n Warning: Fitting not successful. Using no tip and no tilt.\n')
        tip, tilt = np.zeros(2)
    else:
        scale = 2*np.pi*na/wl
        pxsize = pxpitch/mag
        
        coords = -np.asarray([gauss[1], gauss[0]])
        
        shift, _ = ShiftVectors(dset[5:-5, 5:-5], 50, dset.shape[-1]//2, filter_sigma=1)
        _, rotation, mirroring = find_parameters(shift)

        if mirroring == -1:
            coords[1] *= -1

        rm = rotation_matrix(rotation)

        rot_coords = np.einsum('ij, j -> i', rm, coords)
        
        tip, tilt = rot_coords * pxsize * scale

    return tip, tilt

def realign_psf(psf):
    """
    Realign a PSF stack so the brightest pixel is centered.

    Parameters
    ----------
    psf : np.ndarray
        Input PSF stack (nz, ny, nx, nch)

    Returns
    -------
    np.ndarray
        Realigned PSF stack
    """

    nz, ny, nx, nch = psf.shape
    patch = psf[0].sum(-1)

    yc, xc = ny // 2, nx // 2  # integer center

    # Find coordinates of the brightest pixel
    peak_index = np.argmax(patch)
    y_peak, x_peak = np.unravel_index(peak_index, patch.shape)

    # Compute integer shift needed
    y_shift = yc - y_peak
    x_shift = xc - x_peak

    # Apply integer pixel shift using

    aligned_psf = np.empty_like(psf)

    for z in range(nz):
        aligned_psf[z] = np.roll(psf[z], shift=y_shift, axis=0)
        aligned_psf[z] = np.roll(aligned_psf[z], shift=x_shift, axis=1)

    return aligned_psf