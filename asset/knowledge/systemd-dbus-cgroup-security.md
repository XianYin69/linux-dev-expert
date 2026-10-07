# systemd-dbus-cgroup-security

主问句：服务如何被拉起与约束，权限与标签是否最小且可审计？

## 判据

- 先判 init：`ps -o comm= -p 1`。非 systemd（OpenRC/runit/s6/supervisord/容器内 no-init）时
  不得给 unit 文件；容器里常由入口脚本或 s6 承担监管职责。
- 类型选对：`Type=simple`（默认，进程即服务）、`forking`（传统 daemon 双 fork）、
  `notify`/`notify-reload`（`sd_notify(0)`，就绪才算启动成功）、`oneshot`（一次性）、
  `idle`（延后到事务结束）。用 `notify` 就别再靠 `sleep` 猜启动完成。
- socket 激活：`.socket` + `Accept=no`（长连接）或 `Accept=yes`（每连接一进程，`@.service` 模板）。
  程序须用 systemd 传入的 fd（`sd_listen_fds(1)` 或 `$LISTEN_FDS`），自己 bind 就失去激活意义。
- 定时器：`OnCalendar` 比 cron 有 `Persistent=true` 补跑、随机抖动 `RandomizedDelaySec`、
  与 unit 生命周期绑定。替代 cron 时须写清时区（`Timezone=` 或绝对时间）。
- cgroups v2 统一层级：控制器须父委派（`Delegate=`）子树才可写；限额用
  `MemoryMax`/`CPUWeight`/`IOWeight`/`TasksMax`，v1 的 `MemoryLimit`/`cpu.shares` 拼写不同。
  查生效：`systemctl show -p MemoryMax` 与 `cat /sys/fs/cgroup/<path>/memory.max`。
- 安全基线成组写：`NoNewPrivileges`、`ProtectSystem=strict`、`ProtectHome`、`PrivateTmp`、
  `PrivateDevices`、`RestrictAddressFamilies`、`CapabilityBoundingSet=`（配合
  `AmbientCapabilities=CAP_NET_BIND_SERVICE` 而非 root）、`SystemCallFilter=@system-service`。
  每项都要实测功能未破，`systemd-analyze security <unit>` 给评级。
- LSM：`getenforce`（SELinux enforcing/permissive/disabled）与 `aa-status` 决定能否用
  `ExecStart` 里的自定义路径；拒绝看 `journalctl -k | grep -i avc` 或 `ausearch -m avc`，
  修标签/写 policy，而不是 `setenforce 0` 关掉完事。

## 坑位

- `Restart=on-failure` 不覆盖被 `SIGKILL`（OOM）杀掉的场景，需 `Restart=always` + `OOMPolicy=`。
- 用户级单元（`systemctl --user`）在无 linger 时随登录退出：`loginctl enable-linger <user>`。
- `EnvironmentFile=` 不做 shell 展开，`Environment=` 语法与 shell 不同（引号规则）。
- dbus 名字被抢（`org.freedesktop.DBus.Error.ServiceUnknown`）先 `busctl list | grep`，
  再看是 session bus 还是 system bus，两者策略文件不同。

## 取证命令

`systemctl status --no-pager`、`systemd-analyze verify <unit>`、`systemd-cgls`、`busctl tree <name>`、
`journalctl -u <unit> -b --no-pager -n 200`、`systemd-analyze security <unit> --no-pager`

出处：[`references/系统与服务.md`](../../references/系统与服务.md)
