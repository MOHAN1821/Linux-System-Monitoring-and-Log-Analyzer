#!/usr/bin/env python3
"""
log_analyzer.py - Log file analyzer for a system administrator.

What the program does:
  1. Takes a log file path as an argument.
  2. If that file does not exist, it falls back to a local sample.log
     (this is what makes the project work on Windows).
  3. Searches for the keywords ERROR, WARNING, FAILED and CRITICAL.
  4. Counts how many times each keyword appears.
  5. Prints the latest 10 matching lines of each keyword.
  6. Handles missing files and permission errors politely.

Run it with:
    python log_analyzer.py
    python log_analyzer.py sample.log
    python log_analyzer.py /var/log/syslog
    python log_analyzer.py sample.log --limit 5
    python log_analyzer.py sample.log --report reports/log_report.txt
"""

import argparse
import os
from collections import Counter
from datetime import datetime
import platform

# The four keywords we are looking for in every log file.
KEYWORDS = ["ERROR", "WARNING", "FAILED", "CRITICAL"]

# On Linux the interesting log files usually need sudo. On Windows they
# simply do not exist, so we use them only if they are really there.
LINUX_LOG_FILES = [
    "/var/log/syslog",
    "/var/log/auth.log",
    "/var/log/messages",
    "/var/log/kern.log",
]

# Name of the local sample log file used as a fallback.
SAMPLE_FILE = "sample.log"

# The sample log content, written to disk only if sample.log is missing.
SAMPLE_LOG_TEXT = """\
Sep 29 08:01:12 ubuntu systemd[1]: Started Session 12 of user ubuntu.
Sep 29 08:01:15 ubuntu sshd[1201]: Server listening on 0.0.0.0 port 22.
Sep 29 08:04:02 ubuntu CRITICAL: disk /dev/sda1 is almost full, only 2% left
Sep 29 08:05:33 ubuntu kernel: [12345.67] EXT4-fs (sda1): mounted filesystem
Sep 29 08:07:41 ubuntu sshd[1244]: Failed password for invalid user admin
Sep 29 08:07:42 ubuntu sshd[1244]: Failed password for invalid user test
Sep 29 08:07:44 ubuntu sshd[1244]: Failed password for root from 10.0.0.9
Sep 29 08:09:10 ubuntu WARNING: configuration file /etc/app.conf is old
Sep 29 08:11:55 ubuntu app[2210]: ERROR: could not connect to database server
Sep 29 08:12:01 ubuntu app[2210]: ERROR: timeout while waiting for lock file
Sep 29 08:13:26 ubuntu cron[2480]: WARNING: job backup took longer than usual
Sep 29 08:15:03 ubuntu app[2214]: INFO: service restarted successfully
Sep 29 08:16:47 ubuntu systemd[1]: WARNING: unit nginx.service entered failed state
Sep 29 08:18:20 ubuntu kernel: [12890.11] usb 1-2: device disconnect
Sep 29 08:19:34 ubuntu app[2230]: CRITICAL: database connection lost, exiting
Sep 29 08:20:12 ubuntu sshd[1302]: Accepted password for ubuntu from 10.0.0.5
Sep 29 08:21:59 ubuntu network[900]: WARNING: interface eth0 is down
Sep 29 08:24:31 ubuntu app[2245]: ERROR: permission denied writing /var/app/data
Sep 29 08:26:08 ubuntu app[2245]: ERROR: user admin failed to login
Sep 29 08:27:45 ubuntu logrotate[2600]: ERROR: could not rotate /var/log/app.log
Sep 29 08:29:02 ubuntu systemd[1]: Started Daily apt upgrade activities.
Sep 29 08:30:19 ubuntu mail[1180]: WARNING: /var/spool/mail is growing too big
Sep 29 08:32:44 ubuntu app[2260]: INFO: request handled in 120 ms
Sep 29 08:34:10 ubuntu kernel: [13210.44] TCP: request_sock_TCP: overflow
Sep 29 08:36:27 ubuntu app[2270]: FAILED to write checkpoint to disk
Sep 29 08:38:55 ubuntu app[2270]: FAILED to open configuration file
Sep 29 08:40:03 ubuntu cron[2700]: WARNING: command /usr/local/backup.sh timed out
Sep 29 08:42:36 ubuntu systemd[1]: Started Cleanup of Temporary Directories.
Sep 29 08:44:51 ubuntu app[2285]: ERROR: unable to resolve host api.example.com
Sep 29 08:47:12 ubuntu db[1500]: CRITICAL: replication lag too high
Sep 29 08:49:30 ubuntu sshd[1400]: Failed publickey for git from 10.0.0.8
Sep 29 08:51:47 ubuntu app[2290]: INFO: daily backup finished
Sep 29 08:54:05 ubuntu WARNING: low disk space on / (12% free)
Sep 29 08:56:22 ubuntu app[2295]: ERROR: timeout connecting to payment service
Sep 29 08:58:40 ubuntu kernel: [13800.90] Out of memory: Kill process 2295
Sep 29 09:01:15 ubuntu systemd[1]: Started Update UTMP about System Boot.
Sep 29 09:03:33 ubuntu app[2300]: FAILED to start worker thread
Sep 29 09:05:58 ubuntu WARNING: certificate for internal.corp expires in 7 days
Sep 29 09:08:21 ubuntu app[2310]: ERROR: invalid JSON received from client
Sep 29 09:10:47 ubuntu logrotate[2800]: WARNING: old logs were not compressed
Sep 29 09:13:04 ubuntu app[2320]: INFO: cache warmed up in 3 seconds
Sep 29 09:15:29 ubuntu systemd[1]: Started daily system maintenance job.
Sep 29 09:17:56 ubuntu app[2330]: ERROR: file /data/report.csv not found
Sep 29 09:20:23 ubuntu WARNING: high CPU load detected on the server
Sep 29 09:22:50 ubuntu app[2340]: FAILED to authenticate admin user
Sep 29 09:25:17 ubuntu kernel: [14200.55] EXT4-fs error on device sda1
Sep 29 09:27:44 ubuntu app[2350]: INFO: shutting down worker 3
Sep 29 09:30:11 ubuntu systemd[1]: Reached target Multi-User System.
"""


# ---------------------------------------------------------------------
# 1. SMALL HELPERS (date, time, hostname)
# ---------------------------------------------------------------------
def get_current_date():
    """Return today's date as YYYY-MM-DD, for example 2026-09-29."""
    return datetime.now().strftime("%Y-%m-%d")


def get_current_time():
    """Return the current time as HH:MM:SS, for example 21:15:32."""
    return datetime.now().strftime("%H:%M:%S")


def get_host_name():
    """Return the name of the computer, for example MY-PC."""
    return platform.node()


# ---------------------------------------------------------------------
# 2. CREATE THE SAMPLE LOG FILE IF IT IS MISSING
# ---------------------------------------------------------------------
def create_sample_log(path=SAMPLE_FILE):
    """
    Creates sample.log in the current folder if it does not exist yet.
    This is the reason the project also works on Windows, where
    /var/log/syslog does not exist.
    """
    if os.path.exists(path):
        return path

    try:
        with open(path, "w", encoding="utf-8") as file_object:
            file_object.write(SAMPLE_LOG_TEXT)
        print("Created a sample log file: %s" % path)
    except PermissionError:
        print("Permission denied: cannot create %s" % path)
    except OSError as error:
        print("Could not create the sample log file: %s" % error)
    return path


# ---------------------------------------------------------------------
# 2. CHOOSE WHICH LOG FILE TO ANALYZE
# ---------------------------------------------------------------------
def choose_log_file(requested_file):
    """
    Logic:
      - if the user gave a path, we use that path;
      - otherwise we look for a Linux log file (/var/log/syslog, ...);
      - if nothing is found, we create and use sample.log.
    """
    if requested_file:
        return requested_file

    for linux_path in LINUX_LOG_FILES:
        if os.path.exists(linux_path):
            return linux_path

    return create_sample_log(SAMPLE_FILE)


# ---------------------------------------------------------------------
# 3. COUNT THE KEYWORDS
# ---------------------------------------------------------------------
def count_keywords(path, keywords=KEYWORDS):
    """
    Reads the file line by line and counts each keyword.

    Returns something like:
        {'ERROR': 7, 'WARNING': 6, 'FAILED': 5, 'CRITICAL': 3}
    """
    counts = Counter({word: 0 for word in keywords})

    with open(path, "r", encoding="utf-8", errors="ignore") as log_file:
        for line in log_file:
            for word in keywords:
                if word in line:
                    counts[word] += 1

    return counts


# ---------------------------------------------------------------------
# 4. GET THE LATEST MATCHING LINES
# ---------------------------------------------------------------------
def get_latest_any(path, limit=10):
    """
    Returns the last 'limit' lines of the file that contain ANY of the
    keywords, together with the keyword that was found.

    Example result: [("ERROR", "Sep 29 ... ERROR: connection failed"), ...]
    """
    matches = []

    with open(path, "r", encoding="utf-8", errors="ignore") as log_file:
        for line in log_file:
            for word in KEYWORDS:
                if word in line:
                    line = line.strip()
                    if len(line) > 120:          # keep the line short
                        line = line[:120] + "..."
                    matches.append((word, line))
                    break
            if len(matches) > limit:
                matches.pop(0)                   # remove the oldest line

    return matches


# ---------------------------------------------------------------------
# 5. PRINT THE LOG ANALYSIS REPORT
# ---------------------------------------------------------------------
def print_report(path, limit=10):
    """Prints the counts and the latest matching lines of the log file."""
    counts = count_keywords(path)
    total_errors = counts["ERROR"] + counts["FAILED"] + counts["CRITICAL"]

    # Overall health of the log file.
    if counts["CRITICAL"] > 0 or counts["ERROR"] > 0:
        status = "FAILURE - errors found, action needed"
    elif counts["WARNING"] > 0 or counts["FAILED"] > 0:
        status = "WARNING - please check the system"
    else:
        status = "HEALTHY - no problems found"

    size_kb = round(os.path.getsize(path) / 1024, 1)

    print("-" * 40)
    print("LOG ANALYSIS")
    print("-" * 40)
    print("Log File        : %s" % path)
    print("File Size       : %.1f KB" % size_kb)
    print("Status          : %s" % status)
    print("")

    print("KEYWORD COUNTS")
    print("-" * 40)
    for word in KEYWORDS:
        print("%-10s : %d" % (word, counts[word]))
    print("Total Errors    : %d   (ERROR + FAILED + CRITICAL)" % total_errors)
    print("Total Warnings  : %d" % counts["WARNING"])
    print("")

    print("RECENT LOG ENTRIES")
    print("-" * 40)
    recent = get_latest_any(path, limit=limit)
    if recent:
        for word, line in recent:
            print("[%s] %s" % (word, line))
    else:
        print("(no ERROR, WARNING, FAILED or CRITICAL entries found)")
    print("")


# ---------------------------------------------------------------------
# 6. SAVE THE LOG REPORT INTO A FILE
# ---------------------------------------------------------------------
def save_report(path, report_file, limit=10):
    """Writes the same information into a file inside reports/."""
    try:
        folder = os.path.dirname(report_file)
        if folder and not os.path.isdir(folder):
            os.makedirs(folder)

        counts = count_keywords(path)

        with open(report_file, "a", encoding="utf-8") as file_object:
            file_object.write("=" * 40 + "\n")
            file_object.write("LOG ANALYSIS REPORT\n")
            file_object.write("=" * 40 + "\n")
            file_object.write("Date            : %s\n" % get_current_date())
            file_object.write("Time            : %s\n" % get_current_time())
            file_object.write("Hostname        : %s\n" % get_host_name())
            file_object.write("Log File        : %s\n" % path)
            for word in KEYWORDS:
                file_object.write("%-10s : %d\n" % (word, counts[word]))
            file_object.write("-" * 40 + "\n")
            file_object.write("RECENT LOG ENTRIES\n")
            recent = get_latest_any(path, limit=limit) or [("INFO", "(none found)")]
            for word, line in recent:
                file_object.write("[%s] %s\n" % (word, line))
            file_object.write("\n")

        print("Log report saved to: %s" % report_file)
    except PermissionError:
        print("Permission denied: cannot write to %s" % report_file)
    except OSError as error:
        print("Could not write the log report: %s" % error)


def print_final_banner():
    """Prints the closing banner at the end of the log report."""
    print("=" * 40)
    print(" Monitoring completed successfully")
    print("=" * 40)


# ---------------------------------------------------------------------
# 7. MAIN FUNCTION
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Analyze a log file for ERROR, WARNING, FAILED and CRITICAL entries.")
    parser.add_argument("file", nargs="?",
                        help="Path of the log file (default: auto-detect, else sample.log).")
    parser.add_argument("--limit", type=int, default=10,
                        help="How many recent lines to show per keyword (default 10).")
    parser.add_argument("--report", default="",
                        help="Also save the log report into this file.")
    args = parser.parse_args()

    log_file = choose_log_file(args.file)

    # --- Error handling: the file we picked must be readable ---
    if not os.path.exists(log_file):
        print("ERROR: log file not found -> %s" % log_file)
        print("Fix: check the path, or run  python log_analyzer.py sample.log")
        return
    if not os.access(log_file, os.R_OK):
        print("ERROR: no read permission for %s" % log_file)
        print("On Linux log files you usually need:  sudo python3 log_analyzer.py %s"
              % log_file)
        print("Check with:  ls -l %s   and   id" % log_file)
        return

    try:
        print_report(log_file, limit=args.limit)
        if args.report:
            save_report(log_file, args.report, limit=args.limit)
        print_final_banner()          # the last part of the full report
    except PermissionError:
        print("ERROR: permission denied while reading %s" % log_file)
        print("Try again with sudo (Linux only).")
    except IsADirectoryError:
        print("ERROR: %s is a folder, not a log file." % log_file)
    except UnicodeDecodeError:
        print("ERROR: %s is not a normal text log file." % log_file)
    except OSError as error:
        print("ERROR while reading the log file: %s" % error)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
