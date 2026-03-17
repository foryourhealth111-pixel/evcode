param(
    [switch]$WriteArtifacts,
    [string]$OutputDirectory = ''
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\common\vibe-governance-helpers.ps1')
. (Join-Path $PSScriptRoot '..\common\AntiProxyGoalDrift.ps1')

function Add-Assertion {
    param([System.Collections.Generic.List[object]]$Results,[bool]$Condition,[string]$Message,[object]$Details=$null)
    [void]$Results.Add([pscustomobject]@{ pass=[bool]$Condition; message=$Message; details=$Details })
    if ($Condition) { Write-Host "[PASS] $Message" } else { Write-Host "[FAIL] $Message" -ForegroundColor Red }
}

$context = Get-VgoGovernanceContext -ScriptPath $PSCommandPath -EnforceExecutionContext
$repoRoot = $context.repoRoot
$policy = Get-VgoAntiProxyGoalDriftPolicy -RepoRoot $repoRoot
$corpusRoot = Join-Path $repoRoot 'references\fixtures\anti-proxy-goal-drift'
$results = [System.Collections.Generic.List[object]]::new()

$files = @(Get-ChildItem -LiteralPath $corpusRoot -Filter '*.json' -File | Sort-Object Name)
Add-Assertion -Results $results -Condition ($files.Count -ge 10) -Message 'corpus contains at least 10 fixtures' -Details $files.Count

$fixtures = @()
foreach ($file in $files) {
    $fixture = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
    $fixtures += $fixture
    Add-Assertion -Results $results -Condition (-not [string]::IsNullOrWhiteSpace([string]$fixture.fixture_id)) -Message ("fixture_id exists: $($file.Name)")
    Add-Assertion -Results $results -Condition (-not [string]::IsNullOrWhiteSpace([string]$fixture.corpus_family)) -Message ("corpus_family exists: $($file.Name)")
    $assessment = Get-VgoAntiProxyGoalDriftAssessment -Policy $policy -Packet $fixture
    if ($fixture.PSObject.Properties.Name -contains 'expected') {
        $expectedWarnings = @($fixture.expected.warning_codes)
        $actualWarnings = @($assessment.warning_codes)
        $expectedKey = ($expectedWarnings | Sort-Object) -join '|'
        $actualKey = ($actualWarnings | Sort-Object) -join '|'
        Add-Assertion -Results $results -Condition ($expectedKey -eq $actualKey) -Message ("assessment matches expected warnings: $($file.Name)") -Details @{ expected=$expectedWarnings; actual=$actualWarnings }
    }
}

$fixtureIds = @($fixtures | ForEach-Object { [string]$_.fixture_id })
Add-Assertion -Results $results -Condition (($fixtureIds | Select-Object -Unique).Count -eq $fixtureIds.Count) -Message 'fixture_id values are unique'

foreach ($family in @('tier_gold', 'red_team', 'legitimate_specialization', 'completion_state')) {
    Add-Assertion -Results $results -Condition ((@($fixtures | Where-Object { $_.corpus_family -eq $family }).Count) -ge 1) -Message ("corpus contains family $family")
}

$completionStates = @($fixtures | Where-Object { $_.corpus_family -eq 'completion_state' } | ForEach-Object { [string]$_.completion_state })
foreach ($state in @('complete', 'partial', 'scenario-scoped', 'blocked', 'not-yet-generalized')) {
    Add-Assertion -Results $results -Condition ($completionStates -contains $state) -Message ("completion corpus includes state $state")
}

$failed = @($results | Where-Object { -not $_.pass }).Count
$gateResult = if ($failed -eq 0) { 'PASS' } else { 'FAIL' }
$artifact = [pscustomobject]@{
    gate = 'vibe-anti-proxy-goal-drift-corpus-gate'
    generated_at = [DateTime]::UtcNow.ToString('o')
    gate_result = $gateResult
    failure_count = $failed
    fixture_count = $files.Count
    results = @($results)
}

if ($WriteArtifacts) {
    $outDir = if ([string]::IsNullOrWhiteSpace($OutputDirectory)) { Join-Path $repoRoot 'outputs\verify' } else { $OutputDirectory }
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    Write-VgoUtf8NoBomText -Path (Join-Path $outDir 'vibe-anti-proxy-goal-drift-corpus-gate.json') -Content ($artifact | ConvertTo-Json -Depth 60)
}

if ($gateResult -ne 'PASS') { exit 1 }
