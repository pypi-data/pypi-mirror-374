# qstatall

A Python tool to query and display all SGE job information in a formatted table.

## Features
- Query all jobs for a specific user
- Display job information in a well-formatted table
- Show detailed job information including CPU and memory usage

## Installation

### From PyPI (Recommended)
```bash
pip install qstatall
```

### From Source
```bash
git clone https://github.com/liuyanbioinfo/qstatall.git
cd qstatall
pip install .
```

## Usage
```bash
# Basic usage (shows current user's jobs)
qstatall

# Show jobs for specific user
qstatall -u user1 -t plain

# Change table format
qstatall -t grid
```
## Output Example
```
job_id  job_name    job_user    job_state   job_queue   job_submit_time       cpu        vmem     script_file   sge_o_workdir
12345   job1        user1       r           queue1      09/04/2025-09:31:27   00:00:00   3.820M   job1.sh       /data/user1/12345
12346   job2        user1       r           queue2      09/04/2025-09:31:27   00:00:00   3.789M   job2.sh       /data/user1/12346
12347   job3        user1       r           queue3      09/04/2025-09:31:27   00:00:00   3.789M   job3.sh       /data/user1/12347
```

## Requirements
- Python 3.7+
- SGE (Sun Grid Engine) system
- tabulate package (will be installed automatically)

## Table Format Options
This tool uses the `tabulate` package for formatting. Available formats include:
- plain
- simple
- grid
- pipe
- html
- latex
- ... (any format supported by tabulate package)

## Development
Install development dependencies:
```bash
pip install -e .
```

Run type checking:
```bash
mypy qstatall.py
```

## Key Fields

- **job_id**: Job ID
- **job_name**: Job Name
- **job_user**: Job Owner
- **job_state**: Job State
- **job_queue**: Queue Name
- **job_submit_time**: Submit Time
- **cpu**: CPU Usage
- **vmem**: Virtual Memory Usage
- **script_file**: Script File
- **sge_o_workdir**: Working Directory

## License
MIT License

## Author
Liu Yan (liuyanhzau@163.com)
