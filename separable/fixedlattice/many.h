//
//  Version: $Id$
//
#ifndef _CE_MANY_H_
#define _CE_MANY_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include<boost/ptr_container/ptr_list.hpp>
#include<boost/shared_ptr.hpp>

#include<iostream>
#include<vector>
#include<list>

#include <opt/types.h>
#include <opt/debug.h>
#include <opt/indirection.h>

//! \cond 
namespace CE { template< class T_TRAITS > class Many; }
//! \endcond

namespace Traits
{
  namespace CE
  {
    //! Traits of a "Many" collapse functor.
    template< class T_MAPPING = ::CE::Mapping::Basic,
              class T_COEFFICIENTS = boost::numeric::ublas::matrix<types::t_real>,
              class T_VECTOR
                = boost::numeric::ublas::vector<typename T_COEFFICIENTS::value_type> >
    struct Many 
    {
      //! Type of the Mapping.
      typedef T_MAPPING t_Mapping;
      //! Type of the coefficients.
      typedef T_COEFFICIENTS t_Coefficients;
      //! Type of the vectors.
      typedef T_VECTOR t_Vector;
    };
  }

} // end of traits namespace.

namespace CE
{
  namespace details
  {
    //! Redefine separables traits such that coefficients are a range.
    template< class T_TRAITS, class T_COEFFICIENTS >
    struct SepTraits
    {
      //! Mapping traits.
      typedef typename T_TRAITS :: t_Mapping t_Mapping;
      //! Policy traits.
      typedef typename T_TRAITS :: t_Policy t_Policy;
      //! Range coefficients traits.
      typedef ::CE::Policy::MatrixRangeCoefficients t_Coefficients;
      //! Range coefficients traits.
      typedef typename t_Coefficients :: t_Matrix t_Matrix;
      //! Range coefficients traits.
      typedef typename T_TRAITS :: t_Vector t_Vector;
    };
    //! Redefines collapse traits with new separables.
    template< class T_SEPARABLES, class T_TRAITS >
    struct ColTraits
    {
      //! Type of the configuration matrix.
      typedef typename T_TRAITS :: t_Configurations t_Configurations;
      //! Type of the Mapping.
      typedef T_SEPARABLES t_Separables;
      //! Type of the Mapping.
      typedef typename T_TRAITS :: t_Mapping t_Mapping;
      //! Type of the Regulations Policy
      typedef typename T_TRAITS :: t_RegPolicy t_RegPolicy;
      //! Type of the Policy.
      typedef typename T_TRAITS :: t_UpdatePolicy t_UpdatePolicy;
    };
  }

  template< class T_TRAITS >
    class Many 
    {
      public:
        //! Type of the traits.
        typedef T_TRAITS t_Traits;
        //! Type of the of separables function.
        typedef opt::IndirectionBase  t_Separables;
        //! Type of the of separables function.
        typedef opt::IndirectionBase  t_Collapse;
        //! \brief Type of the matrix coefficients.
        typedef typename t_Traits :: t_Coefficients t_Coefficients;
        //! \brief Type of the matrix range.
        //! \details Necessary interface for minimizer.
        typedef typename t_Traits :: t_Coefficients t_Matrix;
        //! Type of the vectors.
        typedef typename t_Traits :: t_Vector t_Vector;
        //! Type of the container of separables.
        typedef boost::ptr_list< t_Collapse > t_Collapses;
        //! Type of the container of separables.
        typedef boost::ptr_list< t_Separables > t_CtnrSeparables;
        //! Type of the general mapping.
        typedef typename t_Traits :: t_Mapping t_Mapping;


        //! Constructor.
        Many() : separables_( new t_CtnrSeparables ),
                 collapses_( new t_Collapses ), dim(0) {}
        //! Copy Constructor.
        Many( const Many& _c ) : separables_( _c.separables_ ),
                                 collapses_( _c.collapses ),
                                 dim( _c.dim ), mapping_( _c.mapping_ ),
                                 coefficients_( _c.coefficients_ ) {}
        //! Destructor.
        ~Many() {}

        //! Creates the fitting matrix and target vector.
        template< class T_MATRIX, class T_VECTOR >
          void operator()( T_MATRIX &_A, T_VECTOR &_b,
                           types::t_unsigned _dim );
        //! Evaluates square errors.
        opt::ErrorTuple evaluate() const;
        //! Predicts target value of a structure.
        typename t_Matrix :: value_type evaluate( size_t _n ) const;

        //! \brief Updates the separable and copies the eci from column 0 to all
        //!        other columns.
        void update_all();
        //! Updates the separable and copies the eci from column d to column 0.
        void update( types::t_unsigned _d );
        //! Resets collapse functor.
        void reset();

        //! Returns the number of dimensions.
        size_t dimensions() const;
        //! Returns the number of degrees of liberty (per dimension).
        size_t dof() const;
        //! Returns the number of configurations.
        size_t nbconfs() const;
       
        //! Randomizes both cluster energies and ecis.
        void randomize( typename t_Vector :: value_type _howrandom );

        //! Add new collapse and separables.
        template< class T_COLLAPSE, class T_SEPARABLES > size_t add_as_is();
        //! Add new collapse and separables.
        template< class T_COLLAPSE, class T_SEPARABLES > size_t wrap_n_add();
        
        //! Returns reference to nth separable function.
        t_Separables* separables( size_t _n ) { return (*separables_)[_n].self(); }
        //! Returns constant reference to nth separable function.
        const t_Separables* separables( size_t _n ) const
          { return (*separables_)[_n].self(); }
        //! Returns reference to nth collapse functor.
        t_Collapse* collapse( size_t _n ) { return (*collapses_)[_n].self(); }
        //! Returns constant reference to nth collapse functor.
        t_Collapse* const collapse( size_t _n ) const
          { return (*collapses_)[_n].self(); }
        //! Returns the number of collapse and separables functions.
        size_t size() const { return collapses_->size(); }
        //! Returns a reference to the mapping.
        t_Mapping mapping() { return mapping_; }
        //! Returns a constant reference to the mapping.
        const t_Mapping mapping() const { return mapping_; }
        //! Initializes a collapse with rank and size.
        void init( size_t _index, size_t _rank, size_t _dimensions );

      protected:
        //! Returns the number of degrees of liberty for current dimension.
        size_t current_dof() const;
        //! Creates the _A and _b matrices for fitting.
        template< class T_MATRIX, class T_VECTOR >
          void create_A_n_b( T_MATRIX &_A, T_VECTOR &_b );

        //! The container of separable functions.
        boost::shared_ptr<t_CtnrSeparables> separables_;
        //! The collapse functor associated with the separable functions.
        boost::shared_ptr<t_Collapses> collapses_;
        //! Current dimension being updated.
        size_t dim;
        //! The mapping to the structures ( e.g. leave-one-out, leave-many-out )
        t_Mapping mapping_;
        //! The coefficienst.
        t_Coefficients coefficients_;
    };

  //! Prints mixed-approach description to a stream.
  template< class T_TRAITS >
  std::ostream& operator<<( std::ostream& _stream, const Many<T_TRAITS> &_col );

  //! Initializes a Many separable function depending on string input and structures.
  template< class T_STRUCTURES, class T_TRAITS >
   void init_many_collapses( const std::string &_desc, size_t _rank,
                             types::t_real _lambda, const T_STRUCTURES &_structures,
                             Many<T_TRAITS> &_many );

} // end of CE namespace

#include "many.impl.h"

#endif