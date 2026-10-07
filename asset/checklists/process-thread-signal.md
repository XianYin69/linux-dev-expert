# 检查清单 · process-thread-signal

## 创建与继承

- [ ] `fork` 后到 `exec` 之间只调用 async-signal-safe 函数（或直接换 `posix_spawn`）
- [ ] `exec` 前显式设定 `PATH`、`LANG`、`TZ`、`LD_LIBRARY_PATH`（如需），不继承脏环境
- [ ] 子进程 fd 继承面已审：非必需 fd 全部 `O_CLOEXEC`/`FD_CLOEXEC`
- [ ] 管道/pty 两端在父进程侧关闭多余副本，否则读端永不 `EOF`

## 终止与回收

- [ ] 有 `SIGCHLD` 收割路径：`waitpid(-1, ..., WNOHANG)` 循环至 `ECHILD` 或 `SA_NOCLDWAIT`
- [ ] 退出码语义约定（0/1/124 超时/128+n 信号）并在文档中写明
- [ ] 子进程用 `_exit` 不用 `exit`（避免冲刷父进程 stdio 缓冲）
- [ ] 超时后有 `kill(SIGKILL)` 兜底，且等过 `waitpid` 防僵尸

## 信号

- [ ] 阻塞掩码在建线程前统一设置，由专用线程 `sigwaitinfo` 消费
- [ ] `SIGPIPE` 已处理（`MSG_NOSIGNAL` 或忽略），写已关连接不会莫名终止
- [ ] `SIGTERM` 走优雅关闭：停接受 → 排空 → 落盘 → 退出，且有 `TimeoutStopSec` 上限
- [ ] 处理函数内只做置标志 + `write` 到 self-pipe/`eventfd`，无 malloc/printf/加锁
- [ ] `errno` 与被打断系统调用的重试策略已处理

## 取证

- [ ] `strace -f -e trace=signal,process` 输出与预期一致
- [ ] `/proc/<pid>/status` 的 `SigBlk/SigIgn/SigCgt` 与代码设定吻合
