//
//  Version: $Id$
//
#ifndef _VFF_VA_H_
#define _VFF_VA_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include "functional.h"

#include <opt/gsl_minimizers.h>

#ifdef _MPI 
  #include "mpi/mpi_object.h"
#endif

namespace Vff
{

  //! \brief Implements a Virtual Atom functional around Vff::Functional.
  //! \details In other words, this functional is capable of returning the
  //!          gradient with respect to a change in the atomic occupation
  //!          within the structure. It should interact quite well with
  //!          Minimizer::VA and Minimizer::Beratan,
  class VirtualAtom : public Functional
  {
     protected:
       //! Type from which the VA functional is derived
       typedef Functional t_Base;

     public:
       //! see functional::Base::t_Type
       typedef types::t_real t_Type;
       //! see functional::Base::t_Container
       typedef std::vector< t_Type >  t_Container;
       //! Type of the minimizer for minimizing strain
       typedef Minimizer::GnuSL<t_Base> t_Minimizer;

     protected:
       t_Container va_vars;
       t_Minimizer minimizer;

     public:
       //! Constructor and Initializer
       VirtualAtom   ( Ising_CE::Structure &_str )
                   : t_Base( _str ), minimizer( *this )
        { va_vars.reserve( _str.atoms.size() ); }
       //! Copy Constructor
       VirtualAtom   ( const VirtualAtom &_c )
                   : t_Base( _c ), minimizer( *this ), va_vars( _c.va_vars ) {}
        
       //! Loads the vff's and the minimizer's parameters from XML
       bool Load( const TiXmlElement &_node );

       // Simple constainer behaviors required by Minimizer::VA and
       // Minimizer::Beratan

       //! Returns the size of VirtualAtom::va_vars.
       types::t_unsigned size() const { return va_vars.size(); }
       //! Returns an iterator to the first \e virtual variable (atomic occupation).
       t_Container::iterator begin() { return va_vars.begin(); }
       //! \brief Returns an iterator to one past the last \e virtual variable
       //!        (atomic occupation).
       t_Container::iterator end() { return va_vars.end(); }
       //! \brief Returns a constant iterator to the first \e virtual variable
       //!        (atomic occupation).
       t_Container::const_iterator begin() const { return va_vars.begin(); }
       //! \brief Returns a constant iterator to one past the last \e virtual
       //!        variable (atomic occupation).
       t_Container::const_iterator end() const { return va_vars.end(); }

       // Now truly "functional" stuff.
       
       //! Initializes the variables with respect to Functional::structure.
       bool init();
       //! \brief Evaluated the strain after copying the occupations from
       //!        VirtualAtom::va_vars.
       t_Type evaluate();
       //! Returns the \e virtual gradient in direction \a _pos
       t_Type evaluate_one_gradient( types::t_unsigned _pos );
       //! Computes the \e virtual gradients and returns the energy
       t_Type evaluate_with_gradient( t_Type* _grad );
       //! Computes the \e virtual gradients
       void evaluate_gradient( t_Type* _grad );

     protected:
       //! Transfers occupations from VirtualAtom::va_vars to Functional::structure.
       void unpack_variables();
  };

} // namespace vff 

#endif // _VFF_FUNCTIONAL_H_
