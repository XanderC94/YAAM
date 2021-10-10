$root=$PSScriptRoot
$requirements=New-Object System.Collections.Generic.List[System.Object]
$requirements.AddRange(@(pipreqs --print))
$nuitka_version=([System.String](@(pip list | Select-String "nuitka"))).Split(" ")[-1]
$requirements.Add("nuitka==$nuitka_version")
$requirements | Sort-Object | Out-File $PSScriptRoot/"requirements.txt" -Encoding utf8 -Force | Out-Null

Write-Output "Updated required project modules file."

$version = @(git describe --tags --always)
$product_name="YAAM-$version"
$product_version="0.0.0.1"
$company_name="https://github.com/XanderC94"
$description="Yet Another Addon Manager"
$icon_path="res/icon/yaam.ico"

$output_dir="bin/msvc"
$target="src/main.py"

Write-Output $target

$params = @(
    "--onefile",
    "--msvc",
    # "--mingw64",
    "--lto",
    "--remove-output",
    "--plugin-enable=pylint-warnings"
    "--windows-product-name=$product_name",
    "--windows-product-version=$product_version",
    "--windows-company-name=$company_name",
    "--windows-file-description=$description",
    "--windows-icon-from-ico=$icon_path"
    "--output-dir=$output_dir"
    # "-o $output_dir/yaam.exe"
)

@(python -m nuitka $params $target)

Move-Item "$root/$output_dir/main.exe" "$root/$output_dir/yaam.exe" -Force
Write-Output "Renamed executable to yaam.exe."

if (!(Test-Path "$root/$output_dir/res/metadata"))
{
    New-Item -ItemType Directory -Force "$root/$output_dir/res/metadata"
}

Copy-Item "$root/res/metadata/*" -Destination "$root/$output_dir/res/metadata" -Recurse | Out-Null

Write-Output "Copied metadata in metadata release folder"
