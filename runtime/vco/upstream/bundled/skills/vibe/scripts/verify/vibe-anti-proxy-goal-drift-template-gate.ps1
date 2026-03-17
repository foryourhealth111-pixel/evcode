param(
    [switch]$WriteArtifacts,
    [string]$OutputDirectory = ''
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\common\vibe-governance-helpers.ps1')
. (Join-Path $PSScriptRoot '..\common\AntiProxyGoalDrift.ps1')

function Add-Check {
    param([System.Collections.Generic.List[object]]$Results,[bool]$Condition,[string]$Message,[object]$Details=$null)
    [void]$Results.Add([pscustomobject]@{ pass=[bool]$Condition; message=$Message; details=$Details })
    if ($Condition) { Write-Host "[PASS] $Message" } else { Write-Host "[FAIL] $Message" -ForegroundColor Red }
}

$context = Get-VgoGovernanceContext -ScriptPath $PSCommandPath -EnforceExecutionContext
$repoRoot = $context.repoRoot
$policy = Get-VgoAntiProxyGoalDriftPolicy -RepoRoot $repoRoot
$results = [System.Collections.Generic.List[object]]::new()

$requirementTemplatePath = Join-Path $repoRoot 'templates\requirements\governed-requirement-template.md'
$planTemplatePath = Join-Path $repoRoot 'templates\plans\governed-execution-plan-template.md'
$cerMdPath = Join-Path $repoRoot 'templates\cer-report.md.template'
$cerJsonPath = Join-Path $repoRoot 'templates\cer-report.json.template'
$requirementPolicyPath = Join-Path $repoRoot 'config\requirement-doc-policy.json'
$planPolicyPath = Join-Path $repoRoot 'config\plan-execution-policy.json'
$governanceDocPath = Join-Path $repoRoot 'docs\anti-proxy-goal-drift-governance.md'

$requirementTemplate = Get-Content -LiteralPath $requirementTemplatePath -Raw -Encoding UTF8
$planTemplate = Get-Content -LiteralPath $planTemplatePath -Raw -Encoding UTF8
$cerMd = Get-Content -LiteralPath $cerMdPath -Raw -Encoding UTF8
$cerJson = Get-Content -LiteralPath $cerJsonPath -Raw -Encoding UTF8
$requirementPolicy = Get-Content -LiteralPath $requirementPolicyPath -Raw -Encoding UTF8 | ConvertFrom-Json
$planPolicy = Get-Content -LiteralPath $planPolicyPath -Raw -Encoding UTF8 | ConvertFrom-Json
$governanceDoc = Get-Content -LiteralPath $governanceDocPath -Raw -Encoding UTF8

foreach ($field in @($policy.required_requirement_fields)) {
    Add-Check -Results $results -Condition ($requirementTemplate.Contains("## $field")) -Message ("requirement template contains $field")
    Add-Check -Results $results -Condition (@($requirementPolicy.required_sections) -contains $field) -Message ("requirement policy tracks $field")
}

foreach ($field in @($policy.required_plan_fields)) {
    $heading = if ($field -eq 'Anti-Proxy-Goal-Drift Controls') { "## $field" } else { "### $field" }
    Add-Check -Results $results -Condition ($planTemplate.Contains($heading)) -Message ("plan template contains $field")
}
Add-Check -Results $results -Condition (@($planPolicy.required_plan_sections) -contains 'Anti-Proxy-Goal-Drift Controls') -Message 'plan policy tracks anti-drift controls section'

foreach ($token in @($policy.required_cer_fields)) {
    Add-Check -Results $results -Condition ($cerMd.Contains($token)) -Message ("CER markdown template contains $token")
    Add-Check -Results $results -Condition ($cerJson.Contains($token)) -Message ("CER json template contains $token")
}

foreach ($keyword in @('report_only', 'Tier A', 'Tier B', 'Tier C', 'completion state', 'specialization')) {
    Add-Check -Results $results -Condition ($governanceDoc.ToLowerInvariant().Contains($keyword.ToLowerInvariant())) -Message ("governance doc contains $keyword")
}

$failed = @($results | Where-Object { -not $_.pass }).Count
$gateResult = if ($failed -eq 0) { 'PASS' } else { 'FAIL' }
$artifact = [pscustomobject]@{
    gate = 'vibe-anti-proxy-goal-drift-template-gate'
    generated_at = [DateTime]::UtcNow.ToString('o')
    gate_result = $gateResult
    failure_count = $failed
    results = @($results)
}

if ($WriteArtifacts) {
    $outDir = if ([string]::IsNullOrWhiteSpace($OutputDirectory)) { Join-Path $repoRoot 'outputs\verify' } else { $OutputDirectory }
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    Write-VgoUtf8NoBomText -Path (Join-Path $outDir 'vibe-anti-proxy-goal-drift-template-gate.json') -Content ($artifact | ConvertTo-Json -Depth 40)
}

if ($gateResult -ne 'PASS') { exit 1 }
