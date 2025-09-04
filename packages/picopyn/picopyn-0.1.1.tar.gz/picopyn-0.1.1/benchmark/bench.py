import argparse
import asyncio
import csv
import time
from datetime import datetime
from uuid import UUID

import matplotlib
import numpy as np

from picopyn import Client

matplotlib.use("Agg")
import os

import matplotlib.pyplot as plt
from colorama import Fore, init

init(autoreset=True)


def parse_args():
    """
    Parse command-line arguments for the benchmark tool.

    Returns:
        argparse.Namespace: Parsed arguments object.
    """
    parser = argparse.ArgumentParser(description="Load data from CSV to Picodata cluster")
    parser.add_argument(
        "--cluster",
        type=str,
        default="postgresql://admin:T0psecret@localhost:55432",
        help="Picodata address and creds",
    )
    parser.add_argument("--input", type=str, default="data.csv", help="Input CSV file name")
    parser.add_argument(
        "--threads", type=int, default=1, help="Amount of threads to use for loading"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Batch size for batched insert. Use 1 if you want single-row inserts",
    )
    parser.add_argument(
        "--overall-output-graph",
        type=str,
        default="graphs/overall_speed_time.png",
        help="Output PNG filename for the overall insertion speed graph",
    )
    parser.add_argument(
        "--threads-output-graph",
        type=str,
        default="graphs/threads_speed_time.png",
        help="Output PNG filename for the per-thread insertion speed graph",
    )
    parser.add_argument(
        "--errors-output-graph",
        type=str,
        default="graphs/errors_cumulative.png",
        help="Output PNG filename for the cumulative errors graph",
    )
    parser.add_argument(
        "--log-insert-errors",
        action="store_true",
        help="If set, log SQL insert errors during the benchmark",
    )
    return parser.parse_args()


def parse_row(row):
    """
    Parse a single CSV row into a list of typed values matching the database schema.

    Args:
        row (list): A list of string values from a CSV row.

    Returns:
        list: Parsed row with appropriate Python types.
    """
    return [
        int(row[0]),
        int(row[1]),
        int(row[2]),
        float(row[3]),
        float(row[4]),
        row[5],
        row[6],
        row[7].lower() == "true",
        datetime.fromisoformat(row[8]),
        UUID(row[9]),
    ]


def read_csv(input_file):
    """
    Read and parse data from CSV file.

    Args:
        input_file (str): Path to the CSV file.

    Returns:
        list: List of parsed rows.
    """
    rows = []
    try:
        print("[INFO] Reading CSV...")
        with open(input_file, newline="") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for idx, row in enumerate(reader):
                if not row or len(row) < 10:
                    print(f"[WARNING] Skipping invalid row {idx}: {row}")
                    continue
                rows.append(parse_row(row))
        print(Fore.GREEN + f"[INFO] Loaded {len(rows)} rows from CSV")
        return rows
    except Exception as e:
        print(Fore.RED + f"[FATAL] Error reading CSV: {e}")
        exit(1)


async def prepare_database(client):
    """
    Prepare the database: drop and recreate the target table.

    Args:
        client (Client): Picodata client connection.
    """
    try:
        await client.connect()
        await client.execute("DROP TABLE IF EXISTS test_all_types;")
        await client.execute(
            """
            CREATE TABLE test_all_types(
                id INTEGER PRIMARY KEY,
                int_field INTEGER,
                unsigned_field UNSIGNED,
                double_field DOUBLE,
                numeric_field DECIMAL,
                text_field TEXT,
                varchar_field VARCHAR(100),
                bool_field BOOLEAN,
                date_field DATETIME,
                uuid_field UUID
            ) USING memtx DISTRIBUTED BY (id) OPTION (TIMEOUT = 3.0);
        """
        )
        print(Fore.GREEN + "[INFO] Database prepared.")
    except Exception as e:
        print(Fore.RED + f"[FATAL] DB preparation error: {e}")
        exit(1)


def build_batch_insert_sql(batch_size: int) -> str:
    """
    Generate parameterized SQL insert statement for batch insert.

    Args:
        batch_size (int): Number of rows in one batch.

    Returns:
        str: SQL INSERT query string.
    """
    value_groups = []
    for i in range(batch_size):
        base = i * 10
        placeholders = [f"${base + j + 1}" for j in range(10)]
        value_groups.append(f"({', '.join(placeholders)})")
    return (
        "INSERT INTO test_all_types ("
        "id, int_field, unsigned_field, double_field, numeric_field, "
        "text_field, varchar_field, bool_field, date_field, uuid_field"
        ") VALUES " + ", ".join(value_groups)
    )


async def worker(thread_id, client, batches, durations, errors, start_time, args):
    """
    Worker coroutine to perform batch inserts for assigned batches.

    Args:
        thread_id (int): Worker ID.
        client (Client): Picodata client connection.
        batches (list): List of batch rows to insert.
        durations (list): List to collect durations per batch.
        errors (list): List to collect timestamps of failed inserts.
        start_time (float): Benchmark start time.
        args (Namespace): Parsed command-line arguments.
    """
    for batch in batches:
        start = time.monotonic()
        try:
            sql = build_batch_insert_sql(len(batch))
            flat_args = [item for row in batch for item in row]
            await client.execute(sql, *flat_args)
        except Exception as e:
            if args.log_insert_errors:
                print(f"[ERROR] Failed batch insert: {e}")
            errors.append((time.monotonic() - start_time, len(batch)))
        end = time.monotonic()
        durations[thread_id].append(end - start)


async def run_benchmark(client, rows, args):
    """
    Run the entire insert benchmark using multiple workers.

    Args:
        client (Client): Picodata client.
        rows (list): Parsed rows to insert.
        args (Namespace): Parsed arguments.

    Returns:
        tuple: (durations, errors)
            durations (list): Per-thread list of durations per batch.
            errors (list): List of error timestamps and batch sizes.
    """
    print("[INFO] Start inserting data...")
    start_time = time.monotonic()

    batches = [rows[i : i + args.batch_size] for i in range(0, len(rows), args.batch_size)]
    batches_per_thread = [[] for _ in range(args.threads)]
    for i, batch in enumerate(batches):
        batches_per_thread[i % args.threads].append(batch)

    durations = [[] for _ in range(args.threads)]
    errors = []

    tasks = [
        worker(i, client, batches_per_thread[i], durations, errors, start_time, args)
        for i in range(args.threads)
    ]
    await asyncio.gather(*tasks)

    total_time = time.monotonic() - start_time
    failed_rows = sum(batch_size for _, batch_size in errors)
    print(
        Fore.GREEN
        + f"[INFO] Successfully loaded {len(rows) - failed_rows} rows in {total_time:.2f}s!"
    )
    return durations, errors


def moving_average(a, window_size):
    """
    Compute moving average for smoothing plots.

    Args:
        a (array-like): Input data.
        window_size (int): Size of the moving window.

    Returns:
        ndarray: Smoothed data.
    """
    return np.convolve(a, np.ones(window_size) / window_size, mode="valid")


def ensure_dir_exists(file_path):
    """
    Ensure that directory for a file path exists.

    Args:
        file_path (str): Target file path.
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def remove_file(file_path):
    """Remove file if exists"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(Fore.RED + f"[WARNING] Failed to delete old file {file_path}: {e}")


def build_overall_graph(durations, rows, args):
    """
    Build and save overall insertion speed graph.

    Args:
        durations (list): Per-thread list of batch durations.
        rows (list): Loaded rows.
        args (Namespace): Parsed arguments.
    """
    print("[INFO] Building overall graph...")
    try:
        all_elapsed, all_speeds = [], []
        for thread in durations:
            if thread:
                elapsed = np.cumsum(thread)
                speeds = np.array([args.batch_size / d for d in thread])
                all_elapsed.extend(elapsed)
                all_speeds.extend(speeds)

        if not all_elapsed or not all_speeds:
            print(Fore.YELLOW + "[WARNING] No data for overall plot.")
            return

        all_data = sorted(zip(all_elapsed, all_speeds, strict=False))
        all_elapsed_sorted, all_speeds_sorted = zip(*all_data, strict=False)
        # In practice, we observe that during the very last moments of insertion (final 1-5% of points),
        # the measured rows-per-second (RPS) may produce significant spikes.
        # This is not due to actual higher throughput, but rather caused by the nature of batch-based insertion timing:
        # - When processing the very last small batch, the time delta for that batch may become very small,
        #   resulting in artificially high instantaneous speed (since RPS = batch_size / duration).
        # - As a result, the end of the graph may show unrealistic spikes (e.g. 10k -> 15k RPS), distorting the plot scale.
        # - These spikes make it harder to visually analyze overall throughput trends.
        #
        # To mitigate this, we simply discard the last 5% of data points when building the graph.
        # This does not affect real throughput calculation but greatly improves graph readability.
        cut_off = int(len(all_speeds_sorted) * 0.95)
        all_speeds_sorted = all_speeds_sorted[:cut_off]
        all_elapsed_sorted = all_elapsed_sorted[:cut_off]

        window_size = max(10, len(all_speeds_sorted) // 20)

        plt.figure(figsize=(12, 7))
        if len(all_speeds_sorted) >= window_size:
            all_speeds_smoothed = np.convolve(
                all_speeds_sorted, np.ones(window_size) / window_size, mode="valid"
            )
            all_elapsed_smoothed = all_elapsed_sorted[window_size - 1 :]
            plt.plot(
                all_elapsed_smoothed,
                all_speeds_smoothed,
                color="black",
                linewidth=2.0,
                label="Average (smoothed)",
            )
        else:
            plt.plot(all_elapsed_sorted, all_speeds_sorted, color="black", label="Raw data")

        plt.xlabel("Elapsed time (s)")
        plt.ylabel("Insert speed (rows/sec)")
        plt.title("Overall insertion speed")
        plt.legend()
        plt.grid(True)
        plt.savefig(args.overall_output_graph)
        print(Fore.GREEN + f"Plot saved to {args.overall_output_graph}")
    except Exception as e:
        print(Fore.RED + f"[ERROR] Overall plot error: {e}")


def build_thread_graph(durations, args):
    """
    Build and save per-thread insertion speed graph.

    Args:
        durations (list): Per-thread list of batch durations.
        args (Namespace): Parsed arguments.
    """
    print("[INFO] Building per-thread graph...")
    try:
        plt.figure(figsize=(12, 7))
        smoothing_window = 20

        for i in range(args.threads):
            elapsed = np.cumsum(durations[i])
            speeds = np.array([args.batch_size / d for d in durations[i]])

            if len(speeds) >= smoothing_window:
                speeds_smooth = moving_average(speeds, smoothing_window)
                elapsed_smooth = elapsed[smoothing_window - 1 :]
            else:
                speeds_smooth = speeds
                elapsed_smooth = elapsed

            # remove last 2% points, see overall graph building
            cut_off = int(len(speeds_smooth) * 0.95)
            speeds_smooth = speeds_smooth[:cut_off]
            elapsed_smooth = elapsed_smooth[:cut_off]

            plt.plot(elapsed_smooth, speeds_smooth, label=f"Thread {i}")

        plt.xlabel("Elapsed time (s)")
        plt.ylabel("Insert speed (rows/sec)")
        plt.title("Insertion speed over time (per thread)")
        plt.legend()
        plt.grid(True)
        plt.savefig(args.threads_output_graph)
        print(Fore.GREEN + f"Plot saved to {args.threads_output_graph}")
    except Exception as e:
        print(Fore.RED + f"[ERROR] Per-thread plot error: {e}")


def build_error_graph(errors, args):
    """
    Build and save cumulative error graph.

    Args:
        errors (list): List of tuples (timestamp, batch_size).
        args (Namespace): Parsed arguments.
    """
    print("[INFO] Building error plot...")
    try:
        if not errors:
            print(Fore.YELLOW + "[INFO] No errors occurred.")
            return

        # Извлекаем только таймстемпы
        error_timestamps = [ts for ts, _ in errors]
        errors_sorted = sorted(error_timestamps)
        cumulative = list(range(1, len(errors_sorted) + 1))

        plt.figure(figsize=(12, 7))
        plt.step(errors_sorted, cumulative, where="post")
        plt.xlabel("Elapsed time (s)")
        plt.ylabel("Cumulative errors")
        plt.title("Cumulative error count over time")
        plt.grid(True)
        plt.savefig(args.errors_output_graph)
        print(Fore.GREEN + f"Error plot saved to {args.errors_output_graph}")
    except Exception as e:
        print(Fore.RED + f"[ERROR] Error plot error: {e}")


def compute_average_speed(durations, rows, args):
    """
    Compute and print average insert speed.

    Args:
        durations (list): Per-thread list of batch durations.
        rows (list): Loaded rows.
        args (Namespace): Parsed arguments.
    """
    try:
        print("[INFO] Computing avg speed (per-thread)...")

        thread_speeds = []
        total_inserted_rows = 0

        for thread_durations in durations:
            batch_count = len(thread_durations)
            total_rows_in_thread = batch_count * args.batch_size
            total_inserted_rows += total_rows_in_thread

            total_duration_in_thread = sum(thread_durations)
            if total_duration_in_thread > 0:
                thread_speed = total_rows_in_thread / total_duration_in_thread
                thread_speeds.append(thread_speed)

        if thread_speeds:
            avg_speed = sum(thread_speeds) / len(thread_speeds)
            print(
                Fore.GREEN
                + f"Average insert speed (per-thread avg): {avg_speed:.2f} rows/sec with batch size {args.batch_size} and {args.threads} threads"
            )
        else:
            print(Fore.YELLOW + "No valid thread durations to compute average speed.")
    except Exception as e:
        print(Fore.RED + f"[ERROR] Avg speed calc error: {e}")


async def main():
    args = parse_args()

    if args.threads < 1 or args.batch_size < 1:
        print(Fore.RED + "[FATAL] Invalid threads or batch size")
        exit(1)

    ensure_dir_exists(args.overall_output_graph)
    ensure_dir_exists(args.threads_output_graph)
    ensure_dir_exists(args.errors_output_graph)

    remove_file(args.overall_output_graph)
    remove_file(args.threads_output_graph)
    remove_file(args.errors_output_graph)

    rows = read_csv(args.input)

    client = Client(dsn=args.cluster, pool_size=args.threads)
    await prepare_database(client)

    durations, errors = await run_benchmark(client, rows, args)

    build_thread_graph(durations, args)
    build_overall_graph(durations, rows, args)
    build_error_graph(errors, args)
    compute_average_speed(durations, rows, args)


if __name__ == "__main__":
    asyncio.run(main())
