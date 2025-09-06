import argparse
import sys
from .core import (
    fix_canonicals,
    fix_flags_match_canonical,
    sync_cross_references,
    repair_all,
    scan_issues,
)


def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--ro-dir", dest="ro_dir", required=True, help="Path to ro/ directory")
    p.add_argument("--en-dir", dest="en_dir", required=True, help="Path to en/ directory")
    p.add_argument("--base-url", dest="base_url", required=True, help="Base URL, e.g. https://neculaifantanaru.com")
    p.add_argument("--dry-run", dest="dry_run", action="store_true", help="Do not write files, just report")
    p.add_argument("--backup-ext", dest="backup_ext", default=None, help="If set (e.g. .bak), write a backup copy before modifying files")


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(prog="html-intersection", description="Fix canonical, FLAGS, and cross-references across mirrored HTML directories (RO<->EN)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_repair = sub.add_parser("repair", help="Run all steps: canonicals, flags, sync")
    _add_common_args(p_repair)

    p_canon = sub.add_parser("fix-canonicals", help="Fix canonical tags to match filenames")
    _add_common_args(p_canon)

    p_flags = sub.add_parser("fix-flags", help="Ensure FLAGS match canonical in the same file")
    _add_common_args(p_flags)

    p_sync = sub.add_parser("sync", help="Synchronize RO<->EN cross-references in FLAGS")
    _add_common_args(p_sync)

    p_scan = sub.add_parser("scan", help="Scan and print detected RO<->EN pairs")
    _add_common_args(p_scan)
    p_scan.add_argument("--report", dest="report", action="store_true", help="Include invalid links, mismatched pairs, and unmatched files")

    args = parser.parse_args(argv)

    if args.cmd == "repair":
        c, f, x = repair_all(args.ro_dir, args.en_dir, args.base_url, dry_run=args.dry_run, backup_ext=args.backup_ext)
        print(f"Canonicals fixed: {c}; Flags fixed: {f}; Cross-ref fixed: {x}")
        return 0
    if args.cmd == "fix-canonicals":
        n = fix_canonicals(args.ro_dir, args.en_dir, args.base_url, dry_run=args.dry_run, backup_ext=args.backup_ext)
        print(f"Canonicals fixed: {n}")
        return 0
    if args.cmd == "fix-flags":
        n = fix_flags_match_canonical(args.ro_dir, args.en_dir, args.base_url, dry_run=args.dry_run, backup_ext=args.backup_ext)
        print(f"Flags fixed: {n}")
        return 0
    if args.cmd == "sync":
        n = sync_cross_references(args.ro_dir, args.en_dir, args.base_url, dry_run=args.dry_run, backup_ext=args.backup_ext)
        print(f"Cross-ref fixed: {n}")
        return 0
    if args.cmd == "scan":
        if args.report:
            report = scan_issues(args.ro_dir, args.en_dir, args.base_url)
            print("RO->EN:")
            for ro, en in report["ro_to_en"].items():
                print(f"  {ro} -> {en}")
            print("EN->RO:")
            for en, ro in report["en_to_ro"].items():
                print(f"  {en} -> {ro}")
            if report["invalid_links"]:
                print("\nInvalid links:")
                for msg in report["invalid_links"]:
                    print(f"  {msg}")
            if report["mismatched_pairs"]:
                print("\nPairs with no common links:")
                for ro, en, details in report["mismatched_pairs"]:
                    print(f"  {ro} <-> {en}: {details}")
            if report["unmatched_ro"] or report["unmatched_en"]:
                print("\nUnmatched files:")
                for ro in report["unmatched_ro"]:
                    print(f"  RO {ro}")
                for en in report["unmatched_en"]:
                    print(f"  EN {en}")
        else:
            from .core import _scan_pairs  # type: ignore
            ro_to_en, en_to_ro = _scan_pairs(args.ro_dir, args.en_dir, args.base_url)
            print("RO->EN:")
            for ro, en in sorted(ro_to_en.items()):
                print(f"  {ro} -> {en}")
            print("EN->RO:")
            for en, ro in sorted(en_to_ro.items()):
                print(f"  {en} -> {ro}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())


