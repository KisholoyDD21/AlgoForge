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
