#!/usr/bin/env python

import glob
import os
import argparse

basedir_orig_def = "/scratch/gpfs/jk11/radps_postproc/R8_2pc_rst.xymax2048.eps10"
#basedir_orig_def = "/scratch/gpfs/jk11/TIGRESS-RT/R4_4pc.RT.nowind"
#basedir_new_def = "/tigress/jk11/TIGRESS-RT/R8_4pc.RT.wind"
#basedir_new_def = "/tigress/jk11/TIGRESS-RT/R4_4pc.RT.wind"
basedir_new_def = "/tigress/jk11/TIGRESS-DIG/R8_2pc_rst.xymax2048.eps10"
#basedir_new_def = "/projects/EOSTRIKE/TIGRESS-RT/R4_4pc.RT.wind"

sync_rst_def = True
join_vtk_def = True

parser = argparse.ArgumentParser(
    description='''Move tigress simulation output files from gpfsto tigress
using rsync. To move vtk files, use vtk/join_vtk.sh script''')

parser.add_argument('--basedir_orig', type=str,
                    default=basedir_orig_def,
                    help='original basedir')
parser.add_argument('--basedir_new', type=str,
                    default=basedir_new_def,
                    help='new basedir')
parser.add_argument('--join_vtk',
                    action='store_true', default=join_vtk_def,
                    help='Toggle to join vtk files')
parser.add_argument('--sync_rst',
                    action='store_true', default=sync_rst_def,
                    help='Toggle to join vtk files')

args = vars(parser.parse_args())
locals().update(args)

basedir_orig_id0 = os.path.join(basedir_orig, 'id0', '') # add trailing slash

print('basedir_orig: ', basedir_orig)
print('basedir_new: ', basedir_new)

if not os.path.isdir(basedir_orig):
    raise IOError('basedir_orig does not exist: ', basedir_orig)

if os.path.isdir(basedir_new):
    print('New basedir {0:s} exists.'.format(basedir_new))
else:
    print('Create new basedir {0:s}'.format(basedir_new))
    os.makedirs(basedir_new)

basedir_new_hst = os.path.join(basedir_new, 'hst')
basedir_new_star = os.path.join(basedir_new, 'starpar')
basedir_new_zprof = os.path.join(basedir_new, 'zprof')
basedir_new_rst = os.path.join(basedir_new, 'rst')
basedir_new_vtk = os.path.join(basedir_new, 'vtk')

for d in (basedir_new_hst, basedir_new_vtk, \
          basedir_new_star, basedir_new_zprof, basedir_new_rst):
    if not os.path.isdir(d):
        os.makedirs(d)
        print('Create directory {0:s}'.format(d))

rsync_id0 = 'rsync -av {0:s} {1:s}'.format(basedir_orig_id0, basedir_new)

rsync_hst = 'rsync -av --include="*.sn" --include="*.hst" --exclude="*" {0:s} {1:s}'.\
                                  format(basedir_orig_id0, basedir_new_hst)
rsync_zprof = 'rsync -av --include="*.zprof" --exclude="*" {0:s} {1:s}'.\
                                    format(basedir_orig_id0, basedir_new_zprof)
rsync_star = 'rsync -av --include="*.starpar.vtk" --exclude="*" {0:s} {1:s}'.\
                                   format(basedir_orig_id0, basedir_new_star)
rsync_rst = 'rsync -av --include="*.rst" --exclude="*" {0:s}/id*/ {1:s}'.\
                                   format(basedir_orig, basedir_new_rst)
rsync_misc = 'rsync -av --include="snapshots" --include="prj*" --include="slc*"  --include="athinput*" --include="athena*" --include="radps_postproc*" --include="tigress*" --include="*.txt" ' + \
                                    '--exclude="*" {0:s} {1:s}'.\
                                    format(os.path.join(basedir_orig, ''), basedir_new)

# do not rsync id0 directory
commands = [rsync_hst, rsync_zprof, rsync_star, rsync_misc]
if sync_rst:
    commands.append(rsync_rst)

for c in commands:
    print(c)
    os.system(c)
