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

    [void]$Assertions.Add([pscustomobject]@{
        pass = [bool]$Condition
        message = $Message
        details = $Details
    })

    if ($Condition) {
        Write-Host "[PASS] $Message"
    } else {
        Write-Host "[FAIL] $Message" -ForegroundColor Red
    }
}

$context = Get-VgoGovernanceContext -ScriptPath $PSCommandPath -EnforceExecutionContext
$repoRoot = $context.repoRoot
$assertions = [System.Collections.Generic.List[object]]::new()

$reviewPath = Join-Path $repoRoot 'protocols\review.md'
$retroPath = Join-Path $repoRoot 'protocols\retro.md'
$cerMdPath = Join-Path $repoRoot 'templates\cer-report.md.template'
$cerJsonPath = Join-Path $repoRoot 'templates\cer-report.json.template'
$cerSchemaPath = Join-Path $repoRoot 'templates\cer-report.schema.json'
$statusReadmePath = Join-Path $repoRoot 'docs\status\README.md'
$closureAuditPath = Join-Path $repoRoot 'docs\status\closure-audit.md'
$sampleReviewPath = Join-Path $repoRoot 'references\fixtures\anti-proxy-goal-drift\lane1-sample-review-report.md'
$sampleClosurePath = Join-Path $repoRoot 'references\fixtures\anti-proxy-goal-drift\lane1-sample-closure-audit.md'
$sampleCerPath = Join-Path $repoRoot 'references\fixtures\anti-proxy-goal-drift\lane1-sample-cer.json'

$review = Get-Content -LiteralPath $reviewPath -Raw -Encoding UTF8
$retro = Get-Content -LiteralPath $retroPath -Raw -Encoding UTF8
$cerMd = Get-Content -LiteralPath $cerMdPath -Raw -Encoding UTF8
$cerJson = Get-Content -LiteralPath $cerJsonPath -Raw -Encoding UTF8
$cerSchema = Get-Content -LiteralPath $cerSchemaPath -Raw -Encoding UTF8 | ConvertFrom-Json -Depth 20
$statusReadme = Get-Content -LiteralPath $statusReadmePath -Raw -Encoding UTF8
$closureAudit = Get-Content -LiteralPath $closureAuditPath -Raw -Encoding UTF8
$sampleCer = Get-Content -LiteralPath $sampleCerPath -Raw -Encoding UTF8 | ConvertFrom-Json -Depth 20

Add-Assertion -Assertions $assertions -Condition ($review.Contains('## Anti-Proxy-Goal-Drift Review Lens')) -Message 'review protocol defines anti-drift review lens'
Add-Assertion -Assertions $assertions -Condition ($review.Contains('report_only_warning')) -Message 'review protocol defines report-only warning disposition'
Add-Assertion -Assertions $assertions -Condition ($review.Contains('specialization_confirmed')) -Message 'review protocol preserves specialization disposition'
Add-Assertion -Assertions $assertions -Condition ($review.Contains('do not by themselves create a new hard gate')) -Message 'review protocol states no hidden hard gate'

Add-Assertion -Assertions $assertions -Condition ($retro.Contains('## Anti-Proxy-Goal-Drift Retro Lens')) -Message 'retro protocol defines anti-drift retro lens'
Add-Assertion -Assertions $assertions -Condition ($retro.Contains('completion_language_corrected')) -Message 'retro protocol defines completion-language correction disposition'
Add-Assertion -Assertions $assertions -Condition ($retro.Contains('specialization_assessment')) -Message 'retro protocol requires specialization assessment in CER vocabulary'
Add-Assertion -Assertions $assertions -Condition ($retro.Contains('must name the separate approved policy or hard gate')) -Message 'retro protocol forbids hidden enforcement'

foreach ($token in @('governance_mode', 'report_only_warning_codes', 'specialization_assessment', 'completion_honesty_notes')) {
    Add-Assertion -Assertions $assertions -Condition ($cerMd.Contains($token)) -Message ("CER markdown template contains {0}" -f $token)
    Add-Assertion -Assertions $assertions -Condition ($cerJson.Contains($token)) -Message ("CER json template contains {0}" -f $token)
}

$requiredTopLevel = @($cerSchema.required)
Add-Assertion -Assertions $assertions -Condition ($requiredTopLevel -contains 'objective_protection') -Message 'CER schema requires objective_protection'

$objectiveProtection = $cerSchema.properties.objective_protection
$requiredObjectiveFields = @($objectiveProtection.required)
foreach ($field in @('governance_mode', 'anti_proxy_goal_drift_tier', 'completion_state', 'primary_objective', 'specialization_assessment', 'report_only_warning_codes', 'completion_honesty_notes')) {
    Add-Assertion -Assertions $assertions -Condition ($requiredObjectiveFields -contains $field) -Message ("CER schema requires objective_protection.{0}" -f $field)
}

Add-Assertion -Assertions $assertions -Condition ($statusReadme.Contains('report-only completion-honesty language')) -Message 'status README indexes closure audit as completion-honesty surface'
Add-Assertion -Assertions $assertions -Condition ($closureAudit.Contains('## Anti-Drift Closure Contract')) -Message 'closure audit includes anti-drift contract section'
Add-Assertion -Assertions $assertions -Condition ($closureAudit.Contains('not as a hidden hard gate')) -Message 'closure audit preserves report-only posture'

Add-Assertion -Assertions $assertions -Condition (Test-Path -LiteralPath $sampleReviewPath) -Message 'lane1 sample review artifact exists'
Add-Assertion -Assertions $assertions -Condition (Test-Path -LiteralPath $sampleClosurePath) -Message 'lane1 sample closure artifact exists'
Add-Assertion -Assertions $assertions -Condition (Test-Path -LiteralPath $sampleCerPath) -Message 'lane1 sample CER artifact exists'
Add-Assertion -Assertions $assertions -Condition ([string]$sampleCer.schema_version -eq '1.2.0') -Message 'lane1 sample CER uses schema version 1.2.0'
Add-Assertion -Assertions $assertions -Condition ([string]$sampleCer.objective_protection.governance_mode -eq 'report_only') -Message 'lane1 sample CER uses report_only governance mode'
Add-Assertion -Assertions $assertions -Condition (@($sampleCer.objective_protection.report_only_warning_codes).Count -ge 1) -Message 'lane1 sample CER carries report-only warning codes'
Add-Assertion -Assertions $assertions -Condition (-not [string]::IsNullOrWhiteSpace([string]$sampleCer.objective_protection.specialization_assessment)) -Message 'lane1 sample CER carries specialization assessment'
Add-Assertion -Assertions $assertions -Condition (-not [string]::IsNullOrWhiteSpace([string]$sampleCer.objective_protection.completion_honesty_notes)) -Message 'lane1 sample CER carries completion honesty notes'

$failed = @($assertions | Where-Object { -not $_.pass }).Count
$result = if ($failed -eq 0) { 'PASS' } else { 'FAIL' }
$artifact = [pscustomobject]@{
    gate = 'vibe-anti-proxy-goal-drift-lane1-gate'
    generated_at = [DateTime]::UtcNow.ToString('o')
    gate_result = $result
    failure_count = $failed
    assertions = @($assertions)
}

if ($WriteArtifacts) {
    $outDir = if ([string]::IsNullOrWhiteSpace($OutputDirectory)) { Join-Path $repoRoot 'outputs\verify' } else { $OutputDirectory }
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    Write-VgoUtf8NoBomText -Path (Join-Path $outDir 'vibe-anti-proxy-goal-drift-lane1-gate.json') -Content ($artifact | ConvertTo-Json -Depth 60)
}

if ($result -ne 'PASS') {
    exit 1
}
