# Convert top batch mode logs into csv files to analyze the CPU usage

## Requirements

Now the script supports Linux, was tested on Ubuntu 22+.

## How to use

1. Record `top` output using the command:
```bash
top --batch --delay 1 --cmdline-toggle --idle-toggle --width 512 > $(date +%y%m%d-%H%M%S).top.log
```

Optionally, add `-nSECONDS` switch if only a specific time interval in seconds should be recorded.

2. Convert recorded output using the command below into a CSV file with each process CPU load in a column at given seconds interval from the start:
```csv
command,1,2,3,4,5
nginx,3,6,0,4,10
python -m controller,54,10,10,33,20
```

```bash
python3 top_to_csv.py top.log [2nd.top.log ...]
```
