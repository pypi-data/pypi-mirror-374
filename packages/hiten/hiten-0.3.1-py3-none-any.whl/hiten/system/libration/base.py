r"""
hiten.system.libration.base
=====================

Abstract helpers to model Libration points of the Circular Restricted Three-Body Problem (CR3BP).

The module introduces two primary abstractions:

* :pyclass:`LinearData` - an immutable record storing the salient linear characteristics (eigenfrequencies and canonical basis) of the flow linearised at a libration point.
* :pyclass:`LibrationPoint` - an abstract base class encapsulating geometry, energetic properties, linear stability analysis and lazy construction of centre-manifold normal forms. 
   Concrete subclasses implement the specific coordinates of the collinear (:math:`L_1`, :math:`L_2`, :math:`L_3`) and triangular (:math:`L_4`, :math:`L_5`) points.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Tuple

import numpy as np

from hiten.algorithms.dynamics.hamiltonian import _HamiltonianSystem
from hiten.algorithms.dynamics.rtbp import _jacobian_crtbp
from hiten.algorithms.dynamics.utils.energy import (crtbp_energy,
                                                    energy_to_jacobi)
from hiten.algorithms.dynamics.utils.linalg import eigenvalue_decomposition
from hiten.utils.log_config import logger

if TYPE_CHECKING:
    from hiten.system.base import System
    from hiten.system.center import CenterManifold
    from hiten.system.orbits.base import PeriodicOrbit

# Constants for stability analysis mode
CONTINUOUS_SYSTEM = 0
DISCRETE_SYSTEM = 1


@dataclass(slots=True)
class LinearData:
    r"""
    Container with linearised CR3BP invariants.

    Parameters
    ----------
    mu : float
        Mass ratio :math:`\mu := m_2/(m_1+m_2)` of the primaries.
    point : str
        Identifier of the libration point (``'L1'``, ``'L2'`` or ``'L3'``).
    lambda1 : float | None
        Real hyperbolic eigenvalue :math:`\lambda_1>0` associated with the
        saddle behaviour along the centre-saddle subspace.
    omega1 : float
        First elliptic frequency :math:`\omega_1>0` of the centre subspace.
    omega2 : float
        Second elliptic frequency :math:`\omega_2>0` of the centre subspace.
    omega3: float | None
        Vertical frequency :math:`\omega_3` of the centre subspace.
    C : numpy.ndarray, shape (6, 6)
        Symplectic change-of-basis matrix such that :math:`C^{-1}AC` is in real
        Jordan canonical form, with :math:`A` the Jacobian of the vector
        field evaluated at the libration point.
    Cinv : numpy.ndarray, shape (6, 6)
        Precomputed inverse of :pyattr:`C`.

    Notes
    -----
    The record is *immutable* thanks to ``slots=True``; all fields are plain
    :pyclass:`numpy.ndarray` or scalars so the instance can be safely cached
    and shared among different computations.
    """
    mu: float
    point: str        # 'L1', 'L2', 'L3'
    lambda1: float | None
    omega1: float
    omega2: float
    omega3: float | None
    C: np.ndarray     # 6x6 symplectic transform
    Cinv: np.ndarray  # inverse


class LibrationPoint(ABC):
    r"""
    Abstract base class for Libration points of the CR3BP.

    Parameters
    ----------
    system : hiten.system.base.System
        Parent CR3BP model providing the mass ratio :math:`\mu` and utility
        functions.

    Attributes
    ----------
    mu : float
        Mass ratio :math:`\mu` of the primaries (copied from *system*).
    system : hiten.system.base.System
        Reference to the owner hiten.system.
    position : numpy.ndarray, shape (3,)
        Cartesian coordinates in the synodic rotating frame. Evaluated on
        first access and cached thereafter.
    energy : float
        Dimensionless mechanical energy evaluated via
        :pyfunc:`hiten.algorithms.dynamics.hiten.utils.energy.crtbp_energy`.
    jacobi_constant : float
        Jacobi integral :math:`C_J = -2E` corresponding to
        :pyattr:`energy`.
    is_stable : bool
        True if all eigenvalues returned by :pyfunc:`analyze_stability` lie
        inside the unit circle (discrete case) or have non-positive real
        part (continuous case).
    eigenvalues : tuple(numpy.ndarray, numpy.ndarray, numpy.ndarray)
        Arrays of stable, unstable and centre eigenvalues.
    eigenvectors : tuple(numpy.ndarray, numpy.ndarray, numpy.ndarray)
        Bases of the corresponding invariant subspaces.
    linear_data : LinearData
        Record with canonical invariants and symplectic basis returned by the
        normal-form computation.

    Notes
    -----
    The class is *abstract*. Concrete subclasses must implement:

    * :pyfunc:`idx`
    * :pyfunc:`_calculate_position`
    * :pyfunc:`_get_linear_data`
    * :pyfunc:`normal_form_transform`

    Heavy algebraic objects produced by the centre-manifold normal-form
    procedure are cached inside a dedicated
    :pyclass:`hiten.system.center.CenterManifold` instance to avoid memory
    bloat.

    Examples
    --------
    >>> from hiten.system.base import System
    >>> sys = System(mu=0.0121505856)   # Earth-Moon system
    >>> L1 = sys.libration_points['L1']
    >>> L1.position
    array([...])
    """
    
    def __init__(self, system: "System"):
        self.system = system
        self.mu = system.mu
        self._position = None
        self._stability_info = None
        self._linear_data = None
        self._energy = None
        self._jacobi_constant = None
        self._cache = {}
        self._cm_registry = {}

        self._dynsys = system.dynsys
        self._var_eq_system = system.var_dynsys
    
    def __str__(self) -> str:
        return f"{type(self).__name__}(mu={self.mu:.6e})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(mu={self.mu:.6e})"

    @property
    def dynsys(self):
        """Underlying vector field instance."""
        return self._dynsys
    
    @property
    def var_eq_system(self):
        """Underlying vector field instance."""
        return self._var_eq_system

    @property
    @abstractmethod
    def idx(self) -> int:
        pass

    @property
    def position(self) -> np.ndarray:
        r"""
        Get the position of the Libration point in the rotating frame.
        
        Returns
        -------
        ndarray
            3D vector [x, y, z] representing the position
        """
        if self._position is None:
            self._position = self._calculate_position()
        return self._position
    
    @property
    def energy(self) -> float:
        r"""
        Get the energy of the Libration point.
        """
        if self._energy is None:
            self._energy = self._compute_energy()
        return self._energy
    
    @property
    def jacobi_constant(self) -> float:
        r"""
        Get the Jacobi constant of the Libration point.
        """
        if self._jacobi_constant is None:
            self._jacobi_constant = self._compute_jacobi_constant()
        return self._jacobi_constant
    
    @property
    def is_stable(self) -> bool:
        r"""
        Check if the Libration point is linearly stable.

        A libration point is considered stable if its linear analysis yields no
        unstable eigenvalues. The check is performed on the continuous-time
        system by default.
        """
        if self._stability_info is None:
            # The default mode for analyze_stability is CONTINUOUS_SYSTEM,
            # which correctly classifies eigenvalues based on their real part
            # for determining stability.
            self.analyze_stability()
        
        unstable_eigenvalues = self._stability_info[1]
        return len(unstable_eigenvalues) == 0

    @property
    def linear_data(self) -> LinearData:
        r"""
        Get the linear data for the Libration point.
        """
        if self._linear_data is None:
            self._linear_data = self._get_linear_data()
        return self._linear_data

    @property
    def eigenvalues(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        r"""
        Get the eigenvalues of the linearized system at the Libration point.
        
        Returns
        -------
        tuple
            (stable_eigenvalues, unstable_eigenvalues, center_eigenvalues)
        """
        if self._stability_info is None:
            self.analyze_stability() # Ensure stability is analyzed
        sn, un, cn, _, _, _ = self._stability_info
        return (sn, un, cn)
    
    @property
    def eigenvectors(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        r"""
        Get the eigenvectors of the linearized system at the Libration point.
        
        Returns
        -------
        tuple
            (stable_eigenvectors, unstable_eigenvectors, center_eigenvectors)
        """
        if self._stability_info is None:
            self.analyze_stability() # Ensure stability is analyzed
        _, _, _, Ws, Wu, Wc = self._stability_info
        return (Ws, Wu, Wc)

    def cache_get(self, key) -> any:
        r"""
        Get item from cache.
        """
        return self._cache.get(key)
    
    def cache_set(self, key, value) -> any:
        r"""
        Set item in cache and return the value.
        """
        self._cache[key] = value
        return value
    
    def cache_clear(self) -> None:
        r"""
        Clear all cached data, including computed properties.
        """
        self._cache.clear()
        self._position = None
        self._stability_info = None
        self._linear_data = None
        self._energy = None
        self._jacobi_constant = None
        logger.debug(f"Cache cleared for {type(self).__name__}")

    def _compute_energy(self) -> float:
        r"""
        Compute the energy of the Libration point.
        """
        state = np.concatenate([self.position, [0, 0, 0]])
        return crtbp_energy(state, self.mu)

    def _compute_jacobi_constant(self) -> float:
        r"""
        Compute the Jacobi constant of the Libration point.
        """
        return energy_to_jacobi(self.energy)

    @abstractmethod
    def _calculate_position(self) -> np.ndarray:
        r"""
        Calculate the position of the Libration point.
        
        This is an abstract method that must be implemented by subclasses.
        
        Returns
        -------
        ndarray
            3D vector [x, y, z] representing the position
        """
        pass

    @abstractmethod
    def _get_linear_data(self) -> LinearData:
        r"""
        Get the linear data for the Libration point.
        """
        pass

    def analyze_stability(self, discrete: int = CONTINUOUS_SYSTEM, delta: float = 1e-4) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        r"""
        Analyze the stability properties of the Libration point.
        
        Parameters
        ----------
        discrete : int, optional
            Classification mode for eigenvalues:
            * CONTINUOUS_SYSTEM (0): continuous-time system (classify by real part sign)
            * DISCRETE_SYSTEM (1): discrete-time system (classify by magnitude relative to 1)
        delta : float, optional
            Tolerance for classification
            
        Returns
        -------
        tuple
            (sn, un, cn, Ws, Wu, Wc) containing:
            - sn: stable eigenvalues
            - un: unstable eigenvalues
            - cn: center eigenvalues
            - Ws: eigenvectors spanning stable subspace
            - Wu: eigenvectors spanning unstable subspace
            - Wc: eigenvectors spanning center subspace
        """
        # Check cache first
        cache_key = ('stability_analysis', discrete, delta)
        cached = self.cache_get(cache_key)
        if cached is not None:
            logger.debug(f"Using cached stability analysis for {type(self).__name__}")
            self._stability_info = cached  # Update instance variable for property access
            return cached
        
        mode_str = "Continuous" if discrete == CONTINUOUS_SYSTEM else "Discrete"
        logger.info(f"Analyzing stability for {type(self).__name__} (mu={self.mu}), mode={mode_str}, delta={delta}.")
        pos = self.position
        A = _jacobian_crtbp(pos[0], pos[1], pos[2], self.mu)
        
        logger.debug(f"Jacobian calculated at position {pos}:\n{A}")

        # Perform eigenvalue decomposition and classification
        stability_info = eigenvalue_decomposition(A, discrete, delta)
        
        # Cache and store in instance variable
        self._stability_info = stability_info
        self.cache_set(cache_key, stability_info)
        
        sn, un, cn, _, _, _ = stability_info
        logger.info(f"Stability analysis complete: {len(sn)} stable, {len(un)} unstable, {len(cn)} center eigenvalues.")
        
        return stability_info

    def get_center_manifold(self, degree: int) -> "CenterManifold":
        r"""
        Return (and lazily construct) a CenterManifold of given degree.

        Heavy polynomial data (Hamiltonians in multiple coordinate systems,
        Lie generators, etc.) are cached *inside* the returned CenterManifold,
        not in the LibrationPoint itself.
        """
        from hiten.system.center import CenterManifold

        if degree not in self._cm_registry:
            self._cm_registry[degree] = CenterManifold(self, degree)
        return self._cm_registry[degree]

    def hamiltonian(self, max_deg: int) -> dict:
        r"""
        Return all Hamiltonian representations from the associated CenterManifold.

        Keys: 'physical', 'real_normal', 'complex_normal', 'normalized',
        'center_manifold_complex', 'center_manifold_real'.
        """
        cm = self.get_center_manifold(max_deg)
        cm.compute()  # ensures all representations are cached

        reprs = {}
        for label in (
            'physical',
            'real_normal',
            'complex_normal',
            'normalized',
            'center_manifold_complex',
            'center_manifold_real',
        ):
            data = cm.cache_get(('hamiltonian', max_deg, label))
            if data is not None:
                reprs[label] = [arr.copy() for arr in data]
        return reprs

    def hamiltonian_system(self, form: str, max_deg: int) -> _HamiltonianSystem:
        r"""
        Return the Hamiltonian system for the given form.
        """
        cm = self.get_center_manifold(max_deg)
        return cm._get_hamsys(form)

    def generating_functions(self, max_deg: int):
        r"""
        Return the Lie-series generating functions from CenterManifold.
        """
        cm = self.get_center_manifold(max_deg)
        cm.compute()  # ensure they exist
        data = cm.cache_get(('generating_functions', max_deg))
        return [] if data is None else [g.copy() for g in data]

    @abstractmethod
    def normal_form_transform(self) -> Tuple[np.ndarray, np.ndarray]:
        r"""
        Get the normal form transform for the Libration point.
        """
        pass

    def __getstate__(self):
        """
        Custom state extractor to enable pickling.

        We remove attributes that may contain unpickleable Numba runtime
        objects (e.g., the compiled variational dynamics system) and restore
        them on unpickling.
        """
        state = self.__dict__.copy()
        # Remove the compiled RHS system which cannot be pickled
        if '_var_eq_system' in state:
            state['_var_eq_system'] = None
        # Remove potential circular/self references to center manifolds
        if '_cm_registry' in state:
            state['_cm_registry'] = {}
        return state

    def __setstate__(self, state):
        """
        Restore object state after unpickling.

        The variational dynamics system is re-constructed because it was
        omitted during pickling (it contains unpickleable Numba objects).
        """
        # Restore the plain attributes
        self.__dict__.update(state)
        # Recreate the compiled variational dynamics system on demand
        from hiten.algorithms.dynamics.rtbp import variational_dynsys
        self._var_eq_system = variational_dynsys(
            self.mu, name=f"CR3BP Variational Equations for {self.__class__.__name__}")

        # Ensure _cm_registry exists after unpickling
        if not hasattr(self, '_cm_registry') or self._cm_registry is None:
            self._cm_registry = {}

    def create_orbit(self, family: str | type["PeriodicOrbit"], /, **kwargs) -> "PeriodicOrbit":
        r"""
        Create a periodic orbit *family* anchored at this libration point.

        The helper transparently instantiates the appropriate concrete
        subclass of :class:`hiten.system.orbits.base.PeriodicOrbit` and
        returns it.  The mapping is based on the *family* string or directly
        on a subclass type::

            L1 = system.get_libration_point(1)
            orb1 = L1.create_orbit("halo", amplitude_z=0.03, zenith="northern")
            orb2 = L1.create_orbit("lyapunov", amplitude_x=0.05)

        Parameters
        ----------
        family : str or PeriodicOrbit subclass
            Identifier of the orbit family or an explicit subclass type.
            Accepted strings (case-insensitive): ``"halo"``, ``"lyapunov"``,
            ``"vertical_lyapunov"`` and ``"generic"``.  If a subclass is
            passed, it is instantiated directly.
        **kwargs
            Forwarded verbatim to the underlying orbit constructor.

        Returns
        -------
        PeriodicOrbit
            Newly created orbit instance.
        """

        # Lazy imports to avoid circular dependencies and reduce import time.
        from hiten.system.orbits.base import GenericOrbit, PeriodicOrbit
        from hiten.system.orbits.halo import HaloOrbit
        from hiten.system.orbits.lyapunov import LyapunovOrbit
        from hiten.system.orbits.vertical import VerticalOrbit

        # Direct class provided
        if isinstance(family, type) and issubclass(family, PeriodicOrbit):
            orbit_cls = family
            return orbit_cls(self, **kwargs)

        # String identifier provided
        if not isinstance(family, str):
            raise TypeError("family must be either a string identifier or a PeriodicOrbit subclass")

        key = family.lower().strip()
        mapping: dict[str, type[PeriodicOrbit]] = {
            "halo": HaloOrbit,
            "lyapunov": LyapunovOrbit,
            "vertical_lyapunov": VerticalOrbit,
            "vertical": VerticalOrbit,
            "generic": GenericOrbit,
        }

        if key not in mapping:
            raise ValueError(
                f"Unknown orbit family '{family}'. Available options: {', '.join(mapping.keys())} "
                "or pass a PeriodicOrbit subclass directly."
            )

        orbit_cls = mapping[key]
        return orbit_cls(self, **kwargs)
