# planned_tasks（计划任务声明）

本目录声明由 SMS 调度器执行的到期任务。**技能自身不得执行计划任务**，只声明。

## 规则

- 一任务一文件：`pt-linux-dev-expert-<slug>.json`。
- schema 字段名与 SMS 读取端一致，不得改动：
  `id` `skill` `title` `status` `scheduled_at` `session` `payload` `note`。
- `status` 仅取 `pending` / `running` / `done` / `paused` / `failed`。
- 时间一律本地 ISO（`YYYY-MM-DDTHH:MM`），不带时区后缀。
- 写入须原子（先 `.tmp` 再 rename）；删除文件即注销任务。
- 到期由 SMS 调度器读取执行，并把执行会话挂到关联链。

## 当前

无到期任务。模板见 [`template.json`](template.json)。
