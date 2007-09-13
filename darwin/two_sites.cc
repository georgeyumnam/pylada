//
//  Version: $Id$
//
#include <functional>
#include <algorithm>
#include <ext/algorithm>
#include <fstream>
#ifndef __PGI
  #include<ext/functional>
  using __gnu_cxx::compose1;
#else
  #include<functional>
  using std::compose1;
#endif

#include "two_sites.h"
#include "lamarck/atom.h"
#include "opt/compose_functors.h"

namespace TwoSites
{

  void rearrange_structure( Ising_CE::Structure &_str)
  {
    if ( not _str.lattice and _str.lattice->sites.size() != 2)
      return;

    std::list< Ising_CE::Structure::t_Atom > sites0;
    std::list< Ising_CE::Structure::t_Atom > sites1;
    Ising_CE::Structure::t_Atoms :: const_iterator i_atom = _str.atoms.begin();
    Ising_CE::Structure::t_Atoms :: const_iterator i_atom_end = _str.atoms.end();
    for(; i_atom != i_atom_end; ++i_atom )
      ( i_atom->site == 0 ) ?
        sites0.push_back( *i_atom ): sites1.push_back( *i_atom );

    std::list< Ising_CE::Structure::t_Atom > :: iterator i_0 = sites0.begin();
    std::list< Ising_CE::Structure::t_Atom > :: iterator i_end = sites0.end();
    std::list< Ising_CE::Structure::t_Atom > :: iterator i_1;
    atat::rVector3d translation = _str.lattice->sites[1].pos - _str.lattice->sites[0].pos; 
    types::t_real (*ptr_norm)(const atat::FixedVector<types::t_real, 3> &) = &atat::norm2;
    _str.atoms.clear();
    for(; i_0 != i_end; ++i_0 )
    {
      atat::rVector3d atom = i_0->pos + translation;
      i_1 = std::min_element ( sites1.begin(), sites1.end(), 
                      opt::ref_compose2( std::less<types::t_real>(),
                                         compose1( std::ptr_fun(ptr_norm),
                                                   bind2nd(std::minus<atat::rVector3d>(), atom) ),
                                         compose1( std::ptr_fun(ptr_norm),
                                                      bind2nd(std::minus<atat::rVector3d>(), atom) ) ) );
      _str.atoms.push_back( *i_0 ); 
      _str.atoms.push_back( *i_1 ); 
    }

  }

} // namespace pescan


