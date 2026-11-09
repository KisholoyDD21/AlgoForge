from scripts.import_codeforces import classify, select_diverse


def test_codeforces_rating_buckets():
    assert classify(800) == "Easy"
    assert classify(1100) == "Easy"
    assert classify(1200) == "Medium"
    assert classify(1800) == "Medium"
    assert classify(1900) == "Hard"


def test_importer_balances_buckets_and_skips_existing_slugs():
    problems = [
        {"contestId": 1, "index": "A", "name": "Easy A", "rating": 800, "tags": ["implementation"], "type": "PROGRAMMING"},
        {"contestId": 1, "index": "B", "name": "Easy B", "rating": 1000, "tags": ["greedy"], "type": "PROGRAMMING"},
        {"contestId": 2, "index": "A", "name": "Medium A", "rating": 1300, "tags": ["dp"], "type": "PROGRAMMING"},
        {"contestId": 3, "index": "A", "name": "Hard A", "rating": 2000, "tags": ["graphs"], "type": "PROGRAMMING"},
        {"contestId": 4, "index": "A", "name": "Gym entry", "rating": 2200, "tags": ["graphs"], "type": "GYM"},
    ]
    stats = [
        {"contestId": 1, "index": "A", "solvedCount": 1000},
        {"contestId": 1, "index": "B", "solvedCount": 900},
        {"contestId": 2, "index": "A", "solvedCount": 700},
        {"contestId": 3, "index": "A", "solvedCount": 300},
    ]
    selected = select_diverse(
        problems,
        stats,
        {"Easy": 1, "Medium": 1, "Hard": 1},
        excluded_slugs={"cf-1-a"},
    )
    assert {classify(p["rating"]) for p in selected} == {"Easy", "Medium", "Hard"}
    assert all(f"cf-{p['contestId']}-{p['index'].lower()}" != "cf-1-a" for p in selected)
    assert all(p.get("type") == "PROGRAMMING" for p in selected)


def test_importer_defaults_to_non_destructive_dry_run_and_requires_explicit_apply():
    import inspect
    from scripts import import_codeforces

    source = inspect.getsource(import_codeforces.main)
    assert 'parser.add_argument("--apply", action="store_true"' in source
    assert 'if not args.apply:' in source
    assert 'DRY RUN ONLY' in source


def test_imported_records_are_metadata_only_and_keep_official_source_link():
    from scripts.import_codeforces import problem_record

    record = problem_record({
        "contestId": 1234,
        "index": "A",
        "name": "Example Task",
        "rating": 1200,
        "tags": ["two pointers", "implementation"],
    })
    assert record["slug"] == "cf-1234-a"
    assert record["difficulty"] == "Medium"
    assert record["url"] == "https://codeforces.com/problemset/problem/1234/A"
    assert record["statement_rehosted"] is False
    assert record["source_licence"].startswith("metadata-only")
    assert "original statement" in record["description"]


def test_catalogue_audit_detects_bad_provenance_and_urls():
    from scripts.audit_catalogue import audit_records

    report = audit_records([{
        "slug": "external-bad", "title": "Bad record", "platform": "Example",
        "pattern": "Arrays", "difficulty": "Impossible", "topics": [],
        "url": "http://example.com/problem", "source_licence": "",
        "statement_rehosted": True, "is_native": False,
    }])
    assert report['error_count'] >= 4
    assert report['warning_count'] >= 1
    messages = {issue['message'] for issue in report['issues']}
    assert 'Source URL must be an absolute HTTPS URL' in messages
    assert 'External problem is marked as rehosted' in messages
    assert 'External problem is missing source/licence provenance' in messages
