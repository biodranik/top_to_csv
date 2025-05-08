# Convert top batch mode logs into csv files to analyze the CPU usage

## Requirements

Now the script supports Linux, was tested on Ubuntu 22+.

## How to use

1. Record `top` output using the command (stop recording at any time using ctrl+C):
```bash
top -b -d 1 -c -i -w 512 > $(date +%y%m%d-%H%M%S).top.log
```
Where:
- `-b`: batch mode useful for machine parsing
- `-d 1`: update results every second
- `-c`: show full command line instead of a binary name
- `-i`: hide processes that do not use CPU
- `-w 512`: use max possible 512 characters to store the command line

Optional switches:
- `-n SECONDS`: record only SECONDS interval and stop after that
- `-H`: record threads in addition to processes

2. Convert recorded output using the command below into a CSV file with each process CPU load in a column at given seconds interval from the start:

```bash
python3 top_to_csv.py top.log [2nd.top.log ...]
```

Possible CSV output:

```csv
command,1,2,3,4,5
nginx,3,6,0,4,10
python -m controller,54,10,10,33,20
```
