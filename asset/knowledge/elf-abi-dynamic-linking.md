# elf-abi-dynamic-linking

主问句：符号从哪个库解析、SONAME/rpath 是否指向预期、ABI 是否向后兼容？

## 判据

- 解析顺序：`DT_RPATH`（已被 GNU ld 默认弃用）→ `LD_LIBRARY_PATH` → `DT_RUNPATH` →
  `/etc/ld.so.cache`（`ldconfig` 生成）→ 默认目录。`RUNPATH` 不传递给间接依赖，`RPATH` 会——
  这是「本地跑得好、部署后找不到库」的根因之一。
- `SONAME` 是 ABI 契约：链接期写入 `DT_SONAME`，运行时按它找。改 `SONAME` = 破坏兼容；
  发布新库须 `ldconfig` 后 `ldd -r` 复验未定义符号为 0。
- 符号版本（`--version-script`、`GLIBC_2.x`）让同一 `.so` 承载多代 ABI。排查
  `version 'GLIBC_2.34' not found` 是**目标机 glibc 太旧**，不是程序 bug——部署前查
  `objdump -T | grep GLIBC_` 取最高需求版本。
- 静态链接三选一：`-static`（全静态，NSS/glibc 动态加载会运行时炸）、`-static-pie`（需 PIE+
  glibc 支持）、musl 静态（`-static` + musl-gcc，最干净）。musl 与 glibc 差异：无 NIS/glibc
  扩展、`pthread_setname_np` 参数不同、DNS 走自身解析、栈大小默认 128KB 需显式设。
- 位置无关：共享库必须 `-fPIC`；`-fPIE -pie` 给可执行文件（ASLR）。混用会报
  `relocation R_X86_64_32 against ... can not be used when making a shared object`。
- C++ ABI 兼容看 `_GLIBCXX_USE_CXX11_ABI`（0/1）与 libstdc++ 的 `GLIBCXX_x.y` 符号版本，
  跨编译器（GCC↔Clang）传 C++ 类型不保证 ABI 稳定，接口层用 C ABI。

## 坑位

- `LD_PRELOAD` 在 setuid 程序下被忽略（安全策略），别拿它当生产补丁手段。
- `dlopen` 符号可见性受 `RTLD_GLOBAL`/`-Bsymbolic`/`-fvisibility=hidden` 三方影响。
- 未 strip 的调试符号 ≠ 导出符号：`nm -D`（动态）与 `nm`（全部）结论不同，别看错。
- `strip --strip-unneeded` 会破坏 `.eh_frame` 之外的栈回溯信息，core 分析前留 build-id。
- 大页/文本重定位（`-Wl,-z,relro,-z,now`）影响启动耗时与安全，须成对评估。

## 取证命令

`readelf -dhlS`、`objdump -T/-p`、`nm -D --defined-only`、`ldd -r`、`ld.so --list`、
`eu-readelf --debug-info`、`file`、`patchelf --print-rpath`

出处：[`references/工具链与打包.md`](../../references/工具链与打包.md)
