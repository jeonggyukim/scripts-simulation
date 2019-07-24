#!/bin/bash
#SBATCH --job-name=R2_2pc_L256_B2.rst
#SBATCH -N 8
#SBATCH -n 224
#SBATCH -t 00:30:00
#SBATCH --mail-type=begin
#SBATCH --mail-type=end
#SBATCH --mail-user=kimjg@astro.princeton.edu
#SBATCH --error=R2_2pc_%j.err
#SBATCH --output=R2_2pc_%j.out
#

# NPROCS="$(($SLURM_NNODES * $SLURM_CPUS_ON_NODE))"
NPROCS=224

PROBLEM=R2_2pc_L256_B2
RST_STEP=0009

JOBID_ORIG=R2_2pc_L256_B2
JOBID_RST=R2_2pc_L256_B2.rst

ATHENADIR=$HOME/athena-tigress-cooling
ATHENA=$ATHENADIR/bin/tigress_rt

RSTDIR=/tigress/changgoo/R2_2pc_L256_B2/rst
RUNDIR=/scratch/gpfs/jk11/TIGRESS-RT/$JOBID_RST

#EXECUTABLE=$RUNDIR_ORIG/athena
EXECUTABLE=$ATHENA

echo "Preparing:"

if [ ! -d $RUNDIR ]; then
    mkdir -p $RUNDIR
fi

cp $EXECUTABLE $RUNDIR/.
cd $RUNDIR

[[ -d rst ]] || mkdir rst
#for d in $(find ${RUNDIR_ORIG} -maxdepth 1 -type d -name 'id*') ; do cp ${d}/${PROBLEM}*${RST_STEP}.rst ./rst/ ; done;

# cp $RSTDIR/${PROBLEM}*${RST_STEP}.rst ./rst/ 

echo "Checking:"
pwd

echo Time is `date`
echo Directory is `pwd`
echo Number of Processors is $NPROCS

module load intel intel-mpi fftw

srun $EXECUTABLE -r ${RUNDIR}/rst/${PROBLEM}.${RST_STEP}.rst 1> $RUNDIR/log.txt 2> $RUNDIR/err.txt

# srun $mpirun -np $NPROCS $EXECUTABLE -r ${RUNDIR}/rst/${PROBLEM}.${RST_STEP}.rst 1> $RUNDIR/log.txt 2> $RUNDIR/err.txt

echo "Stopping:"
date

echo "Done."
