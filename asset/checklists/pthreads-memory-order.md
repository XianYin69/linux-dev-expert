# 检查清单 · pthreads-memory-order

## 竞争与顺序

- [ ] 每个共享可变状态都有明确保护者（互斥锁 / 原子 / 单线程所有权），无「裸读标志位」
- [ ] 原子的非默认内存序逐个给出理由（为何 `release/acquire` 足够、`relaxed` 不跨对象排序）
- [ ] happens-before 链能写成一句话：「A 的写在 X 发布前，B 在 X 获取后读到」
- [ ] 双重检查/惰性初始化改用 `pthread_once`、`std::call_once` 或加锁，不用裸 volatile

## 锁

- [ ] 锁的粒度与保护不变量匹配；持锁区间无阻塞 IO、无 `sleep`、无回调进用户代码
- [ ] 多锁顺序全局固定并有文档，防 ABBA；必要时 `pthread_mutex_trylock` + 退避
- [ ] 条件变量配 `while` 谓词循环（虚假唤醒），且等待与互斥锁是同一把
- [ ] 递归锁/读写锁的使用有理由；rwlock 与 mutex+分片做过基准对比
- [ ] 优先级反转风险已评估（`PRIO_INHERIT` 或改无锁/单线程模型）

## 线程生命周期

- [ ] 线程退出与资源回收路径明确（`pthread_join`/detach 二选一，不混用）
- [ ] 线程栈大小按需求设定（递归/大局部数组场景），默认 8MB 不是保证
- [ ] TLS 初始化的动态开销与析构顺序已核对，`pthread_getspecific` 前 key 已创建
- [ ] 关闭顺序：先停接受 → 排空队列 → 通知退出 → join 带超时

## 取证

- [ ] TSan（`-fsanitize=thread`，全程序重编）与 `valgrind --tool=helgrind` 至少一项跑过
- [ ] 压测覆盖竞争窗口（高并发 + 随机延迟），并记录 P99 与 CPU 利用率
- [ ] 无竞争结论标注覆盖范围；TSan 未插桩的依赖库不得称「已验证无竞争」
