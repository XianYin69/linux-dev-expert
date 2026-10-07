# 检查清单 · fd-io-epoll-iouring

## 描述符

- [ ] 每个 `open`/`socket`/`dup` 都有配对的关闭路径（含错误分支），RAII/清理标签覆盖早退
- [ ] `O_CLOEXEC`、`SOCK_NONBLOCK|SOCK_CLOEXEC`、`accept4` 一步到位，无 `fcntl` 二次设标志竞态
- [ ] fd 数量上限按 `RLIMIT_NOFILE` 验证过，泄漏测试（长跑 + `ls /proc/<pid>/fd | wc -l`）通过
- [ ] `epoll` 注册表与 fd 生命周期一致：关 fd 前已 `EPOLL_CTL_DEL`（或依赖 close 自动移除并说明）

## 事件循环

- [ ] 触发模式选定并写明：LT 读尽缓冲、ET 循环到 `EAGAIN`，二者不混用
- [ ] `EPOLLONESHOT` 使用后每次事件都重 `arm`
- [ ] 每轮循环有超时与心跳，`epoll_wait` 返回 `EINTR` 不终止循环
- [ ] 背压策略明确（队列上限、丢弃或阻塞），慢客户端不会耗尽 fd/内存

## 缓冲与持久性

- [ ] stdio/页缓存/设备三层缓冲各自的处理点写清：`fflush`、`fsync`、`fdatasync` 选对
- [ ] 新建/重命名文件的可见性有目录 `fsync`（掉电一致性）
- [ ] `O_DIRECT` 对齐（buffer/offset/length）已实测，未对齐路径有回退
- [ ] 读写合并与延迟权衡有数据支撑（`pidstat -d`、`blktrace` 或 bpftrace biolatency）

## io_uring（如使用）

- [ ] 内核版本与 liburing 版本已核对，特性（SQPOLL/FIXED_FILE/协程）在版本内可用
- [ ] 提交/完成队列的批量大小与 CQE 溢出处理有策略
- [ ] 与 `epoll` 方案做过同负载对比（吞吐 + P99），收益数据入库；无数据只写「推测」

## 取证

- [ ] `ss -tanp`、`lsof -p`、`strace -e trace=%desc` 至少一项输出作为结论依据
