param(
 [string]$WinForms='D:\VERA\VeraDesktopPreview\0.1.0\VeraDesktop.exe',
 [string]$Tauri='D:\VERA\v-e-r-a-tauri-20261028\clients\tauri-prototype\src-tauri\target\release\vera-desktop.exe'
)
$ErrorActionPreference='Stop'
$results=@()
foreach($row in @(@{name='WinForms';exe=$WinForms},@{name='Tauri';exe=$Tauri})){
 if(!(Test-Path $row.exe)){throw "Missing executable: $($row.name)"}
 for($i=1;$i -le 3;$i++){
  $started=Get-Date
  $sw=[Diagnostics.Stopwatch]::StartNew()
  $proc=Start-Process -FilePath $row.exe -WorkingDirectory (Split-Path $row.exe) -PassThru
  try{
   Start-Sleep -Seconds 3
   $sw.Stop();$proc.Refresh()
   $running= -not $proc.HasExited
   $self=Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
   $processes=@()
   if($self){$processes=@($self)}
   $all=Get-CimInstance Win32_Process | Where-Object {$_.CreationDate -ge $started.AddSeconds(-1)}
   $known=@($proc.Id)
   for($depth=0;$depth -lt 8;$depth++){
    $children=@($all | Where-Object {$known -contains $_.ParentProcessId -and $known -notcontains $_.ProcessId})
    if(!$children.Count){break}
    foreach($c in $children){$known+= $c.ProcessId}
   }
   $childProc=@($known | Where-Object {$_ -ne $proc.Id} | ForEach-Object {Get-Process -Id $_ -ErrorAction SilentlyContinue})
   $processes+= $childProc
   $mem=($processes | Measure-Object -Property WorkingSet64 -Sum).Sum
   $private=($processes | Measure-Object -Property PrivateMemorySize64 -Sum).Sum
   $results+= [pscustomobject]@{Framework=$row.name;Run=$i;Launched=$running;ProcessCount=$processes.Count;WindowHandle=[string]$proc.MainWindowHandle;SnapshotSeconds=3;WorkingSetMB=[math]::Round($mem/1MB,1);PrivateMB=[math]::Round($private/1MB,1);ExeBytes=(Get-Item $row.exe).Length}
  }finally{
   if(!$proc.HasExited){Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue}
   Start-Sleep -Milliseconds 400
  }
 }
}
$results | Format-Table -AutoSize
$dest='D:\VERA\VeraDesktopPreview\comparison-20261028.csv'
$results | Export-Csv $dest -NoTypeInformation
Write-Output ('CSV='+$dest)
