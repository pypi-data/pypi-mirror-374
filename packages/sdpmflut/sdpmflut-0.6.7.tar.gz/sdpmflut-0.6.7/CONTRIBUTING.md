# Contributing / Building locally

## One-time
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -U pip
pip install build
```

## Build wheel (locally)
```bash
python -m build
# dist/sdpmflut-<version>-<tags>.whl
```

If build fails due to C compiler on your dev machine, use the provided GitHub Actions workflow with `cibuildwheel` to build wheels for Windows/macOS/Linux.
End users will install the prebuilt wheels from PyPI and **won't** need a local compiler.
