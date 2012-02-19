#include "LaDaConfig.h"
#include<iostream>
#include<string>
#include<vector>

#include <opt/debug.h>
#include "../supercell.h"
#include "../primitive.h"

#if LADA_INCREMENT == 0
#  define LADA_INIT 
#elif LADA_INCREMENT == 1
#  define LADA_INIT , "Si"
#elif LADA_INCREMENT == 2
#  define LADA_INIT , "Si"
#endif

using namespace std;
int main()
{
  using namespace LaDa;
  using namespace LaDa::crystal;
  using namespace LaDa::math;
  typedef Structure< LADA_TYPE > t_Str; 
  Structure< LADA_TYPE > lattice, lat; 
  lattice.set_cell(0,0.5,0.5)
                  (0.5,0,0.5)
                  (0.5,0.5,0);
  lattice.add_atom(0,0,0, "Si")
                  (0.25,0.25,0.25, "Ge" LADA_INIT);
  lat.set_cell(0,0.5,0.5)
              (0.5,0,0.5)
              (0.5,0.5,0);
  lat.add_atom(0,0,0, "Si")
              (0.25,0.25,0.25, "Si");
  rMatrix3d cell = rMatrix3d::Zero();

  size_t nmax= LADA_LIM;
  bool cont = true;
  for(size_t a(1); a <= nmax and cont; ++a)
  {
    if(nmax % a != 0) continue;
    size_t const Ndiv_a = nmax/a;
    cell(0,0) = a;
    // Iterates over values of a such that a * b * c == nmax
    for(size_t b(1); b <= Ndiv_a and cont; ++b) 
    {
      cell(1,1) = b;
      if(Ndiv_a % b != 0) continue;
      // Iterates over values of a such that a * b * c == nmax
      size_t const c( Ndiv_a/b);
      cell(2,2) = c;
      if( a * b *c != nmax ) BOOST_THROW_EXCEPTION(LaDa::error::internal());
      for(size_t d(0); d < b and cont; ++d) 
      {
        cell(1,0) = d;
        for(size_t e(0); e < c and cont; ++e) 
        {
          cell(2,0) = e;
          for(size_t f(0); f < c and cont; ++f) 
          {
            cell(2,1) = f;

            Structure< LADA_TYPE > structure = supercell(lattice, lattice.cell()*cell);
            structure = primitive(structure, 1e-8);
            LADA_DOASSERT( eq(lattice.cell().determinant(), structure.cell().determinant(), 1e-5),\
                           "Not primitive.\n");
            LADA_DOASSERT(is_integer(structure.cell() * lattice.cell().inverse(), 1e-5), "Not a sublattice.\n");
            LADA_DOASSERT(is_integer(lattice.cell() * structure.cell().inverse(), 1e-5), "Not a sublattice.\n");
            t_Str::const_iterator i_atom = structure.begin();
            t_Str::const_iterator const i_atom_end = structure.end();
            for(; i_atom != i_atom_end; ++i_atom)
            {
              if(not compare_occupations(lattice[i_atom->site()]->type)(i_atom->type()))
                std::cout << structure.cell() << "\n" << lattice[i_atom->site()] << "\n" << *i_atom << "\n";
              LADA_DOASSERT(compare_occupations(lattice[i_atom->site()]->type)
                                               (i_atom->type()), "Inequivalent occupation.\n");
              LADA_DOASSERT( is_integer(   lattice.cell().inverse() 
                                         * (i_atom->pos() - lattice[i_atom->site()]->pos), 1e-5),
                             "Inequivalent positions.\n") 
            }

          } // f
        } // e
      } // d
    } // b
  } // a

  return 0;
}