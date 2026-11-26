# BSG for the 3D bin packing problem

Description
------
BSG is a beam search guided by a greedy algorithm (Araya and Riff 2014; Araya et al. 2017): it builds
the loading of a container with blocks of boxes placed in maximal free spaces, and evaluates each node
of the beam by completing its partial solution with a greedy algorithm that uses the VCS function.

This version adapts BSG to the **three-dimensional bin packing problem** (3D-BPP, multiple container
loading with identical containers): all the boxes must be loaded into the minimum number of identical
bins (`BSG_BPP`). It derives from `bsg-uld` (air cargo palletization, which derives from the optimized
single-container version of `bsg-clp`) and also contains its two programs:

| program | problem | branch where it was developed |
|---|---|---|
| `BSG_BPP` | 3D bin packing, identical bins | `bsg-bpp` (this one) |
| `BSG_ULD` | air cargo palletization into ULDs (Paquay et al. instances) | `bsg-uld` |
| `BSG_CLP` | single container loading (BR instances) | `bsg-clp` |

The multi-objective variants (BSG-B, NSGA-II), other problems and plugins are available in `master`.

Installation
-------

     git clone -b nico/bpp-mejoras https://github.com/NicoFuentese/Metasolver.git
     cd Metasolver
     mkdir build && cd build
     cmake ..
     make

The branch `nico/bpp-mejoras` is the current version of `BSG_BPP`, derived from `bsg-bpp` of
https://github.com/rilianx/Metasolver. This builds `BSG_BPP`, `BSG_ULD` and `BSG_CLP`. `BSG_BPP` uses
[HiGHS](https://highs.dev) (optional, MIT license) for the recombination of bins (`--milp`); if CMake does not find
it, the program is built without that option. The scripts of the experiments use Python 3 (the analysis programs in
`tools/analysis` also need `numpy` and `scipy`).

On Windows the programs are built with MSYS2 (UCRT64: g++, CMake and HiGHS, `cmake -G "MinGW Makefiles"`), and the
folder with its DLLs (`C:\msys64\ucrt64\bin`) must be in the `PATH` to run them; without it the program ends silently.

3D bin packing (BSG_BPP)
-------

The version of `BSG_BPP` described here is the one used in the paper in `escritos/bpp`; it is in the branch
`nico/bpp-mejoras` of https://github.com/NicoFuentese/Metasolver.

### Algorithm

* **Sequential construction.** The bins are loaded one at a time with BSG (with the double search
  effort, `-t` seconds per bin, default 0.02) using all the remaining boxes. A bin is a `ULD` of
  `BSG_ULD` without cuts, weight limit or center of gravity constraints; all the spaces are anchored at
  the origin of the bin (`--corner_anchor`: at their closest corner).
* **Profit of the boxes.** The value of a loading and the VCS evaluation of the blocks use the profit
  v^kappa of the boxes instead of their volume (`--kappa`, default 2), so the large boxes are loaded
  first and are not left alone in the last bins.
* **Squeaky wheel optimization** (default, `--no_swo` for the ablation). The construction is repeated
  during the time limit (`-T`): after each construction, the profit of the box types of the 10% least
  loaded bins is multiplied by 1.3 (`--swo_rate`), and every profit by a small random factor. The best
  solution is kept: fewer bins and, with the same number, the least loaded bin with less volume. The search
  stops if the number of bins reaches the lower bound.
* **Harvest of bins** (`--harvest K`). Each BSG call runs hundreds of greedy completions and keeps only the
  best bin. With `--harvest K`, the `K` most loaded complete bins found by those greedy runs (distinct, at
  least `--harvest_thr` = 0.95 of the best bin of the call) are also added to the pool of bins. It costs
  about 1 s per instance and fills the pool much faster than the squeaky wheel optimization alone.
* **Recombination of the pool** (`--milp <s>`, needs HiGHS). After the search, all the distinct bins
  generated (the pool) are recombined: a MILP chooses the fewest bins that cover the boxes of every
  type (warm start with the best solution found, 1 thread, `s` seconds). Before the MILP, the LP relaxation
  of the pool is solved: if its ceiling is not smaller than the current number of bins, the solution is
  optimal for the pool and the MILP is skipped (in about 80% of the runs); otherwise the columns that cannot improve
  the solution are removed by reduced cost fixing. With the covering model (default), the boxes covered more than once
  are removed from the last bins chosen, which is only valid without vertical support. With `--partition` every box
  is covered exactly once, so no box is removed and the model can be used with `--support`.
  This step does not exist in the original BSG and it is where the gain over the squeaky wheel
  optimization with the same time comes from (see the ablation below).
* **Vertical support** (`--support none|full|corners|area`, default `none`). With `area` (default
  `--min_overlap 0.7`) at least 70% of the base of every box must rest on other boxes or on the floor.
* **Lower bound.** Maximum of the continuous bound and the bounds L1 and L2 of Martello, Pisinger and
  Vigo (2000) (fixed orientation); with `--rot`, the continuous bound.
* Optional: `--adapt` (with `--milp`) stops the squeaky wheel optimization when the LP of the pool proves that
  the current solution is optimal for it (`-T` becomes a maximum): about 14% less time for 0.07% more bins in
  our tests. `--swo_frac` < 1 gives part of the time to an improvement phase that tries to remove bins with ruin and
  recreate (`Insert` of `BSG_ULD`); it did not improve the results.

### Usage

     ./build/BSG_BPP problems/clp/benchs/MPV/original/class8/200.txt -i 3 -T 20 -t 0.005 --harvest 10 --milp 60 -o sol.csv
     python3 problems/clp/validate_bpp.py problems/clp/benchs/MPV/original/class8/200.txt sol.csv -i 3

Output: `n_bins <bins> lb <lower bound> construction <bins of the first construction> swo <bins after
the squeaky wheel optimization> t_construction <s> time <s>`, a line `milp cols <columns> bins <bins> improved
<0|1> t_milp <s> ...` with `--milp`, and a line `stats` with counters. `-T` is the time of the search and
`--milp` adds its own time limit. Both are wall-clock limits.

Main options (`./build/BSG_BPP -h` for all of them):

```
  -T[double]          Time limit of the search (seconds, wall-clock). Default: 60
  -t[double]          Time limit of BSG in each bin (seconds, without the block generation). Default: 0.02
  -i[int]             Instance in files with several instances (from 1). Default: 1
  --seed=[int]        Seed of the random numbers. Default: 1
  --kappa=[double]    Profit of each box: volume^kappa. Default: 2
  --swo_rate=[double] Increase of the profit of the boxes of the least loaded bins. Default: 0.3
  --swo_sigma=[double] Standard deviation of the log-normal noise of the profits. Default: 0.05
  --swo_bins=[double] Fraction of the least loaded bins whose box types are penalised. Default: 0.1
  --harvest=[int]     Bins added to the pool from each BSG call (with --milp or --pool). Default: 0
  --harvest_thr=[double]  Minimum volume of a harvested bin relative to the best of the call. Default: 0.95
  --milp=[double]     Time limit of the recombination MILP (seconds, in addition to -T). Default: 0 (off)
  --partition         Recombination with the set partitioning model (compatible with --support)
  --milp_plain        Recombination with a plain MILP (without the LP proof and the fixing)
  --adapt             Stop the search when the LP of the pool certifies the solution (needs --milp)
  --support=[string]  none, full, corners or area. Default: none
  --min_overlap=[double]  With --support area: minimum fraction of the base that rests on boxes. Default: 0.7
  --rot               The boxes can be rotated (6 orientations). Default: fixed orientation
  --no_swo, --no_improve, --no_ruin, --no_partial   Ablation of the components
  --pool=[string]     Write the distinct bins generated to a file
  -o[string]          Write the solution (one line per box: bin;item;x;y;z;l;w;h)
  -v                  Print the bins
```

The MILP needs [HiGHS](https://highs.dev) (MIT license): if CMake finds it, `BSG_BPP` is built with `--milp`;
without it the program compiles and works as before but `--milp` gives an error.

### Instances and data

* `problems/clp/benchs/MPV/original/class{1..8}/{50,100,150,200}.txt`: the instances of Martello,
  Pisinger and Vigo (2000), 10 instances per file. Each instance starts with a line with its number, a
  lower bound and an upper bound, followed by `n W H D` and one line per box. Bins of 100x100x100
  (classes 1-5 and 8), 10x10x10 (class 6) and 40x40x40 (class 7). They are in the repository.
* `problems/clp/benchs/MPV/gen_mpv.py`: generator of instances with the same distribution (written from
  the description of the paper, not the original generator; `benchs/MPV/instances`). They were used to
  explore the components. The configurations were chosen with them and with classes 1 and 4-8 of the original
  instances; classes 2 and 3 were not used to choose anything and are a held-out set.
* A single instance can also be given as `n L W H` followed by one line `l w h` per box.
* **Data that is not in the repository.** The industrial instances (`Instance_CG`, the collection that accompanies
  Elhedhli, Gzara and Yildiz 2019), the product catalogue (`products.csv`) and the other collections that the
  team uses are in the shared Google Drive of the team (https://drive.google.com/drive/folders/1Zio_xcEqKU9dFtCF_993NUQHiYxorrf7?usp=drive_link); ask the authors for access if you cannot open it. Place
  them outside the repository (for example in a `Datasets` directory next to it) and point the tools to them
  with `BPP_DATA` (see `tools/README.md`). `tools/instances/convert_instance_cg.py` converts `Instance_CG`
  to the input format of `BSG_BPP` (pallet 1200x800x2055 mm), and `tools/instances/gen_mpv_sets.py`
  regenerates the blind set and the large instances of the paper from their registered seeds.
* The result files of the experiments of the paper are not in the repository either; ask the authors.

`problems/clp/validate_bpp.py` is an independent validator (it does not share code with the solver): every
box loaded exactly once, in an allowed orientation (`--rot`: any of the 6), inside its bin and without
overlapping other boxes; with `--support f`, every box above the floor has at least a fraction `f` of its base
supported. All the solutions reported below were validated with it.

### Results

The experiments, with their protocol, are described in `escritos/bpp` (paper). All the numbers below are the mean
and the sample standard deviation over 3 seeds, with times in wall-clock seconds on an Intel i5-14400 with four
runs in parallel, unless stated otherwise.

**Configurations** (240 original instances, classes 1 and 4-8, fixed orientation; total number of bins):

| configuration | options | bins | time per instance (mean, max) |
|---|---|---|---|
| Fast | `-T 4 -t 0.005 --harvest 10 --milp 30` | 7256.7 ± 0.6 | 6.7 s (34 s) |
| Balanced | `-T 20 -t 0.005 --harvest 10 --milp 60` | 7256.0 ± 1.0 | 25.9 s (80 s) |
| Quality | `-T 100 --milp 100` | 7249.3 ± 1.2 | 100.3 s (201 s) |

Literature (classes 1 and 4-8, fixed orientation; other machines, the times are not comparable): Mahvash et al.
(2018, column generation and branching with CPLEX) 7252, BRKGA (Goncalves and Resende 2013) 7258, space
defragmentation (Zhu et al. 2012) 7269, LCGA (Elhedhli et al. 2019) 7284, GVND (Parreño et al. 2010) 7286,
TS2P (Crainic et al. 2009) 7298, GLS (Faroe et al. 2003) 7302. Fast is at the level of BRKGA, and Balanced is not
distinguishable from Fast; Quality is below BRKGA and below Mahvash et al. (by 2.7 bins, with a different machine
and number of runs). We do not claim to be the best method without rotation.

Classes 2 and 3 (80 instances, not used to choose anything; BRKGA 2519, GVND 2527, Mahvash et al. 2514): Fast 2519.7 ± 0.6,
Balanced 2514.3 ± 0.6, Quality 2514.0 ± 0.0. On the eight classes: 9776.3, 9770.3 and 9763.3 against 9766 of
Mahvash et al. and 9777 of BRKGA.

Bins per class and size (sum of the 10 instances; mean of 3 seeds; LB: lower bound of the instance files;
the other methods are from Table 8 of Goncalves and Resende (2013), `benchs/MPV/literature_goncalves2013.csv`,
averages x 10):

| class | n | LB | BRKGA | GVND | TS2P | GLS | Fast | Balanced | Quality |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 50 | 125 | 134 | 134 | 134 | 134 | 134 | 134 | 134 |
| 1 | 100 | 251 | 266 | 266 | 267 | 267 | 265.7 | 265.3 | 266 |
| 1 | 150 | 347 | 364 | 364 | 370 | 370 | 363.7 | 363 | 363 |
| 1 | 200 | 484 | 508 | 509 | 511 | 512 | 507 | 507 | 507 |
| 4 | 50 | 289 | 294 | 294 | 294 | 294 | 294 | 294 | 294 |
| 4 | 100 | 576 | 590 | 590 | 589 | 590 | 590 | 590 | 590 |
| 4 | 150 | 852 | 868 | 868 | 868 | 868 | 868 | 868 | 868 |
| 4 | 200 | 1163 | 1188 | 1188 | 1188 | 1190 | 1188 | 1188 | 1188 |
| 5 | 50 | 74 | 83 | 83 | 83 | 83 | 83 | 83 | 83 |
| 5 | 100 | 129 | 150 | 150 | 152 | 151 | 150 | 149.7 | 149.3 |
| 5 | 150 | 174 | 200 | 201 | 201 | 202 | 199 | 199.3 | 199 |
| 5 | 200 | 244 | 271 | 271 | 274 | 272 | 270 | 270 | 270 |
| 6 | 50 | 91 | 97 | 98 | 98 | 98 | 98 | 98 | 98 |
| 6 | 100 | 175 | 189 | 190 | 191 | 191 | 188.3 | 188.7 | 188 |
| 6 | 150 | 269 | 290 | 292 | 292 | 294 | 291.3 | 291.3 | 290 |
| 6 | 200 | 350 | 373 | 374 | 377 | 377 | 373 | 373 | 372.7 |
| 7 | 50 | 64 | 74 | 74 | 74 | 74 | 74 | 74 | 74 |
| 7 | 100 | 109 | 122 | 125 | 123 | 123 | 123 | 123.3 | 122.7 |
| 7 | 150 | 137 | 153 | 160 | 158 | 158 | 153 | 153 | 152.3 |
| 7 | 200 | 210 | 234 | 235 | 235 | 235 | 234 | 234 | 233.7 |
| 8 | 50 | 83 | 92 | 92 | 92 | 92 | 92 | 92 | 92 |
| 8 | 100 | 176 | 189 | 189 | 188 | 189 | 189 | 189 | 189 |
| 8 | 150 | 213 | 236 | 241 | 239 | 239 | 234 | 234.3 | 234 |
| 8 | 200 | 267 | 293 | 298 | 300 | 299 | 294.7 | 294 | 291.7 |
| **total** |  | **6852** | **7258** | **7286** | **7298** | **7302** | **7256.7** | **7256.0** | **7249.3** |

**Ablation** (240 original instances, `-T 20 -t 0.005`, mean of 3 seeds; run on a Linux machine with four cores,
`results/bpp/ablation_2026-11`, `problems/clp/experiments/run_ablation.sh`):

| configuration | bins |
|---|---|
| construction with the profit v^2 (`--no_swo --no_improve`) | 7383.3 |
| construction maximizing the volume (kappa = 1) | 7594.0 |
| + squeaky wheel optimization | 7272.3 |
| squeaky wheel optimization without learning (`--swo_rate 0`, only noise) | 7306.3 |
| squeaky wheel optimization with the time of the recombination (`-T 26`) | 7270.7 |
| + recombination (`--milp 60`) | 7256.3 |
| + harvest of bins (`--harvest 10`) | 7254.0 |

The profit v^kappa and the squeaky wheel optimization with learning give most of the gain. The recombination saves
14.3 bins with respect to the squeaky wheel optimization with the same time (Wilcoxon p = 7e-5); with the budget of
Fast the harvest alone is worth 9.3 bins, and with the budget of Balanced it adds 2.3 (not significant). The
recombination improves a solution in roughly 4-14% of the runs and it never made a solution worse. On a blind set of 128
generated instances the LP of the pool leaves at most 0.4% to gain, so with these pools this scheme is near its limit.

**With rotation** (`--rot`, 6 orientations; Mahvash et al. 2018, Table 1, sums of their averages x 10; total bins):

| configuration | classes 1 and 4-8 | classes 2 and 3 | eight classes |
|---|---|---|---|
| Fast | 6840.7 ± 0.6 | 2163.3 ± 0.6 | 9004.0 |
| Balanced | 6836.3 ± 0.6 | 2157.3 ± 3.2 | 8993.7 |
| Quality | 6827.7 ± 0.6 | 2154.7 ± 2.1 | 8982.3 |
| Mahvash et al. (column generation) | 6854 | 2159 | 9013 |

The BRKGA values with rotation of the paper of Goncalves and Resende (6837) are below the lower bound in three
cells, so we do not use them as reference. The time of Quality is lower than that of Mahvash et al. only from about 150 boxes on.

**Vertical support, industrial regime.** The instances of Elhedhli, Gzara and Yildiz (2019) (1200x800x2055 mm
pallet, 50-2000 boxes) were converted to the format of this program; the loaded boxes must have at least 70% of
their base supported (`--support area`). With `--no_improve --kappa 1 -t 2`, the sequential construction
needs 144.4 bins (sum over the 16 cells of 500-2000 boxes of the mean number of bins of 5 instances; 17.9 s per instance,
every box with at least 70% of support, checked with the independent validator) against
153.6 of LCGA (608 s per instance on an Intel i7-5500U). For 50-200 boxes the squeaky wheel loop with `-T 10 -t 0.5 --kappa 1`
needs 110.7 bins in the 80 instances (115.0 for LCGA). The harvest and the recombination with `--partition` (compatible
with the support) did not improve any of the runs in these instances, so the gain comes from the construction and the time per bin.
Caveats: our instances are from the same distribution, but we could not verify that they are the same instances of
the paper; LCGA does not impose the support in every box; the recombination does not scale to 500-1000 boxes
either (it improves a solution in 7 of 108 runs of Fast and in 0 of Quality). Stricter supports are expensive for the block
generator (see the paper).

**Reproduce.** The campaigns of the paper are run and analysed with the programs in `tools/` (see `tools/README.md`):

     python tools/runners/run_campaign.py test --seed 1 --classes 1 --ns 50 --insts 1 "Fast|-T 4 -t 0.005 --harvest 10 --milp 30"
     powershell -File tools/chains/paper_campaigns.ps1 -List

`tools/analysis` recomputes the totals, differences and tests of the paper from the result files. The older scripts
`problems/clp/experiments/run_mpv.sh` and `summarize_mpv.py` run the instances in parallel, validate every solution and
summarize the totals:

     ./problems/clp/experiments/run_mpv.sh results/bpp/x.csv "1 4 5 6 7 8" "$(seq -s' ' 1 10)" 4 -- -T 20 -t 0.005 --harvest 10 --milp 60
     python3 problems/clp/experiments/summarize_mpv.py results/bpp/x.csv

`run_bpp.sh` and `summarize_bpp.py` do the same with the generated instances. The old results of the
construction with the squeaky wheel optimization alone (7274 bins with `-T 30`) are in `results/bpp`.


Code structure
-------
* `metasolver/`: generic search framework (`State`, `SearchStrategy`) and
  strategies: `Greedy`, `BSG` (beam search guided by greedy solutions) and
  `DoubleEffort` (runs BSG doubling the effort until the time limit).
* `problems/clp/`:
  * `clpState`: partial solution (container, remaining boxes and valid blocks),
    instance reading (`new_state`), profits of the boxes (`box_profit`).
  * `Block`: blocks of boxes and guillotine block generation.
  * `Container`: placed blocks and maximal free spaces.
  * `VCS_Function`: VCS evaluation function (volume or profit, pseudo-contact surface,
    volume loss and number of boxes).
  * `ULD`: ULD shapes (cuts, weight, center of gravity).
  * `main_bpp.cpp`, `main_uld.cpp`, `main_clp.cpp`: the three programs.
  * `validate_bpp.py`, `validate_uld.py`: independent validators.
  * `experiments/`: scripts of the experiments; `benchs/`: instances.
* `tools/`: generators and converters of instances, runner and chain of the campaigns of the paper, and the
  analysis programs that recompute its tables (see `tools/README.md`).
* `escritos/`: the drafts of the papers (`bpp`: 3D bin packing; `paper`: air cargo palletization).

Implementation notes
-------
The implementation follows the code optimizations proposed by L. Guesser
in his dissertation (chapter 4):
* free spaces and placed blocks are stored in contiguous vectors
  (no external collision-detection library);
* the pseudo-contact surface is computed by first filtering the placed blocks
  near the selected free space and then evaluating each candidate block;
* blocks are deduplicated with a hash during the block generation;
* the greedy remembers the states already visited (skip feature) and
  rebuilds the rest of the solution instead of evaluating it again.

Besides, the volume loss of a candidate block is only computed when an upper
bound of its evaluation can enter the n best ones, and the blocks of the
instance are stored contiguously in memory.

None of them changes the search: for the same parameters, the solutions found
are the same as in the original implementation (~9x faster).

The default parameters of the evaluation function are the ones tuned by
L. Guesser with irace (alpha=2.4407, beta=2.2652, gamma=0.3896, p=0.0164).
On the BR instances (sets 1-15, 10 instances per set, 30 s) they improve
the volume utilization by ~0.17 percentage points w.r.t. the parameters of
Araya et al. (2017): alpha=4, beta=1, gamma=0.2, p=0.04. With these parameters
the search is the same as in the original implementation.

Single container loading (BSG_CLP)
-------
`BSG_CLP` loads one container maximizing the volume utilization (instances in BR format,
Bischoff and Ratcliff / Davies and Bischoff).


```
./BSG_CLP {OPTIONS} [instance-set]

  OPTIONS:

      -h, --help                        Display this help menu
      -i[int]                           Instance
      --min_fr=[double]                 Minimum volume occupied by a block
                                        (proportion)
      -t[int], --timelimit=[int]        Timelimit (it includes the block generation)
      --alpha=[double]                  Alpha parameter. Default: 2.4407
      --beta=[double]                   Beta parameter. Default: 2.2652
      --gamma=[double]                  Gamma parameter. Default: 0.3896
      --delta=[double]                  Delta parameter
      -p[double]                        p parameter. Default: 0.0164
      --fix_knapsack                    Volume loss: consider the lengths of all
                                        the allowed orientations of the boxes
      instance-set                      The name of the instance set (BR format)
```

`--fix_knapsack`: the knapsack problems used to estimate the volume loss only
consider the orientations LWH, WHL and HLW of each box, which omits valid
lengths in the x and y axes when the box cannot be placed with its length in
vertical. With this option all the allowed orientations are considered (it
does not change the average results significantly).

Example:

     ./build/BSG_CLP problems/clp/benchs/BR/BR2.txt -i 47 -t 10

Air cargo loading (BSG_ULD)
-------
`BSG_ULD` solves the air cargo palletization problem with the instances of
Paquay et al. (2018) (`problems/clp/benchs/ULD`): all the boxes must be loaded
into unit load devices (ULDs) of six types (Boeing 777), minimizing the number of
ULDs. The ULDs are loaded one by one with BSG; the next ULD is selected as in
Hessler et al. (2024) and, at the end, the boxes of the last ULD are reloaded into
a smaller ULD when possible.

Constraints:
* ULD shapes: up to four corners cut in the x-z plane (a block is moved away from
  a cut when it does not fit at the anchor corner of the space);
* weight capacity of the ULD;
* allowed orientations of the boxes and fragile boxes (nothing on top of them);
* support (`--support`): blocks are generated with all their boxes fully supported.
  With `corners` (default, the criterion of Paquay et al. 2018 and Hessler et al. 2024),
  the four bottom corners of each box must rest on non-fragile boxes or on the floor and
  no box can touch the top of a fragile box. With `full`, the blocks are placed on the
  floor or on blocks whose top face is complete and without fragile boxes;
* center of gravity: at most the allowed deviation from the center in x and y. The
  load of each ULD is translated to center its center of gravity, the evaluation of the
  solutions is divided by 1 + p * (relative excess of the deviation), and if the deviation
  is exceeded, the ULD is loaded again anchoring all the spaces at the origin
  (the load is grouped and it can be centered); this is also tried when the ULD is less than
  50% utilized and boxes remain. In the evaluation of the blocks, the VCS value is divided by
  1 + `--cog_greedy` (default 0.5987) * the deviation of the center of gravity after placing the
  block (and translating the load).

With a limited number of ULDs (`--uld_count`), the boxes that were not loaded are inserted
into the loaded ULDs before any ULD is eliminated, by ruin and recreate: a proportion (0.3,
0.6, 0.9) of the volume of each ULD is removed (boxes with nothing on top, from the top) and
the ULDs are loaded again keeping the remaining boxes fixed and adding the unloaded ones.

After the sequential loading, the program tries to eliminate ULDs (`--no_eliminate`
disables it): the boxes of a ULD (from the least utilized) are freed and the other ULDs
are loaded again with their boxes and the freed ones; the boxes that are not loaded pass
to the next ULD. The ULD is eliminated if all the freed boxes are loaded.

Parameters: tuned with irace (`problems/clp/tuning`) on 150 preliminary instances of Paquay
et al. (`benchs/ULD/training`, different from the final ones), 0.1 s per ULD, minimizing
the number of ULDs + 5 * the ULDs with the center of gravity out of range:
cog_penalty=12.6619, cog_greedy=0.5987, max_bl=500 and the VCS parameters alpha=1.2335,
beta=0.2389, gamma=0.2243, p=0.0574.

The solutions are verified box by box. With `-o file` the solution is written (one line
per box: ULD, ULD type, item (line of the instance file, from 0), position and dimensions)
and it can be checked with an independent validator:

     python3 problems/clp/validate_uld.py <instance.csv> problems/clp/benchs/ULD/uld.csv <solution> [--support corners|full|none]

Results on the 300 final instances of Paquay et al. (2018) (30 per size, 10 to 100 boxes),
5 runs per configuration (mean ± standard deviation), all the solutions validated with
`validate_uld.py`, scripts in `problems/clp/experiments` (`run_uld.sh`, `summarize.py`).
Comparison instance by instance with Hessler et al. (2024) (`benchs/ULD/hessler2024_table*.json`):
better means more boxes loaded or, with the same boxes, fewer ULDs.

* paquay: instances of Paquay et al. (Hessler et al.: 708 ULDs, 11.2% of the ULDs with the
  CoG out of range; Paquay et al. 2018: 1010 ULDs);
* adapted: edge of 10 mm with vertical offset 10 mm (substructure allowed), support by area
  (min overlap 0.9, padding 10 mm), CoG deviation 10% of the half dimensions (Hessler et al.:
  653 ULDs);
* one: adapted with one ULD of each type (Hessler et al.: 729 ULDs, 24 boxes not loaded).

CoG xy: ULDs with the CoG out of the allowed deviation in x or y; CoG z: CoG above the maximum
height (Paquay et al. 2016, not considered by Hessler et al.).

| instances | -t (per ULD) | ULDs | boxes not loaded | better / worse | CoG xy | CoG z | avg time |
|---|---|---|---|---|---|---|---|
| paquay  | 0.1 s | 617.0 ± 0.0 | 0 | 91.0 / 0 | 0 | 0 | 0.62 s |
| paquay  | 1 s   | 597.8 ± 0.4 | 0 | 111.2 / 1 | 1 | 0 | 5.4 s |
| adapted | 0.1 s | 598.0 ± 0.0 | 0 | 56.0 / 1 | 2 | 0 | 1.2 s |
| adapted | 1 s   | 576.0 ± 0.0 | 0 | 77.0 / 0 | 1 | 0 | 10.3 s |
| one     | 0.1 s | 706.0 ± 0.0 | 22.0 ± 0.0 | 42.0 / 22.0 | 3 | 0 | 1.6 s |
| one     | 1 s   | 675.8 ± 0.4 | 21.0 ± 0.0 | 64.4 / 20.2 | 2 | 1 | 13.0 s |

Machine: two Intel Xeon E5-2620 v4 (2.1 GHz, 8 cores each), 14 runs in parallel
(`problems/clp/experiments/run_all.sh`; results in `results/server`).

Lower bound (`lower_bound_uld.py`: total volume / largest ULD, total weight / largest capacity,
cliques of incompatible boxes): the number of ULDs is proven optimal in 140 (0.1 s) and 157
(1 s) of the 300 paquay instances (Hessler et al.: 80).

Ablation (0.1 s per ULD, one run, one component turned off; ULDs and ULDs with the CoG out of
range in x or y):

| without | paquay | adapted | one (ULDs, boxes not loaded) |
|---|---|---|---|
| (complete algorithm) | 617 / 0 | 598 / 2 | 706, 22 |
| CoG in the evaluation of the blocks (`--cog_greedy 0`) | 625 / 2 | 607 / 6 | 713, 29 |
| CoG penalty in the value (`--cog_penalty 0`) | 615 / 193 | 590 / 296 | 679, 17 (353 CoG) |
| translation of the load (`--no_translate`) | 624 / 84 | 602 / 84 | 723, 28 (158 CoG) |
| grouped reload (`--no_regroup`) | 622 / 25 | 604 / 31 | 726, 39 |
| elimination of ULDs (`--no_eliminate`) | 620 / 0 | 599 / 2 | 719, 22 |
| substructure (`--no_substructure`) | - | 618 / 1 | 731, 28 |
| all the previous except the CoG penalty and the translation | 630 / 26 | 634 / 61 | 804, 39 |

```
./BSG_ULD {OPTIONS} [instance]

      -t[double]                        Timelimit of the search in each ULD
                                        (seconds, without the block generation). Default: 1
      --cog_penalty=[double]            Penalty p of the deviation of the center of gravity. Default: 12.66
      --support=[string]                corners, full or none. Default: corners
      --max_bl=[int]                    Maximum number of blocks. Default: 500
      --no_eliminate                    Do not try to eliminate ULDs
      --uld=[string]                    ULD file (default: uld.csv in the parent directory of the instance)
      -o[string], --output=[string]     Write the solution to this file
      -v, --verbose                     Print the loaded ULDs
```

Example:

     ./build/BSG_ULD problems/clp/benchs/ULD/Final_instances/n50sample0.csv -t 1 -v
