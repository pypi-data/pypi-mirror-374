# Picopyn - Picodata python driver

**Picopyn** is a Python package for working with the distributed Picodata database. It's built on top of the [asyncpg](https://github.com/MagicStack/asyncpg) package.

## Features
* Connection pooling with configurable pool size
* Optional automatic node discovery
* Pluggable load-balancing strategies
* Fully asynchronous API

## Navigation
* [Installation](#install-driver)
* [Quickstart](#simple-start)
* [Development](#dev)
* [Benchmark](#bench)

## <a name="install-driver"></a>Install

Install from source:

``` sh
git clone https://git.picodata.io/solution/picopyn.git
cd picopyn
make install
```

## <a name="simple-start"></a>Quickstart

```python
import asyncio
from picopyn import Client

async def main():
    # create and connect client to the picodata cluster
    client = Client(dsn="postgresql://admin:pass@localhost:5432")
    await client.connect()

    # execute DDL operations
    await client.execute('''
        CREATE TABLE "warehouse" (id INTEGER NOT NULL, item TEXT NOT NULL, PRIMARY KEY (id)) USING memtx DISTRIBUTED BY (id) OPTION (TIMEOUT = 3.0);
    ''')

    # execute DML operations
    await client.execute('INSERT INTO \"warehouse\" VALUES ($1::int, $2::varchar)', 1, "test")
    rows = await client.fetch('SELECT * FROM \"warehouse\"')
    print(rows)

    await client.close()

asyncio.run(main())
```

## <a name="dev"></a>Development

Install development dependencies
```bash
pip install -r requirements-dev.txt
```

### Documentation

To update documentation:
```bash
make gen-doc
```

To view documentation:
```bash
make doc
```

### How to write code

We use several tools to ensure code style and type safety.
* ruff — code style, lint checks and automatic lint fixing
* mypy — static type checking
* black — code formatting

To check code style and static types:
```bash
make lint
````

To automatically fix formatting and style issues:

```bash
make fmt
```

### How to test

Run the test suite:

```bash
make test
```

This will:

1. Start required test containers (Picodata cluster and test-runner) using Docker Compose

2. Execute tests using pytest


### How to debug

Do not forget run environment via `make env`

For debugging purposes:

1. Open a bash shell in the test container:

```bash
make shell
```

2. For interactive Python (with asyncio support) run inside of container:

```bash
python -m asyncio
```

3. To connect directly to Picodata:

```bash
picodata admin tmp/picodata-1-1/admin.sock
```
## <a name="bench"></a>Benchmark

Benchmark instructions and usage examples are available [here](benchmark/README.md).