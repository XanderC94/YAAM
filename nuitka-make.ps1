param (
    [System.String]$mode="standalone",
    [System.String]$compiler="msvc",
    [switch]$lto
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

$root=$PSScriptRoot
$requirements=New-Object System.Collections.Generic.List[System.Object]
$requirements.AddRange(@(pipreqs --print))
$pip_list=@(pip list)
$nuitka_version=([System.String]($pip_list | Select-String "nuitka")).Split(" ")[-1]
$pipreqs_version=([System.String]($pip_list | Select-String "pipreqs")).Split(" ")[-1]
$requirements.Add("nuitka==$nuitka_version")
$requirements.Add("pipreqs==$pipreqs_version")
$requirements | Sort-Object | Set-Content "$root/requirements.txt" -encoding utf8 -force | Out-Null

Write-Output "Updated required project modules file."

$version=[System.String](@(git describe --tags --abbrev=0 --always))
$revision=[System.String](@(git rev-parse --short=8  head))

$product_name="Yet Another Addon Manager"

$version_pattern = "v(?<major>[0-9]+)\.(?<minor>[0-9]+)\.(?<bugfix>[0-9]+)(?>-(?<type>alpha|beta))?(?>-(?<revision>.*))?"
$match_result = [regex]::Matches($version, $version_pattern)

if (-not $match_result[0].Success)
{
    $version="0.0.0.0"
}

Write-Output "YAAM $version-$revision"

$product_version=$version.Replace('v', '').Replace('-alpha', '.2').Replace('-beta', '.1')

$company_name="https://github.com/XanderC94"
$description="YAAM-$version-$revision"
$icon_path="res/icon/yaam.ico"
$template_dir="res/template"
$defaults_dir="res/default"
$output_dir="bin/$mode/$compiler"
$target_name="yaam-release"
$target="src/$target_name.py"

# create output dir if doesn't exist
if (-not(Test-Path -path "$root/$output_dir"))
{
    New-Item -path "$root/$output_dir" -force -itemtype "directory" | Out-Null
}

# Load manifest template and write in bin folder
# Then embed the manifest into the application executable
$manifest = Get-Content -raw -path "$root/$template_dir/MANIFEST" | ConvertFrom-Json
$manifest.version = $version
$manifest.revision = $revision
$manifest | ConvertTo-Json -depth 32 | Set-Content -path "$root/$output_dir/MANIFEST" -force

$params = @(
    "--$mode",
    "--$compiler",
    (&{ if ($lto -eq $true) { "--lto=yes" } else { "" } }),
    "--remove-output",
    "--plugin-enable=pylint-warnings",
    "--include-module=win32com.gen_py",
    "--include-module=win32com.client",
    "--include-module=win32com.server",
    "--include-module=win32com.servers",
    "--include-plugin-files=$env:SystemRoot\system32\pythoncom39.dll"
    "--include-plugin-files=$env:SystemRoot\system32\pywintypes39.dll"
    "--windows-product-name=$product_name",
    "--windows-product-version=$product_version",
    "--windows-company-name=$company_name",
    "--windows-file-description=$description",
    "--windows-icon-from-ico=$icon_path",
    (&{ if ($lto -eq $true) { "--windows-onefile-tempdir-spec=%TEMP%/yaam-release" } else { "" } }),
    "--include-data-dir=$root/$defaults_dir=$defaults_dir",
    "--include-data-file=$root/$output_dir/MANIFEST=MANIFEST",
    "--include-data-file=$root/README.md=README.md",
    "--output-dir=$output_dir"
)

if ($mode -eq "standalone")
{
    if (Test-Path -path "$root/$output_dir/$target_name.bak")
    {
        Remove-Item -path "$root/$output_dir/$target_name.bak" -force -recurse
    }
    
    if (Test-Path -path "$root/$output_dir/$target_name")
    {
        Move-Item -path "$root/$output_dir/$target_name" -destination "$root/$output_dir/$target_name.bak" -force
    } 
}
else 
{
    if (Test-Path -path "$root/$output_dir/$target_name.exe")
    {
        Move-Item -path "$root/$output_dir/$target_name.exe" -destination "$root/$output_dir/$target_name.exe.bak" -force
    }    
}

@(python -m nuitka $params $target)

if ($mode -eq "standalone")
{
    Move-Item -path "$root/$output_dir/$target_name.dist" -destination "$root/$output_dir/$target_name" -force
    Remove-Item -path "$root/$output_dir/MANIFEST" -force
    Remove-Item -path "$root/$output_dir/$target_name.build" -force -recurse
}

exit 1
