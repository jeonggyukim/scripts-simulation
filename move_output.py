#!/usr/bin/env python

import glob
import os
import os.path as osp
import argparse

from read_athinput import read_athinput, find_match, find_files_vtk2d

# Default values
basedir_orig_def = "/scratch/gpfs/jk11/SF-CLOUD/M1E5R20.ALL.N128.test.roe.hydro"
basedir_new_def = "/tigress/jk11/SF-CLOUD/M1E5R20.ALL.N128.test.roe.hydro"

join_vtk_script = "/tigress/jk11/scripts/vtk/join.sh"

join_vtk_def = True
join_vtk_suffix_def = True
sync_rst_def = True

parser = argparse.ArgumentParser(
    description='''Move tigress simulation output files from gpfsto tigress using rsync.
To move vtk files, use vtk/join_vtk.sh script''')

parser.add_argument('-i', '--basedir_orig', type=str,
                    default=basedir_orig_def,
                    help='original basedir')
parser.add_argument('-o', '--basedir_new', type=str,
                    default=basedir_new_def,
                    help='new basedir')
parser.add_argument('-j', '--join_vtk',
                    action='store_true', default=join_vtk_def,
                    help='Toggle to (3d) join vtk files')
parser.add_argument('-s', '--join_vtk_suffix',
                    action='store_true', default=join_vtk_suffix_def,
                    help='Toggle to join (2d) vtk files that have suffix')
parser.add_argument('-r', '--sync_rst',
                    action='store_true', default=sync_rst_def,
                    help='Toggle to sync restart files')

args = vars(parser.parse_args())
locals().update(args)

basedir_orig_id0 = osp.join(basedir_orig, 'id0', '') # add trailing slash

print('basedir_orig: ', basedir_orig)
print('basedir_new: ', basedir_new)

if not osp.isdir(basedir_orig):
    raise IOError('basedir_orig does not exist: ', basedir_orig)

if osp.isdir(basedir_new):
    print('New basedir {0:s} exists.'.format(basedir_new))
else:
    print('Create new basedir {0:s}'.format(basedir_new))
    os.makedirs(basedir_new)

basedir_new_sub = dict()
basedir_new_sub['hst'] = osp.join(basedir_new, 'hst') # hst sphst sn
basedir_new_sub['starpar'] = osp.join(basedir_new, 'starpar')
basedir_new_sub['rst'] = osp.join(basedir_new, 'rst')
basedir_new_sub['vtk'] = osp.join(basedir_new, 'vtk')

if glob.glob(osp.join(basedir_orig, 'id0', '*.zprof')):
    basedir_new_sub['zprof'] = osp.join(basedir_new, 'zprof')

for k,d in basedir_new_sub.items():
    if not osp.isdir(d):
        os.makedirs(d)
        print('Create directory for {0:s}: {1:s}'.format(k,d))

rsync_hst = 'rsync -av --include="*.sn" --include="*.star" --include="*.hst" --exclude="*" {0:s} {1:s}'.\
                                  format(basedir_orig_id0, basedir_new_sub['hst'])
rsync_star = 'rsync -av --include="*.starpar.vtk" --include="*.star" --exclude="*" {0:s} {1:s}'.\
                                   format(basedir_orig_id0, basedir_new_sub['starpar'])
rsync_rst = 'rsync -av --include="*.rst" --exclude="*" {0:s}/id*/ {1:s}'.\
                                   format(basedir_orig, basedir_new_sub['rst'])
if 'zprof' in basedir_new_sub.keys():
    rsync_zprof = 'rsync -av --include="*.zprof" --exclude="*" {0:s} {1:s}'.\
                                        format(basedir_orig_id0, basedir_new_sub['zprof'])

rsync_misc = 'rsync -av --exclude="id*" {0:s} {1:s}'.format(osp.join(basedir_orig, ''), basedir_new)

# do not rsync id0 directory
commands = [rsync_hst, rsync_star, rsync_misc]

if 'zprof' in basedir_new_sub.keys():
    commands.append(rsync_zprof)

#######################
## Run rsync commands #
#######################
for c in commands:
    #print(c)
    os.system(c)

if join_vtk or join_vtk_suffix:
    print('##################')
    print('# join vtk files')
    print('##################')

    # Find all vtk files in id0 directory except for starpar.vtk
    nums = dict()
    nums['vtk'] = []
    suffix = []
    fvtk = glob.glob(osp.join(basedir_orig, 'id0', '*.vtk'))
    for f in fvtk:
        ff = osp.basename(f).split('.')
        problem_id = ff[0] # problem_id
        try:
            nums['vtk'].append(int(ff[-2]))
        except ValueError:
            suffix.append(ff[-2])

    suffix = sorted(list(set(suffix)))
    suffix.remove('starpar')
    nums['vtk'] = sorted(nums['vtk'])

    join_vtk_command = dict()
    if join_vtk:
        num_min = nums['vtk'][0]
        # If joined vtk files exist in the new directory, reset num_min
        for num in nums['vtk']:
            if osp.exists(osp.join(basedir_new,'vtk',
                                   '{0:s}.{1:04d}.vtk'.format(problem_id,num))):
                num_min = num

        r = r'{0:d}:{1:d}'.format(num_min,nums['vtk'][-1])
        join_vtk_command['vtk'] = '{0:s} -r {1:s} -i {2:s} -o {3:s} -C'.format(
            join_vtk_script,r,basedir_orig,osp.join(basedir_new,'vtk'))
        #print(join_vtk_command['vtk'])
        os.system(join_vtk_command['vtk'])
    
    if join_vtk_suffix:
        for s in suffix:
            nums[s] = []
            fvtk = glob.glob(osp.join(basedir_orig, 'id0', f'*.{s}.vtk'))
            for f in fvtk:
                ff = osp.basename(f).split('.')
                nums[s].append(int(ff[-3]))
            nums[s] = sorted(nums[s])

        for s in suffix:
            num_min = nums[s][0]
            if osp.exists(osp.join(basedir_new,s)):
                for num in nums[s]:
                    if osp.exists(osp.join(
                            basedir_new,s,'{0:s}.{1:04d}.{2:s}.vtk'.\
                            format(problem_id,num,s))):
                        num_min = num
            r = r'{0:d}:{1:d}'.format(num_min,nums[s][-1])
            join_vtk_command[s] = '{0:s} -r {1:s} -i {2:s} -o {3:s} -s {4:s} -C'.format(
                join_vtk_script,r,basedir_orig,osp.join(basedir_new,s),s)

        for k,v in join_vtk_command.items():
            if k != 'vtk':
                #print(k,v)
                os.system(v)


        ## join 2d slices
        # Find stdout and read parameter blocks
        fathinput = find_match(basedir_orig, 
                               [('out.txt',),('stdout.txt',),('log.txt',),('*.out',),
                                ('slurm-*',),('athinput.*',),('*.par',)])
        par = read_athinput(fathinput[0])

        # Find all output formats
        out_fmt = []
        for k in par.keys():
            if 'output' in k:
                # Skip if the block number XX (<outputXX>) is greater than maxout
                if int(k.replace('output','')) > par['job']['maxout']:
                    continue
                if par[k]['out_fmt'] == 'vtk' and \
                   not (par[k]['out'] == 'prim' or par[k]['out'] == 'cons'):
                    out_fmt.append(par[k]['id'] + '.' + \
                                   par[k]['out_fmt'])
                else:
                    out_fmt.append(par[k]['out_fmt'])

            problem_id = par['job']['problem_id']

        # Find 2d vtk files
        files_slices = dict()
        nums_slices = dict()
        suffix_slices = []
        for fmt in out_fmt:
            if '.vtk' in fmt:
                fmt = fmt.split('.')[0]
                patterns = [('id0', '*.????.{0:s}.vtk'.format(fmt)),
                            ('{0:s}'.format(fmt), '*.????.{0:s}.vtk'.format(fmt))]
                files_slices_ = find_match(basedir_orig, patterns)
                if files_slices_:
                    pass
                else:
                    # Some 2d vtk files_slices may not be found in id0 folder (e.g., slices)
                    suffix_slices.append(fmt)

        for fmt in suffix_slices:
            files_ = sorted(glob.glob(osp.join(
                basedir_orig, 'id*', '*.????.{0:s}.vtk'.format('d_y'))))
            pid = osp.basename(files_[0]).split('.')[0].replace(problem_id,"")[3:]
            files_slices[fmt] = sorted(glob.glob(
                osp.join(basedir_orig, f'id{pid}', '*.????.{0:s}.vtk'.format('d_y'))))

            nums_slices[f'{fmt}'] = [int(osp.basename(f).split('.')[1]) \
                              for f in files_slices[f'{fmt}']]


        join_vtk_command_slices = dict()
        for s in suffix_slices:
            num_min = nums_slices[s][0]
            if osp.exists(osp.join(basedir_new,s)):
                for num in nums_slices[s]:
                    if osp.exists(osp.join(basedir_new,s,
                                '{0:s}.{1:04d}.{2:s}.vtk'.format(problem_id,num,s))):
                        num_min = num
            r = r'{0:d}:{1:d}'.format(num_min,nums_slices[s][-1])
            join_vtk_command_slices[s] = '{0:s} -r {1:s} -i {2:s} -o {3:s} -s {4:s} -C'.\
                format(join_vtk_script,r,basedir_orig,osp.join(basedir_new,s),s)

        for k,v in join_vtk_command_slices.items():
            if k != 'vtk':
                #print(k,v)
                os.system(v)
                
if sync_rst:
    print('##################')
    print('# rsync rst files')
    print('##################')
    os.system(rsync_rst)

# else:
#     print('##################')
#     print('# rsync rst files: only the last two rst files')
#     print('##################')
#     nums = []
#     frst = glob.glob(osp.join(basedir_orig, 'id0', '*.rst'))
#     for f in fvtk:
#         ff = osp.basename(f).split('.')
#         nums.append(int(ff[-2]))

#     nums = sorted(nums)
#     rsync_rst = 'rsync -av --include="*.{0:04d}.rst" --exclude="*" {1:s}/id*/ {2:s}'.\
#                                    format(nums[-1], basedir_orig, basedir_new_sub['rst'])
#     os.system(rsync_rst)
#     rsync_rst = 'rsync -av --include="*.{0:04d}.rst" --exclude="*" {1:s}/id*/ {2:s}'.\
#                                    format(nums[-2], basedir_orig, basedir_new_sub['rst'])
#     os.system(rsync_rst)



