# 🚀 Codex AI Suite

一站式 AI 模型反向代理 + 自动账号池管理平台。

本项目整合了 **CLI Proxy API** 反向代理网关、**Web 管理面板** 和 **自动账号注册工具**，实现了从账号生成、凭据管理到 OpenAI 兼容 API 对外服务的全链路自动化。

---

## 📦 项目结构

```
Codex/
├── cli-proxy-api.exe                    # 反代网关主程序（需自行下载）
├── config.example.yaml                  # 网关配置模板
├── config.yaml                          # 网关实际配置（.gitignore 已排除）
├── management.html                      # 内置管理面板（需自行下载）
├── clean_expired_auth_files.py          # 清理过期认证文件工具
│
├── Cli-Proxy-API-Management-Center-1.7.7/   # 前端 Web 管理面板源码
│   ├── src/                             # React + TypeScript 源代码
│   └── package.json
│
├── codex_auto_register/                 # 自动账号注册工具
│   ├── chatgpt_register.py              # DuckMail 注册脚本
│   ├── codex/
│   │   ├── protocol_keygen.py           # 核心注册引擎
│   │   ├── config.example.json          # 注册工具配置模板
│   │   └── codex_accounts_tokens/       # Token 凭据输出目录
│   ├── test/                            # 测试脚本目录
│   ├── config.example.json              # 注册工具配置模板
│   └── README.md                        # 注册工具文档
│
├── start_all.bat                        # 一键启动全部服务
├── start_proxy.bat                      # 仅启动反代 + 前端（不含注册）
├── start_register.bat                   # 仅启动自动注册脚本（仅注册）
├── stop_all.bat                         # 一键停止全部服务
└── .gitignore
```

---

## ⚡ 快速开始

### 前置条件

- **Node.js** ≥ 20.19 或 ≥ 22.12
- **Python** ≥ 3.10
- **cli-proxy-api.exe**：从 [CLIProxyAPI Releases](https://github.com/router-for-me/CLIProxyAPI/releases) 下载

### 1. 配置网关

复制配置模板并按需修改：

```bash
cp config.example.yaml config.yaml
```

关键配置项：

```yaml
port: 9544                    # 反代 API 监听端口
remote-management:
  allow-remote: true
  secret-key: "你的管理密码"    # 管理面板登录密钥
auth-dir: "f:/Codex/codex_auto_register/codex/codex_accounts_tokens"
api-keys:
  - "your-api-key"            # 对外分发的调用密钥
```

### 2. 配置注册工具

```bash
cp codex_auto_register/codex/config.example.json codex_auto_register/codex/config.json
```

按需填写 IMAP 邮箱信息、代理地址和上传 API 地址等。

### 3. 安装前端依赖

```bash
cd Cli-Proxy-API-Management-Center-1.7.7
npm install
```

### 4. 安装 Python 依赖

```bash
conda create -n codex python=3.10 -y
conda activate codex
pip install curl_cffi requests
```

---

## 🎮 启动方式

| 脚本 | 用途 |
|------|------|
| `start_all.bat` | 启动全部服务（反代 + 前端 + 注册机） |
| `start_proxy.bat` | **仅启动反代 + 前端**（不注册新号） |
| `start_register.bat` | **仅启动自动注册脚本**（仅注册） |
| `stop_all.bat` | 一键停止全部后台服务 |

```bash
# 全部启动并删除过期认证文件
.\start_all.bat

# 仅使用反代功能（已有账号池时推荐）
.\start_proxy.bat

# 仅启动自动注册脚本（不启动反代和前端）
.\start_register.bat

# 停止所有服务
.\stop_all.bat
```

---

## 🛠️ 工具说明

### 清理过期认证文件

项目提供了 `clean_expired_auth_files.py` 脚本，用于自动清理过期的认证文件：

```bash
python clean_expired_auth_files.py
```

该脚本会：
- 扫描 `config.yaml` 中 `auth-dir` 指定的目录（默认为 `codex_auto_register/codex/codex_accounts_tokens/`）
- 检查每个认证文件的过期时间
- 主动验证 token 是否已被服务端吊销
- 生成失效认证文件记录（expired_auth_files.txt）
- 删除已过期的认证文件
- 同步清理 `accounts.txt`、`registered_accounts.csv`、`ak.txt`、`rk.txt` 中的过期记录

---

## 🔌 API 调用方式

启动服务后，本地会暴露一个 **100% OpenAI 兼容**的 API 端点：

| 配置项 | 值 |
|--------|------|
| Base URL | `http://127.0.0.1:9544/v1` |
| API Key | 在 `config.yaml` 的 `api-keys` 中配置 |
| Model | `gpt-5` 或管理面板中显示的模型别名 |

### cURL 示例

```bash
curl http://127.0.0.1:9544/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{"model": "gpt-5","messages": [{"role": "user", "content": "Hello!"}]}'
```

### Python 示例

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="http://127.0.0.1:9544/v1",
)

response = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

---

## 🖥️ 管理面板

启动服务后访问 `http://127.0.0.1:9533`，功能包括：

- **仪表盘**：连接状态、服务版本、模型概览
- **配置面板**：可视化编辑 / 源文件编辑 config.yaml
- **AI 提供商**：管理 Codex / Gemini / Claude 等多通道
- **认证文件**：查看、上传、删除 OAuth 凭据
- **配额管理**：监控各通道使用配额
- **使用统计**：按小时/天图表、Token 用量拆分

---

## 🔐 安全提示

- `config.yaml`、`config.json` 等配置文件包含密钥和凭据，**已被 .gitignore 排除**
- 请勿将 IMAP 授权码、管理密钥等敏感信息提交到公开仓库
- 建议在非公网环境下使用，如需公网暴露请配置 TLS 和访问控制

---

## 📄 License

MIT
