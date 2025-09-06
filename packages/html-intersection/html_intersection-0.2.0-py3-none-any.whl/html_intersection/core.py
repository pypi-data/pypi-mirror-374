import os
import re
from typing import Dict, Tuple, Optional, List, Iterable

from .utils import read_file_with_fallback_encoding, write_file_with_encoding, list_html_files


CANONICAL_RE = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"\s*/?>', re.IGNORECASE)
# Accept both "+40" and "\+40"; same for +1
RO_FLAG_RE = re.compile(r'<li><a\s+cunt_code="\\?\+40"\s+href="([^"]+)"')
EN_FLAG_RE = re.compile(r'<li><a\s+cunt_code="\\?\+1"\s+href="([^"]+)"')


def _ensure_backup(path: str, content: str, backup_ext: Optional[str]) -> None:
    if backup_ext:
        try:
            with open(path + backup_ext, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass


def _expected_canonical_href(base_url: str, filename: str, is_en: bool) -> str:
    if is_en:
        return f"{base_url}/en/{filename}"
    return f"{base_url}/{filename}"


def fix_canonicals(
    ro_directory: str,
    en_directory: str,
    base_url: str,
    dry_run: bool = False,
    backup_ext: Optional[str] = None,
) -> int:
    fixes = 0

    for is_en, directory in ((False, ro_directory), (True, en_directory)):
        for filename in list_html_files(directory):
            path = os.path.join(directory, filename)
            content = read_file_with_fallback_encoding(path)
            if not content:
                continue
            match = CANONICAL_RE.search(content)
            if not match:
                continue
            current_href = match.group(1)
            expected_href = _expected_canonical_href(base_url, filename, is_en)
            if current_href != expected_href:
                fixes += 1
                if not dry_run:
                    _ensure_backup(path, content, backup_ext)
                    new_content = CANONICAL_RE.sub(
                        f'<link rel="canonical" href="{expected_href}" />', content, count=1
                    )
                    write_file_with_encoding(path, new_content)

    return fixes


def fix_flags_match_canonical(
    ro_directory: str,
    en_directory: str,
    base_url: str,
    dry_run: bool = False,
    backup_ext: Optional[str] = None,
) -> int:
    fixes = 0

    for is_en, directory, own_re in (
        (False, ro_directory, RO_FLAG_RE),
        (True, en_directory, EN_FLAG_RE),
    ):
        for filename in list_html_files(directory):
            path = os.path.join(directory, filename)
            content = read_file_with_fallback_encoding(path)
            if not content:
                continue
            canonical_match = CANONICAL_RE.search(content)
            if not canonical_match:
                continue
            canonical_href = canonical_match.group(1)
            own_flag_match = own_re.search(content)
            if not own_flag_match:
                continue
            current_href = own_flag_match.group(1)
            if current_href != canonical_href:
                fixes += 1
                if not dry_run:
                    _ensure_backup(path, content, backup_ext)
                    # replace only the first own flag link
                    new_content = own_re.sub(
                        own_flag_match.group(0).replace(current_href, canonical_href),
                        content,
                        count=1,
                    )
                    write_file_with_encoding(path, new_content)

    return fixes


def _fix_double_html_suffix(href: str) -> str:
    # Normalize accidental .html.html to .html
    return href.replace('.html.html', '.html')


def _extract_en_filename_from_href(href: str, base_url: str) -> Optional[str]:
    if not href:
        return None
    href = _fix_double_html_suffix(href)
    prefix = f"{base_url}/en/"
    if not href.startswith(prefix) or not href.endswith(".html"):
        return None
    return href[len(prefix):]


def _extract_ro_filename_from_href(href: str, base_url: str) -> Optional[str]:
    if not href:
        return None
    href = _fix_double_html_suffix(href)
    prefix = f"{base_url}/"
    if not href.startswith(prefix) or not href.endswith(".html"):
        return None
    name = href[len(prefix):]
    # Some pages may include a nested path; take last component
    if "/" in name:
        name = name.split("/")[-1]
    return name


def _scan_pairs(
    ro_directory: str,
    en_directory: str,
    base_url: str,
) -> Tuple[Dict[str, str], Dict[str, str]]:
    ro_to_en: Dict[str, str] = {}
    en_to_ro: Dict[str, str] = {}

    ro_files = set(list_html_files(ro_directory))
    en_files = set(list_html_files(en_directory))

    # First pass: deduce from flags if present
    for ro_filename in ro_files:
        ro_path = os.path.join(ro_directory, ro_filename)
        ro_content = read_file_with_fallback_encoding(ro_path)
        if not ro_content:
            continue
        en_flag_match = EN_FLAG_RE.search(ro_content)
        if en_flag_match:
            href = _fix_double_html_suffix(en_flag_match.group(1))
            en_name = _extract_en_filename_from_href(href, base_url)
            if en_name:
                if en_name in en_files and ro_filename not in ro_to_en:
                    ro_to_en[ro_filename] = en_name
                    if en_name not in en_to_ro:
                        en_to_ro[en_name] = ro_filename

    for en_filename in en_files:
        en_path = os.path.join(en_directory, en_filename)
        en_content = read_file_with_fallback_encoding(en_path)
        if not en_content:
            continue
        ro_flag_match = RO_FLAG_RE.search(en_content)
        if ro_flag_match:
            href = _fix_double_html_suffix(ro_flag_match.group(1))
            ro_name = _extract_ro_filename_from_href(href, base_url)
            if ro_name:
                if ro_name in ro_files and ro_name not in ro_to_en:
                    ro_to_en[ro_name] = en_filename
                    if en_filename not in en_to_ro:
                        en_to_ro[en_filename] = ro_name

    # Fallback: pair by normalized base name equality
    if len(ro_to_en) < len(ro_files) or len(en_to_ro) < len(en_files):
        ro_bases = {f[:-5].lower().replace("-", " "): f for f in ro_files}
        en_bases = {f[:-5].lower().replace("-", " "): f for f in en_files}
        for base, ro_name in ro_bases.items():
            if ro_name in ro_to_en:
                continue
            if base in en_bases and en_bases[base] not in en_to_ro:
                en_name = en_bases[base]
                ro_to_en[ro_name] = en_name
                en_to_ro[en_name] = ro_name

    return ro_to_en, en_to_ro


def sync_cross_references(
    ro_directory: str,
    en_directory: str,
    base_url: str,
    dry_run: bool = False,
    backup_ext: Optional[str] = None,
) -> int:
    fixes = 0
    ro_to_en, en_to_ro = _scan_pairs(ro_directory, en_directory, base_url)

    # Update RO files: ensure +1 points to expected EN file
    for ro_filename, en_filename in ro_to_en.items():
        ro_path = os.path.join(ro_directory, ro_filename)
        ro_content = read_file_with_fallback_encoding(ro_path)
        if not ro_content:
            continue
        en_match = EN_FLAG_RE.search(ro_content)
        expected_href = f"{base_url}/en/{en_filename}"
        if en_match and _fix_double_html_suffix(en_match.group(1)) != expected_href:
            fixes += 1
            if not dry_run:
                _ensure_backup(ro_path, ro_content, backup_ext)
                new_content = EN_FLAG_RE.sub(
                    en_match.group(0).replace(en_match.group(1), expected_href),
                    ro_content,
                    count=1,
                )
                write_file_with_encoding(ro_path, new_content)

    # Update EN files: ensure +40 points to expected RO file
    for en_filename, ro_filename in en_to_ro.items():
        en_path = os.path.join(en_directory, en_filename)
        en_content = read_file_with_fallback_encoding(en_path)
        if not en_content:
            continue
        ro_match = RO_FLAG_RE.search(en_content)
        expected_href = f"{base_url}/{ro_filename}"
        if ro_match and _fix_double_html_suffix(ro_match.group(1)) != expected_href:
            fixes += 1
            if not dry_run:
                _ensure_backup(en_path, en_content, backup_ext)
                new_content = RO_FLAG_RE.sub(
                    ro_match.group(0).replace(ro_match.group(1), expected_href),
                    en_content,
                    count=1,
                )
                write_file_with_encoding(en_path, new_content)

    return fixes


def scan_issues(
    ro_directory: str,
    en_directory: str,
    base_url: str,
) -> Dict[str, object]:
    """
    Analyze directories and return a detailed report with:
      - ro_to_en, en_to_ro mappings
      - bidirectional_pairs: list[tuple[str, str]]
      - mismatched_pairs: list[tuple[str, str, str]] (ro, en, details)
      - invalid_links: list[str]
      - unmatched_ro: list[str]
      - unmatched_en: list[str]
    """
    ro_files = set(list_html_files(ro_directory))
    en_files = set(list_html_files(en_directory))

    ro_to_en: Dict[str, str] = {}
    en_to_ro: Dict[str, str] = {}
    invalid_links: List[str] = []
    mismatched_pairs: List[Tuple[str, str, str]] = []

    # First pass: try to pair via flags if they point to existing files
    for ro_filename in ro_files:
        ro_path = os.path.join(ro_directory, ro_filename)
        ro_content = read_file_with_fallback_encoding(ro_path)
        if not ro_content:
            continue
        en_match = EN_FLAG_RE.search(ro_content)
        en_href = _fix_double_html_suffix(en_match.group(1)) if en_match else None
        en_name = _extract_en_filename_from_href(en_href, base_url) if en_href else None
        if en_name:
            if en_name not in en_files:
                invalid_links.append(f"RO {ro_filename}: EN file not found {en_name}")
                continue
            ro_to_en[ro_filename] = en_name

    for en_filename in en_files:
        en_path = os.path.join(en_directory, en_filename)
        en_content = read_file_with_fallback_encoding(en_path)
        if not en_content:
            continue
        ro_match = RO_FLAG_RE.search(en_content)
        ro_href = _fix_double_html_suffix(ro_match.group(1)) if ro_match else None
        ro_name = _extract_ro_filename_from_href(ro_href, base_url) if ro_href else None
        if ro_name:
            if ro_name not in ro_files:
                invalid_links.append(f"EN {en_filename}: RO file not found {ro_name}")
                continue
            en_to_ro[en_filename] = ro_name

    # Bidirectional pairs
    bidirectional_pairs: List[Tuple[str, str]] = []
    for ro_file, en_file in ro_to_en.items():
        if en_file in en_to_ro and en_to_ro[en_file] == ro_file:
            bidirectional_pairs.append((ro_file, en_file))

    # Detect pairs with no common links (RO points to EN, EN points back to a different RO)
    for ro_file, en_file in ro_to_en.items():
        if (ro_file, en_file) in bidirectional_pairs:
            continue
        en_path = os.path.join(en_directory, en_file)
        en_content = read_file_with_fallback_encoding(en_path) or ""
        en_ro_match = RO_FLAG_RE.search(en_content)
        en_ro_href = _fix_double_html_suffix(en_ro_match.group(1)) if en_ro_match else None
        details = f"RO->EN: {base_url}/en/{en_file}, EN->RO: {en_ro_href or '-'}"
        mismatched_pairs.append((ro_file, en_file, details))

    # Unmatched files (not part of any pair)
    matched_ro = {ro for ro, _ in bidirectional_pairs} | {ro for ro, _, _ in mismatched_pairs}
    matched_en = {en for _, en in bidirectional_pairs} | {en for _, en, _ in mismatched_pairs}
    unmatched_ro = sorted(list(ro_files - matched_ro))
    unmatched_en = sorted(list(en_files - matched_en))

    return {
        "ro_to_en": dict(sorted(ro_to_en.items())),
        "en_to_ro": dict(sorted(en_to_ro.items())),
        "bidirectional_pairs": bidirectional_pairs,
        "mismatched_pairs": mismatched_pairs,
        "invalid_links": invalid_links,
        "unmatched_ro": unmatched_ro,
        "unmatched_en": unmatched_en,
    }


def repair_all(
    ro_directory: str,
    en_directory: str,
    base_url: str,
    dry_run: bool = False,
    backup_ext: Optional[str] = None,
) -> Tuple[int, int, int]:
    c = fix_canonicals(ro_directory, en_directory, base_url, dry_run=dry_run, backup_ext=backup_ext)
    f = fix_flags_match_canonical(ro_directory, en_directory, base_url, dry_run=dry_run, backup_ext=backup_ext)
    x = sync_cross_references(ro_directory, en_directory, base_url, dry_run=dry_run, backup_ext=backup_ext)
    return c, f, x


