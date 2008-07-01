//
//  Version: $Id$
//
#ifndef _OPT_ALGORITHMS_H_
#define _OPT_ALGORITHMS_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include<opt/types.h>
#include<opt/debug.h>

namespace opt
{
  template< class T_IT1, class T_IT2, class __APP >
    void concurrent_loop( T_IT1 _first, T_IT1 _last, T_IT2 _second, __APP _app )
    {
      for(; _first != _last; ++_first, ++_second )
        _app( *_first, *_second );
    }
  template< class T_IT1, class T_IT2, class T_IT3, class __APP >
    void concurrent_loop( T_IT1 _first, T_IT1 _last,
                          T_IT2 _second, T_IT3 _third, __APP _app )
    {
      for(; _first != _last; ++_first, ++_second, ++_third )
        _app( *_first, *_second, *_third );
    }

} // end of opt namespace

#endif