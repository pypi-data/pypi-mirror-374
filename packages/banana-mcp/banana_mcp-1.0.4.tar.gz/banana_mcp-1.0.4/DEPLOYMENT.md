# Gemini MCP - Python uvx 方案部署指南

## 🎯 这就是你想要的Python uvx方案！

现在你可以像其他Python MCP包一样，使用简单的配置：

```json
{
  "mcpServers": {
    "gemini": {
      "command": "uvx",
      "args": ["gemini-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## 🚀 快速开始

### 1. 确保uv已安装

```bash
# 检查uv是否已安装
uv --version

# 如果没有安装，运行：
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 测试uvx

```bash
uvx --help
```

### 3. 在Cursor中配置

#### 方法1：通过设置界面
1. 打开Cursor设置 (`Cmd/Ctrl + ,`)
2. 搜索 "MCP" 
3. 添加服务器：
   - 名称: `gemini`
   - 命令: `uvx`
   - 参数: `["gemini-mcp"]`
   - 环境变量: `{"GEMINI_API_KEY": "你的API密钥"}`

#### 方法2：配置文件
将 `cursor-config.json` 的内容添加到你的MCP配置文件中。

### 4. 重启Cursor

配置完成后重启Cursor以加载MCP服务器。

### 5. 开始使用

```
使用generate_image工具生成一张图片：一只穿着太空服的橙色小猫漂浮在星空中
```

## 🔧 本地测试

### 测试包是否工作
```bash
# 直接运行（需要先pip install）
gemini-mcp

# 或使用uvx（推荐）
uvx gemini-mcp
```

### 测试API调用
```bash
# 设置API密钥
export GEMINI_API_KEY="sk-pYZdmlGyl98eYE8MWLIEgQNmCFM6gqkiTd6gMc4UNIJp8nxb"

# 运行服务器
uvx gemini-mcp
```

## 📦 包的优势

### ✅ 对比其他方案

| 特性 | Python uvx 方案 | Node.js 方案 |
|------|----------------|--------------|
| **安装简单度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **配置简洁度** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **依赖管理** | ✅ 自动处理 | ❌ 需要Node.js环境 |
| **更新便捷性** | ✅ uvx自动获取最新版本 | ❌ 需要手动更新 |

### ✅ 主要特点

1. **零安装使用**：`uvx` 自动下载和运行包
2. **环境隔离**：每次运行都在隔离环境中
3. **自动更新**：uvx会获取最新版本
4. **跨平台**：Windows/macOS/Linux都支持
5. **标准化**：遵循Python生态标准

## 🛠️ 高级配置

### 指定版本
```json
{
  "mcpServers": {
    "gemini": {
      "command": "uvx",
      "args": ["gemini-mcp==1.0.0"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 使用不同API密钥
```json
{
  "mcpServers": {
    "gemini-work": {
      "command": "uvx", 
      "args": ["gemini-mcp"],
      "env": {
        "GEMINI_API_KEY": "work-api-key"
      }
    },
    "gemini-personal": {
      "command": "uvx",
      "args": ["gemini-mcp"], 
      "env": {
        "GEMINI_API_KEY": "personal-api-key"
      }
    }
  }
}
```

## 🔍 故障排除

### 1. uvx命令未找到
```bash
# 重新安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # 或 ~/.zshrc
```

### 2. 包下载失败
```bash
# 清除uvx缓存
uvx --help  # 查看缓存位置
rm -rf ~/.local/share/uv/  # 清除缓存
```

### 3. API调用失败
- 检查API密钥是否正确
- 确认网络连接正常
- 查看Cursor/Claude的日志信息

### 4. MCP服务器连接失败
- 重启AI工具（Cursor/Claude）
- 检查配置文件格式是否正确
- 确认uvx可以正常运行

## 📋 完整的配置示例

### Claude Desktop 配置
文件位置：
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gemini-image-generator": {
      "command": "uvx",
      "args": ["gemini-mcp"],
      "env": {
        "GEMINI_API_KEY": "sk-pYZdmlGyl98eYE8MWLIEgQNmCFM6gqkiTd6gMc4UNIJp8nxb"
      }
    }
  }
}
```

### Cursor 配置
在Cursor的MCP设置中添加上述配置。

## 🎉 成功！

现在你拥有了一个标准的Python uvx方案，就像别人的那样简单易用！

使用方法：
```
请用图片生成工具创建一个未来科技风格的办公室设计图
```

AI会自动调用你的MCP服务器生成图片！