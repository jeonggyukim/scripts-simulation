#!/usr/bin/env python
#!/usr/bin/e
import glob
import os
import argparse

basedir_orig_def = "/scratch/gpfs/jk11/TIGRESS-RT/R4_8pc.CR2.radp"
basedir_new_def = "/tigress/jk11/TIGRESS-RT/R4_8pc.CR2.radp"

parser = argparse.ArgumentParser(
    description='''Move tigress simulation output files from gpfsto tigress using rsync. 
To move vtk files, use join_vtk.sh script in Athena-TIGRESS/vtk''')
parser.add_argument('--basedir_orig', type=str,
                    default=basedir_orig_def,
                    help='original basedir')
parser.add_argument('--basedir_new', type=str,
                    default=basedir_new_def,
                    help='new basedir')
parser.add_argument('--join_vtk',
                    action='store_true', default=False,
                    help='Toggle to join vtk files')
args = vars(parser.parse_args())
locals().update(args)

basedir_orig_id0 = os.path.join(basedir_orig, 'id0', '') # add trailing slash

print('basedir_orig: ', basedir_orig)
print('basedir_new: ', basedir_new)

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
