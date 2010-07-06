#include "LaDaConfig.h"

#include <boost/python/module.hpp>
#include <boost/python/docstring_options.hpp>
#include <boost/python/scope.hpp>

#include "cgs.hpp"
#include "interpolated_gradient.hpp"
#include "minimizer.hpp"

BOOST_PYTHON_MODULE(_minimizer)
{
  namespace bp = boost::python;
  bp::scope scope;
  scope.attr("__doc__") = "Interface to c/fortran/c++ minimizers\n\n";
                          "Use numpy mininmizers where possible.";
  bp::docstring_options doc_options(true, false);

  LaDa::Python::expose_cgs();
  LaDa::Python::expose_llsq();
  LaDa::Python::expose_interpolated_gradient();
  LaDa::Python::expose_minimizer();
}
