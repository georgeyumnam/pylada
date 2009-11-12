//
//  Version: $Id$
//
#ifndef LADA_OPT_POW_H_
#define LADA_OPT_POW_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <boost/utility/enable_if.hpp>
#include <boost/type_traits/is_integral.hpp>

namespace LaDa
{
  namespace opt
  {
    template<class T>
      typename boost::enable_if< boost::is_integral<T>, T> :: type
        pow(T base, T power)
        {
          if (power == 0) return 1;
          if (power == 1) return base;
          if (power % 2 == 0) return opt::pow(base * base, power >> 1 );
          if (power % 2 == 1) return base * opt::pow(base * base, power >> 1 );
        }
  }
}

#endif