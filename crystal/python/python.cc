//
//  Version: $Id$
//
#ifdef HAVE_CONFIG_H
# include <config.h>
#endif

#include <boost/python.hpp>

#include "lattice.hpp"
#include "structure.hpp"
#include "atom.hpp"
#include "read_structure.hpp"

BOOST_PYTHON_MODULE(crystal)
{
  LaDa::Python::expose_atom();
  LaDa::Python::expose_structure();
  LaDa::Python::expose_lattice();
  LaDa::Python::expose_read_structure();
}
