# Personal Skills

我的个人 agent skill 仓库，自用为主，不对外提供稳定性或兼容性承诺。

同一份 [`skills/`](./skills) 目录会以三种形式分发：Codex marketplace、Claude Code marketplace、以及普通的本地 skills 目录。

## 当前 skill

| Skill | 说明 |
| --- | --- |
| [`paper-survey`](./skills/paper-survey/SKILL.md) | 中文学术综述报告自动生成：检索 / 下载 / 并行解析 / 双层审查 / 跨 session 恢复 |

## 安装

仓库地址：`https://github.com/ShirlyTaylor73/personal-skills`

### Claude Code

在 Claude Code 会话里执行 slash 命令：

```text
/plugin marketplace add ShirlyTaylor73/personal-skills
/plugin install paper-survey@personal-skills
```

更新 / 列出 / 启停：

```text
/plugin marketplace update
/plugin
/plugin enable paper-survey
/plugin disable paper-survey
```

### Codex

在终端执行 CLI 命令注册 marketplace：

```bash
codex plugin marketplace add ShirlyTaylor73/personal-skills
```

也支持完整 Git URL / SSH / 本地路径：

```bash
codex plugin marketplace add https://github.com/ShirlyTaylor73/personal-skills.git
codex plugin marketplace add git@github.com:ShirlyTaylor73/personal-skills.git
codex plugin marketplace add /abs/path/to/personal-skills
```

注册后进入 Codex TUI，在 `/plugins` 面板选择并启用想要的插件。后续维护：

```bash
codex plugin marketplace upgrade personal-skills
codex plugin marketplace remove personal-skills
```

### 直接挂载本地 skill 目录

如果工具直接读 skill 根目录，把本仓库的 [`skills/`](./skills) 软链过去即可：

```bash
REPO_ROOT=/path/to/personal-skills
ln -sfn "$REPO_ROOT/skills" "$HOME/.codex/skills"
ln -sfn "$REPO_ROOT/skills" "$HOME/.claude/skills"
```

## 致谢

感谢 marketplace 框架来源 [tcztzy/skills](https://github.com/tcztzy/skills) 


## 许可证

[MIT](./LICENSE)
