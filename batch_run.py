import argparse
import csv
from itertools import product
from pathlib import Path
from random import Random

import networkx as nx

from model import NetworkModel


AGENT_COUNT = 200
TARGET_MEAN_DEGREE = 6
INITIAL_BELIEVER_COUNT = 20
BASELINE_ADOPTION_PROBABILITY = 0.02
CORRECTION_PROBABILITY = 0.70
FACT_CHECK_STEPS = (5, 20)
PEER_INFLUENCE_LEVELS = (0.20, 0.60)
STEPS = 100
THRESHOLD = 0.05


def run_simulation(run_seed, fact_check_step, peer_influence):
    seeds = Random(run_seed)
    graph = nx.fast_gnp_random_graph(
        AGENT_COUNT,
        TARGET_MEAN_DEGREE / (AGENT_COUNT - 1),
        seed=seeds.getrandbits(64),
    )
    initial_believers = Random(seeds.getrandbits(64)).sample(
        list(graph), INITIAL_BELIEVER_COUNT
    )
    model = NetworkModel(
        graph,
        initial_believers=initial_believers,
        p0=BASELINE_ADOPTION_PROBABILITY,
        peer_influence=peer_influence,
        fact_check_step=fact_check_step,
        correction_probability=CORRECTION_PROBABILITY,
        rng=seeds.getrandbits(64),
    )
    for _ in range(STEPS):
        model.step()
    return model


def summarize_prevalence(history):
    first_below = next(
        (step for step, prevalence in enumerate(history) if prevalence < THRESHOLD),
        None,
    )
    return {
        "peak_prevalence": max(history),
        "final_prevalence": history[-1],
        "threshold_reached": first_below is not None,
        "first_below_threshold_step": first_below,
    }


def run_experiment(output_dir, replications, batch_seed):
    conditions = tuple(product(FACT_CHECK_STEPS, PEER_INFLUENCE_LEVELS))
    run_seeds = iter(Random(batch_seed).sample(range(1 << 48), len(conditions) * replications))
    summaries = []
    trajectories = []

    for replication in range(1, replications + 1):
        for fact_check_step, peer_influence in conditions:
            run_seed = next(run_seeds)
            model = run_simulation(run_seed, fact_check_step, peer_influence)
            summaries.append(
                {
                    "batch_seed": batch_seed,
                    "run_seed": run_seed,
                    "replication": replication,
                    "fact_check_step": fact_check_step,
                    "peer_influence": peer_influence,
                    "agent_count": AGENT_COUNT,
                    "initial_believer_count": INITIAL_BELIEVER_COUNT,
                    "target_mean_degree": TARGET_MEAN_DEGREE,
                    "realized_mean_degree": 2 * model.graph.number_of_edges() / AGENT_COUNT,
                    "baseline_adoption_probability": BASELINE_ADOPTION_PROBABILITY,
                    "correction_probability": CORRECTION_PROBABILITY,
                    "steps": STEPS,
                    "threshold": THRESHOLD,
                    **summarize_prevalence(model.prevalence_history),
                }
            )
            trajectories.extend(
                (run_seed, step, prevalence)
                for step, prevalence in enumerate(model.prevalence_history)
            )

    output_dir.mkdir(parents=True)
    with (output_dir / "runs.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)
    with (output_dir / "trajectories.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("run_seed", "step", "prevalence"))
        writer.writerows(trajectories)


def main():
    parser = argparse.ArgumentParser(description="Run the four fact-checking conditions.")
    parser.add_argument("output_dir", type=Path, help="New directory for the two CSV files.")
    parser.add_argument("--replications", type=int, default=30, help="Runs per condition.")
    parser.add_argument("--seed", type=int, required=True, help="Seed for the batch.")
    args = parser.parse_args()
    if args.replications < 1:
        parser.error("--replications must be positive")
    try:
        run_experiment(args.output_dir, args.replications, args.seed)
    except FileExistsError:
        parser.error(f"output directory already exists: {args.output_dir}")


if __name__ == "__main__":
    main()
