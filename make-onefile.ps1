$root=$PSScriptRoot
$requirements=New-Object System.Collections.Generic.List[System.Object]
$requirements.AddRange(@(pipreqs --print))
$pip_list=@(pip list)
$nuitka_version=([System.String]($pip_list | Select-String "nuitka")).Split(" ")[-1]
$pipreqs_version=([System.String]($pip_list | Select-String "pipreqs")).Split(" ")[-1]
$requirements.Add("nuitka==$nuitka_version")
$requirements.Add("pipreqs==$pipreqs_version")
$requirements | Sort-Object | Out-File "$root/requirements.txt" -Encoding utf8 -Force | Out-Null

Write-Output "Updated required project modules file."

$version = [System.String](@(git describe --tags --always))
$product_name="Yet Another Addon Manager"
$product_version="0.0.0.1"
$company_name="https://github.com/XanderC94"
$description="YAAM-$version"
$icon_path="res/icon/yaam.ico"
$template_dir="res/template"
$defaults_dir="res/default"
$output_dir="bin"
$target_name="yaam-release"
$target="src/$target_name.py"

# Load manifest template and write in bin folder
# Then embed the manifest into the application executable

$manifest = Get-Content -Raw -Path "$root/$template_dir/MANIFEST" | ConvertFrom-Json
$manifest.version = $version
$manifest | ConvertTo-Json -depth 32 | set-content "$root/bin/MANIFEST"

$params = @(
    "--onefile",
    # "--mingw64",
    "--msvc",
    "--lto=yes",
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
    "--windows-onefile-tempdir-spec=%TEMP%/yaam-release",
    # "--windows-onefile-tempdir-spec=%TEMP%/yaam-release-%PID%",
    "--include-data-dir=$root/$defaults_dir=$defaults_dir",
    "--include-data-file=$root/bin/MANIFEST=MANIFEST",
    "--include-data-file=$root/README.md=README.md",
    "--output-dir=$output_dir"
)

if (Test-Path "$root/$output_dir/$target_name.exe")
{
    Move-Item -path "$root/$output_dir/$target_name.exe" -destination "$root/$output_dir/$target_name.exe.bak" -force
}

@(python -m nuitka $params $target)

# Rename-Item "$root/$output_dir/$target_name.exe" "$target_name-$version.exe"
