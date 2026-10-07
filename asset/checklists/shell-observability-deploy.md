# 检查清单 · shell-observability-deploy

## 脚本健壮性

- [ ] 头部 `set -euo pipefail`（bash）或 POSIX 等价显式错误检查；`sh` 未误用 bash-only 语法
- [ ] 所有变量加引号，`IFS` 显式设定，文件遍历用 `-print0` + `read -r -d ''`，不用 `ls`
- [ ] 参数解析用 `--` 终止选项，异常文件名（空格/换行/`-` 开头）不会造成误操作
- [ ] `mktemp` 建临时文件与目录，`trap` 清理（EXIT/INT/TERM），无固定 `/tmp` 名字
- [ ] 并发入口有锁（`flock`/`mkdir`），cron 任务不会重叠执行
- [ ] `bash -n` 与 `shellcheck` 零告警（或逐条豁免说明）

## 日志与观测

- [ ] 日志走 stdout/stderr 交 journald，或写文件时字段化（`ts= level= msg= key=value`）
- [ ] 文件日志有 logrotate 配置且验证（`logrotate -d`），程序支持重开信号或 `copytruncate`
- [ ] journald 容量策略确认（`SystemMaxUse`），未对 journald 套 logrotate
- [ ] 关键路径有度量：耗时、队列深度、失败计数，可被 `journalctl -o json` 或指标端点取到

## 调度与时区

- [ ] cron 迁移到 systemd timer 时核对 `Persistent=`、时区、抖动与并发保护
- [ ] 时间戳输出带时区（`date +%FT%T%z`），跨机比对不依赖本地默认时区
- [ ] NTP 跳变场景下取证窗口用 `BOOT_ID`/`--cursor` 而非仅 `--since`

## 部署与回滚

- [ ] 交付四件套齐全：构建命令、部署单元、验证命令、回滚方案
- [ ] 健康检查三层（存活/就绪/健康）各有实现与超时，失败时 `Restart` 与告警行为明确
- [ ] 配置与密钥不进镜像层，来源（`EnvironmentFile`/`LoadCredential`/secret 挂载）写明
- [ ] 升级路径兼容旧数据/旧配置，回滚命令实测过（非纸面）

## 文件系统差异

- [ ] 大小写敏感性与文件名编码（UTF-8 归一）在目标文件系统上验证过
- [ ] inotify 上限（`max_user_watches`）与 WSL/drvfs、NFS 上的可用性差异已实测
