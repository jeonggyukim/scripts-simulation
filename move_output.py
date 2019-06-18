#!/usr/bin/env python

import glob
import os
import argparse

# problem_id_def = "R2_2pc_L256_B2"
# suffix_def = "noHII.Z1.CR010.L100"

problem_id_def = "R4_2pc_L512_B10"
suffix_def = "HII_only"

# problem_id_def = "M1_2pc_Tth50"
# suffix_def = "noHII.Z2.CR010.L100.FUV_only"

parser = argparse.ArgumentParser(
    description='''Move tigress simulation output files from gpfsto tigress using rsync. 
To move vtk files, use join_vtk.sh script in Athena-TIGRESS/vtk''')

parser.add_argument('--problem_id', type=str,
                    default=problem_id_def,
                    help='problem id')
parser.add_argument('--suffix', type=str,
                    default=suffix_def,
                    help='suffix')

args = vars(parser.parse_args())
locals().update(args)

model = "{0:s}.{1:s}".format(problem_id, suffix)
basedir_orig = "/scratch/gpfs/jk11/TIGRESS-DIG/{0:s}".format(model)
#basedir_new = "/projects/EOSTRIKE/TIGRESS_XCO_ART/{0:s}".format(model)
basedir_new = "/tigress/jk11/TIGRESS-DIG/{0:s}".format(model)

basedir_orig_id0 = os.path.join(basedir_orig, 'id0', '') # add trailing slash

print('basedir_orig: ', basedir_orig)
print('basedir_new: ', basedir_new)
print('problem_id: ', problem_id)

if not os.path.isdir(basedir_orig):
    raise IOError('basedir_orig does not exist: ', basedir_orig)

if os.path.isdir(basedir_new):
    print('Directory {0:s} exists.'.format(basedir_new))
else:
    print('Create directory {0:s}'.format(basedir_new))
    os.makedirs(basedir_new)

basedir_new_hst = os.path.join(basedir_new, 'hst')
basedir_new_star = os.path.join(basedir_new, 'starpar')
basedir_new_zprof = os.path.join(basedir_new, 'zprof')
basedir_new_vtk = os.path.join(basedir_new, 'vtk')

for d in (basedir_new_hst, basedir_new_vtk, \
          basedir_new_star, basedir_new_zprof):
    if not os.path.isdir(d):
        os.makedirs(d)
        print('Create directory {0:s}'.format(d))

rsync_id0 = 'rsync -av {0:s} {1:s}'.format(basedir_orig_id0, basedir_new)

rsync_hst = 'rsync -av --include="*.hst" --exclude="*" {0:s} {1:s}'.\
                                  format(basedir_orig_id0, basedir_new_hst)
rsync_zprof = 'rsync -av --include="*.zprof" --exclude="*" {0:s} {1:s}'.\
                                    format(basedir_orig_id0, basedir_new_zprof)
rsync_star = 'rsync -av --include="*.starpar.vtk" --exclude="*" {0:s} {1:s}'.\
                                   format(basedir_orig_id0, basedir_new_star)
rsync_misc = 'rsync -av  --include="athinput*" --include="athena" --include="*.txt" ' + \
                                    '--exclude="*" {0:s} {1:s}'.\
                                    format(os.path.join(basedir_orig, ''), basedir_new)

# do not rsync id0 directory
commands = (rsync_hst, rsync_zprof, rsync_star, rsync_misc)
for c in commands:
    print(c)
    os.system(c)
