""" Miscellaneous """
__docformat__  = 'restructuredtext en'
from types import ModuleType
from contextlib import contextmanager

from _opt import __load_vasp_in_global_namespace__, __load_escan_in_global_namespace__,\
                 cReals, _RedirectFortran, ConvexHull, ErrorTuple
from changedir import Changedir
from tempdir import Tempdir
from decorators import broadcast_result, make_cached
from filecache import FileCache
from ._ordered_dict import OrderedDict
from ._extract import AbstractExtractBase, OutcarSearchMixin

__all__ = [ '__load_vasp_in_global_namespace__', '__load_escan_in_global_namespace__',\
            'cReals', 'ConvexHull', 'ErrorTuple', 'redirect_all', 'redirect', 'read_input',\
            'LockFile', 'acquire_lock', 'open_exclusive', 'RelativeDirectory', 'streams',
            'AbstractExtractBase', 'OutcarSearchMixin', 'convert_from_unix_re', 'OrderedDict', 
            'exec_input', 'FileCache', 'Changedir', 'Tempdir', 'broadcast_result', 'make_cached',
            'load' ]

streams = _RedirectFortran.fortran
""" Name of the streams. """

class _RedirectPy:
  """ Redirects C/C++ input, output, error. """
  def __init__(self, unit, filename, append):
    self.unit = unit
    self.filename = filename
    self.append = append
  def __enter__(self):
    import sys
    if self.unit == streams.input:    self.old = sys.stdin
    elif self.unit == streams.error:  self.old = sys.stderr
    elif self.unit == streams.output: self.old = sys.stdout
    else: raise RuntimeError("Unknown redirection unit.")
    self.file = open(self.filename if len(self.filename)\
                else "/dev/null", "a" if self.append else "w")
    if self.unit == streams.input:    sys.stdin  = self.file
    elif self.unit == streams.error:  sys.stderr = self.file
    elif self.unit == streams.output: sys.stdout = self.file
    else: raise RuntimeError("Unknown redirection unit.")
    return self
  def __exit__(self, *wargs):
    import sys 
    if self.unit == streams.input:    sys.stdin  = self.old 
    elif self.unit == streams.error:  sys.stderr = self.old 
    elif self.unit == streams.output: sys.stdout = self.old 
    else: raise RuntimeError("Unknown redirection unit.")
    self.file.close()
      
class _RedirectAll:
  """ Redirects C/C++ input, output, error. """
  def __init__(self, unit, filename, append):
    self.unit = unit
    self.filename = filename
    if self.filename is None: self.filename = ""
    if self.filename == "/dev/null": self.filename = ""
    self.append = append
  def __enter__(self):
    import os
    import sys
    if self.unit == streams.input:    self.old = os.dup(sys.__stdin__.fileno())
    elif self.unit == streams.output: self.old = os.dup(sys.__stdout__.fileno())
    elif self.unit == streams.error:  self.old = os.dup(sys.__stderr__.fileno())
    else: raise RuntimeError("Unknown redirection unit.")
    if len(self.filename) == 0:
      self.filefd = os.open(os.devnull, os.O_RDWR | os.O_APPEND)
    else:
      self.filefd = os.open(self.filename, (os.O_RDWR | os.O_APPEND) if self.append\
                                           else (os.O_CREAT | os.O_WRONLY | os.O_EXCL))
    if self.append: self.file = os.fdopen(self.filefd, 'a')
    else: self.file = os.fdopen(self.filefd, 'w')
    if self.unit == streams.input:    os.dup2(self.file.fileno(), sys.__stdin__.fileno())
    elif self.unit == streams.output: os.dup2(self.file.fileno(), sys.__stdout__.fileno())
    elif self.unit == streams.error:  os.dup2(self.file.fileno(), sys.__stderr__.fileno())
    else: raise RuntimeError("Unknown redirection unit.")
    return self
  def __exit__(self, *wargs):
    import os
    import sys
    # close file descriptor for on-disk file.
    try: self.file.close()
    except OSError: pass
    # returns standard stream to original file/
    try:
      if self.unit == streams.input:    os.dup2(self.old, sys.__stdin__.fileno()) 
      elif self.unit == streams.output: os.dup2(self.old, sys.__stdout__.fileno())
      elif self.unit == streams.error:  os.dup2(self.old, sys.__stderr__.fileno())
      else: raise RuntimeError("Unknown redirection unit.")
    except OSError: pass
    finally: 
      # close duplicate of original standard stream.
      try: os.close(self.old)
      except OSError: pass

def redirect_all(output=None, error=None, input=None, append = False):
  """ A context manager to redirect inputs, outputs, and errors. 
  
      :Parameters:
        output
          Filename to which to redirect output. 
        error
          Filename to which to redirect err. 
        input
          Filename to which to redirect input. 
        append
          If true, will append to files. All or nothing.
  """
  from contextlib import nested
  result = []
  for value, unit in [ (output, streams.output), (error, streams.error), (input, streams.input) ]:
    if value is None: continue
    result.append( _RedirectAll(unit=unit, filename=value, append=append) )
  return nested(*result)


def redirect(fout=None, ferr=None, fin=None, pyout=None, pyerr=None, pyin=None, append = False):
  """ A context manager to redirect inputs, outputs, and errors. 
  
      :Parameters:
        fout
          Filename to which to redirect fortran output. 
        ferr
          Filename to which to redirect fortran err. 
        fin
          Filename to which to redirect fortran input. 
        pyout
          Filename to which to redirect C/C++ output. 
        pyerr
          Filename to which to redirect C/C++ err. 
        pyin
          Filename to which to redirect C/C++ input. 
        append
          If true, will append to files. All or nothing.
  """
  from contextlib import nested
  result = []
  for value, unit in [ (fout, streams.output), (ferr, streams.error), (fin, streams.input) ]:
    if value is None: continue
    result.append( _RedirectFortran(unit=unit, filename=value, append=append) )
  for value, unit in [ (pyout, streams.output), (pyerr, streams.error), (pyin, streams.input) ]:
    if value is None: continue
    result.append( _RedirectPy(unit=unit, filename=value, append=append) )
  return nested(*result)


class Input(ModuleType):
  """ Fake class which will be updated with the local dictionary. """
  def __init__(self, name = "lada_input"): 
    """ Initializes input module. """
    super(Input, self).__init__(name, "Input module for lada scripts.")
  def __getattr__(self, name):
    raise AttributeError( "All out of cheese!\n"
                          "Required input parameter '{0}' not found in {1}." \
                          .format(name, self.__name__) )
  def __delattr__(self, name):
    raise RuntimeError("Cannot delete object from input namespace.")
  def __setattr__(self, name, value):
    raise RuntimeError("Cannot set/change object in input namespace.")
  def update(self, other):
    if hasattr(other, '__dict__'): other = other.__dict__
    for key, value in other.items():
      if key[0] == '_': continue
      super(Input, self).__setattr__(key, value)
  def __contains__(self, name):
    return name in self.__dict__

def read_input(filename='input.py', global_dict=None, local_dict = None, paths=None, comm = None):
  """ Reads and executes input script and returns local dictionary (as namespace instance). """
  from os.path import exists, basename
  assert exists(filename), IOError('File {0} does not exist.'.format(filename))
  with open(filename, 'r') as file: string = file.read()
  return exec_input(string, global_dict, local_dict, paths, comm, basename(filename))

def exec_input( script, global_dict=None, local_dict = None,\
                paths=None, comm = None, name=None):
  """ Executes input script and returns local dictionary (as namespace instance). """
  # stuff to import into script.
  from os import environ
  from os.path import abspath, expanduser
  from math import pi 
  from numpy import array, matrix, dot, sqrt, abs, ceil
  from numpy.linalg import norm, det
  from .. import physics, crystal
  from ..mpi import world
  from . import Input
  
  # Add some names to execution environment.
  if global_dict is None: global_dict = {}
  global_dict.update( { "environ": environ, "pi": pi, "array": array, "matrix": matrix, "dot": dot,
                        "norm": norm, "sqrt": sqrt, "ceil": ceil, "abs": abs,  "det": det,
                        "physics": physics, "expanduser": expanduser, 'world': world,
                        "load": load })
  for key in crystal.__all__: global_dict[key] = getattr(crystal, key)
  if local_dict is None: local_dict = {}
  # Executes input script.
  exec(script, global_dict, local_dict)

  # Makes sure expected paths are absolute.
  if paths is not None:
    for path in paths:
      if path not in local_dict: continue
      local_dict[path] = abspath(expanduser(local_dict[path]))
    
  if name is None: name = 'None'
  result = Input(name)
  result.update(local_dict)
  return result


  
class LockFile(object):
  """ Gets an advisory lock for file C{filename}.

      Creates a lock directory named after a file. Relies on the presumably
      atomic nature of creating a directory. 
      *Beware* of mpi problems! `LockFile` is (purposefully) not mpi aware.
      If used unwisely, processes will lock each other out.
  """
  def __init__(self, filename, timeout = None, sleep = 0.05):
    """ Creates a lock object. 

        :Parameters:
          timeout
            will raise a RuntimeError when calling `lock` if
            the lock could not be aquired within this time.
          sleep
            Time to sleep between checks when waiting to acquire lock. 

        Does not acquire lock at this stage. 
    """
    from os.path import abspath
    self.filename = abspath(filename)
    """ Name of file to lock. """
    self.timeout = timeout
    """ Maximum amount of time to wait when acquiring lock. """
    self.sleep = sleep
    """ Sleep time between checks on lock. """
    self._owns_lock = False
    """ True if this object owns the lock. """

  def lock(self):
    """ Waits until lock is acquired. """
    from os import makedirs, error, mkdir
    from os.path import exists
    import time

    # creates parent directory first, if necessary.
    if not exists(self._parent_directory):
      try: makedirs(self._parent_directory) 
      except error: pass
    start_time = time.time()
    # loops until acqires lock.
    while self._owns_lock == False: 
      # tries to create director.
      try:
        self._owns_lock = True
        mkdir(self.lock_directory)
      # if fails, then another process already created it. Just keep looping.
      except error: 
        self._owns_lock = False
        if self.timeout is not None:
          if time.time() - start_time > self.timeout:
            raise RuntimeError("Could not acquire lock on file {0}.".format(self.filename))
        time.sleep(self.sleep)

  def __enter__(self):
    """ Enters context. """
    self.lock()
    return self

  def __exit__(self, *args):
    """ Exits context. """
    self.release()

  @property
  def lock_directory(self):
    """ Name of lock directory. """
    from os.path import join, basename
    return join(self._parent_directory, "." + basename(self.filename) + "-lada_lockdir")
 
  @property
  def _parent_directory(self):
    from os.path import abspath, dirname
    return dirname(abspath(self.filename))

  @property
  def is_locked(self):
    """ True if a lock for this file exists. """
    from os.path import exists
    return exists(self.lock_directory)

  @property
  def owns_lock(self): 
    """ True if this object owns the lock. """
    return self._owns_lock

  def release(self):
    """ Releases a lock.

        It is an error to release a lock not owned by this object.
        It is also an error to release a lock which is not locked.
        Makes sure things are syncro. The latter is an internal bug though.
    """
    from os import rmdir
    assert self._owns_lock, IOError("Filelock object does not own lock.")
    assert self.is_locked, IOError("Filelock object owns an unlocked lock.")
    self._owns_lock = False
    rmdir(self.lock_directory)

  def __del__(self):
    """ Releases lock if still held. """
    if self.owns_lock and self.is_locked: self.release()

  def remove_stale(self, comm = None):
    """ Removes a stale lock. """
    from os import rmdir
    from os.path import exists
    from ..mpi import Communicator
    comm = Communicator(comm)
    comm.barrier()
    if exists(self.lock_directory):
      try: rmdir(self.lock_directory)
      except: pass
    comm.barrier()
      

def acquire_lock(filename, sleep=0.5, timeout=None):
  """ Alias for a `LockFile` context. 

      *Beware* of mpi problems! `LockFile` is (purposefully) not mpi aware.
      Only the root node should use this method.
  """
  return LockFile(filename, sleep=sleep, timeout=timeout)

@contextmanager
def open_exclusive(filename, mode="r", sleep = 0.5, timeout=None):
  """ Opens file while checking for advisory lock.

      This context uses `LockFile` to first obtain a lock.
      *Beware* of mpi problems! `LockFile` is (purposefully) not mpi aware.
      Only the root node should use this method.
  """
  # Enter context.
  with LockFile(filename, sleep=sleep, timeout=timeout) as lock:
    yield open(filename, mode)

class RelativeDirectory(object):
  """ Directory property which is relative to the user's home.
  
      The path which is returned (eg __get__) is always absolute. However,
      it is stored relative to the user's home, and hence can be passed from
      one computer system to the next.
      Unless you know what you are doing, it is best to get and set using the
      ``path`` attribute, starting from the current working directory if a
      relative path is given, and from the '/' root if an absolute path is
      given.

      >>> from os import getcwd, environ
      >>> getcwd()
      '/home/me/inhere/'
      >>> relative_directory.path = 'use/this/attribute'
      >>> relative_directory.path
      '/home/me/inhere/use/this/attribute'

      Other descriptors have somewhat more complex behaviors. ``envvar`` is the
      root directory - aka the fixed point. Changing it will simply change the
      root directory.

      >>> environ["SCRATCH"]
      '/scratch/me/'
      >>> relative_directory.envvar = "$SCRATCH"
      >>> relative_directory.envvar
      '/scratch/me/use/this/attribute'

      Modifying ``relative`` will change the second part of the relative
      directory. If a relative path is given, that relative path is used as is,
      without reference to the working directory. It is an error to give an
      absolute directory.

      >>> relative_directory.relative = "now/here"
      '/scratch/me/now/here'
      >>> relative_directory.relative = "/now/here"
      ValueError: Cannot set relative with absolute path. 

  """
  global_envvar = "~"
  """ Global envvar position.

      If envvar is set to None in any single instance, than this value takes
      over. Since it is a class attribute, it should be global to all instances
      with ``self.envvar is None``. 
  """
  def __init__(self, path=None, envvar=None, hook=None):
    """ Initializes the relative directory. 
    
        :Parameters:
          path : str or None
            path to store here. It can be relative to the current working
            directory, include envirnonment variables or shorthands for user
            homes. If None, will be set to `envvar`.
          envvar : str or None 
            Fixed point wich can be understood from system to system. It should
            be a shorthand to a user homer directory ("~/") or use an
            environment variable ("$SCRATCH"). If None, defaults to user's
            home.
          hook : callable or None
            This function will be called if/when the directory is changed. Note
            that it may be lost during pickling if it is not itself pickelable.
    """
    super(RelativeDirectory, self).__init__()

    self._relative = None
    """ Private path relative to fixed point. """
    self._envvar = None
    """ Private envvar variable. """
    self._hook = None
    """ Private hook variable. """
    self.envvar = envvar
    """ Fixed point. """
    self.path = path
    """ Relative path. """
    self.hook = hook
    """ An object to call when the path is changed.
    
        Callable with at most one argument.
    """

  @property
  def relative(self):
    """ Path relative to fixed point. """
    return self._relative if self._relative is not None else ""
  @relative.setter
  def relative(self, value):
    """ Path relative to fixed point. """
    from os.path import expandvars, expanduser
    if value is None: value = ""
    value = expandvars(expanduser(value.rstrip().lstrip()))
    assert value[0] != '/', ValueError('Cannot set "relative" attribute with absolute path.')
    self._relative = value if len(value) else None
    self.hook(self.path)

  @property 
  def envvar(self):
    """ Fixed point for relative directory. """
    from os import getcwd
    from os.path import expanduser, expandvars, normpath
    from . import Changedir
    if self._envvar is None:
       with Changedir(expanduser(self.global_envvar)) as pwd: return getcwd()
    return normpath(expandvars(expanduser(self._envvar)))
  @envvar.setter
  def envvar(self, value):
    if value is None: self._envvar = None
    elif len(value.rstrip().lstrip()) == 0: self._envvar = None
    else: self._envvar = value
    self.hook(self.path)

  @property 
  def path(self):
    """ Returns absolute path, including fixed-point. """
    from os.path import join, normpath
    if self._relative is None: return self.envvar
    return normpath(join(self.envvar, self._relative))
  @path.setter
  def path(self, value):
    from os.path import relpath, expandvars, expanduser
    from os import getcwd
    if value is None: value = getcwd()
    if isinstance(value, tuple) and len(value) == 2: 
      self.envvar = value[0]
      self.relative = value[1]
      return
    if len(value.rstrip().lstrip()) == 0: value = getcwd()
    self._relative = relpath(expanduser(expandvars(value)), self.envvar) 
    self.hook(self.path)

  @property
  def unexpanded(self):
    """ Unexpanded path (eg with envvar as is). """
    from os.path import join
    e = self.global_envvar if self._envvar is None else self._envvar
    return e if self._relative is None else join(e, self._relative)


  @property
  def hook(self):
    from inspect import ismethod, getargspec
    if self._hook is None: return lambda x: None
    N = len(getargspec(self._hook)[0])
    if ismethod(self._hook): N -= 1
    if N == 0: return lambda x: self._hook()
    return self._hook
  @hook.setter
  def hook(self, value): 
    from inspect import ismethod, getargspec, isfunction

    if value is None: 
      self._hook = None
      return
    assert ismethod(value) or isfunction(value), \
           TypeError("hook is not a function or bound method.")
    N = len(getargspec(value)[0])
    if ismethod(value):
      assert value.im_self is not None,\
             TypeError("hook callable cannot be an unbound method.")
      N -= 1
    assert N < 2, TypeError("hook callable cannot have more than one argument.")
    self._hook = value
  def __getstate__(self):
    """ Saves state. 

        If hook was not pickleable, then it will not be saved appropriately.
    """
    from pickle import dumps
    try: dumps(self._hook)
    except: return self._relative, self._envvar
    else:   return self._relative, self._envvar, self._hook
  def __setstate__(self, args):
    """ Resets state. 

        If hook was not pickleable, then it will not be reset.
    """
    if len(args) == 3: self._relative, self._envvar, self._hook = args
    else: self._relative, self._envvar = args

  def set(self, path=None, envvar=None):
    """ Sets path and envvar.

        Used by repr.
    """
    hook = self._hook
    self._hook = None
    self.envvar = envvar
    self.path = path
    self._hook = hook
    self.hook(self.path)

  def repr(self):
    """ Makes this instance somewhat representable. 

        Since hook cannot be represented in most cases, and is most-likely set
        on initialization, this method uses ``set`` to get away with
        representability.
    """
    return "{0}, {1}".format(repr(self._envvar), repr(self._relative))


def convert_from_unix_re(pattern):
  """ Converts unix-command-line like regex to python regex.

      Does not handle active python regex characters too well.
  """
  from re import compile
  star = compile(r"(?<!\\)\*")
  optional = compile(r"\[(\S),(\S)\]")
  unknown = compile(r"\?")
  pattern = unknown.sub(r".", pattern)
  pattern = star.sub(r"[^/]*", pattern)
  pattern = optional.sub(r"(?:\1,\2)", pattern)
  return compile(pattern)
    
@broadcast_result(key=True)
def copyfile( src, dest=None, nothrow=None, comm=None,\
              symlink=False, aslink=False, nocopyempty=False ):
  """ Copy ``src`` file onto ``dest`` directory or file.

      :kwarg src: Source file.
      :type  src: str
      :kwarg dest: Destination file or directory.
      :type dest: str or None
      :type nothrow: container or None
      :kwarg nothrow:
          Throwing is disable selectively depending on the content of nothrow:

          - *exists*: will not throw is src does not exist.
          - *isfile*: will not throw is src is not a file.
          - *same*: will not throw if src and dest are the same.
          - *none*: ``src`` can be None.
          - *null*: ``src`` can be '/dev/null'.
          - *never*: will never throw.
      :kwarg symlink:  Creates link rather than actual hard-copy. Symlink are
          created with relative paths given starting from the directory of
          ``dest``.  Defaults to False.
      :type symlink: bool
      :kwarg aslink:  Creates link rather than actual hard-copy *if* ``src`` is
          itself a link. Links to the file which ``src`` points to, not to
          ``src`` itself. Defaults to False.
      :type aslink: bool
      :kwarg nocopyempty: Does not perform copy if file is empty. Defaults to False.
      :type nocopyempty: bool

      This function fails selectively, depending on what is in ``nothrow`` list.
  """
  try:
    from os import getcwd, symlink as ln, remove
    from os.path import isdir, isfile, samefile, exists, basename, dirname,\
                        join, islink, realpath, relpath, getsize
    from shutil import copyfile as cpf
    # sets up nothrow options.
    if nothrow is None: nothrow = []
    if isinstance(nothrow, str): nothrow = nothrow.split()
    if nothrow == 'all': nothrow = 'exists', 'same', 'isfile', 'none', 'null'
    nothrow = [u.lower() for u in nothrow]
    # checks and normalizes input.
    if src is None: 
      if 'none' in nothrow: return False
      raise IOError("Source is None.")
    if dest is None: dest = getcwd()
    if dest == '/dev/null': return True
    if src  == '/dev/null':
      if 'null' in nothrow: return False
      raise IOError("Source is '/dev/null' but Destination is {0}.".format(destination))

    # checks that input source file exists.
    if not exists(src): 
      if 'exists' in nothrow: return False
      raise IOError("{0} does not exist.".format(src))
    if not isfile(src):
      if 'isfile' in nothrow: return False
      raise IOError("{0} is not a file.".format(src))
    # makes destination a file.
    if exists(dest) and isdir(dest): dest = join(dest, basename(src))
    # checks if destination file and source file are the same.
    if exists(dest) and samefile(src, dest): 
      if 'same' in nothrow: return False
      raise IOError("{0} and {1} are the same file.".format(src, dest))
    if nocopyempty and isfile(src):
      if getsize(src) == 0: return
    if aslink and islink(src): symlink, src = True, realpath(src)
    if symlink:
      if exists(dest): remove(dest)
      if relpath(src, dirname(dest)).count("../") == relpath(src, '/').count("../"):
        ln(src, realpath(dest))
      else:
        with Changedir(dirname(dest)) as cwd:
           ln(relpath(src, dirname(dest)), basename(dest))
    else: cpf(src, dest)
  except:
    if 'never' in nothrow: return False
    raise
  else: return True

def cpus_per_node():
  """ Greps /proc/cpuinfo to figure out the number of cpus per node. """
  from re import compile
  try:
    cpu_re = compile("processor\s*:\s*(\d+)")
    ncpus = 0
    with open("/proc/cpuinfo", "r") as file:
      for line in file:
        if cpu_re.search(line) is not None: ncpus += 1
    if ncpus == 0: raise RuntimeError("Could not determine number of cpus.")
    return ncpus
  except: return 1

def total_memory():
  """ Greps /proc/meminfo to figure out the memory per node. """
  from re import compile
  try:
    mem_re = compile("MemTotal\s*:\s*(\d+)\s*kB")
    with open("/proc/meminfo", "r") as file:
      for line in file:
        found = mem_re.search(line)
        if found is not None: return int(found.group(1))
    raise MemoryError("Could not determine total memory from /proc/meminfo.")
  except: return 10e9

def which(program):
  """ Gets location of program using system command which. """
  from subprocess import Popen, PIPE
  output = Popen(["which", program], stdout=PIPE).communicate()[0]
  return output if output[-1] != '\n' else output[:-1]

def load(data, *args, **kwargs):
  """ Loads data from the data files. """
  from os import environ
  from os.path import dirname, exists, join
  if "directory" in kwargs: 
    raise KeyError("directory is a reserved keyword of load")

  # find all possible data directories
  directories = []
  if "data_directory" in globals():
    directory = globals()["data_directory"]
    if hasattr(directory, "__iter__"): directories.extend(directory)
    else: directories.append(directory)
  if "LADA_DATA_DIRECTORY" in environ:
    directories.extend(environ["LADA_DATA_DIRECTORY"].split(":"))

  # then looks for data file.
  if data.rfind(".py") == -1: data += ".py"
  for directory in directories:
    if exists(join(directory, data)):
      kwargs["directory"] = dirname(join(directory, data))
      result = {}
      execfile(join(directory, data), {}, result)
      return result["init"](*args, **kwargs)
  raise IOError("Could not find data ({0}).".format(data))
