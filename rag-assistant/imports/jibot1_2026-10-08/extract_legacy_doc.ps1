$ErrorActionPreference = 'Stop'
$root = 'D:\one project\rag-assistant\imports\jibot1_2026-10-08'
$manifest = Get-Content -LiteralPath (Join-Path $root 'archive_members.json') -Raw -Encoding utf8 | ConvertFrom-Json
$docs = @($manifest | Where-Object { $_.status -eq '等待旧版Word文字提取' })
$queue = @()
$word = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    foreach ($item in $docs) {
        $document = $null
        try {
            $document = $word.Documents.Open($item.extracted_path, $false, $true, $false)
            $text = [string]$document.Content.Text
            $text = [regex]::Replace($text, '[\x00-\x08\x0B\x0C\x0E-\x1F]', '').Replace("`r", "`n")
            if ([string]::IsNullOrWhiteSpace($text)) { throw ('未读出内容：' + $item.name) }
            $base = [IO.Path]::GetFileNameWithoutExtension($item.extracted_path)
            $docxPath = Join-Path (Join-Path $root 'extracted') ($base + '_converted.docx')
            $document.SaveAs2($docxPath, 16)
            $target = Join-Path (Join-Path $root 'prepared') ($base + '（DOC文字提取）.md')
            $content = '# ' + $item.name + "`n`n原始来源：" + $item.source + "`n`n提取范围：正文和表格文字。原文中的图片需另行查看原文件。`n`n" + $text
            [IO.File]::WriteAllText($target, $content, [Text.UTF8Encoding]::new($false))
            $kb = 'c0077d246def4753bc5465e919510b52'
            if ($item.source -match '舵机知识') { $kb = 'f75567ffdb404490bda53d8820cedfa8' }
            $queue += @{path=$target; source=$item.source; knowledge_base_id=$kb}
            Write-Output ('已提取：' + $base + '，字符数：' + $text.Length)
        } finally {
            if ($null -ne $document) { $document.Close(0); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($document) }
        }
    }
} finally {
    if ($null -ne $word) { $word.Quit(); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) }
}
$json = ConvertTo-Json -InputObject $queue -Depth 5
[IO.File]::WriteAllText((Join-Path $root 'legacy_doc_queue.json'), $json, [Text.UTF8Encoding]::new($false))
