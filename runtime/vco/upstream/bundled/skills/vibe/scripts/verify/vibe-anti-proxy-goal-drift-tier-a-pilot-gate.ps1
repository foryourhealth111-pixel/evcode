param(
    [switch]$WriteArtifacts,
    [string]$OutputDirectory = ''
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\common\vibe-governance-helpers.ps1')
. (Join-Path $PSScriptRoot '..\common\AntiProxyGoalDrift.ps1')

$context = Get-VgoGovernanceContext -ScriptPath $PSCommandPath -EnforceExecutionContext
$repoRoot = $context.repoRoot
$policy = Get-VgoAntiProxyGoalDriftPolicy -RepoRoot $repoRoot
$corpusRoot = Join-Path $repoRoot 'references\fixtures\anti-proxy-goal-drift'
$files = @(Get-ChildItem -LiteralPath $corpusRoot -Filter '*.json' -File | Sort-Object Name)
$fixtures = @($files | ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json })
$assessments = @($fixtures | ForEach-Object { Get-VgoAntiProxyGoalDriftAssessment -Policy $policy -Packet $_ })

$redTeamFixtures = @($fixtures | Where-Object { $_.corpus_family -eq 'red_team' })
$specializationFixtures = @($fixtures | Where-Object { $_.corpus_family -eq 'legitimate_specialization' })
$tierGoldFixtures = @($fixtures | Where-Object { $_.corpus_family -eq 'tier_gold' })
$tierAPilotFixtures = @($fixtures | Where-Object { $_.anti_proxy_goal_drift_tier -eq 'Tier A' -or $_.surface_class -match '(_core)$' })

function Get-AssessmentForFixtureId {
    param([string]$FixtureId)
    return @($assessments | Where-Object { $_.fixture_id -eq $FixtureId }) | Select-Object -First 1
}

$redTeamCaught = 0
foreach ($fixture in $redTeamFixtures) {
    $assessment = Get-AssessmentForFixtureId -FixtureId ([string]$fixture.fixture_id)
    if (@($assessment.warning_codes).Count -gt 0) { $redTeamCaught++ }
}

$specializationFalsePositives = 0
foreach ($fixture in $specializationFixtures) {
    $assessment = Get-AssessmentForFixtureId -FixtureId ([string]$fixture.fixture_id)
    if (@($assessment.warning_codes).Count -gt 0) { $specializationFalsePositives++ }
}

$tierAgreement = 0
foreach ($fixture in $tierGoldFixtures) {
    $assessment = Get-AssessmentForFixtureId -FixtureId ([string]$fixture.fixture_id)
    if ($fixture.expected.minimum_tier -eq $assessment.minimum_tier) { $tierAgreement++ }
}

$redTeamRecall = if ($redTeamFixtures.Count -gt 0) { [math]::Round($redTeamCaught / $redTeamFixtures.Count, 4) } else { 0.0 }
$specializationFalsePositiveRate = if ($specializationFixtures.Count -gt 0) { [math]::Round($specializationFalsePositives / $specializationFixtures.Count, 4) } else { 0.0 }
$tierAgreementRate = if ($tierGoldFixtures.Count -gt 0) { [math]::Round($tierAgreement / $tierGoldFixtures.Count, 4) } else { 0.0 }

$decision = 'continue_report_only'
$decisionReasons = @(
    'pilot is deterministic and catches red-team fixtures',
    'specialization false-positive rate is measurable from fixtures',
    'human usability evidence is still missing, so hard enforcement would be dishonest'
)

$artifact = [pscustomobject]@{
    gate = 'vibe-anti-proxy-goal-drift-tier-a-pilot-gate'
    generated_at = [DateTime]::UtcNow.ToString('o')
    policy_mode = $policy.mode
    tier_a_pilot_fixture_count = $tierAPilotFixtures.Count
    metrics = [pscustomobject]@{
        red_team_fixture_count = $redTeamFixtures.Count
        red_team_caught = $redTeamCaught
        red_team_recall = $redTeamRecall
        specialization_fixture_count = $specializationFixtures.Count
        specialization_false_positives = $specializationFalsePositives
        specialization_false_positive_rate = $specializationFalsePositiveRate
        tier_gold_fixture_count = $tierGoldFixtures.Count
        tier_agreement = $tierAgreement
        tier_agreement_rate = $tierAgreementRate
        human_usability_evidence_present = $false
    }
    decision = [pscustomobject]@{
        recommendation = $decision
        eligible_for_hard_enforcement = $false
        reasons = $decisionReasons
    }
}

if ($WriteArtifacts) {
    $outDir = if ([string]::IsNullOrWhiteSpace($OutputDirectory)) { Join-Path $repoRoot 'outputs\verify' } else { $OutputDirectory }
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    Write-VgoUtf8NoBomText -Path (Join-Path $outDir 'vibe-anti-proxy-goal-drift-tier-a-pilot-gate.json') -Content ($artifact | ConvertTo-Json -Depth 60)
    $md = @(
        '# VCO Anti-Proxy-Goal-Drift Tier A Pilot',
        '',
        ('- Recommendation: **{0}**' -f $artifact.decision.recommendation),
        ('- Red-team recall: `{0}`' -f $artifact.metrics.red_team_recall),
        ('- Specialization false-positive rate: `{0}`' -f $artifact.metrics.specialization_false_positive_rate),
        ('- Tier agreement rate: `{0}`' -f $artifact.metrics.tier_agreement_rate),
        ('- Human usability evidence present: `{0}`' -f $artifact.metrics.human_usability_evidence_present)
    ) -join [Environment]::NewLine
    Write-VgoUtf8NoBomText -Path (Join-Path $outDir 'vibe-anti-proxy-goal-drift-tier-a-pilot-gate.md') -Content $md
}

Write-Host ("[PASS] Tier A pilot executed. Recommendation: {0}" -f $decision) -ForegroundColor Green
