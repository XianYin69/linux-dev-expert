# Instructions — linux-dev-expert

使用 `linux-dev-expert` skill 来完成用户请求。

## 适用任务
Linux 上的 C/C++/Rust/Python 系统编程、构建与交叉编译、链接与 ABI、服务化（systemd/dbus）、
容器与 cgroups、安全模块与 capabilities、发行版打包、Shell 脚本健壮化、性能与故障取证、
部署与可观测（journald/logrotate/timer/健康检查）。

## 不适用（须转派）
Windows 桌面（→ windows-app-dev-expert）、Web 前端与界面设计（→ interface-design-expert）、
纯语言语义细节（→ c-expert / cpp-expert / python-expert）、并发架构设计（→ concurrency-design）、
数据库内核（→ database-management）。

## 步骤
1. **探测**：跑 `scripts/probe_os.py`、`probe_pkg.py`、`probe_toolchain.py`、`probe_systemd.py`。
2. **定位知识叶**：按 [知识树](../references/知识树.md) 九叶取 `asset/knowledge/` 与 checklist。
3. **取证**：man / `readelf` / `strace` / `perf` / `journalctl` 输出为准，标注取证时间与主机。
4. **产出**：代码或配置 + 构建命令 + 部署单元 + 验证命令 + 回滚方案。
5. **自检**：`python scripts/check_links.py`、`python scripts/deps_check.py`、行数红线复核。

## 风格
- 命令用 POSIX 或明确标注 bash-only（`[[ ]]`、数组、`pipefail`）。
- 脚本首行 `set -euo pipefail`，并说明与 `sh` 的差异。
- 路径大小写敏感、空格、UTF-8 locale 与 TZ 一律显式处理。
- 权限最小化：先 capability 再 sudo，先用户级再系统级单元。

## 熔断
同一失败重试达 10 次 → `scripts/penalty.py` 记熔断，回退到上一稳定结论并求助用户。
