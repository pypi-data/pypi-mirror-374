# How to publish the python package into PyPI
Please use the package `khx-publish-pypi` to publish the package into PyPI.
For more information, please visit :
- PyPI : [khx-publish-pypi](https://pypi.org/project/khx-publish-pypi/) package page.
- GitHub : [khx-publish-pypi](https://github.com/Khader-X/khx-publish-pypi) repository page.
This package is developed and maintained by Khader-X.
Founder : ABUELTAYEF Khader

# How to use the package
## Step 1: Install the package
You can install the package using pip. Open your terminal and run the following command:
- **Install the package using pip**
```bash
pip install khx-publish-pypi
```
- Check the latest version:
```bash
khx-publish-pypi --version
```

## Step 2: Set up your API tokens
To publish packages to PyPI, you need to set up your API tokens. Follow these steps:
1. Go to your PyPI account settings.
2. Create a new API token with the desired scope (e.g., "Read and Write").
3. Copy the generated token and store it securely.
4. **Set up your API tokens** :
```bash
khx-publish-pypi setup-tokens
```

## Step 3: Publish your package
Once you have your package ready and your API tokens set up, you can publish your package to PyPI using the following command:
```bash
khx-publish-pypi run
```
Follow the instructions provided by the tool to complete the publishing process.

This command provides a complete guided experience:
- ✅ Runs pre-publish checks
- 🔑 Manages API token configuration
- 📈 Offers version bumping options
- 🏗️ Builds your package distributions
- 📤 Publishes to TestPyPI and/or PyPI
- 🔗 If successful, it will display the URL to your published package.
