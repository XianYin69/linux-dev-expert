# 检查清单 · systemd-dbus-cgroup-security

## 单元正确性

- [ ] init 系统已实测（`ps -o comm= -p 1`），非 systemd 时改给对应监管方案
- [ ] `Type=` 与程序行为匹配（simple/forking/notify/oneshot），就绪语义不靠 `sleep` 猜
- [ ] `systemd-analyze verify <unit>` 无错误；`daemon-reload` 后 `is-active` 与 `status` 复验
- [ ] `ExecStart` 用绝对路径且可执行位/解释器正确；`WorkingDirectory`、`Environment` 显式
- [ ] `Restart=`/`RestartSec=`/`StartLimitBurst=` 组合合理，`TimeoutStartSec`/`TimeoutStopSec` 有界

## 激活与依赖

- [ ] socket 激活：程序确实使用 `$LISTEN_FDS`/`sd_listen_fds`，`.socket` 与 `.service` 名字对应
- [ ] timer：`OnCalendar` 语义、`Persistent=`、`RandomizedDelaySec=`、时区已核对
- [ ] `After=`/`Requires=`/`Wants=`/`BindsTo=` 与真实启动依赖一致，无循环依赖

## 资源约束（cgroups v2）

- [ ] `MemoryMax`/`CPUWeight`/`TasksMax`/`IOWeight` 生效（`systemctl show` + `memory.max` 双查）
- [ ] 需要自管子组的已 `Delegate=`，控制器委派链正确（父 no→子可写）
- [ ] OOM 行为预期明确（`OOMPolicy`、`OOMScoreAdjust`），`Restart` 覆盖被杀场景

## 权限与安全

- [ ] 非 root 运行（`User=`/`DynamicUser=`），端口<1024 用 `AmbientCapabilities=CAP_NET_BIND_SERVICE`
- [ ] `CapabilityBoundingSet=` 逐项最小化，`NoNewPrivileges=yes`
- [ ] `ProtectSystem=`/`ProtectHome=`/`PrivateTmp=`/`PrivateDevices=`/`RestrictAddressFamilies=`
  开启且功能未破（逐项开关实测，非「应该没问题」）
- [ ] `SystemCallFilter=` 生效后关键路径无 EPERM（`journalctl` 查 `seccomp` 拒绝）
- [ ] LSM 状态已查（`getenforce`/`aa-status`），AVC 拒绝有修复方案而非关闭模块
- [ ] `systemd-analyze security <unit>` 评级记录在案

## 可观测

- [ ] 日志进 journald（stdout/stderr），字段可 `journalctl -u` 过滤；错误级 `journalctl -p err`
- [ ] dbus 接口名/对象路径经 `busctl list|tree` 验证，session 与 system bus 不混
- [ ] 健康检查/watchdog（`WatchdogSec` + `sd_notify`）或外部探针已配置
