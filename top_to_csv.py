#!/usr/bin/env python3

import os
import re
import sys

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
    #    if name.startswith("python"):
    name += " " + " ".join(command_with_args[1:])
    return name


def sort_by_total_cpu_usage(
    pid_to_name: dict[int, str], measurements: list[dict[int, int]]
) -> list[(int, str)]:
    """Sorts pid_to_name by the total CPU usage in measurements and returns it as a list of tuples [(pid, name)]"""
    pid_total_cpu: dict[int, int] = {}
    # Sum all CPU usage
    for pid_to_cpu in measurements:
        for pid, cpu in pid_to_cpu.items():
            pid_total_cpu[pid] = pid_total_cpu.get(pid, 0) + cpu

    # Sort by total CPU usage
    sorted_pid_total_cpu: list[(int, int)] = sorted(
        list(pid_total_cpu.items()),
        reverse=True,
        key=lambda pid_total_cpu: pid_total_cpu[1],
    )

    sorted_pid_to_name: list[(int, str)] = []
    for pid, total_cpu in sorted_pid_total_cpu:
        sorted_pid_to_name.append((pid, pid_to_name[pid]))

    return sorted_pid_to_name


def top_to_csv(path_to_top_log: str):
    pid_to_name: dict[int, str] = {}
    measurements: list[dict[int, int]] = []

    with open(path_to_top_log, "r") as file:
        pid_to_cpu: dict[int, int] = {}
        measurement_index: int = -1

        for line in file:
            #     PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
            if TOP_HEADER_RE.search(line):
                measurement_index += 1
                # Drop the first measurement, it is inaccurate as top needs a delay to properly calculate it.
                if measurement_index > 1 and len(pid_to_cpu) > 0:
                    measurements.append(pid_to_cpu)
                pid_to_cpu = {}
                continue
            #  188744 www-data  20   0   93180  38908   7168 S   4.0   0.0   6:03.28 nginx: worker process
            if line.startswith(" "):
                values = line.split()
                pid = int(values[0])
                cpu = round(float(values[8]))  # No need in floating point precision
                name = prettify_name(values[11:])  # Command line args split by space
                pid_to_name[pid] = name
                pid_to_cpu[pid] = cpu
        # Also process the last element.
        if len(pid_to_cpu) > 0:
            measurements.append(pid_to_cpu)

    sorted_pid_to_name = sort_by_total_cpu_usage(pid_to_name, measurements)

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

    csv_file: str = path_to_top_log + ".csv"
    with open(csv_file, "w") as csv:
        csv.write(csv_content)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(
            "Converts top logs recorded with `top -b -d 1 -w 512 -i -c >> top.log` into csv format"
        )
        print(
            f"Usage: {sys.argv[0]} <top output file> [<top output file> ...]",
        )
        exit(1)

    for file in sys.argv[1::]:
        top_to_csv(file)
