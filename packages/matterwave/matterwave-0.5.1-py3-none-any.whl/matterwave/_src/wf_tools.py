from typing import Optional, Any
from functools import reduce

import fftarray as fa
from scipy.constants import pi, hbar, Boltzmann
import numpy as np

def norm(psi: fa.Array):
    """Compute the norm of the given fa.Array in its current space.

    Parameters
    ----------
    psi : fa.Array
        The wave function.

    Returns
    -------
    Any
        The norm of the fa.Array as a scalar array of the used Array API implementation.
        If ``xp.sum`` returns a Python float this would be a Python float.

    See Also
    --------
    matterwave.normalize
    """
    abs_sq: fa.Array = fa.abs(psi)**2 # type: ignore
    arr_norm: fa.Array = fa.integrate(abs_sq)
    return arr_norm.values(())

def normalize(psi: fa.Array) -> fa.Array:
    """Normalize the wave function.

    Parameters
    ----------
    psi : fa.Array
        The initial wave function.

    Returns
    -------
    fa.Array
        The normalized wave function.

    See Also
    --------
    matterwave.norm
    """
    norm_factor = psi.xp.sqrt(1./norm(psi))
    return psi * norm_factor

def get_e_kin(psi: fa.Array, mass: float, return_microK: bool = False):
    """Compute the kinetic energy of the given wave function with the given mass.

    Parameters
    ----------
    psi : fa.Array
        The wave function.
    mass : float
        The mass of the wave function.
    return_microK : bool, optional
        Return the kinetic energy in microK instead of Joule.

    Returns
    -------
    Any
        The kinetic energy as a scalar array of the used Array API implementation.
        If ``xp.sum`` returns a Python float this would be a Python float.

    See Also
    --------
    matterwave.expectation_value
    """
    # Move hbar**2/(2*m) until after accumulation to allow accumulation also in fp32.
    # Otherwise the individual values typically underflow to zero.
    kin_op = reduce(lambda a,b: a+b, [(2*np.pi*fa.coords_from_arr(psi, dim.name, "freq"))**2. for dim in psi.dims])
    post_factor = hbar**2/(2*mass)
    if return_microK:
        post_factor /= (Boltzmann * 1e-6)
    return expectation_value(psi, kin_op) * post_factor

def get_ground_state_ho(
            dim: fa.Dimension,
            *,
            mass: float,
            xp: Optional[Any] = None,
            dtype: Optional[Any] = None,
            device: Optional[Any] = None,
            omega: Optional[float] = None,
            sigma_p: Optional[float] = None,
        ) -> fa.Array:
    """Returns a wave function with the ground state of the 1-dimensional
    quantum harmonic oscillator (QHO). Either ``omega`` or ``sigma_p`` has to be specified.
    The ground state is centered at the origin in position and frequency space.
    The result is numerically normalized so that cut-off tails do not result in
    a norm smaller than ``1.``. This also means that even if the center is not
    sampled at all, the norm of the result is ``1.``.

    .. math::

        \\Psi (x) = \\left( \\frac{m \\omega}{\\pi \\hbar}  \\right)^\\frac{1}{4} e^{-\\frac{m\\omega x^2}{2\\hbar}}

    Parameters
    ----------
    dim:
        Dimension in which to create the QHO.
    mass:
        The mass of the matter wave.
    xp:
        Array API namespace to use for the creation of the :py:class:`fftarray.Array`.
    dtype:
        dtype passed to :py:func:`fftarray.coords_from_dim`.
    device:
        device passed to :py:func:`fftarray.coords_from_dim`.
    omega:
        The angular frequency of the QHO, by default None
    sigma_p:
        The momentum uncertainty, by default None

    Returns
    -------
    fa.Array
        The ground state.

    Raises
    ------
    ValueError
        If ``omega`` and ``sigma_p`` are both specified.

    See Also
    --------
    fftarray.coords_from_dim
    """
    if omega and sigma_p:
        raise ValueError("You can only the specify ground state width using either omega or sigma_p, not both.")
    if sigma_p:
        omega =  2 * (sigma_p**2) / (mass * hbar)
    assert omega, "Momentum width has not been specified via either sigma_p or omega."
    x: fa.Array = fa.coords_from_dim(dim, "pos", xp=xp, dtype=dtype, device=device)
    psi: fa.Array = (mass * omega / (pi*hbar))**(1./4.) * fa.exp(-(mass * omega * (x**2.)/(2.*hbar)))
    # Numerically normalize so that the norm is `1.` even if the tails of the Gaussian are cut off.
    psi = normalize(psi)
    return psi


def scalar_product(a: fa.Array, b: fa.Array):
    """Take the scalar product between two wave functions.

    Parameters
    ----------
    a : fa.Array
        Wavefunction <pos|a>
    b : fa.Array
        Wavefunction <pos|b>

    Returns
    -------
    Any
        The Scalar product as a scalar array of the used Array API implementation.
        If ``xp.sum`` returns a Python float this would be a Python float.
    """
    assert a.spaces == b.spaces
    bra_ket: fa.Array = fa.conj(a)*b # type: ignore
    return fa.integrate(bra_ket).values(())


def expectation_value(psi: fa.Array, op: fa.Array):
    """Compute the expectation value of the given diagonal operator on the
    fa.Array in the space of the operator.

    Parameters
    ----------
    wf : fa.Array
        The wave function.
    op : fa.Array
        The diagonal operator.

    Returns
    -------
    Any
        The expectation value of the given diagonal operator as a scalar array of the used Array API implementation.
        If ``xp.sum`` returns a Python float this would be a Python float.
    """
    psi_in_op_space = psi.into_space(op.spaces)
    # We can move the operator out of the scalar product because it is diagonal.
    # This way we can use the more efficient computation of psi_abs_sq.
    psi_abs_sq: fa.Array = fa.abs(psi_in_op_space)**2 # type: ignore
    return fa.integrate(psi_abs_sq*op).values(())
