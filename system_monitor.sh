#!/bin/bash
# ======================================================================
#  system_monitor.sh  -  Linux / macOS / Git Bash version
#
#  It does the same job as system_monitor.ps1:
#    1. Checks that Python 3 and psutil are installed.
#    2. Runs monitor.py   and saves the result in reports/system_report.txt
#    3. Runs log_analyzer.py and saves the result in reports/log_report.txt
#    4. Repeats every N seconds (optional).
#
#  How to run (Linux, macOS or Windows Git Bash):
#    chmod +x system_monitor.sh
#    ./system_monitor.sh
#    ./system_monitor.sh 30        <- every 30 seconds, forever
#    ./system_monitor.sh 30 5      <- every 30 seconds, 5 times
#
#  On Windows PowerShell use system_monitor.ps1 instead.
# ======================================================================

# ---------------------------------------------------------------
# CONFIGURATION (change these values if you want)
# ---------------------------------------------------------------
INTERVAL="${1:-0}"                 # 0 = run only once
COUNT="${2:-0}"                    # 0 = run forever
LOG_FILE="${LOG_FILE:-}"           # empty = auto-detect a log file
REPORT_DIR="reports"
SYSTEM_REPORT="$REPORT_DIR/system_report.txt"
LOG_REPORT="$REPORT_DIR/log_report.txt"

# Use python3 on Linux/macOS, python on Windows Git Bash.
if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
else
    PYTHON=python
fi

# ---------------------------------------------------------------
# STEP 1: create the reports folder
# ---------------------------------------------------------------
mkdir -p "$REPORT_DIR" || {
    echo "ERROR: cannot create folder $REPORT_DIR"
    exit 1
}

# ---------------------------------------------------------------
# STEP 2: check the tools we need
# ---------------------------------------------------------------
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "ERROR: Python 3 is not installed."
    echo "Linux:   sudo apt update && sudo apt install python3 python3-pip"
    echo "Windows: install Python 3 from python.org and tick 'Add Python to PATH'"
    exit 1
fi

# Install psutil automatically if it is missing.
if ! "$PYTHON" -c "import psutil" >/dev/null 2>&1; then
    echo "psutil is not installed. Installing it now..."
    "$PYTHON" -m pip install psutil || {
        echo "ERROR: could not install psutil. Try: pip3 install psutil"
        exit 1
    }
fi

# ---------------------------------------------------------------
# STEP 3: one full check (system monitoring + log analysis)
# ---------------------------------------------------------------
run_once() {
    echo ""
    echo "########## CHECK STARTED: $(date '+%Y-%m-%d %H:%M:%S') ##########"

    # --- System monitoring ---
    "$PYTHON" monitor.py --report "$SYSTEM_REPORT" || echo "monitor.py failed."

    # --- Log analysis ---
    if [ -n "$LOG_FILE" ]; then
        "$PYTHON" log_analyzer.py "$LOG_FILE" --report "$LOG_REPORT" || echo "log_analyzer.py failed."
    else
        "$PYTHON" log_analyzer.py --report "$LOG_REPORT" || echo "log_analyzer.py failed."
    fi

    echo "########## CHECK FINISHED ##########"
}

# ---------------------------------------------------------------
# STEP 4: the main loop
# ---------------------------------------------------------------
iteration=0

while true; do
    iteration=$((iteration + 1))
    run_once

    # Stop after COUNT runs (0 means run forever).
    if [ "$COUNT" -ne 0 ] && [ "$iteration" -ge "$COUNT" ]; then
        echo "Finished $iteration check(s)."
        break
    fi

    # Stop immediately when no interval was given.
    if [ "$INTERVAL" -le 0 ]; then
        break
    fi

    echo "Sleeping for $INTERVAL seconds... (press Ctrl+C to stop)"
    sleep "$INTERVAL"
done

echo "Reports are stored in: $(pwd)/$REPORT_DIR"
