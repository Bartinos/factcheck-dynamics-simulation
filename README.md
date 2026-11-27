# Network simulation

## Run the interactive visualization

```bash
uv run solara run server.py
```

Open the local address printed in the terminal. Click **Step** to see which
agents believe the claim and how prevalence changes, one step at a time. Red
nodes believe the claim and blue nodes reject it. Use play and pause to watch
the run continuously.

Choose the fact-check step and peer influence in the sidebar, then click
**Reset** to apply the settings. Reset reuses the same network, initial beliefs,
and random seed so you can compare settings on the same starting state.

## Run the experiment

```bash
uv run --locked python batch_run.py results --seed 42
```

This runs 30 replications per condition for a total of 120 runs. Add
`--replications 1` for a four-run pilot. Choose a new output directory each
time so existing CSVs are preserved.

Each run generates a new random network with 200 nodes and an expected mean
degree of six. The network remains fixed for its 100 steps. The run seed
determines the network, the 20 randomly selected initial believers, and the
random draws used by the model. To replay one run from Python, pass its
`run_seed`, `fact_check_step`, and `peer_influence` to `run_simulation` in
`batch_run.py`.

- `runs.csv` records the seeds, settings, peak and final prevalence, and the
  first step strictly below 5%. The step field is blank when
  `threshold_reached` is false.
- `trajectories.csv` records prevalence at steps 0 through 100 and joins to
  `runs.csv` by `run_seed`.

## Summarize a batch in R

Generate the batch as shown above, then open `analysis.Rmd` in RStudio.
Run the chunks in order to inspect the CSVs, calculate the summaries, and draw
the prevalence plot with `ggplot2`.

```r
install.packages("ggplot2")
```

Run the install command once if needed. Edit `results_dir` in the first chunk
to use a different batch. Run the export chunk to save both outputs in that
directory.

- `prevalence-by-condition.pdf` shows each run and the condition mean, with
  shared axes and a vertical line at each condition's fact-check step.
- `condition-summary.csv` reports the mean and standard deviation of peak and
  final prevalence, along with counts of runs that reached or never reached
  the persistence threshold. Standard deviations are blank for a one-run pilot.
