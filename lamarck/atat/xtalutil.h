#ifndef _XTALUTIL_H_
#define _XTALUTIL_H_

#include "vectmac.h"
#include "arraylist.h"
#include "integer.h"

#include <opt/types.h>

namespace atat
{ 

using ::ceil;using ::floor;

class Structure {
public:
  rMatrix3d cell;
  Array<rVector3d> atom_pos;
  Array<types::t_int> atom_type;
  Structure(void): atom_pos(), atom_type() {}
 Structure(const Structure &a): cell(a.cell), atom_pos(a.atom_pos), atom_type(a.atom_type) {}
};

class MultiCluster {
 public:
  MultiCluster(types::t_int n=0): clus(n), site_type(n), func(n) {}
  MultiCluster(const MultiCluster &c): clus(c.clus), site_type(c.site_type), func(c.func) {}
  Array<rVector3d> clus;
  Array<types::t_int> site_type;
  Array<types::t_int> func;
  void operator=(const MultiCluster &m) {
    clus=m.clus;
    site_type=m.site_type;
    func=m.func;
  }
};

typedef Array<rVector3d> ArrayrVector3d;

inline types::t_real cos_angle(rVector3d v, rVector3d u) {
  return v*u/sqrt(norm(v)*norm(u));
}

inline types::t_real cylinder_norm(types::t_real x) {
  return fabs(fmod(fabs(x)+0.5,1.)-0.5);
}

inline types::t_real cylinder_norm(rVector3d v) {
  return sqrt(sqr(cylinder_norm(v(0)))+sqr(cylinder_norm(v(1)))+sqr(cylinder_norm(v(2))));
}

inline rVector3d ceil(rVector3d v) {
  return(rVector3d(ceil(v(0)),ceil(v(1)),ceil(v(2))));
}

inline rVector3d floor(rVector3d v) {
  return(rVector3d(floor(v(0)),floor(v(1)),floor(v(2))));
}

inline rVector3d mod1(rVector3d v) {
  return(v-floor(v));
//  return(rVector3d(fmod(u(0),1.),fmod(u(1),1.),fmod(u(2),1.)));
}

inline rVector3d cylinder(rVector3d v) {
  return(rVector3d(cylinder_norm(v(0)),cylinder_norm(v(1)),cylinder_norm(v(2))));
}

inline types::t_int is_int(const rVector3d &v) {
  for (types::t_int i=0; i<3; i++) {
    if (fabs(v(i)-rint(v(i)))>zero_tolerance) return 0;
  }
  return 1;
}

inline types::t_int is_int(const rMatrix3d &m) {
  for (types::t_int i=0; i<3; i++) {
    for (types::t_int j=0; j<3; j++) {
      if (fabs(m(i,j)-rint(m(i,j)))>zero_tolerance) return 0;
    }
  }
  return 1;
}

types::t_int in01(rVector3d v);
types::t_int in01included(rVector3d v);
types::t_int which_atom(const Array<rVector3d> &atom_pos, rVector3d pos, const rMatrix3d &inv_cell);
types::t_int which_atom(const Array<rVector3d> &atom_pos, rVector3d pos);
rVector3d wrap_inside_cell(const rVector3d &v, const rMatrix3d &cell);
rVector3d flip_into_brillouin_1(const rVector3d &k, const rMatrix3d &rec_lat);
rVector3d find_perpendicular(const rVector3d &dir);
void wrap_inside_cell(Array<rVector3d> *dest, const Array<rVector3d> &src, const rMatrix3d &cell);
iVector3d make_miller(rVector3d normal);
void calc_lattice_vectors(rMatrix3d *lattice_vector, const rVector3d &cell_length, rVector3d cell_angle);
void calc_lattice_vectors(rVector3d *cell_length, rVector3d *cell_angle, const rMatrix3d &lattice_vector);
iVector3d find_sphere_bounding_box(const rMatrix3d &cell, types::t_real radius);
types::t_int equivalent_mod_cell(const rVector3d &a, const rVector3d &b, const rMatrix3d &inv_cell);
types::t_int equivalent_mod_cell(const Array<rVector3d> &a, const Array<rVector3d> &b, const rMatrix3d &inv_cell);
types::t_int equivalent_mod_cell(const MultiCluster &a, const MultiCluster &b, const rMatrix3d &inv_cell);

class LatticePointIterator {
  rMatrix3d cell;
  types::t_real max_radius;
  types::t_real inc_radius;
  LinkedList<rVector3d> list;
  void find_new_neighbors(types::t_real new_max_radius);
 public:
  LatticePointIterator(void): list(), cell() {}
  LatticePointIterator(const rMatrix3d &_cell, types::t_int skipzero=1): list(), cell() {init(_cell,skipzero);}
  void init(const rMatrix3d &_cell, types::t_int skipzero=1);
  rVector3d operator++(int);
  operator FixedVector<types::t_real,3> () {
    LinkedListIterator<rVector3d> i(list);
    return *i;
  }
};

class LatticePointInCellIterator {
  rMatrix3d cell;
  rMatrix3d cell_to_super;
  rVector3d shift;
  MultiDimIterator<iVector3d> current;
public:
  LatticePointInCellIterator(void): current() {}
  LatticePointInCellIterator(const rMatrix3d &_cell, const rMatrix3d &_supercell): current() {
    init(_cell,_supercell);
  }
  void init(const rMatrix3d &_cell, const rMatrix3d &_supercell);
  void advance_to_valid(void);
  operator void * () {
    return current;
  }
  operator FixedVector<types::t_real,3> () {
    return cell*to_real(current);
  }
  void operator++(int) {
    current++;
    advance_to_valid();
  }
};

void find_all_atom_in_supercell(Array<rVector3d> *psuper_atom_pos,
				Array<types::t_int> *psuper_atom_type,
				const Array<rVector3d> &atom_pos,
				const Array<types::t_int> &atom_type,
				const rMatrix3d &cell, const rMatrix3d &supercell);

types::t_real find_1nn_radius(const Structure &str, types::t_int atom);
types::t_real find_1nn_radius(const Structure &str);

class AtomPairIterator {
  rMatrix3d cell;
  LinkedList<ArrayrVector3d> list;
  const Array<rVector3d> *atom_pos1;
  const Array<rVector3d> *atom_pos2;
  types::t_real max_dist_in_cell;
  types::t_real inc_radius;
  types::t_real max_radius;
  types::t_int same_pos;
  Array<rVector3d> an_atom;
  void find_new_neighbors(types::t_real new_max_radius);
  void init(void);
 public:
  AtomPairIterator(void): list(), an_atom() {}
  AtomPairIterator(const rMatrix3d &_cell, const Array<rVector3d> &_atom_pos):
                       list(), an_atom() {
    init(_cell,_atom_pos);
  }
  AtomPairIterator(const rMatrix3d &_cell, const Array<rVector3d> &_atom_pos1, const Array<rVector3d> &_atom_pos2):
                       list(), an_atom() {
    init(_cell,_atom_pos1,_atom_pos2);
  }
  AtomPairIterator(const rMatrix3d &_cell, const rVector3d &_an_atom, const Array<rVector3d> &_atom_pos):
                       list(), an_atom() {
    init(_cell,_an_atom,_atom_pos);
  }
  void init(const rMatrix3d &_cell, const Array<rVector3d> &_atom_pos);
  void init(const rMatrix3d &_cell, const Array<rVector3d> &_atom_pos1, const Array<rVector3d> &_atom_pos2);
  void init(const rMatrix3d &_cell, const rVector3d &_an_atom, const Array<rVector3d> &_atom_pos);
  void operator++(int);
  operator const Array<rVector3d>& () {
    LinkedListIterator<ArrayrVector3d> i(list);
    return *i;
  }
  const rVector3d& operator()(types::t_int j) {
    LinkedListIterator<ArrayrVector3d> i(list);
    return (*i)(j);
  }
  types::t_real length(void) {
    LinkedListIterator<ArrayrVector3d> i(list);
    return norm( (*i)(1)-(*i)(0) );
  }
};

class AtomMultipletIterator {
  rMatrix3d cell;
  const Array<rVector3d> *atom_pos;
  types::t_int ntuple;
  Array<rVector3d> multiplet;
  Array<AtomPairIterator> pairs;
 public:
  AtomMultipletIterator(const rMatrix3d &_cell, const Array<rVector3d> &_atom_pos, types::t_int _ntuple):
                       pairs(), multiplet() {
    init(_cell,_atom_pos,_ntuple);
  }
  AtomMultipletIterator(const AtomMultipletIterator &_multiplet, types::t_int _ntuple):
                       pairs(), multiplet() {
    init(_multiplet.cell,*_multiplet.atom_pos,_ntuple);
  }
  void init(const rMatrix3d &_cell, const Array<rVector3d> &_atom_pos, types::t_int _ntuple);
  void operator++(int);
  operator const Array<rVector3d>& (void) {
    return multiplet;
  }
  const FixedVector<types::t_real,3>& operator()(types::t_int j) {
    return multiplet(j);
  }
  types::t_real length(void) {
    return norm(multiplet(ntuple-1)-multiplet(0));
  }
};

types::t_real get_cluster_length(const Array<rVector3d> &c);

void find_common_supercell(rMatrix3d *psupercell, const rMatrix3d &a, const rMatrix3d &b);
void find_common_simple_supercell(iVector3d *psimple_supercell, const rMatrix3d &unitcell, const rMatrix3d &supercell);


} // namespace atat

#endif
