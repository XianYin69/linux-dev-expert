# dependence（薄技能依赖声明）

本技能是**薄技能**：只声明依赖与调用方式，**不复制他技能正文**。机读清单
[`deps.json`](deps.json)（每条必附 `source_url`，校验 `python scripts/deps_check.py`）。

## 技能依赖（local://）

| 名称 | 何时转派 | 调用方式 |
|---|---|---|
| c-expert | C 语言语义、UB、预处理与严格别名 | `skill c-expert <诉求>` |
| cpp-expert | C++ 所有权/模板/RAII/并发库选型 | `skill cpp-expert <诉求>` |
| python-expert | Linux 上 Python 侧实现与打包 | `skill python-expert <诉求>` |
| concurrency-design | 锁层级、无锁结构、内存序架构设计 | `skill concurrency-design <诉求>` |
| database-management | 存储引擎、迁移、备份与查询优化 | `skill database-management <诉求>` |
| interface-design-expert | TUI/GUI 之外的界面与交互设计判断 | `skill interface-design-expert <诉求>` |
| code-guidelines | 提交前规范审查、命名与复杂度红线 | `skill code-guidelines <诉求>` |

## 软件依赖（system）

| 名称 | 用途 | 探测 |
|---|---|---|
| git | 版本控制与功能分支工作流 | `git --version` |
| bash | 脚本执行与 POSIX 差异对照 | `bash --version` |
| GCC | 编译、sanitizer、LTO | `gcc --version` |
| CMake | 配置与交叉编译 toolchain 文件 | `cmake --version` |

## 边界

- 本技能不修改上述任何技能目录；挂接（把它们指回本技能）由调用方统一做。
- 依赖缺失时降级：给「缺失影响 + 可复现安装命令（按发行版族）」，不得静默跳过。
- 新增依赖须同步 `deps.json` 并跑 `deps_check.py`，缺 `source_url` 即判不合格。
