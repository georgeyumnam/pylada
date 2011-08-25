#ifndef LADA_CRYSTAL_EQUIVALENT_STRUCTURES_H
#define LADA_CRYSTAL_EQUIVALENT_STRUCTURES_H
#include "LaDaConfig.h"

#include <list>

#include <boost/foreach.hpp>

#include <math/misc.h>
#include <math/fuzzy.h>
#include <math/gruber.h>

#include "structure.h"
#include "utilities.h"
#include "space_group.h"


namespace LaDa
{
  namespace crystal 
  {
    //! \brief Returns true if two lattices are equivalent. 
    //! \details Rotations are taken into account. Hence two lattices need not
    //!          be on the same cartesian basis. A supercell is *not*
    //!          equivalent to its lattice, unless it is a trivial supercell.
    //! \param[in] _a: The first structure.
    //! \param[in] _b: The second structure.
    //! \param[in] with_scale: whether to take the scale into account. Defaults to true.
    //! \param[in] with_invariants: whether to take lattice point-group
    //!            operations into account. These may end-up rotatiting the motif.
    //! \param[in] tolerance: Tolerance when comparing distances. Defaults to
    //!            types::t_real. It is in the same units as the structures scales, if
    //!            that is taken into account, otherwise, it is in the same
    //!            units as _a.scale.
    template<class T_TYPE> 
      bool equivalent( TemplateStructure<T_TYPE> const &_a,
                       TemplateStructure<T_TYPE> const &_b,
                       bool with_scale = true,
                       bool with_invariants = true,
                       types::t_real _tol = types::tolerance )
      {
        // different number of atoms.
        if(_a.size() != _b.size()) return false;
        types::t_real const scaleA = _a.scale();
        types::t_real const scaleB
          = with_scale ?
              _b.scale():
              _a.scale() * std::pow(_a.cell().determinant() / _b.cell().determinant(), 1e0/3e0);
        // different volume.
        if(math::neq( (_a.cell()*scaleA).determinant(),
                      (_b.cell()*scaleB).determinant(), 3e0*_tol)) return false;
        
        // check possible rotation. 
        math::rMatrix3d const cellA = math::gruber(_a.cell(), 100, _tol) * scaleA;
        math::rMatrix3d const cellB = math::gruber(_b.cell(), 100, _tol) * scaleB;
        math::rMatrix3d const invA = cellA.inverse();
        math::rMatrix3d const invB = cellB.inverse();
        math::rMatrix3d const rot = cellA * cellB.inverse();
        if(not math::is_identity(rot * (~rot), 2*_tol)) return false;
        if(math::neq(rot.determinant(), 1e0, 3*_tol))  return false;

        // Now checks atomic sites. 
        // first computes point-group symmetries.
        boost::shared_ptr<t_SpaceGroup> pg;
        if(with_invariants) pg  = cell_invariants(cellA);
        else
        { 
          pg.reset(new t_SpaceGroup(1));
          pg->front() = math::AngleAxis(0, math::rVector3d::UnitX());
        }
        foreach(math::Affine3d const &invariant, *pg)
        {
          // creates a vector referencing B atomic sites.
          // Items from this list will be removed as they are found.
          typedef std::list<size_t> t_List;
          t_List atomsA;
          for(size_t i(0); i < _a.size(); ++i) atomsA.push_back(i);
          math::rVector3d transA(0,0,0);
          foreach(typename TemplateStructure<T_TYPE>::const_reference atomA, _a)
            transA += into_voronoi(atomA.pos * scaleA, cellA, invA);
          transA /= types::t_real(_a.size());
          math::rVector3d transB(0,0,0);
          foreach(typename TemplateStructure<T_TYPE>::const_reference atomB, _b)
            transB += into_voronoi(atomB.pos * scaleB, cellB, invB);
          transB /= types::t_real(_a.size());
          
          math::rMatrix3d const rotation = rot;
          typename TemplateStructure<T_TYPE>::const_iterator i_b = _b.begin();
          typename TemplateStructure<T_TYPE>::const_iterator const i_bend = _b.end();
          for(; i_b != i_bend; ++i_b)
          {
            math::rVector3d const pos = rotation * (into_voronoi(i_b->pos*scaleB, cellB, invB)-transB);
            typename t_List :: iterator i_first =  atomsA.begin();
            typename t_List :: iterator i_end = atomsA.end();
            for(; i_first != i_end; ++i_first)
            {
              if( not math::is_integer(invA * (pos - _a[*i_first].pos*scaleA + transA), 4*_tol) ) continue;
              CompareSites<T_TYPE> const cmp(*i_b, _tol);
              if( cmp(_a[*i_first].type) ) break;
            }
            if(i_first == i_end) break;
            atomsA.erase(i_first);
          }
          if(i_b == i_bend) return true;
        }
        return false;
      }
  } // namespace crystal
} // namespace LaDa
#endif
