# 检查清单 · posix-glibc-syscalls

交付前逐条勾选；未勾选不得称「已验证」。

## 接口与版本

- [ ] 目标内核版本与 glibc 版本已实测（`uname -r`、`ldd --version`），结论标注版本适用区间
- [ ] 用到的接口分层已标明（POSIX / Linux-only / glibc 扩展），跨发行版结论不越层
- [ ] 新增 syscall 的内核引入版本已核对（`man 2 <name>` 的 COLOPHON/VERSION 段）
- [ ] `_FILE_OFFSET_BITS=64`、`_GNU_SOURCE`、`_POSIX_C_SOURCE` 的定义组合已确定且不冲突

## 错误与阻塞

- [ ] 每个可能 `EINTR` 的调用有重试循环或明确 `SA_RESTART` 策略
- [ ] `errno` 仅在失败分支读取；信号处理函数内保存/恢复 `errno`
- [ ] 失败路径给出可诊断信息（`strerror_r` + 路径/fd/操作名），不静默返回
- [ ] 部分读/部分写（short read/write）被循环处理，`EOF` 与错误区分开

## 资源上限

- [ ] `RLIMIT_NOFILE` 与 systemd `LimitNOFILE` 一致，且高并发场景已按目标值验证
- [ ] `pathconf`/`fpathconf` 取动态上限，不硬编码 `PATH_MAX`/`NAME_MAX`
- [ ] 缓冲区大小来自 `st_blksize`/`getconf`，非拍脑袋常量

## 时间与环境

- [ ] 时区与 locale 显式设置（`TZ`、`LANG`），`localtime_r`/`gmtime_r` 而非静态版本
- [ ] 单调时间用 `clock_gettime(CLOCK_MONOTONIC)`，不用 `gettimeofday` 做超时差值

## 取证

- [ ] 附 `strace -e trace=...` 或 `man` 页截图/文本作为判据出处
- [ ] 与手册冲突处已标注差异并给复现命令
