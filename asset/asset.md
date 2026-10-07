# asset（技能包资产）

本目录是 linux-dev-expert 的可复用资产：知识叶、检查清单、机读知识树。

## 结构

- [`knowledge/`](knowledge/)：九叶知识正文（判据、坑位、命令范式，非教程）。
- [`checklists/`](checklists/)：九叶交付前检查清单（逐条可勾选）。
- [`knowledge_tree.json`](knowledge_tree.json)：机读知识树（叶 id、主问句、探针、出处）。

## 九叶

| 叶 | 知识 | 清单 |
|---|---|---|
| posix-glibc-syscalls | [↗](knowledge/posix-glibc-syscalls.md) | [↗](checklists/posix-glibc-syscalls.md) |
| process-thread-signal | [↗](knowledge/process-thread-signal.md) | [↗](checklists/process-thread-signal.md) |
| fd-io-epoll-iouring | [↗](knowledge/fd-io-epoll-iouring.md) | [↗](checklists/fd-io-epoll-iouring.md) |
| pthreads-memory-order | [↗](knowledge/pthreads-memory-order.md) | [↗](checklists/pthreads-memory-order.md) |
| elf-abi-dynamic-linking | [↗](knowledge/elf-abi-dynamic-linking.md) | [↗](checklists/elf-abi-dynamic-linking.md) |
| toolchain-build-cross | [↗](knowledge/toolchain-build-cross.md) | [↗](checklists/toolchain-build-cross.md) |
| systemd-dbus-cgroup-security | [↗](knowledge/systemd-dbus-cgroup-security.md) | [↗](checklists/systemd-dbus-cgroup-security.md) |
| distro-packaging | [↗](knowledge/distro-packaging.md) | [↗](checklists/distro-packaging.md) |
| shell-observability-deploy | [↗](knowledge/shell-observability-deploy.md) | [↗](checklists/shell-observability-deploy.md) |

## 规则

- 每叶知识 ≤ 50 行，只写判据与坑位；展开内容指向 [`references/`](../references/references.md)。
- 版本敏感结论必须带版本号；未取证的条目行首标 `[未取证]`。
- 新增叶须过 [`../references/知识树.md`](../references/知识树.md) 的拓扑判据，否则并入现有叶。
