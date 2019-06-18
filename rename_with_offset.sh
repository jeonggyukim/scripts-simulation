#!/usr/bin/env bash

offset=1
problem_id=R8_4pc_newacc

dirA=/tigress/jk11/radps_postproc/R8_4pc_newacc.xymax1024
dirB=/tigress/jk11/radps_postproc/R8_4pc_newacc.xymax1024_new

START=445
END=572
STEP=1

for i in $(seq $START $STEP $END) ; do
    ii=$(printf "%04d" $i)
    jj=$(printf "%04d\n" $(($i - $offset)))
    # Move joined vtk files
    mv ${dirA}/vtk/${problem_id}.${ii}.vtk ${dirB}/vtk/${problem_id}.${jj}.vtk
    # Move starpar vtk files
    mv ${dirA}/starpar/${problem_id}.${ii}.starpar.vtk ${dirB}/starpar/${problem_id}.${jj}.starpar.vtk
done

# Move zprof
declare -a arr=("phase1" "phase2" "phase3" "phase4" "phase5" "whole")

for ph in "${arr[@]}" ; do
    echo "Rename ${problem_id}.????.$ph.zprof with offset $offset."
    for i in $(seq $START $STEP $END) ; do
        ii=$(printf "%04d" $i)
        jj=$(printf "%04d\n" $(($i - $offset)))
        mv ${dirA}/zprof/${problem_id}.${ii}.${ph}.zprof ${dirB}/zprof/${problem_id}.${jj}.${ph}.zprof
    done
done
