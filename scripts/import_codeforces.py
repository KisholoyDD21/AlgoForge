#!/usr/bin/env python3
"""Fill the local metadata catalogue to 150 Easy / 250 Medium / 100 Hard.

Uses the official Codeforces problemset API. It imports metadata and official links only;
problem statements, examples, editorials and hidden tests are deliberately not copied.
"""
from __future__ import annotations

import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import httpx
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.main import Problem, Base  # noqa: E402

TARGETS = {"Easy": 150, "Medium": 250, "Hard": 100}
API = "https://codeforces.com/api/problemset.problems"
PATTERN_MAP = {
    "two pointers": "Two Pointers", "binary search": "Binary Search", "dp": "Dynamic Programming",
    "graphs": "Graph Traversal", "dfs and similar": "Graph DFS", "trees": "Trees",
    "data structures": "Data Structures", "dsu": "Disjoint Set Union", "greedy": "Greedy",
    "sortings": "Sorting", "strings": "String Algorithms", "hashing": "Hashing",
    "bitmasks": "Bit Manipulation", "number theory": "Number Theory", "combinatorics": "Combinatorics",
    "shortest paths": "Shortest Paths", "flows": "Network Flow", "divide and conquer": "Divide and Conquer",
    "games": "Game Theory", "constructive algorithms": "Constructive Algorithms", "implementation": "Implementation",
    "math": "Mathematics", "matrices": "Matrix", "geometry": "Geometry", "probabilities": "Probability",
    "strings": "String Algorithms", "meet-in-the-middle": "Meet in the Middle", "fft": "Fast Fourier Transform",
}


def classify(rating: int) -> str:
    if rating <= 1100:
        return "Easy"
    if rating <= 1800:
        return "Medium"
    return "Hard"


def select_diverse(problems: list[dict], stats: list[dict], need: dict[str, int], excluded_slugs: set[str] | None = None) -> list[dict]:
    excluded_slugs = excluded_slugs or set()
    solved = {(s["contestId"], s["index"]): s.get("solvedCount", 0) for s in stats}
    pools: dict[str, list[dict]] = defaultdict(list)
    for p in problems:
        rating = p.get("rating")
        if not rating or p.get("type") != "PROGRAMMING" or not p.get("contestId"):
            continue
        if f"cf-{p['contestId']}-{str(p['index']).lower()}" in excluded_slugs:
            continue
        bucket = classify(int(rating))
        if need.get(bucket, 0) > 0:
            p = dict(p)
            p["_solved"] = solved.get((p["contestId"], p["index"]), 0)
            pools[bucket].append(p)
    # Prefer problems with a meaningful algorithm tag and stronger community solve counts.
    selected: list[dict] = []
    for bucket, count in need.items():
        pool = sorted(pools[bucket], key=lambda p: (p["_solved"], len(p.get("tags", []))), reverse=True)
        chosen: list[dict] = []
        tag_counts: dict[str, int] = defaultdict(int)
        while pool and len(chosen) < count:
            # Re-score after each pick to avoid filling the bucket with one dominant tag.
            best = max(pool, key=lambda p: p["_solved"] / (1 + sum(tag_counts[t] for t in p.get("tags", []) if t != "implementation")))
            chosen.append(best)
            pool.remove(best)
            for tag in best.get("tags", []):
                tag_counts[tag] += 1
        if len(chosen) < count:
            raise RuntimeError(f"Not enough rated Codeforces problems for {bucket}: wanted {count}, found {len(chosen)}")
        selected.extend(chosen)
    return selected


def main() -> None:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./algoforge.db")
    engine = create_engine(database_url, pool_pre_ping=True, connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {})
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        existing = db.scalar(select(func.count(Problem.id))) or 0
        by_diff = {d: db.scalar(select(func.count(Problem.id)).where(Problem.difficulty == d)) or 0 for d in TARGETS}
        need = {d: max(0, TARGETS[d] - by_diff[d]) for d in TARGETS}
        if not any(need.values()):
            print(f"Catalogue already meets targets: {by_diff}; total={existing}")
            return
        print(f"Current catalogue: {existing}; difficulty counts={by_diff}; importing={need}")
        try:
            with httpx.Client(timeout=45, headers={"User-Agent": "AlgoForge-DSA-Catalogue/1.0 (metadata importer)"}) as client:
                response = client.get(API)
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            print(
                "Could not download the official Codeforces problemset catalogue. "
                "Check outbound HTTPS/DNS access and try again. No problems were imported.\n"
                f"Details: {exc}",
                file=sys.stderr,
            )
            raise SystemExit(2) from exc
        if payload.get("status") != "OK":
            raise RuntimeError(f"Codeforces API returned: {payload.get('comment', 'unknown error')}")
        data = payload["result"]
        existing_slugs = set(db.scalars(select(Problem.slug)).all())
        selected = select_diverse(data["problems"], data["problemStatistics"], need, existing_slugs)
        added = 0
        for p in selected:
            contest_id, index = p["contestId"], p["index"]
            slug = f"cf-{contest_id}-{index.lower()}"
            if db.scalar(select(Problem.id).where(Problem.slug == slug)):
                continue
            tags = p.get("tags", [])
            mapped = [PATTERN_MAP.get(tag, tag.replace("-", " ").title()) for tag in tags]
            rating = int(p.get("rating", 1200))
            difficulty = classify(rating)
            primary = mapped[0] if mapped else "Competitive Programming"
            db.add(Problem(
                slug=slug,
                title=p["name"],
                platform="Codeforces",
                url=f"https://codeforces.com/problemset/problem/{contest_id}/{index}",
                difficulty=difficulty,
                pattern=primary,
                topics=mapped or ["Competitive Programming"],
                time_complexity=None,
                space_complexity=None,
                description=f"Codeforces problem metadata: rating {rating}, tags {', '.join(tags) if tags else 'not tagged'}. The original statement and official judging remain on Codeforces.",
                source_licence="metadata-only; source terms apply",
                statement_rehosted=False,
            ))
            added += 1
        db.commit()
        final_counts = {d: db.scalar(select(func.count(Problem.id)).where(Problem.difficulty == d)) or 0 for d in TARGETS}
        final_total = db.scalar(select(func.count(Problem.id))) or 0
        print(f"Imported {added} Codeforces records. Final counts={final_counts}; total={final_total}")
        if any(final_counts[d] < TARGETS[d] for d in TARGETS):
            print("Note: a few source problems may already have existed; rerun the importer to fill remaining gaps.")


if __name__ == "__main__":
    main()
