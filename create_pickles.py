#!/usr/bin/env python

from __future__ import print_function
import os, sys
import argparse, subprocess, socket
try:
    from mpi4py import MPI
except ImportError as e:
    print(e)
    raise

sys.path.insert(0, '/tigress/jk11/athena-tigress/python/')
import pyathena as pa
import pyathena.tigradpy as tp

def split_container(container, count):
    """
    Original source:
    https://gist.github.com/krischer/2c7b95beed642248487a

    Simple function splitting a container into equal length chunks.
    Order is not preserved but this is potentially an advantage depending on
    the use case.
    """
    return [container[_i::count] for _i in range(count)]

def eval_range(string, end_def=2001):
    """
    Returns range(start, end, step) from input string
    'start:end:step' (see examples below)

    Examples:
    'b' - range(b,b+1)
    'a:b' - range(a,b)
    'a:b:c' - range(a,b,c)
    ':b:c' - range(0,b,c)
    '::c' - range(0,end,c)
    'a::c' - range(a,end,c)
    """
    
    r = None
    if string.count(':') == 2:
        s = string.split(':')
        if s[0] and s[1] and s[2]:        # full info given
            r = range(eval(s[0]), eval(s[1])+1, eval(s[2]))
        elif not s[0] and s[1] and s[2]:   # start missing
            r = range(0, eval(s[1])+1, eval(s[2]))
        elif not s[0] and not s[1] and s[2]: # only step size given
            r = range(0, end_def, eval(s[2]))
        elif s[0] and s[1] and not s[2]:   # step missing
            r = range(eval(s[0]),eval(s[1])+1)
        elif s[0] and not s[1] and s[2]:   # end missing
            r = range(eval(s[0]),end_def,eval(s[2]))
    elif string.count(':') == 1:
        s = string.split(':')
        if s[0] and s[1]:
            r = range(eval(s[0]), eval(s[1])+1)
    elif string.count(':') == 0:
        r = range(eval(string), eval(string)+1)
        
    return r

#@profile
def main(**kwargs):

    if kwargs['range'] is None:
        raise ValueError("range should be specified.")
    
    try:
        COMM=MPI.COMM_WORLD
        if COMM.rank == 0:
            if kwargs['range'] is None:
                raise ValueError('Range error:',kwargs['range'])
            else:
                steps_all = eval_range(kwargs['range'])
                
            steps = split_container(list(steps_all), COMM.size)
        else:
            steps = None
            
        # Scatter steps across cores
        mysteps = COMM.scatter(steps, root=0)
        print('rank:', COMM.rank)
    except:
        mysteps = eval_range(kwargs['range'])
        print('mysteps (no mpi):', mysteps)

    
    fields_proj = ['rho', 'nesq', 'xn']
    fields_slc = ['nH', 'nHI', 'temperature', 'xn', 'ne', 'Erad0', 'Erad1',
                  'velocity_z']
    fields_draw = ['star_particles', 'rho_proj', 'nesq_proj', 'nH', 'temperature', 
                   'velocity_z', 'ne', 'xn', 'Erad0']
    plt_args = dict(zoom=1.6)

    nums = mysteps
    print('ID', COMM.rank, 'nums:', nums)
    ls = tp.LoadSimRPS(kwargs['basedir'], verbose=False)

    # fields to plot
    # zoom factor in the z direction
    figs = pa.create_all_pickles(ls.basedir, ls.problem_id, nums=nums,
                                 fields_slc=fields_slc,
                                 fields_proj=fields_proj,
                                 fields_draw=fields_draw,
                                 force_recal=False, force_redraw=True,
                                 no_save=False, verbose=False, **plt_args)

    return
   
if __name__ == '__main__':

    hostname = socket.gethostname()
    print('Hostname: ', hostname)
    basedir_def = '/tigress/jk11/radps_postproc/R4_4pc_L1024_B2_norun.xymax1024/'
    range_def = '1:31:1'
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--basedir', type=str,
                        default=basedir_def,
                        help='input dir Directory where vtk files are located')
    parser.add_argument('-r', '--range', dest='range', default=range_def,
                        help='range, start:end:stride')
    args = parser.parse_args()

    main(**vars(args))
