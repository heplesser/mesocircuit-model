# How I ran mesocircuit benchmarks for PyNEST-NG on Hambach

Hans Ekkehard Plesser, 2026-02-17

## my_sw_flat (Stopwatch, flat probability)

This version uses a fixed probability inside the mask to differentiate mask costs from random number costs.

This version is for use with the png-sw branch of NEST (heplesser), which provides additional stopwatches for spatial connection creation.

Stopwatch data are read written to stdout.
Also collects timings for individual Connect() calls from Python level and writes to stdout.

## Preparations and NEST builds

### Front end node

Do git-stuff on frontend.

```
mkdir -p nest/src
cd nest/src
git clone git@github.com:heplesser/nest-simulator.git
mv nest-simulator main
cd main
git fetch
git worktree add -b pynest-ng ../pynest-ng origin/pynest-ng

cd ../..
mkdir bld
cd bld
mkdir main_meso
mkdir png_meso

cd ~
mkdir mesocircuit-benchmarking
cd mesocircuit-benchmarking
git clone git@github.com:heplesser/mesocircuit-model.git
cd mesocircuit-model
git checkout my_changes
```

### Compute node


Most preparation needs to be done on a actual compute node, so

```
srun --pty --time 2:00:00 --partition hamsteinZen3 --cpus-per-task=128 bash -l
```

The on that node (create the venv and install mesocircuit only once)

```
module load stable/25.07 ias6 gcc
cd mesocircuit-benchmarking

python -m venv vmeso
source vmeso/bin/activate
pip install -e .
pip install parameters
```

#### Build nest in both versions

```
cd ~/nest/bld/main_meso
cmake -DCMAKE_INSTALL_PREFIX=`pwd`/install -Dwith-mpi=ON -Dwith-optimize="-O3 -DNDEBUG -mtune=native -march=native" ../../src/main
make -j64 install

cd ~/nest/bld/png_meso
cmake -DCMAKE_INSTALL_PREFIX=`pwd`/install -Dwith-mpi=ON -Dwith-optimize="-O3 -DNDEBUG -mtune=native -march=native" ../../src/pynest-ng
make -j64 install
```

#### Create the jobscripts

This must be done on a compute node, since the necessary modules are not available on the front end.

##### Downscaled (1 node, N 20%, K 10%)

```
python prep_meso_hep_1node_png.py
python prep_meso_hep_1node_main.py 
```

##### Full scale on 4 nodes

```
python prep_meso_hep_4nodes_png.py
python prep_meso_hep_4nodes_main.py 
```

## Job submission

This happens on the front end node:

```
sbatch  ~/mesocircuit_benchmarking/mesocircuit-model/scripts/mesocircuit_data/mesocircuit_MAMV1/e0fba6424958d2aa5528d0e804476db5/jobscripts/hpc_network_main.sh 
```

This is an example for the full-scale case with NEST master. For the downscaled one, jobscripts are in `.../local_mesocircuit_MAMV1/.../jobscripts` and for the PyNEST-NG executable, the file name is `hpc_network_png.sh`.

## Results

Results are in

```
~/mesocircuit_benchmarking/mesocircuit-model/scripts/mesocircuit_data/mesocircuit_MAMV1/e0fba6424958d2aa5528d0e804476db5/stdout
~/mesocircuit_benchmarking/mesocircuit-model/scripts/mesocircuit_data/local_mesocircuit_MAMV1/868c447eaf70596aa70738cb0ffaad3b/stdout
```

respectively in files names `network_[main|png]_{jobid}.txt`.  Look for timing tables at the end of the file.


