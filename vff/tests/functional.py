def functional():
  from lada.vff.functional import Functional
  vff = Functional()
  vff["In", "As"] = 2.62332, 21.6739, -112.0, 150.0
  vff["Ga", "As"] = 2.44795, 32.1530, -105.0, 150.0
  vff["As", "Ga", "As"] = "tet", -4.099, 9.3703
  vff["Ga", "As", "Ga"] = "tet", -4.099, 9.3703
  vff["In", "As", "In"] = "tet", -5.753, 5.7599
  vff["As", "In", "As"] = "tet", -5.753, 5.7599
  vff["Ga", "As", "In"] = -0.35016, -4.926, 7.5651

  return vff

def test_inas(epsilon = 1e-4):
  from tempfile import mkdtemp
  from shutil import rmtree
  from os.path import exists
  from numpy import abs, dot, array, sqrt, all, abs, identity
  from numpy.linalg import inv
  from lada.crystal.binary import zinc_blende
  from quantities import a0, angstrom
  from lada.misc import Changedir


  vff = functional()

  directory = '/tmp/test' # mkdtemp()
  if directory == '/tmp/test':
    if exists(directory): rmtree(directory)
    with Changedir(directory) as cwd: pass
  try: 
    structure = zinc_blende()
    structure[0].type = 'In'
    structure[1].type = 'As'
    structure.scale = 2.62332 * 4 / sqrt(3)  * angstrom
    out = vff(structure, outdir=directory, tol=1e-9, overwrite=True)
    startdate = out.start_date
    enddate   = out.end_date
    assert out.success
    assert all(abs(out.structure.cell - structure.cell) < 1e-8)
    assert all(abs(out.structure[0].pos - structure[0].pos) < 1e-8)
    assert all(abs(out.structure[1].pos - structure[1].pos) < 1e-8)
    out = vff(structure, outdir=directory, tol=1e-9, overwrite=False)
    assert out.start_date == startdate
    assert out.end_date == enddate
    assert startdate != enddate
    out = vff(structure, outdir=directory, tol=1e-9, overwrite=True)
    assert out.start_date != startdate

  # diff = structure.copy()
  # epsilon = identity(3, dtype='float64')                                     \
  #           + [[0.02, 0.03, -0.1], [0.03, -0.05, -0.05], [-0.1, -0.05, 0.06]]
  # epsilon = identity(3, dtype='float64') * 1.1
  # diff.cell = dot(epsilon, diff.cell)
  # for atom in diff: atom.pos = dot(epsilon, atom.pos)
  # newout = vff(diff, outdir=directory, tol=1e-10, overwrite=True)
  # assert all(abs(newout.structure.cell - structure.cell) < 1e-8)
  # assert all(abs(newout.structure[0].pos - structure[0].pos) < 1e-8)
  # assert all(abs(newout.structure[1].pos - structure[1].pos) < 1e-8)
  # assert abs(newout.structure.energy) < 1e-8

  # diff = structure.copy()
  # epsilon = identity(3, dtype='float64')                                     \
  #           + [[0.02, 0, 0], [0, -0.05, 0], [0, 0, 0.06]]
  # diff.cell = dot(epsilon, diff.cell)
  # for atom in diff: atom.pos = dot(epsilon, atom.pos)
  # newout = vff(diff, outdir=directory, tol=1e-10, overwrite=True)
  # assert all(abs(newout.structure.cell - structure.cell) < 1e-8)
  # assert all(abs(newout.structure[0].pos - structure[0].pos) < 1e-8)
  # assert all(abs(newout.structure[1].pos - structure[1].pos) < 1e-8)
  # assert abs(newout.structure.energy) < 1e-8

  # diff = structure.copy()
  # epsilon = identity(3, dtype='float64')                                     \
  #           + [[0.02, 0.05, 0], [0.05, -0.05, 0], [0, 0, 0.06]]
  # diff.cell = dot(epsilon, diff.cell)
  # for atom in diff: atom.pos = dot(epsilon, atom.pos)
  # newout = vff(diff, outdir=directory, tol=1e-10, overwrite=True)
  # assert all(abs(newout.structure.cell - structure.cell) < 1e-8)
  # assert all(abs(newout.structure[0].pos - structure[0].pos) < 1e-8)
  # assert all(abs(newout.structure[1].pos - structure[1].pos) < 1e-8)
  # assert abs(newout.structure.energy) < 1e-8

    diff = structure.copy()
#   epsilon = identity(3, dtype='float64')                                     \
#             + [[0.02, 0.05, 0], [0.05, -0.05, 0], [0, 0, 0.06]]
#   diff.cell = dot(epsilon, diff.cell)
#   for atom in diff: atom.pos = dot(epsilon, atom.pos)
    diff[1].pos += [0.01, -0.005, 0.03]
    newout = vff(diff, outdir=directory, tol=1e-10, overwrite=True)
    print newout.energy
    print newout.structure
    print newout.optimize
#   assert all(abs(newout.structure.cell - structure.cell) < 1e-8)
    assert all(abs(newout.structure[1].pos - structure[0].pos - [0.25, 0.25, 0.25]) < 1e-8)
#   assert all(abs(newout.structure[1].pos - structure[1].pos) < 1e-8)
    assert abs(newout.structure.energy) < 1e-8
  finally:
    if directory != '/tmp/test': rmtree(directory)
    
      
if __name__ == '__main__':
  test_inas(1e-9)
