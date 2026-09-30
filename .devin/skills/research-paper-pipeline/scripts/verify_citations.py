#!/usr/bin/env python3
"""
Citation verification script.
Validates BibTeX entries against Semantic Scholar and arXiv APIs.

Usage:
    python verify_citations.py references.bib --output verification_report.json

Layers:
  1. arXiv ID / DOI existence check
  2. Semantic Scholar title matching (Levenshtein > 0.85)
  3. Metadata cross-validation (year, first author, venue)
"""

import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path


def levenshtein_ratio(s1: str, s2: str) -> float:
    """Compute Levenshtein similarity ratio between two strings."""
    s1, s2 = s1.lower().strip(), s2.lower().strip()
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0

    matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        matrix[i][0] = i
    for j in range(len2 + 1):
        matrix[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            matrix[i][j] = min(
                matrix[i - 1][j] + 1,
                matrix[i][j - 1] + 1,
                matrix[i - 1][j - 1] + cost,
            )

    distance = matrix[len1][len2]
    max_len = max(len1, len2)
    return 1.0 - distance / max_len


def parse_bibtex(bib_path: str) -> list[dict]:
    """Simple BibTeX parser. Extracts key, title, author, year, doi, arxiv fields."""
    text = Path(bib_path).read_text(encoding="utf-8")
    entries = []

    # Split into entries
    pattern = r"@\w+\{([^,]+),\s*(.*?)\n\}"
    for match in re.finditer(pattern, text, re.DOTALL):
        key = match.group(1).strip()
        body = match.group(2)

        entry = {"key": key, "raw": match.group(0)}

        for field in ("title", "author", "year", "doi", "url", "journal", "booktitle"):
            field_match = re.search(
                rf"{field}\s*=\s*\{{(.+?)\}}", body, re.DOTALL | re.IGNORECASE
            )
            if field_match:
                entry[field] = field_match.group(1).strip().replace("\n", " ")

        # Try to extract arXiv ID from url, eprint, or doi
        arxiv_match = re.search(r"(\d{4}\.\d{4,5})", body)
        if arxiv_match:
            entry["arxiv_id"] = arxiv_match.group(1)

        entries.append(entry)

    return entries


def check_arxiv(arxiv_id: str) -> bool:
    """Check if an arXiv ID exists (Layer 1)."""
    url = f"https://arxiv.org/abs/{arxiv_id}"
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "research-paper-skill/1.0")
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status == 200
    except Exception:
        return False


def check_doi(doi: str) -> bool:
    """Check if a DOI resolves (Layer 1)."""
    url = f"https://doi.org/{doi}"
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "research-paper-skill/1.0")
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status in (200, 301, 302, 303)
    except urllib.error.HTTPError as e:
        return e.code in (301, 302, 303)
    except Exception:
        return False


def search_semantic_scholar(title: str) -> list[dict] | None:
    """Search Semantic Scholar for a paper by title (Layer 2)."""
    query = urllib.parse.quote(title[:200])
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,authors,year,venue,externalIds"
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "research-paper-skill/1.0")
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("data", [])
    except Exception:
        return None


def verify_entry(entry: dict) -> dict:
    """Run Layer 1-3 verification on a single BibTeX entry."""
    result = {
        "key": entry["key"],
        "title": entry.get("title", ""),
        "verified": False,
        "layers": {},
    }

    # Layer 1: Identifier check
    layer1 = {"passed": False, "details": ""}
    if "arxiv_id" in entry:
        exists = check_arxiv(entry["arxiv_id"])
        layer1["passed"] = exists
        layer1["details"] = f"arXiv:{entry['arxiv_id']} -> {'found' if exists else 'NOT FOUND'}"
    elif "doi" in entry:
        exists = check_doi(entry["doi"])
        layer1["passed"] = exists
        layer1["details"] = f"DOI:{entry['doi']} -> {'resolves' if exists else 'NOT FOUND'}"
    else:
        layer1["details"] = "No arXiv ID or DOI available, skipping to Layer 2"

    result["layers"]["L1_identifier"] = layer1
    time.sleep(0.5)

    # Layer 2: Semantic Scholar title match
    layer2 = {"passed": False, "details": "", "best_match": None, "similarity": 0.0}
    title = entry.get("title", "")
    if title:
        ss_results = search_semantic_scholar(title)
        if ss_results:
            best_sim = 0.0
            best_paper = None
            for paper in ss_results:
                sim = levenshtein_ratio(title, paper.get("title", ""))
                if sim > best_sim:
                    best_sim = sim
                    best_paper = paper

            layer2["similarity"] = round(best_sim, 3)
            if best_sim > 0.85:
                layer2["passed"] = True
                layer2["best_match"] = best_paper.get("title", "")
                layer2["details"] = f"Match found (similarity={best_sim:.3f})"
                result["_ss_paper"] = best_paper
            else:
                layer2["details"] = f"No strong match (best similarity={best_sim:.3f})"
        else:
            layer2["details"] = "Semantic Scholar search failed or returned empty"
    else:
        layer2["details"] = "No title in BibTeX entry"

    result["layers"]["L2_title_match"] = layer2
    time.sleep(1.0)

    # Layer 3: Metadata cross-validation
    layer3 = {"passed": False, "details": [], "mismatches": []}
    ss_paper = result.pop("_ss_paper", None)
    if ss_paper and layer2["passed"]:
        checks = 0
        passes = 0

        # Year check
        if "year" in entry and ss_paper.get("year"):
            checks += 1
            try:
                year_diff = abs(int(entry["year"]) - int(ss_paper["year"]))
                if year_diff <= 1:
                    passes += 1
                    layer3["details"].append(f"Year: OK ({entry['year']} vs {ss_paper['year']})")
                else:
                    layer3["mismatches"].append(f"Year: bib={entry['year']} vs ss={ss_paper['year']}")
            except ValueError:
                layer3["details"].append("Year: could not parse")

        # First author check
        if "author" in entry and ss_paper.get("authors"):
            checks += 1
            bib_first = entry["author"].split(",")[0].split(" and ")[0].strip().split()[-1].lower()
            ss_first = ss_paper["authors"][0].get("name", "").split()[-1].lower() if ss_paper["authors"] else ""
            if levenshtein_ratio(bib_first, ss_first) > 0.8:
                passes += 1
                layer3["details"].append(f"First author: OK ({bib_first} ~ {ss_first})")
            else:
                layer3["mismatches"].append(f"First author: bib={bib_first} vs ss={ss_first}")

        if checks > 0 and passes == checks:
            layer3["passed"] = True
        elif checks > 0:
            layer3["passed"] = len(layer3["mismatches"]) == 0

    else:
        layer3["details"].append("Skipped (Layer 2 did not pass)")

    result["layers"]["L3_metadata"] = layer3

    # Overall verdict
    l1_ok = layer1["passed"] or "No arXiv" in layer1["details"]
    l2_ok = layer2["passed"]
    l3_ok = layer3["passed"] or not layer3["mismatches"]

    if l2_ok and l3_ok:
        result["verified"] = True
    elif l1_ok and not l2_ok:
        result["verified"] = False
        result["reason"] = "not_found_in_semantic_scholar"
    elif l2_ok and not l3_ok:
        result["verified"] = "partial"
        result["reason"] = "metadata_mismatch"
    else:
        result["verified"] = False
        result["reason"] = "verification_failed"

    return result


def main():
    parser = argparse.ArgumentParser(description="Verify BibTeX citations")
    parser.add_argument("bib", help="Path to BibTeX file")
    parser.add_argument("--output", default=None, help="Output JSON report path")
    parser.add_argument("--verbose", action="store_true", help="Print progress")

    args = parser.parse_args()

    if not Path(args.bib).exists():
        print(f"Error: BibTeX file not found: {args.bib}", file=sys.stderr)
        sys.exit(1)

    entries = parse_bibtex(args.bib)
    print(f"Parsed {len(entries)} BibTeX entries")

    results = []
    for i, entry in enumerate(entries):
        if args.verbose:
            print(f"[{i+1}/{len(entries)}] Verifying: {entry.get('title', entry['key'])[:60]}...")
        result = verify_entry(entry)
        results.append(result)

    # Summary
    verified = sum(1 for r in results if r["verified"] is True)
    partial = sum(1 for r in results if r["verified"] == "partial")
    failed = sum(1 for r in results if r["verified"] is False)

    report = {
        "total_citations": len(results),
        "verified": verified,
        "partial": partial,
        "failed": failed,
        "entries": results,
        "failed_details": [
            {"key": r["key"], "title": r["title"], "reason": r.get("reason", "")}
            for r in results
            if r["verified"] is False
        ],
    }

    print(f"\nVerification complete: {verified} verified, {partial} partial, {failed} failed")

    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Report written to: {args.output}")
    else:
        for entry in report["failed_details"]:
            print(f"  FAILED: [{entry['key']}] {entry['title'][:60]}... ({entry['reason']})")


if __name__ == "__main__":
    main()
