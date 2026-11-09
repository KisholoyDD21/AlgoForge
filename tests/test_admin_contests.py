from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

import app.main as main


def _registered(client: TestClient, role: str = 'student') -> str:
    email = f"ops-{uuid.uuid4().hex[:12]}@example.com"
    response = client.post('/api/auth/register', json={
        'email': email, 'password': 'Secure-ops-password-1234', 'display_name': 'Ops Tester',
    })
    assert response.status_code == 200, response.text
    if role == 'admin':
        with main.SessionLocal() as db:
            user = db.scalar(select(main.User).where(main.User.email == email))
            user.role = 'admin'
            db.commit()
    return email


def _problem_payload(slug: str) -> dict:
    return {
        'slug': slug,
        'title': 'Test Problem for Admin',
        'difficulty': 'Easy',
        'pattern': 'Arrays',
        'topics': ['Arrays'],
        'description': 'Given an integer, print the same integer.',
        'constraints': '0 <= n <= 100',
        'time_complexity': 'O(1)',
        'space_complexity': 'O(1)',
        'hints': ['Read the input and print it.'],
        'examples': [{'input': '4\\n', 'output': '4\\n'}],
        'test_cases': [
            {'input': '4\\n', 'output': '4\\n', 'sample': True},
            {'input': '9\\n', 'output': '9\\n', 'sample': False},
        ],
    }


def test_admin_problem_create_update_and_delete():
    with TestClient(main.app) as client:
        _registered(client, role='admin')
        slug = f"admin-created-{uuid.uuid4().hex[:8]}"
        payload = _problem_payload(slug)
        created = client.post('/api/admin/problems', json=payload)
        assert created.status_code == 200, created.text
        assert created.json()['test_cases'] == 2

        updated_payload = _problem_payload(slug)
        updated_payload['title'] = 'Updated Admin Problem'
        updated_payload['test_cases'].append({'input': '3\\n', 'output': '3\\n', 'sample': False})
        updated = client.put(f'/api/admin/problems/{slug}', json=updated_payload)
        assert updated.status_code == 200, updated.text
        assert updated.json()['test_cases'] == 3

        listing = client.get('/api/admin/problems')
        match = next(row for row in listing.json()['items'] if row['slug'] == slug)
        assert match['title'] == 'Updated Admin Problem'
        assert match['test_cases'] == 3

        deleted = client.delete(f'/api/admin/problems/{slug}')
        assert deleted.status_code == 200, deleted.text
        assert deleted.json()['deleted'] == slug


def test_student_cannot_access_admin_problem_management():
    with TestClient(main.app) as client:
        _registered(client)
        assert client.get('/api/admin/problems').status_code == 403


def test_contest_registration_hides_problems_until_start_and_reveals_after():
    with TestClient(main.app) as client:
        _registered(client, role='admin')
        slug = f"practice-contest-{uuid.uuid4().hex[:8]}"
        starts = datetime.now(timezone.utc) + timedelta(hours=1)
        ends = starts + timedelta(hours=2)
        created = client.post('/api/admin/contests', json={
            'slug': slug,
            'title': 'Test Scheduled Contest',
            'description': 'Contest test fixture',
            'starts_at': starts.isoformat(),
            'ends_at': ends.isoformat(),
            'problem_slugs': ['af-running-sum'],
        })
        assert created.status_code == 200, created.text

        # Switch to a second account to test the public participant flow.
        with TestClient(main.app) as student:
            _registered(student)
            registered = student.post(f'/api/contests/{slug}/register')
            assert registered.status_code == 200, registered.text
            detail = student.get(f'/api/contests/{slug}').json()
            assert detail['registered'] is True
            assert detail['status'] == 'upcoming'
            assert detail['problems'] == []

            with main.SessionLocal() as db:
                contest = db.scalar(select(main.Contest).where(main.Contest.slug == slug))
                contest.starts_at = datetime.now(timezone.utc) - timedelta(minutes=1)
                contest.ends_at = datetime.now(timezone.utc) + timedelta(hours=1)
                db.commit()

            live_detail = student.get(f'/api/contests/{slug}').json()
            assert live_detail['status'] == 'live'
            assert [problem['slug'] for problem in live_detail['problems']] == ['af-running-sum']
            leaderboard = student.get(f'/api/contests/{slug}/leaderboard')
            assert leaderboard.status_code == 200
            assert leaderboard.json()['items'] == []


def test_profile_timezone_validation():
    with TestClient(main.app) as client:
        _registered(client)
        bad = client.put('/api/me', json={'display_name': 'Valid Name', 'timezone': 'Not/A_Timezone'})
        assert bad.status_code == 422
        good = client.put('/api/me', json={'display_name': 'Valid Name', 'timezone': 'Asia/Kolkata'})
        assert good.status_code == 200, good.text
        assert good.json()['user']['timezone'] == 'Asia/Kolkata'


def test_last_admin_cannot_delete_own_account():
    with TestClient(main.app) as client:
        email = _registered(client, role='admin')
        with main.SessionLocal() as db:
            current = db.scalar(select(main.User).where(main.User.email == email))
            # Other tests share the local test database; reduce the fixture to one admin.
            for other in db.scalars(select(main.User).where(main.User.role == 'admin', main.User.id != current.id)).all():
                other.role = 'student'
            db.commit()
        response = client.delete('/api/account')
        assert response.status_code == 409
        assert 'last admin' in response.json()['detail'].lower()
