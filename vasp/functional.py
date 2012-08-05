# -*- coding: utf-8 -*-
""" Sub-package containing the functional. """
__docformat__ = "restructuredtext en"
__all__ = ['Vasp']
from ..functools import stateless, assign_attributes
from ..functools.block import AttrBlock
from ..misc import add_setter
from extract import Extract


class Vasp(AttrBlock):
  """ Interface to VASP code. """
  Extract = staticmethod(Extract)
  """ Extraction class. """

  def __init__(self, copy=None, species=None, kpoints=None, **kwargs):
    """ Initializes vasp class. """
    from .keywords import BoolKeyword, Magmom, System, Npar, ExtraElectron,    \
                          NElect, Algo, Ediff, Ediffg, Encut, EncutGW, IStart, \
                          ICharg, IStruc, LDAU, PrecFock, Precision, Nsw,     \
                          Isif, IBrion, Relaxation, ISmear, LSorbit, Sigma,    \
                          LMaxMix, EdiffPerAtom, EdiffgPerAtom
    from ..functools.keywords import TypedKeyword, ChoiceKeyword
    super(Vasp, self).__init__()

    self.species = species if species is not None else {}
    """ Species in the system. """
    self.kpoints = kpoints if kpoints is not None \
                   else "\n0\nM\n4 4 4\n0 0 0"
    """ kpoints for which to perform calculations. """
    self.restart = kwargs.get('restart', None)
    """ Calculation from which to restart. 

        Depending on the values of istart_, icharg_, and istruc_, this
        calculation will copy the charge density, wavefunctions, and structure
        from this object. It should be either None, or an extraction object
        returned by a previous calculation::

        .. code-block :: python

           calc1 = vasp(structure)
           calc2 = vasp(structure, restart=calc2, nonscf=True)

        The snippet above performs a non-self-consistent calculation using the
        first calculation. In this example, it is expected that istart_,
        icharg_, and istruc_ are all set to 'auto', in which case LaDa knows to
        do the right thing, e.g. copy whatever is available, and nothing is
        ``vasp.restart is None``.

        .. note:: The calculation from which to restart needs be successful,
        otherwise it is not considered.

        .. seealso:: istart_, istruc_, icharg_

        .. _istruc: :py:attr:`~lada.vasp.functional.Functional.istruc`
        .. _istart: :py:attr:`~lada.vasp.functional.Functional.istart`
        .. _icharg: :py:attr:`~lada.vasp.functional.Functional.icharg`
    """

    self.program = kwargs.get('program', None)
    """ Path to vasp program. 
    
        Can be one of the following:

          - None: defaults to :py:attr:`~lada.vasp_program`.
            :py:attr:`~lada.vasp_program` can take the same values as described
            here, except for None.
          - string: Should be the path to the vasp executable. It can be either
            a full path, or an executable within the environment's $PATH
            variable.
          - callable: The callable is called with a :py:class:`~lada.vasp.Vasp`
            as sole argument. It should return a string, as described above.
            In other words, different vasp executables can be used depending on
            the parameters. 
    """
    self.addgrid = BoolKeyword()
    """ Adds additional support grid for augmentation charge evaluation. 

        Can be only True or False (or None for VASP_ default).

        .. seealso:: 

           ADDGRID_

           .. _ADDGRID: http://cms.mpi.univie.ac.at/wiki/index.php/ADDGRID
    """
    self.ispin   = ChoiceKeyword(values=(1, 2))
    """ Whether to perform spin-polarized or spin-unpolarized calculations.

        Can be only 1 or 2 (or None for VASP_ default).

        .. seealso:: 

           ISPIN_ 

           .. _ISPIN: http://cms.mpi.univie.ac.at/wiki/index.php/ISPIN
    """
    self.istart    = IStart(value='auto')
    """ Starting wavefunctions.
    
        This tag is about which wavefunction (WAVECAR) file to read from, if
        any.  It is best to keep this attribute set to -1, in which case, LaDa
        takes care of copying the relevant files.
    
          - -1, 'auto': (Default) Automatically determined by LaDA. Depends on
            the value of restart_ and the existence of the relevant files. If a
            WAVECAR file exists, then ISTART_ will be set to 1 (constant
            cutoff).
    
          - 0, 'scratch': Start from scratch.
    
          - 1, 'cutoff': Restart with constant cutoff.
    
          - 2, 'basis': Restart with constant basis.
    
          - 3, 'full': Full restart, including TMPCAR.

        This attribute can be set equivalently using an integer or a string, as
        shown above. In practice, the integers will be converted to strings
        within the python interface:

          >>> vasp.istart = 0
          >>> vasp.istart
          'scratch'

        .. note::
        
           Files are copied right before the calculation takes place, not when
           the attribute is set.
    
        .. seealso:: ISTART_, icharg_, istruc_, restart_
        .. _ISTART: http://cms.mpi.univie.ac.at/wiki/index.php/ISTART
        .. _restart: :py:attr:`~lada.vasp.functional.Functional.restart`
        .. _icharg: :py:attr:`~lada.vasp.functional.Functional.icharg`
        .. _istruc: :py:attr:`~lada.vasp.functional.Functional.istruc`
    """ 
    self.icharg    = ICharg('auto')
    """ Charge from which to start. 
    
        This tag decides whether to restart from a previously calculated charge
        density, or not. It is best to keep this attribute set to -1, in which
        case, LaDa takes care of copying the relevant files.
    
          - -1: (Default) Automatically determined by LaDA. Depends on the
                value of restart_ and the existence of the relevant files. Also
                takes care of non-scf bit.
    
          - 0: Tries to restart from wavefunctions. Uses the latest WAVECAR file
               between the one currently in the output directory and the one in
               the restart directory (if specified). Sets nonscf_ to False.
    
               .. note:: CHGCAR is also copied, just in case.
    
          - 1: Tries to restart from wavefunctions. Uses the latest WAVECAR file
               between the one currently in the output directory and the one in
               the restart directory (if specified). Sets nonscf_ to False.
    
          - 2: Superimposition of atomic charge densities. Sets nonscf_ to False.
    
          - 4: Reads potential from POT file (VASP-5.1 only). The POT file is
               deduced the same way as for CHGAR and WAVECAR above.  Sets nonscf_
               to False.
    
          - 10, 11, 12: Same as 0, 1, 2 above, but also sets nonscf_ to True. This
               is a shortcut. The value is actually kept to 0, 1, or 2:
    
               >>> vasp.icharg = 10
               >>> vasp.nonscf, vasp.icharg
               (True, 0)
    
        .. note::
        
           Files are copied right before the calculation takes place, not before.
    
        .. seealso:: ICHARG_, nonscf_, restart_, istruc_, istart_
    
        .. _ICHARG: http://cms.mpi.univie.ac.at/wiki/index.php/ICHARG
        .. _nonscf: :py:attr:`~lada.vasp.functional.Functional.nonscf`
        .. _restart: :py:attr:`~lada.vasp.functional.Functional.restart`
        .. _istruc: :py:attr:`~lada.vasp.functional.Functional.istruc`
        .. _istart: :py:attr:`~lada.vasp.functional.Functional.istart`
    """ 
    self.istruc    = IStruc('auto')
    """ Initial structure. 
    
        Determines which structure is written to the POSCAR. In practice, it
        makes it possible to restart a crashed job from the latest contcar.
        There are two possible options:
    
          - auto: LaDa determines automatically what to use. If a CONTCAR exists
                  in either the current directory or in the restart directory (if
                  any), then uses the latest. Otherwise, uses input structure.
          - scratch: Always uses input structure.
    
        If the run was given the ``overwrite`` option, then always uses the input
        structure.
    
        .. note:: There is no VASP equivalent to this option.
        .. seealso:: restart_, icharg_, istart_
    
        .. _restart: :py:attr:`~lada.vasp.functional.Functional.restart`
        .. _icharg: :py:attr:`~lada.vasp.functional.Functional.icharg`
        .. _istart: :py:attr:`~lada.vasp.functional.Functional.istart`
    """
    self.isym      = ChoiceKeyword(values=range(3))
    """ Symmetry scheme.

        .. seealso:: ISYM_
        .. _ISYM: http://cms.mpi.univie.ac.at/vasp/guide/node115.html
    """ 
    self.lmaxmix   = LMaxMix()
    """ Cutoff *l*-quantum number of PAW charge densities passed to mixer 

        .. seealso:: LMAXMIX_ 
        .. _LMAXMIX: http://cms.mpi.univie.ac.at/wiki/index.php/LMAXMIX
    """
    self.lorbit    = ChoiceKeyword(values=(0, 1, 2, 5, 10, 11, 12))
    """ Decides whether PROOUT and PROOCAR are writtent to disk.

        Can be one of 0|1|2|5|10|11|12|None. 

        .. seealso:: LORBIT_ 
        .. _LORBIT: http://cms.mpi.univie.ac.at/wiki/index.php/LORBIT
    """
    self.nbands    = TypedKeyword(type=int)
    self.nomega    = TypedKeyword(type=int)
    self.nupdown   = TypedKeyword(type=int)
    self.symprec   = TypedKeyword(type=float)
    self.lwave     = BoolKeyword(value=False)
    self.lcharg    = BoolKeyword(value=True)
    self.lvtot     = BoolKeyword(value=False)
    self.lrpa      = BoolKeyword()
    self.loptics   = BoolKeyword()
    self.lpead     = BoolKeyword()
    self.nelm      = TypedKeyword(type=int)
    self.nelmin    = TypedKeyword(type=int)
    self.nelmdl    = TypedKeyword(type=int)
    self.ngx       = TypedKeyword(type=int)
    self.ngy       = TypedKeyword(type=int)
    self.ngz       = TypedKeyword(type=int)
    self.nonscf    = BoolKeyword()
    """ If True, performs a non-self consistent calculation.

        The value of this keyword is checked by :py:attr:`icharg` and used
        appropriately.
    """
    
    self.magmom    = Magmom()
    """ Sets the initial magnetic moments on each atom.
    
        There are three types of usage: 
    
        - if None or False, does nothing
        - if calculations are not spin-polarized, does nothing.
        - if a string, uses that as for the MAGMOM_ keyword
        - if True and at least one atom in the structure has a non-zero
          ``magmom`` attribute, then creates the relevant moment input for
          VASP_
    
        If the calculation is **not** spin-polarized, then the magnetic moment
        tag is not set.
    
        .. note:: Please set by hand for non-collinear calculations

        .. seealso:: MAGMOM_

        .. _MAGMOM: http://cms.mpi.univie.ac.at/wiki/index.php/MAGMOM
    """
    self.system    = System()
    """ System title to use for calculation.
    
        - If None and ... 
           - if the structure has a ``name`` attribute, uses that as the
             calculations title
           - else does not use SYSTEM_ tag
        - If something else which is convertible to a string,  and ...
           - if the structure has a ``name`` attribute, uses 'string: name' as
             the title
           - otherwise, uses the string
    
        .. seealso:: SYSTEM_
        .. _SYSTEM: http://cms.mpi.univie.ac.at/vasp/guide/node94.html>
    """
    self.npar      = Npar()
    """ Parallelization over bands. 
    
        Npar defines how many nodes work on one band.
        It can be set to a particular number:
    
        >>> vasp.npar = 2
    
        Or it can be deduced automatically. Different schemes are available:
        
          - power of two: npar is set to the largest power of 2 which divides
            the number of processors.
   
            >>> vasp.npar = "power of two"
    
            If the number of processors is not a power of two, prints nothing.
    
          - square root: npar is set to the square root of the number of
            processors.
    
            >>> vasp.npar = "sqrt"
        
    
        .. seealso: NPAR_ 
        .. _NPAR: http://cms.mpi.univie.ac.at/vasp/guide/node138.html>
    """
    self.extraelectron = ExtraElectron()
    """ Number of electrons relative to neutral system.
        
        Gets the number of electrons in the (neutral) system. Then adds value to
        it and computes with the resulting number of electrons.
    
        >>> vasp.extraelectron =  0  # charge neutral system
        >>> vasp.extraelectron =  1  # charge -1 (1 extra electron)
        >>> vasp.extraelectron = -1  # charge +1 (1 extra hole)
    
        .. seealso:: NELECT_
        .. _NELECT: http://cms.mpi.univie.ac.at/wiki/index.php/NELECT
    """
    self.nelect = NElect()
    """ Sets the absolute number of electrons.
        
        Disables :py:attr:`lada.vasp.functional.Functional.extraelectron` if set to
        something other than None.
    
        .. seealso:: `NELECT <http://cms.mpi.univie.ac.at/wiki/index.php/NELECT>`_
    """
    self.algo = Algo()
    """ Electronic minimization. 
    
        Defines the kind of algorithm vasp will run.
          - very fast
          - fast, f (default)
          - normal, n
          - all, a
          - damped, d 
          - Diag 
          - conjugate, c (vasp 5)
          - subrot (vasp 5)
          - eigenval (vasp 5)
          - Nothing (vasp 5)
          - Exact  (vasp 5)
          - chi
          - gw
          - gw0
          - scgw
          - scgw0
    
        If :py:data:`is_vasp_4 <lada.is_vasp_4>` is an existing configuration
        variable of :py:mod:`lada` the parameters marked as vasp 5 will fail.
    
        .. warning:: The string None is not  allowed, as it would lead to
           confusion with the python object None. Please use "Nothing" instead.
           The python object None will simply not print the ALGO keyword to the
           INCAR file.
    
        .. note:: By special request, "fast" is the default algorithm.
    
        .. seealso:: ALGO_
        .. _ALGO: http://cms.mpi.univie.ac.at/vasp/vasp/ALGO_tag.html
    """ 
    self.ediff = Ediff()
    """ Sets the absolute energy convergence criteria for electronic minimization.
    
        EDIFF_ is set to this value in the INCAR. 
    
        Sets ediff_per_atom_ to None.
        If negative or null, defaults to zero.
    
        .. seealso:: EDIFF_, ediff_per_atom_
        .. _EDIFF: http://cms.mpi.univie.ac.at/wiki/index.php/EDIFFG
        .. _ediff_per_atom: :py:attr:`~lada.vasp.functional.Vasp.ediff_per_atom`
    """
    self.ediff_per_atom = EdiffPerAtom()
    """ Sets the relative energy convergence criteria for electronic minimization.
    
        EDIFF_ is set to this value *times* the number of atoms in the structure.
        This approach is more sensible than straight-off ediff_ when doing
        high-throughput over many structures.
    
        Sets ediff_ to None.
        If negative or null, defaults to zero.
    
        .. seealso:: EDIFF_, ediff_
        .. _EDIFF: http://cms.mpi.univie.ac.at/wiki/index.php/EDIFFG
        .. _ediff: :py:attr:`~lada.vasp.functional.Vasp.ediff`
    """
    self.ediffg = Ediffg()
    """ Sets the absolute energy convergence criteria for ionic relaxation.
    
        EDIFFG_ is set to this value in the INCAR. 
    
        Sets ediffg_per_atom_ to None.
    
        .. seealso:: EDIFFG_, ediffg_per_atom_
        .. _EDIFFG: http://cms.mpi.univie.ac.at/vasp/guide/node105.html
        .. _ediffg_per_atom: :py:attr:`~lada.vasp.functional.Vasp.ediffg_per_atom`
    """
    self.ediffg_per_atom = EdiffgPerAtom()
    """ Sets the relative energy convergence criteria for ionic relaxation.
  
        - if positive: EDIFFG_ is set to this value *times* the number of atoms
          in the structure. This means that the criteria is for the total energy per atom.
        - if negative: same as a negative EDIFFG_, since that convergence
          criteria is already per atom.
        
        This approach is more sensible than straight-off ediffg_ when doing
        high-throughput over many structures.
  
        Sets ediffg_ to None.
  
        .. seealso:: EDIFFG_, ediff_
        .. _EDIFFG: http://cms.mpi.univie.ac.at/wiki/index.php/EDIFFG
        .. _ediffg: :py:attr:`~lada.vasp.functional.Vasp.ediffg`
    """
    self.encut = Encut()
    """ Defines cutoff factor for calculation. 
    
        There are three ways to set this parameter:
    
        - if value is floating point and 0 < value <= 3: then the cutoff is
          ``value * ENMAX``, where ENMAX is the maximum recommended cutoff for
          the species in the system.
        - if value > 3 eV, then ENCUT_ is exactly value (in eV). Any energy
          unit is acceptable.
        - if value < 0 eV or None, does not print anything to INCAR. 
        
        .. seealso:: `ENCUT <http://cms.mpi.univie.ac.at/vasp/vasp/ENCUT_tag.html>`_
    """
    self.encutgw = EncutGW()
    """ Defines cutoff factor for GW calculation. 
  
        There are three ways to set this parameter:
  
        - if value is floating point and 0 < value <= 3: then the cutoff is
          ``value * ENMAX``, where ENMAX is the maximum recommended cutoff for
          the species in the system.
        - if value > 3 eV, then ENCUTGW_ is exactly value (in eV). Any energy
          unit is acceptable.
        - if value < 0 eV or None, does not print anything to INCAR. 
        
        .. seealso:: ENCUTGW_
        .. _ENCUTGW: http://cms.mpi.univie.ac.at/wiki/index.php/GW_calculations
    """
    self.istart = IStart()
    """ Starting wavefunctions.
    
        It is best to keep this attribute set to -1, in which case, LaDa takes
        care of copying the relevant files.
    
          - -1: Automatically determined by LaDA. Depends on the value of
                restart_ and the existence of the relevant files.
    
          - 0: Start from scratch.
    
          - 1: Restart with constant cutoff.
    
          - 2: Restart with constant basis.
    
          - 3: Full restart, including TMPCAR.
    
        .. note::
        
           Files are copied right before the calculation takes place, not
           before.
    
        .. seealso:: ISTART_
    
        .. _ISTART: http://cms.mpi.univie.ac.at/wiki/index.php/ISTART
        .. _restart: :py:attr:`~lada.vasp.functional.Functional.restart`
    """ 
    self.icharg = ICharg()
    """ Charge from which to start. 
    
        It is best to keep this attribute set to -1, in which case, LaDa takes
        care of copying the relevant files.
    
          - -1: Automatically determined by LaDA. Depends on the value of
                restart_ and the existence of the relevant files. Also takes
                care of non-scf bit.
    
          - 0: Tries to restart from wavefunctions. Uses the latest WAVECAR
               file between the one currently in the output directory and the
               one in the restart directory (if specified). Sets nonscf_ to
               False.
    
               .. note:: CHGCAR is also copied, just in case.
    
          - 1: Tries to restart from wavefunctions. Uses the latest WAVECAR
               file between the one currently in the output directory and the
               one in the restart directory (if specified). Sets nonscf_ to
               False.
    
          - 2: Superimposition of atomic charge densities. Sets nonscf_ to
               False.
    
          - 4: Reads potential from POT file (VASP-5.1 only). The POT file is
               deduced the same way as for CHGAR and WAVECAR above.  Sets
               nonscf_ to False.
    
          - 10, 11, 12: Same as 0, 1, 2 above, but also sets nonscf_ to True.
               This is a shortcut. The value is actually kept to 0, 1, or 2:
    
               >>> vasp.icharg = 10
               >>> vasp.nonscf, vasp.icharg
               (True, 0)
    
        .. note::
        
           Files are copied right before the calculation takes place, not before.
    
        .. seealso:: ICHARG_
    
        .. _ICHARG: http://cms.mpi.univie.ac.at/wiki/index.php/ICHARG
        .. _restart: :py:attr:`~lada.vasp.functional.Functional.restart`
        .. _nonscf: :py:attr:`~lada.vasp.functional.Functional.nonscf`
    """ 
    self.istruc = IStruc()
    """ Initial structure. 
    
        Determines which structure is written to the POSCAR. In practice, it
        makes it possible to restart a crashed job from the latest contcar.
        There are two possible options:
  
          - auto: LaDa determines automatically what to use. If a CONTCAR
                  exists in either the current directory or in the restart
                  directory (if any), then uses the latest. Otherwise, uses
                  input structure.
          - scratch: Always uses input structure.
  
        If the run was given the ``overwrite`` option, then always uses the
        input structure.

        .. note:: There is no VASP equivalent to this option.
    """
    self.ldau = LDAU()
    """ Sets U, nlep, and enlep parameters. 
   
        The U, nlep, and enlep parameters of the atomic species are set at the
        same time as the pseudo-potentials. This object merely sets up the incar
        with right input.
    
        However, it does accept one parameter, which can be "off", "on", "occ" or
        "all", and defines the level of verbosity of VASP (with respect to U and nlep).
    
        .. seealso:: LDAU_, LDAUTYPE_, LDAUL_, LDAUJ_

        .. _LDAU: http://cms.mpi.univie.ac.at/wiki/index.php/LDAU
        .. _LDAUTYPE: http://cms.mpi.univie.ac.at/wiki/index.php/LDAUTYPE
        .. _LDAUL: http://cms.mpi.univie.ac.at/wiki/index.php/LDAUL
        .. _LDAUU: http://cms.mpi.univie.ac.at/wiki/index.php/LDAUU
        .. _LDAUJ: http://cms.mpi.univie.ac.at/wiki/index.php/LDAUJ
    """
    self.precfock = PrecFock()
    """ Sets up FFT grid in hartree-fock related routines.
        
        Allowable options are:
    
        - low
        - medium
        - fast
        - normal
        - accurate
    
        .. seealso:: PRECFOCK_
        
        .. _PRECFOCK: http://cms.mpi.univie.ac.at/wiki/index.php/PRECFOCK
    """
    self.precision = Precision()
    """ Sets accuracy of calculation. 
    
        - accurate (default)
        - low
        - medium
        - high
        - single
    
        .. seealso:: PREC_
        
        .. _PREC: http://cms.mpi.univie.ac.at/wiki/index.php/PREC
    """
    self.nsw = Nsw()
    """ Maxium number of ionic iterations. 

        .. seealso:: NSW_

        .. _NSW: http://cms.mpi.univie.ac.at/wiki/index.php/NSW
    """
    self.ibrion = IBrion()
    """ Ions/cell-shape/volume optimization method.
    
        Can only take a restricted set of values: -1 | 0 | 1 | 2 | 3 | 5 | 6 | 7 | 8 | 44.

        .. seealso:: IBRION_

        .. _IBRION: cms.mpi.univie.ac.at/wiki/index.php/IBRIONN
    """
    self.isif = Isif()
    """ Degree of librerty to optimize during geometry optimization

        .. seealso:: ISIF_

        .. _ISIF: http://cms.mpi.univie.ac.at/vasp/guide/node112.html
    """
    self.relaxation = Relaxation()
    """ Short-cut for setting up relaxation. 

        It accepts two parameters:
        
          - static: for calculation without geometric relaxation.
          - combination of ionic, volume, cellshape: for the type of relaxation
            requested.

        It makes sure that isif_, ibrion_, and nsw_ take the right value for the
        kind of relaxation.
    """
    self.ismear = ISmear()
    """ Smearing function 

        Vasp allows a number of options:

        - metal (-5): Tetrahedron method with Blöchl correction (requires a
          |Gamma|-centered *k*-mesh)
        - tetra (-4): Tetrahedron method (requires a |Gamma|-centered *k*-mesh)
        - dynamic (-3): Performs a loop over smearing parameters supplied in
          :py:attr:`~lada.vasp.functional.smearings`
        - fixed: (-2): Fixed occupation, set *via* FERWE and FERDO
        - fermi (-1): Fermi function
        - gaussian (0): Gaussian function
        - mp n (n>0): Methfessel-Paxton smearing function of order n

        .. |Gamma|  unicode:: U+00393 .. GREEK CAPITAL LETTER GAMMA
    """
    self.isigma = Sigma()
    self.smearings = TypedKeyword(type=[float])
    self.ferwe = TypedKeyword(type=[float])
    self.ferdo = TypedKeyword(type=[float])
    self.lsorbit = LSorbit()
    """ Run calculation with spin-orbit coupling. 
    
        Accepts None, True, or False.
        If True, then sets :py:attr:`~lada.vasp.incar.Incar.nonscf` to True and
        :py:attr:`~lada.vasp.incar.Incar.ispin` to 2.
    """ 
    
    # copies values from other functional.
    if copy is not None: 
      self._input.update(copy._input)
      for key, value in copy.__dict__.iteritems():
        if key in kwargs: continue
        elif key == '_input': continue
        elif hasattr(self, key): setattr(self, key, value)


    # sets all known keywords as attributes.
    for key, value in kwargs.iteritems():
      if hasattr(self, key): setattr(self, key, value)

  def __call__( self, structure, outdir=None, comm=None, overwrite=False, 
                **kwargs):
    """ Calls vasp program. """
    result = None
    for program in self.iter(structure, outdir=outdir, comm=comm, overwrite=overwrite, **kwargs):
      # iterator may yield the result from a prior successful run. 
      if getattr(program, 'success', False):
        result = program
        continue
      # otherwise, it should yield a Program tuple to execute.
      program.start(comm)
      program.wait()
    # Last yield should be an extraction object.
    if not result.success:
      raise RuntimeError("Vasp failed to execute correctly.")
    return result

  @assign_attributes(ignore=['overwrite', 'comm'])
  @stateless
  def iter(self, structure, outdir=None, comm=None, overwrite=False, **kwargs):
    """ Performs a vasp calculation 
     
        If successful results (see :py:attr:`extract.Extract.success`) already
        exist in outdir, calculations are not repeated. Instead, an extraction
        object for the stored results are given.

        :param structure:  
            :py:class:`~lada.crystal.Structure` structure to compute, *unless*
            a CONTCAR already exists in ``outdir``, in which case this
            parameter is ignored. (This feature can be disabled with the
            keyword/attribute ``restart_from_contcar=False``).
        :param outdir:
            Output directory where the results should be stored.  This
            directory will be checked for restart status, eg whether
            calculations already exist. If None, then results are stored in
            current working directory.
        :param comm:
            Holds arguments for executing VASP externally.
        :param overwrite:
            If True, will overwrite pre-existing results. 
            If False, will check whether a successful calculation exists. If
            one does, then does not execute. 
        :param kwargs:
            Any attribute of the VASP instance can be overridden for
            the duration of this call by passing it as keyword argument.  

        :return: Yields an extractor object if a prior successful run exists.
                 Otherwise, yields a tuple object for executing an external
                 program.

        :note: This functor is stateless as long as self and structure can be
               deepcopied correctly.  

        :raise RuntimeError: when computations do not complete.
        :raise IOError: when outdir exists but is not a directory.
    """ 
    from os.path import exists, join
    from numpy import abs
    from numpy.linalg import det
    from ..crystal import specieset
    from ..crystal import read
    from .files import CONTCAR
    from .. import vasp_program
    from ..process.program import ProgramProcess

    # check for pre-existing and successful run.
    if not overwrite:
      extract = self.Extract(outdir)
      if extract.success:
        yield extract # in which case, returns extraction object.
        return
    
    # makes functor stateless/reads structure from CONTCAR if requested and appropriate.
    if kwargs.pop("restart_from_contcar", self.restart_from_contcar): 
      path = join(outdir, CONTCAR)
      if exists(path):
        try: contstruct = read.poscar(path, list(specieset(structure)))
        except: pass
        else:
          # copies poscar info to structure.
          # this function should be stateless at this point, so it does not
          # matter that we change structure.
          for a, b in zip(structure, contstruct):
            a.pos, a.type = b.pos, b.type
          structure.cell = contstruct.cell
          structure.scale = contstruct.scale
    if len(structure) == 0: raise ValueError("Structure is empty.")
    if abs(det(structure.cell)) < 1e-8: raise ValueError("Structure with zero volume.")
    if abs(structure.scale) < 1e-8: raise ValueError("Structure with null scale.")

    # copies/creates file environment for calculation.
    self.bringup(structure, outdir, comm)
    # figures out what program to call.
    program = self.program if self.program is not None else vasp_program
    if hasattr(program, '__call__'): program = program(self)
    # creates a process with a callback to bring-down environment once it is
    # done.
    def onfinish(process, error):  self.bringdown(outdir, structure)
    yield ProgramProcess( program, cmdline=[], outdir=outdir,
                          onfinish=onfinish, stdout='stdout', stderr='stderr',
                          dompi=True )
    # yields final extraction object.
    yield Extract(outdir)

  def bringup(self, structure, outdir, comm):
    """ Creates all input files necessary to run results.

        Performs the following actions.

        - Writes POSCAR file.
        - Writes INCAR file.
        - Writes KPOINTS file.
        - Creates POTCAR file
        - Saves pickle of self.
    """
    import cPickle
    from ..crystal import specieset
    from ..misc.changedir import Changedir
    from . import files

    with Changedir(outdir) as tmpdir:
      # creates INCAR file. Note that POSCAR file might be overwritten here by Restart.
      self.write_incar(structure, comm=comm)
  
      # creates kpoints file
      with open(files.KPOINTS, "w") as kp_file: 
        self.write_kpoints(kp_file, structure)
  
      # creates POTCAR file
      with open(files.POTCAR, 'w') as potcar:
        for s in specieset(structure):
          potcar.writelines( self.species[s].read_potcar() )
    
      with open(files.FUNCCAR, 'w') as file:
        cPickle.dump(self, file)
    

  def bringdown(self, directory, structure):
     """ Copies contcar to outcar. """
     from . import files
     from ..misc import Changedir

     # Appends INCAR and CONTCAR to OUTCAR:
     with Changedir(directory) as pwd:
       with open(files.OUTCAR, 'a') as outcar:
         outcar.write('\n################ CONTCAR ################\n')
         with open(files.CONTCAR, 'r') as contcar: outcar.write(contcar.read())
         outcar.write('\n################ END CONTCAR ################\n')
         outcar.write('\n################ INCAR ################\n')
         with open(files.INCAR, 'r') as incar: outcar.write(incar.read())
         outcar.write('\n################ END INCAR ################\n')
         outcar.write('\n################ INITIAL STRUCTURE ################\n')
         outcar.write("""from {0.__class__.__module__} import {0.__class__.__name__}\n"""\
                      """structure = {1}\n"""\
                      .format(structure, repr(structure).replace('\n', '\n            ')))
         outcar.write('\n################ END INITIAL STRUCTURE ################\n')
         outcar.write('\n################ FUNCTIONAL ################\n')
         outcar.write(repr(self))
         outcar.write('\n################ END FUNCTIONAL ################\n')


  def write_incar(self, structure, path=None, comm=None):
    """ Writes incar file. """
    from lada import default_comm
    from ..misc import RelativePath
    from .files import INCAR

    # check what type path is.
    # if not a file, opens one an does recurrent call.
    if path is None: path = INCAR
    if not hasattr(path, "write"):
      with open(RelativePath(path).path, "w") as file:
        self.write_incar(structure, path=file, comm=comm)
      return

    if comm is None: comm = default_comm
    map = self.input_map(structure=structure, vasp=self, comm=comm)
    length = max(len(u) for u in map)
    for key, value in map.iteritems():
      path.write('{0: >{length}} = {1}\n'.format(key, value, length=length))

  def write_kpoints(self, file, structure, kpoints=None):
    """ Writes kpoints to a stream. """
    if kpoints == None: kpoints = self.kpoints
    if isinstance(self.kpoints, str): file.write(self.kpoints)
    elif hasattr(self.kpoints, "__call__"):
      self.write_kpoints(file, structure, self.kpoints(self, structure))
    else: # numpy array or such.
      file.write("Explicit list of kpoints.\n{0}\nCartesian\n".format(len(self.kpoints)))
      for kpoint in self.kpoints:
        file.write("{0[0]} {0[1]} {0[2]} {1}\n".format(kpoint, 1 if len(kpoint) == 3 else kpoint[3]))

  def __repr__(self, defaults=True, name=None):
    """ Returns representation of this instance """
    from ..functools.uirepr import uirepr
    defaults = self.__class__() if defaults else None
    return uirepr(self, name=name, defaults=defaults)

  def __ui_repr__(self, imports, name=None, defaults=None, exclude=None):
    from ..functools.uirepr import template_ui_repr

    results = template_ui_repr(self, imports, name, defaults, ['add_specie'])
    if name is None:
      name = getattr(self, '__ui_name__', self.__class__.__name__.lower())
    return results

  @add_setter
  def add_specie(self, args):
    """ Adds a specie to current functional. 
     
        The argument is a tuple containing the following.

        - Symbol (str).
        - Directory where POTCAR resides (str).
        - List of U parameters (optional, see module vasp.specie).
        - Maximum (or minimum) oxidation state (optional, int).
        - ... Any other argument in order of `vasp.specie.Specie.__init__`.
    """
    from .specie import Specie
    assert len(args) > 1, ValueError("Too few arguments.")
    self.species[args[0]] = Specie(*args[1:])
    
  def __setstate__(self, args):
    """ Sets state from pickle.

        Takes care of older pickle versions.
    """
    super(Vasp, self).__setstate__(args)
    for key, value in self.__class__().__dict__.iteritems():
       if not hasattr(self, key): setattr(self, key, value)
