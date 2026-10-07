# pthreads-memory-order

主问句：共享状态的 happens-before 从哪来，锁与原子是否覆盖全部访问？

## 判据

- 数据竞争定义：两个线程访问同一内存位置、至少一个是写、无 happens-before 顺序 → UB。
  「只是读个标志位，最坏读到旧值」不是安全理由，编译器可把非原子读提升或撕裂。
- 锁的正确用法是「保护不变量」不是「保护变量」：`pthread_mutex_lock` 前后成对，
  条件变量必须配 `while` 谓词循环（虚假唤醒），`pthread_cond_wait` 与互斥锁绑定同一把。
- 读写锁 `pthread_rwlock` 在写者饥饿与缓存行弹跳上表现差，多数场景 `mutex` + 分片更快；
  用之前先给基准，不得默认「读多写少就用 rwlock」。
- 内存序：`seq_cst` 是默认也是最强；`release/acquire` 只保证「发布前写入对获取后可见」，
  不提供全局单序；`relaxed` 只保证原子性与同址修改顺序，跨对象顺序一律不给。
- 自旋锁在 Linux 上不是首选：无优先级继承会优先级反转，`futex` 让内核托管等待才是正解
  （`pthread_mutex` 底层即 futex）。持锁期间不得做阻塞 IO。
- TLS：`__thread`/`thread_local` 有动态初始化成本，`pthread_getspecific` 需一次性 key 创建；
  线程退出前 `pthread_key_create` 的 destructor 会跑，别在里面拿已销毁对象。

## 坑位

- 双重检查锁定必须用原子或加锁发布，裸 `volatile` 在 C/C++ 内存模型下不成立。
- `pthread_atfork` 注册的处理器在多线程 fork 后极易死锁，能不依赖就不依赖。
- 信号处理函数里唯一安全的异步函数是 `pthread_kill`/`sigprocmask` 等列表内项，其余别碰。
- TSan 只能证「有竞争」不能证「无竞争」；覆盖率不足时结论须标 advisory。
- 线程栈大小与 `RLIMIT_STACK` 无关，`pthread_attr_setstacksize` 单独控制，默认 8MB。

## 取证命令

`gcc -fsanitize=thread`、`valgrind --tool=helgrind`/`--tool=drd`、`perf lock`、
`gdb -ex 'thread apply all bt' -p <pid>`、`cat /proc/<pid>/task/*/stat`

并发架构设计转派 `concurrency-design`（见 [`dependence/dependence.md`](../../dependence/dependence.md)）。
