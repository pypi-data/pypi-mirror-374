# pycmakebuild

Python CMake 批量构建与自动化工具，支持通过 build.json 配置文件和命令行批量编译多个 CMake 项目，适用于跨平台 C++/第三方库工程的自动化批量编译。

## 功能特性
- 支持 build.json 配置批量管理和编译多个 CMake 项目
- 支持 Debug/Release 等多种构建类型，支持自定义 CMakeLists.txt 子目录
- 支持命令行一键初始化环境、生成模板、批量构建
- 自动推断 CMake 构建参数，兼容 Windows/Linux/Mac
- 支持通过 `python -m pycmakebuild` 或 `pycmakebuild` 命令行调用
- 支持变量替换和内置变量（如 workspace）
- 内置 git 检查，确保 git 环境可用
- 支持 CMake 前缀路径配置

## 快速开始

### 1. 安装
```bash
pip install pycmakebuild
```


### 2. 初始化环境和模板
```bash
python -m pycmakebuild --init
```
将在当前目录生成 .env 和 build.json 模板。

### 3. 编辑 build.json
示例：
```json
{
  "vars": {
    "QT_DIR": "C:/Qt/5.15.2/msvc2019",
    "MY_INSTALL_PATH": "{workspace}/install"
  },
  "sources": [
    {
      "path": "../Log4Qt",
      "name": "log4qt",
      "cmakelists_subpath": ".",
      "cmake_prefix_path": [
        "{QT_DIR}/lib"
      ],
      "other_build_params": [
        "-DCUSTOM_OPTION=ON",
        "-DINSTALL_DIR={MY_INSTALL_PATH}"
      ]
    }
  ]
}
```

**配置说明：**
- `vars`: 自定义变量字典，支持变量替换（使用 `{变量名}` 语法）
- `path`: CMake 项目源码路径，支持变量替换
- `name`: 目标名称（安装目录名）
- `cmakelists_subpath`: CMakeLists.txt 所在子目录（可选，默认"."）
- `cmake_prefix_path`: CMake 前缀路径列表，支持变量替换（可选）
- `other_build_params`: 传递给 cmake 的额外参数列表，支持变量替换（可选）

**内置变量：**
- `workspace`: 当前命令行执行路径（自动添加）

### 4. 批量构建
编译Release版本
```bash
python -m pycmakebuild
```
或编译Debug版本
```bash
python -m pycmakebuild --build=Debug
```
或指定配置文件
```bash
python -m pycmakebuild --build=Release --json mybuild.json
```
会自动检测指定json并批量构建所有配置项目，支持自定义 cmake 参数。

### 5. 批量更新源码（git工程）
```bash
python -m pycmakebuild --clean
```
更新所有 build.json 中配置的项目源码，并清理构建和安装目录。
**注意：** 此操作需要 git 环境，工具会自动检查 git 是否安装。


## 变量系统

pycmakebuild 支持强大的变量替换功能：

### 变量定义
在 build.json 的 `vars` 字段中定义自定义变量：
```json
{
  "vars": {
    "QT_DIR": "C:/Qt/5.15.2/msvc2019",
    "BOOST_ROOT": "C:/boost_1_76_0",
    "OUTPUT_DIR": "{workspace}/output"
  }
}
```

### 变量使用
在配置的任何字符串字段中使用 `{变量名}` 语法：
```json
{
  "sources": [
    {
      "path": "{BOOST_ROOT}/libs/filesystem",
      "cmake_prefix_path": [
        "{QT_DIR}/lib",
        "{BOOST_ROOT}/stage/lib"
      ],
      "other_build_params": [
        "-DOUTPUT_DIRECTORY={OUTPUT_DIR}"
      ]
    }
  ]
}
```

### 内置变量
- `workspace`: 当前命令行执行的工作目录路径（自动添加）


## 环境变量加载与自定义

pycmakebuild 内置环境变量解析，不依赖第三方库，且不会污染系统环境变量。

**环境变量文件格式**：

```
INSTALL_PATH=xxx   # 安装根目录
GENERATOR=xxx      # CMake生成器，如 Ninja、Visual Studio 17 2022 等
ARCH=x64           # 架构，可选 x64/Win32/arm64
BUILD_DIR=build    # 构建输出目录
CORES=32           # 并发核心数
```

**自定义 env 文件**：

可通过 `--env=xxx.env` 指定任意环境变量文件，所有变量仅在 pycmakebuild 内部生效，不影响系统环境。

**示例**：

```shell
pycmakebuild --build=Release --env=myenvfile.env
```

如未指定，默认加载当前目录下的 `.env` 文件。

## Git 源码管理

工具内置 git 支持，用于源码更新和清理：

- **自动检查**: 执行 git 操作前自动检查 git 是否安装
- **智能清理**: 清理工作区、重置更改、更新子模块
- **安全操作**: 在执行 git 操作前验证目录有效性

**清理操作包括：**
1. 清理构建目录和安装目录
2. `git clean -fdx` - 清理未跟踪文件
3. `git checkout .` - 重置工作区更改
4. `git submodule` 递归清理和重置
5. `git pull` - 拉取最新代码
6. `git submodule update --init --recursive` - 更新子模块

## 命令行参数
- `--init`  初始化环境和 build.json 模板
- `--build [Debug|Release]`  指定构建类型，支持 --build=Debug 或 --build=Release，默认Release
- `--json <file>`  指定配置json文件，默认为build.json
- `--env <file>`  指定环境变量文件，默认为.env
- `--clean` 清理所有 build.json 配置的项目源码（git clean/pull）
- `--version` 显示版本号


## 依赖
- cmake：Python CMake 封装库

## 更新日志

### v0.2.18
- 新增变量系统，支持在 build.json 中定义和使用自定义变量
- 新增 `cmake_prefix_path` 字段支持，简化依赖库路径配置
- 新增内置变量 `workspace`，自动获取当前工作目录
- 改进 git 检查机制，执行前自动验证 git 环境
- 重构 API 结构，提供更清晰的 `PyCMakeBuild` 类接口
- 增强错误处理和用户提示信息

## 典型应用场景
- 本地一键环境初始化和批量编译 CMake 第三方库
- 跨平台 C++ 项目的自动化构建流程
- 多项目依赖的统一管理和构建
- CI/CD 环境中的批量编译任务

## License
MIT
