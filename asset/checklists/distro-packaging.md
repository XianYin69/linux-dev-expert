# 检查清单 · distro-packaging

## 目标环境判定

- [ ] `/etc/os-release` 的 `ID`/`ID_LIKE`/`VERSION_ID` 已采集，族与包管理器对应关系写明
- [ ] 是否容器/WSL/精简镜像已判定（影响 systemd、locale、tzdata、内核模块可用性）
- [ ] 架构与多架构状态确认（`uname -m`、`dpkg --print-foreign-architectures` / `rpm --eval %{_arch}`）

## 依赖完整性

- [ ] 运行时依赖与构建依赖分开列（`-dev`/`-devel` 只进构建阶段）
- [ ] 每个包名在目标族上验证存在（`apt-cache policy` / `dnf repoquery` / `apk info`）
- [ ] 头文件缺失类问题按「缺 dev 包」排查，未误判为库未装
- [ ] 可选/推荐依赖显式取舍（`--no-install-recommends` 后功能是否受影响已测）

## 安装可复现

- [ ] 非交互安装命令完整（`DEBIAN_FRONTEND=noninteractive`、`-y`、`--no-cache`）
- [ ] 版本锁定写法给出（`pkg=1.2.3-1` / `pkg-1.2.3` / `pkg=1.2.3-r0`），禁 `latest`
- [ ] 源与组件（main/contrib/non-free、EPEL/crb）前置条件写明，附 `repolist` 验证命令
- [ ] 安装后清理与缓存删除在 Dockerfile 同层完成，层体积变化有对比

## 打包交付

- [ ] deb/rpm/APKK 元数据字段核对（`Depends`/`Requires` 由 SONAME 生成，`Provides`/`Conflicts`）
- [ ] 文件清单与 FHS 一致（`/usr/lib/<triplet>`、`/usr/share`、`/etc` 不放可执行）
- [ ] 触发器/脚本片段幂等（`postinst` 重复执行不炸、容器内无 systemctl 调用或已屏蔽）
- [ ] 在干净目标镜像里装过并跑过冒烟测试，非仅在构建机通过

## 差异风险

- [ ] glibc vs musl 差异已评估（DNS、locale、线程栈、静态链接）
- [ ] systemd 依赖型功能在无 init 环境给出替代（脚本 + supervisor / s6 / runit）
