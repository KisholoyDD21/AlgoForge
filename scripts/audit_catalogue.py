#!/usr/bin/env python3
"""Read-only catalogue quality audit; reports metadata defects without modifying data."""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sqlalchemy import create_engine, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from app.main import Problem  # noqa: E402

VALID_DIFFICULTIES = {"Easy", "Medium", "Hard"}


def audit_records(records: list[dict]) -> dict:
    issues: list[dict] = []
    slugs = [str(row.get("slug", "")) for row in records]
    duplicates = sorted(slug for slug, count in Counter(slugs).items() if slug and count > 1)
    for slug in duplicates:
        issues.append({"severity": "error", "slug": slug, "message": "Duplicate problem slug"})

    for row in records:
        slug = str(row.get("slug") or "<missing-slug>")
        for field in ("slug", "title", "platform", "pattern"):
            if not str(row.get(field) or "").strip():
                issues.append({"severity": "error", "slug": slug, "message": f"Missing required field: {field}"})
        if row.get("difficulty") not in VALID_DIFFICULTIES:
            issues.append({"severity": "error", "slug": slug, "message": "Difficulty must be Easy, Medium or Hard"})
        if not isinstance(row.get("topics"), list) or not row.get("topics"):
            issues.append({"severity": "warning", "slug": slug, "message": "No topic tags"})
        if not row.get("is_native"):
            parsed = urlparse(str(row.get("url") or ""))
            if parsed.scheme != "https" or not parsed.netloc:
                issues.append({"severity": "error", "slug": slug, "message": "Source URL must be an absolute HTTPS URL"})
        if not row.get("is_native") and row.get("statement_rehosted"):
            issues.append({"severity": "error", "slug": slug, "message": "External problem is marked as rehosted"})
        if not row.get("is_native") and not str(row.get("source_licence") or "").strip():
            issues.append({"severity": "error", "slug": slug, "message": "External problem is missing source/licence provenance"})
        if row.get("is_native") and not row.get("statement_rehosted"):
            issues.append({"severity": "warning", "slug": slug, "message": "Native problem is not marked as platform-owned statement content"})

    counts = Counter(row.get("difficulty") for row in records)
    platforms = Counter(row.get("platform") for row in records)
    return {
        "total": len(records),
        "difficulty_counts": {key: counts.get(key, 0) for key in ("Easy", "Medium", "Hard")},
        "platform_counts": dict(sorted(platforms.items(), key=lambda item: str(item[0]))),
        "error_count": sum(issue["severity"] == "error" for issue in issues),
        "warning_count": sum(issue["severity"] == "warning" for issue in issues),
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit AlgoForge catalogue metadata (read-only).")
    parser.add_argument("--strict", action="store_true", help="exit non-zero when errors or warnings are found")
    parser.add_argument("--report", type=Path, help="write the audit result to JSON")
    args = parser.parse_args()
    database_url = os.getenv("DATABASE_URL", "sqlite:///./algoforge.db")
    engine = create_engine(database_url, pool_pre_ping=True, connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {})
    with Session(engine) as db:
        problems = db.scalars(select(Problem).order_by(Problem.slug)).all()
        records = [{
            "slug": p.slug, "title": p.title, "platform": p.platform, "pattern": p.pattern,
            "difficulty": p.difficulty, "topics": p.topics, "url": p.url,
            "source_licence": p.source_licence, "statement_rehosted": p.statement_rehosted,
            "is_native": p.is_native,
        } for p in problems]
    report = audit_records(records)
    print(f"Catalogue: {report['total']} records")
    print(f"Difficulty: {report['difficulty_counts']}")
    print(f"Errors: {report['error_count']} · Warnings: {report['warning_count']}")
    for issue in report["issues"]:
        print(f"[{issue['severity'].upper()}] {issue['slug']}: {issue['message']}")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote audit report: {args.report}")
    if args.strict and report["error_count"] + report["warning_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
