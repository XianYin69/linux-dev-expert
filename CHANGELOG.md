# CHANGELOG
本文件遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与语义化版本。

## 0.1.0 - 2026-10-07
### Added
- **初始化**：MIT `LICENSE`、`.gitignore`（ignore `tmp/`、IDE、`private/`）、
  `planned_tasks/`（README + template.json，声明交 SMS 调度器，技能自身不执行）。
- **流程复刻**：`branch/流程/` 创建路径 10 节点 + 修改路径 3 节点，
  与同仓 cpp-expert / interface-design-expert / qt-qtquick-expert 模板同构。
- **知识树**：九叶（posix-glibc-syscalls · process-thread-signal · fd-io-epoll-iouring ·
  pthreads-memory-order · elf-abi-dynamic-linking · toolchain-build-cross ·
  systemd-dbus-cgroup-security · distro-packaging · shell-observability-deploy），
  每叶 `asset/knowledge/` + `asset/checklists/` 双件，机读 `asset/knowledge_tree.json`。
- **脚本**：`scripts/` 12 个 Linux 探针（os/pkg/toolchain/systemd/ports/handles/caps/
  tracing/fs/elf/locale/cgroup）+ 12 个机制脚本（check_links/deps_check/knowledge_index/
  advice_compose/run_tests/logic_chain/process_chain/penalty/garbage_collect/
  context_compress/sandbox/self_update），缓存一律落用户缓存目录。
- **约束**：`resistance/` 探测优先、破坏性命令禁令、root 逐项说明、WSL 与真机差异、
  薄技能依赖、git 工作流、审查约束、五大机制与沙盒兜底。
- **依赖声明**：`dependence/deps.json` 只引用不内嵌（c-expert、cpp-expert、python-expert、
  concurrency-design、database-management、interface-design-expert、code-guidelines、git、
  bash、GCC、CMake），每条附 `source_url`。
- **提示词**：`agent/` 四格式（CLAUDE.md / agent_prompt.md / instructions.md / .cursorrules）。
- **git**：本地仓 `feature/*` → `dev` → `main`，无远端、不推送。
