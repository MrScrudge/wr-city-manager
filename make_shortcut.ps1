# Creates the shortcut "W&R City Manager" (fallback; the app makes it itself with wr_calc.py --make-links).
#   -Here          : next to the program (the app does this by itself)
#   -UpdateDesktop : with -Here: also renew the desktop shortcut if there is one
#   no flag        : onto the desktop (run it by hand); works with a OneDrive Desktop too
#   -Py <pythonw.exe> : the shortcut starts pythonw.exe with wr_calc.py — such a shortcut can be pinned to the taskbar
#                       (Windows does not pin shortcuts to .bat files); without it the shortcut starts the launcher .bat
param([switch]$Here, [switch]$UpdateDesktop, [string]$Py = '')
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
$calc = $PSScriptRoot
$cm = $calc                                  # the shortcut and exports live next to the program
$icon = Join-Path $calc 'assets\calc.ico'
$sh = New-Object -ComObject WScript.Shell

if (-not $Py) {                 # find the real pythonw.exe: ask Python where it lives (a Store alias is not taken)
    foreach ($t in @('py -3', 'python')) {
        try {
            $parts = $t.Split(' '); $exe = $parts[0]; $rest = @($parts | Select-Object -Skip 1)
            $out = & $exe @rest -c 'import sys;print(sys.executable)' 2>$null | Select-Object -First 1
            if ($out) {
                $w = Join-Path (Split-Path -Parent $out.Trim()) 'pythonw.exe'
                if (Test-Path $w) { $Py = $w; break }
            }
        } catch {}
    }
    if (-not $Py) {
        $c = Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python3*\pythonw.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($c) { $Py = $c.FullName }
    }
}

function Make-Link([string]$dir) {
    $lnk = Join-Path $dir 'W&R City Manager.lnk'
    $s = $sh.CreateShortcut($lnk)
    if ($Py -and (Test-Path $Py)) {
        $s.TargetPath = $Py
        $s.Arguments = '"' + (Join-Path $calc 'wr_calc.py') + '"'
        $s.WindowStyle = 1
    } else {
        $s.TargetPath = Join-Path $calc 'W&R City Manager.bat'
        $s.Arguments = ''
        $s.WindowStyle = 7      # the helper .bat starts minimized: no black window flashing
    }
    $s.WorkingDirectory = $calc
    if (Test-Path $icon) { $s.IconLocation = "$icon,0" }
    $s.Description = 'W&R City Manager — calculator over the game'
    $s.Save()
    $old = Join-Path $dir 'W&R Калькулятор.lnk'
    if (Test-Path $old) { Remove-Item $old -ErrorAction SilentlyContinue }      # our own shortcut under the old name
    return $lnk
}

if ($Here) {
    Make-Link $cm | Out-Null
    if ($UpdateDesktop) {
        $d = [Environment]::GetFolderPath('Desktop')
        if ((Test-Path (Join-Path $d 'W&R Калькулятор.lnk')) -or (Test-Path (Join-Path $d 'W&R City Manager.lnk'))) { Make-Link $d | Out-Null }
    }
} else {
    $lnk = Make-Link ([Environment]::GetFolderPath('Desktop'))
    Write-Host ''
    Write-Host "  Готово! Ярлик на робочому столі: $lnk"
    Write-Host '  Щоб закріпити на панелі задач: права кнопка на ярлику -> «Закріпити на панелі завдань»'
    Write-Host '  (у Windows 11 спершу «Показати більше параметрів»), або просто перетягни ярлик на панель задач.'
    Write-Host ''
}
