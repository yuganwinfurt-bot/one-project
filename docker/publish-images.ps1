#requires -Version 5.1
param()

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$projectRoot = Split-Path -Parent $PSScriptRoot
$script:publishJob = $null
$services = @('yugan-agent', 'rag-assistant', 'ecommerce', 'project-hub', 'web-gateway')

function Find-DockerExecutable {
    $dockerCommand = Get-Command docker.exe -ErrorAction SilentlyContinue
    if ($dockerCommand) { return $dockerCommand.Source }
    $candidates = @(
        (Join-Path $env:LOCALAPPDATA 'Programs/DockerDesktop/resources/bin/docker.exe'),
        (Join-Path $env:ProgramFiles 'Docker/Docker/resources/bin/docker.exe')
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    }
    throw '没有找到 Docker Desktop。请先安装并打开 Docker Desktop。'
}

# Runs separately so building/pushing cannot freeze the window.
$publishTask = {
    param($rootPath, $repository, $version, $rebuild, $dockerExecutable)
    $ErrorActionPreference = 'Stop'
    $env:PATH = (Split-Path -Parent $dockerExecutable) + [IO.Path]::PathSeparator + $env:PATH
    $env:DOCKER_HUB_REPOSITORY = $repository
    $env:IMAGE_VERSION = $version
    $env:BUILDKIT_PROGRESS = 'plain'
    $env:COMPOSE_ANSI = 'never'
    $env:COMPOSE_PROGRESS = 'plain'
    $env:DOCKER_CONTEXT = 'desktop-linux'
    Set-Location -LiteralPath $rootPath
    $publishCompose = Join-Path $rootPath 'compose.publish.yaml'
    $serviceNames = @('yugan-agent', 'rag-assistant', 'ecommerce', 'project-hub', 'web-gateway')

    function Invoke-Docker {
        param([string[]]$DockerArguments)
        $previousPreference = $ErrorActionPreference
        try {
            # Windows PowerShell treats native stderr as ErrorRecord objects.
            $ErrorActionPreference = 'Continue'
            & $dockerExecutable @DockerArguments 2>&1 | ForEach-Object { $_.ToString() }
            $commandExitCode = $LASTEXITCODE
        }
        finally {
            $ErrorActionPreference = $previousPreference
        }
        if ($commandExitCode -ne 0) {
            throw ('Docker 操作失败，退出码：' + $commandExitCode + '。请查看上面的具体提示。')
        }
    }

    try {
        Write-Output ('发布仓库：' + $repository)
        Write-Output ('发布版本：' + $version)
        Write-Output '正在连接 Docker Desktop 的 Linux 引擎...'
        Invoke-Docker -DockerArguments @('info', '--format', '{{.OSType}}/{{.Architecture}}')
        Invoke-Docker -DockerArguments @('compose', 'version', '--short')

        if ($rebuild) {
            # Buildx on Windows also needs the host proxy for registry authentication.
            # Respect explicit process settings; otherwise inherit the Windows proxy.
            if (-not $env:HTTP_PROXY -and -not $env:HTTPS_PROXY) {
                try {
                    $probeAddress = [Uri]'https://auth.docker.io/token'
                    $systemProxy = [Net.WebRequest]::GetSystemWebProxy()
                    $proxyAddress = $systemProxy.GetProxy($probeAddress)
                    if ($proxyAddress -and $proxyAddress.AbsoluteUri -ne $probeAddress.AbsoluteUri) {
                        $env:HTTP_PROXY = $proxyAddress.AbsoluteUri
                        $env:HTTPS_PROXY = $proxyAddress.AbsoluteUri
                        Write-Output '构建进程已继承 Windows 代理设置。'
                    }
                }
                catch {
                    Write-Output '无法读取 Windows 代理，将使用 Docker 当前网络设置。'
                }
            }
            Write-Output '正在重新构建全部镜像，首次构建可能需要较长时间...'
            Invoke-Docker -DockerArguments @('compose', '--file', $publishCompose, 'build')
            foreach ($serviceName in $serviceNames) {
                $builtImage = $repository + ':' + $serviceName + '-' + $version
                $localImage = 'one-project/' + $serviceName + ':local'
                Invoke-Docker -DockerArguments @('image', 'tag', $builtImage, $localImage)
            }
        }
        else {
            Write-Output '检查本机的五个已构建镜像...'
            foreach ($serviceName in $serviceNames) {
                $sourceImage = 'one-project/' + $serviceName + ':local'
                Write-Output ('检查：' + $sourceImage)
                Invoke-Docker -DockerArguments @('image', 'inspect', '--format', '{{.Id}}', $sourceImage)
            }
            foreach ($serviceName in $serviceNames) {
                $sourceImage = 'one-project/' + $serviceName + ':local'
                $targetImage = $repository + ':' + $serviceName + '-' + $version
                Write-Output ('添加发布名称：' + $targetImage)
                Invoke-Docker -DockerArguments @('image', 'tag', $sourceImage, $targetImage)
            }
        }

        Write-Output '正在上传全部五个镜像，使用 Docker Desktop 当前登录的账号...'
        Invoke-Docker -DockerArguments @('compose', '--file', $publishCompose, 'push')
        Write-Output '全部五个镜像已上传成功。'
        Write-Output ('仓库地址：https://hub.docker.com/r/' + $repository + '/tags')
    }
    catch {
        Write-Output ('发布未完成：' + $_.Exception.Message)
        Write-Output '权限不足：请确认 Docker Desktop 已登录，仓库前缀是你自己的 Docker ID。'
        Write-Output '镜像缺失：勾选“发布前重新构建”，再重新发布。'
        Write-Output '如果中途上传失败，部分镜像可能已经上传；修复后可以重试。'
        throw
    }
}

$form = New-Object System.Windows.Forms.Form
$form.Text = 'one-project 镜像发布'
$form.ClientSize = New-Object System.Drawing.Size(840, 650)
$form.MinimumSize = New-Object System.Drawing.Size(760, 560)
$form.StartPosition = 'CenterScreen'
$form.Font = New-Object System.Drawing.Font('Microsoft YaHei UI', 10)
$form.AutoScaleMode = [System.Windows.Forms.AutoScaleMode]::Dpi

$heading = New-Object System.Windows.Forms.Label
$heading.Text = '一次发布全部五个镜像到同一个 Docker Hub 仓库'
$heading.SetBounds(20, 15, 790, 28)
$form.Controls.Add($heading)

$repositoryLabel = New-Object System.Windows.Forms.Label
$repositoryLabel.Text = '镜像仓库'
$repositoryLabel.SetBounds(20, 57, 100, 26)
$form.Controls.Add($repositoryLabel)

$repositoryBox = New-Object System.Windows.Forms.TextBox
$repositoryBox.Text = 'yuganwinfurt/one-project'
$repositoryBox.SetBounds(125, 54, 685, 30)
$repositoryBox.Anchor = 'Top, Left, Right'
$form.Controls.Add($repositoryBox)

$versionLabel = New-Object System.Windows.Forms.Label
$versionLabel.Text = '版本标签'
$versionLabel.SetBounds(20, 101, 100, 26)
$form.Controls.Add($versionLabel)

$versionBox = New-Object System.Windows.Forms.TextBox
$versionBox.Text = 'latest'
$versionBox.SetBounds(125, 98, 200, 30)
$form.Controls.Add($versionBox)

$versionHint = New-Object System.Windows.Forms.Label
$versionHint.Text = '同名版本会更新；保留旧版本时请填写新版本号。'
$versionHint.SetBounds(345, 102, 465, 26)
$versionHint.Anchor = 'Top, Left, Right'
$form.Controls.Add($versionHint)

$rebuildBox = New-Object System.Windows.Forms.CheckBox
$rebuildBox.Text = '发布前重新构建（修改代码后勾选）'
$rebuildBox.Checked = $false
$rebuildBox.SetBounds(20, 143, 650, 28)
$form.Controls.Add($rebuildBox)

$note = New-Object System.Windows.Forms.Label
$note.Text = '请先打开并登录 Docker Desktop。仓库公开或私有沿用 Docker Hub 设置。'
$note.SetBounds(20, 178, 790, 26)
$note.Anchor = 'Top, Left, Right'
$form.Controls.Add($note)

$publishButton = New-Object System.Windows.Forms.Button
$publishButton.Text = '发布全部五个镜像'
$publishButton.SetBounds(20, 215, 225, 40)
$form.Controls.Add($publishButton)

$statusLabel = New-Object System.Windows.Forms.Label
$statusLabel.Text = '准备就绪'
$statusLabel.SetBounds(265, 224, 545, 28)
$statusLabel.Anchor = 'Top, Left, Right'
$form.Controls.Add($statusLabel)

$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.SetBounds(20, 270, 790, 10)
$progressBar.Anchor = 'Top, Left, Right'
$form.Controls.Add($progressBar)

$logBox = New-Object System.Windows.Forms.TextBox
$logBox.Multiline = $true
$logBox.ReadOnly = $true
$logBox.ScrollBars = 'Both'
$logBox.WordWrap = $false
$logBox.MaxLength = 0
$logBox.SetBounds(20, 298, 790, 330)
$logBox.Anchor = 'Top, Bottom, Left, Right'
$form.Controls.Add($logBox)

function Add-PublishLog {
    param([string]$Message)
    if ($logBox.TextLength -gt 350000) {
        $logBox.Text = $logBox.Text.Substring($logBox.TextLength - 250000)
    }
    $logBox.AppendText($Message + [Environment]::NewLine)
    $logBox.SelectionStart = $logBox.TextLength
    $logBox.ScrollToCaret()
}

Add-PublishLog '默认发布本机已经构建好的五个镜像。'
Add-PublishLog '修改代码后，请勾选“发布前重新构建”，以便上传最新代码。'
foreach ($service in $services) {
    Add-PublishLog ('  yuganwinfurt/one-project:' + $service + '-latest')
}

$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 500
$timer.Add_Tick({
    if ($null -eq $script:publishJob) { return }
    try {
        $jobErrors = @()
        $messages = @(Receive-Job -Job $script:publishJob -ErrorAction SilentlyContinue -ErrorVariable jobErrors)
        foreach ($message in $messages) { Add-PublishLog -Message ([string]$message) }
        $jobState = $script:publishJob.State
        if ($jobState -in @('Completed', 'Failed', 'Stopped')) {
            foreach ($jobError in $jobErrors) { Add-PublishLog -Message ([string]$jobError) }
            if ($jobState -eq 'Completed') {
                $statusLabel.Text = '发布完成：五个镜像全部上传成功'
                $statusLabel.ForeColor = [Drawing.Color]::DarkGreen
            }
            else {
                $statusLabel.Text = '发布未完成，请查看下方提示后重试'
                $statusLabel.ForeColor = [Drawing.Color]::DarkRed
            }
            $timer.Stop()
            $progressBar.Style = 'Blocks'
            $progressBar.Value = 0
            Remove-Job -Job $script:publishJob -Force
            $script:publishJob = $null
            $publishButton.Enabled = $true
            $repositoryBox.Enabled = $true
            $versionBox.Enabled = $true
            $rebuildBox.Enabled = $true
        }
    }
    catch {
        Add-PublishLog -Message ('读取发布进度失败：' + $_.Exception.Message)
    }
})

$publishButton.Add_Click({
    try {
        $repository = $repositoryBox.Text.Trim()
        $version = $versionBox.Text.Trim()
        if ($repository -notmatch '^[a-z0-9][a-z0-9_-]*/[a-z0-9][a-z0-9_.-]*$') {
            throw '仓库格式应为：DockerHub用户名/仓库名，只能使用小写英文、数字及允许的分隔符。'
        }
        if ($version -notmatch '^[A-Za-z0-9_][A-Za-z0-9_.-]{0,95}$') {
            throw '版本号请使用 1 至 96 个英文、数字、点、下划线或横线，例如 latest 或 v1.0.0。'
        }
        if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'compose.publish.yaml') -PathType Leaf)) {
            throw '项目根目录缺少 compose.publish.yaml，请保留完整的发布工具文件。'
        }
        $dockerExecutable = Find-DockerExecutable
        $logBox.Clear()
        $statusLabel.Text = '正在发布，请等待...'
        $statusLabel.ForeColor = [Drawing.Color]::Black
        $publishButton.Enabled = $false
        $repositoryBox.Enabled = $false
        $versionBox.Enabled = $false
        $rebuildBox.Enabled = $false
        $progressBar.Style = 'Marquee'
        $script:publishJob = Start-Job -ScriptBlock $publishTask -ArgumentList $projectRoot, $repository, $version, ([bool]$rebuildBox.Checked), $dockerExecutable
        $timer.Start()
    }
    catch {
        $publishButton.Enabled = $true
        $repositoryBox.Enabled = $true
        $versionBox.Enabled = $true
        $rebuildBox.Enabled = $true
        $progressBar.Style = 'Blocks'
        $statusLabel.Text = '请处理提示后重试'
        $statusLabel.ForeColor = [Drawing.Color]::DarkRed
        [void][System.Windows.Forms.MessageBox]::Show($form, $_.Exception.Message, '发布提示', 'OK', 'Information')
    }
})

$form.Add_FormClosing({
    param($sender, $eventArguments)
    if ($null -ne $script:publishJob) {
        $eventArguments.Cancel = $true
        [void][System.Windows.Forms.MessageBox]::Show($form, '正在发布，请等待完成后再关闭窗口。', '发布进行中', 'OK', 'Information')
    }
})

try {
    [void]$form.ShowDialog()
}
finally {
    $timer.Dispose()
    $form.Dispose()
}
