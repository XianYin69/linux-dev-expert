# posix-glibc-syscalls

主问句：这个接口在目标 glibc/内核版本上的契约与错误语义是什么？

## 判据

- 接口分层要分清：POSIX 标准接口（`open`/`read`）、Linux 专有 syscall（`epoll_create1`/
  `statx`/`getrandom`）、glibc 包装（`posix_spawn`）。可移植性结论按层给，不按「Linux 都行」给。
- `errno` 只在返回 -1/NULL 时有效；成功返回后读 errno 是错的。跨线程共享 errno 是 glibc 的
  TLS 实现，信号处理函数里改 errno 要显式保存恢复。
- `EINTR` 是常态不是异常：`read`/`accept`/`wait`/`futex` 都可能被打断。要么 `SA_RESTART`
  要么写重试循环，二者不可混用（`poll`/`select`/`sleep` 类不受 `SA_RESTART` 保护）。
- glibc 版本决定行为：≥2.34 `libpthread` 并入 `libc`（旧 `-lpthread` 仍可用但为空壳）；
  ≥2.17 起 `clock_*` 不再需要 `-lrt`；`getrandom` 需内核 ≥3.17。写链接选项前先 `ldd --version`。
- 大文件：`off_t` 32 位风险靠 `-D_FILE_OFFSET_BITS=64` 解决，它改变符号名（`open64`），
  与第三方库混用时 ABI 要一致。
- `O_DIRECT`/`O_SYNC`/`O_APPEND` 语义互不覆盖：`O_APPEND` 保证偏移原子但不管页缓存；
  `O_DIRECT` 要求对齐（offset/length/buffer 均按 `stat.st_blksize` 或 512B 起）。

## 坑位

- `PATH_MAX` 不是硬保证：`pathconf(_PC_PATH_MAX)` 才是；`getcwd` 失败要用动态缓冲。
- `_SC_OPEN_MAX` 与 `ulimit -n` 不同源：systemd 的 `LimitNOFILE`/`RLIMIT_NOFILE` 会覆盖 shell 值。
- `strerror` 非线程安全（静态缓冲），用 `strerror_r`；GNU 版与 XSI 版返回类型不同，须核对。
- `realpath` 在符号链接指向不存在文件时的行为随 glibc 版本变过；判存在再解析。
- 时间：`localtime` 返回静态缓冲，用 `localtime_r`；TZ 改变后须 `tzset()` 才生效。

## 取证命令

`man 2 <name>`、`man 3 <name>`、`getconf -a | grep _SC_`、`ldd --version`、
`strace -e trace=%file,%desc ./prog`、`ulimit -a`、`cat /proc/sys/kernel/osrelease`

出处：[`references/标准与手册.md`](../../references/标准与手册.md)
