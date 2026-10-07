# 检查清单 · elf-abi-dynamic-linking

## 符号与库解析

- [ ] `ldd -r` 无 `undefined symbol`，无 `not a dynamic executable` 误判
- [ ] 实际解析路径与预期一致（`LD_DEBUG=libs` 或 `ldd -v`），无宿主库串味
- [ ] `DT_SONAME` 存在且与文件名规则一致；`SONAME` 变更已同步包名/epoch
- [ ] 依赖库的搜索路径来源明确：`ld.so.conf.d` / `RUNPATH` / 环境变量（生产禁环境变量方案）

## ABI 兼容

- [ ] 最高需求 glibc 版本已提取（`objdump -T | grep -o 'GLIBC_[0-9.]*' | sort -V | tail`）
  并 ≤ 目标机 `ldd --version`
- [ ] C++ 侧确认 `_GLIBCXX_USE_CXX11_ABI` 与 `GLIBCXX_x` 需求一致；跨编译器接口用 C ABI
- [ ] 导出符号受控（`-fvisibility=hidden` + 显式导出 / version script），内部符号不外泄
- [ ] 破坏性变更（结构体布局、虚表、内联函数、枚举）已识别并给出兼容策略

## 链接形态

- [ ] 静态/动态/musl 的选择有理由；`-static` 下 NSS、DNS、locale 动态加载风险已排除
- [ ] `-fPIC`（库）与 `-fPIE -pie`（可执行）配置正确，无重定位报错
- [ ] 安全加固成对：`-z relro,-z now`、`--build-id`、stack canary、`FORTIFY_SOURCE` 已核对
  （`readelf -d` 看 `BIND_NOW`，`checksec` 或 `readelf -l` 看 GNU_RELRO）
- [ ] `rpath` vs `runpath` 选定并说明传递性差异；部署包内路径用 `$ORIGIN` 且经 `patchelf` 验证

## 交付

- [ ] 未 strip 的调试符号或独立 debuginfo 保留（`build-id` 对应），core 可回溯
- [ ] 目标机上跑过 `--version`/冒烟测试，非仅本机通过
- [ ] 体积与启动耗时变化有前后对比数据
