#!/bin/pwsh

# Check if arguments are provided
if ($args.Count -eq 0 || $args[0] -eq "h") {
    Write-Host "Usage: ./dev [lm cd pv]"
    Write-Host "    l: start local                   m: cease local"
    Write-Host "    c: start (and run) containers    d: cease (and remove) containers"
    Write-Host "    p: prune dangling objects        v: prune volumes"
    # Write-Host "  e: prune everything"
    exit 1
}

# Check if .env file exists
if (!(Test-Path -Path ".env")) {
    Write-Host "E: Environment file `.env` not found"
    exit 1
}

# Load environment variables from .env file
$envVars = Get-Content -Path ".env" -Raw
Invoke-Expression -Command $envVars

# Determine container runtime
if ((Get-Command -Name "podman" -ErrorAction SilentlyContinue) -and (Get-Command -Name "podman-compose" -ErrorAction SilentlyContinue)) {
    $cmd = "podman"
    $composeCmd = "podman-compose"
} elseif ((Get-Command -Name "docker" -ErrorAction SilentlyContinue) -and (Get-Command -Name "docker-compose" -ErrorAction SilentlyContinue)) {
    $cmd = "docker"
    $composeCmd = "docker-compose"
} else {
    Write-Host "E: Program requires either podman(-compose) or docker(-compose)"
    exit 1
}

# Handle commands
switch ($args[0]) {
    "l" {
        if (!(Test-Path -Path "logs")) {
            New-Item -ItemType Directory -Path "logs"
        }
        & $composeCmd -p cajon -f compose.yaml up -d redis postgres
        Start-Sleep -Seconds 5
        $celeryProcess = Start-Process -FilePath "celery" -ArgumentList "-A src.cajon.main worker" -RedirectStandardOutput "logs/celery.log" -RedirectStandardError "logs/celery.log" -PassThru
        $celeryPid = $celeryProcess.Id
        Write-Host "Celery started with PID $celeryPid"
        & flask -A src.cajon.main run
        exit $LASTEXITCODE
    }
    "m" {
        # if not killed along with the earlier process group
        # $celeryPid = Get-Content -Path "logs/pid.log" -First 1
        # if ($celeryPid) {
        #     Stop-Process -Id $celeryPid -Force
        #     Write-Host "Stopped Celery process with PID $celeryPid."
        # }
        & $composeCmd -p cajon -f compose.yaml down redis postgres
        if ($cmd -eq "podman") {
            & $cmd pod rm pod_cajon
        }
        exit $LASTEXITCODE
    }
    "c" {
        & $composeCmd -p cajon -f compose.yaml up -d
        exit $LASTEXITCODE
    }
    "d" {
        & $composeCmd -p cajon -f compose.yaml down
        exit $LASTEXITCODE
    }
    "p" {
        & $cmd system prune --force
        exit $LASTEXITCODE
    }
    "v" {
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
