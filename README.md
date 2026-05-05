# Personal Skills
<p align="center">
    <a href="https://linux.do" alt="LINUX DO"><img src="https://shorturl.at/ggSqS" /></a>
</p>

我的个人 agent skill 仓库，自用为主，不对外提供稳定性或兼容性承诺。

同一个 [`plugins/personal-skills/skills/`](./plugins/personal-skills/skills) 目录会以三种形式分发：Codex marketplace、Claude Code marketplace，以及普通的本地 skills 目录。

## 当前 Skill

| Skill | 说明 |
| --- | --- |
| [`paper-survey`](./plugins/personal-skills/skills/paper-survey/SKILL.md) | 中文学术综述报告自动生成：检索 / 下载 / 并行解析 / 双层审查 / 跨 session 恢复 |
| [`hatch-pet-realistic`](./plugins/personal-skills/skills/hatch-pet-realistic/SKILL.md) | Codex 桌面宠物（写实人像）：基于 `$imagegen` + rembg 抠图，产出 1536x1872 / 8x9 的透明 atlas |

## 安装

仓库地址：`https://github.com/ShirlyTaylor73/personal-skills`

### 用 Skills CLI 安装

安装指定 skill：

```bash
npx skills add ShirlyTaylor73/personal-skills --skill paper-survey
npx skills add ShirlyTaylor73/personal-skills --skill hatch-pet-realistic
```

查看可用 skill、使用完整 GitHub URL，或一次安装全部 skill：

```bash
npx skills add https://github.com/ShirlyTaylor73/personal-skills --list
npx skills add https://github.com/ShirlyTaylor73/personal-skills --skill paper-survey
npx skills add https://github.com/ShirlyTaylor73/personal-skills --all
```

`skills` CLI 会扫描仓库并发现 `plugins/personal-skills/skills/` 下的 skill。如果后续 CLI 行为变化，可使用直接 skill 路径作为回退：

```bash
npx skills add https://github.com/ShirlyTaylor73/personal-skills/tree/master/plugins/personal-skills/skills/paper-survey
```

### 在 Claude Code 安装

在 Claude Code 会话里执行 slash 命令：

```text
/plugin marketplace add ShirlyTaylor73/personal-skills
/plugin install personal-skills@personal-skills
```

更新 / 列出 / 启停：

```text
/plugin marketplace update
/plugin
/plugin enable personal-skills
/plugin disable personal-skills
```

### 在 Codex 安装

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

注册后启动 Codex，输入 `/plugins`，选择并安装 / 启用 `personal-skills`。后续维护：

```bash
codex plugin marketplace upgrade personal-skills
codex plugin marketplace remove personal-skills
```

### 在 OpenCode / 本地 Skills 安装

如果工具直接读取 skill 根目录，把插件包内的 skills 目录复制或软链到目标位置：

```bash
REPO_ROOT=/path/to/personal-skills
ln -sfn "$REPO_ROOT/plugins/personal-skills/skills" "$HOME/.codex/skills"
ln -sfn "$REPO_ROOT/plugins/personal-skills/skills" "$HOME/.claude/skills"
ln -sfn "$REPO_ROOT/plugins/personal-skills/skills" "$HOME/.opencode/skills"
```

Windows PowerShell 示例：

```powershell
$repoRoot = "D:\path\to\personal-skills"
New-Item -ItemType Junction -Force -Path "$HOME\.codex\skills" -Target "$repoRoot\plugins\personal-skills\skills"
New-Item -ItemType Junction -Force -Path "$HOME\.claude\skills" -Target "$repoRoot\plugins\personal-skills\skills"
New-Item -ItemType Junction -Force -Path "$HOME\.opencode\skills" -Target "$repoRoot\plugins\personal-skills\skills"
```

## 致谢

感谢 marketplace 框架来源 [tcztzy/skills](https://github.com/tcztzy/skills)，并参考 [ShirlyTaylor73/superpowers-zh](https://github.com/ShirlyTaylor73/superpowers-zh) 的多端插件组织方式。

## 许可证

[MIT](./LICENSE)
