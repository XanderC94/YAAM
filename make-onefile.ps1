$root=$PSScriptRoot
$requirements=New-Object System.Collections.Generic.List[System.Object]
$requirements.AddRange(@(pipreqs --print))
$nuitka_version=([System.String](@(pip list | Select-String "nuitka"))).Split(" ")[-1]
$requirements.Add("nuitka==$nuitka_version")
$requirements | Sort-Object | Out-File "$root/requirements.txt" -Encoding utf8 -Force | Out-Null

Write-Output "Updated required project modules file."

$version = @(git describe --tags --always)
$product_name="Yet Another Addon Manager"
$product_version="0.0.0.1"
$company_name="https://github.com/XanderC94"
$description="YAAM-$version"
$icon_path="res/icon/yaam.ico"
$metadata_dir="res/metadata"
$output_dir="bin/msvc"
$target="src/yaam-release.py"

# Load manifest template and write in bin folder
# Then embed the manifest into the application executable

$manifest = Get-Content -Raw -Path "$root/res/template/MANIFEST" | ConvertFrom-Json
$manifest.version = $version
$manifest | ConvertTo-Json -depth 32| set-content "$root/bin/MANIFEST"

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
    "--windows-icon-from-ico=$icon_path",
    "--windows-onefile-tempdir-spec=%TEMP%/yaam-release-$version",
    "--include-data-dir=$root/$metadata_dir=$metadata_dir",
    "--include-data-file=$root/res/template/MANIFEST=res/MANIFEST",
    "--output-dir=$output_dir"
)

@(python -m nuitka $params $target)
