param(
    [switch]$WriteArtifacts,
    [switch]$IncludeMirrorGates,
    [switch]$SkipInventory,
    [switch]$SkipTmpPurge,
    [switch]$SkipLocalExcludeInstall,
    [switch]$SkipNodeAudit,
    [switch]$SkipNodeCleanup,
    [switch]$ApplyManagedNodeCleanup
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '..\common\vibe-governance-helpers.ps1')

function Invoke-VgoPhaseEndStep {
    param(
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [string]$Kind,
        [Parameter(Mandatory)] [scriptblock]$Action,
        [Parameter(Mandatory)] [System.Collections.Generic.List[object]]$Steps
    )

    try {
        & $Action | Out-Null
        $Steps.Add([pscustomobject]@{
                name = $Name
                kind = $Kind
                status = 'passed'
            }) | Out-Null
    } catch {
        $Steps.Add([pscustomobject]@{
                name = $Name
                kind = $Kind
                status = 'failed'
                error = $_.Exception.Message
            }) | Out-Null
        throw
    }
}

$context = Get-VgoGovernanceContext -ScriptPath $PSCommandPath -EnforceExecutionContext
$repoRoot = $context.repoRoot
$steps = [System.Collections.Generic.List[object]]::new()
$gateArgs = @()
if ($WriteArtifacts) {
    $gateArgs += '-WriteArtifacts'
}

if (-not $SkipTmpPurge) {
    $tmpRoot = Join-Path $repoRoot '.tmp'
    $removedTmp = Test-Path -LiteralPath $tmpRoot
    if ($removedTmp) {
        Remove-Item -LiteralPath $tmpRoot -Recurse -Force
    }
    $steps.Add([pscustomobject]@{
            name = 'tmp-purge'
            kind = 'cleanup'
            status = 'passed'
            removed = $removedTmp
        }) | Out-Null
} else {
    $steps.Add([pscustomobject]@{
            name = 'tmp-purge'
            kind = 'cleanup'
            status = 'skipped'
        }) | Out-Null
}

if (-not $SkipLocalExcludeInstall) {
    Invoke-VgoPhaseEndStep -Name 'install-local-worktree-excludes' -Kind 'governance' -Steps $steps -Action {
        & (Join-Path $repoRoot 'scripts\governance\install-local-worktree-excludes.ps1')
    }
} else {
    $steps.Add([pscustomobject]@{
            name = 'install-local-worktree-excludes'
            kind = 'governance'
            status = 'skipped'
        }) | Out-Null
}

if (-not $SkipInventory) {
    Invoke-VgoPhaseEndStep -Name 'export-repo-cleanliness-inventory' -Kind 'governance' -Steps $steps -Action {
        & (Join-Path $repoRoot 'scripts\governance\export-repo-cleanliness-inventory.ps1') @gateArgs
    }
} else {
    $steps.Add([pscustomobject]@{
            name = 'export-repo-cleanliness-inventory'
            kind = 'governance'
            status = 'skipped'
        }) | Out-Null
}

Invoke-VgoPhaseEndStep -Name 'vibe-repo-cleanliness-gate' -Kind 'verify' -Steps $steps -Action {
    & (Join-Path $repoRoot 'scripts\verify\vibe-repo-cleanliness-gate.ps1') @gateArgs
}

Invoke-VgoPhaseEndStep -Name 'vibe-output-artifact-boundary-gate' -Kind 'verify' -Steps $steps -Action {
    & (Join-Path $repoRoot 'scripts\verify\vibe-output-artifact-boundary-gate.ps1') @gateArgs
}

if ($IncludeMirrorGates) {
    Invoke-VgoPhaseEndStep -Name 'vibe-mirror-edit-hygiene-gate' -Kind 'verify' -Steps $steps -Action {
        & (Join-Path $repoRoot 'scripts\verify\vibe-mirror-edit-hygiene-gate.ps1') @gateArgs
    }

    Invoke-VgoPhaseEndStep -Name 'vibe-nested-bundled-parity-gate' -Kind 'verify' -Steps $steps -Action {
        & (Join-Path $repoRoot 'scripts\verify\vibe-nested-bundled-parity-gate.ps1') @gateArgs
    }

    Invoke-VgoPhaseEndStep -Name 'vibe-version-packaging-gate' -Kind 'verify' -Steps $steps -Action {
        & (Join-Path $repoRoot 'scripts\verify\vibe-version-packaging-gate.ps1') @gateArgs
    }
}

if (-not $SkipNodeAudit) {
    Invoke-VgoPhaseEndStep -Name 'Invoke-NodeProcessAudit' -Kind 'governance' -Steps $steps -Action {
        if ($WriteArtifacts) {
            & (Join-Path $repoRoot 'scripts\governance\Invoke-NodeProcessAudit.ps1') -WriteMarkdown
        } else {
            & (Join-Path $repoRoot 'scripts\governance\Invoke-NodeProcessAudit.ps1')
        }
    }
} else {
    $steps.Add([pscustomobject]@{
            name = 'Invoke-NodeProcessAudit'
            kind = 'governance'
            status = 'skipped'
        }) | Out-Null
}

if (-not $SkipNodeCleanup) {
    Invoke-VgoPhaseEndStep -Name 'Invoke-NodeZombieCleanup' -Kind 'governance' -Steps $steps -Action {
        if ($ApplyManagedNodeCleanup) {
            & (Join-Path $repoRoot 'scripts\governance\Invoke-NodeZombieCleanup.ps1') -Apply
        } else {
            & (Join-Path $repoRoot 'scripts\governance\Invoke-NodeZombieCleanup.ps1')
        }
    }
} else {
    $steps.Add([pscustomobject]@{
            name = 'Invoke-NodeZombieCleanup'
            kind = 'governance'
            status = 'skipped'
        }) | Out-Null
}

[pscustomobject]@{
    generated_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    repo_root = $repoRoot
    write_artifacts = [bool]$WriteArtifacts
    include_mirror_gates = [bool]$IncludeMirrorGates
    apply_managed_node_cleanup = [bool]$ApplyManagedNodeCleanup
    steps = @($steps)
} | ConvertTo-Json -Depth 8
