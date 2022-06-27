[CmdletBinding(DefaultParameterSetName='default')]
param (
    [Parameter(Mandatory=$true)]
    [System.String]$tag,
    # [Parameter(Mandatory=$true)]
    [System.String]$revision='0',
    [Parameter(ParameterSetName='default')]
    # [Parameter(ParameterSetName='short')]
    # [Parameter(ParameterSetName='complete')]
    [Parameter(Mandatory=$false, ParameterSetName='short')]
    [switch]$short,
    [Parameter(Mandatory=$false, ParameterSetName='complete')]
    [switch]$complete
)

function Get-Version {
    param (
        # [Parameter(Mandatory=$true)]
        # [System.String]$tag,
        # [Parameter(Mandatory=$true)]
        # [System.String]$revision,
        # [switch]$short,
        # [switch]$complete
    )

    $version="0.0.0"

    if (-not $short)
    {
        $version+=".0"
    }
    
    $tag_pattern="v?(?<major>[0-9]+)\.(?<minor>[0-9]+)\.(?<bugfix>[0-9]+)(?>-(?<type>alpha|beta))?(?>-(?<test>test))?(?>-(?<revision>.*))?"
    $match_result=[regex]::Matches($tag, $tag_pattern)[0]

    if ($match_result.success)
    {
        $type="0"
        
        if ($match_result.groups["type"].value -eq "alpha")
        {
            $type="2"
        }
        elseif ($match_result.groups['type'].value -eq "beta")
        {
            $type="1"
        }
        
        $istest = $match_result.groups["test"].value.length -ge 0

        if ($istest)
        {
            $type="1"+$type
        }
        
        if ($short)
        {
            $version=[string]::Format(
                "{0}.{1}.{2}", 
                $match_result.Groups['major'].value, 
                $match_result.Groups['minor'].value,
                $match_result.Groups['bugfix'].value
            )
        }
        elseif ($complete)
        {
            $type=$match_result.groups["type"].value
            
            if ($type.length -ge 0)
            {
                $version=[string]::Format(
                    "{0}.{1}.{2}.{3}-{4}", 
                    $match_result.Groups['major'].value, 
                    $match_result.Groups['minor'].value,
                    $match_result.Groups['bugfix'].value,
                    $type + (&{ if ($istest) { "-test" } else { "" } }),
                    $revision
                )
            }
            else
            {
                $version=[string]::Format(
                    "{0}.{1}.{2}-{3}", 
                    $match_result.Groups['major'].value, 
                    $match_result.Groups['minor'].value,
                    $match_result.Groups['bugfix'].value,
                    $revision
                )
            }
        }
        else
        {
            $version=[string]::Format(
                "{0}.{1}.{2}.{3}", 
                $match_result.Groups['major'].value, 
                $match_result.Groups['minor'].value,
                $match_result.Groups['bugfix'].value,
                $type
            )
        }
    }
    
    return $version
}

return Get-Version #-tag $tag -revision $revision -short $short -complete $complete
