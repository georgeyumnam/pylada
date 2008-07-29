//
//  Version: $Id$
//

#include <boost/filesystem/operations.hpp>
#include <boost/filesystem/path.hpp>
#include <boost/lambda/bind.hpp>

#include<opt/algorithms.h>

namespace CE
{
  template< class T_CLUSTERS, class T_PIS >
  void find_pis( const T_CLUSTERS &_clusters,
                 const Crystal::Structure & _str,
                 T_PIS &_pis )
  {
    namespace bl = boost::lambda;
    typedef T_CLUSTERS  t_Clusters;
    typedef typename t_Clusters :: value_type t_EClusters;
    typedef T_PIS t_Pis;

    _pis.resize( _clusters.size() );
    std::fill( _pis.begin(), _pis.end(), 0 );

    atat::rMatrix3d inv_cell = !(~_str.cell);
    Crystal :: Structure :: t_Atoms :: const_iterator i_atom = _str.atoms.begin();
    Crystal :: Structure :: t_Atoms :: const_iterator i_atom_end = _str.atoms.end();
    for(; i_atom != i_atom_end; ++i_atom) // loop over atoms
    {
      // loop over classes of clusters.
      typename t_Clusters :: const_iterator i_clusters = _clusters.begin();
      typename t_Clusters :: const_iterator i_clusters_end = _clusters.end();
      typename t_Pis :: iterator i_pi = _pis.begin();
      for( size_t i(0) ; i_clusters != i_clusters_end; ++i_clusters, ++i_pi, ++i ) 
      {
        __ASSERT( i_clusters->size() == 0, "Cluster class is empty.\n" );
        if( not i_clusters->front().vectors.size() )
          { *i_pi = 1; continue; }
        typename t_EClusters :: const_iterator i_cluster = i_clusters->begin();
        typename t_EClusters :: const_iterator i_cluster_end = i_clusters->end();
        // loop over equivalent clusters.
        for( ; i_cluster != i_cluster_end; ++i_cluster )
        {
          // loop over cluster origin.
          typedef std::vector<atat::rVector3d> :: const_iterator vec_iterator;
          vec_iterator i_cpos_begin = i_cluster->vectors.begin();
          vec_iterator i_cpos_center = i_cluster->vectors.begin();
          vec_iterator i_cpos_end = i_cluster->vectors.end();
          vec_iterator i_cpos;
          for (; i_cpos_center != i_cpos_end; ++i_cpos_center ) 
          {   
            // loop over lattice positions in cluster.
            types::t_int result(1);
            for ( i_cpos = i_cpos_begin; i_cpos != i_cpos_end; ++i_cpos )
            {
              atat::rVector3d shift = i_atom->pos - *i_cpos_center;
              
              if ( not is_int( (!_str.lattice->cell)*shift) ) continue;
              
              // finds atom to which lattice site is equivalent
             types::t_int (*ptr_func)( const atat::rVector3d &a,
                                       const atat::rVector3d &b,
                                       const atat::rMatrix3d &inv_cell);
             ptr_func = &atat::equivalent_mod_cell;
              Crystal::Structure::t_Atoms::const_iterator
                i_equiv = std::find_if
                          (
                            _str.atoms.begin(), i_atom_end,
                            bl::bind
                            ( 
                              ptr_func, 
                              *i_cpos + shift, 
                              bl::bind( &Crystal::Structure::t_Atom::pos, bl::_1 ),
                              inv_cell
                            )
                          );
              
              __ASSERT( i_equiv == i_atom_end,
                        "Could not find equivalent site.\n" )
              result *= i_equiv->type > 0e0 ? 1: -1;

            }  // end of loop over cluster points
            *i_pi += result;
          } // end of rotation
        }  // end of loop over equivalent clusters
        *i_pi /= (types::t_real) i_clusters->front().vectors.size();
      } // end of loop over cluster classes.
    }  // end of loop over atoms 
  }

  template< class T_CLUSTERS, class T_PIS >
  void find_pis( const T_CLUSTERS &_clusters,
                 const std::vector< Crystal::Structure > & _str,
                 T_PIS &_pis )
  {
    namespace bl = boost::lambda;
    typedef typename T_PIS::value_type t_Pis;
    _pis.resize( _str.size() );
    void (*ptr_func)( const T_CLUSTERS &, const Crystal::Structure &, t_Pis & );
    ptr_func = &find_pis<T_CLUSTERS, t_Pis>;
    opt::concurrent_loop
    (
      _str.begin(), _str.end(), _pis.begin(),
      bl::bind( ptr_func, bl::constant( _clusters ), bl::_1, bl::_2 )
    );
  }

} // end of namespace CE

