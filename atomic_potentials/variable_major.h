//
//  Version: $Id$
//
#ifndef LADA_ATOMIC_POTENTIAL_VARIABLE_MAJOR_H_
#define LADA_ATOMIC_POTENTIAL_VARIABLE_MAJOR_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <boost/numeric/ublas/matrix.hpp>

#include "sum_of_separables.h"

namespace LaDa
{
  namespace AtomicPotential
  {
    class VariableMajor
    {
      public:
        //! Constructor.
        VariableMajor(SumOfSepables const &_sumofseps);
        //! Copy Constructor.
        VariableMajor( VariableMajor &_sos ): sos_(_sos) {}

        //! Reassigns functions and coefficients to a sum of separable functions.
        void reassign(SumOfSeparables &_sumofseps);

      private:
       //! Type of the numeric values.
       typedef SumOfSeparables::t_Function::t_Function::arg_type t_Value;
       //! Type of the numeric vectors.
       typedef SumOfSeparables::t_Coefficients t_Vector;
       //! Type of the vectors of vectors of coefficients.
       typedef std::vector<t_Vector> t_CoefVectors;
       //! Type of the vectors of vectors of functions,
       typedef std::vector< std::vector<SumOfSeparables::t_Function::t_Function> > t_FuncVectors;

       //! Vector of scales.
       t_Vector scales_;
       //! Vector of vectors of coefficients.
       t_CoefVectors coefficients_;
       //! Vector of vectors of functions.
       t_FuncVectors functions_;
    };
  } // namespace AtomicPotential
} // namespace LaDa
#endif
