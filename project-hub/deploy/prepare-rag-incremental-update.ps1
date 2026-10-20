$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$outDir = Join-Path $repoRoot 'release-output'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Push-Location (Join-Path $repoRoot 'customer-service-system/customer-service-system/frontend')
try {
    & npm.cmd run build -- --base=/ecommerce/
    if ($LASTEXITCODE -ne 0) { throw 'Ecommerce frontend build failed.' }
} finally { Pop-Location }

$sourcePaths = @(
    'rag-assistant/backend/app/database.py',
    'rag-assistant/backend/app/ecommerce_sync_jobs.py',
    'rag-assistant/backend/app/main.py',
    'rag-assistant/backend/app/config.py',
    'rag-assistant/backend/app/rag/pipeline.py',
    'rag-assistant/backend/app/rag/ecommerce_index.py',
    'rag-assistant/backend/app/rag/embedding_cache.py',
    'customer-service-system/customer-service-system/backend/app/api/semantic.py',
    'customer-service-system/customer-service-system/backend/app/services/semantic_search_service.py',
    'customer-service-system/customer-service-system/frontend/src/views/SemanticSearch.vue'
)
$hashes = [ordered]@{}
$sha = [System.Security.Cryptography.SHA256]::Create()
try {
    foreach ($relativePath in $sourcePaths) {
        $content = [System.IO.File]::ReadAllText((Join-Path $repoRoot $relativePath)).Replace("`r`n", "`n")
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
        $hashes[$relativePath] = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-', '').ToLowerInvariant()
    }
} finally { $sha.Dispose() }
$manifest = @{ format = 1; release = 'rag-incremental-sync'; source_hashes = $hashes }
$manifestPath = Join-Path $outDir 'rag-incremental-sync-manifest.json'
[System.IO.File]::WriteAllText($manifestPath, ($manifest | ConvertTo-Json -Depth 5), [System.Text.UTF8Encoding]::new($false))

$archive = Join-Path $outDir 'rag-incremental-sync-update.tar.gz'
& tar.exe -czf $archive -C $repoRoot `
    'customer-service-system/customer-service-system/frontend/dist' `
    'release-output/rag-incremental-sync-manifest.json'
if ($LASTEXITCODE -ne 0) { throw 'Archive creation failed.' }
Write-Host "Update: $archive"
Write-Host 'Commit and push all source changes, then pull them on the server before applying this archive.'
