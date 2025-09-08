from src.pdc import analyze_dependencies, export_json, export_csv, top_n_packages

# -----------------------------
# Helpers for temporary test files
# -----------------------------
def create_test_file(tmp_path, code):
    file_path = tmp_path / "test_file.py"
    file_path.write_text(code)
    return file_path

# -----------------------------
# Test static imports detection
# -----------------------------
def test_static_imports(tmp_path):
    code = """
import colorama
import iniconfig
"""
    create_test_file(tmp_path, code)
    in_use, unused = analyze_dependencies(str(tmp_path))
    assert "colorama" in in_use
    assert "iniconfig" in in_use

# -----------------------------
# Test unused packages detection
# -----------------------------
def test_unused_packages(tmp_path):
    # six is installed but not imported
    code = "import colorama"
    create_test_file(tmp_path, code)
    in_use, unused = analyze_dependencies(str(tmp_path))
    assert "six" in unused
    assert "colorama" in in_use

# -----------------------------
# Test missing packages detection
# -----------------------------
def test_missing_packages(tmp_path):
    code = "import nonexistent_package"
    create_test_file(tmp_path, code)
    in_use, unused = analyze_dependencies(str(tmp_path))
    # Should not fail, missing packages handled
    assert "nonexistent_package" not in in_use

# -----------------------------
# Test package sizes
# -----------------------------
def test_package_sizes(tmp_path):
    code = "import colorama"
    create_test_file(tmp_path, code)
    in_use, unused = analyze_dependencies(str(tmp_path))
    for size in in_use.values():
        assert isinstance(size, float)
        assert size >= 0

# -----------------------------
# Test Top-N largest packages
# -----------------------------
def test_top_n(tmp_path):
    code = """
import colorama
import iniconfig
import typing_extensions
"""
    create_test_file(tmp_path, code)
    in_use, unused = analyze_dependencies(str(tmp_path))
    top = top_n_packages(in_use, unused, n=2)

    # Assert top is a dict with 2 items
    assert isinstance(top, dict)
    assert len(top) == 2

    # Extract sizes preserving order (dict in Python 3.7+ preserves insertion order)
    sizes = list(top.values())

    # Top package size should be >= second package size
    assert sizes[0] >= sizes[1]

# -----------------------------
# Test JSON export
# -----------------------------
def test_export_json(tmp_path):
    code = "import colorama"
    create_test_file(tmp_path, code)
    in_use, unused = analyze_dependencies(str(tmp_path))
    export_json(in_use, unused, filename=tmp_path / "report.json")
    assert (tmp_path / "report.json").exists()

# -----------------------------
# Test CSV export
# -----------------------------
def test_export_csv(tmp_path):
    code = "import colorama"
    create_test_file(tmp_path, code)
    in_use, unused = analyze_dependencies(str(tmp_path))
    export_csv(in_use, unused, filename=tmp_path / "report.csv")
    assert (tmp_path / "report.csv").exists()
