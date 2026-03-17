param(
    [switch]$WriteArtifacts,
    [string]$OutputDirectory = ''
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\common\vibe-governance-helpers.ps1')

function Add-Assertion {
    param(
        [System.Collections.Generic.List[object]]$Assertions,
        [bool]$Condition,
        [string]$Message,
        [object]$Details = $null
    )

    [void]$Assertions.Add([pscustomobject]@{ pass = [bool]$Condition; message = $Message; details = $Details })
    if ($Condition) { Write-Host "[PASS] $Message" } else { Write-Host "[FAIL] $Message" -ForegroundColor Red }
}

$context = Get-VgoGovernanceContext -ScriptPath $PSCommandPath -EnforceExecutionContext
$repoRoot = $context.repoRoot
$assertions = [System.Collections.Generic.List[object]]::new()

$currentStatePath = Join-Path $repoRoot 'docs\status\current-state.md'
$releaseContractPath = Join-Path $repoRoot 'references\release-evidence-bundle-contract.md'
$execStatusPath = Join-Path $repoRoot 'config\execution-context-status.json'
$promotionBoardPath = Join-Path $repoRoot 'config\promotion-board.json'
$thinkPath = Join-Path $repoRoot 'protocols\think.md'
$doPath = Join-Path $repoRoot 'protocols\do.md'
$teamPath = Join-Path $repoRoot 'protocols\team.md'
$sampleReleasePath = Join-Path $repoRoot 'references\fixtures\anti-proxy-goal-drift\lane2-release-evidence-fragment.json'

$currentState = Get-Content -LiteralPath $currentStatePath -Raw -Encoding UTF8
$releaseContract = Get-Content -LiteralPath $releaseContractPath -Raw -Encoding UTF8
$execStatus = Get-Content -LiteralPath $execStatusPath -Raw -Encoding UTF8 | ConvertFrom-Json -Depth 20
$promotionBoard = Get-Content -LiteralPath $promotionBoardPath -Raw -Encoding UTF8 | ConvertFrom-Json -Depth 40
$think = Get-Content -LiteralPath $thinkPath -Raw -Encoding UTF8
$do = Get-Content -LiteralPath $doPath -Raw -Encoding UTF8
$team = Get-Content -LiteralPath $teamPath -Raw -Encoding UTF8
$sampleRelease = Get-Content -LiteralPath $sampleReleasePath -Raw -Encoding UTF8 | ConvertFrom-Json -Depth 20

Add-Assertion -Assertions $assertions -Condition ($currentState.Contains('## Anti-Drift Observability Snapshot')) -Message 'current-state includes anti-drift observability snapshot'
Add-Assertion -Assertions $assertions -Condition ($currentState.Contains('must not convert report-only warnings into hidden release or execution failure')) -Message 'current-state preserves descriptive-only observability'

foreach ($token in @('anti_drift_governance_mode', 'completion_honesty_summary', 'report_only_warning_codes', 'specialization_notes')) {
    Add-Assertion -Assertions $assertions -Condition ($releaseContract.Contains($token)) -Message ("release evidence contract includes {0}" -f $token)
}
Add-Assertion -Assertions $assertions -Condition ($releaseContract.Contains('must not reinterpret them as automatic release denial')) -Message 'release evidence contract preserves report-only posture'

Add-Assertion -Assertions $assertions -Condition ([string]$execStatus.anti_proxy_goal_drift_observability.mode -eq 'report_only') -Message 'execution-context-status carries report_only observability mode'
Add-Assertion -Assertions $assertions -Condition ([bool]$execStatus.anti_proxy_goal_drift_observability.warning_codes_are_descriptive_only) -Message 'execution-context-status marks warning codes descriptive-only'

Add-Assertion -Assertions $assertions -Condition ([string]$promotionBoard.board_policy.anti_drift_mode -eq 'report_only') -Message 'promotion-board carries report_only anti-drift mode'
Add-Assertion -Assertions $assertions -Condition ([bool]$promotionBoard.board_policy.anti_drift_warning_codes_are_non_blocking_without_independent_failed_gate) -Message 'promotion-board preserves non-blocking warning posture'
Add-Assertion -Assertions $assertions -Condition ([bool]$promotionBoard.stage_requirements.promote.anti_drift_release_summary_required) -Message 'promotion-board requires anti-drift release summary at promote stage'

Add-Assertion -Assertions $assertions -Condition ($think.Contains('## Anti-Drift Planning Guardrails')) -Message 'think protocol includes anti-drift planning guardrails'
Add-Assertion -Assertions $assertions -Condition ($think.Contains('does not create a hidden hard gate')) -Message 'think protocol keeps anti-drift advisory'
Add-Assertion -Assertions $assertions -Condition ($do.Contains('## Anti-Drift Execution Guardrails')) -Message 'do protocol includes anti-drift execution guardrails'
Add-Assertion -Assertions $assertions -Condition ($do.Contains('not a standalone blocking layer')) -Message 'do protocol keeps anti-drift non-blocking'
Add-Assertion -Assertions $assertions -Condition ($team.Contains('## Anti-Drift Handoff Contract')) -Message 'team protocol includes anti-drift handoff contract'
Add-Assertion -Assertions $assertions -Condition ($team.Contains('must not invent a new hard gate')) -Message 'team protocol forbids invented hard gates'

Add-Assertion -Assertions $assertions -Condition (Test-Path -LiteralPath $sampleReleasePath) -Message 'lane2 release evidence sample exists'
Add-Assertion -Assertions $assertions -Condition ([string]$sampleRelease.anti_drift_governance_mode -eq 'report_only') -Message 'lane2 sample release evidence uses report_only mode'
Add-Assertion -Assertions $assertions -Condition (@($sampleRelease.report_only_warning_codes).Count -ge 1) -Message 'lane2 sample release evidence carries warning codes'
Add-Assertion -Assertions $assertions -Condition (-not [string]::IsNullOrWhiteSpace([string]$sampleRelease.specialization_notes)) -Message 'lane2 sample release evidence carries specialization notes'

$failed = @($assertions | Where-Object { -not $_.pass }).Count
$result = if ($failed -eq 0) { 'PASS' } else { 'FAIL' }
$artifact = [pscustomobject]@{
    gate = 'vibe-anti-proxy-goal-drift-lane2-lane3-gate'
    generated_at = [DateTime]::UtcNow.ToString('o')
    gate_result = $result
    failure_count = $failed
    assertions = @($assertions)
}

if ($WriteArtifacts) {
    $outDir = if ([string]::IsNullOrWhiteSpace($OutputDirectory)) { Join-Path $repoRoot 'outputs\verify' } else { $OutputDirectory }
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    Write-VgoUtf8NoBomText -Path (Join-Path $outDir 'vibe-anti-proxy-goal-drift-lane2-lane3-gate.json') -Content ($artifact | ConvertTo-Json -Depth 60)
}

if ($result -ne 'PASS') { exit 1 }
