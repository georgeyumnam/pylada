#ifdef HAVE_CONFIG_H
# include <config.h>
#endif

#include <algorithm>
#include <functional>

#include <opt/smith_normal_form.h>
#include <crystal/ideal_lattice.h>

#include "vff.h"

namespace LaDa
{
  namespace Vff
  { 
    bool Vff :: build_tree()
    {
      namespace bt = boost::tuples;
      __TRYBEGIN
      __DOASSERT( structure.lattice == NULL, "Lattice not set.\n" )
      __DOASSERT( structure.lattice->sites.size() != 2,
                  "Lattice should contain 2 different sites.\n" )
      const size_t Nsites( structure.lattice->sites.size() );
      const size_t Natoms( structure.atoms.size() );

      // computes deformation.
      // 16 is the number of first+second neighbors. I think.
      const boost::tuples::tuple< Eigen::Matrix3d, Eigen::Vector3d >
        deformation( Crystal::retrieve_deformation( structure, 18 ) );

      // now finds smith normal form of ideal lattice.
      const t_Transformation transformation
      ( 
        to_smith_matrix( deformation, structure.lattice->cell, structure.cell )
      );

      __ASSERT
      ( 
       2 * bt::get<2>(transformation)(0) 
         * bt::get<2>(transformation)(1) 
         * bt::get<2>(transformation)(2)
       != structure.atoms.size(),
            "Number of atoms in real and deformed matrices do not correspond: "
       <<  bt::get<2>(transformation)(0) << " * "
       << bt::get<2>(transformation)(1) << " * " <<  bt::get<2>(transformation)(2) 
       << " * " << Nsites << " = " 
       << (   bt::get<2>(transformation)(0) * bt::get<2>(transformation)(1)
            * bt::get<2>(transformation)(2) * Nsites )
       << " != " 
       <<  structure.atoms.size() << ".\n" 
      )

      // finds ideal first neighbor positions for each lattice sits.
      typedef std::vector< std::vector< Eigen::Vector3d > > t_FirstNeighbors;
      t_FirstNeighbors first_neighbors( Nsites );
      foreach( const Crystal::Lattice::t_Site &site, structure.lattice->sites )
        first_neighbors[0].push_back( site.pos );
      first_neighbors[1] = first_neighbors[0];
      std::swap( first_neighbors[1][0], first_neighbors[1][1] ); 
      
      { // finds first neighbors and adds in deformation.
        const Eigen::Matrix3d inv_def( !bt::get<0>( deformation ) );
        for( size_t i(0); i < Nsites; ++i )
        {
          Crystal::find_first_neighbors( first_neighbors[i], structure.lattice->cell, 4 );
          foreach( Eigen::Vector3d &pos, first_neighbors[i] )
            pos = inv_def * pos; // This way, we can input a single vector to smith_index_
        }
      }
      const types::t_unsigned neighbors_site[2] = { 1, 0 };

      // creates an array indexing each atom.
      types::t_real indices[Nsites][ bt::get<2>(transformation)(0) ]
                                   [ bt::get<2>(transformation)(1) ]
                                   [ bt::get<2>(transformation)(2) ];
      for( size_t i(0); i < Nsites; ++i )
        for( size_t j(0); j < bt::get<2>(transformation)(0); ++j )
          for( size_t k(0); k < bt::get<2>(transformation)(1); ++k )
            for( size_t u(0); u < bt::get<2>(transformation)(2); ++u )
              indices[i][j][k][u] = Natoms;
      {
        size_t index(0);
        bool error = false;
        foreach( const Crystal::Structure::t_Atom &atom, structure.atoms )
        {
          Eigen::Vector3i sindex;
          __ASSERT( atom.site < 0, "site indexing is incorrect.\n" );
          __ASSERT( atom.site > structure.lattice->sites.size(),
                    "site indexing is incorrect.\n" );
          const unsigned site( atom.site );
          smith_index_
          ( 
            transformation,
            atom.pos - structure.lattice->sites[ site ].pos, 
            sindex 
          );
          if( indices[ site ][ sindex(0) ][ sindex(1) ][ sindex(2) ] != Natoms )
          { 
            const size_t i( indices[ site ][ sindex(0) ][ sindex(1) ][ sindex(2) ] );
            std::cerr << "error: " << site << " "
                      << sindex(0) << " " << sindex(1) << " " << sindex(2) << "\n"
                      << i << " " << structure.atoms[i] << "\n"
                      << index << " " << atom << "\n";
            error = true;
          }
          else indices[ site ][ sindex(0) ][ sindex(1) ][ sindex(2) ] = index;
          ++index;
        }
        for( size_t i(0); i < Nsites; ++i )
          for( size_t j(0); j < bt::get<2>(transformation)(0); ++j )
            for( size_t k(0); k < bt::get<2>(transformation)(1); ++k )
              for( size_t u(0); u < bt::get<2>(transformation)(2); ++u )
                if( indices[i][j][k][u] == Natoms )
                {
                  std::cerr << "error: " << i << ", " << j << ", " << k  << ", " << u
                                         << " - could not find all indices.\n";
                  error = true;
                }
        __ASSERT( error,  "Two sites with same smith index.\n" )
      }
      
      // constructs list of centers.
      centers.clear();
      centers.reserve( structure.atoms.size() );
      Crystal::Structure::t_Atoms::iterator i_atom = structure.atoms.begin();
      Crystal::Structure::t_Atoms::iterator i_atom_end = structure.atoms.end();
      for(types::t_unsigned index=0; i_atom != i_atom_end; ++i_atom, ++index )
        centers.push_back( AtomicCenter( structure, *i_atom, index ) );

      // finally builds tree.
      typedef std::vector< Eigen::Vector3d > :: const_iterator t_cit;

      t_Centers :: iterator i_center = centers.begin();
      t_Centers :: iterator i_center_end = centers.end();
      const Eigen::Matrix3d inv_cell( !structure.cell );
      i_atom = structure.atoms.begin();
      for(; i_center != i_center_end; ++i_center, ++i_atom )
      {
        const unsigned center_site( i_atom->site );
        const unsigned neighbor_site( neighbors_site[center_site] );
        const Eigen::Vector3d pos
        ( 
          i_atom->pos - structure.lattice->sites[neighbor_site].pos 
        );
        t_cit i_neigh( first_neighbors[center_site].begin() );
        const t_cit i_neigh_end( first_neighbors[center_site].end() );
        for(; i_neigh != i_neigh_end; ++i_neigh )
        {
          // computes index of nearest neighbor.
          Eigen::Vector3i sindex;
          smith_index_
          (
            transformation,
            pos + (*i_neigh), 
            sindex
          );
          const types::t_int
            cindex( indices[neighbor_site][sindex(0)][sindex(1)][sindex(2)] );
          __DOASSERT( cindex == Natoms, "Index corresponds to no site.\n" )
          // now creates branch in tree.
          t_Centers :: iterator i_bond( centers.begin() + cindex );
          i_center->bonds.push_back( t_Center::__make__iterator__( i_bond ) );
          const Eigen::Vector3d dfrac
          ( 
              inv_cell 
            * ( 
                  (const Eigen::Vector3d) *i_center 
                - (const Eigen::Vector3d) *i_bond
                + (*i_neigh)
              )
           ); 
          const Eigen::Vector3d frac
          (
            rint( dfrac(0) ),
            rint( dfrac(1) ),
            rint( dfrac(2) )
          );
          i_center->translations.push_back( frac );
          i_center->do_translates.push_back( not math::is_zero(frac.squaredNorm()) );
        }
      }
      __ENDGROUP__
      catch( ... )
      {
        std::cerr << "Could not build tree.\n";
        return false;
      }
      return true;
    }

    void Vff :: smith_index_( const t_Transformation &_transformation,
                              const Eigen::Vector3d &_pos,
                              Eigen::Vector3i &_index )
    {
      namespace bt = boost::tuples;
      const Eigen::Vector3d pos
      ( 
        bt::get<0>( _transformation ) * _pos - bt::get<1>( _transformation )
      );
      const Eigen::Vector3i int_pos
      (
        types::t_int( rint( pos(0) ) ),
        types::t_int( rint( pos(1) ) ),
        types::t_int( rint( pos(2) ) )
      );
      for( size_t i(0); i < 3; ++i )
      {
        __DOASSERT
        (
          std::abs( pos(i) - types::t_real( int_pos(i) ) ) > 0.5, 
          "Structure is not ideal.\n"
        )
        _index(i) = int_pos(i) % bt::get<2>(_transformation)(i);
        if( _index(i) < 0 ) _index(i) += bt::get<2>(_transformation)(i);
      }
    }

    Vff :: t_Transformation 
      Vff :: to_smith_matrix( const boost::tuples::tuple
                                    <
                                      Eigen::Matrix3d,
                                      Eigen::Vector3d 
                                    > &_deformation,
                              const Eigen::Matrix3d &_lat_cell,
                              const Eigen::Matrix3d &_str_cell )
      {
        namespace bt = boost::tuples;
        t_Transformation result;
        Eigen::Matrix3i left, right, smith;
        const Eigen::Matrix3d inv_lat( !_lat_cell );
        const Eigen::Matrix3d inv_lat_cell( inv_lat * bt::get<0>(_deformation) * _str_cell );
        Eigen::Matrix3i int_cell;
        for( size_t i(0); i < 3; ++i )
          for( size_t j(0); j < 3; ++j )
          {
            int_cell(i,j) = types::t_int( rint( inv_lat_cell(i,j) ) ); 
            std::cout << rint( inv_lat_cell(i,j) ) << " "
                      << inv_lat_cell(i,j) << " " 
                      << types::t_int( rint( inv_lat_cell(i,j) ) ) << "\n";
//           __DOASSERT
//           ( 
//             std::abs( types::t_real( int_cell(i,j) ) - inv_lat_cell(i,j) ) > 0.01,
//                "Input structure is not supercell of the lattice: \n" 
//             << int_cell << "\n != \n" << inv_lat_cell << "\n\n"
//             << bt::get<0>( _deformation ) <<  "\n\n" << bt::get<1>( _deformation ) << "\n";
//           )
          }
        std::cout << "If your cell (in lattice vectors) is not\n" << int_cell 
                  << "\nthen you have a problem.\n";
        math::smith_normal_form( smith, left, int_cell, right );
        for( size_t i(0); i < 3; ++i )
        {
          for( size_t j(0); j < 3; ++j )
            bt::get<0>( result )(i,j) = types::t_real( left(i,j) );
          bt::get<2>( result )(i) = smith(i,i);
        }
        bt::get<0>( result ) = bt::get<0>( result ) * ( !_lat_cell ) * bt::get<0>(_deformation);
        bt::get<1>( result ) = bt::get<1>( _deformation );
        return result;
      }

  }
}
