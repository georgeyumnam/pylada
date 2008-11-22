//
//  Version: $Id$
//
#ifndef _LADA_GA_BITSTRING_CROSSOVER_H_
#define _LADA_GA_BITSTRING_CROSSOVER_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include<boost/bind.hpp>

#include <opt/types.h>
#include <print/xmg.h>

#include "../operators/make_populator.h"

namespace LaDa
{
  namespace GA
  {
    namespace GroundStates
    {
      //! Performs a bitstring crossover.
      template< class T_OBJECT >
        bool krossover( T_OBJECT& _o, const T_OBJECT &_p, types::t_real &_rate, bool do_range,
                        const Crystal :: Structure& _structure,
                        const boost::function< void( Structure& )>& _concentration )
        {
          typedef typename T_OBJECT t_Object;
          Crystal::Structure str1 = structure, str2 = structure;
          str1 << _o; str2 << _p;
          Crystal::Fourier( str1.atoms.begin(),  str1.atoms.end(),
                            str1.k_vecs.begin(), str1.k_vecs.end() );
          Crystal::Fourier( str2.atoms.begin(),  str2.atoms.end(),
                            str2.k_vecs.begin(), str2.k_vecs.end() );
          
          // range crossover ... kvec should be oredered according to size
          if ( do_range and str1.k_vecs.size() > 2 ) 
          {  
            types::t_unsigned n = (types::t_unsigned)
               std::floor(   (types::t_real) rng.random ( str1.k_vecs.size() - 1 ) 
                           * (types::t_real) rate );
            std::copy( str2.k_vecs.begin(), str2.k_vecs.begin() + n, str1.k_vecs.begin() );
          }
          else // every point crossover
          {
            Crystal::Structure::t_kAtoms :: const_iterator i_p = str2.k_vecs.begin();
            Crystal::Structure::t_kAtoms :: const_iterator i_p_end = str2.k_vecs.end();
            Crystal::Structure::t_kAtoms :: iterator i_o = str1.k_vecs.begin();
            for ( ; i_p != i_p_end; ++i_p, ++i_o)
              if ( rng.flip(rate) )  i_o->type = i_p->type;
          }
          if( not _concentration.empty() ) _concentration( str1 );
          
          _o << str1;
          
          return true;
        }

      template< class T_FACTORY >
        void krossover_factory( T_FACTORY &_factory,
                                boost::function<void( typename T_FACTORY::t_Populator& )>&
                                  _function,
                                const TiXmlElement &_node, const Crystal::Structure* _structure )
        {
          typedef typename T_FACTORY :: t_Individual t_Individual;
          typedef typename T_FACTORY :: t_Populator t_Populator;
          typedef typename t_Individual :: t_IndivTraits :: t_Object t_Object;
          types::t_real rate(5e-1);
          if( _node.Attribute( "rate" ) )
            rate = boost::lexical_cast<types::t_real>( _node.Attribute("rate") );
          bool do_range( false );
          if( _node.Attributae( "dorange" ) ) do_range = true;
          if( Fuzzy::leq( rate, 0e0 ) or Fuzzy::geq( rate, 1e0 ) ) rate = 5e-1;
          Operator::MakePopulator<t_Individual, t_Populator>::transform_binary
          ( 
            boost::bind( &krossover<t_Individual>, _1, _2, rate, do_range,
                         boost::ref( _structure ),
                         boost::function<void( Crystal::Structure& )>() ),
            _function 
          );
          if( do_range )
            Print::xmg << Print::Xmg::comment << "Krossover over range with rate="
                       << rate << Print::endl;
          else 
            Print::xmg << Print::Xmg::comment << "Krossover with rate="
                       << rate << Print::endl;
        }
    } // namespace AlloyLayers
  } // namespace GA
} // namespace LaDa
#endif
