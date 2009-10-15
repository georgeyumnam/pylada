//
//  Version: $Id$
//
#ifndef LADA_CRYSTAL_SYMMETRY_OPERATOR_H_
#define LADA_CRYSTAL_SYMMETRY_OPERATOR_H_

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <vector>
#include <iostream>

#include <boost/shared_ptr.hpp>

#include <opt/debug.h>
#include <opt/types.h>
#include <opt/fuzzy.h>
#include <atat/vectmac.h>
#include <atat/findsym.h>


namespace LaDa
{
  namespace Crystal 
  {
    //! \cond
    class Lattice;
    //! \endcond
    

    //! A symmetry operator.
    struct SymmetryOperator
    {
      //! Constructor.
      SymmetryOperator() : trans(0,0,0) { op.zero(); op(0,0)=1e0; op(1,1)=1e0; op(2,2)=1e0; }
      //! Constructor.
      SymmetryOperator   ( atat::rMatrix3d const &_op,
                           atat::rVector3d const& _t = atat::rVector3d(0,0,0) )
                       : op(_op), trans(_t) {}
      //! Constructor.
      SymmetryOperator   ( atat::rVector3d const& _t)
                       : trans(_t) { op.zero(); op(0,0)=1e0; op(1,1)=1e0; op(2,2)=1e0; }
      //! Copy Constructor.
      SymmetryOperator( SymmetryOperator const& _c ) : op(_c.op), trans(_c.trans) {}

      //! Matrix operator.
      atat::rMatrix3d op;
      //! Vector translation
      atat::rVector3d trans;
      //! Applies operator.
      atat::rVector3d operator()( atat::rVector3d const &_a ) const
        { return op*_a + trans; }

      //! True if the matrix is invariant by this operator.
      bool invariant(atat::rMatrix3d const &_mat, types::t_real _tolerance = types::tolerance) const;
      //! Comparison.
      bool operator==(SymmetryOperator const &_sym)
      {
        return not(    Fuzzy::neq(op(0,0), _sym.op(0,0))
                    or Fuzzy::neq(op(1,0), _sym.op(1,0))
                    or Fuzzy::neq(op(2,0), _sym.op(2,0))
                    or Fuzzy::neq(op(0,1), _sym.op(0,1))
                    or Fuzzy::neq(op(1,1), _sym.op(1,1)) 
                    or Fuzzy::neq(op(2,1), _sym.op(2,1))
                    or Fuzzy::neq(op(0,2), _sym.op(0,2)) 
                    or Fuzzy::neq(op(1,2), _sym.op(1,2))
                    or Fuzzy::neq(op(2,2), _sym.op(2,2)) 
                    or Fuzzy::neq(trans.x[0], _sym.trans[0])
                    or Fuzzy::neq(trans.x[1], _sym.trans[1]) 
                    or Fuzzy::neq(trans.x[2], _sym.trans[2]) );
      }
    };

    inline std::ostream& operator<<( std::ostream& _stream, SymmetryOperator const &_sym )
    {
      return _stream << "Trans: " << _sym.trans << "\n" << _sym.op << "\n"; 
    }
    //! \brief Composes two symmetry operations.
    //! \details \a _out.op = \a _a.op * _\a b.op, \a _out.trans = _a.trans + _a.op * _b.trans.
    void compose( SymmetryOperator const &_a,
                  SymmetryOperator const &_b, 
                  SymmetryOperator &_out );


    //! \brief Returns point symmetries of a cell (except identity).
    //! \details Rotations are determined from G-vector triplets with the same
    //!          norm as the unit-cell vectors.
    //! \see Taken from Enum code, PRB 77, 224115 (2008).
    boost::shared_ptr< std::vector<SymmetryOperator> >
      get_point_group_symmetries( atat::rMatrix3d const &_cell, types::t_real _tolerance = -1e0 );

    //! \brief returns space-group symmetries of a lattice.
    //! \warning Works for primitive lattices only.
    //! \see Taken from Enum code, PRB 77, 224115 (2008).
    boost::shared_ptr< std::vector<SymmetryOperator> >
      get_space_group_symmetries( Lattice const &_lattice, types::t_real _tolerance = -1e0 );
  }
}

#endif
