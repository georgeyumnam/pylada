import pickle
import matplotlib.pyplot as plt 
from lada.escan import ExtractBS

def compute_projections(extract, filename, alpha = 1e0, **kwargs):
  """ Computes projected densities around each atom for a calculation. """
  from os.path import exists
  from sys import exit, getrefcount
  if exists(filename): 
    from pickle import load
    with open(filename, "r") as file: return load(file)

  from pickle import dump
  from numpy import zeros, dot, array, exp, sum
  from numpy.linalg import norm
  from lada import periodic_table as table
  from lada.crystal import gaussian_projector
  species = set([u.type for u in extract.structure.atoms])
  species = sorted(list(species))
  result = {}
  for key in species:
    if (key not in kwargs) and (key not in table.__dict__): continue
    radius = kwargs.get(key, getattr(table, key)).atomic_radius
    sigma = -alpha / radius / radius

    # create projection operator.
    proj = zeros(extract.rvectors.shape[:-1])
    cell = extract.structure.cell
    for atom in extract.structure.atoms:
      if atom.type != key: continue
      proj += gaussian_projector(extract.rvectors, atom.pos, cell, sigma )
    proj /= sum(proj) 

    result[key] = [(w.eigenvalue, w.expectation_value(proj)) for w in extract.rwfns]
  
  n = norm(array(result.values()))
  for key in result.keys(): result[key] /= n
  with open(filename, "w") as file: dump(result, file)
  return result

def compute_bs():
  import pickle
  from sys import exit
  from os.path import join
  from numpy import matrix, array
  from numpy.linalg import norm
  from boost.mpi import world
  from lada.opt import read_input
  from lada.escan import Escan, soH, band_structure
  from lada.vff import Vff
  from lada.crystal import fill_structure, sort_layers, FreezeCell, nb_valence_states  

  # reads input file.
  global_dict={"Vff": Vff, "Escan": Escan, "nb_valence_states": nb_valence_states, "soH": soH}
  input = read_input("input.py", global_dict=global_dict)

  # creating unrelaxed structure.
  structure = input.vff.lattice.to_structure()
  structure.atoms[0].type = "Si"
  structure.atoms[1].type = "Ge"
  structure.scale = 5.65

  # some kpoints + associated name
  X = array( [1,0,0], dtype="float64" )
  G = array( [0,0,0], dtype="float64" )
  L = array( [0.5,0.5,0.5], dtype="float64" )
  W = array( [0, 0.5,1], dtype="float64" )

  # Each job is performed for a given kpoint (first argument), at a given
  # reference energy (third argument). Results are stored in a specific directory
  # (second arguement). The expected eigenvalues are given in the fourth argument.
  kpoints = [ (X, G), (G, L) ]
  density = 20 / min( norm(X), norm(L), norm(W) )

  result = band_structure( input.escan, structure, kpoints, density, 
                           outdir = "results",
                           eref   = None, 
                           nbstates = nb_valence_states(structure) + 4,
                           pools = 4)
    
  if world.rank == 0:
    with open(join("results", "pickle"), "w") as file:
      pickle.dump(result, file) 


from lada.escan import ExtractBS
from os.path import join
compute_bs()
extract_bs = ExtractBS("results")
for key, value in extract_bs.iteritems():
  filename = join(value.directory, "PROJECT_BS")
  print key
  a = compute_projections(value, filename)
