#include "LaDaConfig.h"

#include <cmath>

#include <Eigen/LU> 

#include <math/misc.h>
#include <math/fuzzy.h>

#include <boost/foreach.hpp>

#include <math/fuzzy.h>
#include "structure.h"
#include "compare_sites.h"
#include "exceptions.h"
#include "utilities.h"


namespace LaDa
{
  namespace crystal 
  {
    //! Returns the primitive unit structure. 
    template<class T_TYPE>
      TemplateStructure<T_TYPE> primitive(TemplateStructure<T_TYPE> const &_structure, types::t_real _tolerance = -1e0)
      {
        if( _tolerance < 0e0 ) _tolerance = types::tolerance;
        if( _structure.size() == 0 ) BOOST_THROW_EXCEPTIONS(error::empty_structure());

        // copies lattice.
        TemplateStructure<T_TYPE> result(_structure.clone());
        bool is_primitive = true;
  
        // moves sites into unit-cell.
        math::rMatrix3d const inv(result.cell.inverse());
        foreach(t_Site &_site, result) _site.pos = into_cell(_site.pos, result.cell, inv);
  
        // Then compares fractional translations from site 0 to sites of same type.
        std::vector<math::rVector3d> translations;
        CompareSites compsites(result.front(), _tolerance);
        t_Sites :: const_iterator i_site = _structure.begin();
        t_Sites :: const_iterator const i_site_end = _structure.end();
        for(; i_site != i_site_end; ++i_site )
        {
          // Translations are created from equivalent sites only.
          if( not compsites(i_site->type) ) continue;
  
          // creates translation.
          math::rVector3d const translation( into_cell(i_site->pos - compsites.pos, result.cell, inv) );
          
          // loop on null translation.
          if( math::is_null(translation) ) continue;
  
          // checks that it leaves the lattice invariant.
          t_Sites :: const_iterator i_mapping = _structure.begin();
          for(; i_mapping != i_site_end; ++i_mapping)
          {
            CompareSites<T_TYPE> check(*i_mapping, _tolerance);
            check.pos = into_cell( i_mapping->pos + translation, result.cell, inv );
  
            if( std::find_if(_structure.begin(), _structure.end(), check)
                  == result.end() ) break;
          }
  
          if( i_mapping != i_site_end ) continue;
  
          // adds translation to vector. This lattice is not primitive.
          translations.push_back( translation );
          is_primitive = false;
        }
  
        // This lattice is primitive.
        if( is_primitive ) return _structure;
  
        // adds original translations.
        translations.push_back( result.cell.col(0) );
        translations.push_back( result.cell.col(1) );
        translations.push_back( result.cell.col(2) );
  
        // Loops over possible primitive cells.
        typedef std::vector<math::rVector3d> :: const_iterator t_cit;
        t_cit const i_vec_begin( translations.begin() );
        t_cit const i_vec_end( translations.end() );
        math::rMatrix3d new_cell = result.cell;
        types::t_real volume = std::abs(new_cell.determinant());
        for( t_cit i_first(i_vec_begin); i_first != i_vec_end; ++i_first )
          for( t_cit i_second(i_vec_begin); i_second != i_vec_end; ++i_second )
          {
            if( i_first == i_second ) continue;
            for( t_cit i_third(i_vec_begin); i_third != i_vec_end; ++i_third )
            {
              if( i_first == i_third or i_second == i_third ) continue;
              // construct new cell.
              math::rMatrix3d trial;
              trial.col(0) = *i_first;
              trial.col(1) = *i_second;
              trial.col(2) = *i_third;
  
              // singular matrix?
              types::t_real const det(trial.determinant());
              if( math::is_null(det) ) continue;
              // Volume smaller than current new_cell?
              if( math::geq(std::abs(det), volume) ) continue;
              // Direct matrix?
              if( det < 0e0 )
              {
                trial.col(2) = *i_second;
                trial.col(1) = *i_third;
                LADA_ASSERT(trial.determinant() > 0, "Shouldn't happen.\n");
              }
              // Checks that original cell is a supercell.
              if( not math::is_integer(new_cell.inverse() * result.cell, _tolerance) ) continue;
  
              // Checks that all lattice sites are integers.
              volume = std::abs(det);
              new_cell = trial;
            }
          }
  
        // Found the new cell with smallest volume (e.g. primivite)
        if(math::eq(_structure.volume, new_cell.determinant()))
          BOOST_THROW_EXCEPTION(
              error::internal() << error::string("Found translation but no primitive cell."));
  
        // now creates new lattice.
        result.clear();
        result.cell = new_cell;
        math::rMatrix3d const inv_cell(result.cell.inverse());
        for(i_site = _structure.begin(); i_site != i_site_end; ++i_site)
        {
          CompareSites<T_TYPE> check(*i_site, _tolerance);
          check.pos = into_cell(check.pos, result.cell, inv_cell);
          t_Sites::const_iterator i_found = std::find_if(result.begin(), result.end(), check);
          if( i_found == sites.end() )
          {
            result.push_back(*i_site);
            result.back().pos = check.pos;
          }
        }
  
        return result;
      }

  } // namespace Crystal

} // namespace LaDa
