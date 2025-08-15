param (
    [System.String]$projectdir
)

function Find-PythonPath {
    $pythonpath = ""

    try
    {
        $pythonpath = Get-Path $env:PYTHONPATH
        $pythonpathexists = $true
    }
    catch
    {
        $pythonpathexists = $false
        $pythonpath = ""
    }

    if (-not $pythonpathexists)
    {
        $foundlings=@(where.exe "python")

        if ($foundlings.Length -gt 0)
        {
            foreach ($path in $foundlings) 
            {
                if ((Test-Path -path $projectdir -PathType Container) -and ($path.StartsWith($projectdir)))
                {
                    # VENV...
                    $path=@(Split-Path -Path $path -Parent)
                }
                
                $parent=@(Split-Path -Path $path -Parent)

                if (Test-Path -Path "$parent/Lib")
                {
                    $pythonpath=$parent
                    break
                }
            }
        }
    }

    return $pythonpath
}

return Find-PythonPath