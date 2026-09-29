# Linux System Monitoring and Log Analyzer

A small, beginner-friendly command line project that shows how a **system
administrator** keeps an eye on a machine: how much CPU, memory and disk are
being used, which processes are running, and what is happening inside the
log files.

It is written in **Python 3 + psutil** and comes with two automation scripts:
`system_monitor.ps1` for **Windows PowerShell** and `system_monitor.sh` for
**Linux / macOS / Git Bash**.

The project runs on Windows (VS Code + PowerShell) **and** demonstrates
Linux/Bash knowledge, so it can be shown in an interview on any machine.

---

## 1. Project description

| Part | File | What it does |
|---|---|---|
| System monitoring | `monitor.py` | Shows date, time, hostname, CPU, memory, disk, uptime and the top 5 processes |
| Log analysis | `log_analyzer.py` | Counts `ERROR`, `WARNING`, `FAILED`, `CRITICAL` in a log file and shows the latest 10 matching lines |
| Automation (Windows) | `system_monitor.ps1` | Runs both programs, repeats every N seconds, saves reports into `reports/` |
| Automation (Linux) | `system_monitor.sh` | Exactly the same, written in Bash |

---

## 2. Features

- Current **date**, **time** and **hostname** (using the `datetime` module)
- CPU usage percentage and number of CPU cores
- Memory usage, total memory, available memory
- Disk usage, total disk space, free disk space
- System uptime in a human-readable form (`5 hour(s) 24 minute(s)`)
- Top 5 running processes with PID, name, CPU % and memory %
- Log analysis: counts for ERROR / WARNING / FAILED / CRITICAL
- Latest 10 matching log entries, shown with the level in brackets
- Safe error handling: missing file, no permission, not a text file
- Automatically creates a local `sample.log` when no Linux log file exists
  (so the project also works on Windows)
- Saves every run into `reports/system_report.txt` and
  `reports/log_report.txt`

---

## 3. Technologies used

- **Python 3** - the programming language
- **psutil** - the library that reads CPU / memory / disk / process data
- **datetime** - Python module for the current date and time
- **argparse** - Python module for command line options
- **Bash** (`system_monitor.sh`) - Linux automation
- **PowerShell** (`system_monitor.ps1`) - Windows automation
- **Git** - version control
- Linux concepts: processes, PIDs, `/var/log`, uptime, log levels

---

## 4. Project structure

```
linux-system-monitor/
├── monitor.py            # system monitoring program
├── log_analyzer.py       # log file analyzer
├── system_monitor.ps1    # automation script for Windows PowerShell
├── system_monitor.sh     # automation script for Linux / macOS
├── requirements.txt      # Python dependency: psutil
├── README.md             # this file
├── .gitignore            # files Git must not track
├── sample.log            # created automatically on the first run
└── reports/
    ├── system_report.txt # output of monitor.py
    └── log_report.txt    # output of log_analyzer.py
```

---

## 5. Installation

### 5.1 Windows (VS Code + PowerShell)

```powershell
# 1. check that Python is installed
python --version

# 2. create the project folder and go into it
mkdir linux-system-monitor
cd linux-system-monitor

# 3. install the one dependency
pip install psutil

# (or, if you already have the files)
pip install -r requirements.txt
```

If `python` is not recognised, install Python 3 from <https://www.python.org/downloads/>
and **tick "Add Python to PATH"** during the installation.

### 5.2 Linux / Ubuntu

```bash
sudo apt update
sudo apt install python3 python3-pip git

cd linux-system-monitor
pip3 install -r requirements.txt
```

---

## 6. How to run on Windows (PowerShell)

```powershell
# 1. open the project folder
cd "C:\Users\YOURNAME\Desktop\linux-system-monitor"

# 2. system monitoring only
python monitor.py

# 3. top 5 processes by memory instead of CPU
python monitor.py --sort memory

# 4. show 10 processes
python monitor.py --top 10

# 5. log analysis (uses sample.log automatically)
python log_analyzer.py

# 6. log analysis of a specific file
python log_analyzer.py sample.log
python log_analyzer.py sample.log --limit 5

# 7. run everything and save the reports
powershell -ExecutionPolicy Bypass -File .\system_monitor.ps1

# 8. run it every 30 seconds, 3 times
powershell -ExecutionPolicy Bypass -File .\system_monitor.ps1 -Interval 30 -Count 3
```

> If `powershell` is not found, use `pwsh` instead of `powershell` in the
> command, or run `.\system_monitor.ps1` directly inside PowerShell.

### What the PowerShell script does
1. Checks that Python is installed (and installs `psutil` if it is missing).
2. Creates the `reports` folder.
3. Runs `monitor.py --report reports\system_report.txt`.
4. Runs `log_analyzer.py --report reports\log_report.txt`.
5. Repeats the two steps every `-Interval` seconds, `-Count` times.
6. Press `Ctrl + C` to stop it early.

---

## 7. How to run on Linux / macOS (Bash)

```bash
# 1. go into the project folder
cd linux-system-monitor

# 2. give the script permission to run
chmod +x system_monitor.sh

# 3. run once
./system_monitor.sh

# 4. run every 30 seconds, forever
./system_monitor.sh 30

# 5. run every 60 seconds, 5 times
./system_monitor.sh 60 5

# 6. analyze a real Linux log file (needs administrator rights)
sudo python3 log_analyzer.py /var/log/syslog
sudo python3 log_analyzer.py /var/log/auth.log --limit 20
```

Useful Linux commands related to this project:

| Command | What it does |
|---|---|
| `chmod +x system_monitor.sh` | allows the script to be executed |
| `ps aux` | lists all running processes |
| `top` / `htop` | live process viewer |
| `free -h` | memory usage in human-readable form |
| `df -h` | disk usage of all mounted disks |
| `uptime` | how long the system has been running |
| `ls -l /var/log/syslog` | shows the owner and permissions of a log file |
| `grep -i "error" /var/log/syslog` | searches a log file for errors |
| `id` | shows which user you are and your groups |

**About permissions:** on Linux, files in `/var/log` belong to `root`, so
`PermissionError` is normal. The program catches it and prints a clear
message instead of crashing - simply run the command with `sudo`.

---

## 8. Example output

The numbers below are real output from a test run on Windows.

```
========================================
       LINUX SYSTEM MONITOR
========================================

Date            : 2026-09-29
Time            : 21:30:45
Hostname        : MOHAN

CPU Usage       : 18.5%
CPU Cores       : 12
Memory Usage    : 52.4%
Total Memory    : 15.8 GB
Available Memory: 7.5 GB

Disk Usage      : 46.2%   (checked C:\)
Total Disk      : 476.8 GB
Free Disk       : 256.4 GB

System Uptime   : 5 hour(s) 24 minute(s)

----------------------------------------
TOP 5 PROCESSES
----------------------------------------
PID      PROCESS                  CPU%    MEMORY%
4216     chrome                    8.5        7.2
7824     Code                      5.1        6.4
9140     python                    3.2        2.8
1560     explorer                  1.7        1.9
1024     System                    0.8        1.2

----------------------------------------
LOG ANALYSIS
----------------------------------------
Log File        : sample.log
File Size       : 3.5 KB
Status          : FAILURE - errors found, action needed

KEYWORD COUNTS
----------------------------------------
ERROR      : 9
WARNING    : 10
FAILED     : 4
CRITICAL   : 3
Total Errors    : 16   (ERROR + FAILED + CRITICAL)
Total Warnings  : 10

RECENT LOG ENTRIES
----------------------------------------
[ERROR] Sep 29 09:08:21 ubuntu app[2310]: ERROR: invalid JSON received from client
[WARNING] Sep 29 09:10:47 ubuntu logrotate[2800]: WARNING: old logs were not compressed
[ERROR] Sep 29 09:17:56 ubuntu app[2330]: ERROR: file /data/report.csv not found
[WARNING] Sep 29 09:20:23 ubuntu WARNING: high CPU load detected on the server
[FAILED] Sep 29 09:22:50 ubuntu app[2340]: FAILED to authenticate admin user

========================================
 Monitoring completed successfully
========================================
```

---

## 9. How the project works (step by step)

### 9.1 `monitor.py`

1. **Imports**: `argparse` (command line options), `os`, `platform` (system
   name), `time`, `datetime` (date and time) and `psutil` (the real work).
2. **Date, time, hostname**
   ```python
   datetime.now().strftime("%Y-%m-%d")   # 2026-09-29
   datetime.now().strftime("%H:%M:%S")    # 21:30:45
   platform.node()                        # hostname
   ```
3. **CPU**: `psutil.cpu_percent(interval=1)` compares two readings one second
   apart and returns the average, e.g. `18.5`.
4. **Memory**: `psutil.virtual_memory()` returns `percent`, `total` and
   `available`. These are bytes, so we divide by `1024 ** 3` to get GB
   (`bytes_to_gb`).
5. **Disk**: `psutil.disk_usage(path)` returns `percent`, `total` and `free`.
   The default path is `C:\` on Windows and `/` on Linux (`default_disk_path`).
6. **Uptime**: `time.time() - psutil.boot_time()` gives the number of seconds
   since the computer was switched on; we convert it to days/hours/minutes.
7. **Processes**: `psutil.process_iter()` walks through every process. CPU
   percentage needs **two** calls - the first one starts the measuring, the
   second one (after `time.sleep(1)`) gives the real number. Processes that
   are protected or already finished raise `AccessDenied` / `NoSuchProcess`
   and are skipped.
8. **Sorting**: `sorted(processes, key=lambda p: p["cpu"], reverse=True)`
   puts the busiest process first; `[:count]` keeps only the top 5.
9. **Error handling**: every `psutil` call is inside `try / except`, so the
   program never crashes because of one unreadable value.
10. **Saving**: `open(report_file, "a")` - the `a` (append) mode adds a new
    report below the old one instead of erasing it.

### 9.2 `log_analyzer.py`

1. `create_sample_log()` writes a small fake Linux log (`sample.log`) the
   first time it is needed, so the project works on Windows.
2. `choose_log_file()` uses the path you gave, otherwise the first Linux log
   file that exists (`/var/log/syslog`, `/var/log/auth.log`, ...),
   otherwise the sample file.
3. `count_keywords()` reads the file **line by line** and uses
   `collections.Counter` to count each keyword. Reading line by line matters:
   log files can be gigabytes and we must not load them into memory.
4. `get_latest_any()` keeps only the last 10 matching lines: when the list is
   longer than `limit`, the oldest line is removed with `pop(0)`.
5. `main()` checks the file with `os.path.exists()` and `os.access(..., os.R_OK)`
   and prints a friendly message for a missing file or missing permission,
   instead of showing a Python traceback.
6. The file is opened with `errors="ignore"`, so a log file that contains a
   few strange characters does not crash the program.

### 9.3 `system_monitor.ps1` and `system_monitor.sh`

Both scripts do the same four things: check the tools, create the `reports`
folder, run the two Python programs with `--report`, and repeat with
`Start-Sleep` (PowerShell) or `sleep` (Bash) in a `while` loop.

---

## 10. Git commands

```powershell
# 1. go into the project folder
cd linux-system-monitor

# 2. create the repository
git init

# 3. set your name and email (only the first time on a computer)
git config user.name "Your Name"
git config user.email "you@example.com"

# 4. add all files, 5. see them, 6. commit
git add .
git status
git commit -m "Initial commit: Linux system monitor and log analyzer"

# 7. rename the branch to main
git branch -M main
```

### Uploading to GitHub

1. Go to <https://github.com> and click **New repository**.
2. Name it `linux-system-monitor`, choose **Public**.
3. Do **not** tick "Add a README file" (we already have one).
4. Click **Create repository** and copy the URL.
5. In VS Code PowerShell run:

```powershell
git remote add origin https://github.com/YOUR-USERNAME/linux-system-monitor.git
git push -u origin main
```

Useful extra commands:

```powershell
git status           # which files changed
git log --oneline    # list of all commits
git diff             # what exactly changed
git add monitor.py   # add only one file
git commit -m "fix: handle missing log file"
git push             # upload the new commit
```

---

## 11. Interview questions and answers

**Q1. What does your project do?**
A: It is a small system administration tool. It shows how much CPU, memory
and disk are being used, lists the top processes and analyzes log files for
errors and warnings, and saves everything into report files.

**Q2. Why did you use psutil instead of writing the system calls yourself?**
A: psutil already reads the same information as the Linux commands `top`,
`free` and `df`, but from Python, in a clean cross-platform way. It also works
on Windows, which `free` and `df` do not.

**Q3. How do you get the CPU usage in percent?**
A: `psutil.cpu_percent(interval=1)`. The `interval=1` makes psutil wait one
second and compare two readings, which gives the average usage of all CPU
cores.

**Q4. Why is the process CPU percentage called twice?**
A: Because the first call only starts the measurement and returns 0.0. The
second call, made after one second, returns the real percentage.

**Q5. How do you calculate the uptime?**
A: `time.time() - psutil.boot_time()` gives the number of seconds since the
last boot. I divide by 86400, 3600 and 60 to get days, hours and minutes.

**Q6. How do you handle a log file you are not allowed to read?**
A: Before opening it I check `os.access(path, os.R_OK)`, and I also catch
`PermissionError` around the read. Instead of a traceback, the user sees a
message telling them to run the command with `sudo`.

**Q7. Why do you read the log file line by line?**
A: Log files can be very large. Reading line by line and keeping only the
last 10 matches means the memory usage stays almost constant no matter how
big the file is.

**Q8. What is a process and what is a PID?**
A: A process is a program that is currently running. The PID (Process ID) is
the unique number the operating system gives to it, for example 4216. The
`PID 0` entry called "System Idle Process" on Windows is not a real program,
so I skip it.

**Q9. What is the difference between the .sh and the .ps1 script?**
A: They do exactly the same job. The .sh is for Linux/macOS/Git Bash and the
.ps1 is for Windows PowerShell, so a fresher can run the project on any
machine without installing extra software.

**Q10. What is the exit code / how do you know a command failed?**
A: Bash uses `$?` and PowerShell uses `$LASTEXITCODE`. In the scripts I check
those values so a failing Python program is reported instead of silently
ignored.

**Q11. What does `chmod +x` do?**
A: It adds the execute permission to the file so Linux allows you to run it
as a program. Without it you get "Permission denied". The numeric version is
`chmod 755`, where the owner gets read+write+execute.

**Q12. How would you extend this project?**
A: Add email alerts when the CPU stays above 90%, store the history in a CSV
file so it can be graphed, and add unit tests for the log-counting functions.

---

## 12. Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'psutil'` | `pip install psutil` |
| `'python' is not recognized` | reinstall Python and tick "Add Python to PATH" |
| `powershell` not found | use `pwsh -ExecutionPolicy Bypass -File .\system_monitor.ps1` |
| `running scripts is disabled on this system` | `powershell -ExecutionPolicy Bypass -File .\system_monitor.ps1` |
| `./system_monitor.sh: Permission denied` | `chmod +x system_monitor.sh` |
| `Permission denied` on `/var/log/syslog` | run it with `sudo` (Linux only) |
| Log analysis always shows 0 errors | you are analyzing a file that has no error lines - that is normal |

---

## 13. License

MIT - free to use for learning and interviews.
