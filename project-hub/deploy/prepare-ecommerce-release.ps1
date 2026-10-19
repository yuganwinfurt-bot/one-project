# 在 Windows 本机运行。构建页面并打包图片；不会上传或重启服务器。
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$outDir = Join-Path $repoRoot 'release-output'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$builds = @(
    @{ Path = 'project-hub'; BuildArgs = @() },
    @{ Path = 'rag-assistant/frontend'; BuildArgs = @() },
    @{ Path = 'customer-service-system/customer-service-system/frontend'; BuildArgs = @('--', '--base=/ecommerce/') }
)
foreach ($build in $builds) {
    Push-Location (Join-Path $repoRoot $build.Path)
    try {
        if (-not (Test-Path -LiteralPath 'node_modules')) {
            throw "Missing node_modules in $($build.Path). Run npm.cmd ci there first."
        }
        $buildArgs = $build.BuildArgs
        & npm.cmd run build @buildArgs
        if ($LASTEXITCODE -ne 0) { throw "Build failed: $($build.Path)" }
    } finally { Pop-Location }
}

$archive = Join-Path $outDir 'ecommerce-site-assets.tar.gz'
& tar.exe -czf $archive -C $repoRoot `
    'project-hub/dist' `
    'rag-assistant/frontend/dist' `
    'customer-service-system/customer-service-system/frontend/dist' `
    'customer-service-system/customer-service-system/backend/uploads'
if ($LASTEXITCODE -ne 0) { throw 'Archive creation failed.' }
Write-Host "Release assets: $archive"
Write-Host 'Database is separate. Run export-ecommerce-database.py with the ecommerce backend Python.'
