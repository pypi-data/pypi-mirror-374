# shardate

A lightweight Python library for efficiently reading year-month-day partitioned Parquet datasets with PySpark.

## Installation

```bash
pip install shardate
```

## Features

- Read Parquet data partitioned by year/month/day structure
- Efficient date-based filtering
- Built on PySpark for scalable data processing
- Simple and intuitive API

## Quick Start

```python
from datetime import date
from shardate import read_by_date, read_between, read_by_dates

# Read data for a specific date
df = read_by_date("/path/to/data", date(2025, 1, 15))

# Read data between two dates
df = read_between("/path/to/data", date(2025, 1, 1), date(2025, 1, 31))

# Read data for specific dates
dates = [date(2025, 1, 1), date(2025, 1, 15), date(2025, 1, 31)]
df = read_by_dates("/path/to/data", dates)
```

## Requirements

- Python 3.12+
- PySpark 4.0+

## License

MIT