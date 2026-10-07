# scripts（脚本库）

全部英文文件名、可执行、相对技能根真实存在。探针用于取证，机制用于流程与红线自检。

## 探针（12 个 · Linux 侧运行才有真实结论）

| 脚本 | 取什么证 |
|---|---|
| [`probe_os.py`](probe_os.py) | 发行版族、内核、架构、WSL/容器判定、PID1 |
| [`probe_pkg.py`](probe_pkg.py) | 包管理器可用性、架构、包查询与非交互安装模板 |
| [`probe_toolchain.py`](probe_toolchain.py) | 编译器/构建器/pkg-config 版本、glibc、sanitizer 接受度 |
| [`probe_systemd.py`](probe_systemd.py) | systemd 是否 PID1、单元状态、`systemd-analyze verify` |
| [`probe_ports.py`](probe_ports.py) | 监听端口与归属进程（socket 激活/防火墙前置） |
| [`probe_handles.py`](probe_handles.py) | fd 用量、RLIMIT_NOFILE、线程与 RSS（泄漏信号） |
| [`probe_caps.py`](probe_caps.py) | capability 集、uid/euid、SELinux/AppArmor 状态 |
| [`probe_tracing.py`](probe_tracing.py) | strace/perf/eBPF/bpftrace/valgrind 与 BTF、内核追踪开关 |
| [`probe_fs.py`](probe_fs.py) | 文件系统类型、大小写敏感性、符号链接、inotify 上限、umask |
| [`probe_elf.py`](probe_elf.py) | 解释器、SONAME、RPATH/RUNPATH、NEEDED、最高 glibc 需求 |
| [`probe_locale.py`](probe_locale.py) | locale/编码、时区、DST、UTC 偏移 |
| [`probe_cgroup.py`](probe_cgroup.py) | cgroups v1/v2、控制器委派、memory/cpu/pids 限额 |

## 机制（12 个）

[`check_links.py`](check_links.py) 悬空链接 · [`deps_check.py`](deps_check.py) 依赖清单校验 ·
[`knowledge_index.py`](knowledge_index.py) 九叶检索 · [`advice_compose.py`](advice_compose.py) 答复骨架 ·
[`run_tests.py`](run_tests.py) 编译+冒烟+行数红线 · [`logic_chain.py`](logic_chain.py) 逻辑链与双链辩论 ·
[`process_chain.py`](process_chain.py) 过程链与中断恢复 · [`penalty.py`](penalty.py) 惩罚熔断 ·
[`garbage_collect.py`](garbage_collect.py) 垃圾回收审计 · [`context_compress.py`](context_compress.py) 上下文压缩 ·
[`sandbox.py`](sandbox.py) 沙盒兜底 · [`self_update.py`](self_update.py) 唯一写盘通道

## 用法

- 探针统一 `--json`；非 Linux 宿主上会返回 `applicable=false` 并提示到目标机运行。
- 机制脚本默认 `--dry-run` 语义（`self_update.py release` 必须 `--yes` 才写盘）。
- 缓存与链文件一律落用户缓存目录（`_common.cache_dir()`），不得写入技能目录。
- 校验顺序：`run_tests.py` → `check_links.py` → `deps_check.py` → `garbage_collect.py audit`。
