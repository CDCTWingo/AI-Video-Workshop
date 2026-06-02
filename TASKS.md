# AI Video Workshop — 开发任务分解

## Phase 1: 环境搭建 & 配置 (预计2-3小时)

### Task 1.1: 安装系统依赖
- [ ] 安装 FFmpeg (`apt install ffmpeg`)
- [ ] 安装 ImageMagick (`apt install imagemagick`)
- [ ] 配置 ImageMagick policy.xml (允许视频字幕渲染)
- [ ] 验证: `ffmpeg -version`, `convert -version`

### Task 1.2: Python虚拟环境 & 依赖
- [ ] 在 `/root/projects/AI-Video-Workshop/` 创建 venv
- [ ] `pip install -r requirements.txt`
- [ ] 额外安装: `azure-cognitiveservices-speech` (Azure TTS SDK)
- [ ] 验证: `python -c "import moviepy; import edge_tts; import fastapi"`

### Task 1.3: 配置API Keys
- [ ] 复制 `config.example.toml` → `config.toml`
- [ ] 填入 Pexels API Key: `f6a4a08e...`
- [ ] 填入 LLM配置: `llm_provider = "openai"`, `openai_api_key = "sk-pPCu..."`, `openai_base_url = "https://www.shenve10.com/v1"`
- [ ] 填入 Azure Speech: `azure_api_key = "EtHCaLr..."`, `azure_base_url = "southeastasia"`
- [ ] 设置 `video_source = "pexels"`
- [ ] 验证: 启动API服务，调用健康检查

---

## Phase 2: 核心功能跑通 (预计3-4小时)

### Task 2.1: 启动FastAPI后端
- [ ] 启动 `python main.py` (端口8080)
- [ ] 验证 Swagger UI: `http://localhost:8080/docs`
- [ ] 测试 `POST /api/v1/videos` 端到端生成
- [ ] 确认6步pipeline全部走通: 文案→关键词→配音→字幕→素材→合成

### Task 2.2: 启动Streamlit前端
- [ ] 启动 `streamlit run webui/Main.py` (端口8501)
- [ ] 验证WebUI可访问
- [ ] 测试完整用户流程: 输入主题→配置参数→生成视频→预览→下载

### Task 2.3: Azure TTS集成验证
- [ ] 确认Azure Speech Key在MPT中可用
- [ ] 测试中英文TTS生成
- [ ] 验证声音列表加载
- [ ] 如果MPT原生不支持Azure Speech直接调用，需要适配 `voice.py`

### Task 2.4: 字幕生成验证
- [ ] 测试edge模式字幕生成
- [ ] 验证中英文字幕渲染
- [ ] 确认字幕位置/字体/颜色配置生效

---

## Phase 3: 虾壳平台预留 & 改造 (预计2-3小时)

### Task 3.1: 新增虾壳认证模块
- [ ] 创建 `app/services/xiake_auth.py` (接口预留，默认无账号模式)
- [ ] 创建 `app/services/xiake_billing.py` (接口预留，默认免费模式)
- [ ] 在 `config.toml` 新增 `[xiake]` 配置段
- [ ] 在 `app/config/config.py` 加载虾壳配置

### Task 3.2: CORS & 跨域配置
- [ ] 修改 `app/asgi.py` 添加虾壳域名到CORS白名单
- [ ] 临时设为 `allow_origins=["*"]` (开发阶段)
- [ ] 后续限制为虾壳具体域名

### Task 3.3: 品牌化改造
- [ ] 替换WebUI标题 "MoneyPrinterTurbo" → "AI Video Workshop"
- [ ] 替换API项目名 `project_name` 配置
- [ ] 隐藏配置面板 `hide_config = true` (Key已预设，无需用户配置)

### Task 3.4: 无账号登录模式
- [ ] 确保所有API端点无需认证即可调用
- [ ] 保留 `verify_token` 的调用入口(注释状态)，后续对接虾壳时启用
- [ ] 添加 `X-User-ID` header 支持(预留，当前不校验)

---

## Phase 4: 端到端验证 & 优化 (预计2小时)

### Task 4.1: 完整流程测试
- [ ] 测试主题: "5个提高效率的方法" (英文)
- [ ] 测试主题: "人工智能的未来" (中文)
- [ ] 验证竖屏9:16视频生成 (适合短视频平台)
- [ ] 验证横屏16:9视频生成

### Task 4.2: 错误处理 & 健壮性
- [ ] Pexels素材不足时的降级处理
- [ ] Azure TTS超时时的重试机制
- [ ] LLM调用失败时的错误提示
- [ ] 视频合成失败的日志记录

### Task 4.3: 性能优化
- [ ] 视频生成任务异步化确认(已有机制)
- [ ] 素材下载并发优化
- [ ] 生成进度实时反馈

---

## Phase 5: 生产部署准备 (待新服务器到位)

### Task 5.1: Docker化
- [ ] 修改 `docker-compose.yml` 适配我们的配置
- [ ] 构建Docker镜像
- [ ] 测试容器化部署

### Task 5.2: Nginx反向代理
- [ ] 配置SSL证书
- [ ] 配置反向代理到8501/8080
- [ ] 配置域名解析

### Task 5.3: 虾壳平台对接
- [ ] 对接虾壳用户认证API
- [ ] 对接虾壳计费扣费API
- [ ] 联调测试
- [ ] 上线

---

## 任务依赖关系

```
Task 1.1 → Task 1.2 → Task 1.3
                           ↓
Task 2.1 ──────────────→ Task 2.3 (TTS验证)
    ↓                        ↓
Task 2.2 ──────────────→ Task 2.4 (字幕验证)
                               ↓
                    Task 3.1 → 3.2 → 3.3 → 3.4
                                        ↓
                              Task 4.1 → 4.2 → 4.3
                                                    ↓
                                          Task 5.x (待服务器)
```

## 里程碑

| 里程碑 | 完成标志 | 预计时间 |
|--------|----------|----------|
| M1: 环境就绪 | 后端+前端可启动 | Day 1 |
| M2: 核心跑通 | 端到端生成一条视频 | Day 1 |
| M3: 虾壳预留 | 接口位置预留，品牌化完成 | Day 2 |
| M4: 验证通过 | 中英文各生成一条，质量OK | Day 2 |
| M5: 生产部署 | 新服务器Docker部署完成 | Day 3+ |
