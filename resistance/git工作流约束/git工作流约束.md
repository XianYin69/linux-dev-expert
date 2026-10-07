# git 工作流约束

本技能采用功能分支策略；**本仓为本地仓，无远端，不执行 push**。

## 规则

1. **自动 init**：操作前检查 `.git/`，不存在即 `git init`，不得跳过。
2. **功能分支提交**：每个流程步骤完成后提交到 `feature/<topic>`（`feature/init`、
   `feature/flow`、`feature/knowledge`、`feature/scripts`、`feature/resistance`、
   `feature/deps`、`feature/agent`）。功能分支名不得为 `main` 或 `dev`。
3. **禁止直写 main/dev**：所有变更经功能分支进入 `dev`；`main`、`dev` 不接受直接 commit。
4. **审核通过合 dev**：双链辩论（`scripts/logic_chain.py debate`）+ 悬空链接为 0 +
   `deps_check` 通过后，`git merge --no-ff feature/<topic>` 入 `dev`。
5. **整体审查通过入 main**：审查约束九项全过后 `dev` 合入 `main`（`--no-ff`），保留合并记录。
6. **基线提交**：`main` 上首个提交为骨架（LICENSE、.gitignore、SKILL.md、planned_tasks/）。
7. **忽略清单**：`.gitignore` 必含 `tmp/`、`__pycache__/`、`*.pyc`、IDE 目录、`private/`；
   暂存前核对 `git status`，发现临时产物被跟踪先补 ignore。
8. **不推远端**：本技能交付为本地仓（用户明示「本地 dev/main，不推远端」）。
   若日后要加远端，须先按第 9 条判定可见性并征得用户确认，未确认不得 `git push`。
9. **可见性判定**：涉用户隐私、内部路径、第三方授权内容时仓库必须 PRIVATE；
   判定不了即询问用户，不得擅自设 PUBLIC。
10. **附属技能双仓**：附属/私有子技能（前缀如 `software_use_only-*`）进宿主目录下
    `private/` 的独立私有仓（自带 `.git` + remote，可见性 PRIVATE），本体仓保持 PUBLIC
    且 ignore `private/` 仅留 `.gitkeep`；禁止不入库或误推公开仓（`E_LEAK_TO_PUBLIC`）。
11. **熔断**：审查失败重试达 10 次触发 `scripts/penalty.py`，回退当前功能分支或求助用户。

## 违反后果

- 直写 main/dev 使步骤不可回滚；漏 ignore 污染历史；误推公开仓造成不可撤回的泄漏。
