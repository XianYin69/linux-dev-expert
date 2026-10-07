# 检查清单 · toolchain-build-cross

## 可复现构建

- [ ] 编译器/构建器版本入文档并入库（`cc --version`、`cmake --version` 输出快照）
- [ ] 干净构建通过（`rm -rf build && configure && build`），不依赖残留对象文件
- [ ] 警告基线生效（`-Wall -Wextra -Werror` + 追加项），新增警告数为 0
- [ ] 构建产物与本机架构/目标架构一致（`file`、`readelf -h` 的 Machine 字段）

## 依赖发现

- [ ] `pkg-config --cflags --libs <mod>` 解析路径正确，交叉时 `PKG_CONFIG_SYSROOT_DIR` 已设
- [ ] 头文件与库来自同一 sysroot，无宿主 `/usr/include` 泄漏（`gcc -E -v` 搜索路径核对）
- [ ] 可选依赖的开关与降级路径明确，缺失时报错信息可指导安装（含发行版族命令）

## 并行与资源

- [ ] `-j` 取值与 cgroup CPU 限额匹配（`nproc` vs `cpu.max`），容器内无 OOM
- [ ] 长编译有内存上限策略（模板重货拆分、`--param ggc-min-expand` 或降并行）

## sanitizer 与测试

- [ ] ASan/UBSan 构建通过并跑过测试集；LSan 泄漏报告为 0 或有豁免说明
- [ ] sanitizer 的编译与链接 flag 成对给出，依赖库同样插桩（TSan 尤其）
- [ ] Release（`-O2`）与 Debug 都跑过测试，优化期 UB 未被漏掉

## 交叉与 CI

- [ ] toolchain 文件 / meson native file 入库，三元组与 sysroot 路径可移植（无绝对个人路径）
- [ ] 目标架构测试有执行载体（qemu-user、真实板子、CI runner），非仅交叉编译成功
- [ ] 构建耗时与产物体积的前后对比数据留档
