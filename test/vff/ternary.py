from numpy import dot, array
from pylada.mpi import world
from pylada.vff import Vff
from pylada.crystal import Structure, FreezeCell

vff = Vff()
vff.lattice.set_types = ("In", "Ga"), ("As",)
vff.lattice.scale = 6.5
vff.add_bond = "In", "As", (2.62332, 21.6739, -112.0, 150.0)
vff.add_bond = "Ga", "As", (2.44795, 32.1530, -105.0, 150.0)
vff.add_angle = "As", "Ga", "As", ("tet", -4.099, 9.3703)
vff.add_angle = "Ga", "As", "Ga", ("tet", -4.099, 9.3703)
vff.add_angle = "In", "As", "In", ("tet", -5.753, 5.7599)
vff.add_angle = "As", "In", "As", ("tet", -5.753, 5.7599)
vff.add_angle = "Ga", "As", "In", (-0.35016, -4.926, 7.5651)
vff.minimizer.verbose = True
vff.minimizer.type = "gsl_bfgs2"
vff.minimizer.itermax = 1
vff.minimizer.tolerance = 1e-5
vff.minimizer.uncertainties = 1e-3

structure = Structure()
# structure.set_cell = (00.0, 0.5, 0.5),\
#                      (0.50, 0.0, 0.5),\
#                      (0.50, 0.5, 0.0)
# structure.add_atoms = ((0.00, 0.00, 0.00), "In"),\
#                       ((0.25, 0.25, 0.25), "As")
structure.set_cell = (10.0, 0.5, 0.5),\
                     (0.00, 0.0, 0.5),\
                     (0.00, 0.5, 0.0)
structure.add_atoms = ((0.00, 0.00, 0.00), "Ga"),\
                      ((0.25, 0.25, 0.25), "As"),\
                      ((1.00, 0.00, 0.00), "Ga"),\
                      ((1.25, 0.25, 0.25), "As"),\
                      ((2.00, 0.00, 0.00), "In"),\
                      ((2.25, 0.25, 0.25), "As"),\
                      ((3.00, 0.00, 0.00), "In"),\
                      ((3.25, 0.25, 0.25), "As"),\
                      ((4.00, 0.00, 0.00), "Ga"),\
                      ((4.25, 0.25, 0.25), "As"),\
                      ((5.00, 0.00, 0.00), "In"),\
                      ((5.25, 0.25, 0.25), "As"),\
                      ((6.00, 0.00, 0.00), "In"),\
                      ((6.25, 0.25, 0.25), "As"),\
                      ((7.00, 0.00, 0.00), "Ga"),\
                      ((7.25, 0.25, 0.25), "As"),\
                      ((8.00, 0.00, 0.00), "Ga"),\
                      ((8.25, 0.25, 0.25), "As"),\
                      ((9.00, 0.00, 0.00), "Ga"),\
                      ((9.25, 0.25, 0.25), "As"), 
structure.scale = vff.lattice.scale # + 0.1

# vff.direction = FreezeCell.a0 | FreezeCell.a1

# print vff
# print structure

epsilon = array([[1e0, 0.1, 0], [0.1, 1e0, 0], [0, 0, 1e0]])
structure.cell = dot(epsilon, structure.cell)
for atom in structure.atoms: atom.pos = dot(epsilon, atom.pos)

out = vff(structure, outdir = "work", comm = world, relax=False, overwrite=True)
print out.energy
print out.structure
print repr(out.stress)
