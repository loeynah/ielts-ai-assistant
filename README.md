# IELTS AI Prep Companion

雅思智能备考助手 — Vue 3 前端 + FastAPI 后端，覆盖听 / 读 / 说 / 写四大模块，接入 DeepSeek 等大模型进行 AI 批改与诊断。

## 功能概览

| 模块 | 路由 | 说明 |
|------|------|------|
| 主页 | `/dashboard` | AI 学习计划对话、今日任务清单、考试倒计时日历 |
| 听力 | `/listening` | 4 套真题 HTML 练习 + 客观题核对 + AI 深度诊断 |
| 阅读 | `/reading` | 6 套真题双栏精读 + 客观题批改 + AI 错因诊断 |
| 口语 | `/speaking` | 标准模拟考试（Part 1→2→3）+ Part 3 自定义训练 + STT/TTS |
| 写作 | `/writing` | 3 套 Task1+Task2 + 2 道 Task2 单题 + AI 四维评分 |

默认登录：`admin` / `123456`（可在后端 `.env` 修改）

## 技术栈

- **前端**：Vue 3、Pinia、Vue Router、Tailwind CSS v4、ECharts、Vite
- **后端**：FastAPI、httpx、pypdf、python-dotenv
- **AI**：DeepSeek API（未配置 Key 时自动降级 Mock 响应）

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.11+
- （可选）DeepSeek 或 SiliconFlow API Key

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd ielts-ai-dashboard
```

### 2. 后端

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. 前端

```bash
# 在项目根目录
npm install
npm run dev
```

浏览器访问：<http://localhost:5173>

### 4. 生产构建

```bash
npm run build
npm run preview
```

## 环境变量

### 后端 `backend/.env`

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | API 密钥 | 空（Mock 模式） |
| `DEEPSEEK_BASE_URL` | API 地址 | `https://api.deepseek.com/v1` |
| `DEEPSEEK_MODEL` | 模型名 | `deepseek-chat` |
| `ADMIN_USERNAME` | 登录用户名 | `admin` |
| `ADMIN_PASSWORD` | 登录密码 | `123456` |

### 前端（可选）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `VITE_API_BASE` | 后端地址 | `http://localhost:8000` |

## 项目结构

```
ielts-ai-dashboard/
├── assets/                 # 内置题库静态资源
│   ├── reading-exams/      # 6 套阅读 JS 题库
│   ├── listening/          # 4 套听力 HTML（音频/PDF 需自行补充）
│   └── writing/            # 3 张 Task1 图表 PNG
├── backend/                # FastAPI 服务
│   ├── main.py
│   ├── requirements.txt
│   └── app/                # 鉴权、聊天、听读写说 AI 服务
├── src/
│   ├── config/             # 题目注册表（阅读/听力/口语/写作）
│   ├── views/              # 五大页面
│   ├── components/         # 各模块 UI 组件
│   ├── api/                # 前端 API 客户端
│   └── stores/             # Pinia 状态
├── vite.config.js          # 挂载 assets/ 为静态服务
└── package.json
```

详细题库清单见 [assets/CONTENT.md](./assets/CONTENT.md)。

## 内置题目

### 阅读（6 套，Passage 1/2/3 各 2 课）

配置：`src/config/readingLessons.js`  
数据：`assets/reading-exams/*.js`

### 听力（4 课）

配置：`src/config/listeningLessons.js`  
数据：`assets/listening/<课程目录>/`（含 HTML、audio.mp3、PDF）

### 口语（3 套完整模拟）

配置：`src/config/speakingExams.js`（题目内联，无外部文件）

- Set 1 · Clothing & Communication
- Set 2 · Science & Languages
- Set 3 · Parks & Ambition

### 写作（3 套 + 2 道 Task2 演示）

配置：`src/config/writingExams.js`  
图表：`assets/writing/TASK1-1.png` 等

## API 概览

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/auth/login` | 登录 |
| GET/PATCH | `/api/user/profile` | 用户画像 / 考试日期 |
| POST | `/api/chat` | 主页 AI 学习计划 |
| POST | `/api/listening/diagnose` | 听力 AI 诊断 |
| POST | `/api/reading/diagnose` | 阅读 AI 诊断 |
| POST | `/api/reading/assistant` | 阅读长难句 / 词汇助手 |
| POST | `/api/speaking/grade-exam` | 口语模考批改 |
| POST | `/api/speaking/grade-practice` | 口语自定义训练批改 |
| POST | `/api/writing/grade` | 写作批改 |
| GET | `/api/health/llm` | LLM 配置状态 |

## 常见问题

**Q: 没有 API Key 能用吗？**  
A: 可以。登录、做题、客观题核对均正常；AI 批改/诊断会返回 Mock 结果。

**Q: 听力没有声音？**  
A: 确认 `assets/listening/<课程>/audio.mp3` 存在；若缺失，从原始题库目录复制同名文件。

**Q: 如何新增阅读题？**  
A: 将 zyz 格式 `.js` 放入 `assets/reading-exams/`，并在 `src/config/readingLessons.js` 注册 `examId`。

## License

Private / 学习用途。题库内容版权归原作者所有，请勿用于商业分发。
