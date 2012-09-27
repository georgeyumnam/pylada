__docformat__ = "restructuredtext en"
__all__ = ['Electronic']
from .input import AttrBlock, BoolKeyword
from ..tools.input import TypedKeyword, BaseKeyword
from quantities import UnitQuantity, hartree

class Shrink(BaseKeyword):
  """ Implements SHRINK parameter. """
  keyword = 'shrink'
  """ Crystal keyword. """
  def __init__(self, mp=1, gallat=None):
    """ Initializes Shrink keyword. 

        :param mp: 
           - if an integer, corresponds to IS variable of SHRINK.
           - if a sequence of at most three integers, corresponds to IS1, IS2,
             IS3. In that case, IS is of course set to 0. If there are only one
             or two numbers, then IS2 and/or IS3 is set to one. If None, the
             set to 1.
        :param int gallat:
           Corresponds to ISP variable of SHRINK. If None, then it is set equal
           to IS1
    """
    super(Shrink, self).__init__()
    self.mp = mp
    self.gallat = gallat
  @property
  def mp(self):
    """ Defines the Monkhorst-Pack mesh. """
    return self._mp
  @mp.setter
  def mp(self, value):
    if value is None: self._mp = 1
    elif hasattr(value, '__iter__'):
      mp = [max(int(u), 1) for u in value]
      if len(mp) > 3:
        raise ValueError('k-point mesh defined by at most three integers.')
      elif len(mp) == 0: mp = 1
      self._mp = mp
    else: self._mp = max(int(value), 1)
  @property
  def gallat(self): 
    """ Defines Gallat mesh for density matrix and Fermi energy. """
    return self._gallat
  @gallat.setter
  def gallat(self, value): 
    self._gallat = None if value is None else int(value)

  @property
  def raw(self):
    """ Prints raw CRYSTAL input. """
    if hasattr(self.mp, '__iter__'):
      ISP = self.mp[0] if self.gallat is None else self.gallat
      IS = ' '.join(str(u) for u in self.mp + [1]*(3-len(self.mp)))
      return '0 {0}\n{1}\n'.format(ISP, IS)
    else:
      ISP = self.mp if self.gallat is None else self.gallat
      return '{0} {1}\n'.format(self.mp, ISP)
  @raw.setter
  def raw(self, value):
    """ Sets from raw CRYSTAL input. """
    value = value.split()
    IS, ISP = int(value[0]), int(value[1])
    if IS == 0:
      self.mp = [int(u) for u in value[2:5]]
      if self.mp[-1] == 1: self.mp = self.mp[:-1]
      if self.mp[-1] == 1: self.mp = self.mp[:-1]
      if self.mp[-1] == 1: 
        self.mp = 1
        self.gallat = None if ISP == self.mp else ISP
      else: self.gallat = None if ISP == self.mp[0] else ISP
    else: 
      self.mp = IS
      self.gallat = None if ISP == self.mp else ISP

  def __set__(self, instance, value):
    """ Sets the keyword more easily. """
    if value is None: self.mp = None; return
    self.mp = value[0]
    self.gallat = value[1]

  def __repr__(self):
    """ Representation of this instance. """
    args = []
    if self.mp == 1:
      if self.gallat is not None:
        args.append('gallat={0.gallat!r}'.format(self))
    else:
      args.append(repr(self.mp))
      if self.gallat is not None: args.append('{0.gallat!r}'.format(self))
    return '{0.__class__.__name__}({1})'.format(self, ', '.join(args))

  def __ui_repr__(self, imports, name=None, defaults=None, exclude=None):
    """ Creates user friendly representation. """
    from ..tools.uirepr import add_to_imports
    if defaults is not None: 
      if type(defaults) is not type(self): 
        add_to_imports(self, imports)
        return {name: repr(self)}
      if self.gallat == defaults.gallat and self.mp == defaults.mp: 
        return {}
      return {name: '{0.mp!r}, {0.gallat!r}'.format(self)}
    elif name is None:
      add_to_imports(self, imports)
      return {None: 'shrink = {0!r}'.format(self)}
    add_to_imports(self, imports)
    return {name: self.__repr__()}

  def output_map(self, **kwargs):
    """ Prints SHRINK keyword """
    from .molecule import Molecule
    # The 'get' piece is to make testing a bit easier
    if type(kwargs.get('structure', None)) is Molecule: return None
    return super(Shrink, self).output_map(**kwargs)

def _get_list(name): 
  """ Creates getter method for AtomSpin. """
  def getme(this): return getattr(this, '_' + name)
  return getme
def _set_list(name): 
  """ Creates setter method for AtomSpin. """
  def setme(this, value): 
    from collections import Sequence, Iterable
    from ..error import TypeError
    if value is not None: 
      if not isinstance(value, Sequence):
        raise TypeError( 'Expected a sequence when setting {0} in AtomSpin.'   \
                         .format(name) )
      if not isinstance(value, Iterable):
        raise TypeError( 'Expected an iterable when setting {0} in AtomSpin.'  \
                         .format(name) )
      for v in value: 
        try: int(v)
        except:
          raise TypeError( 'Wrong type in list when setting AtomSpin.{0}.'     \
                           'The list should be all integers.'.format(name) )
    setattr(this, '_' + name, value)
  return setme

class AtomSpin(BaseKeyword):
  keyword = 'atomspin' 
  def __init__(self, up=None, down=None, other=None):
    """ Creates AtomSpin instance """
    super(AtomSpin, self).__init__()
    self.up = up
    self.down = down
    self.other = other
  def __getitem__(self, index):
    from ..error import IndexError
    if index in [1, 'up', 'alpha']: return self.up
    elif index in [-1, 'down', 'beta']: return self.down
    elif index in [0, 'other', 'others', 'irrelevant']: return self.others
    raise IndexError('Unknown index to AtomSpin {0}.'.format(index))
  def __setitem__(self, index, value):
    from ..error import IndexError
    if index in [1, 'up', 'alpha']: self.up = value
    elif index in [-1, 'down', 'beta']: self.down = value
    elif index in [0, 'other', 'others', 'irrelevant']: self.others = value
    raise IndexError('Unknown index to AtomSpin {0}.'.format(index))

  
  up = property( _get_list('up'), _set_list('up'),
                 doc=""" Labels of atoms with spin up. """ )
  down = property( _get_list('down'), _set_list('down'),
                   doc=""" Labels of atoms with spin down. """ )
  other = property( _get_list('other'), _set_list('other'),
                    doc = """ Labels of atoms with irrelevant atoms. 
                  
                        'Irrelevant' is the word used by the CRYSTAL_ userguide. It is likely not
                        necessary once one migrates away from bash-scripts.
                    """ )
                    
  def output_map(self, **kwargs):
    if self.up is None and self.down is None and self.other is None: return None
    if kwargs['crystal'].dft.spin is False: return None
    result = ''
    if self.up is not None and len(self.up) > 0:
      result += ' 1  '.join(str(u) for u in self.up) + ' 1\n'
    if self.down is not None and len(self.down) > 0:
      result += ' -1  '.join(str(u) for u in self.down) + ' -1\n'
    if self.other is not None and len(self.other) > 0:
      result += ' 0  '.join(str(u) for u in self.other) + ' 0\n'
    if len(result) == 0: return None
    return {self.keyword: '{0}\n{1}'.format(len(result.split())//2, result)}
  def read_input(self, value, owner=None, **kwargs):
    """ Reads input. """
    results = value.split()
    N = int(results.pop(0))
    self._up, self._down, self._other = [], [], []
    for label, spin in zip(results[:2*N:2], results[1:2*N:2]):
      if spin == '1': self.up.append(int(label))
      elif spin == '-1': self.down.append(int(label))
      elif spin == '0': self.other.append(int(label))
      else:
        raise ValueError( 'Unexpected value when reading AtomSpin data {0}.'   \
                          .format(value) )
    if len(self.up) == 0: self.up = None
    if len(self.down) == 0: self.down = None
    if len(self.other) == 0: self.other = None
  def __repr__(self):
    """ Representation of the this object. """
    args = []
    if self.up is not None: args.append(repr(self.up))
    if self.down is not None:
      if len(args) == 1: args.append(repr(self.down))
      else: args.append('down={0.down!r}'.format(self))
    if self.other is not None:
      if len(args) == 2: args.append(repr(self.other))
      else: args.append('other={0.other!r}'.format(self))
    return '{0.__class__.__name__}({1})'.format(self, ', '.join(args))

  def __ui_repr__(self, imports, name=None, defaults=None, exclude=None):
    """ Creates user friendly representation. """
    from ..tools.uirepr import add_to_imports

    if defaults is not None: 
      if type(defaults) is not type(self): 
        add_to_imports(self.up, imports)
        add_to_imports(self.down, imports)
        add_to_imports(self.other, imports)
        add_to_imports(self, imports)
        return {name: repr(self)}
      if self.up == defaults.up and self.down == defaults.down                 \
         and self.other == defaults.other: 
        return {}
      results = {}
      if self.up is not None:
        add_to_imports(self.up, imports)
        results[name + '.up'] = '{0.up!r}'.format(self)
      if self.down is not None:
        add_to_imports(self.down, imports)
        results[name + '.down'] = '{0.down!r}'.format(self)
      if self.other is not None:
        add_to_imports(self.other, imports)
        results[name + '.down'] = '{0.other!r}'.format(self)
      return results
    elif name is None:
      add_to_imports(self, imports)
      return {None: 'atomspin = {0!r}'.format(self)}
    add_to_imports(self, imports)
    return {name: self.__repr__()}

class SpinLock(BaseKeyword):
  """ Implements SpinLock keyword. """
  keyword = 'spinlock'
  """ CRYSTAL input keyword. """
  def __init__(self, nspin=None, ncycles=None):
    """ Creates the LEVSHIFT keyword. """
    super(SpinLock, self).__init__()
    self.nspin = nspin
    self.ncycles = ncycles
  @property
  def nspin(self): 
    return self._nspin
  @nspin.setter
  def nspin(self, nspin):
    self._nspin = int(nspin) if nspin is not None else None
  @property
  def ncycles(self): 
    """ Whether shift is kept after diagaonalization. """
    return self._ncycles
  @ncycles.setter
  def ncycles(self, ncycles):
    self._ncycles = int(ncycles) if ncycles is not None else None
  def __set__(self, instance, value):
    """ Sets the value of this instance. """
    from ..error import ValueError
    if value is None: self.nspin, self.ncycles = None, None; return
    if not hasattr(value, '__getitem__'): 
      raise ValueError('Incorrect input to spinlock: {0}.'.format(value))
    self.nspin = int(value[0])
    self.ncycles = value[1]
  def __getitem__(self, index):
    """ list [self.nspin, self.ncycles] """
    from ..error import IndexError
    if index == 0: return self.nspin
    elif index == 1 or index == -1: return self.ncycles
    raise IndexError('Levshift can be indexed with 0, 1, or -1 only.')
  def __setitem__(self, index, value):
    """ sets as list [self.nspin, self.ncycles] """
    from ..error import IndexError
    if index == 0: self.nspin = value
    elif index == 1 or index == -1: self.ncycles = value
    else: raise IndexError('Levshift can be indexed with 0, 1, or -1 only.')
  def __len__(self): return 2
  @property
  def raw(self):
    """ CRYSTAL input as a string """
    if self.nspin is None or self.ncycles is None: return ''
    return '{0} {1}'.format(self.nspin, self.ncycles)
  @raw.setter
  def raw(self, value):
    """ Sets instance from raw data """
    self.nspin = int(value.split()[0])
    self.ncycles = int(value.split()[1])
  def output_map(self, **kwargs):
    if self.nspin is None or self.ncycles is None: return None
    if kwargs['crystal'].dft.spin != True: return None
    return super(SpinLock, self).output_map(**kwargs)
  def __repr__(self):
    args = []
    if self.nspin is not None: args.append(str(self.nspin))
    if self.ncycles is not None:
      args.append( 'ncycles={0}'.format(self.ncycles) if len(args) == 0        \
                   else str(self.ncycles) )
    return '{0.__class__.__name__}({1})'.format(self, ', '.join(args))
  def __ui_repr__(self, imports, name=None, defaults=None, exclude=None):
    """ Creates user friendly representation. """
    from ..tools.uirepr import add_to_imports

    if defaults is not None: 
      if type(defaults) is not type(self): 
        add_to_imports(self.shift, imports)
        add_to_imports(self, imports)
        return {name: repr(self)}
      if self.nspin is None and self.ncycles is None: return {}
      results = {}
      if self.nspin is not None:
        add_to_imports(self.nspin, imports)
        results[name + '.nspin'] = '{0.nspin!r}'.format(self)
      if self.ncycles is not None:
        add_to_imports(self.ncycles, imports)
        results[name + '.ncycles'] = '{0.ncycles!r}'.format(self)
      return results
    elif name is None:
      add_to_imports(self, imports)
      return {None: 'levshift = {0!r}'.format(self)}
    add_to_imports(self, imports)
    return {name: self.__repr__()}
class BetaLock(SpinLock):
  keyword = 'betalock'
  

class LevShift(BaseKeyword):
  """ Implements LevShift keyword. """
  keyword = 'levshift'
  """ CRYSTAL input keyword. """
  units = UnitQuantity('decihartree', 0.1*hartree)
  """ LEVSHIFT takes 0.1 * hartrees. """
  def __init__(self, shift=None, lock=None):
    """ Creates the LEVSHIFT keyword. """
    super(LevShift, self).__init__()
    self.shift = shift
    self.lock = lock
  @property
  def shift(self): 
    """ Value to which this keyword is set. """
    return self._shift
  @shift.setter
  def shift(self, shift):
    """ Artificial shift between conduction and valence bands. 
  
        Can be a regular floating point, in which case the units are 0.1 *
        hartree, or a scalar signed by an unit with dimensionality of an energy.
        In the latter case, the value is rescaled to 0.1 H.
    """
    from ..error import ValueError
    if shift is None: self._shift = None; return
    if hasattr(shift, 'rescale'): shift = shift.rescale(self.units)
    else: shift = shift * self.units
    if len(shift.shape) != 0:
      raise ValueError('shift should be a scalar.')
    self._shift = shift
  @property
  def lock(self): 
    """ Whether shift is kept after diagaonalization. """
    return self._lock
  @lock.setter
  def lock(self, lock):
    self._lock = None if lock is None else (lock == True)
  def __set__(self, instance, value):
    """ Sets the value of this instance. """
    from ..error import ValueError
    if not hasattr(value, '__getitem__'): 
      raise ValueError('Incorrect input to levshift: {0}.'.format(value))
    self.shift = value[0]
    self.lock = value[1]
  def __getitem__(self, index):
    """ list [self.shift, self.lock] """
    from ..error import IndexError
    if index == 0: return self.shift
    elif index == 1 or index == -1: return self.lock
    raise IndexError('Levshift can be indexed with 0, 1, or -1 only.')
  def __setitem__(self, index, value):
    """ sets as list [self.shift, self.lock] """
    from ..error import IndexError
    if index == 0: self.shift = value
    elif index == 1 or index == -1: self.lock = value
    else: raise IndexError('Levshift can be indexed with 0, 1, or -1 only.')
  def __len__(self): return 2
  @property
  def raw(self):
    """ CRYSTAL input as a string """
    if self.shift is None or self.lock is None: return ''
    return '{0} {1}'.format(int(float(self.shift)+0.01), 1 if self.lock else 0)
  @raw.setter
  def raw(self, value):
    """ Sets instance from raw data """
    self.shift = int(value.split()[0])
    self.lock = int(value.split()[1]) != 0
  def output_map(self, **kwargs):
    if self.shift is None or self.lock is None: return None
    return super(LevShift, self).output_map(**kwargs)
  def __repr__(self):
    args = []
    if self.shift is not None: args.append(str(float(self.shift)))
    if self.lock is not None:
      args.append( 'lock={0}'.format(self.lock) if len(args) == 0              \
                   else str(self.lock) )
    return '{0.__class__.__name__}({1})'.format(self, ', '.join(args))

  def __ui_repr__(self, imports, name=None, defaults=None, exclude=None):
    """ Creates user friendly representation. """
    from ..tools.uirepr import add_to_imports

    if defaults is not None: 
      if type(defaults) is not type(self): 
        add_to_imports(self.shift, imports)
        add_to_imports(self, imports)
        return {name: repr(self)}
      if self.shift is None and self.lock is None: return {}
      results = {}
      if self.shift is not None:
        results[name + '.shift'] = '{0}'.format(float(self.shift))
      if self.lock is not None:
        add_to_imports(self.lock, imports)
        results[name + '.lock'] = '{0.lock!r}'.format(self)
      return results
    elif name is None:
      add_to_imports(self, imports)
      return {None: 'levshift = {0!r}'.format(self)}
    add_to_imports(self, imports)
    return {name: self.__repr__()}

class GuessP(BoolKeyword):
  """ Implements GuessP parameter. """
  keyword = 'guessp'
  def __init__(self, value=True):
    super(GuessP, self).__init__(value=value)
  def output_map(self, **kwargs):
    from os.path import exists, join
    from ..misc import copyfile
    if self.value is None or self.value == False: return None
    if kwargs['crystal'].restart is None: return None
    path = join(kwargs['crystal'].restart.directory, 'crystal.f9')
    if not exists(path): return None
    if kwargs.get('filework', False) == True:
      copyfile(path, join(kwargs['workdir'], 'fort.20'), nothrow='same')
    return super(GuessP, self).output_map(**kwargs)


class Electronic(AttrBlock):
  """ DFT attribute block. """ 
  __ui_name__ = 'electronics'
  """ Name used when printing this instance with ui_repr """
  def __init__(self):
    """ Creates the scf attribute block. """
    from ..tools.input import ChoiceKeyword, QuantityKeyword
    from .hamiltonian import Dft
    super(Electronic, self).__init__()
    self.maxcycle = TypedKeyword(type=int)
    """ Maximum number of electronic minimization steps.
    
        Should be None(default) or an integer. 
    """
    self.tolinteg = TypedKeyword(type=[int]*5)
    """ Integration truncation criteria.
    
        Should be None(default) or a sequence of 5 integers.
    """
    self.toldep   = TypedKeyword(type=int)
    """ Density matrix convergence criteria.
    
        Should be None(default) or an integer.
    """
    self.tolpseud = TypedKeyword(type=int)
    """ Pseudopotential truncation criteria.
    
        Should be None(default) or an integer.
    """
    self.toldee   = TypedKeyword(type=int)
    """ Total energy convergence criteria.
    
        Should be None(default) or an integer.
    """
    self.testpdim = BoolKeyword()
    """ Stop after processing input and performing symmetry analysis.
    
        Should be None(default), True, or False.
    """
    self.test     = BoolKeyword()
    """ Stop after printing ressource requirement.
    
        Should be None(default), True, or False.
    """
    self.symadapt = BoolKeyword()
    """ Symmetry adapted bloch wavefunctions.
    
        Should be None(default), True, or False.
    """
    self.savewf   = BoolKeyword()
    """ Save wavefunctions to disk.
    
        Should be None(default), True, or False.
    """
    self.shrink   = Shrink()
    """ k-point description -- SHRINK
    
        The IS (or IS1, IS2, IS3) and ISP keywords are mapped to
        :py:attr:`~Shrink.mp` and :py:attr:`~Shrink.gallat`. 
    
        They can be used as follows::
    
          functional.shrink.mp = 5
          functional.shrink.gallat = 10
    
        This will map IS to 5 and ISP to 10.
        ISP automatically set to equal IS (or IS1) when :py:attr:`~Shrink.gallat`
        is set to None::
    
          functional.shrink.mp = 10
          functional.shrink.gallat = None
    
        This will print in the CRYSTAL input:
    
          | SHRINK
          | 5 5
    
        Finally, setting :py:attr:`~Shrink.mp` to a sequence of at most three
        integers will set IS to 0 and IS1, IS2 (defaults to 1), and IS3 (defaults
        to 1) to the relevant values::
    
          functional.shrink.mp = [5, 6]
          functional.shrink.gallat = None
          
        This will lead to the following input, where ISP defaulted automatically
        to IS1:
    
          | SHRINK
          | 0 5
          | 5 6 1
    
    
        Another option it to set :py:attr:`~Shrink.mp` and
        :py:attr:`~Shrink.gallat` directly::
    
          functional.shrink = 8, 8
    
        would result in the following ouput
    
          | SHRINK
          | 8 8
    
        :py:attr:`~Shrink.mp` will be set to the first item. and
        :py:attr:`~Shrink.gallat` to the second. There should always be two
        items.
    """
    self.fmixing  = TypedKeyword(type=int)
    """ Fock mixing during electronic minimiztion.
    
        Should be None(default) or an integer.
    """
    self.levshift = LevShift()
    """ Artificial shift between the valence and conduction band.

        Opens the gap between occupied and unoccupied bands for better
        numerical behavior. It can be set as follows:

        >>> functional.levshift = 5 * decihartree, False
    
        The first parameter is the amount by which to open the gap. It should
        either an integer, or a signed energy quantity (see quantities_). In
        the latter case, the input is converted to decihartree and rounded to
        the nearest integer. 

        The second parameter specifies whether to keep (True) or remove (False)
        the shift after diagonalization.
    """
    self.ppan     = BoolKeyword()
    """ Mulliken population analysis.
    
        Should None(default), True, or False.
    """
    self.biposize = TypedKeyword(type=int)
    """ Size of buffer for Coulomb integrals bipolar expansions.
    
        Should be None(default), True, or False.
    """
    self.exchsize = TypedKeyword(type=int)
    """ Size of buffer for exchange integrals bipolar expansions.
    
        Should be None(default), True, or False.
    """
    self.scfdir   = BoolKeyword()
    """ Whether to reevaluate integrals at each electronic step.
    
        Should be None(default), True, or False.
    """
    self.poleordr = ChoiceKeyword(values=range(0, 7))
    """ Coulomb intergrals pole truncation.
    
        Should be None(default), or an integer between 0 and 6 included.
    """
    self.guessp   = GuessP(value=False)
    """ Reads density matrix from disk.
    
        - If True *and*
          :py:attr:`~lada.dftcrystal.functional.Functional.restart` is not
          None, then copies crystal.f9 to fort.20 in the working directory and
          adds GUESSP keyword to the input.
    
        - If True but :py:attr:`~lada.dftcrystal.functional.Functional.restart`
          is None or the file crystal.f9 does not exist, then does nothing.
          This is not an error, however.
    
        - If False or None, does nothing. Since GuessP can lead to bizarre
          problems, it is *False* by default.
    """ 
    self.dft      = Dft()
    """ Holds definition of the DFT functional itself. """
    self.nofmwf   = BoolKeyword()
    """ Whether to print formatted wavefunctions to disk.
    
        Should be None(default), True, or False.
    """
    self.nobipola = BoolKeyword()
    """ Whether to compute bielectronic integrals exactly.

        Should be None(default), True, or False.
    """
    self.nobipcou = BoolKeyword()
    """ Whether to compute bielectronic Coulomb integrals exactly.

        Should be None(default), True, or False.
    """
    self.nobipexc = BoolKeyword()
    """ Whether to compute bielectronic exchange integrals exactly.

        Should be None(default), True, or False.
    """
    self.nomondir = BoolKeyword()
    """ Whether store monoelectronic integrals to disk. 
    
        If True, the monoelctronic integrals are computed once at the start of
        the SCF calculation and re-read from disk at each geometric
        optimization step. Should be None(default), True, or False.
    """
    self.nosymada = BoolKeyword()
    """ Whether to not use symmetry adapted functions. 
    
        Should be None(default), True, or False.
    """
    self.savewf   = BoolKeyword()
    """ Whether to save wavefunctions at each step. 
    
        Should be None(default), True, or False.
    """
    self.mpp      = BoolKeyword(value=False)
    """ Whether to use MPP or Pcrystal when running mpi. 
    
        If True and more than one process is requested, switches to using
        MPPcrystal as opposed to Pcrystal.
        This only works under the assumption that
        :py:data:`lada.crystal_program` is implemented correctly.
    """
    self.spinlock = SpinLock()
    """ Difference in occupation between the two spin-channels. 
    
        This object takes two values, the difference between of occupations
        between the two spin channels, and the number of electronic
        minimization steps during which the lock is maintained.

        >>> functional.spinlock.nspin   = 2
        >>> functional.spinlock.ncycles = 30

        The above sets the :math:`\\alpha` and :math:`\\beta` occupations to
        :math:`\\frac{N+2}{2}` and  :math:`\\frac{N-2}{2}` respectively, for 30
        iterations of the electronic structure minimization algorithm. It
        results in the input:

          | SPINLOCK
          | 2 30

        Alternatively, the same could be done with the 2-tuple syntax:

        >>> functional.spinlock = 2, 30

        If either the occupation or the cycle-lock is None, then ``SPINLOCK`` is
        *disabled*.
    """
    self.atomspin = AtomSpin()
    """ Atomic spins.

        Defines the atomic spins.

        >>> functional.atomspin.up = range(5)*2 + 1 
        >>> functional.atomspin.down = range(5)*2 + 2

        For spin-polarized calculations, this would result in the CRYSTAL_
        input:

          | ATOMSPIN
          | 8
          | 2 1 4 1 6 1 8 1
          | 1 -1 3 -1 5 -1 7 -1

        There are two main variables, ``up`` and ``down``, which are lists of
        atomic labels. ``up`` contains the atoms which at the start of the
        calculation should have an up spin, and ``down`` those atoms with a
        down spin. A third variable, ``other``, corresponds to the
        ''irrelevant'' atoms, as per CRYSTAL_'s input.

        Alternatively, the ``up`` and ``down`` variables can be reached via indexing:

        >>> functional.atomspin[1] is functional.atomspin.up
        True
        >>> functional.atomspin[-1] is functional.atomspin.down
        True
        >>> functional.atomspin[0] is functional.atomspin.other
        True


        .. note::
        
          py:attr:`~lada.dftcrystal.functional.dft.spin` should be set to True
          for this parameter to take effect.
    """
    self.betalock = BetaLock()
    """ Locks in the number of beta electrons. 

        This tag presents the same user-interface as :py:attr:`spinlock`.
    """
    self.smear = QuantityKeyword(units=hartree)
    """ Smearing energy, if any.

        Expects None (default, does nothing) or an energy wich defines the
        width of the smearing function.
    """
  def output_map(self, **kwargs):
    """ Makes sure DFT subblock is first. """
    result = super(Electronic, self).output_map(**kwargs)
    for i, item in enumerate(result):
      if item[0] == 'DFT': break
    if result[i][0] == 'DFT': 
      dft = result.pop(i)
      result.insert(0, dft)
    return result
