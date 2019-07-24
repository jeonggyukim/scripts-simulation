#!/usr/bin/env python

import glob
import os
import argparse

def rename_problem_id(basedir, problem_id_orig, problem_id_new,
                      verbose=True):
    """Change problem_id of athena simulation output
    """
    files = glob.glob(os.path.join(basedir, '*/*.*'))
    for fname in files:
        if problem_id_orig in fname:
            fname_new = fname.replace('{0:s}.'.format(problem_id_orig),
                                      '{0:s}.'.format(problem_id_new))
            print(fname,fname_new)

            os.rename(fname, fname_new)
            if verbose:
                print('Rename {0:s} to {1:s}', fname, fname_new)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--basedir', type=str,
                        default='',
                        help='base directory')
    parser.add_argument('-o', '--old', type=str,
                        default='',
                        help='old problem id')
    parser.add_argument('-n', '--new', type=str,
                        default='',
                        help='new problem id')
    args = parser.parse_args()

    v = vars(args)
    print(v)
    rename_problem_id(v['basedir'], v['old'], v['new'], verbose=True)
