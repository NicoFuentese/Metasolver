# BSG for the 3D bin packing problem (branch `bsg-bpp`)

Description
------
BSG is a beam search guided by a greedy algorithm (Araya and Riff 2014; Araya et al. 2017): it builds
the loading of a container with blocks of boxes placed in maximal free spaces, and evaluates each node
of the beam by completing its partial solution with a greedy algorithm that uses the VCS function.

This branch adapts BSG to the **three-dimensional bin packing problem** (3D-BPP, multiple container
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

     git clone -b bsg-bpp https://github.com/rilianx/Metasolver.git
     cd Metasolver
     mkdir build && cd build
     cmake ..
     make

This builds `BSG_BPP`, `BSG_ULD` and `BSG_CLP`. `BSG_BPP` uses [HiGHS](https://highs.dev) (optional, MIT license)
for the set covering recombination (`--milp`); if CMake does not find it, the program is built without that option.
The scripts of the experiments use Python 3.

3D bin packing (BSG_BPP)
-------

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
* **Recombination by set covering** (`--milp <s>`, needs HiGHS). After the search, all the distinct bins
  generated (the pool) are recombined: the MILP chooses the fewest bins that cover the boxes of every
  type (warm start with the best solution found, 1 thread, `s` seconds). Before the MILP, the LP relaxation
  of the pool is solved: if its ceiling is not smaller than the current number of bins, the solution is
  optimal for the pool and the MILP is skipped (about 85% of the instances); otherwise the columns that cannot improve
  the solution are removed by reduced cost fixing. The boxes covered more than once are removed from the
  last bins chosen. This step does not exist in the original BSG and it is where most of the gain over the
  squeaky wheel optimization comes from (see the ablation below). It is only valid without vertical
  support (`--support none`).
* **Vertical support** (`--support none|full|corners|area`, default `none`). With `area` (default
  `--min_overlap 0.7`) at least 70% of the base of every box must rest on other boxes or on the floor.
* **Lower bound.** Maximum of the continuous bound and the bounds L1 and L2 of Martello, Pisinger and
  Vigo (2000) (fixed orientation).
* Optional: `--adapt` (with `--milp`) stops the squeaky wheel optimization when the LP of the pool proves that
  the current solution is optimal for it (`-T` becomes a maximum): 14% less time for 0.07% more bins in
  our tests. `--swo_frac` < 1 gives part of the time to the emptying of bins with ruin and recreate
  (`Insert` of `BSG_ULD`), which did not improve the results.

### Usage

     ./build/BSG_BPP problems/clp/benchs/MPV/original/class8/200.txt -i 3 -T 20 -t 0.005 --harvest 10 --milp 60 -o sol.csv
     python3 problems/clp/validate_bpp.py problems/clp/benchs/MPV/original/class8/200.txt sol.csv -i 3

Output: `n_bins <bins> lb <lower bound> construction <bins of the first construction> swo <bins after
the squeaky wheel optimization> t_construction <s> time <s>`, a line `milp cols <columns> bins <bins> improved
<0|1> t_milp <s> ...` with `--milp`, and a line `stats` with counters. `-T` is the time of the search and
`--milp` adds its own time limit.

Main options (`./build/BSG_BPP -h` for all of them):

```
  -T[double]          Time limit of the search (seconds, CPU time). Default: 60
  -t[double]          Time limit of BSG in each bin (seconds, without the block generation). Default: 0.02
  -i[int]             Instance in files with several instances (from 1). Default: 1
  --seed=[int]        Seed of the random numbers. Default: 1
  --kappa=[double]    Profit of each box: volume^kappa. Default: 2
  --swo_rate=[double] Increase of the profit of the boxes of the least loaded bins. Default: 0.3
  --harvest=[int]     Bins added to the pool from each BSG call (with --milp or --pool). Default: 0
  --milp=[double]     Time limit of the set covering MILP (seconds, in addition to -T). Default: 0 (off)
  --adapt             Stop the search when the LP of the pool certifies the solution (needs --milp)
  --support=[string]  none, full, corners or area. Default: none
  --rot               The boxes can be rotated (6 orientations). Default: fixed orientation
  --no_swo, --no_improve, --no_ruin, --no_partial   Ablation of the components
  --pool=[string]     Write the distinct bins generated to a file
  -o[string]          Write the solution (one line per box: bin;item;x;y;z;l;w;h)
  -v                  Print the bins
```

The MILP needs [HiGHS](https://highs.dev) (MIT license): if CMake finds it, `BSG_BPP` is built with `--milp`;
without it the program compiles and works as before but `--milp` gives an error.

### Instances

* `problems/clp/benchs/MPV/original/class{1..8}/{50,100,150,200}.txt`: the instances of Martello,
  Pisinger and Vigo (2000), 10 instances per file. Each instance starts with a line with its number, a
  lower bound and an upper bound, followed by `n W H D` and one line per box. Bins of 100x100x100
  (classes 1-5 and 8), 10x10x10 (class 6) and 40x40x40 (class 7).
* `problems/clp/benchs/MPV/gen_mpv.py`: generator of instances with the same distribution (written from
  the description of the paper, not the original generator; `benchs/MPV/instances`). They were used to
  explore the components. The configurations were chosen with them and with classes 1 and 4-8 of the original
  instances; classes 2 and 3 were never used to choose anything and are the held-out set.
* A single instance can also be given as `n L W H` followed by one line `l w h` per box.

`problems/clp/validate_bpp.py` is an independent validator (it does not share code with the solver): every
box loaded exactly once, in an allowed orientation (`--rot`: any of the 6), inside its bin and without
overlapping other boxes. All the solutions reported below were validated with it.

### Results

**Configurations** (240 original instances, classes 1 and 4-8, fixed orientation, mean and standard deviation of
the total number of bins over 3 seeds, CPU time per instance on an Intel i5-14400, several runs in parallel):

| configuration | options | bins | time per instance (mean, max) |
|---|---|---|---|
| F5 (fast) | `-T 4 -t 0.005 --harvest 10 --milp 30` | 7259.3 ± 2.1 | 6.8 s (34 s) |
| H20 (balanced) | `-T 20 -t 0.005 --harvest 10 --milp 60` | 7253.0 ± 1.0 | 25.6 s (81 s) |
| B100 (quality) | `-T 100 --milp 100` | 7250.0 ± 1.0 | 110 s (about 200 s) |

Literature (classes 1 and 4-8, fixed orientation; other machines, the times are not comparable): Mahvash et al.
(2018, column generation and branching with CPLEX) 7252, BRKGA (Goncalves and Resende 2013) 7258, space
defragmentation (Zhu et al. 2012) 7269, LCGA (Elhedhli et al. 2019) 7284, GVND (Parreño et al. 2010) 7286,
TS2P (Crainic et al. 2009) 7298, GLS (Faroe et al. 2003) 7302. F5 is on par with BRKGA with a fraction of the
time; H20 and B100 are below BRKGA, and only B100 is below Mahvash et al. (by 2 bins, with a different machine
and number of runs). We do not claim to be the best method without rotation.

Held-out classes 2 and 3 (80 instances, never used to choose anything; BRKGA 2519, GVND 2527, Mahvash et al. 2514):
F5 2521.0 ± 2.6 (3 seeds), and with the earlier configuration SWO 33 s + MILP 60 s 2517.0 ± 1.3 (5 seeds)
against 2527.8 for the squeaky wheel optimization alone with the same time.

Bins per class and size (sum of the 10 instances; mean of 3 seeds; LB: lower bound of the instance files;
the other methods are from Table 8 of Goncalves and Resende (2013), `benchs/MPV/literature_goncalves2013.csv`,
averages x 10):

| class | n | LB | BRKGA | GVND | TS2P | GLS | F5 | H20 | B100 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 50 | 125 | 134 | 134 | 134 | 134 | 134 | 134 | 134 |
| 1 | 100 | 251 | 266 | 266 | 267 | 267 | 265.7 | 265 | 265.7 |
| 1 | 150 | 347 | 364 | 364 | 370 | 370 | 363 | 363 | 363 |
| 1 | 200 | 484 | 508 | 509 | 511 | 512 | 507.7 | 507 | 507 |
| 4 | 50 | 289 | 294 | 294 | 294 | 294 | 294 | 294 | 294 |
| 4 | 100 | 576 | 590 | 590 | 589 | 590 | 590 | 590 | 590 |
| 4 | 150 | 852 | 868 | 868 | 868 | 868 | 868 | 868 | 868 |
| 4 | 200 | 1163 | 1188 | 1188 | 1188 | 1190 | 1188 | 1188 | 1188 |
| 5 | 50 | 74 | 83 | 83 | 83 | 83 | 83 | 83 | 83 |
| 5 | 100 | 129 | 150 | 150 | 152 | 151 | 150 | 149.3 | 149.3 |
| 5 | 150 | 174 | 200 | 201 | 201 | 202 | 199.3 | 199.3 | 199 |
| 5 | 200 | 244 | 271 | 271 | 274 | 272 | 270 | 270 | 270 |
| 6 | 50 | 91 | 97 | 98 | 98 | 98 | 98.3 | 98 | 98 |
| 6 | 100 | 175 | 189 | 190 | 191 | 191 | 188.7 | 188 | 188.3 |
| 6 | 150 | 269 | 290 | 292 | 292 | 294 | 291.7 | 291 | 290.3 |
| 6 | 200 | 350 | 373 | 374 | 377 | 377 | 373.3 | 373 | 372.3 |
| 7 | 50 | 64 | 74 | 74 | 74 | 74 | 74 | 74 | 74 |
| 7 | 100 | 109 | 122 | 125 | 123 | 123 | 123 | 122.7 | 123 |
| 7 | 150 | 137 | 153 | 160 | 158 | 158 | 153 | 153 | 152.7 |
| 7 | 200 | 210 | 234 | 235 | 235 | 235 | 234 | 234 | 234 |
| 8 | 50 | 83 | 92 | 92 | 92 | 92 | 92 | 92 | 92 |
| 8 | 100 | 176 | 189 | 189 | 188 | 189 | 189 | 189 | 189 |
| 8 | 150 | 213 | 236 | 241 | 239 | 239 | 234.7 | 234 | 234 |
| 8 | 200 | 267 | 293 | 298 | 300 | 299 | 295 | 293.7 | 291.3 |
| **total** | | **6852** | **7258** | **7286** | **7298** | **7302** | **7259.3** | **7253.0** | **7250.0** |

**Ablation** (240 original instances, `-T 20 -t 0.005`, mean of 2 seeds):

| configuration | bins |
|---|---|
| construction with the profit v^2 (`--no_swo --no_improve`) | 7383.5 |
| construction maximizing the volume (kappa = 1) | 7608.5 |
| + squeaky wheel optimization | 7268.0 |
| squeaky wheel optimization without learning (`--swo_rate 0`, only noise) | 7307.5 |
| + set covering MILP (`--milp 60`) | 7258.0 |
| + harvest of bins (`--harvest 10`) | 7252.5 |

The profit v^kappa and the squeaky wheel optimization with learning give most of the gain. The MILP and the
harvest add 10 and 5 bins (with the budget of F5 the harvest alone is worth 10 bins in the 3-seed tests). On
the held-out classes 2 and 3 the MILP saves 10.8 bins in 80 instances (Wilcoxon p = 0.0002). The MILP improves
1 bin in about 4-13% of the instances, and it never made a solution worse in our campaigns. The LP of the pool
leaves at most 0.5% to gain, so this scheme is near its limit.

**With rotation** (`--rot`, 6 orientations; Mahvash et al. 2018, Table 1, sums of their averages x 10): B100 gives
6831.0 ± 2.0 bins in classes 1 and 4-8 (3 seeds, 98 s per instance) against 6854 of their column generation, and
2154.3 ± 0.6 in classes 2 and 3 (3 seeds, 117 s) against 2159; all the classes: 8985.3 against 9013 (-0.31%). F5 and
H20 with rotation give 6840.0 in classes 1 and 4-8. The BRKGA values with rotation of the paper of Goncalves and
Resende (6837) are below the lower bound in three cells, so we do not use them as reference.

**Vertical support, industrial regime.** The instances of Elhedhli, Gzara and Yildiz (2019) (1200x800x2055 mm
pallet, 50-2000 boxes) were converted to the format of this program; the loaded boxes must have at least 70% of
their base supported (`--support area`). With `--no_improve --kappa 1 -t 2`, the sequential construction
needs 144.6 bins (sum over the 16 cells of 500-2000 boxes of the mean number of bins of 5 instances; one run per
instance, 18 s per instance, every box with at least 70% of support, checked with an independent script) against
153.6 of LCGA (608 s per instance on an Intel i7-5500U). Most of this gain comes from the time per bin (`-t 2`); `--kappa 1` only helps with
instances built from a product catalog. Caveats: our instances are from the same distribution, but we could not
verify that they are the same instances of the paper; LCGA does not impose the support in every box; the MILP
does not scale to 500-1000 boxes (it improves 1 of 36 instances) and it is not used there. Stricter supports
are expensive for the block generator (at least 85% of the base: +10% of bins; fully supported boxes: +80%).

**Reproduce** (`results/bpp`):

     ./problems/clp/experiments/run_mpv.sh results/bpp/x.csv "1 4 5 6 7 8" "$(seq -s' ' 1 10)" 4 -- -T 20 -t 0.005 --harvest 10 --milp 60
     python3 problems/clp/experiments/summarize_mpv.py results/bpp/x.csv

`run_mpv.sh` runs the instances in parallel, writes the solutions and validates them;
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
