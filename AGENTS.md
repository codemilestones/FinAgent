# FinAgent

本项目是一个金融智能助手，通过 Claude Code 的 skill 机制提供各种金融计算和分析工具。

## 项目目的

FinAgent 旨在为金融从业者和投资者提供便捷的自动化工具，包括但不限于：
- A股预期股息率计算
- 更多金融分析工具（持续扩展中...）

## 项目结构

```
.claude/code/
├── AGENTS.md           # 本文件
├── CLAUDE.md           # 软链接到 AGENTS.md
└── skills/             # Skills 目录
    └── dividend-yield-calculator/    # A股预期股息率计算器
        ├── SKILL.md     # Skill 定义文件
        ├── scripts/     # Python 脚本
        └── references/  # 参考资料
```

## 创建新 Skill

本项目使用 `skill-creator` 来创建新的 skill。创建步骤如下：

### 1. 使用 skill-creator 创建 Skill

在 Claude Code 中调用 skill-creator skill：

```
/skill skill-creator
```

根据提示输入 skill 的名称、描述、功能等信息。skill-creator 会生成一个 `.zip` 格式的 skill 文件包。

### 2. 解压 Skill 到本地仓库

创建完成后，需要将 skill 文件包解压到 `.claude/code/skills/` 目录下：

```bash
# 假设生成的 skill 包为 your-skill.zip
unzip your-skill.zip -d .claude/code/skills/your-skill/
```

### 3. 验证 Skill 结构

确保解压后的 skill 目录包含以下结构：

```
.claude/code/skills/your-skill/
├── SKILL.md     # 必需：Skill 定义文件
├── scripts/     # 可选：Python/其他脚本文件
└── references/  # 可选：参考资料文档
```

### 4. 使用新 Skill

解压完成后，新的 skill 会自动被 Claude Code 识别，可以直接通过 `/skill your-skill` 来调用。

## 现有 Skills

### dividend-yield-calculator

A股预期股息率计算器，用于计算和分析A股股票的预期股息率。

**使用方式：**
```
/skill dividend-yield-calculator
```

## 贡献指南

欢迎贡献新的 skill！请按照上述步骤创建并测试您的 skill，然后提交 Pull Request。
