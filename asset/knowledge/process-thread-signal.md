# process-thread-signal

主问句：执行体如何创建、继承、终止，信号在何处被投递与打断？

## 判据

- `fork` 后子进程只继承地址空间快照，锁状态不继承：fork 后到 exec 之间只能做 async-signal-safe
  操作（`_exit`、`execve`、`dup2`），printf/malloc 都可能死锁。优先 `posix_spawn` 或 `vfork`+exec。
- `exec` 家族的环境继承要写清：`PATH`、`LD_LIBRARY_PATH`、`LANG`、`TZ` 缺失是服务启动失败主因；
  systemd 的 `Environment=` 与 shell 环境不是同一套。
- 僵尸来自不 `wait`：`SIGCHLD` 设 `SA_NOCLDWAIT` 或显式 `waitpid(-1, WNOHANG)` 循环收割；
  一次 `waitpid` 收不干净多子进程，必须循环到 `ECHILD`。
- 信号两类：标准 1..31 无排队（同 sig 多次只留一个），`SIGRTMIN..` 实时可排队。
  `kill` 只保证投递，不保证语义——业务同步不要用信号，用 `signalfd`/`eventfd`/self-pipe。
- 信号掩码是 per-thread，但 pending 集是 per-process 的：`pthread_sigmask` 要在建线程前统一屏蔽，
  由专用线程 `sigwaitinfo` 消费，否则随机线程被打断。
- 默认动作要背：`SIGPIPE` 终止（写已关 socket 必踩，`MSG_NOSIGNAL` 或忽略它）、
  `SIGTERM` 可捕获须做优雅关闭、`SIGKILL`/`SIGSTOP` 不可捕获、`SIGHUP` 常作重载配置。

## 坑位

- 信号处理函数里拿 `errno` 会被破坏：进函数先存、出函数再恢复。
- `atexit`/`on_exit` 只在 `exit` 走，`_exit` 不走；`fork` 子进程用 `_exit`。
- 线程崩溃 = 进程崩溃：未捕获异常在 `std::thread` 里直接 `terminate`。
- `prctl(PR_SET_PDEATHSIG)` 有竞态（父已退出则不生效），须再查 `getppid()==1`。
- core 文件：`ulimit -c`、`/proc/sys/kernel/core_pattern`（管道模式由 systemd-coredump 接管）。

## 取证命令

`ps -eLf`、`ls /proc/<pid>/task`、`cat /proc/<pid>/status | grep -E 'SigBlk|SigIgn|SigCgt'`、
`strace -f -e trace=signal,process ./prog`、`sysctl kernel.core_pattern`

出处：[`references/标准与手册.md`](../../references/标准与手册.md)
