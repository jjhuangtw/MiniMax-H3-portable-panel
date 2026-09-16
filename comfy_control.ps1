param([ValidateSet('cancel', 'free')][string]$Action)
$ErrorActionPreference = 'Stop'
$comfy = 'http://127.0.0.1:8188'

function Show-Status {
    $queue = Invoke-RestMethod "$comfy/queue" -TimeoutSec 5
    $device = (Invoke-RestMethod "$comfy/system_stats" -TimeoutSec 5).devices[0]
    $usedGb = ($device.vram_total - $device.vram_free) / 1GB
    Write-Host ("VRAM used: {0:N1} / {1:N1} GB   running: {2}   queued: {3}" -f $usedGb, ($device.vram_total / 1GB), $queue.queue_running.Count, $queue.queue_pending.Count)
}

try {
    Invoke-RestMethod "$comfy/queue" -TimeoutSec 5 | Out-Null
} catch {
    Write-Host 'ComfyUI backend (port 8188) is not running. Nothing to do.'
    exit 1
}

if ($Action -eq 'cancel') {
    # Clear queued jobs first so the interrupt does not simply start the next one.
    Invoke-RestMethod "$comfy/queue" -Method Post -ContentType 'application/json' -Body '{"clear": true}' -TimeoutSec 10 | Out-Null
    Invoke-RestMethod "$comfy/interrupt" -Method Post -TimeoutSec 10 | Out-Null
    Write-Host 'Cancel sent: queued jobs cleared, current job interrupted (it stops after the current step).'
} else {
    $queue = Invoke-RestMethod "$comfy/queue" -TimeoutSec 5
    if ($queue.queue_running.Count -gt 0 -or $queue.queue_pending.Count -gt 0) {
        Write-Host 'A job is still running or queued. Run cancel_generation.bat first, or wait for it to finish.'
        Show-Status
        exit 1
    }
    Invoke-RestMethod "$comfy/free" -Method Post -ContentType 'application/json' -Body '{"unload_models": true, "free_memory": true}' -TimeoutSec 30 | Out-Null
    Start-Sleep -Seconds 2
    Write-Host 'All models unloaded and cache freed. The next generation will reload models.'
}
Show-Status
