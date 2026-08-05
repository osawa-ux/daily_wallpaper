$repo = "$HOME\daily_wallpaper"
$python = "$repo\.venv\Scripts\python.exe"
$user = "$env:USERDOMAIN\$env:USERNAME"

$action = New-ScheduledTaskAction `
    -Execute $python `
    -Argument "main.py" `
    -WorkingDirectory $repo

$daily = New-ScheduledTaskTrigger -Daily -At 9am
$logon = New-ScheduledTaskTrigger -AtLogOn -User $user

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

Register-ScheduledTask `
    -TaskName "DailyQuoteWallpaper" `
    -Action $action `
    -Trigger @($daily, $logon) `
    -Settings $settings `
    -Description "Daily minimal quote wallpaper generator (9:00 daily + at logon catch-up)"
