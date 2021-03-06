from simtk.openmm.app import *
from simtk.openmm import *
from simtk.unit import *
from sys import stdout, exit, stderr

from openmmplumed import PlumedForce

psf = CharmmPsfFile('dia2.psf')
pdb = PDBFile('dia2.pdb')

params = CharmmParameterSet('par_all27_prot_lipid.prm', permissive=True)
system = psf.createSystem(params, nonbondedMethod=NoCutoff,
                          nonbondedCutoff=1*nanometer, constraints=None)

plumedScript = "diala.plumed.nocont"
with open(plumedScript) as f:
    script = f.read()
system.addForce(PlumedForce(script))

req_plt = Platform.getPlatformByName('CUDA')

integrator = LangevinIntegrator(300*kelvin, 1/picosecond, 1*femtoseconds)
simulation = Simulation(psf.topology, system, integrator,
                        req_plt, {'DeviceIndex': '0'} )

ctx = simulation.context
platform = ctx.getPlatform()
print(f"Using platform {platform.getName()} with properties:")
for prop in platform.getPropertyNames():
    print(f"    {prop}\t\t{platform.getPropertyValue(ctx,prop)}")

L = 32.0
ctx.setPeriodicBoxVectors([L,0,0], [0,L,0], [0,0,L])


simulation.context.setPositions(pdb.positions)

simulation.saveState("pre.xml")


simulation.reporters.append(DCDReporter('output.dcd', 100))
simulation.reporters.append(StateDataReporter(stdout, 100, step=True,
        potentialEnergy=True, temperature=True))

simulation.step(1000000)


