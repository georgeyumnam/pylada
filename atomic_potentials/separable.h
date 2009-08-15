//
//  Version: $Id$
//
#ifndef LADA_ATOMIC_POTENTIAL_SEPARABLE_H_
#define LADA_ATOMIC_POTENTIAL_SEPARABLE_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include "functions.h"

namespace LaDa
{
  namespace AtomicPotential
  {
    //! A separable function.
    class Separable
    {
      public:
        //! Argument type.
        typedef std::vector<Functions::arg_type> arg_type;
        //! Type of the return.
        typedef Functions::result_type result_type;

        //! Type of the functions in list.
        typedef Separable t_Function;
        //! Type of the function-list.
        typedef std::list<t_Function> t_Functions;

        //! Type of the iterator over functions and coefficients.
        typedef t_Function::iterator iterator;
        //! Type of the iterator over functions and coefficients.
        typedef t_Function::const_iterator const_iterator;

        //! Constructor.
        Separable() {}
        //! Copy Constructor.
        Separable   ( Separable const& _c ) : functions_(_c.functions) {}

        //! Sums over all functionals.
        template<class T_CONTAINER> 
          result_type operator()( T_CONTAINER const& _x ) const
          {
            LADA_ASSERT( functions_.size() == _x.size(), "Incoherent containers.\n" ) 
  
            result_type result(1);
            t_Functions :: const_iterator i_func( functions_.begin() );
            t_Functions :: const_iterator const i_func_end( functions_.end() );
            t_Functions :: const_iterator i_x( _x.begin() );
            for(; i_func != i_func_end; ++i_func) result *= (*i_func)(*i_x);
            return result;
          }

        //! Returns iterator to functions and coefficients.
        iterator begin() { return functions_.begin(); }
        //! Returns iterator to functions and coefficients.
        const_iterator begin() const { return functions_.begin(); }
        //! Returns iterator to functions and coefficients.
        iterator end() { return functions_.end(); }
        //! Returns iterator to functions and coefficients.
        const_iterator end() const { return functions_.end(); }
        //! pushes a function and coefficient back.
        void push_back( t_Function const& _function )
          { functions_.push_back(_function); }
        //! Clears all functions and coefficients.
        void clear() { functions_.clear(); }

        result_type normalize()
        {
          LADA_ASSERT( functions_.size() == coefficients_.size(), "Incoherent containers.\n" ) 

          types::t_real result(1);
          t_Functions :: iterator i_func( functions_.begin() );
          t_Functions :: iterator const i_func_end( functions_.end() );
          for(; i_func != i_func_end; ++i_func ) result *= i_func->normalize();
          return result;
        }

      private:
        //! List of functions over scalars.
        t_Functions functions_;
    };


  } // namespace AtomicPotential
} // namespace LaDa
#endif
