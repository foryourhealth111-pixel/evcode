param(
    [Parameter(Mandatory)] [string]$FixturePath,
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
$resolvedFixturePath = Resolve-VgoPathSpec -PathSpec $FixturePath -RepoRoot $repoRoot
$packet = Get-Content -LiteralPath $resolvedFixturePath -Raw -Encoding UTF8 | ConvertFrom-Json
$assessment = Get-VgoAntiProxyGoalDriftAssessment -Policy $policy -Packet $packet
$results = [System.Collections.Generic.List[object]]::new()

Add-Assertion -Results $results -Condition (-not [string]::IsNullOrWhiteSpace($assessment.fixture_id)) -Message 'fixture_id exists'
Add-Assertion -Results $results -Condition ($assessment.warning_count -ge 0) -Message 'warning_count is computed'

if ($packet.PSObject.Properties.Name -contains 'expected') {
    $expected = $packet.expected
    if ($expected.PSObject.Properties.Name -contains 'minimum_tier') {
        Add-Assertion -Results $results -Condition ($assessment.minimum_tier -eq [string]$expected.minimum_tier) -Message 'minimum tier matches expectation' -Details $assessment.minimum_tier
    }
    if ($expected.PSObject.Properties.Name -contains 'warning_count') {
        Add-Assertion -Results $results -Condition ($assessment.warning_count -eq [int]$expected.warning_count) -Message 'warning count matches expectation' -Details $assessment.warning_codes
    }
    if ($expected.PSObject.Properties.Name -contains 'warning_codes') {
        $expectedWarnings = @($expected.warning_codes)
        $actualWarnings = @($assessment.warning_codes)
        $expectedKey = ($expectedWarnings | Sort-Object) -join '|'
        $actualKey = ($actualWarnings | Sort-Object) -join '|'
        Add-Assertion -Results $results -Condition ($expectedKey -eq $actualKey) -Message 'warning codes match expectation' -Details @{ expected=$expectedWarnings; actual=$actualWarnings }
    }
}

$failed = @($results | Where-Object { -not $_.pass }).Count
$gateResult = if ($failed -eq 0) { 'PASS' } else { 'FAIL' }
$artifact = [pscustomobject]@{
    gate = 'vibe-anti-proxy-goal-drift-gate'
    generated_at = [DateTime]::UtcNow.ToString('o')
    fixture_path = $resolvedFixturePath
    gate_result = $gateResult
    failure_count = $failed
    assessment = $assessment
    results = @($results)
}

if ($WriteArtifacts) {
    $outDir = if ([string]::IsNullOrWhiteSpace($OutputDirectory)) { Join-Path $repoRoot 'outputs\verify' } else { $OutputDirectory }
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    $leaf = [System.IO.Path]::GetFileNameWithoutExtension($resolvedFixturePath)
    Write-VgoUtf8NoBomText -Path (Join-Path $outDir ("vibe-anti-proxy-goal-drift-gate-$leaf.json")) -Content ($artifact | ConvertTo-Json -Depth 60)
}

if ($gateResult -ne 'PASS') { exit 1 }
