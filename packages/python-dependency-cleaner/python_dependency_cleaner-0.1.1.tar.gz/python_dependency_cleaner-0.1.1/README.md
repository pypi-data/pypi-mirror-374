# PDC (python-dependency-cleaner)

<p align="center">
  <img src="PDC logo.png" alt="PDC Logo" width="200"/>
</p>

**PDC** is a Python library and CLI tool that helps you **analyze your Python projects** to detect:

- ✅ Used dependencies
- ⚠️ Unused dependencies
- 📦 Package sizes
- 📊 Top-N largest packages

It also supports exporting reports in **JSON** and **CSV** formats.

## ✨ Features

- 🔍 Static analysis of imports using **AST**
- ⚡ Optional runtime import tracing
- 📑 Detect unused packages listed in `requirements.txt`
- 📦 Measure installed package sizes
- 📊 Export reports to JSON/CSV
- 🖥️ CLI support for quick usage
- 📈 Show top-N largest packages for optimization

## 📦 Installation

Install via pip (project name is **python-dependency-cleaner**):

🔗 [PyPI: python-dependency-cleaner](https://pypi.org/project/python-dependency-cleaner/0.1.1/)
<br/>
🔗 [Github: python-dependency-cleaner](https://github.com/DorMor1999/PDC-Python-Dependency-Cleaner-)

```bash
pip install python-dependency-cleaner==0.1.1
````

## Usage

### As a library

```python
from pdc import analyze_dependencies, export_json, export_csv, top_n_packages, print_packages

    # Analyze a project
    in_use, unused = analyze_dependencies(".")

    # print in_use
    print_packages(in_use, title="✅ In-Use Packages")

    # print unused
    print_packages(unused, title="⚠️ Unused Packages")

    # Export reports
    export_json(in_use, unused, filename="report.json")
    export_csv(in_use, unused, filename="report.csv")

    # Get top n largest packages
    n = 5
    top_packages = top_n_packages(in_use, unused, n)
    print_packages(top_packages, title=f"Top {n} largest packages:")
```

### CLI Usage

```bash
# Analyze current directory
pdc .

# Export JSON report
pdc . --json

# Export CSV report
pdc . --csv

# Show top 10 largest packages
pdc . --top 10
```

## Requirements

* Python 3.10+
* Optional: packages in your `requirements.txt`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.


