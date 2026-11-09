from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

import app.main as main


def _register(client: TestClient, name: str) -> str:
    email = f"community-{uuid.uuid4().hex[:10]}@example.com"
    result = client.post('/api/auth/register', json={
        'email': email,
        'password': 'Community-test-password-123',
        'display_name': name,
    })
    assert result.status_code == 200, result.text
    return email


def test_discussion_comment_vote_report_and_admin_moderation():
    with TestClient(main.app) as author:
        _register(author, 'Problem Author')
        created = author.post('/api/problems/af-running-sum/discussions', json={
            'title': 'Why does the prefix sum approach work?',
            'body': 'I understand the code but want to reason about the invariant.',
        })
        assert created.status_code == 200, created.text
        discussion_id = created.json()['id']
        self_vote = author.post(f'/api/discussions/{discussion_id}/vote', json={'value': 1})
        assert self_vote.status_code == 403

    with TestClient(main.app) as learner:
        _register(learner, 'Helpful Learner')
        comment = learner.post(f'/api/discussions/{discussion_id}/comments', json={
            'body': 'Each position stores the sum of all values up to that index.',
        })
        assert comment.status_code == 200, comment.text
        vote = learner.post(f'/api/discussions/{discussion_id}/vote', json={'value': 1})
        assert vote.status_code == 200 and vote.json()['score'] == 1
        report = learner.post(f'/api/discussions/{discussion_id}/report', json={
            'reason': 'Testing the community report queue for moderation.',
        })
        assert report.status_code == 200, report.text
        duplicate = learner.post(f'/api/discussions/{discussion_id}/report', json={
            'reason': 'Submitting the same report a second time.',
        })
        assert duplicate.status_code == 409
        visible = learner.get('/api/problems/af-running-sum/discussions').json()['items']
        assert len(visible) >= 1
        post = next(item for item in visible if item['id'] == discussion_id)
        assert post['score'] == 1
        assert post['comments'][0]['body'].startswith('Each position')

    with TestClient(main.app) as admin:
        admin_email = _register(admin, 'Community Moderator')
        with main.SessionLocal() as db:
            moderator = db.scalar(select(main.User).where(main.User.email == admin_email))
            moderator.role = 'admin'
            db.commit()
        reports = admin.get('/api/admin/discussion-reports')
        assert reports.status_code == 200
        assert any(item['discussion_id'] == discussion_id for item in reports.json()['items'])
        moderated = admin.post(f'/api/admin/discussions/{discussion_id}/moderate', json={'is_hidden': True})
        assert moderated.status_code == 200 and moderated.json()['is_hidden'] is True
        assert admin.get('/api/admin/discussion-reports').json()['items'] == []
        admin_view = admin.get('/api/problems/af-running-sum/discussions').json()['items']
        assert next(item for item in admin_view if item['id'] == discussion_id)['is_hidden'] is True

    with TestClient(main.app) as public_client:
        visible_after_hide = public_client.get('/api/problems/af-running-sum/discussions').json()['items']
        assert all(item['id'] != discussion_id for item in visible_after_hide)

    with TestClient(main.app) as blocked_user:
        _register(blocked_user, 'Blocked Commenter')
        hidden_comment = blocked_user.post(f'/api/discussions/{discussion_id}/comments', json={
            'body': 'This should not be accepted on a hidden post.',
        })
        assert hidden_comment.status_code == 404


def test_deleting_discussion_owner_removes_thread_children():
    with TestClient(main.app) as author:
        author_email = _register(author, 'Thread Owner')
        created = author.post('/api/problems/af-running-sum/discussions', json={
            'title': 'Account deletion cascade test',
            'body': 'This thread should be removed with its owner account.',
        })
        assert created.status_code == 200, created.text
        discussion_id = created.json()['id']

    with TestClient(main.app) as participant:
        _register(participant, 'Thread Participant')
        assert participant.post(f'/api/discussions/{discussion_id}/comments', json={
            'body': 'A reply from another account.',
        }).status_code == 200
        assert participant.post(f'/api/discussions/{discussion_id}/vote', json={'value': 1}).status_code == 200

    with TestClient(main.app) as deleting_owner:
        login = deleting_owner.post('/api/auth/login', json={
            'email': author_email, 'password': 'Community-test-password-123',
        })
        assert login.status_code == 200, login.text
        response = deleting_owner.delete('/api/account')
        assert response.status_code == 200, response.text

    with main.SessionLocal() as db:
        assert db.get(main.Discussion, discussion_id) is None
        assert db.scalar(select(main.DiscussionComment).where(main.DiscussionComment.discussion_id == discussion_id)) is None
        assert db.scalar(select(main.DiscussionVote).where(main.DiscussionVote.discussion_id == discussion_id)) is None
