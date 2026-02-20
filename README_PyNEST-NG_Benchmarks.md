# How I ran mesocircuit benchmarks for PyNEST-NG on Hambach

Hans Ekkehard Plesser, 2026-02-17, 2026-02-20

## Benchmark variants

The Mesocircuit benchmarks exist in several variants testing different
aspects to localize the origin of performance fluctuations. These are
implemented in different branches of this repo. Information on the
branches and how to work with them is given below.

All branches were forked from `my_changes`, but later modifications
there have not been merged into the variant branches.

: `my_changes` This is the main benchmark variant of the
  mesocircuit-model repo.
: `my_swapped` Instead of looping over targets in the outermost loop
  and sources inside, loop over sources in the outermost loop.
: `my_plain_syn` Remove all `syn_spec` arguments from `Connect()`
  calls to eliminate any effects of parameter computation. Number of
  connections remains fixed, but spike numbers will change and may
  make no sense.
: `my_nospatial` Use plain Bernoulli connectivity instead of
  position-dependent connectivity. This creates different numbers of
  connections, so timings cannot be directly compared.
: `my_sw` Simulates the mesocircuit model as is, but with a NEST
  binary built from heplesser's `png-sw` branch, which adds additional
  stopwatches to the spatial pairwise-Bernoulli on target builder. It
  also extracts timings for all individual 73 `Connect()` calls (per
  rank) and reports full data from threaded timers in `stdout`.
: `my_sw_flat` Based on `my_sw`, but combines a fixed connection
  probability with the usual circular mask to separate the time used
  for masked iteration from the time used for probability evaluation.


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


Benchmarks print some data above those tables as well (e.g. random
seed and number of connections; rank 0 only). In the `my_sw*`
branches, also data from threaded timers are output, collected across
all ranks, as NumPy arrays with one row per thread and one column per
rank.


## Details on benchmark variants

1. Each variant has its own branch in this repo.
1. To work with a variant, you need to create a separate virtual
   environment. I strongly recommend to use worktrees with one
   directory per variant. See below for the process.
1. For the `my_sw` benchmarks, you also need to build NEST from the
   `png-sw` branch of `heplesser`'s fork of `mesocircuit-model`.
   

### How to set up runs with a variant

Assume that you have cloned the repo as described above into
`mesocircuit_benchmark/mesocircuit-model`.
   
Then on the frontend, check out the variant branch into a worktree
directory

```shell
cd ~/mesocircuit_benchmark/mesocircuit-model
git worktree add -b my_nospatial ../my_nospatial origin/my_nospatial
```

Then on a compute node 

```shell
module load stable/25.07 gcc ias-6
cd ~/mesocircuit_benchmark
python -venv vmeso_my_nospatial
source vmeso_my_nospatial/bin/activate
pip install parameters
cd my_nospatial
pip install -e .

cd scripts
python prep_meso_hep_4nodes_png.py
```

Finally, back on the frontend node, submit jobs with

```shell
sbatch  ~/mesocircuit_benchmarking/my_nospatial/scripts/mesocircuit_data/mesocircuit_MAMV1/e0fba6424958d2aa5528d0e804476db5/jobscripts/hpc_network_png.sh 
```

Results will be in the corresponding `stdout` folder.

**WARNING: Currently, the SLURM script will NOT fail if sourcing the
`nest_vars.sh` file fails. In that case, the benchmark will run, but
with the stock NEST installed in the `ias6` module. If in doubt, check
`stdout` files for the NEST version running.**

### Properties of the variants and some results

#### `my_changes` 
This is the main benchmark variant of the  mesocircuit-model
repo. 

The main workhorse until `my_sw` came with more timers.

#### `my_swapped` 
Instead of looping over targets in the outermost loop and sources
inside, loop over sources in the outermost loop. 

Did not show much effect, and rather seemed to slow things a little.

#### `my_plain_syn` 

Remove all `syn_spec` arguments from `Connect()` calls to eliminate
any effects of parameter computation. Number of connections remains
fixed, but spike numbers will change and may make no sense.

Results still show long connection times for Main and large variation
for PyNEST-NG, so fluctuations are not caused by synapse parameterization.

#### `my_nospatial`

Use plain Bernoulli connectivity instead of position-dependent
connectivity. This creates different numbers of connections, so
timings cannot be directly compared. 

In this case, the large differences in connect times for different
PyNEST-NG runs seem gone, indicating that spatial connectivity
generation causes the problem here.

#### `my_sw` 

Simulates the mesocircuit model as is, but with a NEST binary built
from heplesser's `png-sw` branch, which adds additional stopwatches to
the spatial pairwise-Bernoulli on target builder (not available for
Master). It also extracts timings for all individual 73 `Connect()`
calls (per rank) and reports full data from threaded timers in `stdout`. 

This branch expects NEST to be installed in `~/nest/bld/png_vmeso_sw`,
but **WILL NOT FAIL IF IT ISN'T**, so check for the extra timers in
the table.

Indicates that actual connection creation is not the problem
(`ctt_call` timer) and that that also takes only little time (about
12s). Also, MPI communication of remote position data (`pool` timer)
does not show fluctuations and is fast, so it is not the cause.

For some time, this branch also har a `for_iter` timer, but this
always reports 0.0 because it was deactivated, as it caused simulation
times to increase by more than a factor 10.

Data also indicated that when a run is slow, one (possibly more) rank
is slow, with thread 0 being slowest (450s instead of 250s), while
other threads on rank are around 320s.

#### `my_sw_flat` 

Based on `my_sw`, but combines a fixed connection probability with the
usual circular mask to separate the time used for masked iteration
from the time used for probability evaluation.  Connection numbers are
approximately matched, but connection creation is faster since the
connection probability kernel does not need to be evaluated.

Preliminary results at this point seem to suggest that large
fluctuations persist in this case, i.e., that it is indeed the mask
iteration that is the cause of the trouble.
