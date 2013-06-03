.. testing_ug:

Testing Pylada
**************

Proof of existence test
-----------------------


The simplest possible test is to and load Pylada in a python_ shell:

  $ python
  >>> import pylada

If this fails with a message saying Pylada cannot be loaded, then it is likely
pylada was installed somewhere that python does not know about.
Make sure that Pylada is in one of the directories listed by the commands
below: 

  >>> import sys
  >>> sys.path

If the directory is not listed, please refer to the documentation for
`sys.path`__.

.. __ :: http:://docs.python.org/2/library/sys.html#sys.path

If loading Pylada fails with a message saying a package (other than Pylada)
cannot be found, then please install that package.



Battery of tests
----------------

A series of tests exist for Pylada. Once python can find the Pylada package it
is possible to batch launch these tests:

  $ cd /path/to/pylada/build
  $ make test

It is also possible to test specific mosules:

  $ cd /path/to/pylada/build/module_name 
  $ make test

Or specific tests:
 
  $ cd /path/to/pylada/build
  $ python ../module_name/tests/test_name.py 

Some tests will require an argument.
If you have more tests, please do send them. 


Failure modes and possible solutions
------------------------------------

  1. Pylada cannnot be found. This is the most likely failure mode. Every other
     day in my case. Please check above.

  2. The failed test is called "[vasp, crystal]_run.py". Most likely, Pylada
     cannot find the VASP_/GULP executable. See :ref:`here for
     vasp<install_vasp_ug>`. The others are similar.
  
  3. The failed test is *still* called "[vasp, crystal]_run.py": Check that
     :py:data:`lada.mpirun_exe` is set correctly, and that you have installed
     openmpi or something.

  4. "vff_functional" fails: try upgrading scipy. 

  
