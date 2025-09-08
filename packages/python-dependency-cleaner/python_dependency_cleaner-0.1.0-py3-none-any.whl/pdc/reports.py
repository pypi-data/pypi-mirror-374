import json
import csv


def export_json(in_use, unused, filename="dependency_report.json"):
    """
    Export dependency analysis results to a JSON file.

    The report contains two sections:
    - "in_use": dictionary of active packages and their sizes
    - "unused": dictionary of inactive packages and their sizes

    Parameters
    ----------
    in_use : dict
        Dictionary of packages in use {package_name: size_in_MB}.
        Size may be None if unavailable.
    unused : dict
        Dictionary of unused packages {package_name: size_in_MB}.
        Size may be None if unavailable.
    filename : str, default="dependency_report.json"
        File path where the JSON report will be saved.

    Returns
    -------
    None
        Writes the results to disk and prints the save location.
    """
    report = {"in_use": in_use, "unused": unused}
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[Exported] JSON report saved to {filename}")


def export_csv(in_use, unused, filename="dependency_report.csv"):
    """
    Export dependency analysis results to a CSV file.

    The CSV file contains rows with the following columns:
    - Package : name of the Python package
    - Size (MB): package size in megabytes
    - Status : "in_use" or "unused"

    Parameters
    ----------
    in_use : dict
        Dictionary of packages in use {package_name: size_in_MB}.
        Size may be None if unavailable.
    unused : dict
        Dictionary of unused packages {package_name: size_in_MB}.
        Size may be None if unavailable.
    filename : str, default="dependency_report.csv"
        File path where the CSV report will be saved.

    Returns
    -------
    None
        Writes the results to disk and prints the save location.
    """
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Package", "Size (MB)", "Status"])
        for pkg, size in in_use.items():
            writer.writerow([pkg, size, "in_use"])
        for pkg, size in unused.items():
            writer.writerow([pkg, size, "unused"])
    print(f"[Exported] CSV report saved to {filename}")


def top_n_packages(in_use, unused, n=5):
    """
    Retrieve the top-N largest packages (in-use + unused) by size.

    Packages from both 'in_use' and 'unused' are merged into a single
    dictionary and then sorted in descending order of size (MB).

    Parameters
    ----------
    in_use : dict
        Dictionary {package_name: size_in_MB} for packages currently in use.
        Size may be None, which is treated as 0.
    unused : dict
        Dictionary {package_name: size_in_MB} for unused packages.
        Size may be None, which is treated as 0.
    n : int, default=5
        Number of top packages to return.

    Returns
    -------
    dict
        Dictionary { "package_name [status]": size_in_MB } sorted by size.
        Status is "in_use" or "unused".
    """
    # Tag each package with its status
    combined = {f"{pkg} [in_use]": size for pkg, size in in_use.items()}
    combined.update({f"{pkg} [unused]": size for pkg, size in unused.items()})

    # Sort by size (treat None as 0), and keep only top N
    sorted_pkgs = sorted(
        combined.items(),
        key=lambda x: x[1] or 0,
        reverse=True
    )[:n]

    return dict(sorted_pkgs)

def print_packages(packages, title="Packages"):
    """
    Pretty-print a dictionary of packages with their sizes.

    Parameters
    ----------
    packages : dict
        Dictionary {package_name: size_in_MB}.
        Size may be None if unavailable.
    title : str, default="Packages"
        Optional title to display before the package list.

    Returns
    -------
    None
        Prints each package and its size (or 'unknown').
    """
    print(f"\n--- {title} ---")
    for pkg, size in packages.items():
        if size is not None:
            print(f"{pkg} ({size:.2f} MB)")
        else:
            print(f"{pkg} (unknown MB)")

