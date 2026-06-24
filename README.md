# IELTS AI Prep Companion

雅思智能备考助手 — Vue 3 前端 + FastAPI 后端，覆盖听 / 读 / 说 / 写四大模块，接入大模型进行 AI 批改、错因诊断与学习计划生成。

> 仓库地址：[github.com/loeynah/ielts-ai-assistant](https://github.com/loeynah/ielts-ai-assistant)

---

## 功能概览

| 模块 | 路由 | 说明 |
|------|------|------|
| **主页** | `/dashboard` | AI 智能管家对话、今日任务打卡、考试倒计时日历、批改通知、四科能力诊断 |
| **听力** | `/listening` | 4 套真题 HTML 练习 + 客观题核对 + AI 深度诊断（逐题切片解析） |
| **阅读** | `/reading` | 6 套真题双栏精读 + 客观题批改 + AI 错因诊断 + 长难句/词汇助手 |
| **口语** | `/speaking` | 标准模考（Part 1→2→3 盲盒录音）+ Part 3 自定义训练 + STT/TTS + 得分走势 |
| **写作** | `/writing` | Task1/Task2 机考模拟 + AI 四维深度批改（TR/TA、CC、LR、GRA） |

### 核心能力

- **SQLite 本地持久化**：用户画像、四科分数、考试日期、AI 通知收件箱、练习历史、今日任务均写入 `backend/data/app.db`，刷新或重新登录不丢失
- **多账号隔离**：支持注册新账号，各账号数据独立沙盒
- **新用户空白起步**：注册账号无预设目标分/考试日期/能力分/今日任务，需与 AI 小助手对话或手动设置后才会更新
- **admin 演示账号**：首次启动自动种子化，含考试日、目标分与默认任务（见下方登录说明）
- **严厉判分熔断**：口语/写作字数不足、转写无效时后端强制低分，不依赖模型「自觉」
- **LLM 降级**：未配置 API Key 或调用失败时，听读写说模块自动回退 Mock 结果，不影响客观题练习

---

## 账号说明

| 账号类型 | 登录方式 | 初始数据 |
|----------|----------|----------|
| **admin**（种子） | 用户名 `admin`，密码 `123456`（可在 `.env` 修改） | 考试日 2026-06-25、目标 7.0、四科 6.0、4 条默认今日任务 |
| **新注册用户** | 登录页「没有账号？立即注册」 | 目标分/考试日期/能力分/任务均为空，与 AI 对话后同步 |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3、Pinia、Vue Router、Tailwind CSS v4、ECharts、Vite |
| 后端 | FastAPI、SQLite（stdlib）、httpx、pypdf、python-dotenv |
| AI | 默认 [SiliconFlow](https://cloud.siliconflow.cn) · `deepseek-ai/DeepSeek-V3`（OpenAI 兼容接口） |

---

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.11+
- SiliconFlow 或 DeepSeek API Key（可选；无 Key 时 AI 功能降级 Mock）

### 1. 克隆仓库

```bash
git clone https://github.com/loeynah/ielts-ai-assistant.git
cd ielts-ai-assistant
```

### 2. 后端

```powershell
cd backend
copy .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY（SiliconFlow 控制台复制，sk- 开头）

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

启动后自动创建 SQLite 数据库并种子化 `admin` 账号。

**健康检查：**

```text
GET http://127.0.0.1:8000/api/health/llm
```

返回 `"configured": true` 表示 API Key 已正确配置。

### 3. 前端

```powershell
# 在项目根目录
npm install
npm run dev
```

浏览器访问：<http://localhost:5173>

### 4. 生产构建

```powershell
npm run build
npm run preview
```

---

## 环境变量

### 后端 `backend/.env`

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | LLM API 密钥（须为 ASCII，如 `sk-...`） | 空 |
| `DEEPSEEK_BASE_URL` | API 基址 | `https://api.siliconflow.cn/v1` |
| `DEEPSEEK_MODEL` | 模型名 | `deepseek-ai/DeepSeek-V3` |
| `ADMIN_USERNAME` | 种子 admin 用户名 | `admin` |
| `ADMIN_PASSWORD` | 种子 admin 密码 | `123456` |

**改回官方 DeepSeek：**

```env
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

> ⚠️ `backend/.env` 与 `backend/data/` 已加入 `.gitignore`，**切勿提交到 Git**。

### 前端（可选）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `VITE_API_BASE` | 后端 API 地址 | `http://localhost:8000` |

---

## 数据持久化

| 存储 | 路径 / 表 | 内容 |
|------|-----------|------|
| SQLite | `backend/data/app.db` | 用户、会话、四科分数、考试日期、收件箱 |
| 练习记录 | `practice_records` 表 | 听/读/说/写每次 AI 诊断或批改的完整 JSON |
| 今日任务 | `daily_tasks` 表 | 打卡清单（支持 AI 同步、手动添加、置顶） |

换账号登录后，主页通知、日历星标、口语得分走势图、任务清单均从后端拉取，互不干扰。

---

## 项目结构

```
ielts-ai-dashboard/
├── assets/                      # 内置题库静态资源
│   ├── reading-exams/           # 6 套阅读 JS 题库
│   ├── listening/               # 4 套听力 HTML（音频/PDF 需自行补充）
│   ├── writing/                 # Task1 图表 PNG
│   └── CONTENT.md               # 题库清单说明
├── backend/
│   ├── main.py                  # FastAPI 入口 + 全部路由
│   ├── requirements.txt
│   ├── .env.example
│   ├── data/                    # SQLite（本地生成，不提交 Git）
│   └── app/
│       ├── db.py                # 数据库初始化
│       ├── user_store.py        # 用户 / 会话 / 收件箱
│       ├── history_store.py       # 练习历史
│       ├── task_store.py          # 今日任务
│       ├── auth_service.py        # 登录 / 注册
│       ├── chat_service.py        # 主页 AI 管家
│       ├── prompt_manager.py      # 全科 Prompt 模板
│       ├── grading_rules.py       # 字数熔断等硬性规则
│       ├── listening_service.py
│       ├── reading_service.py
│       ├── speaking_service.py
│       └── writing_service.py
├── src/
│   ├── config/                  # 题目注册表
│   ├── views/                   # 五大页面 + 登录
│   ├── components/              # 各模块 UI
│   ├── api/                     # 前端 API 客户端
│   └── stores/                  # Pinia（auth / user / tasks）
├── vite.config.js               # 挂载 assets/ 为静态服务
└── package.json
```

---

## 内置题目

### 阅读（6 套）

- 配置：`src/config/readingLessons.js`
- 数据：`assets/reading-exams/*.js`

### 听力（4 课）

- 配置：`src/config/listeningLessons.js`
- 数据：`assets/listening/<课程目录>/`（HTML、audio.mp3、PDF）

### 口语（3 套模考）

- 配置：`src/config/speakingExams.js`
- Set 1 · Clothing & Communication / Set 2 · Science & Languages / Set 3 · Parks & Ambition

### 写作（3 套 + 2 道 Task2 演示）

- 配置：`src/config/writingExams.js`
- 图表：`assets/writing/TASK1-*.png`

详细清单见 [assets/CONTENT.md](./assets/CONTENT.md)。

---

## API 概览

### 鉴权与用户

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/auth/register` | 注册新账号 |
| POST | `/api/auth/login` | 登录，返回 token + 用户画像 |
| GET | `/api/user/profile` | 获取画像（分数、考试日、收件箱） |
| PATCH | `/api/user/profile` | 更新考试日期 / 目标分 |

### 主页与任务

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/chat` | AI 智能管家（计划、科普、META 同步） |
| GET | `/api/tasks` | 获取今日任务 |
| PUT | `/api/tasks` | 保存今日任务 |
| GET | `/api/health/llm` | LLM 配置状态 |

### 练习与批改

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/listening/lessons` | 听力课程列表 |
| POST | `/api/listening/diagnose` | 听力 AI 诊断 + 持久化 |
| POST | `/api/reading/diagnose` | 阅读 AI 诊断 + 持久化 |
| POST | `/api/reading/assistant` | 阅读长难句 / 词汇助手 |
| POST | `/api/speaking/grade-exam` | 口语模考批改 + 持久化 |
| POST | `/api/speaking/grade-practice` | 口语自定义训练（四维解析） |
| POST | `/api/writing/grade` | 写作四维批改 + 持久化 |

### 历史记录

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/history/{module}` | 拉取练习历史（`listening` / `reading` / `speaking` / `writing`） |

请求头：`Authorization: Bearer <token>`

---

## 使用流程（新用户）

1. 注册账号并登录
2. 在主页与 **AI 智能管家** 对话，说明目标分、剩余天数、薄弱项
3. 点击「**将此计划一键同步至今日打卡清单**」，或手动「添加打卡」
4. 进入听 / 读 / 说 / 写模块练习；AI 批改后分数与通知自动更新
5. 口语模块可查看 **得分走势**（FC / LR / GRA 分项折线）

---

## 常见问题

**Q: 没有 API Key 能用吗？**  
A: 可以。登录、做题、客观题核对、持久化均正常；AI 批改/诊断/聊天会返回 Mock 或友好错误提示。

**Q: AI 聊天报 `ascii codec` 或 Key 错误？**  
A: 检查 `.env` 中 `DEEPSEEK_API_KEY` 是否为 SiliconFlow 复制的真实 `sk-` 密钥，**不要保留中文占位符**。修改后重启后端。

**Q: 听力没有声音？**  
A: 确认 `assets/listening/<课程>/audio.mp3` 存在；若缺失，从原始题库目录复制。

**Q: 如何新增阅读题？**  
A: 将 zyz 格式 `.js` 放入 `assets/reading-exams/`，并在 `src/config/readingLessons.js` 注册 `examId`。

**Q: 数据库存在哪？如何清空？**  
A: `backend/data/app.db`。删除该文件后重启后端会重建库并重新种子化 admin（**所有用户数据会丢失**）。

**Q: 换电脑如何迁移数据？**  
A: 复制整个 `backend/data/app.db` 到新机器同路径即可。

---

## 开发说明

- 后端热重载：`uvicorn main:app --reload --port 8000`
- 前端热重载：`npm run dev`
- Python 缓存 `__pycache__/`、`*.pyc` 不应提交 Git
- 提交前确认未包含 `backend/.env` 与 `backend/data/`

---

## License

Private / 学习用途。题库内容版权归原作者所有，请勿用于商业分发。
