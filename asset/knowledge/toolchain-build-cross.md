# toolchain-build-cross

主问句：在哪个编译器/构建器版本上可复现，交叉 sysroot 与依赖发现是否闭合？

## 判据

- 编译器选型看三件事：诊断质量（Clang 模板报错友好）、目标平台支持（GCC 对老架构/嵌入式更全）、
  ABI 一致性（libstdc++ vs libc++ 不可混链）。同一 CI 里固定 `--version` 输出并入库。
- 警告基线：`-Wall -Wextra -Werror` 起步，加 `-Wshadow -Wconversion -Wpointer-arith
  -Wformat=2 -Wimplicit-fallthrough`；UB 相关 `-fno-strict-aliasing` 是退让，优先改代码。
  `-O2` 才暴露大部分优化期 UB，Debug 干净不代表 Release 干净。
- sanitizer 组合互斥：ASan/LSan 与 valgrind 不同跑，TSan 需全程序插桩（含依赖库），
  MSan 需所有依赖重编。链接期 `-fsanitize=address` 必须同时给编译与链接，漏了就是假阴性。
- 构建器：Make 只在已有成熟 Makefile 时保留；新工程 CMake（≥3.20）或 meson。CMake 用
  target-based（`target_link_libraries(... PRIVATE/INTERFACE)`），禁 `include_directories` 全局污染；
  meson 用 `dependency('libssl')` 走 pkg-config，交叉时配 `--pkg-config-path` 与 native file。
- 依赖发现：`pkg-config --cflags --libs foo` 前先 `PKG_CONFIG_PATH`/`PKG_CONFIG_SYSROOT_DIR`；
  交叉编译不设 `SYSROOT_DIR` 会把宿主路径混进目标 flag，这是交叉编译失败的头号原因。
- 交叉三元组要实测：`aarch64-linux-gnu-gcc` 是否存在、sysroot 里有没有 `libc.so.6`/musl、
  `readelf -h` 确认 `Machine` 与 `Type`。CI 用 qemu-user 跑目标架构测试。

## 坑位

- `-j$(nproc)` 在容器里按宿主核数算，cgroup 限额下会 OOM：用 `nproc --all` 对比 `cpu.max`。
- LTO 让调试符号与 sanitizer 报告失真，问题定位阶段先关 `-flto`。
- CMake `CMAKE_CROSSCOMPILING` 为真时 `find_package` 走 `CMAKE_FIND_ROOT_PATH_MODE_*`，
  默认 `ONLY` 会找不到宿主工具（如需宿主 protoc 要显式放行）。
- 增量构建不可复现：改 `-D` 宏定义不触发重编（Make 不追踪 flag），一律 clean build 验证发布物。

## 取证命令

`cc --version`、`cmake --version`、`meson --version`、`pkg-config --list-all | wc -l`、
`gcc -v 2>&1 | grep -E 'configured|Target'`、`qemu-aarch64 -L <sysroot> ./prog`

出处：[`references/工具链与打包.md`](../../references/工具链与打包.md)
