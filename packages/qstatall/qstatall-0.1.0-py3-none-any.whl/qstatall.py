#!/usr/bin/env python
"""
A Python tool to query and display all SGE job information in a formatted table.

Usage:
    qstatall [-u user]
Options:
    -u, --user    user name, if not provided, use current user
Example:
    qstatall -u user1 -p plain
Output:
    job_id  job_name    job_user    job_state   job_queue   job_submit_time       cpu        vmem     script_file   sge_o_workdir
    12345   job1        user1       r           queue1      09/04/2025-09:31:27   00:00:00   3.820M   job1.sh       /data/user1/12345
    12346   job2        user1       r           queue2      09/04/2025-09:31:27   00:00:00   3.789M   job2.sh       /data/user1/12346
    12347   job3        user1       r           queue3      09/04/2025-09:31:27   00:00:00   3.789M   job3.sh       /data/user1/12347
"""

from typing import Dict, List, Any
import os
import sys
import subprocess
import argparse
from tabulate import tabulate

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='qstatall')
    parser.add_argument('-u', '--user', help='user name, if not provided, use current user', 
                      required=False, default=os.getenv('USER'), type=str)
    parser.add_argument('-t','--tablefmt', help='table format', required=False, default='plain', type=str)
    args = parser.parse_args()
    return args

def get_job_infos(user: str) -> Dict[str, Dict[str, Any]]:
    cmd = 'qstat -u {}'.format(user)
    try:
        output = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print('Error: {}'.format(e))
        sys.exit(1)
    job_lines = output.decode().splitlines()[2:]
    # job-ID  prior   name       user         state submit/start at     queue
    job_infos: Dict[str, Dict[str, Any]] = {}
    for job_line in job_lines:
        tmp = job_line.split()
        job_id = tmp[0]
        job_user = tmp[3]
        job_state = tmp[4]
        job_submit_time = tmp[5] + '-' + tmp[6]
        job_queue = tmp[7]
        job_infos[job_id] = {'job_id': job_id, 'job_user': job_user, 
                            'job_state': job_state, 'job_submit_time': job_submit_time, 
                            'job_queue': job_queue}
    get_job_detail_info(job_infos)
    return job_infos

def get_job_detail_info(job_infos: Dict[str, Dict[str, Any]]) -> None:
    job_ids = list(job_infos.keys())
    job_id = ','.join(job_ids)
    cmd = 'qstat -j {}'.format(job_id)
    try:
        output = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print('Error: {}'.format(e))
        sys.exit(1)
    job_info_lines = output.decode().splitlines()
    parse_job_detail_info_from_lines(job_info_lines, job_infos)

def parse_job_detail_info_from_lines(job_info_lines: List[str], 
                                   job_infos: Dict[str, Dict[str, Any]]) -> None:
    # set default value
    usage = 'NA'
    sge_o_workdir = 'NA'
    cpu = '00:00:00'
    vmem = 'N/A'
    script_file = 'NA'
    job_name = 'NA'
    job_number = 'NA'
    # set default value for all job, to avoid missing job info while job is pending
    for job_id in job_infos:
        job_infos[job_id]['job_name'] = job_name
        job_infos[job_id]['sge_o_workdir'] = sge_o_workdir
        job_infos[job_id]['cpu'] = cpu
        job_infos[job_id]['vmem'] = vmem
        job_infos[job_id]['script_file'] = script_file
        job_infos[job_id]['job_number'] = job_number
    
    # update job info
    for line in job_info_lines:
        if line.startswith('job_number'):
            job_number = line.split(':')[1].strip()
        if line.startswith('sge_o_workdir'):
            sge_o_workdir = line.split(':')[1].strip()
        if line.startswith('script_file'):
            script_file = line.split(':')[1].strip()
        if line.startswith('job_name'):
            job_name = line.split(':')[1].strip()
        if line.startswith('usage'):
            usage = line.split(':',1)[1].strip()
            # extrat cpu, vmem infos
            cpu = usage.split(',')[0].split('=')[1]
            vmem = usage.split(',')[3].split('=')[1]
            if job_number in job_infos:
                # store job infos to current job_number
                job_infos[job_number]['job_name'] = job_name
                job_infos[job_number]['sge_o_workdir'] = sge_o_workdir
                job_infos[job_number]['cpu'] = cpu
                job_infos[job_number]['vmem'] = vmem
                job_infos[job_number]['script_file'] = script_file
            # reset default value
            usage = 'NA'
            sge_o_workdir = 'NA'
            cpu = '00:00:00'
            vmem = 'N/A'
            script_file = 'NA'
            job_name = 'NA'
            job_number = 'NA'

def main() -> None:
    args = parse_args()
    job_infos = get_job_infos(args.user)
    headers = ['job_id', 'job_name', 'job_user', 'job_state', 'job_queue', 
              'job_submit_time', 'cpu', 'vmem', 'script_file', 'sge_o_workdir']
    tables = []
    for job_id in job_infos:
        tables.append([job_infos[job_id][col] for col in headers])
    print(tabulate(tables, headers=headers, tablefmt=args.tablefmt))

if __name__ == '__main__':
    main()
