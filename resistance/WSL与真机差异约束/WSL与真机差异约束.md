# WSL 与真机差异约束

## 规则

1. **先判定环境类型**：`uname -r | grep -i microsoft`、`/proc/version`、
   `systemd-detect-virt`、`/proc/sys/fs/binfmt_misc` 是否存在，再决定给哪套方案。
2. **systemd 不是默认就有**：WSL 需 `/etc/wsl.conf` 的 `[boot] systemd=true` 且重启发行版
   （`wsl --shutdown`）才生效。判定用 `ps -o comm= -p 1`，不得假定 unit 可用。
3. **文件系统分域**：`/`（ext4，Linux 元数据完整）与 `/mnt/c`（drvfs/9P，权限位与
   符号链接不可靠、inotify 事件不保证、大小写不敏感）。性能与语义结论必须写明所在域。
4. **性能数字不可跨域引用**：drvfs 上 IO 慢 1~2 个数量级属正常，不得据此判定程序有性能缺陷，
   也不得把 ext4 上的数字当作生产环境预期值。
5. **GPU 与设备直通须实测**：`/dev/dri`、`nvidia-smi`、`/dev/infiniband`、串口/USB
   在 WSL 上的可用性依赖 Windows 侧驱动与版本，未实测不得声称可用。
6. **网络模型不同**：WSL2 是 NAT 虚拟网卡，入站连接需端口转发；`localhost` 互通有版本差异；
   组播/广播与 `SO_REUSEPORT` 行为可能不同。
7. **内核能力差异**：WSL 用微软定制内核（`bzImage`），部分模块（`br_netfilter`、`nf_tables`、
   `overlayfs` 上层选项、eBPF/bpf 系统调用限制）可能缺失；`modprobe` 失败即降级说明。
8. **时钟与休眠**：WSL 实例闲置会挂起，`CLOCK_MONOTONIC` 与定时器在恢复后可能跳变，
   长驻服务与 cron/timer 结论须标注此风险。

## 违反后果

- 在 WSL 上给真机方案（或反之）导致服务起不来、性能误判、设备不可用被归因于代码 bug。

## 相关

- [`探测优先约束`](../探测优先约束/探测优先约束.md)
- [`../scripts/probe_os.py`](../../scripts/probe_os.py)
