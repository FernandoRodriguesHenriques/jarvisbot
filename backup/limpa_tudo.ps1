$keep = @("CADJPYm_M15.csv","NZDCADm_M15.csv","GBPNZDm_M15.csv","GBPCADm_M15.csv","CADCHFm_M15.csv","NZDJPYm_M15.csv","AUDCADm_M15.csv","EURAUDm_M15.csv","HK50m_M15.csv")
Get-ChildItem data | Where-Object { $keep -notcontains $_.Name } | Remove-Item -Force
Write-Host "Limpeza feita!"
Get-ChildItem data | Format-Table Name, Length, LastWriteTime
