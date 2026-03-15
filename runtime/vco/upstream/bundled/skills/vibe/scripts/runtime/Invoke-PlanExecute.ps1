param(
    [Parameter(Mandatory)] [string]$Task,
    [string]$Mode = 'interactive_governed',
    [string]$RunId = '',
    [string]$RequirementDocPath = '',
    [string]$ExecutionPlanPath = '',
    [string]$ArtifactRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'VibeRuntime.Common.ps1')

function Expand-VibeExecutionTemplate {
    param(
        [AllowEmptyString()] [string]$Text,
        [hashtable]$Tokens
    )

    $value = if ($null -eq $Text) { '' } else { [string]$Text }
    foreach ($key in @($Tokens.Keys)) {
        $value = $value.Replace($key, [string]$Tokens[$key])
    }
    return $value
}

function Invoke-VibeCapturedProcess {
    param(
        [Parameter(Mandatory)] [string]$Command,
        [string[]]$Arguments = @(),
        [Parameter(Mandatory)] [string]$WorkingDirectory,
        [Parameter(Mandatory)] [int]$TimeoutSeconds,
        [Parameter(Mandatory)] [string]$StdOutPath,
        [Parameter(Mandatory)] [string]$StdErrPath
    )

    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $Command
    $startInfo.WorkingDirectory = $WorkingDirectory
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.CreateNoWindow = $true

    $quotedArguments = foreach ($argument in @($Arguments)) {
        $text = [string]$argument
        if ($text -match '[\s"]') {
            '"' + ($text -replace '"', '\"') + '"'
        } else {
            $text
        }
    }
    $startInfo.Arguments = [string]::Join(' ', @($quotedArguments))

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $startInfo

    try {
        if (-not $process.Start()) {
            throw "Failed to start process: $Command"
        }

        $stdoutTask = $process.StandardOutput.ReadToEndAsync()
        $stderrTask = $process.StandardError.ReadToEndAsync()

        $timedOut = -not $process.WaitForExit($TimeoutSeconds * 1000)
        if ($timedOut) {
            try {
                $process.Kill($true)
            } catch {
            }
            $process.WaitForExit()
        }

        $stdoutText = $stdoutTask.GetAwaiter().GetResult()
        $stderrText = $stderrTask.GetAwaiter().GetResult()
        Write-VgoUtf8NoBomText -Path $StdOutPath -Content $stdoutText
        Write-VgoUtf8NoBomText -Path $StdErrPath -Content $stderrText

        return [pscustomobject]@{
            exit_code = if ($timedOut) { -1 } else { [int]$process.ExitCode }
            timed_out = [bool]$timedOut
            stdout_path = $StdOutPath
            stderr_path = $StdErrPath
            stdout_preview = (($stdoutText -split "`r?`n" | Where-Object { $_ -ne '' }) | Select-Object -First 5)
            stderr_preview = (($stderrText -split "`r?`n" | Where-Object { $_ -ne '' }) | Select-Object -First 5)
        }
    } finally {
        $process.Dispose()
    }
}

function Invoke-VibeExecutionUnit {
    param(
        [Parameter(Mandatory)] [object]$Unit,
        [Parameter(Mandatory)] [string]$RepoRoot,
        [Parameter(Mandatory)] [string]$SessionRoot,
        [Parameter(Mandatory)] [hashtable]$Tokens,
        [Parameter(Mandatory)] [int]$DefaultTimeoutSeconds
    )

    $logsRoot = Join-Path $SessionRoot 'execution-logs'
    $resultsRoot = Join-Path $SessionRoot 'execution-results'
    New-Item -ItemType Directory -Path $logsRoot -Force | Out-Null
    New-Item -ItemType Directory -Path $resultsRoot -Force | Out-Null

    $unitId = [string]$Unit.unit_id
    $kind = [string]$Unit.kind
    $timeoutSeconds = if ($Unit.PSObject.Properties.Name -contains 'timeout_seconds' -and $null -ne $Unit.timeout_seconds) {
        [int]$Unit.timeout_seconds
    } else {
        [int]$DefaultTimeoutSeconds
    }
    $expectedExitCode = if ($Unit.PSObject.Properties.Name -contains 'expected_exit_code' -and $null -ne $Unit.expected_exit_code) {
        [int]$Unit.expected_exit_code
    } else {
        0
    }
    $cwd = Expand-VibeExecutionTemplate -Text ([string]$Unit.cwd) -Tokens $Tokens
    if ([string]::IsNullOrWhiteSpace($cwd)) {
        $cwd = $RepoRoot
    }
    if (-not [System.IO.Path]::IsPathRooted($cwd)) {
        $cwd = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $cwd))
    }

    $stdoutPath = Join-Path $logsRoot ("{0}.stdout.log" -f $unitId)
    $stderrPath = Join-Path $logsRoot ("{0}.stderr.log" -f $unitId)
    $startedAt = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')

    $command = ''
    $arguments = @()
    $display = ''

    switch ($kind) {
        'powershell_file' {
            $scriptPathRaw = Expand-VibeExecutionTemplate -Text ([string]$Unit.script_path) -Tokens $Tokens
            $scriptPath = if ([System.IO.Path]::IsPathRooted($scriptPathRaw)) {
                [System.IO.Path]::GetFullPath($scriptPathRaw)
            } else {
                [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $scriptPathRaw))
            }

            $args = @()
            foreach ($arg in @($Unit.arguments)) {
                $args += (Expand-VibeExecutionTemplate -Text ([string]$arg) -Tokens $Tokens)
            }

            $invocation = Get-VgoPowerShellFileInvocation -ScriptPath $scriptPath -ArgumentList $args -NoProfile
            $command = [string]$invocation.host_path
            $arguments = @($invocation.arguments)
            $display = @($command) + @($arguments) -join ' '
        }
        'python_command' {
            $commandSpec = Expand-VibeExecutionTemplate -Text ([string]$Unit.command) -Tokens $Tokens
            $pythonInvocation = Resolve-VgoPythonCommandSpec -Command $commandSpec
            $command = [string]$pythonInvocation.host_path
            $arguments = @($pythonInvocation.prefix_arguments)
            foreach ($arg in @($Unit.arguments)) {
                $arguments += (Expand-VibeExecutionTemplate -Text ([string]$arg) -Tokens $Tokens)
            }
            $display = @($command) + @($arguments) -join ' '
        }
        'shell_command' {
            $command = Expand-VibeExecutionTemplate -Text ([string]$Unit.command) -Tokens $Tokens
            foreach ($arg in @($Unit.arguments)) {
                $arguments += (Expand-VibeExecutionTemplate -Text ([string]$arg) -Tokens $Tokens)
            }
            $display = @($command) + @($arguments) -join ' '
        }
        default {
            throw "Unsupported benchmark execution unit kind: $kind"
        }
    }

    $processResult = Invoke-VibeCapturedProcess -Command $command -Arguments $arguments -WorkingDirectory $cwd -TimeoutSeconds $timeoutSeconds -StdOutPath $stdoutPath -StdErrPath $stderrPath

    $resolvedArtifacts = @()
    foreach ($artifact in @($Unit.expected_artifacts)) {
        $expanded = Expand-VibeExecutionTemplate -Text ([string]$artifact) -Tokens $Tokens
        $artifactPath = if ([System.IO.Path]::IsPathRooted($expanded)) {
            [System.IO.Path]::GetFullPath($expanded)
        } else {
            [System.IO.Path]::GetFullPath((Join-Path $cwd $expanded))
        }
        $resolvedArtifacts += [pscustomobject]@{
            path = $artifactPath
            exists = [bool](Test-Path -LiteralPath $artifactPath)
        }
    }

    $finishedAt = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    $verificationPassed = (-not $processResult.timed_out) -and ([int]$processResult.exit_code -eq $expectedExitCode) -and (@($resolvedArtifacts | Where-Object { -not $_.exists }).Count -eq 0)

    $unitResult = [pscustomobject]@{
        unit_id = $unitId
        kind = $kind
        status = if ($verificationPassed) { 'completed' } elseif ($processResult.timed_out) { 'timed_out' } else { 'failed' }
        started_at = $startedAt
        finished_at = $finishedAt
        command = $command
        arguments = @($arguments)
        display_command = $display
        cwd = $cwd
        timeout_seconds = $timeoutSeconds
        expected_exit_code = $expectedExitCode
        exit_code = [int]$processResult.exit_code
        timed_out = [bool]$processResult.timed_out
        stdout_path = $processResult.stdout_path
        stderr_path = $processResult.stderr_path
        stdout_preview = @($processResult.stdout_preview)
        stderr_preview = @($processResult.stderr_preview)
        expected_artifacts = @($resolvedArtifacts)
        verification_passed = [bool]$verificationPassed
    }

    $resultPath = Join-Path $resultsRoot ("{0}.json" -f $unitId)
    Write-VibeJsonArtifact -Path $resultPath -Value $unitResult

    return [pscustomobject]@{
        result = $unitResult
        result_path = $resultPath
    }
}

$runtime = Get-VibeRuntimeContext -ScriptPath $PSCommandPath
if ([string]::IsNullOrWhiteSpace($RunId)) {
    $RunId = New-VibeRunId
}

$sessionRoot = Ensure-VibeSessionRoot -RepoRoot $runtime.repo_root -RunId $RunId -ArtifactRoot $ArtifactRoot
$grade = Get-VibeInternalGrade -Task $Task
$requirementPath = if (-not [string]::IsNullOrWhiteSpace($RequirementDocPath)) { $RequirementDocPath } else { Get-VibeRequirementDocPath -RepoRoot $runtime.repo_root -Task $Task -ArtifactRoot $ArtifactRoot }
$planPath = if (-not [string]::IsNullOrWhiteSpace($ExecutionPlanPath)) { $ExecutionPlanPath } else { Get-VibeExecutionPlanPath -RepoRoot $runtime.repo_root -Task $Task -ArtifactRoot $ArtifactRoot }

$policy = $runtime.benchmark_execution_policy
$profile = $null
foreach ($candidate in @($policy.profiles)) {
    if ([string]$candidate.id -eq [string]$policy.default_profile_id) {
        $profile = $candidate
        break
    }
}
if ($null -eq $profile) {
    throw 'Unable to resolve benchmark execution profile from config/benchmark-execution-policy.json.'
}

$logsRoot = Join-Path $sessionRoot 'execution-logs'
$resultsRoot = Join-Path $sessionRoot 'execution-results'
$proofRoot = Join-Path $sessionRoot ([string]$profile.proof_bundle_dirname)
New-Item -ItemType Directory -Path $logsRoot -Force | Out-Null
New-Item -ItemType Directory -Path $resultsRoot -Force | Out-Null
New-Item -ItemType Directory -Path $proofRoot -Force | Out-Null

$tokens = @{
    '${REPO_ROOT}' = [System.IO.Path]::GetFullPath($runtime.repo_root)
    '${SESSION_ROOT}' = [System.IO.Path]::GetFullPath($sessionRoot)
    '${REQUIREMENT_DOC}' = [System.IO.Path]::GetFullPath($requirementPath)
    '${EXECUTION_PLAN}' = [System.IO.Path]::GetFullPath($planPath)
    '${RUN_ID}' = [string]$RunId
}

$waveReceipts = @()
$resultPaths = @()
$executedUnitCount = 0
$successfulUnitCount = 0
$failedUnitCount = 0
$timedOutUnitCount = 0
$plannedUnitCount = 0

foreach ($wave in @($profile.waves)) {
    $waveStartedAt = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    $waveResults = @()
    $plannedUnitCount += @($wave.units).Count

    foreach ($unit in @($wave.units)) {
        $executed = Invoke-VibeExecutionUnit -Unit $unit -RepoRoot $runtime.repo_root -SessionRoot $sessionRoot -Tokens $tokens -DefaultTimeoutSeconds ([int]$policy.scheduler.default_timeout_seconds)
        $waveResults += $executed.result
        $resultPaths += $executed.result_path
        $executedUnitCount += 1
        if ([bool]$executed.result.verification_passed) {
            $successfulUnitCount += 1
        } elseif ([bool]$executed.result.timed_out) {
            $timedOutUnitCount += 1
            $failedUnitCount += 1
        } else {
            $failedUnitCount += 1
        }
    }

    $waveReceipts += [pscustomobject]@{
        wave_id = [string]$wave.wave_id
        description = [string]$wave.description
        status = if (@($waveResults | Where-Object { -not $_.verification_passed }).Count -eq 0) { 'completed' } else { 'failed' }
        started_at = $waveStartedAt
        finished_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        planned_unit_count = @($wave.units).Count
        executed_unit_count = @($waveResults).Count
        units = @($waveResults | ForEach-Object {
            [pscustomobject]@{
                unit_id = [string]$_.unit_id
                status = [string]$_.status
                exit_code = [int]$_.exit_code
                result_path = (Join-Path $resultsRoot ("{0}.json" -f $_.unit_id))
            }
        })
    }
}

$executionManifest = [pscustomobject]@{
    stage = 'plan_execute'
    run_id = $RunId
    mode = $Mode
    internal_grade = $grade
    scheduler_kind = [string]$policy.scheduler.kind
    profile_id = [string]$profile.id
    requirement_doc_path = $requirementPath
    execution_plan_path = $planPath
    generated_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    planned_wave_count = @($profile.waves).Count
    planned_unit_count = $plannedUnitCount
    executed_unit_count = $executedUnitCount
    successful_unit_count = $successfulUnitCount
    failed_unit_count = $failedUnitCount
    timed_out_unit_count = $timedOutUnitCount
    status = if ($failedUnitCount -eq 0 -and $executedUnitCount -ge [int]$profile.expected_minimum_units) { 'completed' } elseif ($executedUnitCount -eq 0) { 'failed' } else { 'completed_with_failures' }
    waves = @($waveReceipts)
}

$executionManifestPath = Join-Path $sessionRoot 'execution-manifest.json'
Write-VibeJsonArtifact -Path $executionManifestPath -Value $executionManifest

$proofManifest = [pscustomobject]@{
    bundle_kind = 'benchmark_autonomous_execution_proof'
    generated_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    run_id = $RunId
    mode = $Mode
    task = $Task
    session_root = $sessionRoot
    execution_manifest_path = $executionManifestPath
    result_paths = @($resultPaths)
    executed_unit_count = $executedUnitCount
    successful_unit_count = $successfulUnitCount
    failed_unit_count = $failedUnitCount
    minimum_units_required = [int]$profile.expected_minimum_units
    proof_passed = [bool](($failedUnitCount -eq 0) -and ($executedUnitCount -ge [int]$profile.expected_minimum_units))
}
$proofManifestPath = Join-Path $proofRoot 'manifest.json'
Write-VibeJsonArtifact -Path $proofManifestPath -Value $proofManifest

$proofLines = @(
    '# Benchmark Autonomous Proof',
    '',
    ('- run_id: `{0}`' -f $RunId),
    ('- mode: `{0}`' -f $Mode),
    ('- profile: `{0}`' -f ([string]$profile.id)),
    ('- executed_unit_count: `{0}`' -f $executedUnitCount),
    ('- successful_unit_count: `{0}`' -f $successfulUnitCount),
    ('- failed_unit_count: `{0}`' -f $failedUnitCount),
    ('- execution_manifest: `{0}`' -f $executionManifestPath),
    ''
)
foreach ($waveReceipt in @($waveReceipts)) {
    $proofLines += @(
        "## $([string]$waveReceipt.wave_id)",
        "- status: $([string]$waveReceipt.status)",
        "- executed_unit_count: $([int]$waveReceipt.executed_unit_count)"
    )
    foreach ($unitReceipt in @($waveReceipt.units)) {
        $proofLines += ('- unit `{0}` -> status `{1}`, exit_code `{2}`' -f ([string]$unitReceipt.unit_id), ([string]$unitReceipt.status), ([int]$unitReceipt.exit_code))
    }
    $proofLines += ''
}
$proofSummaryPath = Join-Path $proofRoot 'operation-record.md'
Write-VibeMarkdownArtifact -Path $proofSummaryPath -Lines $proofLines

$receipt = [pscustomobject]@{
    stage = 'plan_execute'
    run_id = $RunId
    mode = $Mode
    internal_grade = $grade
    status = [string]$executionManifest.status
    requirement_doc_path = $requirementPath
    execution_plan_path = $planPath
    execution_manifest_path = $executionManifestPath
    benchmark_proof_manifest_path = $proofManifestPath
    executed_unit_count = $executedUnitCount
    successful_unit_count = $successfulUnitCount
    failed_unit_count = $failedUnitCount
    verification_contract = @(
        'No completion claim without verification evidence.',
        'All subagent prompts must end with $vibe.',
        'Phase cleanup must run after execution.'
    )
    generated_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
}

$receiptPath = Join-Path $sessionRoot 'phase-execute.json'
Write-VibeJsonArtifact -Path $receiptPath -Value $receipt

[pscustomobject]@{
    run_id = $RunId
    session_root = $sessionRoot
    receipt_path = $receiptPath
    execution_manifest_path = $executionManifestPath
    benchmark_proof_manifest_path = $proofManifestPath
    receipt = $receipt
}
