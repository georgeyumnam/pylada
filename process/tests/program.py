def test(executable):
  """ Tests ProgramProcess. Includes failure modes.  """
  from tempfile import mkdtemp
  from os.path import join, exists
  from shutil import rmtree
  from lada.process.program import ProgramProcess
  from lada.process import Fail
  from lada.misc import Changedir
  from lada import default_comm
  from functional import ExtractSingle as Extract
  dir = mkdtemp()
  comm = default_comm.copy()
  try: 
    with Changedir(dir) as pwd: pass
    stdout = join(dir, 'stdout')
    program = ProgramProcess( executable, outdir=dir, 
                              cmdline=['--sleep', 0, '--order', 4], 
                              stdout=stdout, comm=comm, dompi=True )
    program.start()
    while not program.poll():  continue
    extract = Extract(stdout)
    assert extract.success
    assert abs(extract.pi-3.146801e+00) < 1e-2 * extract.error
    assert abs(extract.error-0.005207865) < 1e-2 * extract.error
    assert extract.comm['n'] == comm['n']
    # restart
    assert program.process is None
    program.start()
    assert program.process is None
  finally: rmtree(dir)

  try: 
    with Changedir(dir) as pwd: pass
    stdout = join(dir, 'stdout')
    program = ProgramProcess( executable, outdir=dir, 
                              cmdline=['--sleep', 0, '--order', 666], 
                              stdout=stdout, comm=comm, dompi=True )
    program.start()
    while not program.poll():  continue
  except Fail: pass
  else: raise Exception()
  finally: rmtree(dir)

  try: 
    with Changedir(dir) as pwd: pass
    stdout = join(dir, 'stdout')
    program = ProgramProcess( executable, outdir=dir, 
                              cmdline=['--sleep', 0, '--order', 6666], 
                              stdout=stdout, comm=comm, dompi=True )
    program.start()
    while not program.poll():  continue
  except Fail: pass
  else: raise Exception()
  finally: rmtree(dir)

if __name__ == "__main__":
  from sys import argv, path
  from os.path import abspath
  if len(argv) < 1: raise ValueError("test need to be passed location of pifunc.")
  if len(argv) > 2: path.extend(argv[2:])
  test(abspath(argv[1]))
