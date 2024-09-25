[CmdletBinding()]
param (
    [Parameter()]
    [int]
    $MinuteInterval = 5
)
Push-Location $PSScriptRoot
try {
    while ($true) {
        $current_time = Get-Date
        $timeParams = @{
            Year   = $current_time.Year
            Month  = $current_time.Month
            Day    = $current_time.Day
            Hour   = $current_time.Hour
            Minute = [Math]::Truncate($current_time.Minute / $MinuteInterval) * $MinuteInterval
            Second = 0
        }
        $timeToWait = Get-Date @timeParams
        $timeToWait = $timeToWait.AddMinutes($MinuteInterval)
        $durationToWait = $timeToWait - ((Get-Date))
        Write-Host "Waiting until $($timeToWait.ToString('HH\:mm\:ss'))" -ForegroundColor Yellow
        Start-Sleep -Seconds ([Math]::Round($durationToWait.TotalSeconds))
        $datetimeString = $timeToWait.ToString('s')
        python main.py $datetimeString
    }
} finally {
    Pop-Location
}