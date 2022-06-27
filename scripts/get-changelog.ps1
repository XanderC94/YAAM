param (
    [Parameter(Mandatory=$true)]
    [System.String]$tag
)

function Get-Changelog {
    param (
        [Parameter(Mandatory=$true)]
        [System.String]$tag
    )

    $version="0.0.0"
    
    $tag_pattern="v?(?<major>[0-9]+)\.(?<minor>[0-9]+)\.(?<bugfix>[0-9]+)(?>-(?<type>alpha|beta))?(?>-(?<revision>.*))?"
    $match_result=[regex]::Matches($tag, $tag_pattern)[0]
    
    $changelog="# Automated build release"
    
    if ($match_result.success)
    {
        $version=[string]::Format(
            "{0}.{1}.{2}", 
            $match_result.Groups['major'].value, 
            $match_result.Groups['minor'].value,
            $match_result.Groups['bugfix'].value
        )

        

        $changelog_file = "./changelogs/v$version.md"
        if (Test-Path -Path $changelog_file)
        {
            $changelog=Get-Content -Raw -Path $changelog_file
        }
        else 
        {
            $changelog=$changelog+" "+$tag
        }
        
    }
    else {
        $changelog=$changelog+"."
    }

    return $changelog
}

return Get-Changelog -tag $tag
