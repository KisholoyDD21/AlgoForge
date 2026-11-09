# Catalogue governance

AlgoForge intentionally separates three kinds of problem records:

1. **AlgoForge originals** — platform-authored statements, examples and test suites that AlgoForge is entitled to host and judge.
2. **External metadata records** — title, platform, canonical URL, difficulty label and topic metadata. The original statement, examples, editorial and judging remain on the source platform.
3. **User progress records** — a learner's completion state. External completions are self-reported unless an authenticated source-platform integration is added in the future.

A public repository, an accessible URL or an API response is not by itself a licence to republish a problem statement, editorial, sample or hidden test. Do not import third-party problem content without documented permission or a licence that clearly permits the intended use.

## Difficulty labels

The Codeforces metadata importer applies these local buckets:

| Codeforces rating | AlgoForge label |
|---:|---|
| 800–1100 | Easy |
| 1200–1800 | Medium |
| 1900+ | Hard |

This is an AlgoForge heuristic for catalogue filtering, not an official Codeforces difficulty taxonomy or a universal mapping to interview difficulty. The importer selects rated programming problems and attempts to diversify by tags and solve counts. It does not constitute human editorial review.

## Safe import workflow

Run from the repository root after applying database migrations, on a machine with outbound HTTPS access:

```bash
python scripts/import_codeforces.py --report reports/codeforces-import-plan.json
```

Inspect the projected difficulty totals and sample records. The command is a dry run and does not insert catalogue rows. To apply the exact selected batch:

```bash
python scripts/import_codeforces.py --apply --report reports/codeforces-import-applied.json
```

The importer uses the official Codeforces problemset API and stores metadata plus canonical problem links only. It does not fetch statements, examples, editorials, solutions or tests.

## Audit workflow

```bash
python scripts/audit_catalogue.py --report reports/catalogue-audit.json
python scripts/audit_catalogue.py --strict
```

The audit is read-only. It checks duplicate slugs, required display metadata, allowed difficulty labels, topic tags, absolute HTTPS URLs for external records, and the boundary that external records must not be marked as rehosted. It cannot determine whether a third-party licence actually grants redistribution rights, whether an external URL is still live, whether a problem is pedagogically appropriate, or whether its difficulty label is accurate. Those checks still require human review.

## Release evidence

For a catalogue release, retain the import plan, applied import report, audit report and human review notes. Do not claim a 500-question catalogue until the database report confirms 500 unique records and the actual difficulty counts. Do not describe metadata-only records as AlgoForge-judged problems.
