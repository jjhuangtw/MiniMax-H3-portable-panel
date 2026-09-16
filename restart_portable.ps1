$ErrorActionPreference = 'Stop'
$portablePython = Join-Path $PSScriptRoot 'python_embeded\python.exe'
$listeners = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in 7860,8188 })
$processes = @()
foreach ($listener in $listeners) {
    $candidate = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
    $scriptName = if ($listener.LocalPort -eq 7860) { 'webui\.py' } else { 'main\.py' }
    if ($candidate.ExecutablePath -ne $portablePython -or $candidate.CommandLine -notmatch $scriptName) {
        throw "Port $($listener.LocalPort) belongs to another app. Nothing was stopped."
    }
    $processes += $candidate.ProcessId
}
if ($listeners.LocalPort -contains 8188) {
    $queue = Invoke-RestMethod 'http://127.0.0.1:8188/queue' -TimeoutSec 5
    if ($queue.queue_running.Count -gt 0 -or $queue.queue_pending.Count -gt 0) {
        throw 'Generation is running or queued. Wait until it finishes, then restart. Nothing was stopped.'
    }
}
foreach ($processIdToStop in ($processes | Select-Object -Unique)) {
    Stop-Process -Id $processIdToStop
}
Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONIOENCODING = 'utf-8'
& $portablePython (Join-Path $PSScriptRoot 'webui.py')
