## This script is to take a ligand file (format can be pdb, mol2, or sdf), calculate AM1-BCC partial charges, Make Rosetta Gen Params
## Example run: python PrepGALigand.py -i Glucose.sdf -n GLC -c 0 -f sdf
import sys
import os
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', dest='inputligand', type=str , help="Ligand file in format pdb, mol2, or sdf", required=True)
parser.add_argument('-n', '--name', dest='finalname', type=str , help="Name of output ligand; 3 characters", required=True)
parser.add_argument('-c', '--charge', dest='charge', type=int , help="Total charge of the ligand", required=True)
parser.add_argument('-f', '--format', dest='ligformat', type=str , help="Format of ligand file; can be mol2, sdf, or pdb", required=True)
args = parser.parse_args()

ParamScript = '/share/siegellab/software/Rosetta_group_0618/main/source/scripts/python/public/generic_potential/mol2genparams.py'
RosPath = '/share/siegellab/software/Rosetta_group_0618'
Babel = '/share/siegellab/tcoulther/software/pkg/anaconda3/envs/Pyrosetta_Bootcamp/bin/obabel'
AnteChamber = '/share/siegellab/tcoulther/software/pkg/anaconda3/envs/Pyrosetta_Bootcamp/bin/antechamber'

os.environ['LD_LIBRARY_PATH'] = '/share/siegellab/software/Rosetta_group_0618/main/source/build/src/release/linux/4.4/64/x86/gcc/5.4/default/:/share/siegellab/software/Rosetta_group_0618/main/source/build/external/release/linux/4.4/64/x86/gcc/5.4/default/'
os.environ['ROSETTA_BIN'] = '/share/siegellab/software/Rosetta_group_0618/main/source/bin'
os.environ['ROSETTA_DB'] = 'share/siegellab/software/Rosetta_group_0618/main/source/bin'


## Conversion with babel to mol2 format. Even if input is in mol2, just to be sure format is correct
os.system('%s -i%s %s -omol2 -O%s.mol2 -p 7.0' % (Babel, args.ligformat, args.inputligand, args.finalname))
ligand = args.finalname+'.mol2'

## Cleans the mol2 file. Theres a section the doesnt jibe with ambertools
with open(ligand, 'r') as old:
    with open(ligand+'.edit', 'w') as new:
        write = 'yes'
        for line in old:
            if line.startswith('@<TRIPOS>UNITY_ATOM_ATTR'):      
                write = 'no'
            if line.startswith('@<TRIPOS>BOND'):
                write = 'yes'
            if write == 'yes':
                new.write(line)
os.system('mv %s.edit %s' % (ligand,ligand))   

## Calculating partial charges and making new mol2 from ambertools
os.system('%s -i %s -fi mol2 -o %s.am1-bcc.mol2 -fo mol2 -c bcc -at sybyl -nc %s -ek "scfconv=1.d-6, ndiis_attempts=700"' % (AnteChamber, ligand, args.finalname, args.charge))
ligand = args.finalname+'.am1-bcc.mol2'

## Making parameter file from Rosetta for ligand (Mol2GenParams for GALigandDock)
os.system('python %s -s %s' % (ParamScript, ligand))
os.system('mv %s %s' % (ligand[:-5]+'.params',args.finalname+'.params'))
os.system('mv %s %s' % (ligand[:-5]+'_0001.pdb',args.finalname+'.pdb'))
os.system("sed -i 's/%s/%s/g' %s" % ('LG1',args.finalname, args.finalname+'.params'))
os.system("sed -i 's/%s/%s/g' %s" % ('LG1',args.finalname, args.finalname+'.pdb'))




