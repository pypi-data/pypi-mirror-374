# Picopyn Benchmark Tool

This directory contains a benchmark tool for measuring Picopyn insert performance into a Picodata cluster.

## Features

- Parallel data loading with configurable number of threads
- Support for batch inserts with custom batch size
- Detailed CSV parsing (including UUIDs, booleans, decimals, datetime, etc.)
- Measurement of insert speed and error rate
- Automatic generation of performance graphs:
  - Overall insert speed over time
  - Per-thread insert speed over time
  - Cumulative error count
- Colored console output (via `colorama`)
- Optional logging of failed insert queries

---

## Navigation
* [Prerequisites](#prerequisites)
* [Running benchmark](#run-bench)
* [Analyze the results](#results)
* [Notes](#notes)

## <a name="prerequisites"></a>Prerequisites

- Python 3.10+
- Install project dependencies (including `picopyn` and deps from `./requirements.txt`):

Attention! It's recommended to use out test-runner container. All commands below are for the docker container! To enter to container execute in console:

```bash
# root dir
make shell
```

To install deps:
```bash
make install
cd benchmark
# not necessary for docker container
pip install -r requirements.txt
```

## <a name="csv"></a>CSV Input Format

The input CSV file should contain 10 columns:

| Column Name   | Type     |
| -------------- | -------- |
| id             | INTEGER  |
| int_field      | INTEGER  |
| unsigned_field | UNSIGNED |
| double_field   | DOUBLE   |
| numeric_field  | DECIMAL  |
| text_field     | TEXT     |
| varchar_field  | VARCHAR  |
| bool_field     | BOOLEAN (true/false) |
| date_field     | DATETIME (ISO8601 format) |
| uuid_field     | UUID     |

Example row:

```csv
1,-687,1055,109.005522,1946.31,mbmfwobdohxfybflqoen,qcyhiwobr,False,2022-04-11T00:00:00,3e96136e-551c-4deb-9469-7efa63176b57
```

To generate data file use:

```bash
#/app/benchmark dir
python generate_data_to_csv.py --rows 100000 --output data.csv
```

To see the current script arguments, run the command
```bash
python generate_data_to_csv.py -h
# command output
usage: generate_data_to_csv.py [-h] [--rows ROWS] [--output OUTPUT]

Generate data file in CSV format

options:
    -h, --help       show this help message and exit
    --rows ROWS      Number of rows to generate
    --output OUTPUT  Output CSV file name
```

## <a name="run-bench"></a>Running benchmark

You can run the benchmark script via:

```bash
python bench.py \
  --cluster postgresql://admin:T0psecret@picodata-1-1:5432 \
  --input data.csv \
  --threads 4 \
  --batch-size 100 \
  --log-insert-errors
```

This command will load `data.csv` using 4 parallel threads, with batch inserts of 100 rows each, and log failed inserts if any.

After execution, you will get 3 PNG graphs visualizing performance.

To see the current script arguments, run the command
```bash
python3
bench.py -h
# command output
usage: bench.py [-h] [--cluster CLUSTER] [--input INPUT] [--threads THREADS] [--batch-size BATCH_SIZE] [--overall-output-graph OVERALL_OUTPUT_GRAPH]
                 [--threads-output-graph THREADS_OUTPUT_GRAPH] [--errors-output-graph ERRORS_OUTPUT_GRAPH] [--log-insert-errors]

Load data from CSV to Picodata cluster

options:
    -h, --help            show this help message and exit
    --cluster CLUSTER     Picodata address and creds
    --input INPUT         Input CSV file name
    --threads THREADS     Amount of threads to use for loading
    --batch-size BATCH_SIZE
                            Batch size for batched insert. Use 1 if you want single-row inserts
    --overall-output-graph OVERALL_OUTPUT_GRAPH
                            Output PNG filename for the overall insertion speed graph
    --threads-output-graph THREADS_OUTPUT_GRAPH
                            Output PNG filename for the per-thread insertion speed graph
    --errors-output-graph ERRORS_OUTPUT_GRAPH
                            Output PNG filename for the cumulative errors graph
    --log-insert-errors   If set, log SQL insert errors during the benchmark
```

## <a name="results"></a>Analyze the results

As the script runs, you will see log information for each step, for example:
```bash
python bench.py --cluster "postgresql://admin:T0psecret@picodata-1-1:5432" --threads 10 --batch-size 100
[INFO] Reading CSV...
[INFO] Loaded 5000000 rows from CSV
[INFO] Database prepared.
[INFO] Start inserting data...
[INFO] Loaded 5000000 rows in 66.54s! Batch size 100, threads 10
[INFO] Building per-thread graph...
Plot saved to graphs/threads_speed_time.png
[INFO] Building overall graph...
Plot saved to graphs/overall_speed_time.png
[INFO] Building error plot...
Error plot saved to graphs/errors_cumulative.png
[INFO] Computing avg speed...
Average insert speed: 7623.58 rows/sec with batch size 100 and 10 threads
```

Also you will get 3 output graphs
- _Overall insertion speed_ — average insert rate across all threads over time (default name is `graphs/overall_speed_time.png`)
- _Per-thread speed_ — individual insert speed for each thread (default name is `graphs/threads_speed_time.png`)
- _Cumulative errors_ — total count of failed inserts over time **if errors occured** (default name is `graphs/errors_cumulative.png`)

Let's see graph samples for 1M rows (a few rows were invalid to simulate errors) and its output:
```bash
python bench.py --cluster "postgresql://admin:T0psecret@picodata-1-1:5432" --threads 10 --batch-size 100
[INFO] Reading CSV...
[INFO] Loaded 1000000 rows from CSV
[INFO] Database prepared.
[INFO] Start inserting data...
[INFO] Successfully loaded 999300 rows in 13.81s!
[INFO] Building per-thread graph...
Plot saved to graphs/threads_speed_time.png
[INFO] Building overall graph...
Plot saved to graphs/overall_speed_time.png
[INFO] Building error plot...
Error plot saved to graphs/errors_cumulative.png
[INFO] Computing avg speed (per-thread)...
Average insert speed (per-thread avg): 7434.73 rows/sec with batch size 100 and 10 threads
```

![Overall sample](./examples/1m_rows_10_threads_100_batch/overall_speed_time.png)
![Thread sample](./examples/1m_rows_10_threads_100_batch/threads_speed_time.png)
![Error graph sample](./examples/1m_rows_10_threads_100_batch/errors_cumulative.png)

In practice, we observe that during the final stages of insertion (the last 1-5% of data points), the measured rows-per-second (RPS) may exhibit significant spikes.

Why this happens:
1. Short final batch duration

* When processing the last remaining (small) batch, the time delta for that batch can become extremely small.
* Since RPS = batch_size / duration, this leads to an artificially inflated instantaneous speed.
* As a result, the graph may show unrealistic spikes (e.g., jumping from 10K to 15K RPS), distorting the scale.

2. Threads finishing at different times (tails effect)

* In multi-threaded inserts, some threads may complete earlier than others.
* This creates gradual "tails" in the RPS graph—where throughput slowly declines instead of sharply dropping to zero.
* These tails can obscure real performance trends.

To mitigate these distortions, we simply discard the last 5% of measurements when generating the graph. This does not affect the actual throughput calculation. It significantly improves graph readability by removing misleading spikes and tails.

## <a name="notes"></a>Notes

- Before each run, the benchmark recreates the target table (`test_all_types`).
- The target table is created in `memtx` engine for maximum insert performance.
- The bench use only `INSERT` SQL operation

This benchmark is designed for internal development and diagnostic purposes.
For production-level benchmarks consider more complex scenarios including:

- Reads, updates, deletes
- Larger datasets
- System monitoring and resource utilization analysis

For a big dataset you may need to inscrease Picodata memory. Use:

```bash
# connect to picodata instance
picodata admin tmp/data/picodata-1-1/admin.sock
# inside picodata console switch to LUA
(admin) sql> \lua
Language switched to lua
# see current value if you need
(admin) lua> box.cfg.memtx_memory;
---
- 67108864
...
# set memtx_memory to value that you need
(admin) lua> box.cfg{memtx_memory = 134217728};
```