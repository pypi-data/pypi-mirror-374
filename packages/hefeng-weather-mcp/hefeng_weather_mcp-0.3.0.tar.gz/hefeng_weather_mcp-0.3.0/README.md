# 和风天气 MCP 服务

一个基于 Model Context Protocol (MCP) 的和风天气服务，提供天气预报、气象预警、太阳辐射等多种气象数据查询功能。

![天气](image-天气.png)
![生活指数](image-生活指数.png)
![空气质量](image-空气质量.png)
![历史空气质量](image-历史空气质量.png)
![当前天气](image-当前天气.png)
![广州未来三天天气](image-广州未来三天天气.png)
![未来广州12小时内的天气](image-未来广州12小时内的天气.png)

## 功能特性

- **天气预报**: 获取未来三天详细天气预报
- **气象预警**: 查询实时气象灾害预警信息
- **生活指数**: 获取各类生活指数预报，如洗车、穿衣、感冒等
- **空气质量**: 获取城市的空气质量指数（AQI）及主要污染物信息
- **逐小时预报**: 获取未来 24/72/168 小时逐小时天气（温度、天气状况、风力/风速/风向、相对湿度、气压、降水概率、露点、云量等）
- **实况天气**: 获取近实时天气（温度、体感温度、风、湿度、气压、降水量、能见度、露点、云量等）
- **安全认证**: 使用 JWT + EdDSA 数字签名认证
- **详细日志**: 完整的操作日志和错误处理

## 安装

```bash
uv tool install hefeng-weather-mcp
```

或使用 pip 安装：

```bash
pip install hefeng-weather-mcp
```

```env
HEFENG_API_HOST=devapi.qweather.com
HEFENG_PROJECT_ID=你的项目ID
HEFENG_KEY_ID=你的凭据ID
HEFENG_PRIVATE_KEY_PATH=./ed25519-private.pem

# 可选：直接加载密钥内容，方便远程部署
HEFENG_PRIVATE_KEY=
```

## 使用

### streamable-http 模式

配置环境变量后运行程序

```bash
hefeng-weather-mcp http
```

vscode MCP 配置文件：

```json
{
  "servers": {
    "hefeng-weather-mcp": {
      "url": "http://127.0.0.1:8000/mcp",
      "type": "http"
    }
  },
  "inputs": []
}
```

### stdio 模式

安装并配置环境变量后运行程序

```bash
hefeng-weather-mcp stdio
```

vscode MCP 配置文件：

```json
{
  "servers": {
    "hefeng-weather-mcp-stdio": {
      "type": "stdio",
      "command": "hefeng-weather-mcp stdio"
    }
  },
  "inputs": []
}
```

或者使用 `uv` 命令：

```json
{
  "servers": {
    "hefeng-weather-mcp-uv": {
      "type": "stdio",
      "command": "uvx hefeng-weather-mcp stdio",
      "envFile": "${workspaceFolder}/.env"
    }
  },
  "inputs": []
}
```

## 前置要求

- Python >= 3.11
- OpenSSL (用于生成密钥对)
- 和风天气开发者账号

## 开发

### 1. 克隆项目

```bash
git clone https://github.com/yeisme/hefeng-weather-mcp.git
cd hefeng-weather-mcp
```

### 2. 安装依赖

使用 pip:

```bash
pip install -e .
```

或使用 uv (推荐):

```bash
uv sync
```

### 3. 创建和风天气项目

1. 访问 [和风天气控制台](https://console.qweather.com/project/)
2. 注册/登录账号
3. 点击"创建项目"，填写项目信息
4. 记录下生成的 **Project ID**

### 4. 生成密钥对

在项目根目录下运行以下命令生成 EdDSA ed25519 密钥对：

```bash
openssl genpkey -algorithm ED25519 -out ed25519-private.pem \
&& openssl pkey -pubout -in ed25519-private.pem > ed25519-public.pem
```

这将生成两个文件：

- `ed25519-private.pem`: 私钥文件（保密，不要提交到代码库）
- `ed25519-public.pem`: 公钥文件

### 5. 创建 API 凭据

1. 在和风天气控制台中，进入你创建的项目
2. 点击"凭据管理" → "创建凭据"
3. 选择凭据类型为 **"数字签名"**
4. 上传刚才生成的 `ed25519-public.pem` 公钥文件
5. 记录下生成的 **Key ID**

### 6. 配置环境变量

复制配置模板文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入实际的配置信息：

```env
# 和风天气API配置
HEFENG_API_HOST=devapi.qweather.com
HEFENG_PROJECT_ID=你的项目ID
HEFENG_KEY_ID=你的凭据ID
HEFENG_PRIVATE_KEY_PATH=./ed25519-private.pem
```

**配置说明：**

- `HEFENG_API_HOST`:
  - 开发环境使用: `devapi.qweather.com`
  - 生产环境使用: `api.qweather.com`
- `HEFENG_PROJECT_ID`: 步骤 3 中获得的项目 ID
- `HEFENG_KEY_ID`: 步骤 5 中获得的凭据 ID
- `HEFENG_PRIVATE_KEY_PATH`: 私钥文件路径，默认为 `./ed25519-private.pem`

### 开发指南

1. **代码风格**: 项目使用 `ruff` 进行代码格式化和检查
2. **类型检查**: 使用 `mypy` 进行静态类型检查
3. **测试**: 建议为新功能添加相应的单元测试
4. **文档**: 确保所有新功能都有详细的 docstring 文档

## 许可证

MIT License

## 贡献指南

我们欢迎任何形式的贡献！

### 提交 Issue

如果你发现了 bug 或有功能建议，请：

1. 查看现有的 Issue，避免重复提交
2. 使用清晰的标题和详细的描述
3. 如果是 bug 报告，请包含重现步骤和环境信息

## 相关链接

- [和风天气官网](https://www.qweather.com/)
- [和风天气开发者控制台](https://console.qweather.com/project/)
- [和风天气 API 文档](https://dev.qweather.com/docs/api/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: [yefun2004@gmail.com](mailto:yefun2004@gmail.com)
- 🐛 Issues: [GitHub Issues](https://github.com/yeisme/hefeng-weather-mcp/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/yeisme/hefeng-weather-mcp/discussions)

---

**免责声明**: 本项目仅供学习和研究使用，请遵守和风天气的服务条款和 API 使用规范。
