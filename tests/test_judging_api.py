from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

import app.main as main


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeJudgeClient:
    next_poll_payload = None

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, *args, **kwargs):
        count = len(kwargs['json']['submissions'])
        return FakeResponse({'submissions': [{'token': f'case-token-{i}'} for i in range(count)]})

    async def get(self, *args, **kwargs):
        return FakeResponse(self.next_poll_payload)


def _register(client: TestClient) -> str:
    email = f"test-{uuid.uuid4().hex[:12]}@example.com"
    response = client.post('/api/auth/register', json={
        'email': email,
        'password': 'A-very-strong-test-password-17',
        'display_name': 'Judge Test',
    })
    assert response.status_code == 200, response.text
    return email


def test_native_submission_passes_all_cases_and_awards_progress(monkeypatch):
    monkeypatch.setattr(main, 'JUDGE0_URL', 'https://judge.example.test')
    monkeypatch.setattr(main.httpx, 'AsyncClient', FakeJudgeClient)
    FakeJudgeClient.next_poll_payload = {'submissions': [
        {'status': {'description': 'Accepted'}, 'stdout': '1 3 6 10 15\n', 'time': '0.01', 'memory': 1024},
        {'status': {'description': 'Accepted'}, 'stdout': '', 'time': '0.01', 'memory': 1024},
        {'status': {'description': 'Accepted'}, 'stdout': '', 'time': '0.01', 'memory': 1024},
        {'status': {'description': 'Accepted'}, 'stdout': '', 'time': '0.01', 'memory': 1024},
    ]}
    with TestClient(main.app) as client:
        _register(client)
        response = client.post('/api/problems/af-running-sum/submit', json={
            'language': 'python',
            'source_code': 'print("1 3 6 10 15")',
        })
        assert response.status_code == 200, response.text
        submission_id = response.json()['id']
        result = client.get(f'/api/submissions/{submission_id}/judge')
        assert result.status_code == 200, result.text
        assert result.json()['status'] == 'Accepted'
        assert result.json()['passed'] == result.json()['total'] == 4
        problem = client.get('/api/problems/af-running-sum').json()
        assert problem['progress'] == 'solved'


def test_wrong_answer_does_not_mark_problem_solved(monkeypatch):
    monkeypatch.setattr(main, 'JUDGE0_URL', 'https://judge.example.test')
    monkeypatch.setattr(main.httpx, 'AsyncClient', FakeJudgeClient)
    FakeJudgeClient.next_poll_payload = {'submissions': [
        {'status': {'description': 'Accepted'}, 'time': '0.01', 'memory': 1024},
        {'status': {'description': 'Wrong Answer'}, 'time': '0.01', 'memory': 1024},
        {'status': {'description': 'Accepted'}, 'time': '0.01', 'memory': 1024},
        {'status': {'description': 'Accepted'}, 'time': '0.01', 'memory': 1024},
    ]}
    with TestClient(main.app) as client:
        _register(client)
        response = client.post('/api/problems/af-running-sum/submit', json={
            'language': 'python',
            'source_code': 'print("incorrect")',
        })
        assert response.status_code == 200, response.text
        result = client.get(f"/api/submissions/{response.json()['id']}/judge")
        assert result.status_code == 200, result.text
        assert result.json()['status'] == 'Wrong Answer'
        problem = client.get('/api/problems/af-running-sum').json()
        assert problem['progress'] == 'todo'


def test_third_party_problem_cannot_be_submitted_to_algojudge(monkeypatch):
    monkeypatch.setattr(main, 'JUDGE0_URL', 'https://judge.example.test')
    with TestClient(main.app) as client:
        _register(client)
        response = client.post('/api/problems/two-sum/submit', json={
            'language': 'python',
            'source_code': 'print(0)',
        })
        assert response.status_code == 409
        assert 'third-party' in response.json()['detail'].lower()


def test_judge_poll_never_reveals_hidden_case_output(monkeypatch):
    monkeypatch.setattr(main, 'JUDGE0_URL', 'https://judge.example.test')
    monkeypatch.setattr(main.httpx, 'AsyncClient', FakeJudgeClient)
    FakeJudgeClient.next_poll_payload = {'submissions': [
        {'status': {'description': 'Wrong Answer'}, 'stdout': 'public sample output', 'stderr': 'sample stderr'},
        {'status': {'description': 'Wrong Answer'}, 'stdout': 'secret hidden output', 'stderr': 'secret hidden stderr'},
        {'status': {'description': 'Wrong Answer'}, 'stdout': 'secret hidden output 2'},
        {'status': {'description': 'Wrong Answer'}, 'stdout': 'secret hidden output 3'},
    ]}
    with TestClient(main.app) as client:
        _register(client)
        submitted = client.post('/api/problems/af-running-sum/submit', json={
            'language': 'python', 'source_code': 'print("not the answer")',
        })
        assert submitted.status_code == 200, submitted.text
        result = client.get(f"/api/submissions/{submitted.json()['id']}/judge")
        cases = result.json()['cases']
        assert cases[0]['sample'] is True
        assert cases[0]['stdout'] == 'public sample output'
        assert all(case['stdout'] is None and case['stderr'] is None for case in cases[1:])
        assert all(case['compile_output'] is None for case in cases[1:])
