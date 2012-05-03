""" A GA subpackage defining standard genetic operator for bitstrings. """
__docformat__ = "restructuredtext en"

class Individual(object):
  """ An individual for bitstrings.

      The size of the individual is given statically by Individual.size.
      :attention: This class does handle mpi at all. Created instances will
        differ from one process to the next.
  """

  size = 10

  def __init__(self, size = None):
    """ Initializes a bitstring individual randomly. 

      :attention: This class does handle mpi at all. Created instances will
        differ from one process to the next.
    """
    from random import randint
    from numpy import array

    super(Individual, self).__init__()
    if size is None: size = self.size
    self.genes = array([ randint(0,1) for i in xrange(size) ])
  
  def __eq__(self, a): 
    from math import fabs
    if a is None: return False
    for i, u in enumerate(a.genes):
      if fabs( self.genes[i] - u ) > 1e-18: return False
    return True

  def __str__(self): return repr(self.genes)

def roll(indiv, layers=1, invert=True):
  """ Rolls superlattices around. """
  from random import randint, choice
  from numpy import roll
  N = len(indiv.genes)
  if N % layers != 0:
    raise ValueError('Number of layers and genes are incompatible')
  n = randint(0, N//layers) * layers
  if n != 0: indiv.genes = roll(indiv.genes.copy(), n)
  if invert and choice([True, False]): 
    indiv.genes[:] = indiv.genes.copy()[::-1]
  return indiv


class VariableSizeCrossover(object):
  """ A crossover operation. """

  def __init__(self, nmin=-1, nmax=-1, step=2, roll=None):
    """ Initializes crossover. 

        :Parameter:
          nmin : int
            Minimum size of  a bitstring. Only used if two bitstrings differ in
            size.
          nmin : int
            Minimum size of  a bitstring. Only used if two bitstrings differ in
            size.
          role : tuple
            Parameters for roll. No rick-rolling if None.
    """
    self.nmin = nmin
    """ Minimum bitstring size. """
    self.nmax = nmax
    """ Maximum bitstring size. """
    self.roll = () if roll == True else roll
    """ Roll bitstring. """

  def __call__(self, first, second):
    """ Create new individual from ``first`` and ``second`` using bitstring crossover. 
    
        :Parameter:
          first 
            First parent individual.
          second 
            This is the other parent individual.

        :return: An offspring individual.
    """
    from copy import deepcopy
    from random import randint
    from numpy import array

    if self.roll is not None: 
      first = roll(deepcopy(first), *self.roll)
      second = roll(deepcopy(second), *self.roll)
       
    a = [u for u in first.genes]
    b = [u for u in second.genes]
    if len(a) <= 1 : return deepcopy(second)
    if len(b) <= 1 : return deepcopy(first) 
    if len(a) <= 3 and len(b) <= 3: a = a[:1] + b[1:]
    elif len(a) <= 3: a += b[3:]
    elif len(b) <= 3: a = b + a[3:]
    else:
      i = randint(1, min(len(a), len(b))-2)
      j = randint(i+1, min(len(a), len(b)))
      a = a[:i] + b[i:j] + a[j:]
    result = deepcopy(first)
    result.genes  = array(a)
    assert len(result.genes) >= self.nmin 
    assert len(result.genes) <= self.nmax
    if hasattr(result, "fitness"): delattr(result, "fitness")

    return result
  
  def __repr__(self):
    return "{0.__class__.__name__}({0.nmin!r}, {0.nmax!r}, {0.roll!r})".format(self)

class Crossover(object):
  """ A crossover operation. """

  def __init__(self, rate = 0.5, roll=None):
    self.rate = rate
    self.roll = () if roll == True else roll
    """ Roll bitstring. """

  def __call__(self, a, b):
    from random import uniform
    from copy import deepcopy
    
    assert len(a.genes) == len(b.genes), "Bitstring must be of equal lengths"
    if self.roll is not None:
      a, b = roll(deepcopy(a), *self.roll), roll(deepcopy(b), *self.roll)

    i = int( uniform(0, 1) * len(a.genes) )
    j = int( self.rate * len(a.genes) )
    if j >= len(a.genes): 
      a.genes[i:] = b.genes[i:] 
      a.genes[:j-len(a.genes)] = b.genes[:j-len(a.genes)]
    else: a.genes[i:j] = b.genes[i:j]

    if hasattr(a, "fitness"): delattr(a, "fitness")
    return a

  def __repr__(self):
    return "{0.__class__.__name__}({0.rate!r}, {0.roll!r})".format(self)

class Mutation(object):
  """ A mutation operation. """

  def __init__(self, rate = 0.10, roll=None):
    """ Initializes mutation operation. 

        :Parameters:
          rate : float
            Mutation rate for each bit in the bitstring.
          role : tuple
            Parameters for roll. No rick-rolling if None.
    """
    self.rate = rate
    """ Mutation rate for each bitstring. """
    self.roll = () if roll == True else roll
    """ Roll bitstring. """

  def __call__(self, indiv):
    """ Returns invidual with mutated genes. """
    from random import uniform
    from copy import deepcopy
    if self.roll is not None: indiv = roll(deepcopy(indiv), *self.roll)
    
    if len(indiv.genes) == 0: return indiv
    rate = self.rate if self.rate >= 0e0 else -float(self.rate)/float(len(indiv.genes))
    for i in xrange(len(indiv.genes)):
      if uniform(0, 1)  < rate:
        indiv.genes[i] = 0 if indiv.genes[i] == 1 else 1 
    if hasattr(indiv, "fitness"): delattr(indiv, "fitness")
    return indiv

  def __repr__(self):
    return "{0.__class__.__name__}({0.rate!r}, {0.roll!r})".format(self)
SwapMutation = Mutation
""" Fixed-size bitstring mutation operation. """


class GrowthMutation(object):
  """ Mutation which inserts a bit in the bitstring. """
  def __init__(self, nmin = -1, nmax = -1, step=1, roll=None):
    """ Initiatizes the bit insertion.

        :Parameters:
          nmax : integer
            Maximum size of a bistring. If nmax = -1, there are no limits to the
            size of a bitstring.
          nmin : integer
            Minimum size of a bistring. If nmin = -1, there are no limits to the
            size of a bitstring.
          role : tuple
            Parameters for roll. No rick-rolling if None.
    """
    self.nmax = nmax
    """ Maximum bistring size. """ 
    self.nmin = nmin
    """ Minimum bistring size. """ 
    # Cannot  have nmin == nmax since the operation would be meaningless.
    assert self.nmin < self.nmax or self.nmin == -1 or self.nmax == -1,\
           ValueError("nmin and nmax are incorrect.")
    self.step = step
    """ By how much to grow or shrink. """
    self.roll = () if roll == True else roll
    """ Roll bitstring. """

  def __call__(self, indiv):
    """ Inserts extra bit in bitstring. """
    from copy import deepcopy
    from numpy import array
    from random import randint

    if self.roll is not None: indiv = roll(deepcopy(indiv), *self.roll)
    step = getattr(self, 'step', 1)
    l = [u for u in indiv.genes]
    if randint(0,1) == 0 and\
       ( (self.nmin == -1 and len(l) > step - 1) or \
         (self.nmin != -1 and len(l) > step - 1 + self.nmin) ):
      nmin = self.nmin if self.nmin != -1 else 0
      i = randint(nmin, len(l)-step)
      for j in xrange(step): l.pop(i)
    elif self.nmax == -1 or (len(l) <= self.nmax - step): 
      i = randint(0, len(l))
      j = randint(0, 1)
      for i in xrange(self.step): l.insert(i, j)
    indiv.genes = array(l)
    assert len(indiv.genes) >= self.nmin or self.nmin == -1
    assert len(indiv.genes) <= self.nmax or self.nmax == -1
     
    if hasattr(indiv, "fitness"): delattr(indiv, "fitness")
    return indiv

  def __repr__(self):
    return "{0.__class__.__name__}({0.nmin!r}, {0.nmax!r}, {0.roll!r})".format(self)
