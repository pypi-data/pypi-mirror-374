# Epic LLM

**摆脱厂商锁定。** 在任何地方、使用任何客户端使用你的个人LLM订阅。

> **语言**: [English](README.md) | 中文

## ⚠️ 重要免责声明

**使用前请仔细阅读**

### 服务条款警告
**使用此工具可能违反LLM提供商的服务条款。** 我们不对任何后果负责，包括但不限于：
- **账户暂停或终止**
- **订阅访问权限丢失**
- **违反提供商条款**
- **任何损害或损失**

### 用户责任
- ✅ **仅限个人使用** - 仅在您个人拥有和付费的订阅上使用
- ❌ **禁止共享** - 不要与多个用户或组织共享API访问权限
- ❌ **禁止商业用途** - 不要用于商业API转售或业务运营
- ⚖️ **风险自负** - 您承担使用此工具的所有法律和财务风险

### 第三方工具法律声明
**重要提示：Epic LLM不包含任何第三方API工具。** 所有提供商工具都由独立的第三方开发者开发（不隶属于Epic LLM、Anthropic、Google、GitHub或其他AI公司）：

- **claude-code-api**: 第三方独立开发者工具（需要单独下载）
- **copilot-api**: 第三方独立开发者工具（需要单独下载）  
- **geminicli2api**: 第三方独立开发者工具（需要单独下载）

**Epic LLM仅提供编排和管理功能** - 它不打包、分发或提供任何第三方工具。用户完全负责：
- 自行决定下载第三方工具
- 遵守每个工具的许可证和AI提供商的服务条款
- 使用非官方第三方API工具的任何法律后果

**这种分离保护用户和Epic LLM免受AI服务提供商的潜在法律问题。**

### 提供商特定风险
- **Claude**: 可能检测到自动化使用模式
- **GitHub Copilot**: 仅适用于开发环境
- **Gemini**: OAuth使用跟踪可能标记异常访问模式

**使用风险自负。我们不提供任何保证，不承担任何责任。**

---

## Epic LLM是什么？

Epic LLM是一个**订阅聚合服务**，帮助您管理第三方工具，将您的个人LLM订阅（Claude Pro、GitHub Copilot、Gemini Advanced）转换为统一的OpenAI兼容API。与需要API密钥的传统网关（如LiteLLM）不同，这个编排工具通过**自动化第三方仓库管理**帮助您利用现有的消费者订阅。

### 问题所在

- **厂商锁定**: 每个LLM提供商都强迫您只使用他们的官方客户端
- **访问受限**: 您的Claude Pro订阅只能在Claude的网页界面中使用
- **工作流分散**: 需要在不同应用间切换使用不同模型
- **订阅浪费**: 付费购买多个订阅但无法在您偏好的工具中使用
- **复杂的手动设置**: 每个提供商都需要找到和克隆不同的第三方API仓库，学习各种认证方法，管理独立工具
- **依赖地狱**: 安装Node.js包、Python工具、CLI实用程序，以及在不同提供商仓库间保持更新

### 解决方案

Epic LLM **自动下载和管理由独立开发者创建的第三方仓库**，帮助将您现有的订阅聚合为标准OpenAI兼容API：

**🤖 自动仓库克隆**: 一条命令找到并克隆所有第三方提供商仓库 - 无需手动搜索仓库  
**🔧 统一管理**: 单一界面启动/停止/监控所有第三方工具，而不是管理多个仓库  
**⚡ 零配置**: 智能依赖检测和自动安装所需工具（Node.js、npm包、CLI工具）  
**🎯 一站式设置**: `epic-llm install` 处理一切 - 克隆第三方仓库、安装依赖、设置认证

```bash
# 您的Claude Pro订阅 → 随处可用
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# 您的GitHub Copilot → 随处可用  
curl http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Write a function"}]
  }'
```

### 为什么这很重要

**🚀 跳过设置噩梦**: 无需再搜索GitHub仓库、阅读安装文档或调试依赖冲突  
**🔓 解锁您的订阅**: 在VSCode、Cursor或任何OpenAI兼容工具中使用Claude Pro  
**💰 价值最大化**: 从您已付费的订阅中获得全部效用  
**🔧 通用访问**: 一种API格式适用于数百种现有工具  
**🔒 私密安全**: 您的凭据保留在您的机器上，可选网关身份验证
**⚡ 团队友好**: 通过API密钥保护安全地共享订阅访问
**⏱️ 节省时间**: 以前需要数小时的手动设置现在只需几分钟自动安装

## 工作原理

1. **检查依赖**: `epic-llm check` 扫描您的系统并显示需要什么
2. **自动克隆仓库**: `epic-llm install` 自动找到并克隆第三方提供商仓库  
3. **一次认证**: 使用官方提供商方法（Claude CLI、GitHub CLI、Google OAuth）- Epic LLM指导您完成每个步骤
4. **启动即忘**: `epic-llm start` 启动所有提供商工具，自动管理端口和健康监控
5. **随处使用**: 您的订阅现在可作为标准OpenAI API在任何兼容工具中使用

*注意：Epic LLM管理使用官方提供商认证方法的外部GitHub仓库。原始服务的速率限制仍然适用。*

```mermaid
graph LR
    A[您的工具] --> B[Epic LLM]
    B --> C[Claude Pro]
    B --> D[GitHub Copilot] 
    B --> E[Gemini Advanced]
    
    A --> F[VSCode/Cursor]
    A --> G[自定义脚本]
    A --> H[AI工具]
```

## 支持的提供商

| 提供商 | 需要订阅 | 端口 | 认证 |
|----------|----------------------|------|----------------|
| **Claude** | Claude Pro/Team | 8000 | Claude CLI (`claude auth login`) |
| **Copilot** | GitHub Copilot | 8081 | GitHub CLI (`gh auth login`) |
| **Gemini** | Gemini Advanced | 8888 | Google OAuth (网页流程) |

## 快速开始

### 1. 运行Epic LLM（无需安装！）

```bash
# 使用uvx直接运行Epic LLM - 无需安装！
uvx epic-llm --help

# 检查每个提供商需要什么
uvx epic-llm check

# 自动安装第三方提供商工具
uvx epic-llm check --install
```

### 2. 备选方案：安装Epic LLM

如果您更喜欢安装Epic LLM：

```bash
# 使用uv安装（推荐）
uv tool install epic-llm

# 或使用pip安装
pip install epic-llm

# 然后正常使用
epic-llm --help
```

### 3. 自动化设置（一条命令！）

```bash
# 检查需要什么并自动安装一切
uvx epic-llm check --install

# 这会自动克隆和设置第三方工具：
# ✅ claude-code-api 仓库（第三方Claude工具）
# ✅ copilot-api 仓库（第三方GitHub Copilot工具） 
# ✅ geminicli2api 仓库（第三方Gemini工具）
# ✅ 所有Node.js依赖
# ✅ 所需的Python包和CLI工具
```

### 4. 认证（Epic LLM指导您）

```bash
# Epic LLM会提示您完成每个步骤
uvx epic-llm auth-status  # 显示需要什么认证

# Claude: 一条命令登录
claude auth login

# Copilot: GitHub认证  
gh auth login

# Gemini: 首次启动时OAuth流程自动打开
```

### 5. 启动一切

```bash
# 一条命令启动所有提供商仓库，自动管理端口
uvx epic-llm start

# Epic LLM处理：
# ✅ 启动下载的仓库工具
# ✅ 端口分配（避免冲突）
# ✅ 进程监控
# ✅ 健康检查
# ✅ 失败时重启

# 或启动特定提供商
uvx epic-llm start claude copilot

# 随时检查状态
uvx epic-llm status
```

### 6. 随处使用（您的订阅现在是API了）

```python
# 在您的Python代码中
import openai

# 使用Claude Pro订阅
client = openai.OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
response = client.chat.completions.create(
    model="claude-3-5-sonnet",
    messages=[{"role": "user", "content": "你好Claude！"}]
)

# 使用GitHub Copilot订阅  
client = openai.OpenAI(base_url="http://localhost:8081/v1", api_key="dummy")
response = client.chat.completions.create(
    model="gpt-4", 
    messages=[{"role": "user", "content": "写一个函数"}]
)
```

## 管理命令

```bash
# 列出可用提供商
uvx epic-llm list

# 安装提供商依赖项
uvx epic-llm install

# 启动/停止服务
uvx epic-llm start [provider...]
uvx epic-llm stop [provider...]

# 检查状态和健康状况
uvx epic-llm status
uvx epic-llm auth-status

# 验证依赖项
uvx epic-llm check [provider]

# 网关安全（保护您的提供商端点）
uvx epic-llm set-gateway-key claude --key "your-secure-key"    # 启用身份验证
uvx epic-llm set-gateway-key claude                            # 禁用身份验证  
uvx epic-llm show-gateway-key claude                          # 显示当前状态
```

## 🔒 网关安全

使用API密钥身份验证保护您的提供商端点以控制访问：

### 用例：物联网开发团队
**场景**：您的物联网开发团队需要访问Gemini模型来进行设备自动化和边缘AI，但不想购买单独的API密钥，希望重用团队成员已有的Google账户Gemini订阅。

**解决方案**：使用Epic LLM与网关身份验证：

```bash
# 使用您现有的Google账户设置Gemini
uvx epic-llm install gemini
uvx epic-llm start gemini

# 为团队访问提供网关安全
uvx epic-llm set-gateway-key gemini --key "iot-team-secure-key-2024"

# 团队成员通过OpenAI兼容端点访问
curl -H "Authorization: Bearer iot-team-secure-key-2024" \
     -H "Content-Type: application/json" \
     -d '{"model": "gemini-2.5-flash", "messages": [{"role": "user", "content": "生成物联网传感器校准代码"}]}' \
     http://your-server:8888/v1/chat/completions
```

**优势**：
- ✅ 重用现有Google订阅而不是购买API密钥
- ✅ 使用共享网关身份验证的安全团队访问
- ✅ OpenAI兼容API适用于现有代码库  
- ✅ 开发团队的经济高效解决方案
- ✅ 控制对基于订阅端点的访问

# 安装提供商依赖
uvx epic-llm install

# 启动/停止服务
uvx epic-llm start [provider...]
uvx epic-llm stop [provider...]

# 检查状态和健康
uvx epic-llm status
uvx epic-llm auth-status

# 验证依赖
uvx epic-llm check [provider]
```

## 目录结构

```
~/.local/share/epic-llm/
├── state.json                     # 服务状态和配置
└── pkg/                          # 下载的提供商仓库
    ├── claude-code-api/          # Git仓库：https://github.com/codingworkflow/claude-code-api.git
    ├── copilot-api/              # Git仓库：https://github.com/ericc-ch/copilot-api.git  
    └── geminicli2api/            # Git仓库：https://github.com/gzzhongqi/geminicli2api.git
        └── oauth_creds.json      # Gemini OAuth凭证
```

外部认证（由官方CLI管理）：
- **Claude**: `~/.claude/.credentials.json`
- **Copilot**: `~/.config/gh/hosts.yml` 
- **Gemini**: pkg目录中的OAuth令牌

## 端口配置

- **Claude**: `localhost:8000`（可配置）
- **Copilot**: `localhost:8081`（可配置）  
- **Gemini**: `localhost:8888`（可配置）
- **⚠️ 端口8080**: 为Gemini OAuth回调保留（硬编码，无法更改）

覆盖默认端口：
```bash
uvx epic-llm start --port claude:8001 --port gemini:8889
```

## 与其他解决方案比较

| 功能 | Epic LLM | 手动设置 | LiteLLM | 官方API |
|---------|----------|--------------|---------|---------------|
| **使用现有订阅** | ✅ | ✅ | ❌ | ❌ |
| **无额外API费用** | ✅ | ✅ | ❌ | ❌ |
| **自动化安装** | ✅ | ❌ | ❌ | ❌ |
| **统一管理界面** | ✅ | ❌ | ✅ | ❌ |
| **依赖自动检测** | ✅ | ❌ | ❌ | ❌ |
| **一键设置** | ✅ | ❌ | ❌ | ❌ |
| **自动端口管理** | ✅ | ❌ | ❌ | ❌ |
| **健康监控** | ✅ | ❌ | ❌ | ❌ |
| **设置时间** | 5分钟 | 2-4小时 | 30分钟 | N/A |
| **统一OpenAI格式** | ✅ | ❌ | ✅ | ❌ |
| **自托管** | ✅ | ✅ | ✅ | ❌ |

### 手动设置现实检查

**没有Epic LLM，您需要：**
- 找到并克隆3+个不同的GitHub仓库：
  - 用于Claude Pro的`claude-code-api`
  - 用于GitHub Copilot的`copilot-api`  
  - 用于Gemini Advanced的`geminicli2api`
- 安装Node.js、npm、Python工具和各种CLI实用程序
- 阅读多个README文件和安装指南
- 调试版本冲突和依赖问题
- 手动为每个提供商仓库配置认证
- 设置端口管理以避免工具间冲突
- 创建自己的监控和重启脚本
- 随着提供商仓库变化保持一切更新

**使用Epic LLM：**
```bash
# 就这样。Epic LLM自动处理仓库管理。
epic-llm install  # 克隆所有仓库并安装依赖
epic-llm start    # 启动所有提供商工具并管理
```

## 使用案例

- **开发者**: 在VSCode、Cursor或自定义工具中使用Claude Pro
- **研究人员**: 通过单一界面访问多个模型
- **团队**: 在不同应用程序间共享订阅访问
- **自动化**: 使用您已经付费的高级模型构建脚本
- **隐私**: 保持一切本地 - 无外部API调用或密钥共享

## 贡献

我们欢迎贡献！Epic LLM设计为可扩展的，支持新的提供商。

### 快速开始
```bash
# 设置开发环境
git clone https://github.com/your-username/epic-llm.git
cd epic-llm
uv sync --dev

# 测试您的更改
./scripts/quick-test.sh

# 检查代码质量
uv run ruff check .
```

### 常见贡献
- 🚀 **添加新提供商**: 支持OpenAI API、Anthropic API、本地模型
- 🐛 **修复Bug**: 查看 [GitHub Issues](https://github.com/epic-llm/epic-llm/issues)  
- 📚 **改进文档**: 用户指南、示例、翻译
- 🧪 **添加测试**: 提高覆盖率和可靠性

### 详细指南
查看 **[CONTRIBUTING.md](CONTRIBUTING.md)** 了解：
- 添加新LLM提供商（分步指南）
- Bug修复工作流程
- 代码风格指南
- 测试要求
- 安全考虑

### 获取帮助
- 📖 首先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)
- 🐛 查看 [GitHub Issues](https://github.com/epic-llm/epic-llm/issues) 
- 💬 开始 [GitHub Discussion](https://github.com/epic-llm/epic-llm/discussions)
- 🧪 查看现有提供商实现作为示例

## 法律与道德

**⚠️ 警告：使用风险自负。可能被封号。**

此工具可能违反LLM提供商服务条款。用户承担以下全部责任：

### 禁止用途
- ❌ **多用户共享** - 不要与他人共享API访问权限
- ❌ **商业转售** - 不要转售或monetize API访问权限
- ❌ **违反条款** - 尊重每个提供商的使用政策
- ❌ **滥用速率限制** - 不要超出合理使用模式

### 推荐做法
- ✅ **仅限个人使用** - 仅在您自己的订阅上使用
- ✅ **适度使用** - 不要滥用或超出正常使用模式
- ✅ **监控ToS变化** - 提供商条款可能变化并影响此工具

### 责任免责声明
**软件按"原样"提供，不提供任何形式的保证。我们不对以下情况负责：**
- 账户暂停、封禁或终止
- 订阅访问或服务丢失  
- 违反第三方服务条款
- 任何直接、间接、偶然或后果性损害

**您承认使用此软件可能导致账户限制，您承担所有风险。**

## 许可证

MIT许可证 - 详见[LICENSE](LICENSE)。

---

**💡 提示**: 如果这个仓库帮助您从LLM订阅中获得更多价值，请给它一个星标！与朋友分享此信息，让他们摆脱供应商锁定。