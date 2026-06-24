"""
IELTS AI Prep Companion — FastAPI 全栈入口

启动: cd backend && uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.auth_service import login as auth_login
from app.chat_service import build_plan_reply
from app.listening_service import diagnose_listening, list_lessons
from app.reading_service import assistant_reply, diagnose_reading
from app.speaking_service import grade_speaking_exam, grade_speaking_practice
from app.user_store import get_user_by_token, push_inbox, update_profile, update_skill_score
from app.writing_service import grade_writing
from app.config import llm_config_status
from app.score_utils import estimated_listening_band, format_ielts_band, round_ielts_band

app = FastAPI(title="IELTS AI Prep Companion API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_token(authorization: str | None = Header(default=None)) -> str | None:
    if not authorization:
        return None
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization


def require_user(token: str | None = Depends(get_token)) -> dict:
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="会话已失效")
    return user


class LoginRequest(BaseModel):
    username: str
    password: str


class WrongAnswer(BaseModel):
    user_ans: str
    correct_ans: str


class QuestionMeta(BaseModel):
    id: str
    num: str


class ListeningDiagnoseRequest(BaseModel):
    lesson_id: str
    wrong_answers: dict[str, WrongAnswer] = Field(default_factory=dict)
    all_answers: dict[str, WrongAnswer] = Field(default_factory=dict)
    question_meta: list[QuestionMeta] = Field(default_factory=list)


class ReadingDiagnoseRequest(BaseModel):
    exam_id: str
    wrong_answers: dict[str, WrongAnswer] = Field(default_factory=dict)
    all_answers: dict[str, WrongAnswer] = Field(default_factory=dict)
    passage_excerpt: str = ""
    question_meta: list[QuestionMeta] = Field(default_factory=list)


class ReadingAssistantRequest(BaseModel):
    mode: str = "sentence"
    text: str
    exam_title: str = ""


class ChatRequest(BaseModel):
    message: str


class ProfilePatchRequest(BaseModel):
    exam_date: str | None = None
    target_score: float | None = None


class WritingGradeRequest(BaseModel):
    task_id: str
    task_type: str
    essay_text: str
    prompt: str = ""


class SpeakingAnswerItem(BaseModel):
    question: str = ""
    transcript: str = ""
    duration: float = 0


class SpeakingExamRequest(BaseModel):
    exam_id: str = ""
    part1: list[SpeakingAnswerItem] = Field(default_factory=list)
    part2: SpeakingAnswerItem | None = None
    part3: list[SpeakingAnswerItem] = Field(default_factory=list)


class SpeakingPracticeRequest(BaseModel):
    question: str
    transcript: str
    duration: float = 0


@app.get("/api/health/llm")
def get_llm_health():
    return llm_config_status()


@app.post("/api/auth/login")
def post_login(body: LoginRequest):
    result = auth_login(body.username, body.password)
    if not result:
        raise HTTPException(status_code=401, detail="账号或密码错误")
    return result


@app.get("/api/user/profile")
def get_profile(user: dict = Depends(require_user)):
    return user


@app.patch("/api/user/profile")
def patch_profile(body: ProfilePatchRequest, user: dict = Depends(require_user)):
    updated = update_profile(
        user["username"],
        exam_date=body.exam_date,
        target_score=body.target_score,
    )
    return updated


@app.post("/api/chat")
async def post_chat(body: ChatRequest, user: dict = Depends(require_user)):
    return await build_plan_reply(body.message, user)


@app.get("/api/listening/lessons")
def get_lessons():
    return list_lessons()


@app.post("/api/listening/diagnose")
async def post_listening_diagnose(body: ListeningDiagnoseRequest, user: dict = Depends(require_user)):
    meta = [m.model_dump() for m in body.question_meta]
    result = await diagnose_listening(
        body.lesson_id, body.wrong_answers, body.all_answers, meta
    )
    items = result.get("items") or []
    total = len(items)
    correct = sum(1 for i in items if i.get("is_correct"))
    wrong_count = total - correct
    score = estimated_listening_band(correct, total)
    update_skill_score(user["username"], "listening", score)
    push_inbox(
        user["username"],
        module="listening",
        title=f"听力 Lesson {body.lesson_id} AI 深度诊断已送达",
        meta=f"预估分 {format_ielts_band(score)} · {wrong_count} 题需复盘",
    )
    result["updated_score"] = score
    return result


@app.post("/api/reading/diagnose")
async def post_reading_diagnose(body: ReadingDiagnoseRequest, user: dict = Depends(require_user)):
    meta = [m.model_dump() for m in body.question_meta]
    result = await diagnose_reading(
        body.exam_id,
        body.wrong_answers,
        body.passage_excerpt,
        body.all_answers,
        meta,
    )
    items = result.get("items") or []
    total = len(items)
    correct = sum(1 for i in items if i.get("is_correct"))
    score = estimated_listening_band(correct, total) if total else 6.0
    update_skill_score(user["username"], "reading", score)
    push_inbox(
        user["username"],
        module="reading",
        title=f"阅读 {body.exam_id} AI 深度诊断已送达",
        meta=f"预估分 {format_ielts_band(score)}",
    )
    result["updated_score"] = score
    return result


@app.post("/api/reading/assistant")
async def post_reading_assistant(body: ReadingAssistantRequest, user: dict = Depends(require_user)):
    reply = await assistant_reply(body.mode, body.text, body.exam_title)
    return {"reply": reply}


@app.post("/api/speaking/grade-exam")
async def post_speaking_exam(body: SpeakingExamRequest, user: dict = Depends(require_user)):
    payload = {
        "exam_id": body.exam_id,
        "part1": [p.model_dump() for p in body.part1],
        "part2": body.part2.model_dump() if body.part2 else {},
        "part3": [p.model_dump() for p in body.part3],
    }
    result = await grade_speaking_exam(payload)
    if result.get("overall_score", 0) > 0:
        update_skill_score(user["username"], "speaking", result["overall_score"])
    push_inbox(
        user["username"],
        module="speaking",
        title="口语模拟考试 AI 批改报告已送达",
        meta=f"Overall {result['overall_score']}",
    )
    return result


@app.post("/api/speaking/grade-practice")
async def post_speaking_practice(body: SpeakingPracticeRequest, user: dict = Depends(require_user)):
    result = await grade_speaking_practice(body.question, body.transcript, body.duration)
    if result.get("score", 0) > 0:
        update_skill_score(user["username"], "speaking", result["score"])
    return result


@app.post("/api/writing/grade")
async def post_writing_grade(body: WritingGradeRequest, user: dict = Depends(require_user)):
    result = await grade_writing(body.task_id, body.task_type, body.essay_text, body.prompt)
    update_skill_score(user["username"], "writing", result["overall_score"])
    push_inbox(
        user["username"],
        module="writing",
        title="写作 AI 深度批改报告已送达",
        meta=f"Overall {result['overall_score']}",
    )
    return result
