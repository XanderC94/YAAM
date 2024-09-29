param (
    [Parameter(Mandatory=$true)]
    [System.String]$tag
)

function Get-Changelog-String {
    param (
        [Parameter(Mandatory=$true)]
        [System.String]$tag
    )

    $version=[System.String]@(./scripts/get-version-string.ps1 -tag $tag -mode short)
    
    $changelog_file = "./changelogs/v$version.md"
    
    $changelog="# YAAM version $version"
    
    if (Test-Path -Path $changelog_file)
    {
        $changelog=Get-Content -Raw -Path $changelog_file
    }

    return $changelog
}

return Get-Changelog-String -tag $tag
