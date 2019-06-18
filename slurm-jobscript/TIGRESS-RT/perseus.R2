#!/bin/bash
#SBATCH --job-name=R2_2pc_rad.xymax128
#SBATCH -N 9
#SBATCH -n 252
#SBATCH -t 48:00:00
#SBATCH --mail-type=begin
#SBATCH --mail-type=end
#SBATCH --mail-user=kimjg@astro.princeton.edu
#SBATCH --error=R2_2pc_%j.err
#SBATCH --output=R2_2pc_%j.out
#

NPROCS="$(($SLURM_NNODES * $SLURM_CPUS_ON_NODE))"

JOBID=R2_2pc_rad.xymax128
ATHINPUT=athinput.R2
ATHENA=athena

ATHENADIR=$HOME/athena-tigress-cooling
INPUT=$ATHENADIR/athinput/TIGRESS-RT/$ATHINPUT
RUNDIR=/scratch/gpfs/$USER/TIGRESS-RT/$JOBID

# Create run directory
if [ -d $RUNDIR ] ; then
    rm -rf $RUNDIR/*
else
    mkdir -p $RUNDIR
fi

# Copy athena and athinput
cp $ATHENADIR/bin/$ATHENA $RUNDIR/.
cp $INPUT $RUNDIR/.
cd $RUNDIR

echo "Checking:"
pwd

echo "Time: $(date)"
echo "Directory: $(pwd)"
echo "Number of Processors: $NPROCS"

module load intel intel-mpi fftw

srun $ATHENA -i $ATHINPUT 1> $RUNDIR/out.txt 2> $RUNDIR/err.txt
#srun athena -i $ATHINPUT domain1/AutoWithNProc=64 1> $RUNDIR/out.txt 2> $RUNDIR/err.txt
#srun athena -i $ATHINPUT job/problem_id=$JOBID domain1/AutoWithNProc=$NPROCS 1> $RUNDIR/out.txt 2> $RUNDIR/err.txt
