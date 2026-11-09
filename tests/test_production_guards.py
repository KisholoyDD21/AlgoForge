import pytest

import app.main as main


class FakeRedis:
    def ping(self):
        return True


def _set_production_baseline(monkeypatch, *, judge_url="https://judge.private.example", judge_token="judge-secret"):
    monkeypatch.setattr(main, "APP_ENV", "production")
    monkeypatch.setattr(main, "DATABASE_URL", "postgresql+psycopg://app:secret@db:5432/algoforge")
    monkeypatch.setattr(main, "PUBLIC_BASE_URL", "https://practice.example")
    monkeypatch.setattr(main, "REDIS_URL", "redis://:redis-secret@redis:6379/0")
    monkeypatch.setattr(main, "redis_client", FakeRedis())
    monkeypatch.setattr(main, "JUDGE0_URL", judge_url)
    monkeypatch.setattr(main, "JUDGE0_TOKEN", judge_token)


def test_production_requires_postgresql(monkeypatch):
    _set_production_baseline(monkeypatch)
    monkeypatch.setattr(main, "DATABASE_URL", "sqlite:///./algoforge.db")
    with pytest.raises(RuntimeError, match="requires PostgreSQL"):
        main.startup()


def test_production_rejects_public_shared_judge0(monkeypatch):
    _set_production_baseline(monkeypatch, judge_url="https://ce.judge0.com", judge_token="")
    with pytest.raises(RuntimeError, match="public CE endpoint is development-only"):
        main.startup()


def test_production_requires_authenticated_judge0(monkeypatch):
    _set_production_baseline(monkeypatch, judge_token="")
    with pytest.raises(RuntimeError, match="requires JUDGE0_TOKEN"):
        main.startup()


def test_production_requires_password_protected_redis(monkeypatch):
    _set_production_baseline(monkeypatch)
    monkeypatch.setattr(main, "REDIS_URL", "redis://redis:6379/0")
    with pytest.raises(RuntimeError, match="Redis must require authentication"):
        main.startup()
