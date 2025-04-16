#!/usr/bin/env python3

import argparse
import os
import re
from io import TextIOWrapper

OUTPUT_CPU = "-cpu"
OUTPUT_MEMORY = "-memory"
DEFAULT_MODE = OUTPUT_CPU

CSV_DELIMITER: str = ","
ZERO_FILLER: str = "0"

TOP_HEADER_RE = re.compile(r"^\s*PID\s")


def prettify_name(command_with_args: list[str]) -> str:
    """Cleans up unimportant command line details"""
    name = (
        os.path.basename(command_with_args[0])
        if command_with_args[0][0] != "["
        else command_with_args[0]
    )
    if name.startswith("python"):
        name += " " + " ".join(command_with_args[1:])
    return name


def sort_by_total_usage(
    pid_to_name: dict[int, str], measurements: list[dict[int, int]]
) -> list[(int, str)]:
    """Sorts pid_to_name by the total usage in measurements and returns it as a list of tuples [(pid, name)]"""
    pid_total_usage: dict[int, int] = {}
    # Sum all values (usage)
    for pid_to_value in measurements:
        for pid, value in pid_to_value.items():
            pid_total_usage[pid] = pid_total_usage.get(pid, 0) + value

    # Sort by total usage
    sorted_pid_total_usage: list[(int, int)] = sorted(
        list(pid_total_usage.items()),
        reverse=True,
        key=lambda pid_total_usage: pid_total_usage[1],
    )

    sorted_pid_to_name: list[(int, str)] = []
    for pid, total_usage in sorted_pid_total_usage:
        sorted_pid_to_name.append((pid, pid_to_name[pid]))

    return sorted_pid_to_name


def top_to_csv(top_log_file: TextIOWrapper, memory_instead_of_cpu: bool, prettify: bool):
    pid_to_name: dict[int, str] = {}
    measurements: list[dict[int, int]] = []

    if memory_instead_of_cpu:
        value_index = 9
    else:
        value_index = 8

    pid_to_value: dict[int, int] = {}
    measurement_index: int = -1

    for line in top_log_file:
        #     PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
        if TOP_HEADER_RE.search(line):
            measurement_index += 1
            # Drop the first measurement as inaccurate, top needs a delay to properly calculate it.
            if measurement_index > 1 and len(pid_to_value) > 0:
                measurements.append(pid_to_value)
            pid_to_value = {}
            continue
        #  188744 www-data  20   0   93180  38908   7168 S   4.0   0.0   6:03.28 nginx: worker process
        if line.startswith(" "):
            values = line.split()
            pid = int(values[0])
            value = round(float(values[value_index]))  # No need in floating point precision
            if prettify:
                name = prettify_name(values[11:])  # Command line args split by space
            else:
                name = ' '.join(values[11:])
            pid_to_name[pid] = name
            pid_to_value[pid] = value
    # Also process the last element.
    if len(pid_to_value) > 0:
        measurements.append(pid_to_value)

    sorted_pid_to_name = sort_by_total_usage(pid_to_name, measurements)

    # Create CSV
    # CSV header goes first
    csv_content: str = (
        "command"
        + CSV_DELIMITER
        + CSV_DELIMITER.join(
            str(seconds) for seconds in range(1, len(measurements) + 1)
        )
        + "\n"
    )

    for pid, name in sorted_pid_to_name:
        csv_content += name + CSV_DELIMITER

        csv_content += CSV_DELIMITER.join(
            str(pid_to_cpu[pid] if pid in pid_to_cpu else ZERO_FILLER)
            for pid_to_cpu in measurements
        )
        csv_content += "\n"

    print(csv_content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog='top_to_csv',
            description='Converts top logs recorded with `top -b -d 1 -w 512 -i -c >> top.log` into csv format', )

    parser.add_argument('file', type=argparse.FileType('r'), nargs='+', help="A list of recorded top output files")
    parser.add_argument('-m', '--memory', action='store_true', help="Output CSV with used RAM instead of CPU usage")
    parser.add_argument('-p', '--prettify', action='store_true', help="Prettify process names")

    args = parser.parse_args()

    for file in args.file:
        top_to_csv(file, args.memory, args.prettify)
