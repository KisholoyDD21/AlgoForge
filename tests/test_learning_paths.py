from __future__ import annotations

import uuid
from fastapi.testclient import TestClient

import app.main as main


def register(client: TestClient):
    email = f"paths-{uuid.uuid4().hex[:12]}@example.com"
    response = client.post('/api/auth/register', json={
        'email': email,
        'password': 'A-very-strong-test-password-2026',
        'display_name': 'Path Learner',
    })
    assert response.status_code == 200, response.text


def test_roadmaps_are_catalogue_backed_and_expose_real_question_links():
    with TestClient(main.app) as client:
        response = client.get('/api/roadmaps')
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['personalised'] is False
        assert len(data['items']) == 4
        foundations = next(path for path in data['items'] if path['slug'] == 'dsa-foundations')
        arrays = next(module for module in foundations['modules'] if module['id'] == 'arrays')
        assert arrays['total_problems'] > 0
        assert arrays['recommended']
        assert {'slug', 'title', 'difficulty', 'pattern', 'platform', 'is_native'} <= set(arrays['recommended'][0])
        assert arrays['status'] == 'ready'
        assert all('target_count' in module and 'prerequisites' in module for path in data['items'] for module in path['modules'])


def test_roadmap_progress_updates_from_recorded_problem_completion():
    with TestClient(main.app) as client:
        register(client)
        before = client.get('/api/roadmaps').json()
        foundation = next(path for path in before['items'] if path['slug'] == 'dsa-foundations')
        arrays = next(module for module in foundation['modules'] if module['id'] == 'arrays')
        chosen = arrays['recommended'][0]['slug']
        updated = client.post(f'/api/problems/{chosen}/progress', json={'status': 'solved'})
        assert updated.status_code == 200, updated.text
        after = client.get('/api/roadmaps').json()
        foundation_after = next(path for path in after['items'] if path['slug'] == 'dsa-foundations')
        arrays_after = next(module for module in foundation_after['modules'] if module['id'] == 'arrays')
        assert arrays_after['solved'] == 1
        assert arrays_after['progress_pct'] > 0
        assert arrays_after['status'] == 'in-progress'
        assert after['personalised'] is True
        assert 'self-reported' in after['progress_basis']


def test_prerequisite_unlock_requires_sixty_percent_of_module_target():
    with TestClient(main.app) as client:
        register(client)
        def graph_path():
            paths = client.get('/api/roadmaps').json()['items']
            return next(path for path in paths if path['slug'] == 'graph-algorithms')

        initial = graph_path()
        traversal = next(module for module in initial['modules'] if module['id'] == 'graph-traversal')
        components = next(module for module in initial['modules'] if module['id'] == 'components')
        assert traversal['target_count'] >= 2
        assert components['status'] == 'locked'
        for question in traversal['recommended'][:2]:
            response = client.post(f"/api/problems/{question['slug']}/progress", json={'status': 'solved'})
            assert response.status_code == 200, response.text
        refreshed = graph_path()
        traversal_after = next(module for module in refreshed['modules'] if module['id'] == 'graph-traversal')
        components_after = next(module for module in refreshed['modules'] if module['id'] == 'components')
        assert traversal_after['progress_pct'] >= 60
        assert components_after['unlocked'] is True
        assert components_after['status'] in {'ready', 'in-progress', 'complete'}
