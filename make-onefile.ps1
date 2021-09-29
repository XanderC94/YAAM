$version = @(git describe --tags --always)

$params = @(
    "--onefile",
    "--msvc",
    "--lto",
    "--remove-output",
    "--windows-product-name=""YAAM-$version""",
    "--windows-product-version=""0.0.0.1""",
    "--windows-company-name=""https://github.com/XanderC94""",
    "--windows-file-description=""Yet Another Addon Manager""",
    "--output-dir=""bin/msvc""",
    "src/yaam/yaam.py"
)

@(python -m nuitka @params)
