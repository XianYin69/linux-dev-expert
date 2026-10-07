# fd-io-epoll-iouring

主问句：阻塞点在哪、就绪事件如何取、缓冲与提交队列如何影响尾延迟？

## 判据

- fd 是进程级资源：`dup`/`fork` 共享 file description（偏移也共享），`O_CLOEXEC` 漏设是
  子进程句柄泄漏的头号原因。查泄漏：`ls -l /proc/<pid>/fd | wc -l` 随时间增长即泄漏。
- 缓冲三层：stdio（`BUFSIZ`，行/全缓冲）、页缓存（`dirty_ratio` 控制回写）、设备队列。
  `fflush` 只出 stdio，`fsync` 才落设备；掉电安全要 `fsync` 文件 + 目录 fd（重命名可见性）。
- `epoll` 三坑：水平触发下忘读尽导致忙循环；边缘触发必须读到 `EAGAIN` 且每 fd 只注册一次；
  `EPOLLONESHOT` 后不重arm 就再也不通知。`accept4(..., SOCK_NONBLOCK|SOCK_CLOEXEC)` 一步到位。
- `epoll` 的 `man` 明确：并发场景下 `EPOLL_CTL_DEL` 无需先 `EPOLL_CTL_MOD` 删空（旧说法已作废）。
- `io_uring` 需内核 ≥5.1（实用 ≥5.10 才有 SQPOLL/协程友好），liburing 版本要与内核特性对齐；
  它把 syscall 摊成批量提交，收益在高 IOPS 小 IO，低并发大文件不明显——须 `perf` 实测再下结论。
- 阻塞判定：`/proc/<pid>/task/*/wchan` 与 `stack`、`pidstat -d`、`offcputime` 三处交叉，
  单看 CPU 占用会漏掉「卡在内核里不耗 CPU」的情况。

## 坑位

- `select` 有 `FD_SETSIZE`（常 1024）上限且每次重建集合，O(n)；高并发一律 `epoll`。
- `O_NONBLOCK` 下 `write` 返回短写是正常，必须循环；`send` 的 `MSG_MORE` 与 Nagle 交互要实测。
- 管道/PTY 的 `SIGPIPE` 与 `EPIPE` 二选一，取决于是否忽略信号。
- inotify 有 `max_user_watches`（`/proc/sys/fs/inotify/`），容器与 WSL 上默认值常不够。
- 网络 fd 上的 `EPOLLET` + 短读会丢事件：循环到 `EAGAIN` 是唯一正确写法。

## 取证命令

`ss -tanp`、`cat /proc/<pid>/fdinfo/*`、`lsof -p <pid>`、`strace -e trace=%desc,%net ./prog`、
`io_uring` 侧 `cat /proc/<pid>/fdinfo/<ring>`、`perf trace -e '*:ioctl'`

出处：[`references/排障与性能.md`](../../references/排障与性能.md)
