@(pipreqs --force)

$version = @(git describe --tags --always)

$product_name="YAAM-$version"
$product_version="0.0.0.1"
$company_name="https://github.com/XanderC94"
$description="Yet Another Addon Manager"

$output_dir="bin/msvc"
$target="src/yaam/yaam.py"

$params = @(
    "--onefile",
    "--msvc",
    "--lto",
    "--remove-output",
    "--windows-product-name=$product_name",
    "--windows-product-version=$product_version",
    "--windows-company-name=$company_name",
    "--windows-file-description=$description"
    "--output-dir=$output_dir"
)

@(python -m nuitka $params $target)
