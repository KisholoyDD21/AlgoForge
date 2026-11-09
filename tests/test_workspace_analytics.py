from __future__ import annotations

import uuid
from fastapi.testclient import TestClient

import app.main as main


class FakeResponse:
    def __init__(self, payload): self.payload = payload
    def raise_for_status(self): return None
    def json(self): return self.payload


class FakeJudgeClient:
    next_poll_payload = None
    last_post_json = None
    def __init__(self, *args, **kwargs): pass
    async def __aenter__(self): return self
    async def __aexit__(self, *args): return False
    async def post(self, *args, **kwargs):
        FakeJudgeClient.last_post_json = kwargs['json']
        count = len(kwargs['json']['submissions'])
        return FakeResponse({'submissions': [{'token': f'custom-token-{i}'} for i in range(count)]})
    async def get(self, *args, **kwargs): return FakeResponse(FakeJudgeClient.next_poll_payload)


def register(client: TestClient):
    email=f"ws-{uuid.uuid4().hex[:10]}@example.com"
    response=client.post('/api/auth/register',json={'email':email,'password':'A-very-strong-test-password-2026','display_name':'Workspace Test'})
    assert response.status_code==200,response.text
    return email


def test_dashboard_and_analytics_use_recorded_activity_not_sample_numbers():
    with TestClient(main.app) as client:
        register(client)
        unauth=TestClient(main.app)
        assert unauth.get('/api/analytics').status_code==401
        for slug in ('af-running-sum','af-maximum-pair-sum'):
            response=client.post(f'/api/problems/{slug}/progress',json={'status':'solved'})
            assert response.status_code==200,response.text
        dashboard=client.get('/api/dashboard').json()
        assert dashboard['total_active_days'] >= 1
        assert dashboard['contributions'] >= 2
        analytics=client.get('/api/analytics')
        assert analytics.status_code==200,analytics.text
        data=analytics.json()
        assert data['total_active_days'] >= 1
        assert data['contributions'] >= 2
        assert data['consistency']['active_days_last_7'] >= 1
        assert len(data['weekly_report'])==7
        assert data['pattern_mastery']
        assert data['topic_mastery']
        assert 'weak_topics' in data
        assert data['recommendations']
        assert 'method' in data['prediction']
        assert data['week_comparison']['current_week_solves'] >= 2
        assert 'previous_week_solves' in data['week_comparison']


def test_code_drafts_autosave_versions_and_restore_are_user_scoped():
    with TestClient(main.app) as client:
        register(client)
        first=client.put('/api/drafts/af-running-sum/cpp',json={'language':'cpp','source_code':'int main(){return 0;}','stdin':'1'})
        assert first.status_code==200,first.text
        second=client.put('/api/drafts/af-running-sum/cpp',json={'language':'cpp','source_code':'int main(){return 1;}','stdin':'2'})
        assert second.status_code==200,second.text
        versions=client.get('/api/drafts/af-running-sum/cpp/versions')
        assert versions.status_code==200,versions.text
        assert len(versions.json()['items'])==1
        version_id=versions.json()['items'][0]['id']
        restored=client.post('/api/drafts/af-running-sum/cpp/restore',json={'version_id':version_id})
        assert restored.status_code==200,restored.text
        assert restored.json()['source_code']=='int main(){return 0;}'
        current=client.get('/api/drafts/af-running-sum/cpp').json()['draft']
        assert current['stdin']=='1'
        # Function-mode drafts are scoped to a real native problem signature.
        function_draft=client.put('/api/drafts/af-running-sum%3A%3Afunction/python',json={'language':'python','source_code':'class Solution: pass','stdin':''})
        assert function_draft.status_code==200,function_draft.text
        assert client.get('/api/drafts/not-a-problem%3A%3Afunction/python').status_code==404
        assert client.put('/api/drafts/not-a-problem%3A%3Afunction/python',json={'language':'python','source_code':'x','stdin':''}).status_code==404
        # A different account cannot see or restore the first account's versions.
        with TestClient(main.app) as other:
            register(other)
            assert other.get('/api/drafts/af-running-sum/cpp/versions').json()['items']==[]
            assert other.post('/api/drafts/af-running-sum/cpp/restore',json={'version_id':version_id}).status_code==404


def test_custom_test_runner_returns_each_case_output_without_marking_problem_solved(monkeypatch):
    monkeypatch.setattr(main,'JUDGE0_URL','https://judge.example.test')
    monkeypatch.setattr(main.httpx,'AsyncClient',FakeJudgeClient)
    FakeJudgeClient.next_poll_payload={'submissions':[
        {'status':{'description':'Accepted'},'stdout':'1 3 6\n','time':'0.01','memory':1024},
        {'status':{'description':'Accepted'},'stdout':'2 4\n','time':'0.02','memory':2048},
    ]}
    with TestClient(main.app) as client:
        register(client)
        started=client.post('/api/problems/af-running-sum/run-custom',json={
            'language':'python','source_code':'print("test")','mode':'stdin',
            'test_cases':[{'input':'3\n1 2 3\n','expected_output':'1 3 6\n'},{'input':'2\n2 2\n'}],
        })
        assert started.status_code==200,started.text
        submission_id=started.json()['id']
        result=client.get(f'/api/submissions/{submission_id}/judge')
        assert result.status_code==200,result.text
        body=result.json()
        assert body['status']=='Executed'
        assert body['total']==2
        assert body['cases'][0]['passed'] is True
        assert body['cases'][1]['passed'] is None
        assert body['compared_total']==1
        assert body['execution_only_total']==1
        assert body['cases'][0]['stdout']=='1 3 6\n'
        # Custom execution is not the private full-suite submit operation.
        problem=client.get('/api/problems/af-running-sum').json()
        assert problem['progress']=='todo'


def test_function_mode_wraps_user_method_in_trusted_runner(monkeypatch):
    monkeypatch.setattr(main,'JUDGE0_URL','https://judge.example.test')
    monkeypatch.setattr(main.httpx,'AsyncClient',FakeJudgeClient)
    with TestClient(main.app) as client:
        register(client)
        problem=client.get('/api/problems/af-running-sum').json()
        assert problem['function_mode_supported'] is True
        source='''from typing import List\nclass Solution:\n    def runningSum(self, nums: List[int]) -> List[int]:\n        result=[]\n        total=0\n        for value in nums:\n            total += value\n            result.append(total)\n        return result\n'''
        response=client.post('/api/problems/af-running-sum/submit',json={'language':'python','source_code':source,'mode':'function'})
        assert response.status_code==200,response.text
        submitted=FakeJudgeClient.last_post_json['submissions'][0]['source_code']
        assert 'Solution().runningSum' in submitted
        assert submitted.startswith(source)
        other=client.get('/api/problems/af-maximum-subarray').json()
        assert other['function_mode_supported'] is True


def test_custom_test_payload_limits_and_language_validation():
    with TestClient(main.app) as client:
        register(client)
        too_many=[{'input':'1','expected_output':'1'} for _ in range(21)]
        response=client.post('/api/problems/af-running-sum/run-custom',json={'language':'python','source_code':'print(1)','test_cases':too_many})
        assert response.status_code==422
        bad_lang=client.post('/api/problems/af-running-sum/run-custom',json={'language':'javascript','source_code':'console.log(1)','test_cases':[{'input':'1'}]})
        assert bad_lang.status_code==422


def test_function_workspace_is_advertised_only_for_supported_original_problems():
    with TestClient(main.app) as client:
        register(client)
        for slug in ('af-running-sum', 'af-maximum-pair-sum', 'af-binary-search-index', 'af-missing-number', 'af-valid-parentheses', 'af-maximum-subarray', 'af-longest-unique-substring'):
            result = client.get(f'/api/problems/{slug}')
            assert result.status_code == 200
            assert result.json()['function_mode_supported'] is True
        unsupported = client.get('/api/problems/af-subarray-sum-count')
        assert unsupported.status_code == 200
        assert unsupported.json()['function_mode_supported'] is False
