//
//  Version: $Id$
//
#ifndef _CE_MANY_H_
#define _CE_MANY_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include<boost/ptr_container/ptr_vector.hpp>
#include<boost/shared_ptr.hpp>
#include<boost/mpl/apply.hpp>
#include<boost/mpl/transform.hpp>
#include<boost/fusion/container.hpp>
#include<boost/fusion/sequence.hpp>
#include<boost/fusion/functional.hpp>
#include<boost/fusion/support.hpp>
#include<boost/fusion/view.hpp>
#include<boost/fusion/iterator.hpp>
#include<boost/fusion/tuple.hpp>
#include<boost/fusion/algorithm.hpp>
#include<boost/fusion/mpl.hpp>
#include<boost/fusion/adapted.hpp>

#include<iostream>
#include<vector>

#include <opt/types.h>
#include <opt/debug.h>

#include "many.macros.h"

//! \cond 
namespace CE { template< class T_TRAITS > class Many; }
//! \endcond

namespace Traits
{
  namespace CE
  {
    //! Traits of a "Many" collapse functor.
    template< class T_VECTORS_OF_SEPARABLES,
              class T_VECTORS_OF_COLLAPSES,
              class T_MAPPING = ::CE::Mapping::Basic,
              class T_COEFFICIENTS = boost::numeric::ublas::matrix<types::t_real>,
              class T_VECTOR
                = boost::numeric::ublas::vector<typename T_COEFFICIENTS::value_type> >
    struct Many 
    {
      public:
        typedef typename boost::mpl::transform
                <
                  T_VECTORS_OF_SEPARABLES,
                  SeparablesWithMatrixRange< boost::mpl::_ >  
                > :: type t_Separables;
        //! Collapses with Ranged separables.
        typedef typename boost::mpl::transform
                <
                  T_VECTORS_OF_COLLAPSES, 
                  t_Separables,
                  CollapseWithNewSeparables< boost::mpl::_1, boost::mpl::_2 >
                > :: type t_Collapses;
      protected:
        //! Transforms an type into the type of a container of vectors.
        typedef boost::ptr_vector< boost::mpl::_ >  make_ptrvector;
        //! \brief Vector of separables type.
        //! \details After this double transformation, the mpl tuple should
        //!          contain pointer containers to ranged separables.
        typedef typename boost::mpl::transform
                < 
                  t_Separables,
                  make_ptrvector
                > :: type t_MPLVectorOfSeparables;
        //! \brief Vector of collapse type.
        //! \details After this double transformation, the mpl tuple should
        //!          contain pointer containers to collapses acting on ranged
        //!          separables.
        typedef typename boost::mpl::transform
                < 
                  t_Collapses,
                  make_ptrvector
                >  :: type t_MPLVectorOfCollapses;
      public:
        //! Tuple of containers of separables.
        typedef t_MPLVectorOfSeparables t_VectorsOfSeparables;
        //! Tuple of containers of collapses.
        typedef t_MPLVectorOfCollapses t_VectorsOfCollapses;
        //! Type of the Mapping.
        typedef T_MAPPING t_Mapping;
        //! Type of the coefficients.
        typedef T_COEFFICIENTS t_Coefficients;
        //! Type of the vectors.
        typedef T_VECTOR t_Vector;

        //! Meta-function for rebinding with new pararmeters.
        template< class TT_VECTORS_OF_SEPARABLES = T_VECTORS_OF_SEPARABLES, 
                  class TT_VECTORS_OF_COLLAPSES = T_VECTORS_OF_COLLAPSES,
                  class TT_MAPPING = T_MAPPING,
                  class TT_COEFFICIENTS = T_COEFFICIENTS, 
                  class TT_VECTOR = T_VECTOR >
        struct rebind
        {
          //! new rebound type.
          typedef Many< TT_VECTORS_OF_SEPARABLES,
                        TT_VECTORS_OF_COLLAPSES,
                        TT_MAPPING,
                        TT_COEFFICIENTS,
                        TT_VECTOR > type;
        };
        //! Meta-function for rebinding with new mapping.
        template< class TT_MAPPING = T_MAPPING >
        struct rebind_with_new_mapping
        {
          //! new rebound type.
          typedef Many< T_VECTORS_OF_SEPARABLES,
                        T_VECTORS_OF_COLLAPSES,
                        TT_MAPPING,
                        T_COEFFICIENTS,
                        T_VECTOR > type;
        };
    };

    //! Changes mapping of a ::CE::Many collapse functor.
    template< class T_MANYSEP, class T_NEW_MAPPING > class ChangeManyMapping
    {
        //! The old traits.
        typedef typename T_MANYSEP :: t_Traits t_Traits;
        //! The new traits with the new mapping.
        typedef typename t_Traits ::template rebind_with_new_mapping
                         < 
                           T_NEW_MAPPING
                         > :: type t_NewTraits;
      public:
        //! The resulting type.
        typedef typename T_MANYSEP ::template rebind< t_NewTraits > :: type type;
    };
  }

} // end of traits namespace.

namespace CE
{
  // Forward declaration.
  //! \cond
  template< class T_TRAITS > class Many;
  class ManyState;
  //! \endcond
  
  //! Prints mixed-approach description to a stream.
  template< class T_TRAITS >
    std::ostream& operator<<( std::ostream& _stream, const Many<T_TRAITS> &_col );

  //! Initializes a Many separable function depending on string input and structures.
  template< class T_STRUCTURES, class T_TRAITS >
   void init_many_collapses( const std::string &_desc, size_t _rank,
                             types::t_real _lambda, const T_STRUCTURES &_structures,
                             Many<T_TRAITS> &_many );


  template< class T_TRAITS > class Many 
  {
      friend std::ostream& operator<< <T_TRAITS>( std::ostream& _stream, 
                                                  const Many<T_TRAITS> &_col );
      template< class TT_TRAITS> friend class Many;
      friend class ManyState;
    public:
      //! Type of the traits.
      typedef T_TRAITS t_Traits;
    protected:
      //! \brief Type of the matrix coefficients.
      typedef typename t_Traits :: t_Coefficients t_Coefficients;
      //! Type of the vectors.
      typedef typename t_Traits :: t_Vector t_Vector;
      //! Type of the container of separables.
      typedef typename t_Traits :: t_VectorsOfCollapses t_VectorsOfCollapses;
      //! Type of the container of separables.
      typedef typename t_Traits :: t_VectorsOfSeparables t_VectorsOfSeparables;
      //! Type of the container of separables.
      typedef typename t_Traits :: t_Collapses t_Collapses;
      //! Type of the container of separables.
      typedef typename t_Traits :: t_Separables t_Separables;
      //! Type of the general mapping.
      typedef typename t_Traits :: t_Mapping t_Mapping;
    public:
      //! \brief Type of the matrix range.
      //! \details Necessary interface for minimizer.
      typedef typename t_Traits :: t_Coefficients t_Matrix;

    public:
      //! Constructor.
      Many() : separables_( new t_VectorsOfSeparables ),
               collapses_( new t_VectorsOfCollapses ), dim(0) {}
      //! Copy Constructor.
      template< class TT_TRAITS >
        Many   ( const Many<TT_TRAITS>& _c )
             : separables_( _c.separables_ ),
               collapses_( _c.collapses_ ),
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
      typename t_Matrix :: value_type evaluate( size_t _n ) const
      {
        return 0; } //boost::fusion::accumulate( viewasref( *collapses_ ), 0, ApplyEvaluateOne(_n) ); 
//      { return boost::fusion::accumulate( *collapses_, 0, ApplyEvaluateOne(_n) ); }


      //! \brief Updates the separable and copies the eci from column 0 to all
      //!        other columns.
      void update_all()
       { boost::fusion::transform( *collapses_, VOID_MFUNC(update_all)() ); }
      //! Updates the separable and copies the eci from column d to column 0.
      void update( types::t_unsigned _d )
       { boost::fusion::transform( *collapses_, U_MFUNC(update)(_d) ); }
      //! Resets collapse functor.
      void reset()
       { boost::fusion::transform( *collapses_, VOID_MFUNC(reset)() ); }

      //! Returns the number of dimensions.
      size_t dimensions() const
       { return 0; } //boost::fusion::fold( viewasref(*collapses_), 0, ApplyDimensions() ); }
      //! Returns the number of degrees of liberty (per dimension).
      size_t dof() const
       { return 0; } //return boost::fusion::accumulate( viewasref(*collapses_), 0, ACC_MFUNC(dof)() ); }
      //! Returns the number of configurations.
      size_t nbconfs() const
        { return 0; } //boost::fusion::accumulate( viewasref(*collapses_), 0, ACC_MFUNC(nbconfs)() ); }
     
      //! Randomizes both cluster energies and ecis.
      void randomize( typename t_Vector :: value_type _howrandom )
       { boost::fusion::transform( *collapses_, U_MFUNC(randomize)(_howrandom) ); }

      //! Add new collapse and separables.
      template< size_t _index > size_t addone();
      
      //! Returns reference to nth separable function.
      template< size_t _index >
        typename boost::mpl::at< t_Separables, boost::mpl::int_<_index> > :: type&
          separables( size_t _n )
           { return boost::fusion::at< boost::mpl::int_<_index> >(*separables_)[_n]; }
      //! Returns constant reference to nth separable function.
      template< size_t _index >
        const typename boost::mpl::at< t_Separables,
                                       boost::mpl::int_<_index> > :: type&
          separables( size_t _n ) const
           { return boost::fusion::at< boost::mpl::int_<_index> >(*separables_)[_n]; }
      //! Returns reference to nth collapse functor.
      template< size_t _index >
        typename boost::mpl::at< t_Collapses, boost::mpl::int_<_index> > :: type&
          collapses( size_t _n )
           { return boost::fusion::at< boost::mpl::int_<_index> >(*collapses_)[_n]; }
      //! Returns constant reference to nth collapse functor.
      template< size_t _index >
        const typename boost::mpl::at< t_Collapses, 
                                       boost::mpl::int_<_index> > :: type&
          collapses( size_t _n ) const
           { return boost::fusion::at< boost::mpl::int_<_index> >(*collapses_)[_n]; }
      //! Returns the number of collapse and separables functions.
      size_t size() const { return collapses_->size(); }
      //! Returns a reference to the mapping.
      t_Mapping& mapping() { return mapping_; }
      //! Returns a constant reference to the mapping.
      const t_Mapping& mapping() const { return mapping_; }
      //! Initializes a collapse with rank and size.
      template< size_t _index > void init( size_t _rank, size_t _dimensions );
      //! Returns a reference to the coefficients.
      t_Coefficients& coefficients() { return coefficients_; }
      //! Returns a constant reference to the coefficients.
      const t_Coefficients& coefficients() const { return coefficients_; }

    public:
      //! Meta-function for rebinding with new traits.
      template< class TT_TRAITS >
      struct rebind
      {
        //! new rebound type.
        typedef Many<TT_TRAITS> type;
      };

    protected:
      //! Returns the number of degrees of liberty for current dimension.
      size_t current_dof() const
       { return 0; } //boost::fusion::accumulate( viewasref(*collapses_), 0, ApplyCurrentDof(dim) ); }
      //! Creates the _A and _b matrices for fitting.
      template< class T_MATRIX, class T_VECTOR >
        void create_A_n_b( T_MATRIX &_A, T_VECTOR &_b );

      //! The container of separable functions.
      boost::shared_ptr< t_VectorsOfSeparables > separables_;
      //! The collapse functor associated with the separable functions.
      boost::shared_ptr< t_VectorsOfCollapses > collapses_;
      //! Current dimension being updated.
      size_t dim;
      //! The mapping to the structures ( e.g. leave-one-out, leave-many-out )
      t_Mapping mapping_;
      //! The coefficienst.
      t_Coefficients coefficients_;

      // metafunctions.
      //! \cond
      struct ApplyDimensions;
      ACC_MFUNC_DECLARE(dof, size_t)
      ACC_MFUNC_DECLARE(nbconfs, size_t)
      struct ApplyCurrentDof;
      VOID_MFUNC_DECLARE(reset);
      template< class T_VECTOR > struct ApplyCreateAnB;
      template< class T_MATRIX, class T_VECTOR > struct ApplyRegularization;
      U_MFUNC_DECLARE( randomize, .randomize(arg), typename t_Vector :: value_type )
      VOID_MFUNC_DECLARE(update_all)
      U_MFUNC_DECLARE( update, .update(arg), const types::t_unsigned& )
      struct ApplyEvaluateOne;
//     U_MFUNC_DECLARE( assign, .dim = arg, types::t_unsigned& )
      template< class T_COEFFICIENTS > struct ApplyResize;
      template< class T_STREAM > struct PrintToStream;
      struct add_ref;
      template< class T > struct ViewAsRef;
      template< class T > ViewAsRef<T> static viewasref( T& _c ) { return ViewAsRef<T>(_c); }
      template< class T > ViewAsRef<const T> static const_viewasref( const T& _c )
        { return ViewAsRef<const T>(_c); }
      //! \endcond
  };

  //! Saves the state of a Many collapse object.
  class ManyState
  {
    public:
      //! Saves a state.
      template< class T_MANY > void operator=( const T_MANY& _many );
      //! Resets a saved state.
      template< class T_MANY > void reset( T_MANY& _many ) const;

    protected:
      //! Coefficients to save.
      typedef boost::numeric::ublas::matrix<types::t_real> t_Coefficients;
      //! Norms to save.
      typedef std::vector< boost::numeric::ublas::vector<types::t_real> > t_Norms;
      //! Coefficients to save.
      t_Coefficients coefficients_;
      //! Norms to save.
      t_Norms norms_;
      //! A meta-function for saving states.
      struct Save;
      //! A meta-function for resetting saved-states.
      struct Reset;
      //! \brief has_norms<T>::value is true(1) if T:::norms exists and fulfills
      //!        some requirements.
      //! \details Concept checks for T::norms.clear(), T::norms.begin(),
      //!          T::norms.end().
      template<class T > struct has_norms;
  };

} // end of CE namespace

#include "many.meta.impl.h"
#include "many.impl.h"
#include "many.macros.h"


#endif
