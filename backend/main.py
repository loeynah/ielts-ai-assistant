from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.auth_service import login as auth_login
from app.auth_service import register as auth_register
from app.chat_service import build_plan_reply
from app.config import llm_config_status
from app.history_store import list_practice_records, save_practice_record
from app.listening_service import diagnose_listening, list_lessons
from app.reading_service import assistant_reply, diagnose_reading
from app.score_utils import estimated_listening_band, format_ielts_band, round_ielts_band
from app.speaking_service import grade_speaking_exam, grade_speaking_practice
from app.task_store import get_tasks, replace_tasks
from app.user_store import bootstrap_storage, get_user_by_token, push_inbox, update_profile, update_skill_score
from app.writing_service import grade_writing


@asynccontextmanager
async def lifespan(_app: FastAPI):
    bootstrap_storage()
    yield


app = FastAPI(title="IELTS AI Prep Companion API", version="0.3.0", lifespan=lifespan)

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


class RegisterRequest(BaseModel):
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
    exam_id: str = "practice"
    exam_title: str = "口语自定义训练"
    rounds: int = 1


class TaskItem(BaseModel):
    id: int | None = None
    category: str = "other"
    content: str
    done: bool = False
    pinned: bool = False
    source: str = "system"


class TasksReplaceRequest(BaseModel):
    tasks: list[TaskItem] = Field(default_factory=list)


@app.get("/api/health/llm")
def get_llm_health():
    return llm_config_status()


@app.post("/api/auth/register")
def post_register(body: RegisterRequest):
    try:
        return auth_register(body.username, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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
    try:
        updated = update_profile(
            user["username"],
            exam_date=body.exam_date,
            target_score=body.target_score,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return updated


@app.get("/api/history/{module}")
def get_module_history(module: str, user: dict = Depends(require_user)):
    allowed = {"listening", "reading", "speaking", "writing"}
    if module not in allowed:
        raise HTTPException(status_code=404, detail="未知模块")
    return list_practice_records(user["username"], module)


@app.get("/api/tasks")
def get_user_tasks(user: dict = Depends(require_user)):
    return get_tasks(user["username"])


@app.put("/api/tasks")
def put_user_tasks(body: TasksReplaceRequest, user: dict = Depends(require_user)):
    tasks = [t.model_dump() for t in body.tasks]
    return replace_tasks(user["username"], tasks)


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
    save_practice_record(
        user["username"],
        module="listening",
        record_type="diagnose",
        ref_id=body.lesson_id,
        title=f"听力 Lesson {body.lesson_id}",
        overall_score=score,
        payload=result,
        meta={"lesson_id": body.lesson_id, "title": f"听力 Lesson {body.lesson_id}"},
    )
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
    save_practice_record(
        user["username"],
        module="reading",
        record_type="diagnose",
        ref_id=body.exam_id,
        title=f"阅读 {body.exam_id}",
        overall_score=score,
        payload=result,
        meta={"exam_id": body.exam_id, "title": f"阅读 {body.exam_id}"},
    )
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
    audio_count = len(body.part1) + (1 if body.part2 else 0) + len(body.part3)
    save_practice_record(
        user["username"],
        module="speaking",
        record_type="exam",
        ref_id=body.exam_id,
        title=f"口语模考 {body.exam_id}",
        overall_score=result.get("overall_score"),
        payload=result,
        meta={
            "exam_id": body.exam_id,
            "exam_title": f"口语模考 {body.exam_id}",
            "mode": "exam",
            "audio_count": audio_count,
        },
    )
    return result


@app.post("/api/speaking/grade-practice")
async def post_speaking_practice(body: SpeakingPracticeRequest, user: dict = Depends(require_user)):
    result = await grade_speaking_practice(body.question, body.transcript, body.duration)
    score = result.get("overall_score") or result.get("score") or 0
    if score > 0:
        update_skill_score(user["username"], "speaking", score)
        push_inbox(
            user["username"],
            module="speaking",
            title="口语自定义训练单题批改已完成",
            meta=f"评分 {format_ielts_band(score)}",
        )
    save_practice_record(
        user["username"],
        module="speaking",
        record_type="practice",
        ref_id=body.exam_id,
        title=body.exam_title,
        overall_score=score if score > 0 else None,
        payload=result,
        meta={
            "exam_id": body.exam_id,
            "exam_title": body.exam_title,
            "mode": "practice",
            "rounds": body.rounds,
        },
    )
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
    save_practice_record(
        user["username"],
        module="writing",
        record_type="grade",
        ref_id=body.task_id,
        title=f"写作 {body.task_id}",
        overall_score=result.get("overall_score"),
        payload=result,
        meta={"task_id": body.task_id, "task_type": body.task_type},
    )
    return result
