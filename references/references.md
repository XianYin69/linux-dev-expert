# references（知识库索引）

本目录存 linux-dev-expert 的权威出处清单与知识树索引。**只记出处与用途，不抄正文**。

## 目录

| 分类 | 文件 | 用途 |
|---|---|---|
| 标准与手册 | [`标准与手册.md`](标准与手册.md) | POSIX / man-pages / glibc / kernel.org |
| 系统与服务 | [`系统与服务.md`](系统与服务.md) | systemd / dbus / cgroups / 安全模块 |
| 工具链与打包 | [`工具链与打包.md`](工具链与打包.md) | GCC/Clang/CMake/meson / deb-rpm-APK |
| 排障与性能 | [`排障与性能.md`](排障与性能.md) | strace/perf/eBPF/valgrind |
| 书目 | [`书目.md`](书目.md) | 系统编程与性能经典书 |
| 知识树 | [`知识树.md`](知识树.md) | 九叶索引与拓扑判据 |

## 取证规则

- 每条出处须给原始 URL 与访问日期；未确证的条目标 `[本地]` 且不得编 URL。
- 结论引用出处时须写「条文/页码 + 实测命令」，只引出处不引实测的一律标 advisory。
- 版本敏感内容（glibc 行为、systemd 单元字段、内核 syscall 语义）须带版本号。

## 关联

- 机读知识树：[`../asset/knowledge_tree.json`](../asset/knowledge_tree.json)
- 知识正文：[`../asset/asset.md`](../asset/asset.md)
- 依赖：[`../dependence/dependence.md`](../dependence/dependence.md)
