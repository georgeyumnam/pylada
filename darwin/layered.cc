//
//  Version: $Id: layered.impl.h 333 2007-10-21 19:12:32Z davezac $
//

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <stdexcept>       // std::runtime_error

#include <functional>
#ifndef __PGI
  #include<ext/functional>
  using __gnu_cxx::compose1;
#else
  #include<functional>
  using std::compose1;
#endif


#include <lamarck/structure.h>
#include <lamarck/atom.h>

#include <opt/types.h>
#include <atat/vectmac.h>
#include <opt/ndim_iterator.h>
#include <opt/traits.h>


void FillStructure( Ising_CE::Structure &_str )
{
  if( not _str.lattice ) return;
  
  atat::rVector3d vec;
  atat::rMatrix3d &cell = _str.cell; 
  Ising_CE::Lattice &lattice = *_str.lattice; 

  // Construct the transition matrix from the lattice basis to this cell-shape basis
  atat::rMatrix3d M = (!cell) * lattice.cell;
  // The next few operations should tell us the maximum range of the structure
  // cell int terms of the lattice cell.
  types::t_real bull=0.0;
  for( types::t_unsigned i = 0; i < 3; ++i )
    for( types::t_unsigned j = 0; j < 3; ++j )
      if( Traits::Fuzzy<types::t_real>::equal( M(i,j), 0 ) ) continue;
      else if ( Traits::Fuzzy<types::t_real>::less( bull, 1.0 / std::abs(M(i,j)) ) )
        bull = 1.0 / std::abs(M(i,j));
  types::t_int amax = (types::t_int) std::ceil( bull );

  // now that we have the range, we can fully explore the region
  // sets up the n-dimensional iterators
  atat::iVector3d range;
  Ising_CE::find_range( M, range );
  opt::Ndim_Iterator< types::t_int, std::less_equal<types::t_int> > global_iterator;
  global_iterator.add( -range[0], range[0]);
  global_iterator.add( -range[1], range[1]);
  global_iterator.add( -range[2], range[2]);

  
  _str.atoms.clear();
  do
  {
    // creates vector in lattice basis
    vec[0] =  (types::t_real) global_iterator.access(0);
    vec[1] =  (types::t_real) global_iterator.access(1);
    vec[2] =  (types::t_real) global_iterator.access(2);
    // Transforms vec to fractional coordinates in current cell-shape
    vec = M * vec;
    // if any of the coordinates is >= 1, then this is a periodic image
    if (    Traits::Fuzzy<types::t_real>::geq( vec(0), 1.0 ) 
         or Traits::Fuzzy<types::t_real>::geq( vec(1), 1.0 ) 
         or Traits::Fuzzy<types::t_real>::geq( vec(2), 1.0 ) ) continue;
    // if any of the coordinates is < 0, then this is a periodic image
    if (    Traits::Fuzzy<types::t_real>::less( vec(0), 0.0 ) 
         or Traits::Fuzzy<types::t_real>::less( vec(1), 0.0 ) 
         or Traits::Fuzzy<types::t_real>::less( vec(2), 0.0 ) ) continue;


    // Goes back to lattice basis
    vec[0] =  (types::t_real) global_iterator.access(0);
    vec[1] =  (types::t_real) global_iterator.access(1);
    vec[2] =  (types::t_real) global_iterator.access(2);
    // And then to cartesian
    vec = lattice.cell * vec;

    _str.atoms.push_back( Ising_CE::Structure::t_Atom(vec,0) );
    
  } while( ++global_iterator );

}
