from app.main import analyze_complexity, hash_password, verify_password
from app.seed_data import seed_rows


def test_password_hash_is_salted_and_verifies():
    first = hash_password('Secure-passphrase-123')
    second = hash_password('Secure-passphrase-123')
    assert first != second
    assert verify_password('Secure-passphrase-123', first)
    assert not verify_password('wrong-password', first)


def test_catalogue_seed_has_three_difficulty_levels_and_source_links():
    rows = seed_rows()
    assert len(rows) >= 100
    assert {row[2] for row in rows} == {'Easy', 'Medium', 'Hard'}
    assert all(row[5].startswith('https://') for row in rows)
    assert len({row[0] for row in rows}) == len(rows)


def test_complexity_estimator_flags_simple_linear_loop():
    result = analyze_complexity('for (int i = 0; i < n; i++) { total += i; }', 'cpp')
    assert result['estimated_time'] == 'O(n) likely'
    assert result['confidence'] == 'low'


def test_complexity_estimator_flags_nested_loops():
    code = 'for (int i=0; i<n; i++) { for (int j=0; j<n; j++) { work(); } }'
    result = analyze_complexity(code, 'cpp')
    assert result['estimated_time'] == 'O(n²) likely'


def test_complexity_estimator_discloses_limitations():
    result = analyze_complexity('print("hello")', 'python')
    assert result['method'] == 'static pattern heuristics'
    assert len(result['caveats']) >= 1


def test_problem_search_includes_topic_and_slug_metadata():
    from fastapi.testclient import TestClient
    import app.main as main

    with TestClient(main.app) as client:
        topic = client.get('/api/problems', params={'q': 'Prefix Sum', 'limit': 100})
        assert topic.status_code == 200
        assert any('Prefix Sum' in item['topics'] for item in topic.json()['items'])
        slug = client.get('/api/problems', params={'q': 'af-running-sum'})
        assert slug.status_code == 200
        assert any(item['slug'] == 'af-running-sum' for item in slug.json()['items'])
