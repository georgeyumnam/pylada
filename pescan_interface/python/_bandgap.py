""" Submodule to compute bandgaps with escan. """
from ..opt.decorators import make_cached
from _extract import Extract as ExtractVasp

def band_gap(escan, structure, outdir=None, references=None, comm=None, n=5, **kwargs):
  """ Computes bandgap of a structure with a given escan functional. 
  
      The band-gap is computed using an all-electron method (if references=None
      in argument), or a folded spectrum method. The latter expects two
      references: one slightly above the vbm, and the other slightly below the
      cbm. It performs two folded spectrum calculations, one for each method,
      using the functional and keyword arguments given on input. If the
      references are not placed accurately (eg slightly above the CBM and
      slightly below the VBM), the algorithm applies some heuristics to try an
      determine a better set of references. The calculations then repeat for a
      maximum of n times. Beyond that, or if the references vs eigenvalues
      cannot be made sense of, an electron-calculation is performed.
  """
  from os import getcwd
  from os.path import abspath
  from copy import deepcopy

  assert "do_genpot" not in kwargs,\
         ValueError("\"do_genpot\" is not an admissible argument of bandgap.")
  assert "do_escan" not in kwargs,\
         ValueError("\"do_escan\" is not an admissible argument of bandgap.")

  escan = deepcopy(escan)
         
  if outdir == None: outdir = getcwd()
  outdir    = abspath(outdir)
  
  return _band_gap_ae_impl(escan, structure, outdir, comm) if references == None\
         else _band_gap_refs_impl(escan, structure, outdir, references, comm, n) 

class ExtractAE(ExtractVasp):
  """ Band-gap extraction class. """
  is_ae = True
  """ This was an all-electron bandgap calculation. """
  def __init__(self, extract):
    super(ExtractAE, self).__init__(directory=extract.directory, comm=extract.comm)
    self.OUTCAR = extract.OUTCAR

  @property
  def bandgap(self):
    """ Greps band-gap from calculation. """
    return self.cbm - self.vbm

  @property
  @make_cached
  def vbm(self):
    """ Greps VBM from calculations. """
    eigenvalues = self.eigenvalues.copy()
    eigenvalues.sort()
    return self.eigenvalues[-5]

  @property
  @make_cached
  def cbm(self):
    """ Greps CBM from calculations. """
    eigenvalues = self.eigenvalues.copy()
    eigenvalues.sort()
    return self.eigenvalues[-4]

  def oscillator_strength(degeneracy=1e-3):
    """ Computes oscillator strength between vbm and cbm. """
    from numpy import numpy
    from . import dipole_matrix_elements
    dme = dipole_matrix_elements(self) # computes all dmes.
    result = 0e0
    for i, vbm in enumerate(self.eigenvalues):
      if abs(vbm - self.vbm) > degeneracy: continue
      for j, cbm in enumerate(self.eigenvalues): 
        if abs(cbm - self.cbm) > degeneracy: continue
        result += 2e0/3e0 / (cbm - vbm) * norm(result[i,j,:])
    return result
    

def _band_gap_ae_impl(escan, structure, outdir, comm, **kwargs):
  """ Computes bandgap of a structure using all-electron method. """
  from os.path import join
  from lada.escan._escan import nb_valence_states
  
  if "eref" in kwargs:
    assert kwargs["eref"] == None, ValueError("Unexpected eref argument when computing bandgap.")
    del kwargs["eref"]
  outdir = join(outdir, "AE")
  nbstates = nb_valence_states(structure)
  extract = escan( structure, outdir = outdir, comm = comm, eref = None,\
                   nbstates = nbstates + 4, **kwargs)
  return ExtractAE(extract)

class ExtractRefs(object):
  """ Band-gap extraction class for folded spectrum 2-ref method. """
  is_ae = False
  """ This was not an all-electron bandgap calculation. """
  def __init__(self, vbm_out, cbm_out):
    super(ExtractRefs, self).__init__()
    self.extract_vbm = vbm_out
    """ VBM extraction method. """
    self.extract_cbm = cbm_out
    """ CBM extraction method. """

  @property
  def bandgap(self):
    """ Greps band-gap from calculation. """
    return self.cbm - self.vbm

  @property
  @make_cached
  def _raw(self):
    vbm_eigs = self.extract_vbm.eigenvalues.copy()
    cbm_eigs = self.extract_cbm.eigenvalues.copy()

    between_refs =       [u for u in cbm_eigs if u >= vbm_ref and u < cbm_ref]
    between_refs.extend( [u for u in vbm_eigs if u >= vbm_ref and u < cbm_ref])
    between_refs = array([u for u in set(between_refs)] );
    between_refs.sort()

    return between_refs[0], between_refs[1]

  @property
  def vbm(self):
    """ Greps VBM from calculations. """
    from numpy import amax
    vbm_eigs = self.extract_vbm.eigenvalues.copy()
    return _raw[0]

  @property
  def cbm(self):
    """ Greps CBM from calculations. """
    from numpy import amin
    cbm_eigs = self.extract_cbm.eigenvalues.copy()
    return _raw[1]

  def oscillator_strength(degeneracy=1e-3):
    """ Computes oscillator strength between vbm and cbm. """
    from numpy import numpy
    from . import dipole_matrix_elements
    dme = dipole_matrix_elements(vbm_out, cbm_out) # computes all dmes.
    result = 0e0
    for i, vbm in enumerate(vbm_out.eigenvalues):
      if abs(vbm - self.vbm) > degeneracy: continue
      for j, cbm in enumerate(cbm_out.eigenvalues): 
        if abs(cbm - self.cbm) > degeneracy: continue
        result += 2e0/3e0 / (cbm - vbm) * norm(result[i,j,:])
    return result

def _band_gap_refs_impl(escan, structure, outdir, references, comm, n=5, **kwargs):
  """ Computes band-gap using two references. """
  from os.path import join, exists
  from shutil import copyfile
  from numpy import array, argmax
  from ..opt.changedir import Changedir
  
  # some sanity checks.
  nbstates = escan.nbstates
  if "nbstates" in kwargs:
    nbstates = kwargs["nbstates"]
    del kwargs["nbstates"]
  if nbstates < 2: nbstates = 2
  if "eref" in kwargs:
    assert kwargs["eref"] == None, ValueError("Unexpected eref argument when computing bandgap.")
    del kwargs["eref"]
  # check/correct input arguments
  do_relax = escan.do_relax
  if do_relax in kwargs:
    do_relax = kwargs["do_relax"]
    del kwargs["do_relax"]
  
  assert len(references) == 2, ValueError("Expected 2-tuple for argument \"references\".")
  vbm_ref, cbm_ref = references
  if vbm_ref > cbm_ref: cbm_ref, vbm_ref = references

  # first computes vff and genpot.
  vffout = escan( structure, outdir=outdir, do_escan=False, do_genpot=True,\
                  do_relax=do_relax, comm = comm, **kwargs )
  
  def _copy_files(directory):
    with Changedir(join(outdir, directory), comm = comm) as cwd:
      POSCAR = escan._POSCAR + "." + str(comm.rank)
      if exists(join(outdir, POSCAR)): copyfile(join(outdir, POSCAR), POSCAR)
      POTCAR = escan._POTCAR + "." + str(comm.rank)
      if exists(join(outdir, POTCAR)): copyfile(join(outdir, POTCAR), POTCAR)
      cout = escan.vff._cout(comm)
      if exists(join(outdir, cout)): copyfile(join(outdir, cout), cout)

  iter, continue_loop = 0, True
  recompute = [True, True]
  while iter < n and continue_loop:
    print "recompute: ", recompute
    print "refs: ", vbm_ref, cbm_ref
    # computes vbm
    if recompute[0]:
      directory = join(outdir, "VBM")
      _copy_files(directory)
      vbm_out = escan( structure, outdir=directory, comm=comm,\
                       eref=vbm_ref, overwrite=True, do_relax=False,\
                       do_genpot=False, **kwargs )
      vbm_eigs = vbm_out.eigenvalues.copy()
    # computes cbm
    if recompute[1]:
      directory = join(outdir, "CBM")
      _copy_files(directory)
      cbm_out = escan( structure, outdir=directory, comm=comm,\
                       eref=cbm_ref, overwrite=True, do_relax=False,
                       do_genpot=False, **kwargs )
      cbm_eigs = cbm_out.eigenvalues.copy()
    recompute = [False, False] # by default, does not recompute
  
    below_refs =       [u for u in cbm_eigs if u < vbm_ref]
    below_refs.extend( [u for u in vbm_eigs if u < vbm_ref])
    below_refs = array([u for u in set(below_refs)] )
    below_refs.sort()
    between_refs =       [u for u in cbm_eigs if u >= vbm_ref and u < cbm_ref]
    between_refs.extend( [u for u in vbm_eigs if u >= vbm_ref and u < cbm_ref])
    between_refs = array([u for u in set(between_refs)] );
    between_refs.sort()
    above_refs =       [u for u in cbm_eigs if u >= cbm_ref]
    above_refs.extend( [u for u in vbm_eigs if u >= cbm_ref])
    above_refs = array([u for u in set(above_refs)] )
    above_refs.sort()
  
    if between_refs.size == 0: # no eigenvalues between the references.
      if below_refs.size > 0 and above_refs.size > 0: break # sole case where break is allowed.
      continue_loop = False; continue # got to all electron calculation.

    # there are eigenvalues between the references. Determines the largest "gap"
    a = [ vbm_ref ]; a.extend(u for u in between_refs.flat); a.append(cbm_ref)
    gap_index = argmax(array(a[1:]) - array(a[:-1])) # computes all differences.
    deltas = [a[gap_index] - a[0], a[gap_index+1] - a[gap_index], a[-1] - a[gap_index+1]]
    print "deltas: ", deltas
    print "gap_index: ", gap_index
    # Check pathological case where vbm and cbm give essentially same eigenvalues.
    if gap_index == 0 and below_refs.size == 0:
      if deltas[1] > 10e0*deltas[2]: vbm_ref -= deltas[1] * 0.95; recompute[0] = False
      else: continue_loop = False;
      continue 
    if gap_index == len(a)-1 and above_refs.size == 0:
      if deltas[1] > 10e0*deltas[1]: cbm_ref += deltas[1] * 0.95; recompute[1] = False
      else: continue_loop = False;
      continue #
    # Computes actual gap.
    if gap_index == 0: deltas[1] += vbm_ref - below_refs[-1]
    if gap_index == len(a)-1: deltas[1] += above_refs[0] - cbm_ref 
    print "new deltas: ", deltas
    # case where no gap can be truly determined.
    if not (deltas[1] > 10e0 * deltas[0] and deltas[1] > 10e0 * deltas[2]):
      continue_loop = False; continue # go to all electron calculation.

    # finally, recomputation case. Sets reference to best possible values.
    vbm_ref = below_refs[-1] if gap_index == 0        else a[gap_index]
    cbm_ref = above_refs[0]  if gap_index == len(a)-1 else a[gap_index+1]
    print between_refs
    print a
    vbm_ref +=  deltas[1] * 0.3 
    cbm_ref -=  deltas[1] * 0.3 
    recompute = [True, True]
    iter += 1
  else: # ran through all iterations and failed.
    return _band_gap_ae_impl(escan, structure, outdir, comm)
  return ExtractRefs(vbm_out, cbm_out)



      

