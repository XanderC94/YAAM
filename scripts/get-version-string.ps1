[CmdletBinding(DefaultParameterSetName='default')]
param (
    [Parameter(Mandatory=$true)]
    [System.String]$tag,
    # [Parameter(Mandatory=$true)]
    [System.String]$revision='HEAD',
    [Parameter(Mandatory=$false)][ValidateSet('short', 'windows', 'complete')]
    [string]$mode='complete'
)

function Get-Version-String {
    [CmdletBinding(DefaultParameterSetName='default')]
    param (
        [Parameter(Mandatory=$true)]
        [System.String]$tag,
        # [Parameter(Mandatory=$true)]
        [System.String]$revision='HEAD',
        [Parameter(Mandatory=$false)][ValidateSet('short', 'windows', 'complete')]
        [string]$mode='complete'
    )

    $short=$mode -eq 'short'
    $windows=$mode -eq 'windows'

    $version="0.0.0"

    $revision_count=[System.String]@(git rev-list --count $revision)

    if (-not ($revision_count -match "^\d+$"))
    {
        $revision_count="0"
    }

    $tag_pattern="v?(?<major>[0-9]+)\.(?<minor>[0-9]+)\.(?<bugfix>[0-9]+)?(?>-(?<release>alpha|beta|prerelease|preview|release))?(?>-(?<production>test))?"

    $match_result=[regex]::Matches($tag, $tag_pattern)[0]

    if ($match_result.success)
    {
        if ($short)
        {
            $version=[string]::Format(
                "{0}.{1}.{2}", 
                $match_result.Groups['major'].value, 
                $match_result.Groups['minor'].value,
                $match_result.Groups['bugfix'].value
            )
        }
        else
        {
            $version=[string]::Format(
                "{0}.{1}.{2}.{3}", 
                $match_result.Groups['major'].value, 
                $match_result.Groups['minor'].value,
                $match_result.Groups['bugfix'].value,
                $revision_count
            )
            
            if (-not $windows)
            {
                $release=$match_result.groups["release"].value
                
                if ($release.length -gt 0 -and $release -ne 'release')
                {
                    $version=[string]::Format("{0}-{1}", $version, $release)
                }
                
                $production=$match_result.groups["production"]
    
                if ($production.length -gt 0 -and $production -ne 'production')
                {
                    $version=[string]::Format("{0}-{1}", $version, $production)
                }
            }
        }
    }
    elseif (-not $short)
    {   
        $version=[string]::Format("{0}-{1}", $version, $revision_count)
    }
    
    return $version
}

return Get-Version-String -tag $tag -revision $revision -mode $mode
