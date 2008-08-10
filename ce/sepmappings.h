//
//  Version: $Id$
//
#ifndef _CE_SEPMAPPINGS_H_
#define _CE_SEPMAPPINGS_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <opt/types.h>
#include <opt/debug.h>

namespace CE
{
  //! Contains mapping policies for fixed-lattice separable functions.
  namespace Mapping
  {
    //! \brief Allows different types of mapping from confs to coef parameters.
    //! \detail This mapping is equivalent to VectorPlus, eg (1,0..), (0,1,....),
    //!          and so on.
    template< size_t DIM > class VectorPlus 
    {
      public:
        //! A D dimensional mapping.
        const static size_t D = DIM;
        //! Applies function itself.
        template< class T_CONF, class T_ITCOEF, clas T_OUT >
          const static void apply( const T_CONF &_conf,
                                   const T_ITCOEF &_coef, 
                                   T_OUT &_out )
            { _out *= *( _coef + typename T_ITCOEF::difference_type( _conf ) ); }
        //! Returns the normalized, coef-less vector.
        template< class T_CONF, class T_OUT >
          const static void add_tovec( const T_CONF &_conf, T_OUT &_out, 
                                       typename T_OUT::value_type _s  
                                           = typename T_OUT::value_type(1) )
          { _out[ size_t( _conf ) ] += typename T_OUT::value_type(_s); }
    };
    //! \brief Allows different types of mapping from confs to coef parameters.
    //! \detail This mapping is equivalent to VectorPlus, eg (1,0) and (0,1),
    //!         specialized for two species.
    template<> class VectorPlus<2>
    {
      public:
        //! A D dimensional mapping.
        const static size_t D = 2;
        //! Applies function itself.
        template< class T_CONF, class T_ITCOEF, class T_OUT >
          const static void apply( const T_CONF &_conf,
                                   const T_ITCOEF &_coef, 
                                   T_OUT &_out )
          {
            typedef T_ITCOEF :: difference_type t_difftype;
            _out *= *( _coef + _conf > T_CONF(0) ? t_difftype(1): t_difftype(0) );
          }
        //! Returns the normalized, coef-less vector.
        template< class T_CONF, class T_OUT >
          const static void add_tovec( const T_CONF &_conf, T_OUT &_out, 
                                       const typename T_OUT::value_type _s 
                                               = typename T_OUT::value_type(1) )
          { _out[_conf > T_CONF(0) ? 1:0] +=  typename T_OUT::value_type(_s); }
    };
    //! \brief Allows different types of mapping from confs to coef parameters.
    //! \detail This mapping is equivalent to VectorPlus, with one constant
    //!         vector, and all other vectors with a single non-zero component.
    template< size_t DIM > class VectorDiff
    {
      public:
        //! A D dimensional mapping.
        const static size_t D = DIM;
        //! Applies functions with appropriate coef.
        template< class T_CONF, class T_ITCOEF, clas T_OUT >
          const static void apply( const T_CONF &_conf,
                                   const T_ITCOEF &_coef, 
                                   T_OUT &_out )
          {
            _out *= *_coef:
            if( Fuzzy::is_zero( _conf ) ) return;
            _out *= *( _coef + typename T_ITCOEF::difference_type( _conf ) );
          }
        //! Returns the normalized, coef-less vector.
        template< class T_CONF, class T_OUT >
          const static void add_tovec( const T_CONF &_conf, T_OUT &_out, 
                                       const typename T_OUT::value_type _s 
                                               = typename T_OUT::value_type(1) )
          {
            _out[0] += typename T_OUT::value_type(_s);
            if( Fuzzy::is_zero( _conf ) ) return;
            _out[ size_t( _conf ) ] +=  typename T_OUT::value_type(_s); 
          }
    };
    //! \brief Allows different types of mapping from confs to coef parameters.
    //! \detail This mapping is equivalent to VectorPlus, with one constant
    //!         vector, and all other vectors with a single non-zero component.
    //!         This version is specialized for two species.
    template<> class VectorDiff<2>
    {
      public:
        //! A D dimensional mapping.
        const static size_t D = 2;
        //! Applies function itself.
        template< class T_CONF, class T_ITCOEF, clas T_OUT >
          const static void apply( const T_CONF &_conf,
                                   const T_ITCOEF &_coef, 
                                   T_OUT &_out )
          {
            Fuzzy::geq( _conf, T_CONF(0) ) ? _out *= *_coef: 
                                             _out *= *_coef + *(_coef+1);
          }
        //! Returns the normalized, coef-less vector.
        template< class T_CONF, class T_OUT >
          const static void add_tovec( const T_CONF &_conf, T_OUT &_out, 
                                       const typename T_OUT::value_type _s 
                                               = typename T_OUT::value_type(1) )
          {
            _out[0] += typename T_OUT::value_type(_s);
            if( Fuzzy::geq( _conf, T_CONF(0) ) ) return;
            _out[ 1 ] +=  typename T_OUT::value_type(_s); 
          }
    };
  } // end of Mapping namespace.
} // end of CE namespace.
#endif