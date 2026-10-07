# distro-packaging

主问句：这个包名/依赖/多架构路径在目标发行版族上成立吗？

## 判据

- 族判定只看 `/etc/os-release` 的 `ID` 与 `ID_LIKE`：debian/ubuntu→apt+dpkg；
  fedora/rhel/centos/rocky/almalinux→dnf/yum+rpm；alpine→apk+musl；arch→pacman；
  suse→zypper。包名跨族不同（`libssl-dev` vs `openssl-devel`），给命令必须按族并列或限定范围。
- 开发头文件与运行时库分包：`libfoo3`（运行时）+ `libfoo-dev`/`libfoo-devel`（头与 .so 符号链接）。
  编译报 `foo.h: No such file` 十有八九是缺 dev 包，不是库没装。
- 非交互安装三件套：`DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends`、
  `dnf -y --setopt=install_weak_deps=False`、`apk add --no-cache`。镜像里再叠一层
  `--no-install-recommends` + 清理缓存，体积差异常在 2~5 倍。
- 多架构（Debian `dpkg --add-architecture arm64`）：交叉依赖源须加 `[arch=arm64]` 到 sources，
  库路径变 `/usr/lib/aarch64-linux-gnu`，`pkg-config` 需 `PKG_CONFIG_LIBDIR` 指向该目录。
  RPM 族用 `dnf install pkg(aarch64)`/`--archno` 风格不同，别混用命令。
- 打包元数据即契约：deb 的 `Depends`（soname 由 shlibs/dh_makeshlibs 生成）、rpm 的
  `Requires`/自动依赖（`%{_requires}`、`find-requires`）。SONAME 变更必须同步包名或 epoch。
- 版本锁定与可复现：镜像构建禁 `latest`；apt 用 `apt-get install pkg=1.2.3-1`，
  dnf 用 `dnf install pkg-1.2.3`，apk 用 `pkg=1.2.3-r0`；并记录 `dpkg -l`/`rpm -qa` 快照。

## 坑位

- Alpine（musl）上二进制直接跑 glibc 编译产物会 `not found`（实为缺 interpreter），
  要么重编 musl 版，要么换 `gcr.io/distroless`/Debian slim 基础镜像。
- `systemd` 在容器/WSL 里可能不是 PID1，`apt` 触发 `systemctl` 会失败：用
  `policy-rc.d`/`invoke-rc.d` 屏蔽或 `--no-install-recommends` 避开。
- 源里 `contrib`/`non-free`/`crb`/`EPEL` 未启用导致「包不存在」，先 `apt-cache policy` /
  `dnf repolist` 再下结论。
- 时间/语言包：`tzdata`、`locales`/`glibc-locales` 缺失会让程序回退 UTC 或 C locale，
  精简镜像里是高发故障。

## 取证命令

`grep -E '^(ID|ID_LIKE|VERSION_ID)=' /etc/os-release`、`apt-cache policy <pkg>`、
`dnf repoquery --whatprovides '*/foo.h'`、`apk info -a | head`、`dpkg -L <pkg>`、`rpm -ql <pkg>`

出处：[`references/工具链与打包.md`](../../references/工具链与打包.md)
