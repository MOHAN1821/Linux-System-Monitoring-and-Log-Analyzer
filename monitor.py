#!/usr/bin/env python3
"""
monitor.py - System Monitoring tool (CPU, memory, disk, uptime, processes).

Beginner friendly. Uses the psutil library, which is the Python version of
the Linux commands top, free and df.

Run it with:
    python monitor.py
    python monitor.py --top 5
    python monitor.py --sort memory
    python monitor.py --report reports/system_report.txt
"""

import argparse
import os
import platform
import time
from datetime import datetime

# psutil = Python System Utilities. It reads the same information that
# "top", "free -h" and "df -h" show on Linux.
import psutil


# ---------------------------------------------------------------------
# SMALL HELPERS
# ---------------------------------------------------------------------
def bytes_to_gb(number):
    """Convert bytes into gigabytes and round it to 1 decimal place."""
    return round(number / (1024 ** 3), 1)


def get_host_name():
    """Return the name of the computer (for example MOHAN-PC)."""
    return platform.node()


def get_current_date():
    """Return today's date as YYYY-MM-DD, for example 2026-09-29."""
    return datetime.now().strftime("%Y-%m-%d")


def get_current_time():
    """Return the current time as HH:MM:SS, for example 21:15:32."""
    return datetime.now().strftime("%H:%M:%S")


def default_disk_path():
    """
    Windows uses drive letters (C:\\), Linux uses mount points (/).
    We pick the correct one automatically.
    """
    if os.name == "nt":
        return os.environ.get("SystemDrive", "C:") + "\\"
    return "/"


# ---------------------------------------------------------------------
# 1. CPU INFORMATION
# ---------------------------------------------------------------------
def get_cpu_usage():
    """
    psutil.cpu_percent(interval=1) waits 1 second and then returns the
    average CPU usage of the whole system, for example 25.4.
    """
    try:
        return psutil.cpu_percent(interval=1)
    except Exception as error:
        print("Could not read CPU usage: %s" % error)
        return 0.0


def get_cpu_count():
    """Return the number of CPU cores, for example 8."""
    try:
        return psutil.cpu_count() or 1
    except Exception:
        return 1


# ---------------------------------------------------------------------
# 2. MEMORY (RAM) INFORMATION
# ---------------------------------------------------------------------
def get_memory_info():
    """
    Returns a dictionary with:
        percent      -> RAM used in percent
        total_gb     -> total RAM in GB
        available_gb -> free RAM in GB
    """
    try:
        memory = psutil.virtual_memory()
        return {
            "percent": memory.percent,
            "total_gb": bytes_to_gb(memory.total),
            "available_gb": bytes_to_gb(memory.available),
        }
    except Exception as error:
        print("Could not read memory information: %s" % error)
        return {"percent": 0.0, "total_gb": 0.0, "available_gb": 0.0}


# ---------------------------------------------------------------------
# 3. DISK INFORMATION
# ---------------------------------------------------------------------
def get_disk_info(path):
    """
    Returns a dictionary with:
        percent   -> disk used in percent
        total_gb  -> total disk size in GB
        free_gb   -> free disk space in GB
    """
    try:
        disk = psutil.disk_usage(path)
        return {
            "path": path,
            "percent": disk.percent,
            "total_gb": bytes_to_gb(disk.total),
            "free_gb": bytes_to_gb(disk.free),
        }
    except PermissionError:
        print("Permission denied while reading disk: %s" % path)
        return None
    except Exception as error:
        print("Could not read disk information: %s" % error)
        return None


# ---------------------------------------------------------------------
# 4. SYSTEM UPTIME
# ---------------------------------------------------------------------
def get_uptime():
    """
    psutil.boot_time() gives the moment the computer was switched on.
    time.time() - boot_time = number of seconds the system has been up.
    We convert seconds into days / hours / minutes.
    """
    try:
        seconds = time.time() - psutil.boot_time()
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)

        parts = []
        if days > 0:
            parts.append("%d day(s)" % days)
        parts.append("%d hour(s)" % hours)
        parts.append("%d minute(s)" % minutes)
        return " ".join(parts)
    except Exception as error:
        print("Could not read uptime: %s" % error)
        return "unknown"


# ---------------------------------------------------------------------
# 5. RUNNING PROCESSES
# ---------------------------------------------------------------------
def get_processes():
    """
    Returns a list of dictionaries - one entry for every running process.
    Each entry has: pid, name, cpu, memory.

    Note: psutil returns 0.0 the first time we ask for a process CPU value.
    That is why we do two passes: the first one "starts the measuring",
    the second one (after 1 second) gives the real number.
    """
    processes = []

    # First pass - start measuring every process.
    for process in psutil.process_iter(["pid", "name"]):
        try:
            process.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception:
            continue

    time.sleep(1)  # give the system a moment to collect real numbers

    # Second pass - read the values.
    for process in psutil.process_iter(["pid", "name"]):
        info = process.info
        # PID 0 on Windows is the "System Idle Process" - not a real program.
        if info["pid"] == 0:
            continue
        try:
            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu": process.cpu_percent(interval=None),
                "memory": process.memory_percent(),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # The process ended, or it is protected. We skip it.
            continue
        except Exception:
            continue

    return processes


def get_top_processes(sort_by="cpu", count=5):
    """
    Sort all processes and return only the top 'count' of them.
    sort_by can be "cpu" or "memory".
    """
    processes = get_processes()
    field = "memory" if sort_by == "memory" else "cpu"
    return sorted(processes, key=lambda p: p[field], reverse=True)[:count]


# ---------------------------------------------------------------------
# 6. PRINTING THE REPORT
# ---------------------------------------------------------------------
def print_header():
    print("=" * 40)
    print("       LINUX SYSTEM MONITOR")
    print("=" * 40)
    print("Date            : %s" % get_current_date())
    print("Time            : %s" % get_current_time())
    print("Hostname        : %s" % get_host_name())
    print("")


def print_system_section(disk_path):
    """Print CPU, memory, disk and uptime information."""
    cpu = get_cpu_usage()
    memory = get_memory_info()
    disk = get_disk_info(disk_path)
    uptime = get_uptime()

    print("CPU Usage       : %.1f%%" % cpu)
    print("CPU Cores       : %d" % get_cpu_count())
    print("Memory Usage    : %.1f%%" % memory["percent"])
    print("Total Memory    : %.1f GB" % memory["total_gb"])
    print("Available Memory: %.1f GB" % memory["available_gb"])
    print("")
    if disk:
        print("Disk Usage      : %.1f%%   (checked %s)" % (disk["percent"], disk["path"]))
        print("Total Disk      : %.1f GB" % disk["total_gb"])
        print("Free Disk       : %.1f GB" % disk["free_gb"])
    else:
        print("Disk Usage      : not available")
    print("")
    print("System Uptime   : %s" % uptime)
    print("")


def print_processes_table(processes):
    """Print the top processes in a simple table."""
    print("-" * 40)
    print("TOP %d PROCESSES" % len(processes))
    print("-" * 40)
    print("%-8s %-20s %8s %10s" % ("PID", "PROCESS", "CPU%", "MEMORY%"))

    if not processes:
        print("(no process information available)")
        print("")
        return

    for process in processes:
        print("%-8s %-20s %8.1f %10.1f" % (
            process["pid"],
            process["name"][:20],
            process["cpu"],
            process["memory"],
        ))
    print("")


def print_final_banner():
    """Prints the closing banner at the end of the report."""
    print("=" * 40)
    print(" Monitoring completed successfully")
    print("=" * 40)


def show_report(sort_by="cpu", top=5, disk_path=None):
    """Print the complete monitoring report (used on screen and in files)."""
    if disk_path is None:
        disk_path = default_disk_path()

    print_header()
    print_system_section(disk_path)
    print_processes_table(get_top_processes(sort_by=sort_by, count=top))


# ---------------------------------------------------------------------
# 7. SAVE THE REPORT INTO A FILE
# ---------------------------------------------------------------------
def save_report(report_file, sort_by="cpu", top=5, disk_path=None):
    """
    Save the report into a file.
    The file is opened in append mode ("a"), so every run adds a new
    report at the end of the file instead of deleting the old one.
    """
    if disk_path is None:
        disk_path = default_disk_path()

    try:
        folder = os.path.dirname(report_file)
        if folder and not os.path.isdir(folder):
            os.makedirs(folder)          # create reports/ if missing

        cpu = get_cpu_usage()
        memory = get_memory_info()
        disk = get_disk_info(disk_path)
        top_processes = get_top_processes(sort_by=sort_by, count=top)

        with open(report_file, "a", encoding="utf-8") as file_object:
            file_object.write("=" * 40 + "\n")
            file_object.write("       LINUX SYSTEM MONITOR\n")
            file_object.write("=" * 40 + "\n")
            file_object.write("Date            : %s\n" % get_current_date())
            file_object.write("Time            : %s\n" % get_current_time())
            file_object.write("Hostname        : %s\n" % get_host_name())
            file_object.write("CPU Usage       : %.1f%%\n" % cpu)
            file_object.write("CPU Cores       : %d\n" % get_cpu_count())
            file_object.write("Memory Usage    : %.1f%%\n" % memory["percent"])
            file_object.write("Total Memory    : %.1f GB\n" % memory["total_gb"])
            file_object.write("Available Memory: %.1f GB\n" % memory["available_gb"])
            file_object.write("Disk Usage      : %.1f%%\n" % (disk["percent"] if disk else 0))
            file_object.write("Total Disk      : %.1f GB\n" % (disk["total_gb"] if disk else 0))
            file_object.write("Free Disk       : %.1f GB\n" % (disk["free_gb"] if disk else 0))
            file_object.write("System Uptime   : %s\n" % get_uptime())
            file_object.write("-" * 40 + "\n")
            file_object.write("TOP %d PROCESSES (by %s)\n" % (len(top_processes),
                                                              sort_by.upper()))
            file_object.write("-" * 40 + "\n")
            file_object.write("%-8s %-20s %8s %10s\n" % ("PID", "PROCESS", "CPU%", "MEMORY%"))
            for process in top_processes:
                file_object.write("%-8s %-20s %8.1f %10.1f\n" % (
                    process["pid"], process["name"][:20],
                    process["cpu"], process["memory"]))
            file_object.write("\n")

        print("System report saved to: %s" % report_file)
    except PermissionError:
        print("Permission denied: cannot write to %s" % report_file)
    except OSError as error:
        print("Could not write the report file: %s" % error)


# ---------------------------------------------------------------------
# 8. MAIN FUNCTION - reads the command line options
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Monitor CPU, memory, disk, uptime and running processes.")
    parser.add_argument("--top", type=int, default=5,
                        help="How many top processes to show (default 5).")
    parser.add_argument("--sort", choices=["cpu", "memory"], default="cpu",
                        help="Sort processes by cpu or memory (default cpu).")
    parser.add_argument("--disk", default=None,
                        help="Disk to check (default: / on Linux, C:\\ on Windows).")
    parser.add_argument("--report", default="",
                        help="Also save the report into this file.")
    args = parser.parse_args()

    if args.report:
        # Save first, then print, so the "saved to ..." message does not
        # appear in the middle of the report on the screen.
        # The automation script (system_monitor.ps1 / .sh) prints the
        # closing banner after the log analysis part is also finished.
        save_report(args.report, sort_by=args.sort, top=args.top,
                    disk_path=args.disk)

    show_report(sort_by=args.sort, top=args.top, disk_path=args.disk)

    if not args.report:
        print_final_banner()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
