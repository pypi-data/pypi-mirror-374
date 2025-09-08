from pdc import analyze_dependencies, export_json, export_csv, top_n_packages, print_packages


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Dep-Cleaner: Analyze Python project dependencies."
    )
    parser.add_argument("path", nargs="?", default=".", help="Path to project")
    parser.add_argument("--runtime", action="store_true", help="Trace runtime imports")
    parser.add_argument("--json", action="store_true", help="Export results to JSON")
    parser.add_argument("--csv", action="store_true", help="Export results to CSV")
    parser.add_argument("--top", type=int, help="Show top N largest packages")
    args = parser.parse_args()

    in_use, unused = analyze_dependencies(args.path, runtime=args.runtime)

    print_packages(in_use, title="✅ In-Use Packages")

    print_packages(unused, title="⚠️ Unused Packages")

    if args.json:
        export_json(in_use, unused)
    if args.csv:
        export_csv(in_use, unused)
    if args.top:
        top_packages = top_n_packages(in_use, unused, n=args.top)
        print_packages(top_packages, title=f"Top {args.top} largest packages:")


if __name__ == "__main__":
    main()
