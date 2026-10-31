from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from contextlib import asynccontextmanager
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from dotenv import load_dotenv
try:
    import redis as redis_lib
except ImportError:  # Local unit-test environments may omit the optional production extra.
    redis_lib = None
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

from .seed_data import seed_rows
from .native_problems import native_problems

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT.parent / ".env")
APP_ENV = os.getenv("APP_ENV", "development").lower()
APP_NAME = os.getenv("APP_NAME", "AlgoForge")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./algoforge.db")
JUDGE0_URL = os.getenv("JUDGE0_URL", "").strip().rstrip("/")
JUDGE0_TOKEN = os.getenv("JUDGE0_TOKEN", "").strip()
JUDGE0_TIMEOUT_SECONDS = max(5, min(60, int(os.getenv("JUDGE0_TIMEOUT_SECONDS", "20"))))
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true" or APP_ENV == "production"
SESSION_TTL_DAYS = int(os.getenv("SESSION_TTL_DAYS", "7"))
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
REDIS_URL = os.getenv("REDIS_URL", "").strip()
redis_client = redis_lib.Redis.from_url(REDIS_URL, decode_responses=True) if REDIS_URL and redis_lib else None

engine_kwargs: dict[str, Any] = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(80))
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(20), default="student")
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class Problem(Base):
    __tablename__ = "problems"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(240), index=True)
    platform: Mapped[str] = mapped_column(String(80), index=True)
    url: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(12), index=True)
    pattern: Mapped[str] = mapped_column(String(100), index=True)
    topics: Mapped[list] = mapped_column(JSON, default=list)
    time_complexity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    space_complexity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    source_licence: Mapped[str] = mapped_column(String(80), default="metadata-only")
    statement_rehosted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_native: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    constraints: Mapped[str] = mapped_column(Text, default="")
    examples: Mapped[list] = mapped_column(JSON, default=list)
    hints: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ProblemTestCase(Base):
    __tablename__ = "problem_test_cases"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), index=True)
    input_data: Mapped[str] = mapped_column(Text, default="")
    expected_output: Mapped[str] = mapped_column(Text, default="")
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int] = mapped_column(Integer, default=0)


class Contest(Base):
    __tablename__ = "contests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)


class ContestProblem(Base):
    __tablename__ = "contest_problems"
    __table_args__ = (UniqueConstraint("contest_id", "problem_id", name="uq_contest_problem"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id", ondelete="CASCADE"), index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), index=True)
    points: Mapped[int] = mapped_column(Integer, default=100)
    position: Mapped[int] = mapped_column(Integer, default=0)


class ContestParticipant(Base):
    __tablename__ = "contest_participants"
    __table_args__ = (UniqueConstraint("contest_id", "user_id", name="uq_contest_participant"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DailyChallenge(Base):
    __tablename__ = "daily_challenges"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    challenge_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UserProgress(Base):
    __tablename__ = "user_progress"
    __table_args__ = (UniqueConstraint("user_id", "problem_id", name="uq_user_problem_progress"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="todo")
    source: Mapped[str] = mapped_column(String(40), default="self_reported_external")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Activity(Base):
    __tablename__ = "daily_activity"
    __table_args__ = (UniqueConstraint("user_id", "activity_date", name="uq_user_activity_day"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    activity_date: Mapped[date] = mapped_column(Date, index=True)
    solved_count: Mapped[int] = mapped_column(Integer, default=0)


class Bookmark(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("user_id", "problem_id", name="uq_user_problem_bookmark"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Note(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), index=True)
    content: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Discussion(Base):
    __tablename__ = "discussions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    body: Mapped[str] = mapped_column(Text)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class DiscussionComment(Base):
    __tablename__ = "discussion_comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    discussion_id: Mapped[int] = mapped_column(ForeignKey("discussions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class DiscussionVote(Base):
    __tablename__ = "discussion_votes"
    __table_args__ = (UniqueConstraint("discussion_id", "user_id", name="uq_discussion_vote"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    discussion_id: Mapped[int] = mapped_column(ForeignKey("discussions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    value: Mapped[int] = mapped_column(Integer)


class DiscussionReport(Base):
    __tablename__ = "discussion_reports"
    __table_args__ = (UniqueConstraint("discussion_id", "user_id", name="uq_discussion_report"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    discussion_id: Mapped[int] = mapped_column(ForeignKey("discussions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    reason: Mapped[str] = mapped_column(String(1000))
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class Submission(Base):
    __tablename__ = "submissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    problem_id: Mapped[int | None] = mapped_column(ForeignKey("problems.id", ondelete="SET NULL"), nullable=True, index=True)
    language: Mapped[str] = mapped_column(String(24))
    source_code: Mapped[str] = mapped_column(Text)
    stdin: Mapped[str] = mapped_column(Text, default="")
    judge_token: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    access_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    judge_tokens: Mapped[list] = mapped_column(JSON, default=list)
    case_results: Mapped[list] = mapped_column(JSON, default=list)
    custom_test_cases: Mapped[list] = mapped_column(JSON, default=list)
    contest_id: Mapped[int | None] = mapped_column(ForeignKey("contests.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(48), default="Queued")
    stdout: Mapped[str] = mapped_column(Text, default="")
    stderr: Mapped[str] = mapped_column(Text, default="")
    compile_output: Mapped[str] = mapped_column(Text, default="")
    time_seconds: Mapped[str | None] = mapped_column(String(40), nullable=True)
    memory_kb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    complexity: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class CodeDraft(Base):
    __tablename__ = "code_drafts"
    __table_args__ = (UniqueConstraint("user_id", "problem_key", "language", name="uq_code_draft_user_problem_language"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    problem_key: Mapped[str] = mapped_column(String(180), index=True)
    language: Mapped[str] = mapped_column(String(24))
    source_code: Mapped[str] = mapped_column(Text, default="")
    stdin: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class CodeDraftVersion(Base):
    __tablename__ = "code_draft_versions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("code_drafts.id", ondelete="CASCADE"), index=True)
    source_code: Mapped[str] = mapped_column(Text)
    stdin: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class RegisterBody(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    display_name: str = Field(min_length=2, max_length=80)


class LoginBody(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ProgressBody(BaseModel):
    status: str = Field(pattern="^(todo|in_progress|solved)$")


class NoteBody(BaseModel):
    content: str = Field(max_length=8000)


class RunBody(BaseModel):
    language: str = Field(pattern="^(c|cpp|java|python)$")
    source_code: str = Field(min_length=1, max_length=25000)
    stdin: str = Field(default="", max_length=8000)
    problem_slug: str | None = None


class SubmitBody(BaseModel):
    language: str = Field(pattern="^(c|cpp|java|python)$")
    source_code: str = Field(min_length=1, max_length=25000)
    contest_slug: str | None = None
    mode: str = Field(default="stdin", pattern="^(stdin|function)$")


class CustomTestCaseBody(BaseModel):
    input: str = Field(default="", max_length=12000)
    expected_output: str | None = Field(default=None, max_length=12000)


class CustomRunBody(BaseModel):
    language: str = Field(pattern="^(c|cpp|java|python)$")
    source_code: str = Field(min_length=1, max_length=25000)
    mode: str = Field(default="stdin", pattern="^(stdin|function)$")
    test_cases: list[CustomTestCaseBody] = Field(min_length=1, max_length=20)


class DraftSaveBody(BaseModel):
    language: str = Field(pattern="^(c|cpp|java|python)$")
    source_code: str = Field(max_length=25000)
    stdin: str = Field(default="", max_length=12000)


class DraftRestoreBody(BaseModel):
    version_id: int


class AdminProblemBody(BaseModel):
    slug: str = Field(pattern="^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=160)
    title: str = Field(min_length=3, max_length=240)
    difficulty: str = Field(pattern="^(Easy|Medium|Hard)$")
    pattern: str = Field(min_length=2, max_length=100)
    topics: list[str] = Field(default_factory=list, max_length=12)
    description: str = Field(min_length=10, max_length=15000)
    constraints: str = Field(default="", max_length=2000)
    time_complexity: str = Field(default="", max_length=100)
    space_complexity: str = Field(default="", max_length=100)
    hints: list[str] = Field(default_factory=list, max_length=8)
    examples: list[dict[str, str]] = Field(default_factory=list, max_length=5)
    test_cases: list[dict[str, str | bool]] = Field(min_length=2, max_length=100)


class ContestCreateBody(BaseModel):
    slug: str = Field(pattern="^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=160)
    title: str = Field(min_length=3, max_length=180)
    description: str = Field(default="", max_length=3000)
    starts_at: datetime
    ends_at: datetime
    problem_slugs: list[str] = Field(min_length=1, max_length=20)


class ProfileBody(BaseModel):
    display_name: str = Field(min_length=2, max_length=80)
    timezone: str = Field(default="Asia/Kolkata", max_length=64)


class DiscussionCreateBody(BaseModel):
    title: str = Field(min_length=5, max_length=180)
    body: str = Field(min_length=10, max_length=8000)


class DiscussionCommentBody(BaseModel):
    body: str = Field(min_length=2, max_length=4000)


class DiscussionVoteBody(BaseModel):
    value: int = Field(ge=-1, le=1)


class DiscussionReportBody(BaseModel):
    reason: str = Field(min_length=10, max_length=1000)


class DiscussionModerationBody(BaseModel):
    is_hidden: bool


@asynccontextmanager
async def lifespan(application: FastAPI):
    startup()
    yield


app = FastAPI(title=APP_NAME, version="0.4.0", docs_url=None if APP_ENV == "production" else "/api/docs", redoc_url=None, lifespan=lifespan)

# Small per-process limiter; production deployments should put a shared limiter (e.g. Redis) in front.
_rate_buckets: dict[str, list[float]] = defaultdict(list)


def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=64)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, salt_hex, digest_hex = stored.split("$", 2)
        if algorithm != "scrypt":
            return False
        candidate = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1, dklen=64)
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except Exception:
        return False


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def issue_session(response: Response, db: Session, user: User) -> None:
    raw = secrets.token_urlsafe(36)
    expires = datetime.now(timezone.utc) + timedelta(days=SESSION_TTL_DAYS)
    db.add(AuthSession(user_id=user.id, token_hash=token_digest(raw), expires_at=expires))
    db.commit()
    response.set_cookie(
        "algoforge_session", raw, httponly=True, secure=COOKIE_SECURE,
        samesite="lax", max_age=SESSION_TTL_DAYS * 86400, path="/",
    )


def get_optional_user(request: Request, db: Session = Depends(db_session)) -> User | None:
    raw = request.cookies.get("algoforge_session")
    if not raw:
        return None
    session_row = db.scalar(select(AuthSession).where(AuthSession.token_hash == token_digest(raw)))
    if not session_row:
        return None
    # SQLite may return a naive datetime; compare in UTC safely.
    expiry = session_row.expires_at
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if expiry <= datetime.now(timezone.utc):
        db.delete(session_row)
        db.commit()
        return None
    return db.get(User, session_row.user_id)


def require_user(user: User | None = Depends(get_optional_user)) -> User:
    if not user:
        raise HTTPException(401, "Sign in to use this feature.")
    return user


def require_admin(user: User = Depends(require_user)) -> User:
    if user.role != "admin":
        raise HTTPException(403, "Administrator access required.")
    return user


def _today_for(user: User) -> date:
    try:
        tz = ZoneInfo(user.timezone or "Asia/Kolkata")
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")
    return datetime.now(tz).date()


def _problem_dict(problem: Problem, progress: dict[int, str] | None = None, bookmarks: set[int] | None = None) -> dict[str, Any]:
    return {
        "id": problem.id, "slug": problem.slug, "title": problem.title,
        "platform": problem.platform, "url": problem.url, "difficulty": problem.difficulty,
        "pattern": problem.pattern, "topics": problem.topics or [],
        "time_complexity": problem.time_complexity, "space_complexity": problem.space_complexity,
        "description": problem.description,
        "function_mode_supported": bool(problem.is_native and problem.slug in FUNCTION_PROBLEM_SLUGS),
        "is_native": bool(problem.is_native),
        "constraints": problem.constraints or "",
        "examples": problem.examples or [],
        "hints": problem.hints or [],
        "progress": (progress or {}).get(problem.id, "todo"),
        "bookmarked": problem.id in (bookmarks or set()),
    }


def analyze_complexity(source: str, language: str) -> dict[str, Any]:
    """Conservative heuristic estimator; not a proof of asymptotic complexity."""
    normalized = re.sub(r"//.*?$|#.*?$|/\*.*?\*/", " ", source, flags=re.M | re.S)
    loop_matches = list(re.finditer(r"\b(for|while|foreach)\b", normalized, re.I))
    loop_ranges: list[tuple[int, int]] = []
    for match in loop_matches:
        open_brace = normalized.find("{", match.end())
        next_semicolon = normalized.find(";", match.end())
        if open_brace >= 0 and (next_semicolon < 0 or open_brace < next_semicolon + 120):
            depth = 0
            close_brace = len(normalized) - 1
            for pos in range(open_brace, len(normalized)):
                if normalized[pos] == "{":
                    depth += 1
                elif normalized[pos] == "}":
                    depth -= 1
                    if depth == 0:
                        close_brace = pos
                        break
            loop_ranges.append((match.start(), close_brace))
        else:
            line_end = normalized.find("\n", match.end())
            loop_ranges.append((match.start(), line_end if line_end >= 0 else len(normalized)))
    max_depth = 0
    for match in loop_matches:
        enclosing = sum(1 for start, end in loop_ranges if start <= match.start() <= end)
        max_depth = max(max_depth, enclosing)
    has_sort = bool(re.search(r"\b(sort|stable_sort|Arrays\.sort|Collections\.sort|sorted)\s*\(", normalized))
    has_recursion = False
    fn_names: list[str] = []
    if language == "python":
        fn_names = re.findall(r"\bdef\s+(\w+)\s*\(", normalized)
    else:
        fn_names = re.findall(r"(?:\b\w+[\*&\s]+)+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{", normalized)
    has_recursion = any(re.search(rf"\b{re.escape(name)}\s*\(", normalized[normalized.find(name) + len(name):]) for name in fn_names)
    if len(loop_matches) == 0 and not has_sort and not has_recursion:
        time_guess = "O(1) likely"
    elif max_depth >= 2 and max_depth >= 3:
        time_guess = "O(n³) or higher"
    elif max_depth >= 2:
        time_guess = "O(n²) likely"
    elif has_sort:
        time_guess = "O(n log n) likely"
    elif has_recursion and len(loop_matches) == 0:
        time_guess = "Recurrence-dependent"
    else:
        time_guess = "O(n) likely"
    has_dynamic_storage = bool(re.search(r"\b(vector|array|list|dict|set|map|unordered_map|unordered_set|new\s+\w+\s*\[|\[\s*\])\b", normalized, re.I))
    space_guess = "O(n) likely" if has_dynamic_storage else "O(1) likely"
    caveats = [
        "This is a source-code heuristic, not a formal proof. Input-size relationships and library internals may change the result.",
        "Benchmark time and memory are returned separately by the execution service and are hardware/runtime dependent.",
    ]
    return {"estimated_time": time_guess, "estimated_space": space_guess, "confidence": "low", "method": "static pattern heuristics", "caveats": caveats}


def _status_from_judge(payload: dict[str, Any]) -> tuple[str, str, str, str, int | None]:
    status = (payload.get("status") or {}).get("description", "Processing")
    # Judge0 status 3 means the program exited successfully, not that a problem was solved.
    if status == "Accepted":
        status = "Executed"
    return (
        status,
        payload.get("stdout") or "",
        payload.get("stderr") or "",
        payload.get("compile_output") or "",
        payload.get("memory"),
    )


def _check_same_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if not origin:
        return
    host = request.headers.get("host", "")
    parsed = urlparse(origin)
    if parsed.netloc != host:
        raise HTTPException(403, "Cross-origin request rejected.")


def _rate_limit(request: Request, key: str, limit: int, window: int = 60) -> None:
    ip = request.client.host if request.client else "unknown"
    bucket_key = f"{key}:{ip}"
    if REDIS_URL:
        if redis_client is None:
            raise HTTPException(503, "Shared rate limiter is not available.")
        try:
            redis_key = f"algoforge:rate:{bucket_key}"
            count = redis_client.incr(redis_key)
            if count == 1:
                redis_client.expire(redis_key, window)
            if count > limit:
                raise HTTPException(429, "Too many requests. Please retry shortly.")
            return
        except HTTPException:
            raise
        except Exception:
            # Fail closed when production depends on the shared limiter.
            if APP_ENV == "production":
                raise HTTPException(503, "Shared rate limiter is temporarily unavailable.")
    now = time.time()
    _rate_buckets[bucket_key] = [t for t in _rate_buckets[bucket_key] if now - t < window]
    if len(_rate_buckets[bucket_key]) >= limit:
        raise HTTPException(429, "Too many requests. Please retry shortly.")
    _rate_buckets[bucket_key].append(now)


def startup() -> None:
    if APP_ENV == "production":
        if not DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg://")):
            raise RuntimeError("Production requires PostgreSQL; SQLite is for local development only.")
        if not PUBLIC_BASE_URL.startswith("https://"):
            raise RuntimeError("Production requires PUBLIC_BASE_URL to use HTTPS.")
        if not REDIS_URL or redis_client is None:
            raise RuntimeError("Production requires REDIS_URL and the redis Python package for shared rate limiting.")
        redis_password = urlparse(REDIS_URL).password
        if not redis_password:
            raise RuntimeError("Production Redis must require authentication; include a password in REDIS_URL.")
        judge_parsed = urlparse(JUDGE0_URL) if JUDGE0_URL else None
        judge_host = (judge_parsed.hostname or "").lower() if judge_parsed else ""
        if not JUDGE0_URL or judge_parsed.scheme != "https" or judge_host in {"ce.judge0.com", "judge0.com"}:
            raise RuntimeError("Production requires a privately operated or contracted HTTPS Judge0 service; the public CE endpoint is development-only.")
        if judge_parsed.username or judge_parsed.password:
            raise RuntimeError("Do not put Judge0 credentials in the URL; configure JUDGE0_TOKEN as a server-side secret.")
        if not JUDGE0_TOKEN:
            raise RuntimeError("Production requires JUDGE0_TOKEN and an authenticated Judge0 API.")
        bootstrap_password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")
        if bootstrap_password and len(bootstrap_password) < 16:
            raise RuntimeError("BOOTSTRAP_ADMIN_PASSWORD must be at least 16 characters when creating the first administrator.")
        try:
            redis_client.ping()
        except Exception as exc:
            raise RuntimeError("Configured Redis service is not reachable.") from exc
    if APP_ENV != "production" or os.getenv("AUTO_CREATE_SCHEMA", "false").lower() == "true":
        Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for row in seed_rows():
            slug, title, difficulty, pattern, topics, url, tc, sc = row[:8]
            source_platform = row[8] if len(row) > 8 else "LeetCode"
            existing = db.scalar(select(Problem).where(Problem.slug == slug))
            if not existing:
                db.add(Problem(
                    slug=slug, title=title, difficulty=difficulty, pattern=pattern,
                    topics=topics, url=url, time_complexity=tc, space_complexity=sc,
                    platform=source_platform, description="Third-party problem metadata only. Open the source platform for the original statement and official judge.",
                    source_licence="metadata-only", statement_rehosted=False, is_native=False,
                ))
        db.flush()
        # Original AlgoForge exercises have licensed statements and platform-owned tests.
        for item in native_problems():
            problem = db.scalar(select(Problem).where(Problem.slug == item["slug"]))
            if not problem:
                problem = Problem(
                    slug=item["slug"], title=item["title"], difficulty=item["difficulty"],
                    pattern=item["pattern"], topics=item["topics"], url=f"{PUBLIC_BASE_URL}/#/problem/{item['slug']}",
                    time_complexity=item["time_complexity"], space_complexity=item["space_complexity"],
                    description=item["description"], platform="AlgoForge Originals",
                    source_licence="Original AlgoForge content", statement_rehosted=True, is_native=True,
                    constraints=item["constraints"], examples=item["examples"], hints=item["hints"],
                )
                db.add(problem)
                db.flush()
            if db.scalar(select(func.count(ProblemTestCase.id)).where(ProblemTestCase.problem_id == problem.id)) == 0:
                for position, (input_data, expected_output, is_sample) in enumerate(item["tests"]):
                    db.add(ProblemTestCase(problem_id=problem.id, input_data=input_data, expected_output=expected_output, is_sample=is_sample, position=position))
        admin_email = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
        admin_password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")
        if admin_email and admin_password and not db.scalar(select(User).where(User.email == admin_email)):
            db.add(User(email=admin_email, display_name="Platform Admin", password_hash=hash_password(admin_password), role="admin"))
        if APP_ENV != "production" and not db.scalar(select(User).where(User.email == "demo@algoforge.dev")):
            db.add(User(email="demo@algoforge.dev", display_name="Demo Learner", password_hash=hash_password("demo-pass-123"), role="student"))
        db.commit()
        if APP_ENV == "production" and not db.scalar(select(User.id).where(User.role == "admin").limit(1)):
            raise RuntimeError("No administrator exists. Set BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD for the first launch.")
    finally:
        db.close()


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; script-src 'self' https://cdnjs.cloudflare.com; worker-src 'self' blob:; "
        "connect-src 'self' https://cdnjs.cloudflare.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    if APP_ENV == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response


@app.get("/api/health")
def health(db: Session = Depends(db_session)):
    return {"ok": True, "app": APP_NAME, "database": "connected", "judge_configured": bool(JUDGE0_URL), "question_count": db.scalar(select(func.count(Problem.id))) or 0}


@app.post("/api/auth/register")
def register(body: RegisterBody, response: Response, request: Request, db: Session = Depends(db_session)):
    _check_same_origin(request)
    _rate_limit(request, "register", 5)
    email = body.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "An account with this email already exists.")
    user = User(email=email, display_name=body.display_name.strip(), password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    issue_session(response, db, user)
    return {"user": {"id": user.id, "email": user.email, "display_name": user.display_name, "role": user.role}}


@app.post("/api/auth/login")
def login(body: LoginBody, response: Response, request: Request, db: Session = Depends(db_session)):
    _check_same_origin(request)
    _rate_limit(request, "login", 10)
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Email or password is incorrect.")
    issue_session(response, db, user)
    return {"user": {"id": user.id, "email": user.email, "display_name": user.display_name, "role": user.role}}


@app.post("/api/auth/logout")
def logout(request: Request, response: Response, db: Session = Depends(db_session)):
    _check_same_origin(request)
    raw = request.cookies.get("algoforge_session")
    if raw:
        row = db.scalar(select(AuthSession).where(AuthSession.token_hash == token_digest(raw)))
        if row:
            db.delete(row)
            db.commit()
    response.delete_cookie("algoforge_session", path="/")
    return {"ok": True}


@app.get("/api/me")
def me(user: User | None = Depends(get_optional_user)):
    if not user:
        return {"user": None}
    return {"user": {"id": user.id, "email": user.email, "display_name": user.display_name, "role": user.role, "timezone": user.timezone}}


@app.get("/api/problems")
def list_problems(
    q: str = "", difficulty: str = "All", pattern: str = "All", platform: str = "All",
    status: str = "All", bookmarked: bool = False, limit: int = 30, offset: int = 0,
    user: User | None = Depends(get_optional_user), db: Session = Depends(db_session),
):
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    query = select(Problem)
    if q.strip():
        term = f"%{q.strip()[:100]}%"
        query = query.where((Problem.title.ilike(term)) | (Problem.pattern.ilike(term)) | (Problem.platform.ilike(term)))
    if difficulty in {"Easy", "Medium", "Hard"}:
        query = query.where(Problem.difficulty == difficulty)
    if pattern != "All":
        query = query.where(Problem.pattern == pattern)
    if platform != "All":
        query = query.where(Problem.platform == platform)
    progress_map: dict[int, str] = {}
    bookmark_ids: set[int] = set()
    if user:
        rows = db.scalars(select(UserProgress).where(UserProgress.user_id == user.id)).all()
        progress_map = {r.problem_id: r.status for r in rows}
        bookmark_ids = set(db.scalars(select(Bookmark.problem_id).where(Bookmark.user_id == user.id)).all())
    if status in {"todo", "in_progress", "solved"}:
        if user:
            problem_ids = [pid for pid, st in progress_map.items() if st == status]
            query = query.where(Problem.id.in_(problem_ids) if problem_ids else Problem.id == -1)
        else:
            query = query.where(Problem.id == -1)
    if bookmarked:
        query = query.where(Problem.id.in_(bookmark_ids) if bookmark_ids else Problem.id == -1)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(query.order_by(Problem.difficulty, Problem.title).offset(offset).limit(limit)).all()
    return {"items": [_problem_dict(p, progress_map, bookmark_ids) for p in rows], "total": total, "limit": limit, "offset": offset}


@app.get("/api/problems/{slug}")
def get_problem(slug: str, user: User | None = Depends(get_optional_user), db: Session = Depends(db_session)):
    problem = db.scalar(select(Problem).where(Problem.slug == slug))
    if not problem:
        raise HTTPException(404, "Problem not found.")
    progress = "todo"
    bookmarked = False
    if user:
        p = db.scalar(select(UserProgress).where(UserProgress.user_id == user.id, UserProgress.problem_id == problem.id))
        progress = p.status if p else "todo"
        bookmarked = db.scalar(select(Bookmark.id).where(Bookmark.user_id == user.id, Bookmark.problem_id == problem.id)) is not None
    result = _problem_dict(problem, {problem.id: progress}, {problem.id} if bookmarked else set())
    if problem.is_native:
        samples = db.scalars(select(ProblemTestCase).where(ProblemTestCase.problem_id == problem.id, ProblemTestCase.is_sample.is_(True)).order_by(ProblemTestCase.position)).all()
        result["examples"] = [{"input": c.input_data, "output": c.expected_output} for c in samples]
    else:
        result["examples"] = []
        result["hints"] = []
        result["constraints"] = ""
    return result


@app.get("/api/platforms")
def platforms(db: Session = Depends(db_session)):
    values = db.scalars(select(Problem.platform).distinct().order_by(Problem.platform)).all()
    return {"items": values}


@app.get("/api/patterns")
def patterns(db: Session = Depends(db_session)):
    values = db.execute(select(Problem.pattern, func.count(Problem.id)).group_by(Problem.pattern).order_by(Problem.pattern)).all()
    return {"items": [{"name": name, "count": count} for name, count in values]}


@app.get("/api/dashboard")
def dashboard(user: User | None = Depends(get_optional_user), db: Session = Depends(db_session)):
    total = db.scalar(select(func.count(Problem.id))) or 0
    if not user:
        return {"user": None, "total_questions": total, "solved": 0, "easy": 0, "medium": 0, "hard": 0, "streak": 0, "longest_streak": 0, "activity": [], "recent": []}
    solved_rows = db.execute(select(Problem.difficulty, func.count(UserProgress.id)).join(UserProgress, UserProgress.problem_id == Problem.id).where(UserProgress.user_id == user.id, UserProgress.status == "solved").group_by(Problem.difficulty)).all()
    by_difficulty = {d.lower(): c for d, c in solved_rows}
    solved = sum(by_difficulty.values())
    activity_rows = db.scalars(select(Activity).where(Activity.user_id == user.id).order_by(Activity.activity_date.desc()).limit(365)).all()
    dates = {r.activity_date for r in activity_rows if r.solved_count > 0}
    today = _today_for(user)
    current = today if today in dates else today - timedelta(days=1)
    streak = 0
    while current in dates:
        streak += 1
        current -= timedelta(days=1)
    longest = 0
    run = 0
    previous = None
    for day in sorted(dates):
        run = run + 1 if previous and day == previous + timedelta(days=1) else 1
        longest = max(longest, run)
        previous = day
    activity = [{"date": r.activity_date.isoformat(), "count": r.solved_count} for r in reversed(activity_rows)]
    total_active_days = db.scalar(select(func.count(Activity.id)).where(Activity.user_id == user.id, Activity.solved_count > 0)) or 0
    contributions = db.scalar(select(func.coalesce(func.sum(Activity.solved_count), 0)).where(Activity.user_id == user.id)) or 0
    recent_rows = db.scalars(select(Submission).where(Submission.user_id == user.id).order_by(Submission.created_at.desc()).limit(5)).all()
    recent = [{"id": s.id, "language": s.language, "status": s.status, "created_at": s.created_at.isoformat(), "problem_id": s.problem_id} for s in recent_rows]
    return {"user": {"display_name": user.display_name, "email": user.email}, "total_questions": total, "solved": solved,
            "easy": by_difficulty.get("easy", 0), "medium": by_difficulty.get("medium", 0), "hard": by_difficulty.get("hard", 0),
            "streak": streak, "longest_streak": longest, "total_active_days": total_active_days,
            "contributions": int(contributions), "activity": activity, "recent": recent}


@app.post("/api/problems/{slug}/progress")
def update_progress(slug: str, body: ProgressBody, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    problem = db.scalar(select(Problem).where(Problem.slug == slug))
    if not problem:
        raise HTTPException(404, "Problem not found.")
    row = db.scalar(select(UserProgress).where(UserProgress.user_id == user.id, UserProgress.problem_id == problem.id))
    if not row:
        row = UserProgress(user_id=user.id, problem_id=problem.id)
        db.add(row)
    was_solved = bool(row and row.status == "solved")
    row.status = body.status
    row.source = "self_reported_external" if body.status == "solved" else "manual_progress"
    row.updated_at = datetime.now(timezone.utc)
    today = _today_for(user)
    activity = db.scalar(select(Activity).where(Activity.user_id == user.id, Activity.activity_date == today))
    if body.status == "solved" and not was_solved:
        if not activity:
            activity = Activity(user_id=user.id, activity_date=today, solved_count=0)
            db.add(activity)
        activity.solved_count += 1
    elif was_solved and body.status != "solved" and activity:
        activity.solved_count = max(0, activity.solved_count - 1)
        if activity.solved_count == 0:
            db.delete(activity)
    db.commit()
    return {"ok": True, "status": body.status, "source": row.source, "note": "External completion is self-reported; it is not verified by the source platform." if body.status == "solved" else None}


@app.post("/api/problems/{slug}/bookmark")
def toggle_bookmark(slug: str, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    problem = db.scalar(select(Problem).where(Problem.slug == slug))
    if not problem:
        raise HTTPException(404, "Problem not found.")
    row = db.scalar(select(Bookmark).where(Bookmark.user_id == user.id, Bookmark.problem_id == problem.id))
    if row:
        db.delete(row)
        bookmarked = False
    else:
        db.add(Bookmark(user_id=user.id, problem_id=problem.id))
        bookmarked = True
    db.commit()
    return {"bookmarked": bookmarked}


@app.get("/api/problems/{slug}/note")
def get_note(slug: str, user: User = Depends(require_user), db: Session = Depends(db_session)):
    problem = db.scalar(select(Problem).where(Problem.slug == slug))
    if not problem:
        raise HTTPException(404, "Problem not found.")
    note = db.scalar(select(Note).where(Note.user_id == user.id, Note.problem_id == problem.id))
    return {"content": note.content if note else ""}


@app.put("/api/problems/{slug}/note")
def save_note(slug: str, body: NoteBody, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    problem = db.scalar(select(Problem).where(Problem.slug == slug))
    if not problem:
        raise HTTPException(404, "Problem not found.")
    note = db.scalar(select(Note).where(Note.user_id == user.id, Note.problem_id == problem.id))
    if not note:
        note = Note(user_id=user.id, problem_id=problem.id)
        db.add(note)
    note.content = body.content
    note.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}


@app.get("/api/problems/{slug}/discussions")
def list_problem_discussions(slug: str, limit: int = 30, user: User | None = Depends(get_optional_user), db: Session = Depends(db_session)):
    problem = db.scalar(select(Problem).where(Problem.slug == slug))
    if not problem:
        raise HTTPException(404, "Problem not found.")
    query = select(Discussion).where(Discussion.problem_id == problem.id)
    if not user or user.role != "admin":
        query = query.where(Discussion.is_hidden.is_(False))
    discussions = db.scalars(query.order_by(Discussion.created_at.desc()).limit(max(1, min(limit, 50)))).all()
    items = []
    for discussion in discussions:
        author = db.get(User, discussion.user_id)
        score = db.scalar(select(func.coalesce(func.sum(DiscussionVote.value), 0)).where(DiscussionVote.discussion_id == discussion.id)) or 0
        my_vote = db.scalar(select(DiscussionVote.value).where(DiscussionVote.discussion_id == discussion.id, DiscussionVote.user_id == user.id)) if user else 0
        comments = db.scalars(select(DiscussionComment).where(DiscussionComment.discussion_id == discussion.id).order_by(DiscussionComment.created_at.asc()).limit(20)).all()
        comment_items = []
        for comment in comments:
            comment_author = db.get(User, comment.user_id)
            comment_items.append({"id": comment.id, "body": comment.body, "author": comment_author.display_name if comment_author else "Deleted user", "created_at": comment.created_at.isoformat()})
        items.append({
            "id": discussion.id, "title": discussion.title, "body": discussion.body,
            "author": author.display_name if author else "Deleted user", "created_at": discussion.created_at.isoformat(),
            "score": int(score), "my_vote": int(my_vote or 0), "comments": comment_items,
            "is_owner": bool(user and user.id == discussion.user_id), "is_hidden": discussion.is_hidden,
        })
    return {"items": items, "can_post": bool(user)}


@app.post("/api/problems/{slug}/discussions")
def create_problem_discussion(slug: str, body: DiscussionCreateBody, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    _rate_limit(request, "discussion-create", 5)
    problem = db.scalar(select(Problem).where(Problem.slug == slug))
    if not problem:
        raise HTTPException(404, "Problem not found.")
    discussion = Discussion(problem_id=problem.id, user_id=user.id, title=body.title.strip(), body=body.body.strip())
    db.add(discussion)
    db.commit()
    db.refresh(discussion)
    return {"ok": True, "id": discussion.id}


@app.post("/api/discussions/{discussion_id}/comments")
def create_discussion_comment(discussion_id: int, body: DiscussionCommentBody, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    _rate_limit(request, "discussion-comment", 12)
    discussion = db.get(Discussion, discussion_id)
    if not discussion or discussion.is_hidden:
        raise HTTPException(404, "Discussion not found.")
    db.add(DiscussionComment(discussion_id=discussion.id, user_id=user.id, body=body.body.strip()))
    db.commit()
    return {"ok": True}


@app.post("/api/discussions/{discussion_id}/vote")
def vote_discussion(discussion_id: int, body: DiscussionVoteBody, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    discussion = db.get(Discussion, discussion_id)
    if not discussion or discussion.is_hidden:
        raise HTTPException(404, "Discussion not found.")
    if discussion.user_id == user.id and body.value != 0:
        raise HTTPException(403, "You cannot vote on your own discussion.")
    vote = db.scalar(select(DiscussionVote).where(DiscussionVote.discussion_id == discussion.id, DiscussionVote.user_id == user.id))
    if body.value == 0:
        if vote:
            db.delete(vote)
    elif vote:
        vote.value = body.value
    else:
        db.add(DiscussionVote(discussion_id=discussion.id, user_id=user.id, value=body.value))
    db.commit()
    score = db.scalar(select(func.coalesce(func.sum(DiscussionVote.value), 0)).where(DiscussionVote.discussion_id == discussion.id)) or 0
    return {"ok": True, "score": int(score), "my_vote": body.value}


@app.post("/api/discussions/{discussion_id}/report")
def report_discussion(discussion_id: int, body: DiscussionReportBody, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    _rate_limit(request, "discussion-report", 4)
    discussion = db.get(Discussion, discussion_id)
    if not discussion or discussion.user_id == user.id:
        raise HTTPException(404, "Discussion not found.")
    existing = db.scalar(select(DiscussionReport).where(DiscussionReport.discussion_id == discussion.id, DiscussionReport.user_id == user.id))
    if existing:
        raise HTTPException(409, "You have already reported this discussion.")
    db.add(DiscussionReport(discussion_id=discussion.id, user_id=user.id, reason=body.reason.strip()))
    db.commit()
    return {"ok": True}


@app.delete("/api/discussions/{discussion_id}")
def delete_discussion(discussion_id: int, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    discussion = db.get(Discussion, discussion_id)
    if not discussion or (discussion.user_id != user.id and user.role != "admin"):
        raise HTTPException(404, "Discussion not found.")
    db.query(DiscussionReport).filter(DiscussionReport.discussion_id == discussion.id).delete(synchronize_session=False)
    db.query(DiscussionVote).filter(DiscussionVote.discussion_id == discussion.id).delete(synchronize_session=False)
    db.query(DiscussionComment).filter(DiscussionComment.discussion_id == discussion.id).delete(synchronize_session=False)
    db.delete(discussion)
    db.commit()
    return {"ok": True}


@app.get("/api/admin/discussion-reports")
def admin_discussion_reports(user: User = Depends(require_admin), db: Session = Depends(db_session)):
    reports = db.scalars(select(DiscussionReport).where(DiscussionReport.resolved.is_(False)).order_by(DiscussionReport.created_at.desc()).limit(100)).all()
    items = []
    for report in reports:
        discussion = db.get(Discussion, report.discussion_id)
        reporter = db.get(User, report.user_id)
        if discussion:
            items.append({"id": report.id, "discussion_id": discussion.id, "discussion_title": discussion.title,
                          "reason": report.reason, "reporter": reporter.display_name if reporter else "Deleted user",
                          "created_at": report.created_at.isoformat(), "is_hidden": discussion.is_hidden})
    return {"items": items}


@app.post("/api/admin/discussions/{discussion_id}/moderate")
def moderate_discussion(discussion_id: int, body: DiscussionModerationBody, request: Request, user: User = Depends(require_admin), db: Session = Depends(db_session)):
    _check_same_origin(request)
    discussion = db.get(Discussion, discussion_id)
    if not discussion:
        raise HTTPException(404, "Discussion not found.")
    discussion.is_hidden = body.is_hidden
    db.query(DiscussionReport).filter(DiscussionReport.discussion_id == discussion.id).update({DiscussionReport.resolved: True}, synchronize_session=False)
    db.commit()
    return {"ok": True, "discussion_id": discussion.id, "is_hidden": discussion.is_hidden}


# --- Original-problem judging, daily learning, profile and contest services ---

def _judge_headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if JUDGE0_TOKEN:
        headers["X-Auth-Token"] = JUDGE0_TOKEN
    return headers


def _judge_limits() -> dict[str, Any]:
    return {
        "cpu_time_limit": 2,
        "cpu_extra_time": 1,
        "wall_time_limit": 5,
        "memory_limit": 128000,
        "stack_limit": 64000,
        "max_processes_and_or_threads": 30,
        "enable_per_process_and_thread_time_limit": True,
        "enable_per_process_and_thread_memory_limit": True,
    }


def _award_judged_solve(db: Session, user: User, problem: Problem) -> None:
    row = db.scalar(select(UserProgress).where(UserProgress.user_id == user.id, UserProgress.problem_id == problem.id))
    already_solved = bool(row and row.status == "solved")
    if not row:
        row = UserProgress(user_id=user.id, problem_id=problem.id)
        db.add(row)
    row.status = "solved"
    row.source = "algoforge_judge"
    row.updated_at = datetime.now(timezone.utc)
    if not already_solved:
        today = _today_for(user)
        activity = db.scalar(select(Activity).where(Activity.user_id == user.id, Activity.activity_date == today))
        if not activity:
            activity = Activity(user_id=user.id, activity_date=today, solved_count=0)
            db.add(activity)
        activity.solved_count += 1


@app.put("/api/me")
def update_profile(body: ProfileBody, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    try:
        ZoneInfo(body.timezone)
    except ZoneInfoNotFoundError:
        raise HTTPException(422, "Choose a valid IANA timezone, such as Asia/Kolkata.")
    user.display_name = body.display_name.strip()
    user.timezone = body.timezone
    db.commit()
    return {"user": {"id": user.id, "email": user.email, "display_name": user.display_name, "role": user.role, "timezone": user.timezone}}


@app.get("/api/daily-challenge")
def daily_challenge(user: User | None = Depends(get_optional_user), db: Session = Depends(db_session)):
    today = _today_for(user) if user else date.today()
    challenge = db.scalar(select(DailyChallenge).where(DailyChallenge.challenge_date == today))
    if not challenge:
        originals = db.scalars(select(Problem).where(Problem.is_native.is_(True)).order_by(Problem.id)).all()
        if not originals:
            raise HTTPException(503, "The original practice bank has not been seeded yet.")
        index = today.toordinal() % len(originals)
        challenge = DailyChallenge(challenge_date=today, problem_id=originals[index].id)
        db.add(challenge)
        db.commit()
        db.refresh(challenge)
    problem = db.get(Problem, challenge.problem_id)
    completed = False
    if user:
        progress = db.scalar(select(UserProgress).where(UserProgress.user_id == user.id, UserProgress.problem_id == problem.id))
        completed = bool(progress and progress.status == "solved" and progress.source == "algoforge_judge")
    return {"date": today.isoformat(), "completed": completed, "problem": _problem_dict(problem)}


@app.get("/api/achievements")
def achievements(user: User = Depends(require_user), db: Session = Depends(db_session)):
    solved_ids = db.scalars(select(UserProgress.problem_id).where(UserProgress.user_id == user.id, UserProgress.status == "solved")).all()
    solved = len(solved_ids)
    hard = db.scalar(select(func.count(UserProgress.id)).join(Problem, Problem.id == UserProgress.problem_id).where(UserProgress.user_id == user.id, UserProgress.status == "solved", Problem.difficulty == "Hard")) or 0
    activity_rows = db.scalars(select(Activity.activity_date).where(Activity.user_id == user.id, Activity.solved_count > 0).order_by(Activity.activity_date)).all()
    longest = 0
    run = 0
    previous = None
    for day in activity_rows:
        run = run + 1 if previous and day == previous + timedelta(days=1) else 1
        longest = max(longest, run)
        previous = day
    definitions = [
        ("first-solve", "First steps", "Solve your first problem", solved >= 1),
        ("five-solves", "Finding rhythm", "Solve 5 problems", solved >= 5),
        ("twenty-five-solves", "Problem explorer", "Solve 25 problems", solved >= 25),
        ("hundred-solves", "Centurion", "Solve 100 problems", solved >= 100),
        ("hard-solve", "Deep reasoning", "Solve a hard problem", hard >= 1),
        ("three-day-streak", "Three-day streak", "Practise on 3 consecutive days", longest >= 3),
        ("seven-day-streak", "One-week habit", "Practise on 7 consecutive days", longest >= 7),
        ("thirty-day-streak", "Consistency is key", "Practise on 30 consecutive days", longest >= 30),
    ]
    return {"items": [{"id": key, "title": title, "description": desc, "unlocked": unlocked} for key, title, desc, unlocked in definitions], "solved": solved, "hard_solved": hard, "longest_streak": longest}


@app.post("/api/admin/problems")
def admin_create_problem(body: AdminProblemBody, request: Request, user: User = Depends(require_admin), db: Session = Depends(db_session)):
    _check_same_origin(request)
    if db.scalar(select(Problem.id).where(Problem.slug == body.slug)):
        raise HTTPException(409, "A problem with this slug already exists.")
    if any(len(str(x.get("input", ""))) > 20000 or len(str(x.get("output", ""))) > 20000 for x in body.test_cases):
        raise HTTPException(422, "Each test input and output must be at most 20,000 characters.")
    if sum(1 for item in body.test_cases if bool(item.get("sample"))) < 1:
        raise HTTPException(422, "At least one sample test case is required.")
    problem = Problem(
        slug=body.slug, title=body.title.strip(), platform="AlgoForge Originals", url=f"{PUBLIC_BASE_URL}/#/problem/{body.slug}",
        difficulty=body.difficulty, pattern=body.pattern, topics=body.topics, time_complexity=body.time_complexity,
        space_complexity=body.space_complexity, description=body.description, source_licence="Original AlgoForge content",
        statement_rehosted=True, is_native=True, constraints=body.constraints, hints=body.hints, examples=[],
    )
    db.add(problem)
    db.flush()
    for position, item in enumerate(body.test_cases):
        db.add(ProblemTestCase(problem_id=problem.id, input_data=str(item.get("input", "")), expected_output=str(item.get("output", "")), is_sample=bool(item.get("sample", False)), position=position))
    db.commit()
    return {"ok": True, "slug": problem.slug, "test_cases": len(body.test_cases)}


@app.get("/api/admin/problems")
def admin_list_problems(user: User = Depends(require_admin), db: Session = Depends(db_session)):
    problems = db.scalars(select(Problem).where(Problem.is_native.is_(True)).order_by(Problem.title)).all()
    return {"items": [{"slug": p.slug, "title": p.title, "difficulty": p.difficulty, "pattern": p.pattern,
                        "test_cases": db.scalar(select(func.count(ProblemTestCase.id)).where(ProblemTestCase.problem_id == p.id)) or 0}
                       for p in problems]}


@app.put("/api/admin/problems/{slug}")
def admin_update_problem(slug: str, body: AdminProblemBody, request: Request, user: User = Depends(require_admin), db: Session = Depends(db_session)):
    _check_same_origin(request)
    if body.slug != slug:
        raise HTTPException(422, "Problem slugs are immutable; the payload slug must match the URL.")
    problem = db.scalar(select(Problem).where(Problem.slug == slug, Problem.is_native.is_(True)))
    if not problem:
        raise HTTPException(404, "Original problem not found.")
    if db.scalar(select(Submission.id).where(Submission.problem_id == problem.id).limit(1)):
        raise HTTPException(409, "This problem has submissions. Create a new version instead of changing its judging data.")
    if any(len(str(x.get("input", ""))) > 20000 or len(str(x.get("output", ""))) > 20000 for x in body.test_cases):
        raise HTTPException(422, "Each test input and output must be at most 20,000 characters.")
    if sum(1 for item in body.test_cases if bool(item.get("sample"))) < 1:
        raise HTTPException(422, "At least one sample test case is required.")
    problem.title = body.title.strip()
    problem.difficulty = body.difficulty
    problem.pattern = body.pattern
    problem.topics = body.topics
    problem.description = body.description
    problem.constraints = body.constraints
    problem.time_complexity = body.time_complexity or None
    problem.space_complexity = body.space_complexity or None
    problem.hints = body.hints
    db.query(ProblemTestCase).filter(ProblemTestCase.problem_id == problem.id).delete(synchronize_session=False)
    for position, item in enumerate(body.test_cases):
        db.add(ProblemTestCase(problem_id=problem.id, input_data=str(item.get("input", "")), expected_output=str(item.get("output", "")), is_sample=bool(item.get("sample", False)), position=position))
    db.commit()
    return {"ok": True, "slug": problem.slug, "test_cases": len(body.test_cases)}


@app.delete("/api/admin/problems/{slug}")
def admin_delete_problem(slug: str, request: Request, user: User = Depends(require_admin), db: Session = Depends(db_session)):
    _check_same_origin(request)
    problem = db.scalar(select(Problem).where(Problem.slug == slug, Problem.is_native.is_(True)))
    if not problem:
        raise HTTPException(404, "Original problem not found.")
    references = (
        db.scalar(select(Submission.id).where(Submission.problem_id == problem.id).limit(1))
        or db.scalar(select(ContestProblem.id).where(ContestProblem.problem_id == problem.id).limit(1))
        or db.scalar(select(UserProgress.id).where(UserProgress.problem_id == problem.id).limit(1))
        or db.scalar(select(Discussion.id).where(Discussion.problem_id == problem.id).limit(1))
    )
    if references:
        raise HTTPException(409, "This problem is referenced by submissions, contests or learner progress and cannot be deleted.")
    db.query(DailyChallenge).filter(DailyChallenge.problem_id == problem.id).delete(synchronize_session=False)
    db.query(ProblemTestCase).filter(ProblemTestCase.problem_id == problem.id).delete(synchronize_session=False)
    db.query(Bookmark).filter(Bookmark.problem_id == problem.id).delete(synchronize_session=False)
    db.query(Note).filter(Note.problem_id == problem.id).delete(synchronize_session=False)
    db.delete(problem)
    db.commit()
    return {"ok": True, "deleted": slug}


# LeetCode-style adapters for AlgoForge-original problems. Each adapter is
# explicit: its method signature and input decoder must match the statement.
# Third-party link records never receive function adapters.
FUNCTION_PROBLEM_SLUGS = {
    "af-running-sum", "af-maximum-pair-sum", "af-binary-search-index", "af-missing-number"
}

_FUNCTION_RUNNERS: dict[str, dict[str, str]] = {
    "af-running-sum": {
        "cpp": r"""
int main(){
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; if(!(cin>>n)) return 0;
    vector<int> a(n); for(int &x:a) cin>>x;
    auto out=Solution().runningSum(a);
    for(size_t i=0;i<out.size();++i) cout<<(i?" ":"")<<out[i];
    cout<<'\n';
}
""",
        "java": r"""
public class Main {
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in); int n=sc.nextInt(); int[] a=new int[n];
        for(int i=0;i<n;i++) a[i]=sc.nextInt();
        long[] out=new Solution().runningSum(a);
        for(int i=0;i<out.length;i++) System.out.print((i>0?" ":"")+out[i]);
        System.out.println();
    }
}
""",
        "python": r"""
if __name__ == "__main__":
    import sys
    values=list(map(int,sys.stdin.read().split()))
    if values:
        n=values[0]
        print(" ".join(map(str, Solution().runningSum(values[1:1+n]))))
""",
        "c": r"""
int main(void){
    int n=0; if(scanf("%d",&n)!=1) return 0;
    int *a=malloc(sizeof(int)*(size_t)n); for(int i=0;i<n;i++) scanf("%d",&a[i]);
    int outN=0; long long *out=runningSum(a,n,&outN);
    for(int i=0;i<outN;i++) printf("%s%lld",i?" ":"",out[i]);
    puts(""); free(a); free(out); return 0;
}
""",
    },
    "af-maximum-pair-sum": {
        "cpp": r"""
int main(){
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; if(!(cin>>n)) return 0; vector<int> a(n); for(int &x:a) cin>>x;
    cout<<Solution().maxPairSum(a)<<'\n';
}
""",
        "java": r"""
public class Main {
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in); int n=sc.nextInt(); int[] a=new int[n];
        for(int i=0;i<n;i++) a[i]=sc.nextInt();
        System.out.println(new Solution().maxPairSum(a));
    }
}
""",
        "python": r"""
if __name__ == "__main__":
    import sys
    values=list(map(int,sys.stdin.read().split()))
    if values:
        n=values[0]
        print(Solution().maxPairSum(values[1:1+n]))
""",
        "c": r"""
int main(void){
    int n=0; if(scanf("%d",&n)!=1) return 0; int *a=malloc(sizeof(int)*(size_t)n);
    for(int i=0;i<n;i++) scanf("%d",&a[i]);
    printf("%lld\n",maxPairSum(a,n)); free(a); return 0;
}
""",
    },
    "af-binary-search-index": {
        "cpp": r"""
int main(){
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; if(!(cin>>n)) return 0; vector<int> a(n); for(int &x:a) cin>>x;
    int target; cin>>target; cout<<Solution().search(a,target)<<'\n';
}
""",
        "java": r"""
public class Main {
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in); int n=sc.nextInt(); int[] a=new int[n];
        for(int i=0;i<n;i++) a[i]=sc.nextInt(); int target=sc.nextInt();
        System.out.println(new Solution().search(a,target));
    }
}
""",
        "python": r"""
if __name__ == "__main__":
    import sys
    values=list(map(int,sys.stdin.read().split()))
    if values:
        n=values[0]
        print(Solution().search(values[1:1+n],values[1+n]))
""",
        "c": r"""
int main(void){
    int n=0; if(scanf("%d",&n)!=1) return 0; int *a=malloc(sizeof(int)*(size_t)n);
    for(int i=0;i<n;i++) scanf("%d",&a[i]); int target=0; scanf("%d",&target);
    printf("%d\n",search(a,n,target)); free(a); return 0;
}
""",
    },
    "af-missing-number": {
        "cpp": r"""
int main(){
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; if(!(cin>>n)) return 0; vector<int> a(n); for(int &x:a) cin>>x;
    cout<<Solution().missingNumber(a)<<'\n';
}
""",
        "java": r"""
public class Main {
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in); int n=sc.nextInt(); int[] a=new int[n];
        for(int i=0;i<n;i++) a[i]=sc.nextInt();
        System.out.println(new Solution().missingNumber(a));
    }
}
""",
        "python": r"""
if __name__ == "__main__":
    import sys
    values=list(map(int,sys.stdin.read().split()))
    if values:
        n=values[0]
        print(Solution().missingNumber(values[1:1+n]))
""",
        "c": r"""
int main(void){
    int n=0; if(scanf("%d",&n)!=1) return 0; int *a=malloc(sizeof(int)*(size_t)n);
    for(int i=0;i<n;i++) scanf("%d",&a[i]);
    printf("%d\n",missingNumber(a,n)); free(a); return 0;
}
""",
    },
}


def _function_supported(problem_slug: str | None, mode: str) -> bool:
    return mode == "stdin" or (mode == "function" and problem_slug in FUNCTION_PROBLEM_SLUGS)


def _wrap_function_solution(problem_slug: str, language: str, source: str) -> str:
    if problem_slug not in FUNCTION_PROBLEM_SLUGS or language not in LANGUAGE_IDS:
        raise HTTPException(422, "Function-style execution is not configured for this problem and language.")
    return source.rstrip() + "\n\n" + _FUNCTION_RUNNERS[problem_slug][language] + "\n"


@app.get("/api/analytics")
def learning_analytics(user: User = Depends(require_user), db: Session = Depends(db_session)):
    problems = db.scalars(select(Problem)).all()
    progress_rows = db.scalars(select(UserProgress).where(UserProgress.user_id == user.id)).all()
    progress_by_problem = {row.problem_id: row.status for row in progress_rows}
    pattern_totals: dict[str, dict[str, int]] = {}
    topic_totals: dict[str, dict[str, int]] = {}
    for problem in problems:
        pattern = problem.pattern or "Uncategorised"
        group = pattern_totals.setdefault(pattern, {"total": 0, "solved": 0, "attempted": 0})
        group["total"] += 1
        status = progress_by_problem.get(problem.id, "todo")
        if status == "solved": group["solved"] += 1
        if status != "todo": group["attempted"] += 1
        for topic in (problem.topics or []):
            t = topic_totals.setdefault(str(topic), {"total": 0, "solved": 0, "attempted": 0})
            t["total"] += 1
            if status == "solved": t["solved"] += 1
            if status != "todo": t["attempted"] += 1

    def scored_rows(source: dict[str, dict[str, int]]) -> list[dict[str, Any]]:
        rows = []
        for name, values in source.items():
            mastery = round(100 * values["solved"] / max(1, values["total"]))
            rows.append({"name": name, **values, "mastery_pct": mastery})
        return sorted(rows, key=lambda row: (row["mastery_pct"], -row["attempted"], row["name"]))

    patterns = scored_rows(pattern_totals)
    topics = scored_rows(topic_totals)
    # A topic is only labelled weak after the learner has attempted at least
    # one problem in it. Untouched topics remain unexplored, not falsely weak.
    weak = [row for row in patterns if row["attempted"] and row["mastery_pct"] < 60][:5]
    weak_topics = [row for row in topics if row["attempted"] and row["mastery_pct"] < 60][:5]
    weak_names = {row["name"] for row in weak}
    recommendations = [p for p in problems if progress_by_problem.get(p.id, "todo") != "solved"]
    recommendations.sort(key=lambda p: (0 if p.pattern in weak_names else 1, {"Easy": 0, "Medium": 1, "Hard": 2}.get(p.difficulty, 3), p.title.casefold()))
    recommended = [{"slug": p.slug, "title": p.title, "difficulty": p.difficulty, "pattern": p.pattern,
                     "reason": "Strengthen a topic with lower completion" if p.pattern in weak_names else "Build breadth across your DSA patterns"} for p in recommendations[:8]]

    today = _today_for(user)
    recent_14_start = today - timedelta(days=13)
    last_14 = db.scalars(select(Activity).where(Activity.user_id == user.id, Activity.activity_date >= recent_14_start, Activity.activity_date <= today)).all()
    daily_counts = {row.activity_date: row.solved_count for row in last_14}
    recent_solves = sum(daily_counts.values())
    daily_velocity = recent_solves / 14
    solved_count = sum(1 for status in progress_by_problem.values() if status == "solved")
    remaining = max(0, len(problems) - solved_count)
    prediction_days = round(remaining / daily_velocity) if daily_velocity > 0 else None
    week_start = today - timedelta(days=6)
    previous_week_start = today - timedelta(days=13)
    week_rows = db.scalars(select(Activity).where(Activity.user_id == user.id, Activity.activity_date >= previous_week_start, Activity.activity_date <= today)).all()
    week_map = {row.activity_date: row.solved_count for row in week_rows}
    weekly = [{"date": (week_start + timedelta(days=i)).isoformat(), "label": (week_start + timedelta(days=i)).strftime("%a"), "solved": week_map.get(week_start + timedelta(days=i), 0)} for i in range(7)]
    current_week_solves = sum(week_map.get(week_start + timedelta(days=i), 0) for i in range(7))
    previous_week_solves = sum(week_map.get(previous_week_start + timedelta(days=i), 0) for i in range(7))
    week_delta_pct = round(100 * (current_week_solves - previous_week_solves) / previous_week_solves) if previous_week_solves else None
    total_active_days = db.scalar(select(func.count(Activity.id)).where(Activity.user_id == user.id, Activity.solved_count > 0)) or 0
    contributions = db.scalar(select(func.coalesce(func.sum(Activity.solved_count), 0)).where(Activity.user_id == user.id)) or 0
    return {
        "total_active_days": total_active_days, "contributions": int(contributions), "solved": solved_count,
        "pattern_mastery": patterns, "topic_mastery": topics,
        "weak_patterns": weak, "weak_topics": weak_topics,
        "weekly_report": weekly,
        "week_comparison": {"current_week_solves": current_week_solves, "previous_week_solves": previous_week_solves, "change_pct": week_delta_pct},
        "consistency": {"active_days_last_7": sum(1 for value in weekly if value["solved"] > 0), "active_days_last_14": sum(1 for value in daily_counts.values() if value > 0), "active_rate_14d": round(100 * sum(1 for value in daily_counts.values() if value > 0) / 14), "solves_last_14d": recent_solves},
        "recommendations": recommended,
        "prediction": {"remaining_questions": remaining, "recent_daily_solves": round(daily_velocity, 2), "estimated_days_to_complete_catalogue": prediction_days, "method": "14-day recorded-completion velocity; externally self-reported completions may be included. This is a simple trend estimate, not a guarantee."},
    }


def _valid_draft_key(problem_key: str, db: Session) -> bool:
    if problem_key == "playground":
        return True
    base_key = problem_key.removesuffix("::function")
    return db.scalar(select(Problem.id).where(Problem.slug == base_key)) is not None


@app.get("/api/drafts/{problem_key}/{language}")
def get_code_draft(problem_key: str, language: str, user: User = Depends(require_user), db: Session = Depends(db_session)):
    if language not in LANGUAGE_IDS or not _valid_draft_key(problem_key, db):
        raise HTTPException(404, "Draft target not found.")
    draft = db.scalar(select(CodeDraft).where(CodeDraft.user_id == user.id, CodeDraft.problem_key == problem_key, CodeDraft.language == language))
    if not draft:
        return {"draft": None, "versions": []}
    versions = db.scalars(select(CodeDraftVersion).where(CodeDraftVersion.draft_id == draft.id).order_by(CodeDraftVersion.created_at.desc()).limit(20)).all()
    return {"draft": {"id": draft.id, "source_code": draft.source_code, "stdin": draft.stdin, "updated_at": draft.updated_at.isoformat()},
            "versions": [{"id": v.id, "created_at": v.created_at.isoformat()} for v in versions]}


@app.put("/api/drafts/{problem_key}/{language}")
def save_code_draft(problem_key: str, language: str, body: DraftSaveBody, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    if language not in LANGUAGE_IDS or not _valid_draft_key(problem_key, db):
        raise HTTPException(404, "Draft target not found.")
    draft = db.scalar(select(CodeDraft).where(CodeDraft.user_id == user.id, CodeDraft.problem_key == problem_key, CodeDraft.language == language))
    if not draft:
        draft = CodeDraft(user_id=user.id, problem_key=problem_key, language=language, source_code=body.source_code, stdin=body.stdin)
        db.add(draft); db.flush()
    elif draft.source_code != body.source_code or draft.stdin != body.stdin:
        latest = db.scalar(select(CodeDraftVersion).where(CodeDraftVersion.draft_id == draft.id).order_by(CodeDraftVersion.created_at.desc()).limit(1))
        if not latest or latest.source_code != draft.source_code or latest.stdin != draft.stdin:
            db.add(CodeDraftVersion(draft_id=draft.id, source_code=draft.source_code, stdin=draft.stdin))
        draft.source_code = body.source_code
        draft.stdin = body.stdin
    draft.updated_at = datetime.now(timezone.utc)
    db.flush()
    old = db.scalars(select(CodeDraftVersion).where(CodeDraftVersion.draft_id == draft.id).order_by(CodeDraftVersion.created_at.desc()).offset(30)).all()
    for version in old: db.delete(version)
    db.commit()
    return {"ok": True, "draft_id": draft.id, "updated_at": draft.updated_at.isoformat()}


@app.get("/api/drafts/{problem_key}/{language}/versions")
def list_code_draft_versions(problem_key: str, language: str, user: User = Depends(require_user), db: Session = Depends(db_session)):
    draft = db.scalar(select(CodeDraft).where(CodeDraft.user_id == user.id, CodeDraft.problem_key == problem_key, CodeDraft.language == language))
    if not draft: return {"items": []}
    rows = db.scalars(select(CodeDraftVersion).where(CodeDraftVersion.draft_id == draft.id).order_by(CodeDraftVersion.created_at.desc()).limit(30)).all()
    return {"items": [{"id": row.id, "created_at": row.created_at.isoformat(), "preview": row.source_code[:180]} for row in rows]}


@app.post("/api/drafts/{problem_key}/{language}/restore")
def restore_code_draft(problem_key: str, language: str, body: DraftRestoreBody, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    draft = db.scalar(select(CodeDraft).where(CodeDraft.user_id == user.id, CodeDraft.problem_key == problem_key, CodeDraft.language == language))
    version = db.get(CodeDraftVersion, body.version_id)
    if not draft or not version or version.draft_id != draft.id:
        raise HTTPException(404, "Draft version not found.")
    db.add(CodeDraftVersion(draft_id=draft.id, source_code=draft.source_code, stdin=draft.stdin))
    draft.source_code = version.source_code; draft.stdin = version.stdin; draft.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True, "source_code": draft.source_code, "stdin": draft.stdin}


@app.post("/api/problems/{slug}/submit")
async def submit_problem(slug: str, body: SubmitBody, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    _rate_limit(request, "submit", 5)
    problem = db.scalar(select(Problem).where(Problem.slug == slug))
    if not problem:
        raise HTTPException(404, "Problem not found.")
    if not problem.is_native:
        raise HTTPException(409, "This is a third-party catalogue link. Open the source platform for official judging; AlgoForge does not host its private tests.")
    if not JUDGE0_URL:
        raise HTTPException(503, "Problem judging is unavailable until a secured Judge0 service is configured.")
    test_cases = db.scalars(select(ProblemTestCase).where(ProblemTestCase.problem_id == problem.id).order_by(ProblemTestCase.position)).all()
    if not test_cases:
        raise HTTPException(503, "No judge test cases are configured for this problem.")
    contest_id = None
    if body.contest_slug:
        contest = db.scalar(select(Contest).where(Contest.slug == body.contest_slug, Contest.is_published.is_(True)))
        if not contest:
            raise HTTPException(404, "Contest not found.")
        now = datetime.now(timezone.utc)
        starts = contest.starts_at.replace(tzinfo=timezone.utc) if contest.starts_at.tzinfo is None else contest.starts_at
        ends = contest.ends_at.replace(tzinfo=timezone.utc) if contest.ends_at.tzinfo is None else contest.ends_at
        if now < starts or now > ends:
            raise HTTPException(409, "Contest submissions are accepted only during the scheduled contest window.")
        if not db.scalar(select(ContestParticipant.id).where(ContestParticipant.contest_id == contest.id, ContestParticipant.user_id == user.id)):
            raise HTTPException(403, "Register for this contest before submitting.")
        if not db.scalar(select(ContestProblem.id).where(ContestProblem.contest_id == contest.id, ContestProblem.problem_id == problem.id)):
            raise HTTPException(403, "This problem is not part of the selected contest.")
        contest_id = contest.id
    if body.mode == "function" and not _function_supported(problem.slug, body.mode):
        raise HTTPException(422, "Function-style mode is available only for configured problem signatures.")
    judge_source = _wrap_function_solution(problem.slug, body.language, body.source_code) if body.mode == "function" else body.source_code
    lang_id = LANGUAGE_IDS[body.language]
    submissions_payload = []
    limits = _judge_limits()
    for case in test_cases:
        submissions_payload.append({
            "source_code": judge_source, "language_id": lang_id,
            "stdin": case.input_data, "expected_output": case.expected_output,
            **limits,
        })
    try:
        async with httpx.AsyncClient(timeout=JUDGE0_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{JUDGE0_URL}/submissions/batch?base64_encoded=false", json={"submissions": submissions_payload}, headers=_judge_headers())
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(502, "Judge service rejected the problem submission. Check service capacity and language configuration.") from exc
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(502, "The judging service could not be reached.") from exc
    tokens_payload = data.get("submissions") if isinstance(data, dict) else data
    tokens = [item.get("token") for item in (tokens_payload or []) if isinstance(item, dict) and item.get("token")]
    if len(tokens) != len(test_cases):
        raise HTTPException(502, "Judge service returned an incomplete test-case batch.")
    complexity = analyze_complexity(body.source_code, body.language)
    complexity.update({"expected_time": problem.time_complexity, "expected_space": problem.space_complexity})
    submission = Submission(user_id=user.id, problem_id=problem.id, language=body.language, source_code=body.source_code,
                            stdin="", judge_tokens=tokens, case_results=[], contest_id=contest_id, status="Judging", complexity=complexity)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return {"id": submission.id, "status": submission.status, "test_cases": len(tokens), "complexity": complexity}


@app.post("/api/problems/{slug}/run-custom")
async def run_custom_tests(slug: str, body: CustomRunBody, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    _rate_limit(request, "custom-test", 8)
    problem = db.scalar(select(Problem).where(Problem.slug == slug, Problem.is_native.is_(True)))
    if not problem:
        raise HTTPException(404, "Custom test runs are available for AlgoForge original problems.")
    if not JUDGE0_URL:
        raise HTTPException(503, "Code execution is not configured. Set JUDGE0_URL to a secured Judge0 instance.")
    if body.mode == "function" and not _function_supported(problem.slug, body.mode):
        raise HTTPException(422, "Function-style mode is not configured for this problem yet.")
    judge_source = _wrap_function_solution(problem.slug, body.language, body.source_code) if body.mode == "function" else body.source_code
    payloads = []
    custom_metadata = []
    for case in body.test_cases:
        item = {"source_code": judge_source, "language_id": LANGUAGE_IDS[body.language], "stdin": case.input, **_judge_limits()}
        expected = case.expected_output
        if expected is not None and expected.strip() != "":
            item["expected_output"] = expected
        payloads.append(item)
        custom_metadata.append({"expected_output": expected, "has_expected_output": expected is not None and expected.strip() != ""})
    try:
        async with httpx.AsyncClient(timeout=JUDGE0_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{JUDGE0_URL}/submissions/batch?base64_encoded=false", json={"submissions": payloads}, headers=_judge_headers())
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(502, "Judge service rejected the custom test run.") from exc
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(502, "The judging service could not be reached.") from exc
    token_rows = data.get("submissions") if isinstance(data, dict) else data
    tokens = [row.get("token") for row in (token_rows or []) if isinstance(row, dict) and row.get("token")]
    if len(tokens) != len(payloads):
        raise HTTPException(502, "Judge service returned an incomplete custom-test batch.")
    complexity = analyze_complexity(body.source_code, body.language)
    complexity.update({"expected_time": problem.time_complexity, "expected_space": problem.space_complexity})
    submission = Submission(user_id=user.id, problem_id=problem.id, language=body.language, source_code=body.source_code,
                            stdin="", judge_tokens=tokens, case_results=[], custom_test_cases=custom_metadata,
                            status="Running Custom Tests", complexity=complexity)
    db.add(submission); db.commit(); db.refresh(submission)
    return {"id": submission.id, "status": submission.status, "test_cases": len(tokens), "complexity": complexity}


@app.get("/api/submissions/{submission_id}/judge")
async def judged_submission(submission_id: int, user: User = Depends(require_user), db: Session = Depends(db_session)):
    submission = db.get(Submission, submission_id)
    if not submission or submission.user_id != user.id or not (submission.judge_tokens or []):
        raise HTTPException(404, "Judged submission not found.")
    tokens = submission.judge_tokens or []
    if submission.status in {"Judging", "Running Custom Tests"}:
        try:
            async with httpx.AsyncClient(timeout=JUDGE0_TIMEOUT_SECONDS) as client:
                response = await client.get(f"{JUDGE0_URL}/submissions/batch", params={"tokens": ",".join(tokens), "base64_encoded": "false"}, headers=_judge_headers())
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise HTTPException(502, "Could not retrieve the judging results.") from exc
        rows = data.get("submissions", []) if isinstance(data, dict) else []
        results = []
        pending = False
        is_custom_run = bool(submission.custom_test_cases)
        sample_flags = ([True] * len(submission.custom_test_cases)) if is_custom_run else db.scalars(select(ProblemTestCase.is_sample).where(ProblemTestCase.problem_id == submission.problem_id).order_by(ProblemTestCase.position)).all()
        for index, result in enumerate(rows):
            status_obj = result.get("status") or {}
            status = status_obj.get("description", "Processing")
            if status in {"In Queue", "Processing", "Compiling"}:
                pending = True
            public_case = bool(index < len(sample_flags) and sample_flags[index])
            custom_meta = (submission.custom_test_cases or [])[index] if is_custom_run and index < len(submission.custom_test_cases or []) else {}
            passed = status == "Accepted" if (not is_custom_run or custom_meta.get("has_expected_output")) else None
            results.append({
                "case": index + 1, "status": status, "passed": passed,
                "time_seconds": result.get("time"), "memory_kb": result.get("memory"),
                "sample": public_case, "custom": is_custom_run,
                "has_expected_output": bool(custom_meta.get("has_expected_output")) if is_custom_run else None,
                "stdout": (result.get("stdout") or "")[:4000] if public_case else None,
                "stderr": (result.get("stderr") or "")[:4000] if public_case else None,
                "compile_output": (result.get("compile_output") or "")[:4000] if public_case else None,
                "expected_output": custom_meta.get("expected_output") if is_custom_run else None,
            })
        if len(results) < len(tokens):
            pending = True
        submission.case_results = results
        if not pending and len(results) == len(tokens):
            passed = sum(1 for row in results if row["passed"])
            if is_custom_run:
                expected_rows = [row for row in results if row.get("has_expected_output")]
                all_execution_ok = all(row["status"] == "Accepted" for row in results)
                if expected_rows and len(expected_rows) == len(results) and passed == len(tokens):
                    submission.status = "Custom Tests Passed"
                elif all_execution_ok:
                    submission.status = "Executed"
                else:
                    submission.status = next((row["status"] for row in results if row["status"] != "Accepted"), "Wrong Answer")
            elif passed == len(tokens):
                submission.status = "Accepted"
                problem = db.get(Problem, submission.problem_id)
                if problem:
                    _award_judged_solve(db, user, problem)
            else:
                submission.status = next((row["status"] for row in results if not row["passed"]), "Wrong Answer")
            measured = [float(row["time_seconds"]) for row in results if row.get("time_seconds") not in (None, "")]
            memories = [int(row["memory_kb"]) for row in results if row.get("memory_kb") is not None]
            submission.time_seconds = str(max(measured)) if measured else None
            submission.memory_kb = max(memories) if memories else None
        db.commit()
    else:
        results = submission.case_results or []
    compared_total = sum(1 for row in results if row.get("has_expected_output") is True) if submission.custom_test_cases else len(tokens)
    execution_only_total = max(0, len(results) - compared_total) if submission.custom_test_cases else 0
    return {"id": submission.id, "status": submission.status, "passed": sum(1 for row in results if row.get("passed")),
            "total": len(tokens), "compared_total": compared_total, "execution_only_total": execution_only_total,
            "cases": results, "complexity": submission.complexity,
            "time_seconds": submission.time_seconds, "memory_kb": submission.memory_kb}


@app.get("/api/contests")
def list_contests(db: Session = Depends(db_session)):
    now = datetime.now(timezone.utc)
    rows = db.scalars(select(Contest).where(Contest.is_published.is_(True)).order_by(Contest.starts_at.desc()).limit(30)).all()
    items = []
    for contest in rows:
        start = contest.starts_at.replace(tzinfo=timezone.utc) if contest.starts_at.tzinfo is None else contest.starts_at
        end = contest.ends_at.replace(tzinfo=timezone.utc) if contest.ends_at.tzinfo is None else contest.ends_at
        status = "upcoming" if now < start else "ended" if now > end else "live"
        items.append({"slug": contest.slug, "title": contest.title, "description": contest.description, "starts_at": start.isoformat(), "ends_at": end.isoformat(), "status": status,
                      "participants": db.scalar(select(func.count(ContestParticipant.id)).where(ContestParticipant.contest_id == contest.id)) or 0,
                      "problems": db.scalar(select(func.count(ContestProblem.id)).where(ContestProblem.contest_id == contest.id)) or 0})
    return {"items": items}


@app.post("/api/admin/contests")
def admin_create_contest(body: ContestCreateBody, request: Request, user: User = Depends(require_admin), db: Session = Depends(db_session)):
    _check_same_origin(request)
    if db.scalar(select(Contest.id).where(Contest.slug == body.slug)):
        raise HTTPException(409, "Contest slug already exists.")
    if body.starts_at.tzinfo is None or body.ends_at.tzinfo is None or body.ends_at <= body.starts_at:
        raise HTTPException(422, "Contest dates must include a timezone and the end must be after the start.")
    slugs = list(dict.fromkeys(body.problem_slugs))
    if len(slugs) != len(body.problem_slugs):
        raise HTTPException(422, "A problem may only appear once in a contest.")
    problems = db.scalars(select(Problem).where(Problem.slug.in_(slugs), Problem.is_native.is_(True))).all()
    by_slug = {p.slug: p for p in problems}
    if len(by_slug) != len(slugs):
        raise HTTPException(422, "All contest problems must be existing AlgoForge-original judged problems.")
    contest = Contest(slug=body.slug, title=body.title.strip(), description=body.description,
                      starts_at=body.starts_at.astimezone(timezone.utc), ends_at=body.ends_at.astimezone(timezone.utc), created_by=user.id, is_published=True)
    db.add(contest)
    db.flush()
    for position, slug in enumerate(slugs):
        db.add(ContestProblem(contest_id=contest.id, problem_id=by_slug[slug].id, points=100, position=position))
    db.commit()
    return {"ok": True, "slug": contest.slug}


@app.post("/api/contests/{slug}/register")
def register_contest(slug: str, request: Request, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    contest = db.scalar(select(Contest).where(Contest.slug == slug, Contest.is_published.is_(True)))
    if not contest:
        raise HTTPException(404, "Contest not found.")
    end = contest.ends_at.replace(tzinfo=timezone.utc) if contest.ends_at.tzinfo is None else contest.ends_at
    if datetime.now(timezone.utc) > end:
        raise HTTPException(409, "Registration is closed because the contest has ended.")
    participant = db.scalar(select(ContestParticipant).where(ContestParticipant.contest_id == contest.id, ContestParticipant.user_id == user.id))
    if not participant:
        db.add(ContestParticipant(contest_id=contest.id, user_id=user.id))
        db.commit()
    return {"registered": True}


@app.get("/api/contests/{slug}")
def contest_detail(slug: str, user: User | None = Depends(get_optional_user), db: Session = Depends(db_session)):
    contest = db.scalar(select(Contest).where(Contest.slug == slug, Contest.is_published.is_(True)))
    if not contest:
        raise HTTPException(404, "Contest not found.")
    now = datetime.now(timezone.utc)
    start = contest.starts_at.replace(tzinfo=timezone.utc) if contest.starts_at.tzinfo is None else contest.starts_at
    end = contest.ends_at.replace(tzinfo=timezone.utc) if contest.ends_at.tzinfo is None else contest.ends_at
    participant = bool(user and db.scalar(select(ContestParticipant.id).where(ContestParticipant.contest_id == contest.id, ContestParticipant.user_id == user.id)))
    show_problems = participant and now >= start
    items = []
    if show_problems:
        links = db.scalars(select(ContestProblem).where(ContestProblem.contest_id == contest.id).order_by(ContestProblem.position)).all()
        for link in links:
            p = db.get(Problem, link.problem_id)
            items.append({"slug": p.slug, "title": p.title, "difficulty": p.difficulty, "pattern": p.pattern, "points": link.points})
    return {"slug": contest.slug, "title": contest.title, "description": contest.description, "starts_at": start.isoformat(), "ends_at": end.isoformat(),
            "status": "upcoming" if now < start else "ended" if now > end else "live", "registered": participant, "problems": items,
            "problem_count": db.scalar(select(func.count(ContestProblem.id)).where(ContestProblem.contest_id == contest.id)) or 0}


@app.get("/api/contests/{slug}/leaderboard")
def contest_leaderboard(slug: str, db: Session = Depends(db_session)):
    contest = db.scalar(select(Contest).where(Contest.slug == slug, Contest.is_published.is_(True)))
    if not contest:
        raise HTTPException(404, "Contest not found.")
    rows = db.scalars(select(Submission).where(Submission.contest_id == contest.id).order_by(Submission.created_at)).all()
    problems = db.scalars(select(ContestProblem).where(ContestProblem.contest_id == contest.id)).all()
    points = {row.problem_id: row.points for row in problems}
    score_by_user: dict[int, dict[str, Any]] = {}
    for submission in rows:
        if submission.user_id is None or submission.problem_id is None:
            continue
        item = score_by_user.setdefault(submission.user_id, {"solved": set(), "penalty": 0, "wrong": defaultdict(int), "first": {}})
        if submission.status == "Accepted" and submission.problem_id not in item["solved"]:
            item["solved"].add(submission.problem_id)
            elapsed = max(0, int((submission.created_at.replace(tzinfo=timezone.utc) - (contest.starts_at.replace(tzinfo=timezone.utc) if contest.starts_at.tzinfo is None else contest.starts_at)).total_seconds() // 60))
            item["penalty"] += elapsed + item["wrong"][submission.problem_id] * 10
            item["first"][submission.problem_id] = submission.created_at.isoformat()
        elif submission.status in {"Wrong Answer", "Time Limit Exceeded", "Runtime Error", "Compilation Error"} and submission.problem_id not in item["solved"]:
            item["wrong"][submission.problem_id] += 1
    output = []
    for uid, item in score_by_user.items():
        person = db.get(User, uid)
        if not person:
            continue
        score = sum(points.get(pid, 0) for pid in item["solved"])
        output.append({"display_name": person.display_name, "score": score, "solved": len(item["solved"]), "penalty_minutes": item["penalty"]})
    output.sort(key=lambda x: (-x["score"], x["penalty_minutes"], x["display_name"].casefold()))
    for index, item in enumerate(output, 1):
        item["rank"] = index
    return {"items": output}


LANGUAGE_IDS = {
    "c": int(os.getenv("JUDGE0_LANGUAGE_C", "103")),
    "cpp": int(os.getenv("JUDGE0_LANGUAGE_CPP", "105")),
    "java": int(os.getenv("JUDGE0_LANGUAGE_JAVA", "91")),
    "python": int(os.getenv("JUDGE0_LANGUAGE_PYTHON", "109")),
}


@app.get("/api/judge/languages")
async def judge_languages():
    if not JUDGE0_URL:
        return {"configured": False, "items": [], "message": "Configure JUDGE0_URL to inspect the installed compiler runtimes."}
    try:
        async with httpx.AsyncClient(timeout=JUDGE0_TIMEOUT_SECONDS) as client:
            response = await client.get(f"{JUDGE0_URL}/languages", headers=_judge_headers())
            response.raise_for_status()
            languages = response.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(502, "Could not inspect the configured Judge0 language catalogue.")
    by_id = {int(item.get("id")): item for item in languages if isinstance(item, dict) and str(item.get("id", "")).isdigit()}
    labels = {key: by_id.get(value, {}).get("name", "Unavailable") for key, value in LANGUAGE_IDS.items()}
    return {"configured": True, "items": [{"language": key, "id": value, "runtime": labels[key], "available": labels[key] != "Unavailable"} for key, value in LANGUAGE_IDS.items()]}


@app.get("/api/judge/health")
async def judge_health():
    if not JUDGE0_URL:
        return {"configured": False, "reachable": False, "message": "Set JUDGE0_URL to a secured Judge0 service."}
    try:
        async with httpx.AsyncClient(timeout=JUDGE0_TIMEOUT_SECONDS) as client:
            response = await client.get(f"{JUDGE0_URL}/about", headers=_judge_headers())
            response.raise_for_status()
            about = response.json()
            config_response = await client.get(f"{JUDGE0_URL}/config_info", headers=_judge_headers())
            config_response.raise_for_status()
            limits = config_response.json()
        return {"configured": True, "reachable": True, "version": about.get("version"), "homepage": about.get("homepage"),
                "max_cpu_time_limit": limits.get("max_cpu_time_limit"), "max_memory_limit": limits.get("max_memory_limit"),
                "max_queue_size": limits.get("max_queue_size")}
    except (httpx.HTTPError, ValueError):
        return {"configured": True, "reachable": False, "message": "Judge0 health endpoint is unavailable or rejected the request."}


@app.post("/api/run")
async def run_code(body: RunBody, request: Request, user: User | None = Depends(get_optional_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    _rate_limit(request, "run", 8)
    if not JUDGE0_URL:
        raise HTTPException(503, "Code execution is not configured. Set JUDGE0_URL to a secured Judge0 instance.")
    problem = db.scalar(select(Problem).where(Problem.slug == body.problem_slug)) if body.problem_slug else None
    complexity = analyze_complexity(body.source_code, body.language)
    complexity["expected_time"] = problem.time_complexity if problem else None
    complexity["expected_space"] = problem.space_complexity if problem else None
    payload = {
        "source_code": body.source_code,
        "language_id": LANGUAGE_IDS[body.language],
        "stdin": body.stdin,
        "cpu_time_limit": 2,
        "cpu_extra_time": 1,
        "wall_time_limit": 5,
        "memory_limit": 128000,
        "stack_limit": 64000,
        "max_processes_and_or_threads": 30,
        "enable_per_process_and_thread_time_limit": True,
        "enable_per_process_and_thread_memory_limit": True,
    }
    headers = {"Content-Type": "application/json"}
    if JUDGE0_TOKEN:
        headers["X-Auth-Token"] = JUDGE0_TOKEN
    try:
        async with httpx.AsyncClient(timeout=JUDGE0_TIMEOUT_SECONDS) as client:
            resp = await client.post(f"{JUDGE0_URL}/submissions?base64_encoded=false&wait=false", json=payload, headers=headers)
            resp.raise_for_status()
            result = resp.json()
    except httpx.HTTPStatusError as e:
        detail = "Judge service rejected this request. Check its language configuration and limits."
        if e.response.status_code == 401:
            detail = "Judge0 authentication failed. Check JUDGE0_TOKEN."
        raise HTTPException(502, detail)
    except (httpx.HTTPError, ValueError):
        raise HTTPException(502, "The code execution service could not be reached. Check the Judge0 deployment.")
    token = result.get("token")
    if not token:
        raise HTTPException(502, "Judge0 did not return a submission token.")
    guest_access_token = secrets.token_urlsafe(28) if not user else None
    submission = Submission(user_id=user.id if user else None, problem_id=problem.id if problem else None,
                            language=body.language, source_code=body.source_code, stdin=body.stdin,
                            judge_token=token, access_token_hash=token_digest(guest_access_token) if guest_access_token else None,
                            status="Queued", complexity=complexity)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return {"id": submission.id, "status": "Queued", "complexity": complexity, "access_token": guest_access_token}


@app.get("/api/run/{submission_id}")
async def run_status(submission_id: int, request: Request, user: User | None = Depends(get_optional_user), db: Session = Depends(db_session)):
    submission = db.get(Submission, submission_id)
    access_token = request.headers.get("x-run-token")
    if not submission:
        raise HTTPException(404, "Submission not found.")
    if submission.user_id is not None and (not user or user.id != submission.user_id):
        raise HTTPException(404, "Submission not found.")
    if submission.user_id is None:
        if not access_token or not submission.access_token_hash or not hmac.compare_digest(token_digest(access_token), submission.access_token_hash):
            raise HTTPException(404, "Submission not found.")
    if not JUDGE0_URL or not submission.judge_token:
        raise HTTPException(503, "Judge service is not configured.")
    headers = {"X-Auth-Token": JUDGE0_TOKEN} if JUDGE0_TOKEN else {}
    try:
        async with httpx.AsyncClient(timeout=JUDGE0_TIMEOUT_SECONDS) as client:
            resp = await client.get(f"{JUDGE0_URL}/submissions/{submission.judge_token}?base64_encoded=false", headers=headers)
            resp.raise_for_status()
            result = resp.json()
    except httpx.HTTPError:
        raise HTTPException(502, "Could not retrieve the execution result.")
    status, stdout, stderr, compile_output, memory = _status_from_judge(result)
    submission.status = status
    submission.stdout = stdout[:20000]
    submission.stderr = stderr[:20000]
    submission.compile_output = compile_output[:20000]
    submission.time_seconds = result.get("time")
    submission.memory_kb = memory
    db.commit()
    return {"id": submission.id, "status": status, "stdout": stdout[:20000], "stderr": stderr[:20000],
            "compile_output": compile_output[:20000], "time_seconds": result.get("time"), "memory_kb": memory,
            "complexity": submission.complexity,
            "message": "Execution completed. This is a run result, not a full problem verdict." if status == "Executed" else None}


@app.get("/api/submissions")
def submissions(limit: int = 30, user: User = Depends(require_user), db: Session = Depends(db_session)):
    rows = db.scalars(select(Submission).where(Submission.user_id == user.id).order_by(Submission.created_at.desc()).limit(max(1, min(limit, 100)))).all()
    return {"items": [{"id": s.id, "language": s.language, "status": s.status, "created_at": s.created_at.isoformat(),
                       "time_seconds": s.time_seconds, "memory_kb": s.memory_kb, "complexity": s.complexity,
                       "problem": (db.get(Problem, s.problem_id).title if s.problem_id and db.get(Problem, s.problem_id) else "Scratch run"),
                       "test_cases": len(s.judge_tokens or []), "passed": sum(1 for c in (s.case_results or []) if c.get("passed"))} for s in rows]}


@app.get("/api/roadmaps")
def roadmaps():
    return {"items": [
        {"name": "Foundations to Interview Ready", "level": "Beginner → Intermediate", "duration": "12 weeks", "description": "Build fluency in arrays, strings, hashing, linked lists, stacks, queues, trees and core problem-solving patterns.", "steps": ["Complexity analysis", "Arrays and strings", "Hashing and prefix sums", "Two pointers and sliding windows", "Linked lists, stacks and queues", "Binary search", "Trees and recursion", "Greedy and introductory DP"]},
        {"name": "Graph Algorithms", "level": "Intermediate", "duration": "6 weeks", "description": "Move from graph representation to traversal, shortest paths and spanning trees.", "steps": ["Graph representations", "BFS and DFS", "Connected components", "Topological sorting", "Shortest paths", "Minimum spanning trees and DSU"]},
        {"name": "Dynamic Programming", "level": "Intermediate → Advanced", "duration": "8 weeks", "description": "Learn to recognise states, transitions, optimisations and classic DP families.", "steps": ["Recursion and memoization", "1D and grid DP", "Knapsack families", "Subsequence DP", "LIS and string DP", "Tree and bitmask DP"]},
        {"name": "Competitive Programming Core", "level": "Intermediate → Advanced", "duration": "10 weeks", "description": "Strengthen implementation speed, mathematics, greedy reasoning and contest technique.", "steps": ["Implementation and complexity", "Sorting and binary search", "Greedy proofs", "Number theory", "Combinatorics", "Bitmasks", "Segment tree and Fenwick tree", "Timed virtual contests"]},
    ]}


@app.get("/api/admin/summary")
def admin_summary(user: User = Depends(require_admin), db: Session = Depends(db_session)):
    return {"users": db.scalar(select(func.count(User.id))) or 0,
            "problems": db.scalar(select(func.count(Problem.id))) or 0,
            "submissions": db.scalar(select(func.count(Submission.id))) or 0,
            "discussions": db.scalar(select(func.count(Discussion.id))) or 0,
            "pending_reports": db.scalar(select(func.count(DiscussionReport.id)).where(DiscussionReport.resolved.is_(False))) or 0,
            "judge_configured": bool(JUDGE0_URL)}


@app.delete("/api/account")
def delete_account(request: Request, response: Response, user: User = Depends(require_user), db: Session = Depends(db_session)):
    _check_same_origin(request)
    if user.role == "admin" and (db.scalar(select(func.count(User.id)).where(User.role == "admin")) or 0) <= 1:
        raise HTTPException(409, "Create another administrator before deleting the last admin account.")
    # Delete explicitly as well as relying on FK cascades; this also works with SQLite defaults.
    db.query(AuthSession).filter(AuthSession.user_id == user.id).delete(synchronize_session=False)
    db.query(UserProgress).filter(UserProgress.user_id == user.id).delete(synchronize_session=False)
    db.query(Activity).filter(Activity.user_id == user.id).delete(synchronize_session=False)
    db.query(Bookmark).filter(Bookmark.user_id == user.id).delete(synchronize_session=False)
    db.query(Note).filter(Note.user_id == user.id).delete(synchronize_session=False)
    db.query(ContestParticipant).filter(ContestParticipant.user_id == user.id).delete(synchronize_session=False)
    # Remove the user's own activity and all child records on threads they own.
    # Explicit cleanup is needed for SQLite deployments where FK cascades may be off.
    owned_discussion_ids = list(db.scalars(select(Discussion.id).where(Discussion.user_id == user.id)).all())
    db.query(DiscussionReport).filter(DiscussionReport.user_id == user.id).delete(synchronize_session=False)
    db.query(DiscussionVote).filter(DiscussionVote.user_id == user.id).delete(synchronize_session=False)
    db.query(DiscussionComment).filter(DiscussionComment.user_id == user.id).delete(synchronize_session=False)
    if owned_discussion_ids:
        db.query(DiscussionReport).filter(DiscussionReport.discussion_id.in_(owned_discussion_ids)).delete(synchronize_session=False)
        db.query(DiscussionVote).filter(DiscussionVote.discussion_id.in_(owned_discussion_ids)).delete(synchronize_session=False)
        db.query(DiscussionComment).filter(DiscussionComment.discussion_id.in_(owned_discussion_ids)).delete(synchronize_session=False)
    db.query(Discussion).filter(Discussion.user_id == user.id).delete(synchronize_session=False)
    db.query(Submission).filter(Submission.user_id == user.id).delete(synchronize_session=False)
    draft_ids = list(db.scalars(select(CodeDraft.id).where(CodeDraft.user_id == user.id)).all())
    if draft_ids:
        db.query(CodeDraftVersion).filter(CodeDraftVersion.draft_id.in_(draft_ids)).delete(synchronize_session=False)
    db.query(CodeDraft).filter(CodeDraft.user_id == user.id).delete(synchronize_session=False)
    db.delete(user)
    db.commit()
    response.delete_cookie("algoforge_session", path="/")
    return {"ok": True}


@app.get("/home", include_in_schema=False)
def legacy_home_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/#/dashboard", status_code=301)


@app.get("/sitemap.xml", include_in_schema=False)
def sitemap():
    paths = ["/", "/privacy", "/terms"]
    body = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">" + "".join(f"<url><loc>{PUBLIC_BASE_URL}{p}</loc></url>" for p in paths) + "</urlset>"
    return Response(content=body, media_type="application/xml")


@app.get("/robots.txt", include_in_schema=False)
def robots():
    return Response(content=f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /app/\nSitemap: {PUBLIC_BASE_URL}/sitemap.xml\n", media_type="text/plain")


@app.get("/favicon.svg", include_in_schema=False)
def favicon():
    return FileResponse(ROOT / "static" / "favicon.svg", media_type="image/svg+xml")


app.mount("/assets", StaticFiles(directory=ROOT / "static"), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
def frontend(full_path: str):
    # FastAPI serves a pre-rendered public HTML shell; authenticated workspace views hydrate client-side.
    if full_path.startswith("api/"):
        raise HTTPException(404, "Not found")
    return FileResponse(ROOT / "static" / "index.html")



