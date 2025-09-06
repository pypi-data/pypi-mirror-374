#!/bin/bash

#SBATCH --account=omr@v100
#SBATCH -C v100-32g
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=10
#SBATCH --hint=nomultithread
#SBATCH --time=2:00:00
#SBATCH --qos=qos_gpu-dev
#SBATCH --job-name=pl_test
#SBATCH --error=test_pl_%j.log
#SBATCH --output=test_pl_%j.log


# Enable the standard and error outputs of Python.
export PYTHONUNBUFFERED=1

module load pytorch-gpu/py3/2.6.0

cd /lustre/fswork/projects/rech/omr/uuf18sd/zarrdataset

source .venv/bin/activate

# Avoid no space left in device on Jean Zay.
export TMPDIR=$JOBSCRATCH

srun python tests/test_it_ds_pl.py

returned_code=$?
echo "> script completed with exit code ${returned_code}"
exit ${returned_code}
