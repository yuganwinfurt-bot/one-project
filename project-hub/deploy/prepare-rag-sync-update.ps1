# 只构建和打包本次需要的两个前端；Python 和 Agent 源码由 Git 更新。
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$outDir = Join-Path $repoRoot 'release-output'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$builds = @(
    @{ Path = 'rag-assistant/frontend'; BuildArgs = @() },
    @{ Path = 'customer-service-system/customer-service-system/frontend'; BuildArgs = @('--', '--base=/ecommerce/') }
)
foreach ($build in $builds) {
    Push-Location (Join-Path $repoRoot $build.Path)
    try {
        $buildArgs = $build.BuildArgs
        & npm.cmd run build @buildArgs
        if ($LASTEXITCODE -ne 0) { throw "Build failed: $($build.Path)" }
    } finally { Pop-Location }
}

$archive = Join-Path $outDir 'rag-sync-navigation-update.tar.gz'
& tar.exe -czf $archive -C $repoRoot `
    'rag-assistant/frontend/dist' `
    'customer-service-system/customer-service-system/frontend/dist'
if ($LASTEXITCODE -ne 0) { throw 'Archive creation failed.' }
Write-Host "Frontend update: $archive"
Write-Host 'Commit and push source changes before pulling on the server. Then upload this archive.'
