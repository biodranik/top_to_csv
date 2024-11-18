#!/usr/bin/env python3

import re
import sys

CSV_DELIMITER: str = ","
ZERO_FILLER: str = "0"

TOP_HEADER_RE = re.compile(r"^\s*PID\s")


def top_to_csv(path_to_top_log: str):
    pid_to_name: dict = {}
    rows: list = []
    with open(path_to_top_log, "r") as file:
        row: dict = {}
        measurement_index: int = -1

        for line in file:
            #     PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
            if TOP_HEADER_RE.search(line):
                measurement_index += 1
                # Drop the first measurement, it is inaccurate as top needs a delay to properly calculate it.
                if measurement_index > 1 and len(row) > 0:
                    rows.append(row)
                row = {}
                continue
            #  188744 www-data  20   0   93180  38908   7168 S   4.0   0.0   6:03.28 nginx: worker process
            if line.startswith(" "):
                values = line.split()
                pid = values[0]
                cpu = str(
                    round(float(values[8]))
                )  # No need in floating point precision
                name = values[11]
                # name = " ".join(values[11:])  # join back the command line arguments

                pid_to_name[pid] = name
                row[pid] = cpu
        # Also process the last element.
        if len(row) > 0:
            rows.append(row)

    # Create CSV
    # CSV header goes first
    csv_content: str = (
        "command"
        + CSV_DELIMITER
        + CSV_DELIMITER.join(str(seconds) for seconds in range(1, len(rows) + 1))
        + "\n"
    )

    for pid, name in pid_to_name.items():
        csv_content += name + CSV_DELIMITER

        csv_content += CSV_DELIMITER.join(
            (row[pid] if pid in row else ZERO_FILLER) for row in rows
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
