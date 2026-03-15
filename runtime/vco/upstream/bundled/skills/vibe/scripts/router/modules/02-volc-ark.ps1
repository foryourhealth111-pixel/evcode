$script:VolcArkDefaultBaseUrl = "https://ark.cn-beijing.volces.com/api/v3"

function Get-VolcArkBaseUrl {
    param([string]$Override)

    if ($Override) { return ([string]$Override).TrimEnd("/") }
    if ($env:ARK_BASE_URL) { return ([string]$env:ARK_BASE_URL).TrimEnd("/") }
    if ($env:VOLC_ARK_BASE_URL) { return ([string]$env:VOLC_ARK_BASE_URL).TrimEnd("/") }
    return $script:VolcArkDefaultBaseUrl
}

function Get-VolcArkApiKey {
    param([string]$EnvName = "ARK_API_KEY")

    $name = if ($EnvName) { [string]$EnvName } else { "ARK_API_KEY" }
    try {
        $val = [System.Environment]::GetEnvironmentVariable($name)
        if ($val) { return [string]$val }
    } catch { }

    return $null
}

function Get-VolcArkEmbeddingsEndpoint {
    param(
        [string]$BaseUrl,
        [string]$EndpointPath = "/embeddings/multimodal"
    )

    $base = Get-VolcArkBaseUrl -Override $BaseUrl
    if (-not $base) { return $null }

    $trimBase = ([string]$base).TrimEnd("/")
    $path = if ($EndpointPath) { [string]$EndpointPath } else { "/embeddings/multimodal" }
    $trimPath = $path.Trim()
    if (-not $trimPath.StartsWith("/")) { $trimPath = "/" + $trimPath }

    return ("{0}{1}" -f $trimBase, $trimPath)
}

function Get-VolcArkEmbeddingsOutputVectors {
    param([object]$Response)

    if (-not $Response) { return @() }

    try {
        $data = @($Response.data)
        if ($data.Count -eq 0) { return @() }

        $hasIndex = $true
        try {
            $null = $data[0].index
        } catch {
            $hasIndex = $false
        }

        $rows = if ($hasIndex) { @($data | Sort-Object -Property index) } else { @($data) }

        $vectors = @()
        foreach ($row in $rows) {
            if (-not $row) { continue }
            if ($row.embedding) {
                $vectors += ,@($row.embedding)
                continue
            }

            # Tolerate alternate shapes: embedding.embedding, embedding.vector
            try {
                if ($row.embedding.embedding) {
                    $vectors += ,@($row.embedding.embedding)
                    continue
                }
            } catch { }
            try {
                if ($row.embedding.vector) {
                    $vectors += ,@($row.embedding.vector)
                    continue
                }
            } catch { }
        }

        if ($vectors.Count -eq 0) { return @() }
        return ,$vectors
    } catch {
        return @()
    }
}

function Invoke-VolcArkEmbeddingsCreate {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Model,
        [Parameter(Mandatory = $true)]
        [object]$InputItems,
        [int]$TimeoutMs = 2500,
        [string]$ApiKey,
        [string]$BaseUrl,
        [string]$EndpointPath = "/embeddings/multimodal",
        [string]$ApiKeyEnv = "ARK_API_KEY"
    )

    $resolvedApiKey = if ($ApiKey) { [string]$ApiKey } else { Get-VolcArkApiKey -EnvName $ApiKeyEnv }
    if (-not $resolvedApiKey) {
        return [pscustomobject]@{
            ok = $false
            abstained = $true
            reason = "missing_ark_api_key"
            status_code = $null
            latency_ms = 0
            vectors = @()
            response = $null
            error = $null
        }
    }

    $endpoint = Get-VolcArkEmbeddingsEndpoint -BaseUrl $BaseUrl -EndpointPath $EndpointPath
    if (-not $endpoint) {
        return [pscustomobject]@{
            ok = $false
            abstained = $true
            reason = "missing_ark_base_url"
            status_code = $null
            latency_ms = 0
            vectors = @()
            response = $null
            error = $null
        }
    }

    $timeoutSec = [Math]::Max(1, [int][Math]::Ceiling([double]$TimeoutMs / 1000.0))

    $body = [ordered]@{
        model = $Model
        input = $InputItems
    }

    $json = ($body | ConvertTo-Json -Depth 20 -Compress)

    $headers = @{
        "Authorization" = ("Bearer {0}" -f $resolvedApiKey)
        "Content-Type"  = "application/json"
    }

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $resp = Invoke-RestMethod -Uri $endpoint -Method Post -Headers $headers -Body $json -TimeoutSec $timeoutSec
        $sw.Stop()
        $vectors = Get-VolcArkEmbeddingsOutputVectors -Response $resp
        return [pscustomobject]@{
            ok = $true
            abstained = $false
            reason = "ok"
            status_code = 200
            latency_ms = [int]$sw.ElapsedMilliseconds
            vectors = @($vectors)
            response = $resp
            error = $null
        }
    } catch {
        $sw.Stop()
        $message = $_.Exception.Message
        $status = $null
        try {
            if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
                $status = [int]$_.Exception.Response.StatusCode
            }
        } catch { }

        return [pscustomobject]@{
            ok = $false
            abstained = $true
            reason = "ark_http_error"
            status_code = $status
            latency_ms = [int]$sw.ElapsedMilliseconds
            vectors = @()
            response = $null
            error = $message
        }
    }
}
