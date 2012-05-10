Atom, Structure, and SmithTransform
-----------------------------------

.. currentmodule:: lada.crystal.cppwrappers

.. autoclass:: Atom
  :show-inheritance:
  :members: pos, type
  
  This class is also available directly under :py:mod:`lada.crystal`.

  .. automethod:: copy()->Atom
  .. automethod:: to_dict()->dict

.. autoclass:: Structure
  :show-inheritance:

  This class is also available directly under :py:mod:`lada.crystal`.

  .. autoattribute:: volume
  .. autoattribute:: cell
  .. autoattribute:: scale

  .. automethod:: copy()->Structure
  .. automethod:: to_dict()->dict
  .. automethod:: clear()->None
  .. automethod:: insert(index, atom)->None
  .. automethod:: pop(index)->Atom
  .. automethod:: extend(atoms)->None
  .. automethod:: append(atoms)->None
  .. automethod:: transform(matrix)->Structure
  .. automethod:: add_atom(...)->Structure
  .. automethod:: __getitem__()
  .. automethod:: __setitem__()

.. autoclass:: SmithTransform
  :show-inheritance:

  This class is also available directly under :py:mod:`lada.crystal`.

  .. autoattribute:: quotient
  .. autoattribute:: transform

  .. automethod:: copy()->SmithTransform
  .. automethod:: indices(position)->numpy.array
  .. automethod:: flatten_indices(indices, index=0)->numpy.array
  .. automethod:: index(position, index=0)->numpy.array
