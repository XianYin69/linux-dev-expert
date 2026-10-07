# shell-observability-deploy

主问句：脚本在异常输入下是否失败即停，运行状态能否被日志与健康检查观测？

## 判据

- 健壮性头三行：`set -euo pipefail`（bash）、`IFS=$' \t\n'` 显式、`trap 'exit 130' INT TERM`。
  `sh`/dash 无 `pipefail` 与数组——POSIX 脚本改用显式 `if ! cmd; then exit; fi` 与 `$?` 检查。
- 引号与展开：`"$var"` 与 `${var:?"must be set"}`；文件参数用 `--` 终止选项解析，
  防 `-rf` 之类被当选项。遍历文件用 `find -print0 | while IFS= read -r -d ''`，不用 `ls`。
- 临时文件与并发：`mktemp -t name.XXXXXX`（勿用 `/tmp/fixed`，符号链接劫持），
  锁用 `flock /var/lock/x.lock -c '...'` 或 `mkdir` 原子语义，cron 任务必加锁防重叠。
- 观测面：日志走 stdout/stderr 交给 journald（`StandardOutput=journal`），字段化
  （`key=value`）便于 `journalctl -o json` / `grep`；文件日志一律配 logrotate
  `copytruncate` 或程序侧重开信号（`systemctl reload` + `ExecReload`）。
- cron vs timer：timer 有 `Persistent`、`RandomizedDelaySec`、`Accuracy`、可与 unit 依赖绑定，
  新代码一律 timer；遗留 crontab 迁移时须核对时区（cron 用系统 TZ，timer 可 `Timezone=`）。
- 健康检查三层：进程存活（`sd_notify`/`Type=notify`）、就绪（`ExecStartPost` 探测端口）、
  健康（watchdog `WatchdogSec` + `sd_notify(WATCHDOG=1)`，或外部 `curl /healthz`）。
- 时区与 locale：程序行为随 `LC_*` 变（排序、数字、大小写转换、`strptime`）。服务显式设
  `Environment=LANG=C.UTF-8`/`TZ=`，别依赖宿主环境；`date` 输出跨机比对须带 `%z`。
- 大小写与编码：ext4 大小写敏感、vfat/WSL drvfs 不敏感；文件名 UTF-8 无规范化保证，
  比对前 `iconv`/`unicodedata` 归一。路径含空格与换行是常态，脚本按 NUL 分隔处理。

## 坑位

- `set -e` 不管管道中段（须 `pipefail`）、不管 `cmd || true` 掩盖的失败、不管函数返回值未检查。
- `$(...)` 里 `exit` 只退子 shell；`while read` 循环里的变量在管道后丢失（用 `< file` 重定向）。
- logrotate 对 journald 无意义（journald 自管 `SystemMaxUse`），别给 journal 套 logrotate。
- `journalctl --since` 依赖机器时钟，NTP 跳变后取证窗口要按 `--cursor` 或 `BOOT_ID` 划。

## 取证命令

`bash -n script.sh`、`shellcheck script.sh`、`journalctl -u <unit> --since -5m -p err`、
`systemctl is-active/is-enabled`、`curl -fsS localhost:health`、`logrotate -d /etc/logrotate.d/x`

出处：[`references/排障与性能.md`](../../references/排障与性能.md)
