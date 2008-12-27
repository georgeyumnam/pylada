//
//  Version: $Id$
//
#ifndef _LADA_MINIMIZERS_MINUIT_H_
#define _LADA_MINIMIZERS_MINUIT_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <Minuit2/FCNGradientBase.h>
#include <Minuit2/FunctionMinimum.h>
#include <Minuit2/MnMigrad.h>
#include <Minuit2/MnUserParameters.h>
#include <Minuit2/MnPrint.h>

#include <limits.h>

#include <opt/types.h>

#include "variant.h"


namespace LaDa
{
  namespace Minimizer 
  {

    //! Minimizer interfaces for the Minuit2 library.
    class Minuit2
    {
      protected:
        //! A wrapper for Minuit2 function classes.
        template< class T_FUNCTION > class FunctionWrapper;
      public:
        //! Convergence criteria.
        types::t_real tolerance;
        //! Maximum number of calls to functional.
        types::t_unsigned itermax; 
        //! Whether to be verbose.
        bool verbose;
        //! Migrad strategy( fast = 0, slow = 1, slowest = 2 )
        types::t_unsigned strategy;
        //! uncertainties, whatever those are.
        types::t_real uncertainties;

      public:
        //! Constructor.
        Minuit2() : tolerance(types::tolerance),
                    itermax(0), verbose(false),
                    strategy(2), uncertainties(0.1) {}
              
        //! Destructor
        virtual ~Minuit2(){};

        //! Minimization functor
        template< class T_FUNCTION >
          typename T_FUNCTION :: t_Return
            operator()( const T_FUNCTION &_func,
                        typename T_FUNCTION :: t_Arg &_arg ) const
            { return operator_< T_FUNCTION,
                                typename T_FUNCTION :: t_Arg,
                                typename T_FUNCTION :: t_Return
                              >( _func, _arg ); }
        //! Loads the minimizer from XML
        bool Load( const TiXmlElement &_node );
      private:
        //! Minimization functor
        template< class T_FUNCTION, class T_CONTAINER, class T_RETURN >
          T_RETURN operator_( const T_FUNCTION &_func, T_CONTAINER &_arg ) const;
        //! Serializes a structure.
        template<class ARCHIVE> void serialize(ARCHIVE & _ar, const unsigned int _version);
    };

    LADA_REGISTER_MINIMIZER_VARIANT_HEADER( Minuit2, "Minuit2 Migrad" )

    template< class T_FUNCTION > 
      class Minuit2 :: FunctionWrapper : public ROOT::Minuit2::FCNGradientBase
      {
        public:
          //! Type of the original function.
          typedef T_FUNCTION t_Function;
          //! Type of the argument
          typedef std::vector<double> t_Arg;
          //! Type of the return.
          typedef double t_Return;

          //! Constructor.
          explicit FunctionWrapper( const T_FUNCTION&  _f ) : function_(_f) {}
          //! Copy Constructor.
          FunctionWrapper   ( const FunctionWrapper &_c )
                          : ROOT::Minuit2::FCNGradientBase( _c ),
                            function_( _c.function_ ) {}
          //! Destructor.
          virtual ~FunctionWrapper() {};
          //! Evaluation.
          t_Return operator()(const t_Arg& _arg) const { return function_( _arg ); }
          //! See Minuit2 lack of description.
          virtual double Up() const { return 1e0; }
          //! Gradient. 
          t_Arg Gradient( const t_Arg& _arg ) const 
          { 
            typename T_FUNCTION :: t_Arg grad( _arg.size(), 0e0 );
            function_.gradient( _arg, &grad[0] );
            return grad;
          }
        // //! do not check gradient.
        // virtual bool CheckGradient() const {return false;}

        protected:
          //! A constant reference to the wrapped function.
          const t_Function &function_;
      };


    template<class T_FUNCTION, class T_CONTAINER, class T_RETURN> 
      T_RETURN  Minuit2 :: operator_( const T_FUNCTION &_func, T_CONTAINER &_arg ) const
      {
        namespace rm2 = ROOT::Minuit2;
        __DEBUGTRYBEGIN
   
          if ( verbose ) std::cout << "Starting Minuit2 MIGRAD minimization\n";

          rm2::MnUserParameters parameters
                                ( 
                                  _arg, 
                                  std::vector<double>( _arg.size(), uncertainties )
                                );
          rm2::MnStrategy stra( strategy );
          FunctionWrapper<T_FUNCTION> wrapper( _func );
          rm2::MnMigrad minimizer
                        ( 
                          wrapper,
                          parameters,
                          strategy
                        );
          rm2::FunctionMinimum result = minimizer
                                        (
                                          itermax != 0 ? itermax: UINT_MAX, 
                                          tolerance 
                                        );
          _arg = result.UserState().Params();
          if( verbose ) std::cout << result << "\n";

          { // recomputes gradient just to make sure.
            typedef typename T_CONTAINER::value_type t_Type;
            t_Type *grad = new t_Type[ _arg.size() ];
            _func.gradient( _arg, grad );
            delete[] grad;
          }
   
          return _func( _arg );
   
        __DEBUGTRYEND(, "Error encountered while minimizing with the Minuit2 library\n")
   
      }  // dummy minimizer


    template<class ARCHIVE>
      void Minuit2 :: serialize(ARCHIVE & _ar, const unsigned int _version)
      {
         _ar & itermax;
         _ar & tolerance;
         _ar & verbose;
         _ar & strategy;
         _ar & uncertainties;
      }
    
  }
} 
#endif