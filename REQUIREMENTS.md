# AI Video Workshop — 需求规格 & 开发计划

> 基于 MoneyPrinterTurbo v1.2.9 (MIT) 改造，对接虾壳平台

## 一、项目概述

**产品名**: AI Video Workshop (AI视频工坊)  
**定位**: 输入主题 → 全自动生成短视频（文案→素材→配音→字幕→合成）  
**部署**: 给虾壳平台一个URL链接，iframe或新页签调起  
**许可**: MIT（原项目 + 改造代码均可商用）

## 二、核心流程

```
用户输入主题 + 参数
  → ① LLM生成文案 (gpt-5.4 via shenve10.com)
  → ② LLM生成搜索关键词 (gpt-5.4)
  → ③ Azure TTS配音 (southeastasia)
  → ④ 生成字幕 (edge模式)
  → ⑤ Pexels下载视频素材
  → ⑥ MoviePy+FFmpeg合成最终视频
  → 输出视频文件 + 播放/下载链接
```

## 三、API资源配置

| 资源 | 提供方 | Key/配置 | 状态 |
|------|--------|----------|------|
| 视频素材 | Pexels | `f6a4a08e...` | ✅ 已验证 |
| LLM文案+关键词 | shenve10.com | gpt-5.4, `sk-pPCu...` | ✅ 已验证 |
| TTS配音 | Azure Speech | southeastasia, `EtHCaLr...` | ✅ 已验证 |
| 虾壳平台接口 | 虾壳 | 待提供 | ⏳ 预留 |
| 图片生成(可选) | shenve10.com | gpt-image-2 | ✅ 后续优化用 |

## 四、部署架构

### 当前：本地开发测试
```
本机 (148.153.253.19)
├── Streamlit WebUI  :8501  (前端)
├── FastAPI Backend  :8080  (API)
├── FFmpeg + ImageMagick     (视频合成)
└── 本地文件系统              (素材/视频存储)
```

### 后续：生产服务器部署
```
新服务器
├── Docker Compose
│   ├── webui容器  :8501  (Streamlit前端)
│   ├── api容器    :8080  (FastAPI后端)
│   └── nginx      :80/443 (反向代理 + SSL)
├── 对象存储(S3/OSS)         (视频/素材持久化)
└── 虾壳平台 → iframe/新页签调起
```

## 五、功能需求

### 5.1 P0 — 核心功能（本次开发）

**F1: 视频主题输入**
- 用户输入视频主题/关键词
- 选择视频比例：横屏16:9 / 竖屏9:16 / 方形1:1
- 选择配音声音（Azure TTS声音列表）
- 选择字幕样式（字体/颜色/位置）
- 选择BGM（随机/指定/无）

**F2: 全自动视频生成**
- 6步pipeline全自动执行
- 实时显示当前步骤和进度
- 生成完成后可预览和下载

**F3: 视频任务管理**
- 查看历史生成任务列表
- 查询任务状态（排队中/生成中/已完成/失败）
- 重新生成/删除任务

**F4: API接口（供虾壳平台调用）**
- `POST /api/v1/videos` — 创建视频生成任务
- `GET /api/v1/tasks/{id}` — 查询任务状态
- `GET /api/v1/tasks` — 任务列表
- `GET /api/v1/videos/stream/{path}` — 流式播放
- `GET /api/v1/videos/download/{path}` — 下载视频

### 5.2 P1 — 虾壳平台对接（接口到位后开发）

**F5: 用户认证（预留接口）**
- 虾壳SSO/JWT/Cookie认证
- 无账号登录模式（当前默认）
- 用户身份信息获取

**F6: 计费扣费（预留接口）**
- 视频生成按次/按Token扣费
- 余额查询
- 消费日志上报

**F7: 会员权限分级**
- normal: 可预览，不可下载
- member: 可下载标清
- diamond: 可下载高清

### 5.3 P2 — 优化迭代（后续）

**F8: AI图片素材生成**
- 接入 gpt-image-2 生成独特视频素材
- 替代/补充 Pexels 素材库
- 避免视频素材重复

**F9: 视频模板系统**
- 预设视频风格模板（新闻播报/知识科普/产品推广...）
- 一键套用模板参数

**F10: 批量生成**
- 一次输入多个主题批量生成
- 定时生成（每日自动生成N条视频）

**F11: 自动发布**
- 生成后自动发布到 TikTok/YouTube Shorts/Instagram

## 六、虾壳平台接口预留

### 6.1 用户认证接口（待虾壳提供）
```python
# 预留位置: app/services/xiake_auth.py
class XiakeAuthService:
    def verify_user(self, token: str) -> dict:
        """验证用户身份，返回用户信息"""
        # TODO: 对接虾壳认证API
        # 返回: {"user_id": "", "level": "normal|member|diamond", "balance": 0.0}
        pass

    def get_user_info(self, user_id: str) -> dict:
        """获取用户详情"""
        # TODO: 对接虾壳用户信息API
        pass
```

### 6.2 计费扣费接口（待虾壳提供）
```python
# 预留位置: app/services/xiake_billing.py
class XiakeBillingService:
    def check_balance(self, user_id: str) -> float:
        """查询用户余额"""
        # TODO: 对接虾壳余额查询API
        pass

    def deduct(self, user_id: str, amount: float, description: str) -> bool:
        """扣费"""
        # TODO: 对接虾壳扣费API
        pass

    def get_consumption_log(self, user_id: str) -> list:
        """获取消费记录"""
        # TODO: 对接虾壳消费日志API
        pass
```

### 6.3 无账号登录模式
```python
# 当前默认: 无需认证即可使用
# 虾壳对接后: 通过URL参数/Header传递用户token
# config.toml 中添加:
[xiake]
enabled = false  # 对接后改为 true
auth_url = ""    # 认证接口
billing_url = "" # 计费接口
api_key = ""     # 虾壳平台API Key
```

## 七、改造点清单（vs 原版MPT）

| # | 改造项 | 说明 | 优先级 |
|---|--------|------|--------|
| 1 | LLM配置 | `openai_api_key` + `openai_base_url` 指向 shenve10.com | P0 |
| 2 | Azure TTS配置 | `azure_api_key` + `azure_base_url` 填入你提供的Key | P0 |
| 3 | Pexels配置 | `pexels_api_keys` 填入你提供的Key | P0 |
| 4 | 用户认证 | 新增 `xiake_auth.py`，预留接口 | P0 |
| 5 | 计费扣费 | 新增 `xiake_billing.py`，预留接口 | P0 |
| 6 | CORS配置 | 允许虾壳域名跨域访问 | P0 |
| 7 | 前端品牌化 | 替换MPT品牌为"AI Video Workshop" | P1 |
| 8 | 多语言 | 中/英双语界面 | P1 |
| 9 | 视频存储 | 本地→S3/OSS | P2 |
| 10 | AI图片素材 | 接入gpt-image-2 | P2 |

## 八、技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 后端 | FastAPI + Uvicorn | 0.111+ |
| 前端 | Streamlit | 1.38+ |
| LLM | OpenAI兼容协议 (shenve10.com) | gpt-5.4 |
| TTS | Azure Speech Services | southeastasia |
| 字幕 | edge-tts (内置) | — |
| 视频素材 | Pexels API | v1 |
| 视频合成 | MoviePy + FFmpeg | 2.x + 6.x |
| 任务管理 | 内存/Redis | — |
| 配置 | TOML | — |

## 九、风险与注意事项

1. **Azure TTS配额**: Azure Speech有免费额度(500K字符/月)，超出需付费
2. **Pexels限流**: 单Key 200请求/小时，建议后续多Key轮换
3. **视频生成耗时**: 单条视频约2-5分钟（取决于素材下载+合成），需异步处理
4. **FFmpeg依赖**: 视频合成的核心依赖，服务器必须安装
5. **ImageMagick**: 字幕渲染依赖，需配置policy.xml允许操作
6. **shenve10稳定性**: LLM调用依赖第三方代理，需做好重试和降级
7. **存储空间**: 视频文件较大(50-200MB/条)，需定期清理或迁移到对象存储
