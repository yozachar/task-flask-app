#!/bin/pwsh

$ErrorActionPreference="Stop"

# Sub commands and usage
if ($args.Count -eq 0 -or $args[0] -eq "h") {
    Write-Host "Usage: ./dev [i lm cd pv]"
    Write-Host "    i: install and setup project"
    Write-Host "    l: start local                   m: cease local"
    Write-Host "    c: start (and run) containers    d: cease (and remove) containers"
    Write-Host "    p: prune dangling objects        v: prune volumes"
    # Write-Host "    e: prune everything"
    exit 1
}

# Check if the environment file exists
if (!(Test-Path -Path ".env")) {
    Write-Host "E: Environment file `.env` not found"
    exit 1
}

# Load the environment file
$envVars = Get-Content -Path ".env" -Raw
Invoke-Expression $envVars

# Determine the containerization command
$cmd = ""
$cmdCompose = ""
if (Get-Command -Name "podman" -ErrorAction SilentlyContinue) {
    $cmd = "podman"
    $cmdCompose = "podman-compose"
} elseif (Get-Command -Name "docker" -ErrorAction SilentlyContinue) {
    $cmd = "docker"
    $cmdCompose = "docker compose"
} else {
    Write-Host "E: Program requires either podman(-compose) or docker(-compose)"
    exit 1
}

# Handle sub commands
switch ($args[0]) {
    "i" {
        # Install and setup
        if (Test-Path -Path ".marker") {
            Write-Host "I: Project is ready"
            Write-Host "I: Pass h for help"
            exit 0
        }

        # Check if Python is installed
        if (!(Get-Command -Name "python" -ErrorAction SilentlyContinue)) {
            Write-Host "E: Please install Python"
            exit 1
        }

        # Create a virtual environment if it doesn't exist
        if (!(Test-Path -Path ".venv")) {
            python -m venv .venv
        }

        # Activate the virtual environment
        .\.venv\Scripts\Activate.ps1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "E: Virtual environment activation failed"
            exit 1
        }

        # Check if pip is installed
        if (!(Get-Command -Name "pip" -ErrorAction SilentlyContinue)) {
            Write-Host "E: Cannot find pip"
            exit 1
        }

        # Install required packages
        if (!(Get-Command -Name "flask" -ErrorAction SilentlyContinue) -or !(Get-Command -Name "celery" -ErrorAction SilentlyContinue)) {
            pip install -r requirements.package.txt
        }

        New-Item -Path ".marker" -ItemType File
        Write-Host "I: Project is ready"
    }
    "l" {
        # Construct local deployment
        if (!(Test-Path -Path ".marker")) {
            Write-Host "E: Project not ready, please install and set it up"
            Write-Host "I: Pass h for help"
            exit 1
        }

        # Create the logs directory if it doesn't exist
        if (!(Test-Path -Path "logs")) {
            New-Item -Path "logs" -ItemType Directory
        }

        # Start Redis and Postgres
        & $cmdCompose -p cajon -f compose.yaml up -d redis postgres
        Start-Sleep -s 5

        # Activate the virtual environment
        .\.venv\Scripts\Activate.ps1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "E: Virtual environment activation failed"
            exit 1
        }

        # Start Celery
        $celeryProcess = Start-Process -FilePath "celery" -ArgumentList "-A src.cajon.main worker" -RedirectStandardOutput "logs\celery.log" -RedirectStandardError "logs\celery.log" -PassThru
        $celeryPid = $celeryProcess.Id
        Write-Host "Celery started with PID $celeryPid"

        # Start Flask
        flask -A src.cajon.main run
        exit $LASTEXITCODE
    }
    "m" {
        # Destruct local deployment
        # Stop Celery (gets killed by CTRL+C on previous process group)
        # $celeryPid = Get-Content -Path "logs\pid.log" -First 1
        # if ($celeryPid) {
        #     Stop-Process -Id $celeryPid -Force
        #     Write-Host "Stopped Celery process with PID $celeryPid."
        # }

        # Stop Redis and Postgres
        & $cmdCompose -p cajon -f compose.yaml down redis postgres

        # Remove the pod if using Podman
        if ($cmd -eq "podman") {
            & $cmd pod rm pod_cajon
        }
        exit $
            }
    "c" {
        # Construct containerized deployment
        & $cmdCompose -p cajon -f compose.yaml up -d
        exit $LASTEXITCODE
    }
    "d" {
        # Destruct containerized deployment
        & $cmdCompose -p cajon -f compose.yaml down
        exit $LASTEXITCODE
    }
    "p" {
        # Prune dangling objects
        & $cmd system prune --force
        exit $LASTEXITCODE
    }
    "v" {
        # Prune volumes
        & $cmd system prune --volumes --force
        exit $LASTEXITCODE
    }
    # "e" {
    #     & $cmd system prune --all --force
    #     exit $LASTEXITCODE
    # }
    default {
        Write-Host "E: Invalid command"
        Write-Host "I: Pass h for help"
        exit 1
    }
}
