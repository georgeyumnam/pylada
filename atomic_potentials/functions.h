#ifndef LADA_ATOMIC_POTENTIAL_FUNCTIONS_H_
#define LADA_ATOMIC_POTENTIAL_FUNCTIONS_H_

#include "LaDaConfig.h"

#ifndef LADA_SEPN
# define LADA_SEPN 2
#endif

#include <list>
#include <iostream>
#include <numeric>
#include <algorithm>

#include <boost/function.hpp>
#include <boost/shared_ptr.hpp>

#include <misc/types.h>
#include <opt/debug.h>

#include "numeric_types.h"

namespace LaDa
{
  //! Contains classes for generalized atomic potentials.
  namespace atomic_potential
  {
    class Functions
    {
      public:
        //! Number of atomic species.
        const static size_t N = LADA_SEPN;
        //! Type of the argument.
        typedef std::pair<numeric_type, specie_type> arg_type;
        //! Type of the return.
        typedef numeric_type result_type;

        //! Type of the functions in list.
        typedef boost::function<result_type(arg_type::first_type const&)> t_Function;
        //! Type of the function-list.
        typedef std::list<t_Function> t_Functions;
        //! Type of the list of coefficients.
        typedef result_type t_Coefficient;
        //! Type of the list of coefficients.
        typedef std::vector<t_Coefficient> t_Coefficients;
        //! Type of the list of coefficients.
        typedef std::vector<std::string> t_Names;

        //! Type of the iterator over functions and coefficients.
        class iterator;
        //! Type of the iterator over functions and coefficients.
        class const_iterator;

        // includes iterator definitions here.
#       if defined(LADA_WITH_CONST) or defined(LADA_ITERATOR_NAME)
#         error LADA_WITH_CONST and LADA_ITERATOR_NAME already defined.
#       endif
#       define LADA_ITERATOR_NAME iterator
#       define LADA_WITH_CONST 
#       include "functions.iterator.h"
#       define LADA_ITERATOR_NAME const_iterator
#       define LADA_WITH_CONST const
#       include "functions.iterator.h"

        //! Constructor.
        Functions() {}
        //! Copy Constructor.
        Functions   ( Functions const& _c )
                  : functions_(_c.functions_),
                    coefficients_(_c.coefficients_),
                    names_(_c.names_) {}

        //! Sums over all functionals.
        result_type operator()( arg_type const& _x ) const;

        //! Returns iterator to functions and coefficients.
        iterator begin()
          { return iterator( functions_.begin(), coefficients_.begin(), names_.begin()); }
        //! Returns iterator to functions and coefficients.
        const_iterator begin() const
          { return const_iterator( functions_.begin(), coefficients_.begin(), names_.begin()); }
        //! Returns iterator to functions and coefficients.
        iterator end()
          { return iterator( functions_.end(), coefficients_.end(), names_.end()); }
        //! Returns iterator to functions and coefficients.
        const_iterator end() const
          { return const_iterator( functions_.end(), coefficients_.end(), names_.end()); }
        //! pushes a function and coefficient back.
        template< class T_FUNCTION >
          void push_back( T_FUNCTION const& _function,
                          numeric_type const _coef[N],
                          std::string const &_name )
          {
            functions_.push_back(_function);
            names_.push_back(_name);
            for(size_t i(0); i < N; ++i ) coefficients_.push_back(_coef[i]); 
          }
        //! Clears all functions and coefficients.
        void clear() { functions_.clear(); coefficients_.clear(); names_.clear(); }

        //! Normalizes coefficients to one, and returns norm.
        t_Coefficient normalize();

        //! Returns the number of functions.
        size_t size() const { return functions_.size(); }

      private:
        //! List of functions over scalars.
        t_Functions functions_;
        //! List of coefficients.
        t_Coefficients coefficients_;
        //! List of function names.
        t_Names names_;
    };

    //! Dumps iterator reference to stream.
    std::ostream& operator<<( std::ostream &_stream, 
                              Functions::const_iterator::reference const &_func );

    //! Dumps iterator reference to stream.
    std::ostream& operator<<( std::ostream &_stream,
                              Functions::iterator::reference const &_func );

    //! Dumps function to stream.
    std::ostream& operator<<( std::ostream &_stream, Functions const &_func );

  } // namespace atomic_potential
} // namespace LaDa
#endif
