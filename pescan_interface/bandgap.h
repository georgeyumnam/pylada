//
//  Version: $Id$
//
#ifndef _PESCAN_BANDGAP_H_
#define _PESCAN_BANDGAP_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#ifdef _MPI
#include <mpi/mpi_object.h>
#endif

#include <lamarck/structure.h>

#include "interface.h"

namespace Pescan 
{

  //! Keeps track of the HOMO and LUMO
  struct Bands
  { 
    types::t_real cbm;  //!< Conduction Band Minimum
    types::t_real vbm;  //!< Valence Band minimum
    Bands() : cbm(0), vbm(0) {}; //!< Constructor
    //! Constructor and Initializer
    Bands( const types :: t_real _cbm, types::t_real _vbm ) : cbm(_cbm), vbm(_vbm) {};
    //! Copy Constructor.
    Bands( const Bands &_bands ) : cbm(_bands.cbm), vbm(_bands.vbm) {};
    //! Returns the gap.
    types::t_real gap() const { return cbm - vbm; }
  };

  class BandGap : public Interface
  {
    protected:
      //! For folded spectrum, whcih band is being computed.
      enum t_computation
      { 
        VBM,  //!< Valence Band Maximum is being computed.
        CBM   //!< Conduction Band Minimum is being computed.
      };

    public:
      //! Stores results
      Bands bands;
      //! Reference energy for folded spectrum method
      Bands Eref;

    protected:
      //! For folded spectrum, which computation (VBM or CBM) is being performed.
      t_computation computation;
      //! Wether to apply correction scheme when metallic band-gap is found
      bool do_correct;

    public:
      //! Constructor
      BandGap() : bands(0,0), Eref(0,0), computation( CBM ), do_correct(true) {}
      //! Copy Constructor
      BandGap   ( const BandGap & _c ) 
              : Interface( _c ), bands( _c.bands ), Eref( _c.Eref ),
                computation( CBM ), do_correct( _c.do_correct ) {} 
      //! Destructor
      ~BandGap() {};


      //! \brief Loads all parameters from XML.
      //! \details Adds band-gap references
      bool Load( const TiXmlElement &_node );

      //! Launches a calculation for structure \a _str
      types::t_real operator()( const Ising_CE::Structure &_str ); 

    protected:
      types::t_real folded_spectrum();
      types::t_real all_electron( const Ising_CE::Structure &_str );
      types::t_real find_closest_eig( types::t_real _ref );
      void correct( const std::string &_dir );
  };

  inline types::t_real BandGap :: operator()( const Ising_CE::Structure &_str )
  {
    escan.scale = _str.scale;

    return escan.method == ALL_ELECTRON ? all_electron( _str ): folded_spectrum();
  }

  inline types::t_real BandGap :: find_closest_eig( types::t_real _ref )
  {
    std::vector<types::t_real> :: const_iterator i_eig = eigenvalues.begin();
    std::vector<types::t_real> :: const_iterator i_eig_end = eigenvalues.end();
    std::vector<types::t_real> :: const_iterator i_eig_result = i_eig;
    types::t_real mini = std::abs(*i_eig-_ref); 
    for(++i_eig; i_eig != i_eig_end; ++i_eig)
      if( std::abs( *i_eig - _ref ) < mini )
      {
        mini = std::abs( *i_eig - _ref );
        i_eig_result = i_eig;
      }
    return *i_eig_result;
  }

} // namespace Pescan

#endif // _PESCAN_BANDGAP_H_