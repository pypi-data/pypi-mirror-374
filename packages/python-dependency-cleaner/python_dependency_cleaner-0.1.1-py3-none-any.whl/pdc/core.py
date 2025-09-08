import os
import sys
import ast
import subprocess
import tempfile
import builtins
import runpy
import importlib.metadata as metadata


# -----------------------------
# Extract imports (AST-based)
# -----------------------------
def extract_imports_from_ast(tree):
    """
    Extract all top-level import names from an AST tree.

    This function scans through an abstract syntax tree (AST) and extracts:
    - Standard `import module`
    - `from module import ...`
    - Calls to `__import__("module")`
    - Calls to `importlib.import_module("module")`

    Parameters
    ----------
    tree : ast.AST
        The parsed AST tree from a Python file.

    Returns
    -------
    set
        A set of unique module names (strings) that were imported in the file.
    """
    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])

        elif isinstance(node, ast.Call):
            # Handle __import__("module")
            if isinstance(node.func, ast.Name) and node.func.id == "__import__":
                if node.args and isinstance(node.args[0], ast.Constant):
                    if isinstance(node.args[0].value, str):
                        imports.add(node.args[0].value.split(".")[0])

            # Handle importlib.import_module("module")
            elif isinstance(node.func, ast.Attribute):
                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "importlib"
                    and node.func.attr == "import_module"
                ):
                    if node.args and isinstance(node.args[0], ast.Constant):
                        if isinstance(node.args[0].value, str):
                            imports.add(node.args[0].value.split(".")[0])

    return imports


def get_imports_from_code(base_path: str):
    """
    Recursively scan Python files in a directory and extract imports via AST.

    Parameters
    ----------
    base_path : str
        Path to the root directory containing Python source files.

    Returns
    -------
    set
        A set of module names imported anywhere in the codebase.
    """
    imports = set()

    for root, _, files in os.walk(base_path):
        for f in files:
            if f.endswith(".py"):
                file_path = os.path.join(root, f)
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        tree = ast.parse(file.read(), filename=f)
                        imports |= extract_imports_from_ast(tree)
                except (SyntaxError, UnicodeDecodeError):
                    pass

    return imports


# -----------------------------
# Runtime import tracing (optional)
# -----------------------------
def trace_runtime_imports(base_path: str):
    """
    Run the project and trace imports dynamically.

    This function overrides Python's built-in import mechanism to capture
    all modules loaded at runtime. It attempts to run `__main__.py` from
    the provided base_path.

    Parameters
    ----------
    base_path : str
        Path to the project root containing `__main__.py`.

    Returns
    -------
    set
        A set of module names dynamically loaded during runtime.
    """
    runtime_imports = set()
    original_import = builtins.__import__

    def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
        runtime_imports.add(name.split(".")[0])
        return original_import(name, globals, locals, fromlist, level)

    builtins.__import__ = custom_import

    try:
        runpy.run_path(os.path.join(base_path, "__main__.py"), run_name="__main__")
    except Exception as e:
        print(f"[Runtime trace warning] {e}")
    finally:
        builtins.__import__ = original_import

    return runtime_imports


# -----------------------------
# Read installed packages
# -----------------------------
def read_requirements_from_env():
    """
    Get the list of currently installed Python packages via `pip freeze`.

    Returns
    -------
    set
        A set of installed package names in lowercase, without versions.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=True,
        )
        requirements = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running pip freeze: {e}")
        return set()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
        tmp.write(requirements)
        tmp_path = tmp.name

    try:
        try:
            with open(tmp_path, "r", encoding="utf-8-sig") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(tmp_path, "r", encoding="utf-16") as f:
                lines = f.readlines()
    finally:
        os.remove(tmp_path)

    packages = {
        line.strip().split("==")[0].lower()
        for line in lines
        if line.strip() and not line.startswith("#")
    }

    return packages


# -----------------------------
# Package ↔ Module mapping
# -----------------------------
def build_import_to_package_map():
    """
    Build a mapping from importable module names to their corresponding package.

    Uses `importlib.metadata.packages_distributions()` to resolve relationships.

    Returns
    -------
    dict
        A dictionary {module_name: {package_name, ...}} mapping modules
        to one or more package names.
    """
    mapping = {}
    try:
        modules = metadata.packages_distributions()
        for mod, pkgs in modules.items():
            for pkg in pkgs:
                mapping.setdefault(mod.lower(), set()).add(pkg.lower())
    except Exception:
        pass
    return mapping


# -----------------------------
# Get package size
# -----------------------------
def get_package_size(pkg_name: str):
    """
    Calculate the disk space used by an installed package.

    Parameters
    ----------
    pkg_name : str
        The name of the installed package.

    Returns
    -------
    float or None
        The total size of the package in MB (rounded to 2 decimals).
        Returns None if the package is not installed or metadata not found.
    """
    try:
        dist = metadata.distribution(pkg_name)
        total_size = 0
        if dist.files:
            for file in dist.files:
                try:
                    path = dist.locate_file(file)
                    if path.is_file():
                        total_size += path.stat().st_size
                except FileNotFoundError:
                    continue
        return round(total_size / (1024 * 1024), 2)  # MB
    except metadata.PackageNotFoundError:
        return None


# -----------------------------
# Dependency analysis
# -----------------------------
def analyze_dependencies(base_path=".", runtime=False):
    """
    Perform dependency analysis for a project.

    This function:
    - Extracts imports statically (AST)
    - Optionally adds runtime imports if enabled
    - Checks against installed packages
    - Categorizes packages into 'in use' vs 'unused'
    - Estimates disk usage size of each installed package

    Parameters
    ----------
    base_path : str, default="."
        Path to the project directory.
    runtime : bool, default=False
        Whether to trace runtime imports by executing `__main__.py`.

    Returns
    -------
    tuple
        - dict: {package_name: size_in_MB} for packages in use
        - dict: {package_name: size_in_MB} for unused packages
    """
    code_imports = get_imports_from_code(base_path)
    if runtime:
        code_imports |= trace_runtime_imports(base_path)

    requirements = read_requirements_from_env()
    import_to_pkg = build_import_to_package_map()

    used_packages = set()
    for imp in code_imports:
        if imp.lower() in import_to_pkg:
            used_packages |= import_to_pkg[imp.lower()]

    in_use = [pkg for pkg in requirements if pkg in used_packages]
    unused = [pkg for pkg in requirements if pkg not in used_packages]

    in_use_info = {pkg: get_package_size(pkg) for pkg in in_use}
    unused_info = {pkg: get_package_size(pkg) for pkg in unused}

    return in_use_info, unused_info
