# =====================================================================
#  system_monitor.ps1
#  Windows (PowerShell) version of system_monitor.sh
#
#  It does the same job:
#    1. Checks that Python 3 and psutil are installed.
#    2. Runs monitor.py   and saves the result in reports\system_report.txt
#    3. Runs log_analyzer.py and saves the result in reports\log_report.txt
#    4. Repeats every $Interval seconds (optional).
#
#  How to run (from VS Code PowerShell terminal, inside the project folder):
#    powershell -ExecutionPolicy Bypass -File .\system_monitor.ps1
#    powershell -ExecutionPolicy Bypass -File .\system_monitor.ps1 -Interval 30
#    powershell -ExecutionPolicy Bypass -File .\system_monitor.ps1 -Interval 30 -Count 3
# =====================================================================

# ---------------------------------------------------------------------
# PARAMETERS (values you can change when you run the script)
#   -Interval : seconds between two checks   (0 = run only once)
#   -Count    : how many times to run        (0 = run forever)
#   -LogFile  : log file to analyze          (empty = auto-detect)
# ---------------------------------------------------------------------
param(
    [int]$Interval = 0,
    [int]$Count = 0,
    [string]$LogFile = ""
)

$ErrorActionPreference = "Stop"   # stop the script when a command fails
$ReportDir = "reports"
$SystemReport = Join-Path $ReportDir "system_report.txt"
$LogReport = Join-Path $ReportDir "log_report.txt"

# ---------------------------------------------------------------------
# STEP 1: create the reports folder
# ---------------------------------------------------------------------
if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir | Out-Null
    Write-Host "Created folder: $ReportDir"
}

# ---------------------------------------------------------------------
# STEP 2: check the tools we need
# ---------------------------------------------------------------------
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "ERROR: Python 3 is not installed or not in PATH."
    Write-Host "Download it from https://www.python.org/downloads/ and tick 'Add Python to PATH'."
    exit 1
}

Write-Host "Python is ready. Starting the monitoring run..."

# Install psutil automatically if it is missing.
& python -c "import psutil" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "psutil is not installed. Installing it now..."
    & python -m pip install psutil
}

# ---------------------------------------------------------------------
# STEP 3: one full check (system monitoring + log analysis)
# ---------------------------------------------------------------------
function Run-Once {
    Write-Host ""
    Write-Host "########## CHECK STARTED: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ##########"

    # --- System monitoring ---
    & python monitor.py --report $SystemReport
    if ($LASTEXITCODE -ne 0) { Write-Host "monitor.py failed." }

    # --- Log analysis ---
    if ($LogFile -ne "") {
        & python log_analyzer.py $LogFile --report $LogReport
    } else {
        & python log_analyzer.py --report $LogReport
    }
    if ($LASTEXITCODE -ne 0) { Write-Host "log_analyzer.py failed." }

    Write-Host "########## CHECK FINISHED ##########"
}

# ---------------------------------------------------------------------
# STEP 4: the main loop
# ---------------------------------------------------------------------
$iteration = 0

while ($true) {
    $iteration = $iteration + 1
    Run-Once

    # Stop after $Count runs ($Count = 0 means keep running).
    if ($Count -ne 0 -and $iteration -ge $Count) {
        Write-Host "Finished $iteration check(s)."
        break
    }

    # Stop immediately when no interval was given.
    if ($Interval -le 0) {
        break
    }

    Write-Host "Sleeping for $Interval seconds... (press Ctrl+C to stop)"
    Start-Sleep -Seconds $Interval
}

Write-Host "Reports are stored in: $ReportDir\system_report.txt and $ReportDir\log_report.txt"
