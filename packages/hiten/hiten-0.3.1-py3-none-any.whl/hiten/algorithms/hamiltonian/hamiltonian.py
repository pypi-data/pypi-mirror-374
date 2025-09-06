r"""
hamiltonian.hamiltonian
==================

Construct polynomial representations of the Collinear Restricted Three-Body Problem (CR3BP)
Hamiltonian and the Lindstedt-Poincaré right-hand sides.

The routines generate multivariate polynomials (NumPy arrays wrapped in Numba typed
lists) that symbolically encode the rotating-frame Hamiltonian up to a prescribed
truncation degree.  These objects form the algebraic backbone for centre-manifold
reductions, normal-form computations, and invariant manifold analyses carried out
elsewhere in the package.

References
----------
Jorba, À., Masdemont, J. (1999). "Dynamics in the center manifold of the collinear points of the restricted
three body problem".
"""

from typing import Tuple

import numpy as np
from numba import njit, types
from numba.typed import List

from hiten.algorithms.polynomial.base import (_create_encode_dict_from_clmo,
                                              _init_index_tables, _combinations,
                                              _encode_multiindex)
from hiten.algorithms.polynomial.operations import (_polynomial_add_inplace,
                                                    _polynomial_multiply,
                                                    _polynomial_variable,
                                                    _polynomial_zero_list,
                                                    _substitute_affine)
from hiten.algorithms.utils.config import FASTMATH


@njit(fastmath=FASTMATH, cache=False)
def _build_T_polynomials(poly_x, poly_y, poly_z, max_deg: int, psi_table, clmo_table, encode_dict_list) -> types.ListType:
    r"""
    Compute three-dimensional Chebyshev polynomials of the first kind
    :math:`T_n(r)` where :math:`r = x / \sqrt{x^2 + y^2 + z^2}`.

    Parameters
    ----------
    poly_x, poly_y, poly_z : List[np.ndarray]
        Polynomial representations of the Cartesian coordinates :math:`x,y,z`.
    max_deg : int
        Highest order :math:`n` such that :math:`T_n` is returned.
    psi_table : ndarray
        Combinatorial index table produced by
        :pyfunc:`hiten.algorithms.polynomial.base._init_index_tables`.
    clmo_table : List[np.ndarray]
        Packed multi-index table returned by *_init_index_tables*.
    encode_dict_list : List[dict]
        Lookup tables mapping packed multi-indices to coefficient positions.

    Returns
    -------
    List[List[np.ndarray]]
        Numba typed list; element *i* holds the coefficients of :math:`	T_i`.

    Raises
    ------
    None

    Notes
    -----
    The classical recurrence
    :math:`T_0 = 1,\; T_1 = r,\; T_n = 2 r\,T_{n-1} - T_{n-2}`
    becomes in Cartesian variables
    :math:`T_n = \frac{2n-1}{n}\,x\,T_{n-1}-\frac{n-1}{n}\,(x^2 + y^2 + z^2)\,T_{n-2}`.
    """
    poly_T_list_of_polys = List()
    for _ in range(max_deg + 1):
        poly_T_list_of_polys.append(_polynomial_zero_list(max_deg, psi_table))

    if max_deg >= 0 and len(poly_T_list_of_polys[0]) > 0 and len(poly_T_list_of_polys[0][0]) > 0:
        poly_T_list_of_polys[0][0][0] = 1.0
    if max_deg >= 1:
        poly_T_list_of_polys[1] = poly_x

    for n in range(2, max_deg + 1):
        n_ = float(n)
        a = (2 * n_ - 1) / n_
        b = (n_ - 1) / n_

        term1_mult = _polynomial_multiply(poly_x, poly_T_list_of_polys[n - 1], max_deg, psi_table, clmo_table, encode_dict_list)
        term1 = _polynomial_zero_list(max_deg, psi_table)
        _polynomial_add_inplace(term1, term1_mult, a)

        poly_x_sq = _polynomial_multiply(poly_x, poly_x, max_deg, psi_table, clmo_table, encode_dict_list)
        poly_y_sq = _polynomial_multiply(poly_y, poly_y, max_deg, psi_table, clmo_table, encode_dict_list)
        poly_z_sq = _polynomial_multiply(poly_z, poly_z, max_deg, psi_table, clmo_table, encode_dict_list)

        poly_sum_sq = _polynomial_zero_list(max_deg, psi_table)
        _polynomial_add_inplace(poly_sum_sq, poly_x_sq, 1.0)
        _polynomial_add_inplace(poly_sum_sq, poly_y_sq, 1.0)
        _polynomial_add_inplace(poly_sum_sq, poly_z_sq, 1.0)

        term2_mult = _polynomial_multiply(poly_sum_sq, poly_T_list_of_polys[n - 2], max_deg, psi_table, clmo_table, encode_dict_list)
        term2 = _polynomial_zero_list(max_deg, psi_table)
        _polynomial_add_inplace(term2, term2_mult, -b)

        poly_Tn = _polynomial_zero_list(max_deg, psi_table)
        _polynomial_add_inplace(poly_Tn, term1, 1.0)
        _polynomial_add_inplace(poly_Tn, term2, 1.0)
        poly_T_list_of_polys[n] = poly_Tn
    return poly_T_list_of_polys


@njit(fastmath=FASTMATH, cache=False)
def _build_R_polynomials(poly_x, poly_y, poly_z, poly_T: types.ListType, max_deg: int, psi_table, clmo_table, encode_dict_list) -> types.ListType:
    r"""
    Generate the auxiliary sequence :math:`R_n` required by the Lindstedt-Poincaré
    formulation.

    Parameters
    ----------
    poly_x, poly_y, poly_z : List[np.ndarray]
        Polynomial representations of :math:`x,y,z`.
    poly_T : List[List[np.ndarray]]
        Output of :pyfunc:`_build_T_polynomials`.
    max_deg, psi_table, clmo_table, encode_dict_list
        See :pyfunc:`_build_T_polynomials`.

    Returns
    -------
    List[List[np.ndarray]]
        Polynomials :math:`\{R_0,\dots,R_{\text{max\_deg}}\}`.

    Raises
    ------
    None

    Notes
    -----
    The recurrence implemented is
    \[
      \begin{aligned}
      R_0 &= -1,\\
      R_1 &= -3x,\\
      R_n &= \frac{2n+3}{n+2} x R_{n-1}
              - \frac{2n+2}{n+2} T_n
              - \frac{n+1}{n+2}(x^2+y^2+z^2) R_{n-2}.
      \end{aligned}
    \]
    """
    poly_R_list_of_polys = List()
    for _ in range(max_deg + 1):
        poly_R_list_of_polys.append(_polynomial_zero_list(max_deg, psi_table))

    if max_deg >= 0:
        # R_0 = -1
        if len(poly_R_list_of_polys[0]) > 0 and len(poly_R_list_of_polys[0][0]) > 0:
            poly_R_list_of_polys[0][0][0] = -1.0
    
    if max_deg >= 1:
        # R_1 = -3x
        r1_poly = _polynomial_zero_list(max_deg, psi_table)
        _polynomial_add_inplace(r1_poly, poly_x, -3.0)
        poly_R_list_of_polys[1] = r1_poly

    # Pre-calculate x^2, y^2, z^2, and x^2 + y^2 + z^2 as they are used in the loop
    poly_x_sq = None # Represents x^2
    poly_y_sq = None # Represents y^2
    poly_z_sq = None # Represents z^2
    poly_rho_sq = None # Represents x^2 + y^2 + z^2

    if max_deg >=2: # Only needed if the loop runs
        poly_x_sq = _polynomial_multiply(poly_x, poly_x, max_deg, psi_table, clmo_table, encode_dict_list)
        poly_y_sq = _polynomial_multiply(poly_y, poly_y, max_deg, psi_table, clmo_table, encode_dict_list)
        poly_z_sq = _polynomial_multiply(poly_z, poly_z, max_deg, psi_table, clmo_table, encode_dict_list)
        
        poly_rho_sq = _polynomial_zero_list(max_deg, psi_table)
        _polynomial_add_inplace(poly_rho_sq, poly_x_sq, 1.0)
        _polynomial_add_inplace(poly_rho_sq, poly_y_sq, 1.0)
        _polynomial_add_inplace(poly_rho_sq, poly_z_sq, 1.0)

    for n in range(2, max_deg + 1):
        n_ = float(n)
        
        coeff1 = (2.0 * n_ + 3.0) / (n_ + 2.0)
        coeff2 = (2.0 * n_ + 2.0) / (n_ + 2.0)
        coeff3 = (n_ + 1.0) / (n_ + 2.0)

        # Term 1: coeff1 * x * R_{n-1}
        term1_mult_x_Rnm1 = _polynomial_multiply(poly_x, poly_R_list_of_polys[n - 1], max_deg, psi_table, clmo_table, encode_dict_list)
        term1_poly = _polynomial_zero_list(max_deg, psi_table)
        _polynomial_add_inplace(term1_poly, term1_mult_x_Rnm1, coeff1)

        # Term 2: -coeff2 * T_n
        term2_poly = _polynomial_zero_list(max_deg, psi_table)
        # poly_T[n] is T_n
        _polynomial_add_inplace(term2_poly, poly_T[n], -coeff2)
        
        # Term 3: -coeff3 * (x^2 + y^2 + z^2) * R_{n-2}
        # poly_rho_sq is already computed if needed
        term3_mult_rhosq_Rnm2 = _polynomial_multiply(poly_rho_sq, poly_R_list_of_polys[n - 2], max_deg, psi_table, clmo_table, encode_dict_list)
        term3_poly = _polynomial_zero_list(max_deg, psi_table)
        _polynomial_add_inplace(term3_poly, term3_mult_rhosq_Rnm2, -coeff3)
        
        # Combine terms for R_n
        poly_Rn = _polynomial_zero_list(max_deg, psi_table)
        _polynomial_add_inplace(poly_Rn, term1_poly, 1.0)
        _polynomial_add_inplace(poly_Rn, term2_poly, 1.0)
        _polynomial_add_inplace(poly_Rn, term3_poly, 1.0)
        poly_R_list_of_polys[n] = poly_Rn
        
    return poly_R_list_of_polys


def _build_potential_U(poly_T, point, max_deg: int, psi_table) -> List[np.ndarray]:
    r"""
    Assemble the gravitational potential expansion
    :math:`U = -\sum_{n\ge 2} c_n T_n(r)`.

    Parameters
    ----------
    poly_T : List[List[np.ndarray]]
        Chebyshev polynomials from :pyfunc:`_build_T_polynomials`.
    point : Any
        Object exposing ``_cn(k)`` which returns the coefficient :math:`c_k`.
    max_deg : int
        Polynomial truncation degree.
    psi_table : ndarray
        See :pyfunc:`_build_T_polynomials`.

    Returns
    -------
    List[np.ndarray]
        Polynomial representation of :math:`U`.

    Raises
    ------
    None
    """
    poly_U = _polynomial_zero_list(max_deg, psi_table)
    for n in range(2, max_deg + 1):
        _polynomial_add_inplace(poly_U, poly_T[n], -point._cn(n))
    return poly_U


def _build_kinetic_energy_terms(poly_px, poly_py, poly_pz, max_deg: int, psi_table, clmo_table, encode_dict_list) -> List[np.ndarray]:
    r"""
    Build the kinetic energy term
    :math:`T = \frac{1}{2}(p_x^2 + p_y^2 + p_z^2)`.

    Parameters
    ----------
    poly_px, poly_py, poly_pz : List[np.ndarray]
        Polynomial representations of the canonical momenta.
    max_deg, psi_table, clmo_table, encode_dict_list
        See :pyfunc:`_build_T_polynomials`.

    Returns
    -------
    List[np.ndarray]
        Polynomial representation of :math:`T`.

    Raises
    ------
    None
    """
    poly_kinetic = _polynomial_zero_list(max_deg, psi_table)
    for poly_momentum in (poly_px, poly_py, poly_pz):
        term = _polynomial_multiply(poly_momentum, poly_momentum, max_deg, psi_table, clmo_table, encode_dict_list)
        _polynomial_add_inplace(poly_kinetic, term, 0.5)
    return poly_kinetic


def _build_rotational_terms(poly_x, poly_y, poly_px, poly_py, max_deg: int, psi_table, clmo_table, encode_dict_list) -> List[np.ndarray]:
    r"""
    Construct the Coriolis (rotational) contribution
    :math:`C = y\,p_x - x\,p_y`.

    Parameters
    ----------
    poly_x, poly_y : List[np.ndarray]
        Position polynomials.
    poly_px, poly_py : List[np.ndarray]
        Momentum polynomials.
    max_deg, psi_table, clmo_table, encode_dict_list
        See :pyfunc:`_build_T_polynomials`.

    Returns
    -------
    List[np.ndarray]
        Polynomial representation of :math:`C`.

    Raises
    ------
    None
    """
    poly_rot = _polynomial_zero_list(max_deg, psi_table)
    
    term_ypx = _polynomial_multiply(poly_y, poly_px, max_deg, psi_table, clmo_table, encode_dict_list)
    _polynomial_add_inplace(poly_rot, term_ypx, 1.0)

    term_xpy = _polynomial_multiply(poly_x, poly_py, max_deg, psi_table, clmo_table, encode_dict_list)
    _polynomial_add_inplace(poly_rot, term_xpy, -1.0)
    
    return poly_rot


def _build_physical_hamiltonian_collinear(point, max_deg: int) -> List[np.ndarray]:
    r"""
    Combine kinetic, potential, and Coriolis parts to obtain the full
    rotating-frame Hamiltonian :math:`H = T + U + C`.

    Parameters
    ----------
    point : Any
        Object with method ``_cn(k)`` returning the potential coefficient
        :math:`c_k` of order *k*.
    max_deg : int
        Truncation degree for every polynomial sub-component.

    Returns
    -------
    List[np.ndarray]
        Hamiltonian coefficients up to *max_deg*.

    Raises
    ------
    None

    Examples
    --------
    >>> from hiten.algorithms.hamiltonian.center.hamiltonian import _build_physical_hamiltonian_collinear
    >>> H = _build_physical_hamiltonian_collinear(l1_point, max_deg=6)  # doctest: +SKIP
    """
    psi_table, clmo_table = _init_index_tables(max_deg)
    encode_dict_list = _create_encode_dict_from_clmo(clmo_table)

    poly_H = _polynomial_zero_list(max_deg, psi_table)

    poly_x, poly_y, poly_z, poly_px, poly_py, poly_pz = [
        _polynomial_variable(i, max_deg, psi_table, clmo_table, encode_dict_list) for i in range(6)
    ]

    poly_kinetic = _build_kinetic_energy_terms(poly_px, poly_py, poly_pz, max_deg, psi_table, clmo_table, encode_dict_list)
    _polynomial_add_inplace(poly_H, poly_kinetic, 1.0)

    poly_rot = _build_rotational_terms(poly_x, poly_y, poly_px, poly_py, max_deg, psi_table, clmo_table, encode_dict_list)
    _polynomial_add_inplace(poly_H, poly_rot, 1.0)

    poly_T = _build_T_polynomials(poly_x, poly_y, poly_z, max_deg, psi_table, clmo_table, encode_dict_list)
    
    poly_U = _build_potential_U(poly_T, point, max_deg, psi_table)

    _polynomial_add_inplace(poly_H, poly_U, 1.0)

    # Remove the constant term (equilibrium potential energy) 
    if len(poly_H) > 0 and len(poly_H[0]) > 0:
        poly_H[0][0] = 0.0

    return poly_H

@njit(fastmath=FASTMATH, cache=False)
def _build_A_polynomials(poly_x, poly_y, poly_z, d_x: float, d_y: float, max_deg: int, psi_table, clmo_table, encode_dict_list) -> types.ListType:
    poly_A_list = List()
    for _ in range(max_deg + 1):
        poly_A_list.append(_polynomial_zero_list(max_deg, psi_table))

    # A_0 = 1
    if max_deg >= 0 and len(poly_A_list[0]) > 0 and len(poly_A_list[0][0]) > 0:
        poly_A_list[0][0][0] = 1.0

    # A_1 = d_x * x + d_y * y  (note: z component of d is zero in planar primaries)
    if max_deg >= 1:
        poly_A1 = _polynomial_zero_list(max_deg, psi_table)
        if d_x != 0.0:
            _polynomial_add_inplace(poly_A1, poly_x, d_x)
        if d_y != 0.0:
            _polynomial_add_inplace(poly_A1, poly_y, d_y)
        poly_A_list[1] = poly_A1

    if max_deg < 2:
        return poly_A_list

    # Pre-compute rho^2 = x^2 + y^2 + z^2 and dot = d_x x + d_y y
    poly_x_sq = _polynomial_multiply(poly_x, poly_x, max_deg, psi_table, clmo_table, encode_dict_list)
    poly_y_sq = _polynomial_multiply(poly_y, poly_y, max_deg, psi_table, clmo_table, encode_dict_list)
    poly_z_sq = _polynomial_multiply(poly_z, poly_z, max_deg, psi_table, clmo_table, encode_dict_list)

    poly_rho2 = _polynomial_zero_list(max_deg, psi_table)
    _polynomial_add_inplace(poly_rho2, poly_x_sq, 1.0)
    _polynomial_add_inplace(poly_rho2, poly_y_sq, 1.0)
    _polynomial_add_inplace(poly_rho2, poly_z_sq, 1.0)

    poly_dot = _polynomial_zero_list(max_deg, psi_table)
    if d_x != 0.0:
        _polynomial_add_inplace(poly_dot, poly_x, d_x)
    if d_y != 0.0:
        _polynomial_add_inplace(poly_dot, poly_y, d_y)

    # Recurrence: A_{n+1} = ((2n+1)/(n+1)) (dot) A_n - (n/(n+1)) rho2 A_{n-1}
    for n in range(1, max_deg):  # n corresponds to current highest index (A_n)
        n_ = float(n)
        coeff1 = (2.0 * n_ + 1.0) / (n_ + 1.0)
        coeff2 = n_ / (n_ + 1.0)

        # term1 = coeff1 * dot * A_n
        term1_mult = _polynomial_multiply(poly_dot, poly_A_list[n], max_deg, psi_table, clmo_table, encode_dict_list)
        term1 = _polynomial_zero_list(max_deg, psi_table)
        _polynomial_add_inplace(term1, term1_mult, coeff1)

        # term2 = -coeff2 * rho2 * A_{n-1}
        term2_mult = _polynomial_multiply(poly_rho2, poly_A_list[n - 1], max_deg, psi_table, clmo_table, encode_dict_list)
        term2 = _polynomial_zero_list(max_deg, psi_table)
        _polynomial_add_inplace(term2, term2_mult, -coeff2)

        # Combine to obtain A_{n+1}
        poly_An1 = _polynomial_zero_list(max_deg, psi_table)
        _polynomial_add_inplace(poly_An1, term1, 1.0)
        _polynomial_add_inplace(poly_An1, term2, 1.0)

        poly_A_list[n + 1] = poly_An1

    return poly_A_list


def _build_physical_hamiltonian_triangular(point, max_deg: int) -> List[np.ndarray]:
    r"""
    Construct the rotating-frame Hamiltonian expanded around a triangular
    (L4/L5) equilibrium to arbitrary polynomial degree *max_deg*.

    The starting expression is the (already shifted) Hamiltonian quoted in
    Gómez et al. (2001, eq. 57):

    :math:`
        H = \\tfrac12 (p_x^2 + p_y^2 + p_z^2) + y p_x - x p_y 
            + \\bigl(\tfrac12 - \\mu\\bigr)\\,x \;\pm\; \\tfrac{\\sqrt{3}}{2}\\,y
            - \\frac{1-\\mu}{r_{PS}} - \\frac{\\mu}{r_{PJ}}`

    where the distances to the primaries written in *local* coordinates are

    :math:`
        r_{PS}^2 = (x - x_S)^2 + (y - y_S)^2 + z^2,\\,
        r_{PJ}^2 = (x - x_J)^2 + (y - y_J)^2 + z^2,\\,
        (x_S, y_S) = \\bigl(\\, +\\tfrac12, \; s \\tfrac{\\sqrt{3}}{2}\\bigr),\\qquad
        (x_J, y_J) = \\bigl(\\, -\\tfrac12, \; s \\tfrac{\\sqrt{3}}{2}\\bigr)`

    with *s = +1* for L4 and *s = -1* for L5.  At the equilibrium the
    distances equal one, hence we may expand each inverse distance with the
    binomial series

    :math:`
        \\frac{1}{r} = \\bigl(1 + u\\bigr)^{-1/2} = \\sum_{k\\ge 0} \\binom{-1/2}{k}
        u^k, \\qquad u = r^2 - 1.`
    """
    psi_table, clmo_table = _init_index_tables(max_deg)
    encode_dict_list = _create_encode_dict_from_clmo(clmo_table)

    poly_x, poly_y, poly_z, poly_px, poly_py, poly_pz = [
        _polynomial_variable(i, max_deg, psi_table, clmo_table, encode_dict_list)
        for i in range(6)
    ]

    poly_H = _polynomial_zero_list(max_deg, psi_table)

    poly_T = _build_kinetic_energy_terms(
        poly_px, poly_py, poly_pz,
        max_deg, psi_table, clmo_table, encode_dict_list,
    )
    _polynomial_add_inplace(poly_H, poly_T, 1.0)

    poly_C = _build_rotational_terms(
        poly_x, poly_y, poly_px, poly_py,
        max_deg, psi_table, clmo_table, encode_dict_list,
    )
    _polynomial_add_inplace(poly_H, poly_C, 1.0)

    mu = float(point.mu)
    sgn = float(point.sign)  # +1 for L4, -1 for L5

    poly_linear = _polynomial_zero_list(max_deg, psi_table)
    _polynomial_add_inplace(poly_linear, poly_x, 0.5 - mu)
    _polynomial_add_inplace(poly_linear, poly_y, - sgn * np.sqrt(3) / 2.0)
    _polynomial_add_inplace(poly_H, poly_linear, 1.0)

    # Linear dot products with the primary offsets
    d_Sx, d_Sy = 0.5, sgn * np.sqrt(3) / 2.0    # Primary at negative x
    d_Jx, d_Jy = -0.5, sgn * np.sqrt(3) / 2.0     # Secondary at positive x

    # Construct inverse distances via Legendre-type homogeneous polynomials
    poly_A_S = _build_A_polynomials(
        poly_x, poly_y, poly_z,
        d_Sx, d_Sy,
        max_deg, psi_table, clmo_table, encode_dict_list,
    )
    poly_A_J = _build_A_polynomials(
        poly_x, poly_y, poly_z,
        d_Jx, d_Jy,
        max_deg, psi_table, clmo_table, encode_dict_list,
    )

    # The expansion of 1/r_PS is A_0 + A_1 + A_2 + ... 
    # At equilibrium, A_0 = 1, and we want to subtract the constant part
    poly_inv_r_S = _polynomial_zero_list(max_deg, psi_table)
    poly_inv_r_J = _polynomial_zero_list(max_deg, psi_table)

    # Add all A_n terms for each primary
    for n in range(0, min(len(poly_A_S), max_deg + 1)):
        _polynomial_add_inplace(poly_inv_r_S, poly_A_S[n], 1.0)
        
    for n in range(0, min(len(poly_A_J), max_deg + 1)):
        _polynomial_add_inplace(poly_inv_r_J, poly_A_J[n], 1.0)

    # Construct the potential: -(1-mu)/r_PS - mu/r_PJ
    poly_U = _polynomial_zero_list(max_deg, psi_table)
    _polynomial_add_inplace(poly_U, poly_inv_r_S, -(1.0 - mu))
    _polynomial_add_inplace(poly_U, poly_inv_r_J, -mu)
    _polynomial_add_inplace(poly_H, poly_U, 1.0)

    # Remove the constant term (equilibrium potential energy = -1)
    if len(poly_H) > 0 and len(poly_H[0]) > 0:
        poly_H[0][0] = 0.0

    return poly_H


def _build_lindstedt_poincare_rhs_polynomials(point, max_deg: int) -> Tuple[List, List, List]:
    r"""
    Compute RHS polynomials for the first Lindstedt-Poincaré iteration.

    Parameters
    ----------
    point : Any
        Provider of the sequence :math:`c_k` via ``_cn``.
    max_deg : int
        Truncation degree.

    Returns
    -------
    Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray]]
        Polynomials for the x-, y-, and z-equations, respectively.

    Raises
    ------
    None

    Examples
    --------
    >>> rhs_x, rhs_y, rhs_z = _build_lindstedt_poincare_rhs_polynomials(l1_point, 6)  # doctest: +SKIP
    """
    psi_table, clmo_table = _init_index_tables(max_deg)
    encode_dict_list = _create_encode_dict_from_clmo(clmo_table)

    poly_x, poly_y, poly_z = [
        _polynomial_variable(i, max_deg, psi_table, clmo_table, encode_dict_list) for i in range(3)
    ]

    poly_T_list = _build_T_polynomials(poly_x, poly_y, poly_z, max_deg, psi_table, clmo_table, encode_dict_list)
    poly_R_list = _build_R_polynomials(poly_x, poly_y, poly_z, poly_T_list, max_deg, psi_table, clmo_table, encode_dict_list)

    rhs_x_poly = _polynomial_zero_list(max_deg, psi_table)

    sum_term_for_y_z_eqs = _polynomial_zero_list(max_deg, psi_table)

    for n in range(2, max_deg + 1):
        cn_plus_1 = point._cn(n + 1)
        coeff = cn_plus_1 * float(n + 1)
        _polynomial_add_inplace(rhs_x_poly, poly_T_list[n], coeff)

    for n in range(2, max_deg + 1):
        cn_plus_1 = point._cn(n + 1)
        if (n - 1) < len(poly_R_list):
            _polynomial_add_inplace(sum_term_for_y_z_eqs, poly_R_list[n - 1], cn_plus_1)

    rhs_y_poly = _polynomial_multiply(poly_y, sum_term_for_y_z_eqs, max_deg, psi_table, clmo_table, encode_dict_list)

    rhs_z_poly = _polynomial_multiply(poly_z, sum_term_for_y_z_eqs, max_deg, psi_table, clmo_table, encode_dict_list)
    
    return rhs_x_poly, rhs_y_poly, rhs_z_poly
