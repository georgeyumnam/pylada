//
//  Version: $Id$
//
#ifndef _LADA_GA_BITSTRING_TRANSLATE_H_
#define _LADA_GA_BITSTRING_TRANSLATE_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <string>
#include <ostream>

namespace LaDa
{
  namespace GA
  {
    namespace BitString
    {
      //! Policy to translate an object containing a vector of 1:0 values to a structure.
      template< class T_OBJECT >
        struct Translate
        {
          //! Type of the Object.
          typedef T_OBJECT t_Object;
          //! From Crystal::Structure to objects.
          static void translate( const t_Object&, std :: string& );
          //! From Crystal::Structure to objects.
          static void translate( const std::string&, t_Object& );
        };

      template< class T_OBJECT >
        void Translate<T_OBJECT> :: translate( const std::string& _string, 
                                               t_Object& _object ) 
        {
          typedef typename t_Object :: t_Container :: iterator t_ivar;
          std::istringstream sstr( _string );
          t_ivar i_var = _object.Container().begin();
          __DODEBUGCODE( t_ivar i_var_end = _object.Container().end(); )
          do
          {
            __ASSERT( i_var == i_var_end, "Object smaller than string.\n" )
            sstr >> *i_var;
            ++i_var;
          }
          while( not sstr.eof() );
          __ASSERT( i_var != i_var_end, "String smaller than object.\n" )
        }

      template< class T_OBJECT >
        void Translate<T_OBJECT> :: translate( const t_Object& _object,
                                               std::string &_string ) 
        {
          typedef typename t_Object :: t_Container :: const_iterator t_ivar;
          std::ostringstream sstr( _string );
          t_ivar i_var = _object.Container().begin();
          t_ivar i_var_end = _object.Container().end();
          for(; i_var != i_var_end; ++i_var ) sstr << (*i_var) << " ";
          _string = sstr.str(); 
        }

    } // namespace GroundStates.
  } // namespace GA
} // namespace LaDa 
#endif
