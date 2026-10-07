# root 权限约束

## 规则

1. **最小权限优先**：能用非特权解决的不得请求 root。顺序为——用户级能力 →
   `setcap`/`AmbientCapabilities` → polkit 单操作授权 → udev 规则改设备组 → 最后才 sudo。
2. **逐项说明必要性**：每条需要 root 的命令必须附三行：
   `为什么必须特权`、`不执行的后果`、`最小化替代（含命令）`。缺任一项即不得给出。
3. **禁止整脚本 sudo**：不得建议 `sudo bash script.sh` 全量提权；提权只包住真正需要的那几条，
   并在脚本内 `[[ $EUID -eq 0 ]] || die` 显式断言边界。
4. **禁止持久化提权面**：不得写 `/etc/sudoers`、`sudoers.d` 放宽 `NOPASSWD`；
   不得 `chmod u+s`、不得设 `setuid` 位作为「快速修法」。
5. **服务侧优先降权**：给 systemd 单元时默认 `User=`/`DynamicUser=yes` +
   `CapabilityBoundingSet=`，而不是 `root` + 全能力。
6. **文件写入边界**：系统路径写入前先 `test -w`/`ls -l` 判定，改配置一律
   `cp -a file file.bak-$(date +%F-%H%M)` 备份，并给回滚命令。
7. **审计留痕**：特权操作完成后附验证命令（`id`、`getcap`、`systemctl show -p User`）
   与撤销命令（`setcap -r`、`loginctl disable-linger`）。

## 违反后果

- 提权面永久残留，成为横向移动入口；误操作影响整机；违反用户环境的安全基线。

## 相关

- [`破坏性命令约束`](../破坏性命令约束/破坏性命令约束.md)
- [`探测优先约束`](../探测优先约束/探测优先约束.md)
- [`../SKILL.md`](../../SKILL.md)
