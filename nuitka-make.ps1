param (
    [System.String]$mode="standalone", # choose between standalone and onefile
    [System.String]$compiler="msvc", # choose between msvc, mingw64 or llvm
    [System.String]$msvc="latest", # msvc compiler version, e.g.: 14.3, 14.2, ... latest
    [switch]$lto,
    [switch]$artifacts,
    [switch]$backup,
    [System.String]$tag,
    [System.String]$revision,
    [System.String]$pythonpath
)

$root=$PSScriptRoot

if ($pythonpath.Length -eq 0)
{
    $pythonpath=[System.String]@(./scripts/find-pythonpath.ps1)

    if ($pythonpath.Length -eq 0)
    {
        Write-Error "Python-path not found... Closing."
        exit 1
    }
}

Write-Output "Python path is $pythonpath"    

if ($tag.Length -eq 0)
{
    # $tag=[System.String](@(git describe --tags --abbrev=0 --always))
    $tag=[System.String](@((@(git tag -l) -split '\n') | Select-Object -last 1))
}

if ($revision.Length -eq 0)
{
    $revision=[System.String](@(git rev-parse --short=8 HEAD))
}

$version=[System.String]@(./scripts/get-version-string.ps1 -tag $tag -rev $revision)
# $version_short=[System.String]@(./scripts/get-version.ps1 -tag $tag)
$version_for_metadata=[System.String]@(./scripts/get-version-string.ps1 -tag $tag -mode windows)

Write-Output "YAAM $version"

$product_name="Yet Another Addon Manager"
$company_name="https://github.com/XanderC94"
$description="YAAM-$version"
$icon_path="res/icon/yaam.ico"
$template_dir="res/template"
$defaults_dir="res/default"
$output_dir="bin/$mode/$compiler"
$target_name="yaam"
$entrypoint_name="main"
$entrypoint="src/$entrypoint_name.py"
# $build_date=@(Get-Date -Format "yyyy-MM-dd")

# create output dir if doesn't exist
if (-not(Test-Path -path "$root/$output_dir"))
{
    New-Item -path "$root/$output_dir" -force -itemtype "directory" | Out-Null
    Write-Output "Created output dir $root/$output_dir"
}
elseif ($backup -eq $true)
{
    $ext = &( { if ($mode -eq "onefile") { ".exe" } else { "" } })
    @(./scripts/backup-target.ps1 -target "$root/$output_dir/$target_name$ext")
}
else
{
    Remove-Item -path "$root/$output_dir/*" -force -recurse
    Write-Output "Cleared $root/$output_dir content"
}

# create artifacts dir if doesn't exist
if (-not(Test-Path -path "$root/artifacts"))
{
    New-Item -path "$root/artifacts" -force -itemtype "directory" | Out-Null
    Write-Output "Created artifacts dir $root/artifacts"
}
elseif ($backup -eq $false)
{
    Remove-Item -path "$root/artifacts/*" -force -recurse
    Write-Output "Cleared $root/artifacts content"
}

# Load manifest template and write in bin folder
# Then embed the manifest into the application executable
$manifest = Get-Content -raw -path "$root/$template_dir/MANIFEST" | ConvertFrom-Json
$manifest.version = $tag
$manifest.revision = $revision
$manifest | ConvertTo-Json -depth 32 | Set-Content -path "$root/$output_dir/MANIFEST" -force

$params = @(
    "--$mode",
    (&{ if ($compiler -eq "msvc") { "--$compiler=$msvc" } else { "--$compiler" } }),
    (&{ if ($lto -eq $true) { "--lto=yes" } else { "--lto=no" } }),
    "--plugin-enable=pylint-warnings",
    # "--follow-imports",
    # "--include-module=win32com.gen_py",
    # "--include-module=win32com.client",
    # "--include-module=win32com.server",
    # "--include-module=win32com.servers",
    # "--include-plugin-files=$env:SystemRoot\system32\pythoncom39.dll"
    # "--include-plugin-files=$env:SystemRoot\system32\pywintypes39.dll"
    "--windows-product-name=$product_name",
    "--windows-product-version=$version_for_metadata",
    "--windows-company-name=$company_name",
    "--windows-file-description=$description",
    "--windows-icon-from-ico=$icon_path",
    (&{ if ($mode -eq "onefile") { "--windows-onefile-tempdir-spec=%TEMP%/yaam-release" } else { "" } }),
    "--include-data-dir=$root/$defaults_dir=$defaults_dir",
    "--include-data-file=$root/$output_dir/MANIFEST=MANIFEST",
    "--include-data-file=$root/README.md=README.md",
    "--include-data-file=$root/LICENSE=LICENSE",
    "--include-data-file=$pythonpath/Lib/site-packages/orderedmultidict/__version__.py=orderedmultidict/__version__.py"
    "--assume-yes-for-downloads",
    "--force-dll-dependency-cache-update",
    "--remove-output",
    "--output-dir=$output_dir"
)

$nuitka_version=[System.String]([array]@(nuitka --version)[0])

Write-Output "Building with Nuitka $nuitka_version $mode $compiler lto=$lto"
# Write-Output "Command: nuitka $params $entrypoint"

@(nuitka $params $entrypoint)

$build_location="$root/$output_dir/$target_name"

if ($mode -eq "onefile")
{
    $build_location="$build_location.exe"
}

# Rename built objects
if ($mode -eq "standalone")
{
    Move-Item -path "$root/$output_dir/$entrypoint_name.dist" -destination $build_location -force
    Move-Item -path "$build_location/$entrypoint_name.exe" -destination "$build_location/$target_name.exe" -force

    Write-Output "Renamed $root/$output_dir/$entrypoint_name.dist/$entrypoint_name.exe to $build_location/$target_name.exe"
}
else 
{
    Move-Item -path "$root/$output_dir/$entrypoint_name.exe" -destination $build_location -force
    Write-Output "Renamed $root/$output_dir/$entrypoint_name.exe to $build_location"
}

# clear leftovers
if (Test-Path -path "$root/$output_dir/MANIFEST")
{
    Remove-Item -path "$root/$output_dir/MANIFEST" -force
    Write-Output "Cleared $root/$output_dir/MANIFEST"
}

if (Test-Path -path "$root/$output_dir/$entrypoint_name.build")
{
    Remove-Item -path "$root/$output_dir/$entrypoint_name.build" -force -recurse
    Write-Output "Cleared $root/$output_dir/$entrypoint_name.build"
}

$artifacts_location=$build_location

# create artifacts
if ($artifacts)
{
    $artifacts_destination="$root/artifacts/$target_name-$mode-$compiler-$version.zip"

    Compress-Archive -path $artifacts_location -destinationpath $artifacts_destination

    $artifacts_location=$artifacts_destination

    Write-Output "Created $artifacts_destination"
}

return $artifacts_location
