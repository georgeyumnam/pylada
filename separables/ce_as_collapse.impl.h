#include <ce/fit.h>

namespace LaDa
{
  //! \cond
  namespace Traits
  {
    namespace CE
    {
      namespace details
      {
        template< class T_MAPPING, class T_POLICY, 
                  class T_COEFFICIENTS, class T_VECTOR, class T_FIT >
            struct CEasSeparables
            {
              //! Type of mapping.
              typedef T_MAPPING t_Mapping;
              //! Type of policy.
              typedef T_POLICY t_Policy;
              //! Type of the coefficient interface.
              typedef T_COEFFICIENTS t_Coefficients;
              //! Type of matrix.
              typedef typename t_Coefficients :: t_Matrix t_Matrix;
              //! Type of vector.
              typedef T_VECTOR t_Vector;
              //! Allows rebinding of the separables function traits.
              template< class TT_MAPPING, class TT_POLICY, 
                        class TT_COEFFICIENTS, class TT_VECTOR >
               struct rebind
               {
                 //! new type.
                 typedef CEasSeparables< TT_MAPPING, TT_POLICY,
                                         TT_COEFFICIENTS, TT_VECTOR, T_FIT > type;
               };
            };
      }
    }
  }
  //! \endcond

  namespace CE
  {
    template< class T_TRAITS > void CEasCollapse<T_TRAITS> :: reassign()
    {
      namespace bl = boost::lambda;
      __DEBUGTRYBEGIN
      __ASSERT( coefficients().size1() != clusters_->size(), "Inconsistent sizes.\n")
   
      typename t_Coefficients :: t_Matrix 
                              :: const_iterator1 i_eci = coefficients().begin1();
      foreach( typename t_Clusters::value_type & _clusters, *clusters_ )
      {
        foreach( ::CE::Cluster & _cluster, _clusters ) _cluster.eci = *i_eci;
        ++i_eci;
      }
      __DEBUGTRYEND(,"Error in CEasCollapse::reassign().\n" )
    }
    template< class T_TRAITS >
      void CEasCollapse<T_TRAITS>
        :: randomize( typename t_Matrix :: value_type _howrandom )
        {
          typename t_Matrix :: iterator1 i_c = coefficients().begin1();
          typename t_Matrix :: iterator1 i_c_end = coefficients().end1();
          typedef typename t_Matrix :: value_type t_Type;
          for(; i_c != i_c_end; ++i_c )
            *i_c = t_Type( opt::math::rng() - 5e-1 ) * _howrandom;
        }
    template< class T_TRAITS > template< class T_CLUSTERS >
      void CEasCollapse<T_TRAITS> :: init( const T_CLUSTERS &_clusters )
      {
        std::copy( _clusters.begin(), _clusters.end(),
                   std::back_inserter( *clusters_ ) );
        cefit().init( *clusters_ );
      }

    template< class T_TRAITS > 
      typename CEasCollapse<T_TRAITS> :: t_Matrix :: value_type 
        CEasCollapse<T_TRAITS> :: evaluate( size_t _n ) const
        {
          namespace bblas = boost::numeric::ublas;
          const bblas::matrix_column< const t_Matrix > column( coefficients(), 0 );
          return bblas::inner_prod( column, cefit().pis[ _n ] ); 
        }
    namespace details
    {
      //! \brief Wrapper around CE::RegulatedFit regularization.
      template< class T_CEFIT > 
      class Regularization
      {
        public:
          //! Helps to obtain a differently typed regularization.
          template< class TT_CEFIT > struct rebind
          { 
            //! Type of the regularization policy.
            typedef Regularization< TT_CEFIT > type;
          };
          //! Type of the separable function.
          typedef T_CEFIT t_CEFit;

          //! Constructor
          Regularization() : cefit_(NULL) {};
          //! Copy Constructor.
          template <class TT_CEFIT> 
            Regularization   ( const Regularization<T_CEFIT> &_c )
                           : cefit_( _c.cefit_ ) {};

          //! Would modify A matrix and b vector.
          template< class T_MATRIX, class T_VECTOR >
            void operator()( T_MATRIX &_m, T_VECTOR &_v, size_t _dim ) const
            {
              __ASSERT( cefit_ == NULL, "null pointer.\n" )
              if( _dim == 1 ) cefit_->other_A_n_b( _m, _v ); 
            };

          //! Initializes pointer.
          void init( const t_CEFit &_fit ) { cefit_ = &_fit; }

        protected:
          //! Pointer to regularization functor.
          const t_CEFit* cefit_;
      };
    }
  } // end of CE namespace
} // namespace LaDa