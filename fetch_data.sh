#!/usr/bin/env bash

model=R4_2pc_L512_B10
start=100
end=300
step=1

datadir="/tigress/changgoo/${model}"
outdir="/tigress/${USER}/TIGRESS-DIG/${model}"

################################################################

if [[ ! -d $datadir ]]; then
    echo "[Error]: Data directory $datadir does not exist."
    exit 0
fi

printf "datadir: %s\n" $datadir
printf "outdir: %s\n" $outdir

## Create outdir if it does not exist
[[ -d $outdir ]] || mkdir -p $outdir

## Copy hst output
if [[ -f ${datadir}/id0/${model}.hst ]]; then
    fhst=${datadir}/id0/${model}.hst
    echo "Copy history file: ${fhst}"
    cp ${fhst} ${outdir}/${model}.hst
elif [[ -f ${datadir}/id0/${model}_merged.hst ]]; then
    fhst=${datadir}/id0/${model}_merged.hst
    echo "Copy history file: ${fhst}"
    cp ${fhst} ${outdir}/${model}.hst
elif [[ -f ${datadir}/hst/${model}.hst ]]; then
    fhst=${datadir}/hst/${model}.hst
    echo "Copy history file: ${fhst}"
    cp ${fhst} ${outdir}/${model}.hst
else
    echo "[Warning]: Couldn't find history file."
fi

## Copy starpar vtk files
echo "Copy starpar vtk: "
for i in $(seq $start $step $end) ; do
    printf "%d " $i
    num=$(printf "%04d" $i)
    f="${model}.${num}.starpar.vtk"
    [[ ! -f ${datadir}/$f ]] || echo "[Warning]: Couldn't find starpar file ${datadir}/${f}."
    [[ -f ${outdir}/$f ]] || cp $datadir/starpar/$f $outdir/
done
printf "\n"

## Dump input parameters to athinput.${model}
rst=( $(find $datadir/rst -name ${model}.????.rst 2> /dev/null ) )
if [[ -f ${rst[0]} ]]; then
    echo "Extract athinput from restart file" ${rst[0]}
    parfile=${rst[0]}
    sed -n -e '/<comment>/,/<par_end>/ p' $parfile > $outdir/athinput.$model
elif [[ -f ${datadir}/out.txt ]]; then
    echo "Extract athinput from out.txt" ${rst[0]}
    parfile=${datadir}/out.txt
    sed -n -e '/<comment>/,/PAR_DUMP/ p' $parfile > $outdir/athinput.$model
else
    out=( $(find $datadir -name ${model}.*.out 2> /dev/null ) )
    echo "Extract athinput from " ${out[0]}
    parfile=${out[0]}
    sed -n -e '/<comment>/,/PAR_DUMP/ p' $parfile > $outdir/athinput.$model
fi

if [[ ! -f ${parfile} ]]; then
    echo "[Warning]: Couldn't find restart files or out.txt"
fi

## Join vtk files using bash wrapper
join=./vtk/join.sh
$join -i $datadir -o $outdir -r $start:$end:$step

## join vtk using parallel python wrapper for join.sh
#joinpy=$HOME/athena-tigress/vtk/join_parallel.py
# python $joinpy -i $datadir -o $outdir -r $start:$end:$step
