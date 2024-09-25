Push-Location $PSScriptRoot
try {
    while ($true) {
        python main.py
        Start-Sleep -Seconds 295
    }
} finally {
    Pop-Location
}