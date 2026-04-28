# LabVIEW CLI — Complete Reference Guide

> **Version:** NI LabVIEW Command Line Interface 2025 Q3 (all operations current as of August 2025)
> **Platform:** Windows · Linux · macOS

---

## Table of Contents

1. [Overview](#1-overview)
2. [Installation & Prerequisites](#2-installation--prerequisites)
3. [Global Syntax](#3-global-syntax)
4. [Global Flags Reference](#4-global-flags-reference)
5. [Exit Codes](#5-exit-codes)
6. [Operations](#6-operations)
   - 6.1 [ExecuteBuildSpec](#61-executebuildspec)
   - 6.2 [MassCompile](#62-masscompile)
   - 6.3 [RunVI](#63-runvi)
   - 6.4 [RunUnitTests](#64-rununittests)
   - 6.5 [RunVIAnalyzer](#65-runvianalyzer)
   - 6.6 [CloseLabVIEW](#66-closelabview)
   - 6.7 [CreateComparisonReport](#67-createcomparisonreport)
7. [Custom Operations](#7-custom-operations)
8. [CI/CD Integration](#8-cicd-integration)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Overview

The **NI LabVIEW Command Line Interface (LabVIEW CLI)** is an add-on for LabVIEW that exposes LabVIEW operations — such as building executables, running VIs, and executing unit tests — directly from the operating system command line.

It was first introduced in **LabVIEW 2014** and is included with LabVIEW Full and higher editions. LabVIEW CLI is installed in the version-independent `Shared` directory, making it available to all installed versions of LabVIEW on the machine.

### How It Works

LabVIEW CLI operates as a **client–server system**:

1. `LabVIEWCLI.exe` (the client) sends an operation request over TCP/IP to a running LabVIEW instance (the server).
2. LabVIEW executes the operation and returns the result.
3. The CLI process exits with a code indicating success or failure.

Because LabVIEW must be running (or is launched automatically), a **full LabVIEW installation** is required on the machine where the CLI is invoked. There is no headless/minimal mode without LabVIEW installed — except when using the official NI Docker container image.

### Key Use Cases

- **Automated builds** — compile LabVIEW EXEs, installers, shared libraries, and packed libraries from a CI/CD pipeline.
- **Unit testing** — run LabVIEW Unit Test Framework tests and export JUnit XML reports.
- **Static analysis** — run VI Analyzer checks and export reports.
- **Scripted VI execution** — invoke specific VIs with arguments and capture return values.
- **Mass recompilation** — recompile all VIs in a directory after a LabVIEW upgrade.
- **VI diffing** — generate comparison reports between two versions of a VI.

---

## 2. Installation & Prerequisites

### Default Install Location

```
# Windows (32-bit CLI, supports both 32-bit and 64-bit LabVIEW)
C:\Program Files (x86)\National Instruments\Shared\LabVIEW CLI\LabVIEWCLI.exe

# LabVIEW executable (version-specific, update year as needed)
C:\Program Files\National Instruments\LabVIEW 2023\LabVIEW.exe
```

### Prerequisites

| Requirement | Details |
|---|---|
| LabVIEW edition | Full or higher (Professional, Application Builder required for `ExecuteBuildSpec`) |
| VI Server enabled | Tools → Options → VI Server → TCP/IP checkbox must be ON |
| VI Server port | Default: **3363** (must match `-PortNumber` if changed) |
| .NET Framework | Required on Windows for the CLI client |

### Enabling VI Server (Required)

The CLI communicates with LabVIEW via VI Server over TCP/IP. Before using the CLI:

1. Open LabVIEW.
2. Go to **Tools → Options → VI Server**.
3. Check **TCP/IP** under Protocols.
4. Leave the port as **3363** (or note your custom port for use with `-PortNumber`).
5. Click **OK**.

On Linux containers (NI Docker image), `xvfb-run` is needed to provide a virtual display:

```bash
xvfb-run LabVIEWCLI -OperationName ExecuteBuildSpec ...
```

---

## 3. Global Syntax

All LabVIEW CLI commands follow this structure:

```
LabVIEWCLI -OperationName <name> [operation-specific args...]
           [-AdditionalOperationDirectory <path>]
           [-LabVIEWPath <path>]
           [-PortNumber <number>]
           [-LogFilePath <path>]
           [-LogToConsole (true|false)]
           [-Verbosity (Minimal|Default|Detailed|Diagnostic)]
           [-Help]
```

**Global flags must come after operation-specific arguments**, or they may be interpreted as operation arguments. The recommended pattern is:

```
LabVIEWCLI -OperationName <name> \
  -OperationFlag1 value1 \
  -OperationFlag2 value2 \
  -LogFilePath "C:\logs\build.log" \
  -Verbosity Detailed
```

---

## 4. Global Flags Reference

These flags apply to every operation and control how the CLI client connects to LabVIEW and handles logging.

---

### `-OperationName <name>`

**Required.** Specifies which operation to run.

```bash
LabVIEWCLI -OperationName ExecuteBuildSpec ...
```

---

### `-LabVIEWPath <path>`

Path to the LabVIEW **executable** (`LabVIEW.exe` on Windows).

- **Windows:** Optional. Defaults to the most recently started LabVIEW instance.
- **macOS / Linux:** **Required.**

```bash
# Windows — explicit version targeting
LabVIEWCLI -OperationName MassCompile \
  -LabVIEWPath "C:\Program Files\National Instruments\LabVIEW 2023\LabVIEW.exe" \
  -DirectoryToCompile "C:\MyProject"

# Linux (e.g., in NI Docker container)
LabVIEWCLI -OperationName ExecuteBuildSpec \
  -LabVIEWPath /usr/local/natinst/LabVIEW-2023/labviewprofull \
  -ProjectPath "/workspace/MyProject.lvproj"
```

> **Tip:** On machines with multiple LabVIEW versions, always specify `-LabVIEWPath` explicitly to avoid building with the wrong version.

---

### `-PortNumber <number>`

TCP port used to communicate with the LabVIEW VI Server.

- **Default:** `3363`
- Use a custom port when running multiple parallel builds on the same machine.

```bash
# Build on a non-default port (useful for parallel CI jobs)
LabVIEWCLI -OperationName ExecuteBuildSpec \
  -ProjectPath "C:\MyProject\MyProject.lvproj" \
  -BuildSpecName "Release Build" \
  -PortNumber 3364
```

---

### `-LogFilePath <path>`

Absolute path to a log file where CLI output is written.

- If not specified, the log is written to the system temporary directory.
- Combine with `-Verbosity Diagnostic` for maximum debug output.

```bash
LabVIEWCLI -OperationName ExecuteBuildSpec \
  -ProjectPath "C:\MyProject\MyProject.lvproj" \
  -BuildSpecName "Release Build" \
  -LogFilePath "C:\CI\logs\build-2026-04-28.log"
```

---

### `-LogToConsole (true|false)`

Controls whether log output is also printed to stdout/stderr.

- **Default:** `true`
- Set to `false` to suppress console output (e.g., when capturing only the exit code in a script).

```bash
LabVIEWCLI -OperationName CloseLabVIEW \
  -LogToConsole false
```

---

### `-Verbosity (Minimal|Default|Detailed|Diagnostic)`

Controls the detail level of log messages.

| Level | Output |
|---|---|
| `Minimal` | Errors only |
| `Default` | Standard operation progress messages |
| `Detailed` | Step-by-step execution details |
| `Diagnostic` | Full debug trace — use when troubleshooting failures |

```bash
# Diagnose a failing build
LabVIEWCLI -OperationName ExecuteBuildSpec \
  -ProjectPath "C:\MyProject\MyProject.lvproj" \
  -BuildSpecName "Release Build" \
  -LogFilePath "C:\logs\debug.log" \
  -Verbosity Diagnostic
```

---

### `-AdditionalOperationDirectory <path>`

Directory path where custom CLI operations (DLLs) are located. Used when extending LabVIEW CLI with your own operations.

```bash
LabVIEWCLI -OperationName MyCustomOperation \
  -AdditionalOperationDirectory "C:\MyCustomOps" \
  -SomeCustomFlag value
```

---

### `-Help`

Displays help text for the specified operation and exits.

```bash
# Get help for a specific operation
LabVIEWCLI -OperationName ExecuteBuildSpec -Help

# Get general CLI help
LabVIEWCLI -Help
```

---

## 5. Exit Codes

LabVIEW CLI exits with a numeric code. **Always check exit codes in CI/CD scripts** to detect failures.

| Code | Meaning |
|---|---|
| `0` | Success — operation completed without errors |
| Non-zero | Failure — operation did not complete successfully |

Specific non-zero values vary by operation and LabVIEW version. In CI/CD scripts, treat any non-zero exit as a pipeline failure:

```powershell
# PowerShell
& LabVIEWCLI.exe -OperationName ExecuteBuildSpec ...
if ($LASTEXITCODE -ne 0) {
    Write-Error "LabVIEW CLI failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}
```

```bash
# Bash (Linux / Docker)
LabVIEWCLI -OperationName ExecuteBuildSpec ...
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
  echo "LabVIEW CLI failed: exit code $EXIT_CODE"
  exit $EXIT_CODE
fi
```

---

## 6. Operations

LabVIEW CLI 2025 Q3 includes **7 predefined operations**:

| # | Operation | Purpose |
|---|---|---|
| 1 | `ExecuteBuildSpec` | Build EXE, installer, shared library, or packed library |
| 2 | `MassCompile` | Recompile all VIs in a directory |
| 3 | `RunVI` | Execute a VI from the command line |
| 4 | `RunUnitTests` | Run Unit Test Framework tests, export JUnit XML |
| 5 | `RunVIAnalyzer` | Run VI Analyzer static analysis, export report |
| 6 | `CloseLabVIEW` | Gracefully close the LabVIEW instance |
| 7 | `CreateComparisonReport` | Diff two VIs and generate a comparison report |

---

### 6.1 ExecuteBuildSpec

**Introduced:** LabVIEW CLI 1.0
**Purpose:** Builds one or all build specifications in a LabVIEW project. Supports EXE, installer, shared library (.dll), and packed library (.lvlibp) build types.

#### Synopsis

```
LabVIEWCLI -OperationName ExecuteBuildSpec
           -ProjectPath <path>
           [-TargetName <target>]
           [-BuildSpecName <name>]
```

#### Parameters

| Parameter | Required | Description |
|---|---|---|
| `-ProjectPath <path>` | **Yes** | Absolute path to the `.lvproj` file containing the build specification. |
| `-TargetName <target>` | No | The project target that owns the build spec. Defaults to `"My Computer"` when not specified. Use for RT or FPGA targets. |
| `-BuildSpecName <name>` | No | Name of the specific build spec to run. When omitted, **all build specs** under the target are built. |

#### Behaviour Notes

- The build spec must already be configured and saved in the `.lvproj` file. The CLI cannot create or modify build specs.
- The output path (where the EXE is placed) is defined inside the build spec in the project, not by the CLI.
- If `-BuildSpecName` is omitted, all build specs under the target run sequentially. A failure in one does not necessarily abort others — check the log.
- On the first run, LabVIEW may take time to load the project and resolve dependencies.

#### Examples

**Build a single EXE:**
```bash
LabVIEWCLI -OperationName ExecuteBuildSpec \
  -ProjectPath "C:\MyProject\MyProject.lvproj" \
  -BuildSpecName "My Application"
```

**Build all specs in the project:**
```bash
LabVIEWCLI -OperationName ExecuteBuildSpec \
  -ProjectPath "C:\MyProject\MyProject.lvproj"
```

**Target a Real-Time (RT) target:**
```bash
LabVIEWCLI -OperationName ExecuteBuildSpec \
  -ProjectPath "C:\MyProject\MyProject.lvproj" \
  -TargetName "cRIO-9045" \
  -BuildSpecName "RT Application"
```

**With logging and explicit LabVIEW path:**
```bash
LabVIEWCLI -OperationName ExecuteBuildSpec \
  -ProjectPath "C:\MyProject\MyProject.lvproj" \
  -BuildSpecName "Release Build" \
  -LabVIEWPath "C:\Program Files\National Instruments\LabVIEW 2023\LabVIEW.exe" \
  -LogFilePath "C:\logs\build.log" \
  -Verbosity Detailed
```

**Linux / Docker container:**
```bash
xvfb-run LabVIEWCLI \
  -OperationName ExecuteBuildSpec \
  -ProjectPath "$GITHUB_WORKSPACE/MyProject.lvproj" \
  -BuildSpecName "Release Build" \
  -LogFilePath "$GITHUB_WORKSPACE/logs/build.log"
```

**PowerShell CI script with exit code check:**
```powershell
$cli = "C:\Program Files (x86)\National Instruments\Shared\LabVIEW CLI\LabVIEWCLI.exe"

& $cli -OperationName ExecuteBuildSpec `
       -ProjectPath "$env:WORKSPACE\MyProject.lvproj" `
       -BuildSpecName "Release Build" `
       -LogFilePath "$env:WORKSPACE\logs\build.log"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed. Check logs at $env:WORKSPACE\logs\build.log"
    exit $LASTEXITCODE
}

Write-Host "Build succeeded."
```

#### Finding the EXE Output Path

The CLI does not return the output path. The EXE is placed wherever the build spec's **Destinations** tab specifies. The default is:

```
<ProjectFolder>\builds\<BuildSpecName>\<AppName>.exe
```

To locate it programmatically after building:

```powershell
$exe = Get-ChildItem -Path "$env:WORKSPACE\builds" -Filter "*.exe" -Recurse | Select-Object -First 1
Write-Host "EXE at: $($exe.FullName)"
```

---

### 6.2 MassCompile

**Introduced:** LabVIEW CLI 1.0
**Purpose:** Recompiles all VIs in a specified directory and its subdirectories. Used to migrate VIs to a new LabVIEW version, repair broken VIs, or verify a codebase compiles cleanly.

#### Synopsis

```
LabVIEWCLI -OperationName MassCompile
           -DirectoryToCompile <path>
           -MassCompileLogFile <path>
           [-AppendToMassCompileLog (true|false)]
           [-NumOfVIsToCache <n>]
           [-ReloadLVSBs (true|false)]
```

#### Parameters

| Parameter | Required | Default | Description |
|---|---|---|---|
| `-DirectoryToCompile <path>` | **Yes** | — | Absolute path to the directory to compile. All subdirectories are included recursively. |
| `-MassCompileLogFile <path>` | **Yes** | — | Absolute path to the output log file. Records compilation results per VI. |
| `-AppendToMassCompileLog (true\|false)` | No | `false` | `true`: append to existing log. `false`: overwrite the log file. |
| `-NumOfVIsToCache <n>` | No | `0` | Number of VIs to keep in memory during compilation. Increasing this speeds up compile but risks cross-linking if VIs share names across subdirectories. |
| `-ReloadLVSBs (true\|false)` | No | `false` | `true`: LabVIEW ignores cached Code Interface Nodes (CINs) and searches for them fresh. |

#### Behaviour Notes

- MassCompile opens each VI, compiles it against the current LabVIEW version, and saves it. This modifies the `.vi` files on disk.
- **Run before `ExecuteBuildSpec`** in CI pipelines to catch compilation errors early.
- The log file lists each VI with its compile status. Parse it to detect VIs that failed compilation.
- VIs that cannot be found, are password-protected, or have broken dependencies will be logged as errors.
- Using `NumOfVIsToCache` greater than 0 can significantly speed up large codebases, but use with caution if you have VIs with the same filename in different subdirectories (cross-linking risk).

#### Examples

**Basic mass compile:**
```bash
LabVIEWCLI -OperationName MassCompile \
  -DirectoryToCompile "C:\MyProject" \
  -MassCompileLogFile "C:\logs\masscompile.log"
```

**Append to an existing log file:**
```bash
LabVIEWCLI -OperationName MassCompile \
  -DirectoryToCompile "C:\MyProject" \
  -MassCompileLogFile "C:\logs\masscompile.log" \
  -AppendToMassCompileLog true
```

**Speed up with VI caching (safe when no duplicate VI names):**
```bash
LabVIEWCLI -OperationName MassCompile \
  -DirectoryToCompile "C:\MyProject" \
  -MassCompileLogFile "C:\logs\masscompile.log" \
  -NumOfVIsToCache 50
```

**Reload Code Interface Nodes (CINs) from scratch:**
```bash
LabVIEWCLI -OperationName MassCompile \
  -DirectoryToCompile "C:\MyProject" \
  -MassCompileLogFile "C:\logs\masscompile.log" \
  -ReloadLVSBs true
```

**Full example with all options:**
```bash
LabVIEWCLI -OperationName MassCompile \
  -DirectoryToCompile "C:\MyProject" \
  -MassCompileLogFile "C:\logs\masscompile.log" \
  -AppendToMassCompileLog false \
  -NumOfVIsToCache 20 \
  -ReloadLVSBs false \
  -LabVIEWPath "C:\Program Files\National Instruments\LabVIEW 2023\LabVIEW.exe" \
  -Verbosity Detailed
```

**Linux / Docker:**
```bash
xvfb-run LabVIEWCLI \
  -OperationName MassCompile \
  -DirectoryToCompile "$GITHUB_WORKSPACE" \
  -MassCompileLogFile "$GITHUB_WORKSPACE/logs/masscompile.log"
```

**Post-compile: check log for errors (PowerShell):**
```powershell
$log = Get-Content "C:\logs\masscompile.log"
$errors = $log | Where-Object { $_ -match "error" -or $_ -match "failed" }
if ($errors) {
    Write-Warning "MassCompile reported issues:"
    $errors | ForEach-Object { Write-Warning $_ }
}
```

---

### 6.3 RunVI

**Introduced:** LabVIEW CLI 1.0
**Purpose:** Executes a VI from the command line, passing arguments and capturing the return code and output message. Useful for running custom scripts, setup tasks, or any arbitrary LabVIEW logic as part of a pipeline.

#### Connector Pane Requirement

VIs executed by `RunVI` **must** have a specific connector pane — the **4x2x2x4 pattern** — with exactly these terminals wired:

| Terminal Position | Data Type | Role |
|---|---|---|
| Terminal 11 (top-left) | String Array | Command line arguments (input) |
| Terminal 3 (top-right) | I32 | Return code (output) |
| Terminal 2 (bottom-right) | String | Output / error message (output) |

If the VI does not have this connector pane wired correctly, `RunVI` will fail.

#### Synopsis

```
LabVIEWCLI -OperationName RunVI
           -VIPath <path> [<arg>...]
```

#### Parameters

| Parameter | Required | Description |
|---|---|---|
| `-VIPath <path>` | **Yes** | Absolute path to the VI file. Additional space-separated arguments after the path are passed to the VI as the string array on terminal 11. |

#### Behaviour Notes

- The VI receives all arguments as a **1D string array**. Parse them inside the VI as needed.
- The **return code** from terminal 3 is used as the CLI exit code. Return `0` for success, non-zero for failure.
- The **output string** from terminal 2 is printed to the console and log file.
- The VI must be saved and accessible at the specified path. It does not need to be part of a project.

#### Examples

**Run a VI with no arguments:**
```bash
LabVIEWCLI -OperationName RunVI \
  -VIPath "C:\MyProject\Scripts\Setup.vi"
```

**Run a VI and pass arguments:**
```bash
LabVIEWCLI -OperationName RunVI \
  -VIPath "C:\MyProject\Scripts\Deploy.vi" \
  arg1 arg2 "argument with spaces"
```

**Run a VI and capture output in CI (PowerShell):**
```powershell
$output = & LabVIEWCLI.exe -OperationName RunVI `
    -VIPath "C:\MyProject\Scripts\ValidateConfig.vi" `
    "config.ini" `
    -LogToConsole true
Write-Host "VI output: $output"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

**Run a VI on Linux with arguments:**
```bash
xvfb-run LabVIEWCLI \
  -OperationName RunVI \
  -VIPath "/workspace/Scripts/GenerateReport.vi" \
  "--output=/workspace/reports" \
  "--format=html"
```

#### Sample VI Connector Pane Wiring

Inside your VI, wire the terminals like this:

```
[In]  Terminal 11 → String Array control named "Arguments"
[Out] Terminal 3  → I32 indicator named "Return Code"
[Out] Terminal 2  → String indicator named "Output Message"
```

Your VI block diagram reads from `Arguments[0]`, `Arguments[1]`, etc., does its work, then writes a code to `Return Code` and a message to `Output Message`.

---

### 6.4 RunUnitTests

**Introduced:** LabVIEW CLI 2.0
**Purpose:** Runs automated unit tests defined using the **LabVIEW Unit Test Framework (UTF) Toolkit** and saves the results to a **JUnit XML** report. The JUnit format is supported by all major CI platforms (GitHub Actions, Jenkins, GitLab CI).

> **Prerequisite:** The LabVIEW Unit Test Framework Toolkit must be installed.

#### Synopsis

```
LabVIEWCLI -OperationName RunUnitTests
           -ProjectPath <path>
           -JUnitReportPath <path>
```

#### Parameters

| Parameter | Required | Description |
|---|---|---|
| `-ProjectPath <path>` | **Yes** | Absolute path to the `.lvproj` file that contains unit test VIs configured for the Unit Test Framework Toolkit. |
| `-JUnitReportPath <path>` | **Yes** | Absolute path to the output JUnit XML file (`.xml`). The file is created or overwritten. |

#### Behaviour Notes

- All tests in the project tagged for the UTF Toolkit are discovered and run automatically.
- The JUnit XML file can be consumed by CI systems to display test results, track failures over time, and fail the pipeline on test failures.
- The CLI exit code reflects the overall test outcome: `0` = all tests passed, non-zero = one or more tests failed.
- Test output and failure details are available both in the JUnit XML and the CLI log file.

#### Examples

**Run all unit tests in a project:**
```bash
LabVIEWCLI -OperationName RunUnitTests \
  -ProjectPath "C:\MyProject\MyProject.lvproj" \
  -JUnitReportPath "C:\reports\test-results.xml"
```

**With logging:**
```bash
LabVIEWCLI -OperationName RunUnitTests \
  -ProjectPath "C:\MyProject\MyProject.lvproj" \
  -JUnitReportPath "C:\reports\test-results.xml" \
  -LogFilePath "C:\logs\unit-tests.log" \
  -Verbosity Detailed
```

**Linux / Docker:**
```bash
xvfb-run LabVIEWCLI \
  -OperationName RunUnitTests \
  -ProjectPath "$GITHUB_WORKSPACE/MyProject.lvproj" \
  -JUnitReportPath "$GITHUB_WORKSPACE/reports/test-results.xml"
```

**GitHub Actions — publish test results:**
```yaml
- name: Run Unit Tests
  run: |
    xvfb-run LabVIEWCLI \
      -OperationName RunUnitTests \
      -ProjectPath "$GITHUB_WORKSPACE/MyProject.lvproj" \
      -JUnitReportPath "$GITHUB_WORKSPACE/reports/test-results.xml"

- name: Publish Test Results
  uses: mikepenz/action-junit-report@v4
  if: always()
  with:
    report_paths: "${{ github.workspace }}/reports/test-results.xml"
```

**Jenkins — publish test results:**
```groovy
stage('Test') {
  steps {
    bat """
      LabVIEWCLI -OperationName RunUnitTests ^
        -ProjectPath "%WORKSPACE%\\MyProject.lvproj" ^
        -JUnitReportPath "%WORKSPACE%\\reports\\test-results.xml"
    """
  }
  post {
    always {
      junit 'reports/test-results.xml'
    }
  }
}
```

---

### 6.5 RunVIAnalyzer

**Introduced:** LabVIEW CLI 2.0
**Purpose:** Runs static analysis on LabVIEW VIs using the **VI Analyzer Toolkit**, checking for code quality issues, style violations, and best practice deviations. Results are saved to a report file.

> **Prerequisite:** The LabVIEW VI Analyzer Toolkit must be installed.

#### Synopsis

```
LabVIEWCLI -OperationName RunVIAnalyzer
           -ConfigPath <path>
           -ReportPath <path>
           [-ConfigPassword <password>]
           [-ReportSaveType (ASCII|HTML|RSL)]
```

#### Parameters

| Parameter | Required | Default | Description |
|---|---|---|---|
| `-ConfigPath <path>` | **Yes** | — | Absolute path to a VI Analyzer Configuration File (`.viancfg`). Alternatively, pass a path to a VI, folder, or LLB to analyze using all VI Analyzer tests with default settings. |
| `-ReportPath <path>` | **Yes** | — | Absolute path to the output report file. The file type is set by `-ReportSaveType`. |
| `-ConfigPassword <password>` | No | *(empty)* | Password for a password-protected configuration file. |
| `-ReportSaveType (ASCII\|HTML\|RSL)` | No | `ASCII` | Format of the report file. `ASCII` = plain text, `HTML` = browser-viewable, `RSL` = LabVIEW-specific report format. |

#### Behaviour Notes

- VI Analyzer checks a wide range of code quality rules: naming conventions, front panel layout, block diagram complexity, error handling, and more.
- Using a configuration file (`.viancfg`) lets you select exactly which tests to run and configure their parameters. This is the recommended approach for CI use.
- When a folder or VI is passed directly to `-ConfigPath`, all available VI Analyzer tests run with default settings — useful for quick ad-hoc checks.
- The exit code reflects whether any violations were found (non-zero = violations detected).

#### Examples

**Analyze using a configuration file, output as HTML:**
```bash
LabVIEWCLI -OperationName RunVIAnalyzer \
  -ConfigPath "C:\MyProject\Analysis\vi-analyzer-config.viancfg" \
  -ReportPath "C:\reports\vi-analysis.html" \
  -ReportSaveType HTML
```

**Analyze a folder directly (all tests, default settings):**
```bash
LabVIEWCLI -OperationName RunVIAnalyzer \
  -ConfigPath "C:\MyProject\SubVIs" \
  -ReportPath "C:\reports\vi-analysis.txt" \
  -ReportSaveType ASCII
```

**Use a password-protected config:**
```bash
LabVIEWCLI -OperationName RunVIAnalyzer \
  -ConfigPath "C:\Configs\secure-vi-config.viancfg" \
  -ReportPath "C:\reports\analysis.html" \
  -ConfigPassword "mypassword" \
  -ReportSaveType HTML
```

**In a CI pipeline (fail on violations):**
```bash
xvfb-run LabVIEWCLI \
  -OperationName RunVIAnalyzer \
  -ConfigPath "$GITHUB_WORKSPACE/configs/vi-analyzer.viancfg" \
  -ReportPath "$GITHUB_WORKSPACE/reports/vi-analysis.html" \
  -ReportSaveType HTML

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
  echo "::error::VI Analyzer found violations. See report at reports/vi-analysis.html"
  exit $EXIT_CODE
fi
```

---

### 6.6 CloseLabVIEW

**Introduced:** LabVIEW CLI 1.0
**Purpose:** Gracefully closes the currently connected LabVIEW instance **without any user prompts or save dialogs**. Essential in CI/CD pipelines to prevent LabVIEW from remaining as a zombie process after builds.

#### Synopsis

```
LabVIEWCLI -OperationName CloseLabVIEW
```

#### Parameters

This operation has **no operation-specific parameters**. Only global flags apply.

#### Behaviour Notes

- Closes LabVIEW immediately without prompting to save unsaved VIs.
- If multiple LabVIEW instances are running, uses `-PortNumber` to target a specific instance.
- Should **always be called at the end of a CI pipeline step** — even on failure — to prevent orphaned LabVIEW processes from accumulating on the build runner.
- If LabVIEW is not running when this is called, the operation fails with a non-zero exit code. This is usually harmless; use `if: always()` in GitHub Actions or equivalent.

#### Examples

**Basic close:**
```bash
LabVIEWCLI -OperationName CloseLabVIEW
```

**Close a specific LabVIEW instance on a custom port:**
```bash
LabVIEWCLI -OperationName CloseLabVIEW -PortNumber 3364
```

**GitHub Actions — always close even on failure:**
```yaml
- name: Close LabVIEW
  if: always()   # This is critical — runs even if previous steps failed
  shell: bash
  run: |
    xvfb-run LabVIEWCLI -OperationName CloseLabVIEW || true
    # '|| true' prevents this step from failing the pipeline if LabVIEW wasn't running
```

**Jenkins — always close (declarative pipeline):**
```groovy
post {
  always {
    bat 'LabVIEWCLI -OperationName CloseLabVIEW'
  }
}
```

**PowerShell — close and suppress non-zero exit if LabVIEW wasn't running:**
```powershell
& LabVIEWCLI.exe -OperationName CloseLabVIEW
# Don't check exit code here — it may be non-zero if LV wasn't running, which is fine
Write-Host "LabVIEW close attempted."
```

---

### 6.7 CreateComparisonReport

**Introduced:** LabVIEW CLI 2025 Q3 (newest operation)
**Purpose:** Runs LVDiff on two VI files and generates a visual or text-based comparison report showing differences in front panel, block diagram, and VI attributes. Useful for code review automation and change tracking.

#### Synopsis

```
LabVIEWCLI -OperationName CreateComparisonReport
           -vi1 <path>
           -vi2 <path>
           -reportPath <path>
           [-reportType (HTML|HTMLSingleFile|MicrosoftWord|PlainText|XML)]
           [-o]
           [-c]
           [-nofp]
           [-nofppos]
           [-nobd]
           [-nobdcosm]
           [-noattr]
           [-d]
```

#### Parameters

| Parameter | Required | Default | Description |
|---|---|---|---|
| `-vi1 <path>` | **Yes** | — | Absolute path to the **first** (base) VI. |
| `-vi2 <path>` | **Yes** | — | Absolute path to the **second** (modified) VI. |
| `-reportPath <path>` | **Yes** | — | Absolute path to the output report file. |
| `-reportType` | No | `HTMLSingleFile` | Report format. Options: `HTML`, `HTMLSingleFile`, `MicrosoftWord`, `PlainText`, `XML`. |
| `-o` | No | — | **Overwrite** existing report file if it already exists. |
| `-c` | No | — | **Create** the report directory if it does not exist. |
| `-nofp` | No | — | **Exclude** front panel differences from the report. |
| `-nofppos` | No | — | **Exclude** front panel position/layout differences. |
| `-nobd` | No | — | **Exclude** block diagram differences. |
| `-nobdcosm` | No | — | **Exclude** cosmetic block diagram differences (wire routing, comment positions, etc.). |
| `-noattr` | No | — | **Exclude** VI attribute differences (description, revision history, etc.). |
| `-d` | No | — | **Exclude** dependency differences. |

#### Behaviour Notes

- The report compares `vi1` (base) against `vi2` (modified) — the "direction" matters in how changes are described.
- `HTMLSingleFile` produces a self-contained HTML file (all assets embedded) — the most portable option for sharing.
- `MicrosoftWord` produces a `.docx` file — requires Microsoft Word or LibreOffice to view.
- Use the exclusion flags (`-nofp`, `-nobd`, etc.) to focus the report on what matters for your review.
- The `-c` flag is strongly recommended in CI pipelines where the output directory may not exist yet.

#### Examples

**Generate a self-contained HTML diff report:**
```bash
LabVIEWCLI -OperationName CreateComparisonReport \
  -vi1 "C:\MyProject\v1.0\MyVI.vi" \
  -vi2 "C:\MyProject\v1.1\MyVI.vi" \
  -reportPath "C:\reports\MyVI-diff.html" \
  -reportType HTMLSingleFile \
  -o -c
```

**Block diagram only — skip front panel and attributes:**
```bash
LabVIEWCLI -OperationName CreateComparisonReport \
  -vi1 "C:\Baseline\Control.vi" \
  -vi2 "C:\Modified\Control.vi" \
  -reportPath "C:\reports\Control-diff.html" \
  -nofp \
  -noattr \
  -o -c
```

**Plain text diff (for machine parsing in CI):**
```bash
LabVIEWCLI -OperationName CreateComparisonReport \
  -vi1 "C:\old\Signal.vi" \
  -vi2 "C:\new\Signal.vi" \
  -reportPath "C:\reports\Signal-diff.txt" \
  -reportType PlainText \
  -o -c
```

**Export as Word document:**
```bash
LabVIEWCLI -OperationName CreateComparisonReport \
  -vi1 "C:\Released\Algorithm.vi" \
  -vi2 "C:\Updated\Algorithm.vi" \
  -reportPath "C:\reports\Algorithm-diff.docx" \
  -reportType MicrosoftWord \
  -o -c
```

**In a GitHub Actions PR workflow:**
```yaml
- name: Generate VI Diff Report
  run: |
    xvfb-run LabVIEWCLI \
      -OperationName CreateComparisonReport \
      -vi1 "${{ github.workspace }}/baseline/MyVI.vi" \
      -vi2 "${{ github.workspace }}/MyVI.vi" \
      -reportPath "${{ github.workspace }}/reports/vi-diff.html" \
      -reportType HTMLSingleFile \
      -o -c

- name: Upload Diff Report
  uses: actions/upload-artifact@v4
  with:
    name: vi-diff-report
    path: ${{ github.workspace }}/reports/vi-diff.html
```

---

## 7. Custom Operations

LabVIEW CLI can be extended with your own operations by creating a custom operation class in LabVIEW.

### Requirements

- Inherit from the `CoreOperation` class (included with LabVIEW CLI).
- Override the `GetHelp` and `RunOperation` methods.
- Compile to a DLL and place it in a directory accessible via `-AdditionalOperationDirectory`.

### Invocation

```bash
LabVIEWCLI -OperationName MyCustomOperation \
  -AdditionalOperationDirectory "C:\MyCustomOps" \
  -MyCustomFlag value
```

### Resources

- [Creating Custom Command Line Operations](https://www.ni.com/docs/en-US/bundle/labview/page/creating-custom-command-line-operations.html) — NI official documentation.
- NI Community example: `ExecuteBuildSpecv2` — adds support for version injection, project save after build, and NIPKG installation.

---

## 8. CI/CD Integration

### Recommended Pipeline Order

```
1. Checkout source code
2. MassCompile          ← catch broken VIs early
3. RunVIAnalyzer        ← static analysis (optional but recommended)
4. RunUnitTests         ← automated tests
5. ExecuteBuildSpec     ← build the EXE / installer
6. CloseLabVIEW         ← always runs, prevents zombie processes
7. Publish artifact     ← upload EXE to GitHub Release, Artifactory, etc.
```

### Full GitHub Actions Example (Linux Container)

```yaml
name: LabVIEW CI

on:
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  build:
    runs-on: self-hosted
    container:
      image: nationalinstruments/labview:2025q3-linux
      volumes:
        - /etc/natinst/license:/etc/natinst/license:ro
      options: --shm-size=2g

    steps:
      - uses: actions/checkout@v4

      - name: MassCompile
        run: |
          mkdir -p "$GITHUB_WORKSPACE/logs"
          xvfb-run LabVIEWCLI \
            -OperationName MassCompile \
            -DirectoryToCompile "$GITHUB_WORKSPACE" \
            -MassCompileLogFile "$GITHUB_WORKSPACE/logs/masscompile.log"
          [ $? -eq 0 ] || exit $?

      - name: Run Unit Tests
        run: |
          xvfb-run LabVIEWCLI \
            -OperationName RunUnitTests \
            -ProjectPath "$GITHUB_WORKSPACE/MyProject.lvproj" \
            -JUnitReportPath "$GITHUB_WORKSPACE/reports/tests.xml"
          [ $? -eq 0 ] || exit $?

      - name: Build EXE
        run: |
          xvfb-run LabVIEWCLI \
            -OperationName ExecuteBuildSpec \
            -ProjectPath "$GITHUB_WORKSPACE/MyProject.lvproj" \
            -BuildSpecName "Release Build" \
            -LogFilePath "$GITHUB_WORKSPACE/logs/build.log"
          [ $? -eq 0 ] || exit $?

      - name: Close LabVIEW
        if: always()
        run: xvfb-run LabVIEWCLI -OperationName CloseLabVIEW || true

      - name: Upload logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: build-logs
          path: ${{ github.workspace }}/logs/
```

### Running Parallel Builds (Multiple LabVIEW Versions)

Use `-PortNumber` to run two LabVIEW instances simultaneously:

```powershell
# Instance 1 — LabVIEW 2022 on port 3363
Start-Job {
    & "C:\...\LabVIEW 2022\LabVIEW.exe"
    & LabVIEWCLI.exe -OperationName ExecuteBuildSpec `
        -ProjectPath "C:\Project\App.lvproj" -BuildSpecName "Build" -PortNumber 3363
}

# Instance 2 — LabVIEW 2023 on port 3364
Start-Job {
    & "C:\...\LabVIEW 2023\LabVIEW.exe"
    & LabVIEWCLI.exe -OperationName ExecuteBuildSpec `
        -ProjectPath "C:\Project\App.lvproj" -BuildSpecName "Build" -PortNumber 3364
}
```

---

## 9. Troubleshooting

### "Cannot connect to LabVIEW"

**Cause:** VI Server not enabled or wrong port.

**Fix:**
1. Open LabVIEW → Tools → Options → VI Server.
2. Check TCP/IP is enabled.
3. Confirm port matches your `-PortNumber` (default: 3363).
4. Check Windows Firewall is not blocking port 3363.

---

### Build fails but no clear error message

**Fix:** Add `-Verbosity Diagnostic -LogFilePath "C:\logs\debug.log"` and inspect the log.

```bash
LabVIEWCLI -OperationName ExecuteBuildSpec \
  -ProjectPath "C:\MyProject\MyProject.lvproj" \
  -BuildSpecName "Release Build" \
  -LogFilePath "C:\logs\debug.log" \
  -Verbosity Diagnostic
```

---

### `RunVI` exits with non-zero but VI logic is correct

**Cause:** VI connector pane is not wired correctly.

**Fix:** Ensure terminal 3 (return code, I32) is wired to a control, and your VI writes `0` to it on success. An unwired terminal returns garbage or zero depending on LabVIEW version.

---

### MassCompile is very slow

**Fix:** Increase `-NumOfVIsToCache` incrementally (try 10, then 50). Only safe when no two VIs share the same filename in different subdirectories.

---

### LabVIEW process remains after pipeline

**Cause:** `CloseLabVIEW` step was skipped (pipeline failed before reaching it).

**Fix:** Always run `CloseLabVIEW` with `if: always()` in GitHub Actions, or in the `post { always { } }` block in Jenkins.

---

### On Linux: "cannot connect to X server"

**Cause:** LabVIEW requires a display even in headless environments.

**Fix:** Wrap every LabVIEW CLI call with `xvfb-run`:

```bash
xvfb-run LabVIEWCLI -OperationName ExecuteBuildSpec ...
```

---

*Reference compiled from [LabVIEW Wiki](https://labviewwiki.org/wiki/NI_LabVIEW_Command_Line_Interface) and NI official documentation. Current as of LabVIEW CLI 2025 Q3.*
