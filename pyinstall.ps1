param (
    # [System.String]$mode="standalone", # choose between standalone and onefile
    # [System.String]$compiler="msvc", # choose between msvc, mingw64 or llvm
    # [System.String]$msvc="latest", # msvc compiler version, e.g.: 14.3, 14.2, ... latest
    # [switch]$lto,
    # [switch]$artifacts,
    [switch]$backup,
    [System.String]$tag,
    [System.String]$revision,
    [System.String]$pythonpath
)

$root=$PSScriptRoot

$scripts_dir="$root/res/scripts"

if ($pythonpath.Length -eq 0)
{
    $pythonpath=[System.String]@(."$scripts_dir/find-pythonpath.ps1")
    
    if ($pythonpath.Length -eq 0)
    {
        Write-Error "Python-path not found... Closing."
        exit 1
    }
}

Write-Output "Python path is $pythonpath"

if ($tag.Length -eq 0)
{
    $tag=[System.String](@((@(git tag -l) -split '\n') | Select-Object -last 1))
}

if ($revision.Length -eq 0)
{
    $revision=[System.String](@(git rev-parse --short=8 HEAD))
}

$version=[System.String]@(."$scripts_dir/get-version-string.ps1" -tag $tag -rev $revision)

$version_for_metadata=[System.String]@(."$scripts_dir/get-version-string.ps1" -tag $tag -mode windows)

$version_array=$version_for_metadata.Split(".")

Write-Output "YAAM $version"

Write-Output "Workspace is $root"

$template_dir="res/template"
$defaults_dir="res/default"
$output_dir="bin"
$temp_dir="tmp"
# $artifacts_dir="artifacts/$builder"
$target_name="yaam"
$entrypoint_name="main"
$entrypoint="src/$entrypoint_name.py"
$build_date=@(Get-Date -Format "yyyy-MM-dd")
# $build_time_utc_ms=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()

# create output dir if doesn't exist
if (-not(Test-Path -path "$root/$output_dir"))
{
    New-Item -path "$root/$output_dir" -force -itemtype "directory" | Out-Null
    Write-Output "Created output dir $root/$output_dir"
}
elseif ($backup -eq $true)
{
    @(."$scripts_dir/backup-target.ps1" -target "$root/$output_dir/$target_name")
}
else
{
    Remove-Item -path "$root/$output_dir/*" -force -recurse
    Write-Output "Cleared $root/$output_dir content"
}

# create temp dir if doesn't exist
if (-not(Test-Path -path "$root/$temp_dir"))
{
    New-Item -path "$root/$temp_dir" -force -itemtype "directory" | Out-Null
    Write-Output "Created temp dir $root/$temp_dir"
}

$product_name="Yet Another Addon Manager"
$company_name="Alessandro Cevoli, https://github.com/XanderC94"
$description="YAAM-$version"
$icon_path="res/icon/yaam.ico"

$versionfile = Get-Content -raw -path "$root/$template_dir/WINDOWS_VERSION_FILE.txt"

$versionfile = $versionfile.Replace("{{major_version}}", [int]($version_array[0]))
$versionfile = $versionfile.Replace("{{minor_version}}", [int]($version_array[1]))
$versionfile = $versionfile.Replace("{{bugfix_version}}", [int]($version_array[2]))
$versionfile = $versionfile.Replace("{{build_number}}", [int]($version_array[3]))
$versionfile = $versionfile.Replace("{{file_version_string}}", $version)
$versionfile = $versionfile.Replace("{{product_version_string}}", $version)
$versionfile = $versionfile.Replace("{{private_build_string}}", "")
$versionfile = $versionfile.Replace("{{special_build_string}}", "")
$versionfile = $versionfile.Replace("{{date_ms_bits}}", 0)
$versionfile = $versionfile.Replace("{{date_ls_bits}}", 0)
$versionfile = $versionfile.Replace("{{lang_id}}", 0)
$versionfile = $versionfile.Replace("{{charset_id}}", 1200)

$versionfile = $versionfile.Replace("{{company_name}}", $company_name)
$versionfile = $versionfile.Replace("{{product_name}}", $product_name)
$versionfile = $versionfile.Replace("{{file_description}}", $description)
$versionfile = $versionfile.Replace("{{file_comments}}", "")
$versionfile = $versionfile.Replace("{{product_version_string}}", $version)
$versionfile = $versionfile.Replace("{{file_version_string}}", $version)
$versionfile = $versionfile.Replace("{{original_filename}}", "$target_name.exe")
$versionfile = $versionfile.Replace("{{internal_name}}", $target_name)
$versionfile = $versionfile.Replace("{{legal_copyright}}", "Copyright (c) $build_date, $company_name")

$versionfile | Set-Content -path "$root/$temp_dir/YAAM_WINDOWS_VERSION_FILE.py" -Encoding "UTF8" -force

$build_location="$root/$output_dir/$target_name"

$add_data = @(
    [pscustomobject]@{ 
        Target="$root/$defaults_dir"; 
        Destination="$build_location/$defaults_dir" 
    },
    [pscustomobject]@{ 
        Target="$root/README.md"; 
        Destination="$build_location/README.md" 
    },
    [pscustomobject]@{ 
        Target="$root/LICENSE"; 
        Destination="$build_location/LICENSE" 
    },
    [pscustomobject]@{ 
        Target="$pythonpath/Lib/site-packages/orderedmultidict/__version__.py"; 
        Destination="$build_location/_internal/orderedmultidict/__version__.py" 
    }
)

$params = @(
    "--name=$target_name",
    "--version-file=$root/$temp_dir/YAAM_WINDOWS_VERSION_FILE.py",
    "--onedir"
    "--icon=$root/$icon_path",
    # "--add-data=$root/$defaults_dir/*;./$defaults_dir",
    # "--add-data=$root/README.md;.",
    # "--add-data=$root/LICENSE;.",
    # "--add-data=$pythonpath/Lib/site-packages/orderedmultidict/__version__.py;./orderedmultidict",
    "--distpath=$root/$output_dir",
    "--workpath=$root/$temp_dir",
    # "--log-level=DEBUG",
    "--clean",
    "--noconfirm"
)

# $builder_version=[System.String]([array]@(pyinstaller --version)[0])

# Write-Output "Bundling application with with Pyinstaller $builder_version"

# Write-Output "pyinstaller $params $root/$entrypoint"

@(pyinstaller $params $root/$entrypoint)

foreach ($data_pair in $add_data)
{
    $target = $data_pair.Target
    $destination = $data_pair.Destination

    Write-Output "Copying $target to $destination"

    if (Test-Path -path $target -PathType Container)
    {
        New-Item -path $destination -force -itemtype Directory | Out-Null
    }
    else
    {
        New-Item -path $destination -force -itemtype File | Out-Null
    }

    Copy-Item -path $target -destination $destination -Force | Out-Null
}

# clear leftovers
if (Test-Path -path "$root/$temp_dir")
{
    Remove-Item -path "$root/$temp_dir" -force -recurse
    Write-Output "Cleared $root/$temp_dir"
}

# clear leftovers
if (Test-Path -path "$root/$temp_dir")
{
    Remove-Item -path "$root/$temp_dir" -force -recurse
    Write-Output "Cleared $root/$temp_dir"
}

return $build_location
