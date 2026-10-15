$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$desktop = [Environment]::GetFolderPath('Desktop')
$shell = New-Object -ComObject WScript.Shell
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw "Install project dependencies first: $python"
}

$shortcutName = (-join @([char]0x542f, [char]0x52a8)) + ' yugan-agent.lnk'
$linkPath = Join-Path $desktop $shortcutName
$link = $shell.CreateShortcut($linkPath)
$link.TargetPath = $python
$link.Arguments = '-m yugan_agent serve --port 8020 --open-browser'
$link.WorkingDirectory = $projectRoot
$link.IconLocation = $python + ',0'
$link.Description = 'Start yugan-agent and open the browser; close the console to stop it.'
$link.Save()
Write-Output $linkPath
