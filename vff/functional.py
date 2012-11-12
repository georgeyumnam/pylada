from ..tools import stateless, assign_attributes
from .vff import Vff
from .extract import Extract as ExtractVFF

class Functional(Vff): 
  Extract = ExtractVFF
  """ Extraction object for Vff. """
  def __init__(self, relax=True, method='BFGS', tol=1e-8, maxiter=50): 
    super(Functional, self).__init__()

    self._parameters = {}
    """ Holds vff parameters. """
    self.relax = relax
    """ Whether to relax the structure """
    self.methods = method
    """ Type of method used to relax the structure. 
    
        .. see:: 
         
          `scipy.optimize.minimize`__'s method argument.
          
        .. __: http://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html
    """
    self.tol = tol
    """ Convergence criteria. """
    self.maxiter = maxiter
    """ Maximum number of iterations. """


  def _is_static(self, **kwargs):
    """ True if calculation is static. """
    relax = kwargs.get('relax', self.relax)
    if relax is False or relax is None: return True
    if not isinstance(relax, str): return False
    return relax.lower() == 'static'

  @stateless
  @assign_attributes(ignore=['overwrite', 'comm'])
  def __call__(self, structure, outdir=None, overwrite=False, **kwargs):
    """ Evaluates energy and forces on a structure. """
    from datetime import datetime
    from os.path import join
    from .extract import Extract as ExtractVFF

    if ExtractVFF(outdir).success and not overwrite: return ExtractVFF(outdir)

    header = ''.join(['#']*20)
    with open(join(outdir, 'vff.out'), 'w') as file:
      file.write('Start date: {0!s}\n'.format(datetime.today()))
      file.write('{0} {1} {0}\n'.format(header, 'INITIAL STRUCTURE'))
      file.write( 'from {0.__class__.__module__} '                             \
                  'import {0.__class__.__name__}\n'.format(structure) )
      string = repr(structure).replace('\n', '\n            ')
      file.write('structure = ' + string + '\n')
      file.write('{0} END {1} {0}\n'.format(header, 'INITIAL STRUCTURE'))
      file.write('{0} {1} {0}\n'.format(header, 'FUNCTIONAL'))
      file.write(self.__repr__(defaults=False) + '\n')
      file.write('{0} END {1} {0}\n\n'.format(header, 'FUNCTIONAL'))
    minimization, result = None, None
    try: 
      if self._is_static(**kwargs):
        result = super(Functional, self).__call__(structure)
      else: 
        result, minimization = self._relax_all(structure)
    finally: 
      with open(join(outdir, 'vff.out'), 'a') as file:
        if minimization is not None:
          file.write('{0} {1} {0}\n'.format(header, 'MINIMIZATION'))
          file.write(repr(minimization) + '\n')
          file.write('{0} END {1} {0}\n\n'.format(header, 'MINIMIZATION'))
        if result is not None:
          file.write('{0} {1} {0}\n'.format(header, 'STRUCTURE'))
          file.write( 'from {0.__class__.__module__} '                         \
                      'import {0.__class__.__name__}\n'.format(result) )
          string = repr(result).replace('\n', '\n            ')
          file.write('structure = ' + string + '\n')
          file.write('{0} END {1} {0}\n'.format(header, 'STRUCTURE'))
        file.write('End date: {0!s}\n'.format(datetime.today()))
    return ExtractVFF(outdir)


  def _relax_all(self, structure):
    from numpy import dot, array, zeros
    from numpy.linalg import inv, det
    from scipy.optimize import minimize
    from quantities import angstrom
    from . import build_tree

    structure = structure.copy()
    cell0 = structure.cell.copy()
    tree = build_tree(structure)
    invscale = 1e0 / float(structure.scale.rescale(angstrom))

    def xtostrain(x0):
      return array([[x0[0] + 1e0, x0[1], x0[2]],
                    [x0[1], 1e0 + x0[3], x0[4]],
                    [x0[2], x0[4], x0[5]+1e0]])
      
    def update_structure(x0, strain):
      structure.cell = dot(strain, cell0)
      for i, atom in enumerate(structure[1:]):
        atom.pos = dot(structure.cell, x0[i*3:3+i*3])

    def energy(x0):
      strain = xtostrain(x0)
      update_structure(x0[6:], strain)
      return self.energy(structure, _tree=tree).magnitude

    def jacobian(x0):
      strain = xtostrain(x0)
      update_structure(x0[6:], strain)

      stress, forces = self.jacobian(structure, _tree=tree)
      stress *= -det(structure.scale * structure.cell)

      stress = dot(stress, inv(strain))
      result = stress[0].tolist() + stress[1,1:].tolist() + [stress[2,2]]
      result += dot(inv(structure.cell)*invscale, forces[1:].T).T.flatten().tolist()
      return array(result)

    x = zeros(3+len(structure)*3, dtype='float64')
    x[:6] = 0e0
    frac = inv(structure.cell)
    for i, atom in enumerate(structure[1:]): x[6+3*i:9+3*i] = dot(frac, atom.pos)

    result = minimize( energy, jac=jacobian, x0=x, 
                       tol=self.tol, options={'maxiter': self.maxiter} )
    strain = xtostrain(result.x)
    update_structure(result.x[6:], strain)
    return super(Functional, self).__call__(structure), result

del stateless
del assign_attributes
del Vff
del ExtractVFF
