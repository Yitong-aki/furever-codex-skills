# Furever Codex Skills

本仓库用于保存 Furever 内部的可复用 Codex Skill。目前包含：

- `furever-weekly-feedback-report`：生成、审核和交接每周用户反馈周报。

仓库为私有仓库。请只向需要执行周报工作的同事或实习生开放访问，不要公开转发。

## 安装

先确保使用者已经获得本仓库的 GitHub 访问权限，然后在 Codex 中发送：

```text
使用 $skill-installer，从 https://github.com/Yitong-aki/furever-codex-skills/tree/main/skills/furever-weekly-feedback-report 安装这个 Skill。
```

安装后重启 Codex，并在一个全新任务中运行回归测试。完整步骤见：

- [实习生交接说明](./Furever用户反馈周报交接说明.md)
- [Skill 验收测试](./skills/furever-weekly-feedback-report/references/acceptance-test.md)
- [权限配置](./skills/furever-weekly-feedback-report/references/access-setup.md)

## 目录

```text
skills/
└── furever-weekly-feedback-report/
    ├── SKILL.md
    ├── agents/
    ├── assets/
    ├── references/
    └── scripts/
```

仓库不保存历史周报、用户反馈原始数据、后台导出、Cookie、密码、访问令牌或个人登录信息。
