import argparse
import asyncio
import itertools
import json
import logging
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from multiprocessing import cpu_count
from typing import TYPE_CHECKING, List, Literal, Optional

import matplotlib.pyplot as plt
import numpy as np
from pydantic import BaseModel, Field, confloat, conint

# Ensure the source code is in the path for imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from wombat.multiprocessing import requires_props, task
from wombat.multiprocessing.models import Prop
from wombat.multiprocessing.orchestrator import Orchestrator

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from wombat.multiprocessing.worker import Worker


class ExpensiveClient:
    """A client that simulates an expensive, one-time setup cost."""

    def __init__(self, startup_time: float = 0.5):
        # Simulate a high-cost operation like loading a large model from disk.
        time.sleep(startup_time)
        self.data = "some_large_resource" * 100

    def do_work(self, task_time: float = 0.0) -> int:
        # Simulate a cheap, repeatable operation on the loaded resource.
        time.sleep(task_time)
        return len(self.data)


# --- Task Definitions ---


@task()
def cpu_bound_action(_worker: "Worker", n: int) -> bool:
    """A simple CPU-bound task for benchmarking with Wombat."""
    sum(i * i for i in range(n))
    return True


def cpu_bound_task_cf(n: int) -> bool:
    """A simple CPU-bound task for benchmarking with concurrent.futures."""
    sum(i * i for i in range(n))
    return True


# --- Prop-based Task Definitions ---


@task()
@requires_props(requires_props=["expensive_client"])
def use_persistent_client_action(
    worker: "Worker", task_time: float, props: dict[str, Prop]
) -> int:
    """Action that uses a persistent client from props."""
    client: ExpensiveClient = props["expensive_client"].instance
    return client.do_work(task_time)


# --- Wombat (QPool) Benchmark ---


async def run_wombat_benchmark(
    num_tasks: int, num_workers: int, task_complexity: int
) -> float:
    """Runs the benchmark using Wombat Orchestrator."""
    tasks = [cpu_bound_action(task_complexity) for _ in range(num_tasks)]
    config = {
        "actions": {cpu_bound_action.action_name: cpu_bound_action},
        "props": {},
    }

    logger.info("--- Running Wombat Benchmark ---")
    logger.info(
        f"Tasks: {num_tasks}, Workers: {num_workers}, Complexity: {task_complexity}"
    )

    start_time = time.monotonic()
    async with Orchestrator(
        num_workers=num_workers,
        show_progress=False,
        **config,
    ) as orchestrator:
        await orchestrator.add_tasks(tasks)
        results = await orchestrator.stop_workers()
    end_time = time.monotonic()

    return _report_benchmark_results("Wombat", start_time, end_time, num_tasks, results)


async def run_wombat_prop_benchmark(
    num_tasks: int, num_workers: int, startup_time: float, task_time: float
) -> float:
    """Runs the benchmark using Wombat Orchestrator with a persistent client."""
    tasks = [use_persistent_client_action(task_time) for _ in range(num_tasks)]

    config = {
        "actions": {
            use_persistent_client_action.action_name: use_persistent_client_action
        },
        "props": {
            "expensive_client": Prop(
                initializer=partial(ExpensiveClient, startup_time=startup_time),
                use_context_manager=False,
            )
        },
    }

    logger.info("--- Running Wombat Benchmark with Persistent Client ---")
    logger.info(
        f"Tasks: {num_tasks}, Workers: {num_workers}, Startup Time: {startup_time:.3f}s, Task Time: {task_time:.3f}s"
    )

    start_time = time.monotonic()
    async with Orchestrator(
        num_workers=num_workers,
        show_progress=False,
        **config,
    ) as orchestrator:
        await orchestrator.add_tasks(tasks)
        results = await orchestrator.stop_workers()
    end_time = time.monotonic()

    return _report_benchmark_results(
        "Wombat (Props)", start_time, end_time, num_tasks, results
    )


# --- Concurrent.futures Benchmark ---


def _report_benchmark_results(
    name: str, start_time: float, end_time: float, num_tasks: int, results: list
) -> float:
    """Calculates and prints benchmark results, then returns throughput."""
    duration = end_time - start_time
    tasks_per_second = num_tasks / duration if duration > 0 else float("inf")

    logger.info(f"[{name}] Total time: {duration:.2f} seconds")
    logger.info(f"[{name}] Throughput: {tasks_per_second:.2f} tasks/sec")
    assert len(results) == num_tasks, f"{name} did not return all results"

    return tasks_per_second


# --- Globals and Initializer for concurrent.futures ---

_global_client: Optional[ExpensiveClient] = None


def init_expensive_client(startup_time: float):
    """Initializer for ProcessPoolExecutor workers to set up a global client."""
    global _global_client
    if _global_client is None:
        _global_client = ExpensiveClient(startup_time=startup_time)


def use_global_client_task_cf(task_time: float) -> int:
    """A task for concurrent.futures that uses a pre-initialized global client."""
    if _global_client is None:
        # This should not happen if the initializer is used correctly.
        raise RuntimeError("Global client not initialized in worker.")
    return _global_client.do_work(task_time=task_time)


def run_concurrent_futures_benchmark(
    num_tasks: int, num_workers: int, task_complexity: int
) -> float:
    """Runs the benchmark using concurrent.futures.ProcessPoolExecutor."""
    logger.info("--- Running concurrent.futures Benchmark ---")
    logger.info(
        f"Tasks: {num_tasks}, Workers: {num_workers}, Complexity: {task_complexity}"
    )

    start_time = time.monotonic()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(cpu_bound_task_cf, task_complexity)
            for _ in range(num_tasks)
        ]
        results = [f.result() for f in futures]
    end_time = time.monotonic()

    return _report_benchmark_results(
        "concurrent.futures", start_time, end_time, num_tasks, results
    )


def run_concurrent_futures_prop_benchmark(
    num_tasks: int, num_workers: int, startup_time: float, task_time: float
) -> float:
    """
    Runs the benchmark using concurrent.futures.ProcessPoolExecutor
    with an efficient, per-worker client initializer.
    """
    logger.info("--- Running concurrent.futures Benchmark with Initializer ---")
    logger.info(
        f"Tasks: {num_tasks}, Workers: {num_workers}, Startup Time: {startup_time:.3f}s, Task Time: {task_time:.3f}s"
    )

    start_time = time.monotonic()
    with ProcessPoolExecutor(
        max_workers=num_workers,
        initializer=init_expensive_client,
        initargs=(startup_time,),
    ) as executor:
        futures = [
            executor.submit(use_global_client_task_cf, task_time)
            for _ in range(num_tasks)
        ]
        results = [f.result() for f in futures]
    end_time = time.monotonic()

    return _report_benchmark_results(
        "concurrent.futures (Initializer)", start_time, end_time, num_tasks, results
    )


def plot_permutation_grid(all_results, task_counts, startup_times, worker_counts):
    """Generates and saves a grid of plots for all permutations."""
    num_rows = len(task_counts) * len(startup_times)
    num_cols = len(worker_counts)

    if num_rows == 0 or num_cols == 0:
        logger.warning("No data to plot for permutations.")
        return

    fig, axes = plt.subplots(
        num_rows,
        num_cols,
        figsize=(7 * num_cols, 6 * num_rows),
        squeeze=False,
        sharex=True,
        sharey=True,
    )

    param_combinations = list(itertools.product(task_counts, startup_times))

    for row_idx, (tasks, startup_time) in enumerate(param_combinations):
        for col_idx, workers in enumerate(worker_counts):
            ax = axes[row_idx, col_idx]
            key = (tasks, startup_time, workers)
            if key not in all_results:
                ax.text(0.5, 0.5, "No data", ha="center", va="center")
                continue

            data = all_results[key]
            task_times = data["task_times"]
            wombat_tps_list = data["wombat"]
            cf_tps_list = data["cf"]

            ax.plot(
                task_times,
                wombat_tps_list,
                "o-",
                label="Wombat with Persistent Client",
            )
            ax.plot(
                task_times,
                cf_tps_list,
                "s--",
                label="concurrent.futures with Initializer",
            )

            diff = np.array(wombat_tps_list) - np.array(cf_tps_list)
            sign_change_indices = np.where(np.diff(np.sign(diff)))[0]

            if len(sign_change_indices) > 0:
                idx = sign_change_indices[0]
                ax.plot(
                    task_times[idx],
                    wombat_tps_list[idx],
                    "rx",
                    markersize=10,
                    markeredgewidth=2,
                )

            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.grid(True, which="both", linestyle="--", linewidth=0.5)
            ax.set_title(
                f"Tasks: {tasks}, Startup: {startup_time:.2f}s, Workers: {workers}",
                fontsize=10,
            )

    fig.supxlabel("Task Execution Time (seconds) - log scale", fontsize=14)
    fig.supylabel("Throughput (tasks/sec) - log scale", fontsize=14)
    fig.suptitle(
        "Wombat vs. concurrent.futures Throughput Benchmark", fontsize=18, y=0.99
    )

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    filename = "benchmark_permutations.png"
    plt.savefig(filename)
    logger.info(f"Graph saved to {filename}")


# --- Pydantic Configuration Models ---


class ScenarioPermutations(BaseModel):
    """Defines parameter lists to generate scenario permutations for graphing."""

    tasks: List[conint(ge=1)]
    startup_time: List[confloat(ge=0)]
    workers: List[conint(ge=1)]


class BenchmarkConfig(BaseModel):
    """Configuration for the benchmark script, loaded from a JSON file."""

    name: Optional[str] = None
    tasks: conint(ge=1) = 1000
    workers: Optional[conint(ge=1)] = Field(default_factory=cpu_count)
    complexity: conint(ge=1) = 10000
    benchmark: Literal["baseline-throughput", "prop-throughput"] = "baseline-throughput"
    startup_time: confloat(ge=0) = 0.5
    task_time: confloat(ge=0) = 0.01
    graph: bool = False
    scenarios: Optional[ScenarioPermutations] = None
    task_times: Optional[List[float]] = None


# --- Main Execution ---


def main():
    """Parses a config file and runs the benchmarks."""
    parser = argparse.ArgumentParser(
        description="Throughput benchmark for Wombat vs. concurrent.futures."
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the JSON configuration file for the benchmark.",
    )
    args = parser.parse_args()

    try:
        with open(args.config, "r") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Error: Configuration file not found at '{args.config}'")
        sys.exit(1)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Error parsing configuration file: {e}")
        sys.exit(1)

    if not isinstance(config_data, list):
        config_data = [config_data]

    for i, scenario_data in enumerate(config_data):
        try:
            config = BenchmarkConfig(**scenario_data)
        except Exception as e:
            logger.error(f"Error parsing configuration for scenario {i + 1}: {e}")
            continue

        if config.name:
            logger.info(f"\n{'=' * 20} Running Benchmark: {config.name} {'=' * 20}")

        if config.graph:
            if config.benchmark != "prop-throughput":
                logger.error(
                    "Graphing is only supported for the 'prop-throughput' benchmark."
                )
                sys.exit(1)

            # Use task times from config or a default logspace for the x-axis
            task_times = config.task_times or np.logspace(-3, 0, 20)

            if config.scenarios:
                p = config.scenarios
                param_grid = list(
                    itertools.product(p.tasks, p.startup_time, p.workers)
                )
            else:
                # Default to a single plot using the main config parameters
                param_grid = [(config.tasks, config.startup_time, config.workers)]

            # The plotting function needs separate lists of unique parameter values
            # to construct the grid axes correctly.
            task_counts = sorted(list(set(item[0] for item in param_grid)))
            startup_times = sorted(list(set(item[1] for item in param_grid)))
            worker_counts = sorted(list(set(item[2] for item in param_grid)))

            all_results = {}

            for tasks, startup_time, workers in param_grid:
                wombat_results = []
                cf_results = []

                logger.info(
                    f"--- Running Permutation: Tasks={tasks}, Startup={startup_time:.3f}s, Workers={workers} ---"
                )
                for task_time in task_times:
                    wombat_tps = asyncio.run(
                        run_wombat_prop_benchmark(
                            tasks, workers, startup_time, task_time
                        )
                    )
                    cf_tps = run_concurrent_futures_prop_benchmark(
                        tasks, workers, startup_time, task_time
                    )
                    wombat_results.append(wombat_tps)
                    cf_results.append(cf_tps)

                key = (tasks, startup_time, workers)
                all_results[key] = {
                    "task_times": task_times,
                    "wombat": wombat_results,
                    "cf": cf_results,
                }

            plot_permutation_grid(
                all_results, task_counts, startup_times, worker_counts
            )
            return

        if config.benchmark == "baseline-throughput":
            wombat_tps = asyncio.run(
                run_wombat_benchmark(config.tasks, config.workers, config.complexity)
            )
            cf_tps = run_concurrent_futures_benchmark(
                config.tasks, config.workers, config.complexity
            )
        elif config.benchmark == "prop-throughput":
            wombat_tps = asyncio.run(
                run_wombat_prop_benchmark(
                    config.tasks, config.workers, config.startup_time, config.task_time
                )
            )
            cf_tps = run_concurrent_futures_prop_benchmark(
                config.tasks, config.workers, config.startup_time, config.task_time
            )
        else:
            logger.error(f"Unknown benchmark type: {config.benchmark}")
            continue

        logger.info("--- Summary ---")
        logger.info(f"Wombat Throughput:            {wombat_tps:.2f} tasks/sec")
        logger.info(f"concurrent.futures Throughput: {cf_tps:.2f} tasks/sec")

        if wombat_tps > cf_tps:
            ratio = wombat_tps / cf_tps if cf_tps > 0 else float("inf")
            logger.info(f"Wombat is {ratio:.2f}x faster.")
        else:
            ratio = cf_tps / wombat_tps if wombat_tps > 0 else float("inf")
            logger.info(f"concurrent.futures is {ratio:.2f}x faster.")


if __name__ == "__main__":
    main()
