param (
    [Parameter(Mandatory=$true)]
    [System.String]$target
)
function Backup-Target {
    param (
        [Parameter(Mandatory=$true)]
        [System.String]$target
    )

    if (Test-Path -path "$target.bak")
    {
        Remove-Item -path "$target.bak" -force -recurse
        Write-Output "Cleared previous backup $target.bak"
    }
    
    if (Test-Path -path "$target")
    {
        Move-Item -path "$target" -destination "$target.bak" -force
        Write-Output "Created new backup of $target -> $target.bak"
    } 
}

return Backup-Target $target
