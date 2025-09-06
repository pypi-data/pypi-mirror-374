[Read this in English](./doc/README-EN.md)

# Nekro Agent Toolkit

Nekro Agent Toolkit 是一个用于快速部署 Nekro Agent 及其相关服务的专业安装工具。它简化了基于 Docker 的 QQ 机器人服务部署流程，提供完整的安装、更新、备份和恢复解决方案。

## ✨ 核心特性

### 🚀 统一管理
- **一体化工具**：通过单一 `app.py` 脚本处理所有操作
- **智能环境检测**：自动识别源码运行和包安装环境
- **动态命令提示**：根据运行环境显示正确的命令格式
- **版本信息显示**：源码运行显示 Git SHA，包安装显示版本号

### 🌍 多语言支持
- **自动语言检测**：根据系统环境自动切换中英文界面
- **完整国际化**：所有用户消息支持多语言显示
- **手动切换**：可通过环境变量强制指定语言

### 🐳 Docker 卷智能管理
- **动态发现**：自动发现所有符合条件的 Docker 卷进行备份
- **后缀匹配**：严格后缀匹配，如 `my_app-nekro_postgres_data`
- **跨平台备份**：Linux 直接访问，macOS/Windows 容器化备份

### 🛡️ 智能备份系统
- **精确过滤**：自动排除日志、上传文件、临时文件等
- **压缩优化**：优先使用 zstd 压缩，显著减小备份体积
- **跨平台兼容**：同一备份文件可在不同系统间恢复

## 💻 系统要求

- **操作系统**：Linux / macOS / Windows（通过 Docker Desktop）
- **Python 版本**：Python 3.6+ （兼容性考虑）
- **必需软件**：
  - Docker（必需）
  - Docker Compose v1 或 v2（必需）
- **可选软件**：
  - `zstd` 压缩工具（推荐，用于创建更小的备份文件）
  - `ufw` 防火墙工具（Linux 上可选）
- **权限要求**：管理员权限（sudo）

## 🚀 安装方式

### 方法一：使用 pip 安装（推荐）

```bash
# 安装最新版本
pip install nekro-agent-toolkit

# 升级到最新版本
pip install --upgrade nekro-agent-toolkit
```

安装完成后，即可直接使用 `nekro-agent-toolkit` 命令：

```bash
# 在当前目录下创建一个名为 na_data 的文件夹，并安装服务
nekro-agent-toolkit --install ./na_data

# 查看版本信息
nekro-agent-toolkit --version

# 查看帮助信息
nekro-agent-toolkit --help
```

### 方法二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/your-repo/nekro-agent-toolkit.git
cd nekro-agent-toolkit

# 安装依赖（可选）
pip install -r requirements.txt

# 运行安装
python3 app.py --install ./na_data

# 查看版本信息（显示 Git SHA）
python3 app.py --version
```

## 📚 使用指南

### 🌍 多语言界面

项目支持中英文界面自动切换，根据系统语言环境自动识别：

```bash
# 中文环境
LANG=zh_CN.UTF-8 nekro-agent-toolkit --help

# 英文环境
LANG=en_US.UTF-8 nekro-agent-toolkit --help

# 自动检测（默认）
nekro-agent-toolkit --help
```

### 📎 版本信息显示

项目支持智能版本信息显示：

```bash
# 源码运行时显示 Git SHA
python3 app.py --version
# 输出示例: nekro-agent-toolkit (源码) a1b2c3d4

# 包安装运行时显示版本号
nekro-agent-toolkit --version
# 输出示例: nekro-agent-toolkit 1.2.4

# 如果有未提交的修改，会显示 (dirty)
# 输出示例: nekro-agent-toolkit (源码) a1b2c3d4 (dirty)
```

### 🚀 基本安装

#### 标准安装

```bash
# 基本安装（仅 Nekro Agent 主服务）
nekro-agent-toolkit --install ./na_data

# 含 NapCat QQ 机器人服务的安装
nekro-agent-toolkit --install ./na_data --with-napcat

# 预演模式（仅生成配置，不执行实际安装）
nekro-agent-toolkit --install ./na_data --dry-run

# 自动确认模式（无需交互确认）
nekro-agent-toolkit --install ./na_data --yes
```

#### 组合选项

```bash
# 完整安装：包含 NapCat + 自动确认
nekro-agent-toolkit --install ./na_data --with-napcat --yes

# 安全预演：在正式安装前预览操作
nekro-agent-toolkit --install ./na_data --with-napcat --dry-run
```

### 🔄 服务更新

#### 部分更新（推荐）

仅更新 Nekro Agent 核心服务和沙箱镜像，保留数据库等组件：

```bash
# 标准部分更新
nekro-agent-toolkit --update ./na_data

# 源码运行
python3 app.py --update ./na_data
```

#### 完全更新（升级）

更新所有 Docker 镜像（包括数据库等）并重启容器：

```bash
# 完全升级（谨慎使用）
nekro-agent-toolkit --upgrade ./na_data

# 源码运行
python3 app.py --upgrade ./na_data
```

**注意**：完全更新可能影响数据库等组件，建议在操作前先进行备份。

### 💾 备份与恢复

本工具提供先进的跨平台备份与恢复功能，支持 Linux、macOS 和 Windows 系统。

### 💾 备份操作

```bash
nekro-agent-toolkit --backup ./na_data ./backups
```

备份特性：
- 自动生成带时间戳的备份文件
- 动态发现符合条件的 Docker 卷
- 智能文件过滤，优先使用 zstd 压缩

### 🔄 恢复操作

```bash
nekro-agent-toolkit --recovery ./backups/na_backup_1678886400.tar.zstd ./na_data_new
```

恢复特性：
- 支持 `.tar` 和 `.tar.zstd` 格式
- 自动创建缺失的 Docker 卷
- 跨平台兼容

### 🚀 恢复并安装

```bash
nekro-agent-toolkit --recover-install ./backups/na_backup_1678886400.tar.zstd ./na_data_new
```

一步完成恢复和安装，适用于新环境部署。

## 📋 项目信息

### 贡献指南

欢迎提交 Issue 和 Pull Request！请参考 [`doc/REGULATE.md`](./doc/REGULATE.md) 了解详细的开发规范。

### 许可证

请参考 [Nekro Agent 项目](https://github.com/KroMiose/nekro-agent)和[本项目](./LICENSE) 获取许可证信息。