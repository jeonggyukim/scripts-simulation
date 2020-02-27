#!/usr/bin/env bash

# Delete id-*.????.vtk files in gpfs
# Use after vtk files are joined.

START=0
END=400
STEP=1

BASEDIR="/scratch/gpfs/${USER}/TIGRESS-RT/R4_4pc.RT.nowind"
PROBLEM_ID="R4"

printf "Base directory: %s\n" "${BASEDIR}"
printf "Delete vtk files: "
for i in $(seq $START $STEP $END) ; do echo -n "$i " ; done; echo

confirm() {
    # call with a prompt string or use a default
    read -r -p "${1:-Are you sure? [y/N]} " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            true
            ;;
        *)
            false
            ;;
    esac
}

# read -n 1 -s -r -p "Press any key to continue"
if confirm ; then
    for i in $(seq $START $STEP $END)
    do
        ivtk=$(printf "%04d" $i)
        find ${BASEDIR} -name "${PROBLEM_ID}-id*.${ivtk}.vtk" -print0 \
            | xargs -0 -r /bin/rm -f
    done
fi
