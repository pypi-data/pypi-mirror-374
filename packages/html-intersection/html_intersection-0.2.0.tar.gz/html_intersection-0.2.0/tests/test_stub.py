from html_intersection.core import _expected_canonical_href


def test_expected_canonical_href_ro():
    assert _expected_canonical_href("https://ex", "file.html", False) == "https://ex/file.html"


def test_expected_canonical_href_en():
    assert _expected_canonical_href("https://ex", "File.html", True) == "https://ex/en/File.html"


