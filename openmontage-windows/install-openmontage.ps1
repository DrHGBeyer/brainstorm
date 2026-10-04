<#
.SYNOPSIS
    Installs OpenMontage (https://github.com/calesthio/OpenMontage) permanently on Windows 11.

.DESCRIPTION
    1. Installs missing prerequisites via winget: Git, Python 3.11, Node.js LTS, FFmpeg.
    2. Clones OpenMontage into -InstallDir (or updates an existing checkout with git pull).
    3. Creates the Python virtual environment .venv and installs requirements.txt + piper-tts.
    4. Installs the Remotion composer (npm install) and warms the HyperFrames npx cache.
    5. Creates .env from .env.example if it does not exist yet.
    6. Optional (-Demo): renders the three zero-key demo videos.

    The script can be run again at any time; it skips what is already there and updates the rest.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\install-openmontage.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\install-openmontage.ps1 -InstallDir D:\Video\OpenMontage -Demo
#>

[CmdletBinding()]
param(
    [string]$InstallDir = "C:\Projekte\OpenMontage",
    [switch]$Demo
)

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/calesthio/OpenMontage.git"

function Write-Step([string]$Text) { Write-Host ""; Write-Host "==> $Text" -ForegroundColor Cyan }
function Write-Ok([string]$Text)   { Write-Host "    [ok] $Text" -ForegroundColor Green }
function Write-Warn([string]$Text) { Write-Host "    [hinweis] $Text" -ForegroundColor Yellow }

# Runs a native program and stops the script if it returns a non-zero exit code.
function Invoke-Native {
    param([string]$Exe, [string[]]$Arguments, [switch]$AllowFailure)
    # Out-Host keeps the program's output on screen but out of this function's return value.
    & $Exe @Arguments | Out-Host
    $code = $LASTEXITCODE
    if ($code -ne 0 -and -not $AllowFailure) {
        throw "Befehl fehlgeschlagen (Exit-Code $code): $Exe $($Arguments -join ' ')"
    }
    return ($code -eq 0)
}

# Reloads PATH from the registry so freshly installed programs are found in this window.
function Update-SessionPath {
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user    = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$user"
}

function Test-Command([string]$Name) {
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Install-WithWinget([string]$Id, [string]$Label) {
    Write-Host "    Installiere $Label ($Id) ..."
    $ok = Invoke-Native "winget" @("install", "--id", $Id, "-e", "--silent",
        "--accept-source-agreements", "--accept-package-agreements") -AllowFailure
    if (-not $ok) { Write-Warn "winget meldete einen Fehler fuer $Label - pruefe, ob es trotzdem installiert ist." }
    Update-SessionPath
}

# Finds a Python 3.10+ interpreter; prefers the py launcher with 3.11.
function Find-Python {
    if (Test-Command "py") {
        # Windows PowerShell 5.1 turns redirected stderr into errors; don't let "Stop" abort here.
        $previous = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        try {
            foreach ($v in @("-3.11", "-3.12", "-3.10")) {
                & py $v -c "import sys" 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) { return @("py", $v) }
            }
        } finally { $ErrorActionPreference = $previous }
    }
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:ProgramFiles\Python311\python.exe"
    )
    foreach ($c in $candidates) { if (Test-Path $c) { return @($c) } }
    # No output at all (not $null), so that @(Find-Python) yields an empty array.
}

function Get-NodeMajor {
    if (-not (Test-Command "node")) { return 0 }
    $v = (& node --version) -replace "^v", ""
    return [int]($v.Split(".")[0])
}

# ---------------------------------------------------------------------------
Write-Host "OpenMontage-Installation fuer Windows" -ForegroundColor White
Write-Host "Zielordner: $InstallDir"

if ($InstallDir -match "OneDrive") {
    Write-Warn "Der Zielordner liegt in OneDrive. OneDrive wuerde zehntausende kleine Dateien synchronisieren."
    Write-Warn "Empfohlen: ein Ordner ausserhalb von OneDrive, z. B. C:\Projekte\OpenMontage."
    $answer = Read-Host "    Trotzdem fortfahren? (j/n)"
    if ($answer -notmatch "^[jJyY]") { exit 1 }
}

if (-not (Test-Command "winget")) {
    throw "winget wurde nicht gefunden. Installiere bzw. aktualisiere 'App-Installer' aus dem Microsoft Store und starte das Skript erneut."
}

# ---- 1. Prerequisites -----------------------------------------------------
Write-Step "1/6  Voraussetzungen pruefen"

if (Test-Command "git") { Write-Ok "Git vorhanden" } else { Install-WithWinget "Git.Git" "Git" }

$pythonCmd = @(Find-Python)
if ($pythonCmd.Count -gt 0) { Write-Ok "Python vorhanden ($($pythonCmd -join ' '))" }
else {
    Install-WithWinget "Python.Python.3.11" "Python 3.11"
    $pythonCmd = @(Find-Python)
}

$nodeMajor = Get-NodeMajor
if ($nodeMajor -ge 22) { Write-Ok "Node.js vorhanden (v$nodeMajor)" }
elseif ($nodeMajor -gt 0) {
    Write-Warn "Node.js v$nodeMajor ist zu alt (HyperFrames braucht 22+). Aktualisiere ..."
    Install-WithWinget "OpenJS.NodeJS.LTS" "Node.js LTS"
}
else { Install-WithWinget "OpenJS.NodeJS.LTS" "Node.js LTS" }

if (Test-Command "ffmpeg") { Write-Ok "FFmpeg vorhanden" } else { Install-WithWinget "Gyan.FFmpeg" "FFmpeg" }

# Final check - some installers only become visible in a new window.
$missing = @()
if (-not (Test-Command "git"))  { $missing += "Git" }
if ($pythonCmd.Count -eq 0)      { $missing += "Python" }
if ((Get-NodeMajor) -lt 18)     { $missing += "Node.js" }
if (-not (Test-Command "ffmpeg")) { $missing += "FFmpeg" }
if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "Noch nicht gefunden: $($missing -join ', ')" -ForegroundColor Red
    Write-Host "Bitte PowerShell schliessen, neu oeffnen (ggf. Rechner neu starten) und das Skript erneut ausfuehren." -ForegroundColor Red
    exit 1
}
if ((Get-NodeMajor) -lt 22) { Write-Warn "Node.js ist aelter als v22 - Remotion laeuft, HyperFrames evtl. nicht." }

$pyExe  = $pythonCmd[0]
$pyArgs = @($pythonCmd | Select-Object -Skip 1)

# ---- 2. Clone / update ----------------------------------------------------
Write-Step "2/6  OpenMontage herunterladen"
Invoke-Native "git" @("config", "--global", "core.longpaths", "true") | Out-Null

if (Test-Path (Join-Path $InstallDir ".git")) {
    Write-Host "    Vorhandene Installation gefunden - aktualisiere mit git pull ..."
    Invoke-Native "git" @("-C", $InstallDir, "pull", "--ff-only") | Out-Null
} else {
    $parent = Split-Path $InstallDir -Parent
    if ($parent -and -not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    Invoke-Native "git" @("clone", $RepoUrl, $InstallDir) | Out-Null
}
Write-Ok "Quellcode in $InstallDir"
Set-Location $InstallDir

# ---- 3. Python environment ------------------------------------------------
Write-Step "3/6  Python-Umgebung (.venv) und Pakete"
$venvPy = Join-Path $InstallDir ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Invoke-Native $pyExe ($pyArgs + @("-m", "venv", ".venv")) | Out-Null
}
Invoke-Native $venvPy @("-m", "pip", "install", "--upgrade", "pip") | Out-Null
Invoke-Native $venvPy @("-m", "pip", "install", "-r", "requirements.txt") | Out-Null
Write-Ok "requirements.txt installiert"

if (Invoke-Native $venvPy @("-m", "pip", "install", "piper-tts") -AllowFailure) {
    Write-Ok "Piper (Offline-Sprachausgabe) installiert"
} else {
    Write-Warn "piper-tts konnte nicht installiert werden - Sprachausgabe dann nur ueber Cloud-Anbieter."
}

# ---- 4. Remotion + HyperFrames --------------------------------------------
Write-Step "4/6  Remotion-Composer (npm install)"
Push-Location (Join-Path $InstallDir "remotion-composer")
try {
    if (-not (Invoke-Native "npm.cmd" @("install") -AllowFailure)) {
        Write-Warn "npm install fehlgeschlagen - versuche Ausweichweg aus der README (npx --yes npm install) ..."
        Invoke-Native "npx.cmd" @("--yes", "npm", "install") | Out-Null
    }
} finally { Pop-Location }
Write-Ok "Remotion-Composer installiert"

Write-Step "5/6  HyperFrames-Cache vorwaermen"
if (Invoke-Native "npx.cmd" @("--yes", "hyperframes", "--version") -AllowFailure) {
    Write-Ok "HyperFrames bereit"
} else {
    Write-Warn "HyperFrames-Cache konnte nicht vorgewaermt werden - wird beim ersten Rendern nachgeladen."
}

# ---- 5. .env ---------------------------------------------------------------
Write-Step "6/6  Konfigurationsdatei .env"
if (Test-Path ".env") { Write-Ok ".env existiert bereits - unveraendert gelassen" }
else { Copy-Item ".env.example" ".env"; Write-Ok ".env aus .env.example angelegt" }

# ---- Optional demo ---------------------------------------------------------
if ($Demo) {
    Write-Step "Demo-Videos rendern (dauert einige Minuten; beim ersten Mal laedt Remotion einen Browser)"
    Invoke-Native $venvPy @("render_demo.py") | Out-Null
    Write-Ok "Videos in $(Join-Path $InstallDir 'projects\demos\renders')"
}

Write-Host ""
Write-Host "Fertig! OpenMontage ist installiert in: $InstallDir" -ForegroundColor Green
Write-Host "  Demo testen:     cd `"$InstallDir`"; .\.venv\Scripts\python.exe render_demo.py"
Write-Host "  API-Keys:        notepad `"$(Join-Path $InstallDir '.env')`"   (optional)"
Write-Host "  Arbeiten:        Ordner in der Claude-Desktop-App (Code, lokal) oeffnen"
Write-Host "                   oder im Terminal: cd `"$InstallDir`"; claude"
