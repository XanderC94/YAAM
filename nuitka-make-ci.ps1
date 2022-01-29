param (
    [System.String]$mode="standalone",
    [System.String]$compiler="msvc",
    [switch]$lto,
    [Parameter(Mandatory=$true)]
    [System.String]$tag,
    [Parameter(Mandatory=$true)]
    [System.String]$revision
)

if (-not($mode -eq "onefile" -or $mode -eq "standalone"))
{
    Write-Error "Invalid make mode. Choose [onefile, standalone]."
    exit 0
}

if (-not($compiler -eq "msvc" -or $compiler -eq "mingw64"))
{
    Write-Error "Invalid compiler mode. Choose [msvc, mingw64]."
    exit 0
}

$tag_pattern="v(?<major>[0-9]+)\.(?<minor>[0-9]+)\.(?<bugfix>[0-9]+)(?>-(?<type>alpha|beta))?(?>-(?<revision>.*))?"
$match_result=[regex]::Matches($tag, $tag_pattern)[0]

$version="0.0.0.0"

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

    $version=[string]::Format(
        "{0}.{1}.{2}.{3}", 
        $match_result.Groups['major'].value, 
        $match_result.Groups['minor'].value,
        $match_result.Groups['bugfix'].value,
        $type
    )
}

Write-Output "YAAM $tag-$revision ($version)"

$root=$PSScriptRoot

$product_name="Yet Another Addon Manager"
$company_name="https://github.com/XanderC94"
$description="YAAM-$tag-$revision"
$icon_path="res/icon/yaam.ico"
$template_dir="res/template"
$defaults_dir="res/default"
$output_dir="bin/$mode/$compiler"
$target_name="yaam"
$entrypoint_name="main"
$entrypoint="src/$entrypoint_name.py"

# create output dir if doesn't exist
if (-not(Test-Path -path "$root/$output_dir"))
{
    New-Item -path "$root/$output_dir" -force -itemtype "directory" | Out-Null
}

# Load manifest template and write in bin folder
# Then embed the manifest into the application executable
$manifest = Get-Content -raw -path "$root/$template_dir/MANIFEST" | ConvertFrom-Json
$manifest.version = $tag
$manifest.revision = $revision
$manifest | ConvertTo-Json -depth 32 | Set-Content -path "$root/$output_dir/MANIFEST" -force

$params = @(
    "--$mode",
    # "--$compiler"
    (&{ if ($compiler -eq "msvc") { "--$compiler=14.2" } else { "--$compiler" } }),
    (&{ if ($lto -eq $true) { "--lto=yes" } else { "" } }),
    "--plugin-enable=pylint-warnings",
    "--include-module=win32com.gen_py",
    "--include-module=win32com.client",
    "--include-module=win32com.server",
    "--include-module=win32com.servers",
    "--include-plugin-files=$env:SystemRoot\system32\pythoncom39.dll"
    "--include-plugin-files=$env:SystemRoot\system32\pywintypes39.dll"
    "--windows-product-name=$product_name",
    "--windows-product-version=$version",
    "--windows-company-name=$company_name",
    "--windows-file-description=$description",
    "--windows-icon-from-ico=$icon_path",
    (&{ if ($lto -eq $true) { "--windows-onefile-tempdir-spec=%TEMP%/yaam-release" } else { "" } }),
    "--include-data-dir=$root/$defaults_dir=$defaults_dir",
    "--include-data-file=$root/$output_dir/MANIFEST=MANIFEST",
    "--include-data-file=$root/README.md=README.md",
    "--include-data-file=$root/LICENSE=LICENSE",
    "--assume-yes-for-downloads"
    "--remove-output",
    "--output-dir=$output_dir"
)

if ($mode -eq "standalone")
{
    if (Test-Path -path "$root/$output_dir/$target_name")
    {
        Remove-Item -path "$root/$output_dir/$target_name" -force -recurse
        Write-Output "Cleared previous build $root/$output_dir/$target_name"
    }
}
else 
{
    if (Test-Path -path "$root/$output_dir/$target_name.exe")
    {
        Remove-Item -path "$root/$output_dir/$target_name.exe" -force
        Write-Output "Cleared previous build $root/$output_dir/$target_name.exe"
    }    
}

@(python -m nuitka $params $entrypoint)

if ($mode -eq "standalone")
{
    Move-Item -path "$root/$output_dir/$entrypoint_name.dist" -destination "$root/$output_dir/$target_name" -force
    Move-Item -path "$root/$output_dir/$target_name/$entrypoint_name.exe" -destination "$root/$output_dir/$target_name/$target_name.exe" -force
    Write-Output "Renamed $root/$output_dir/$entrypoint_name.dist/$entrypoint_name.exe to $root/$output_dir/$target_name/$target_name.exe"
    
    Remove-Item -path "$root/$output_dir/MANIFEST" -force
    Write-Output "Cleared $root/$output_dir/MANIFEST"
    Remove-Item -path "$root/$output_dir/$entrypoint_name.build" -force -recurse
    Write-Output "Cleared $root/$output_dir/$entrypoint_name.build"
}
else 
{
    Move-Item -path "$root/$output_dir/$entrypoint_name.exe" -destination "$root/$output_dir/$target_name.exe" -force
    Write-Output "Renamed $root/$output_dir/$entrypoint_name.exe to $root/$output_dir/$target_name.exe"
}

exit 0
