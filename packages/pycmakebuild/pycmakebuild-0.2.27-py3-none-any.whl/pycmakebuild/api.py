from cmake import CMAKE_BIN_DIR
from enum import Enum
from pathlib import Path
import os
import sys
import json
import subprocess


class BuildType(Enum):
    """构建类型枚举

    Args:
        Enum (_type_): _description_
    """

    # Debug模式
    Debug = "Debug"
    # Release模式
    Release = "Release"


class Source(object):
    """源代码信息

    Args:
        object (_type_): _description_
    """

    def __init__(
        self,
        path: str,
        name: str,
        cmakelists_subpath: str,
        cmake_prefix_path: list,
        other_build_params: list,
        vars: dict,
    ):
        self.path: Path = Path(self.replace_string_by_vars(path, vars))
        self.name: str = name
        self.cmakelists_subpath: str = cmakelists_subpath
        self.cmake_prefix_path: list = self.replace_string_array_by_vars(cmake_prefix_path, vars)
        self.other_build_params: list = self.replace_string_array_by_vars(other_build_params, vars)

    def replace_string_by_vars(self, text: str, vars_dict: dict) -> str:
        """替换字符串中的变量

        Args:
            text (str): 需要替换的字符串
            vars_dict (dict): 变量字典

        Returns:
            str: 替换后的字符串
        """
        _text = text
        for k, v in vars_dict.items():
            _text = _text.replace(f"${{{k}}}", v)
        return _text

    def replace_string_array_by_vars(self, texts: list, vars_dict: dict) -> list:
        """替换字符串数组中的变量

        Args:
            texts (list): 需要替换的字符串数组
            vars_dict (dict): 变量字典

        Returns:
            list: 替换后的字符串数组
        """
        return [self.replace_string_by_vars(text, vars_dict) for text in texts]


class PyCMakeBuild(object):
    def __init__(self, env_path: Path, build_json_path: Path):
        # 检测环境变量文件
        if not env_path.exists():
            raise Exception(
                f"""未找到.env文件({env_path.absolute().as_posix()})或加载环境变量失败.
使用pycmakebuild --init进行初始化
使用pycmakebuild --help查看帮助信息。"""
            )

        if not build_json_path.exists():
            raise Exception(
                f"""未找到{build_json_path}
请先执行pycmakebuild --init初始化或指定正确的json文件。"""
            )

        # 环境变量
        envs = {}
        with open(env_path.absolute().as_posix(), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    envs[k.strip()] = v.strip()
        print(f"加载环境变量文件{env_path.absolute().as_posix()}完成。")

        install_path = envs.get("INSTALL_PATH")  # 安装路径
        if install_path is None or len(install_path) == 0:
            raise Exception("未设置安装路径INSTALL_PATH")
        else:
            print(f"[安装路径]:INSTALL_PATH={install_path}")
            self.__install_path: Path = Path(install_path).absolute()

        generator = envs.get("GENERATOR")  # 生成器
        if generator is None or len(generator) == 0:
            raise Exception("未设置生成器环境变量GENERATOR")
        else:
            print(f"[生 成 器]:GENERATOR={generator}")
            self.__generator: str = generator

        arch = envs.get("ARCH")  # 架构
        if arch is None or len(arch) == 0:
            raise Exception("未设置架构环境变量ARCH")
        else:
            print(f"[架    构]:ARCH={arch}")
            self.__arch: str = arch
            self.__cmake_arch: str = self._guess_cmake_arch()
            if len(self.__cmake_arch) > 0:
                print(f"[CMake架构]:{self.__cmake_arch}")

        build_dir = envs.get("BUILD_DIR")
        if build_dir is None or len(build_dir) == 0:
            raise Exception("未设置构建目录环境变量:BUILD_DIR")
        else:
            print(f"[构建目录]:BUILD_DIR={build_dir}")
            self.__build_dir: Path = Path(build_dir).absolute()

        cores = envs.get("CORES")
        try:
            self.__cores: int = int(cores)
            if self.__cores <= 0:
                self.__cores = 32
        except Exception:
            self.__cores: int = 32
        print(f"[核 心 数]:CORES={self.__cores}")

        # 读取构建信息： 变量字典 和 源码列表
        self.__vars: dict = {}
        self.__source_list: list[Source] = []

        self._read_build_infos(build_json_path, self.__vars, self.__source_list)

    @classmethod
    def print_version(cls):
        """打印版本信息"""
        try:
            from importlib.metadata import version
        except ImportError:
            from pkg_resources import get_distribution as version
        try:
            ver = version("pycmakebuild")
        except Exception:
            ver = "(dev)"
        print(f"版本: {ver}")

    def build(self, build_type: BuildType, emcmake: bool = False):
        """
        构建代码

        Args:

        """
        for src in self.__source_list:
            self._build_and_install(
                project_path=src.path,
                name=src.name,
                build_type=build_type,
                cmakelists_subpath=src.cmakelists_subpath,
                cmake_prefix_path=src.cmake_prefix_path,
                other_build_params=src.other_build_params,
                emcmake=emcmake
            )

    @classmethod
    def init_envs(cls):
        """初始化环境变量和构建配置"""
        cls._init_env_file()
        cls._init_build_json()
        print("环境初始化完成!")

    def update_git_source(self) -> bool:
        """更新指定路径的Git源码

        Args:
            src_dir (Path): 源码目录

        Returns:
            bool: 更新是否成功
        """
        # 检查git是否安装
        import shutil

        try:
            if os.path.exists(self.__install_path.absolute().as_posix()):
                print(f"清理安装路径:{self.__install_path.absolute().as_posix()}...")
                shutil.rmtree(self.__install_path.absolute().as_posix())
            if os.path.exists(self.__build_dir.absolute().as_posix()):
                print(f"清理构建路径:{self.__build_dir.absolute().as_posix()}...")
                shutil.rmtree(self.__build_dir.absolute().as_posix())

            if not shutil.which("git"):
                print("错误: 系统中未安装git或git不在PATH环境变量中")
                return False

            for src in self.__source_list:
                print(f"更新源码工程:{src.path.absolute().as_posix()}...")
                self._execute_cmd("git clean -fdx", cwd=src.path.absolute().as_posix())
                self._execute_cmd("git checkout .", cwd=src.path.absolute().as_posix())
                self._execute_cmd(
                    "git submodule foreach --recursive git clean -fdx",
                    cwd=src.path.absolute().as_posix(),
                )
                self._execute_cmd(
                    "git submodule foreach --recursive git checkout .",
                    cwd=src.path.absolute().as_posix(),
                )
                self._execute_cmd("git pull", cwd=src.path.absolute().as_posix())
                self._execute_cmd(
                    "git submodule update --init --recursive",
                    cwd=src.path.absolute().as_posix(),
                )
                print(f"更新源码工程{src.path.absolute().as_posix()}成功!")
            return True
        except Exception as e:
            print(f"更新源码工程失败: {e}")
            return False

    def _guess_cmake_arch(self) -> str:
        """根据平台、CMake生成器和架构自动推断CMake的-A参数，仅在Windows+Visual Studio下生效。

        Args:
            gen (str): CMake生成器
            arch (str): 架构

        Returns:
            str: -A参数字符串，如果不适用则返回空字符串
        """
        if not sys.platform.startswith("win"):
            return ""

        if "visual studio" in self.__generator.lower():
            if self.__arch in ["x86", "win32"]:
                return "-A Win32"
            elif self.__arch in ["x64", "amd64"]:
                return "-A x64"
            elif self.__arch in ["arm64"]:
                return "-A ARM64"
        return ""

    def _build_and_install(
        self,
        project_path: Path,
        name: str,
        other_build_params: list,
        cmakelists_subpath: str,
        cmake_prefix_path: list,
        build_type: BuildType,
        emcmake: bool = False,
    ) -> bool:
        """
        编译并安装指定的CMake工程。

        Args:
            project_path (Path): CMake工程的路径。
            name (str): 工程名称。
            other_build_params (list): 其他CMake构建参数。
            cmakelists_subpath (str): CMakeLists.txt的子目录(相对路径)。
            build_type (BuildType): 构建类型。
            emcmake (bool): 是否使用emcmake前缀。

        Returns:
            bool: 如果编译和安装成功返回True，否则返回False。
        """
        source_path = project_path
        if len(cmakelists_subpath) > 0:
            # 工程CMakeLists.txt所在的子目录
            print(f"[子 目 录]:CMakeLists.txt所在{cmakelists_subpath}")
            source_path = source_path.joinpath(cmakelists_subpath)

        if not source_path.exists():
            raise Exception(f"源码目录不存在:{source_path.absolute().as_posix()}")

        if len(name) == 0:
            raise Exception("库名称为空")

        abs_source_path = source_path.absolute().as_posix()
        print(f"====================开始编译源码:{name}====================")
        print(f"[源码路径]:{abs_source_path}")

        install_full_path = Path(self.__install_path)
        install_full_path = install_full_path.joinpath(self.__arch)
        install_full_path = install_full_path.joinpath(build_type.value)
        install_full_path = install_full_path.joinpath(name + ("_wasm" if emcmake else ""))
        print(f"[编译信息]:{name}/{build_type.value}")

        print(f"[工程路径]:{abs_source_path}")
        print(f"[安装路径]:{install_full_path.absolute().as_posix()}")
        if not install_full_path.exists():
            print(f"新建安装路径:{install_full_path.absolute().as_posix()}")
            os.makedirs(install_full_path.absolute().as_posix())

        build_full_dir = (
            f"{self.__build_dir}/{name}/build{"_wasm" if emcmake else ""}_{self.__arch}_{build_type.value}"
        )
        print(f"[临时路径]:{build_full_dir}")
        if not os.path.exists(build_full_dir):
            print(f"新建临时路径:{build_full_dir}")
            os.makedirs(build_full_dir)

        cmake_prefix = "emcmake " if emcmake else ""
        args = [
            f"-S {abs_source_path}",
            f"-B {build_full_dir}",
            f'-G "{self.__generator}"',
            self.__cmake_arch,
            f"-DCMAKE_BUILD_TYPE={build_type.value}",
            f"-DCMAKE_INSTALL_PREFIX={install_full_path.absolute().as_posix()}",
            self._gen_prefix_list(cmake_prefix_path),
            "  ".join(other_build_params),
        ]
        self._execute_cmd(
            f"{cmake_prefix}{CMAKE_BIN_DIR}/cmake {' '.join(args)}", cwd=abs_source_path
        )
        print(f"配置工程{name}成功!")

        print(f"开始编译工程{name}...")
        args = [
            f"--build {build_full_dir}",
            f"--config {build_type.value}",
            f"-j{self.__cores}",
        ]
        self._execute_cmd(
            f"{CMAKE_BIN_DIR}/cmake {' '.join(args)}", cwd=abs_source_path
        )
        print(f"编译工程{name}成功!")

        print(f"开始安装工程{name}...")
        args = [f"--install {build_full_dir}", f"--config {build_type.value}"]
        self._execute_cmd(
            f"{CMAKE_BIN_DIR}/cmake {' '.join(args)}", cwd=abs_source_path
        )
        print(f"安装工程{name}成功!\n")
        return True

    def _read_build_infos(self, json_path: Path, vars: dict, sources: list):
        vars.clear()
        sources.clear()
        with open(json_path.absolute().as_posix(), "r", encoding="utf-8") as f:
            config = json.load(f)

        vars = config.get("vars", {})
        # 添加workspace变量，值为当前命令行执行路径
        vars["workspace"] = Path.cwd().absolute().as_posix()

        _srcs = config.get("sources", [])
        for s in _srcs:
            s["vars"] = vars
            src = Source(**s)
            sources.append(src)

    @classmethod
    def _init_env_file(cls):
        """
        初始化环境变量文件 .env
        """
        pwd_dir = Path.cwd()
        full_env_path = pwd_dir.joinpath(".env").absolute()
        if not full_env_path.exists():
            envs = []
            envs.append(f"# 安装路径")
            envs.append(f"INSTALL_PATH={pwd_dir.joinpath('libs').absolute()}")
            envs.append(f"# 架构类型 可选值: x86, x64, arm64, amd64, win32, i386, i686")
            # 自动推断架构
            if sys.platform.startswith("win"):
                import platform

                arch = platform.machine().lower()
                if arch in ["amd64", "x86_64"]:
                    envs.append(f"ARCH=x64")
                elif arch in ["x86", "i386", "i686"]:
                    envs.append(f"ARCH=x86")
                elif "arm" in arch:
                    envs.append(f"ARCH=arm64")
                else:
                    envs.append(f"ARCH={arch}")
            else:
                envs.append(f"ARCH=x64")
            envs.append(f"# 构建中间文件夹路径")
            envs.append(f"BUILD_DIR={pwd_dir.joinpath('builds').absolute()}")
            # 自动推断生成器
            generator_comment = "# 可用CMake生成器类型(自动检测):"
            try:
                import subprocess

                result = subprocess.run(
                    ["cmake", "-G"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                )
                lines = (
                    result.stderr.splitlines()
                    if result.stderr
                    else result.stdout.splitlines()
                )
                gen_lines = []
                found = False
                last_line = None
                for line in lines:
                    if "Generators" in line:
                        found = True
                        continue
                    if found:
                        if not line.strip():
                            break
                        # 过滤掉(deprecated)相关行
                        if "(deprecated)" in line:
                            continue
                        # 合并多行描述
                        if last_line is not None and (
                            line.startswith("    ") or line.startswith("\t")
                        ):
                            # 上一行是生成器名，这一行是描述，合并
                            gen_lines[-1] += " " + line.strip()
                            last_line = gen_lines[-1]
                        else:
                            gen_lines.append(line.strip())
                            last_line = gen_lines[-1]
                if gen_lines:
                    generator_comment += "\n" + "\n".join(
                        [f"#   {l}" for l in gen_lines]
                    )
            except Exception as e:
                generator_comment += f" (获取失败: {e})"
            envs.append(generator_comment)
            if sys.platform.startswith("win"):
                import shutil

                # 优先检测 vswhere
                vswhere = shutil.which("vswhere")
                envs.append(f"# CMake生成器类型")
                if vswhere:
                    envs.append(f"GENERATOR=Visual Studio 16 2019")
                elif shutil.which("ninja"):
                    envs.append(f"GENERATOR=Ninja")
                else:
                    envs.append(f"GENERATOR=Visual Studio 16 2019")
            else:
                import shutil

                if os.path.exists("/usr/bin/ninja") or shutil.which("ninja"):
                    envs.append(f"GENERATOR=Ninja")
                else:
                    envs.append(f"GENERATOR=Unix Makefiles")
            envs.append(f"# 默认编译核心数")
            envs.append(f"CORES=32")

            with open(full_env_path.absolute().as_posix(), "w", encoding="utf-8") as f:
                f.write("\n".join(envs))
                print(f"写入默认.env文件:{full_env_path.absolute().as_posix()}")
        else:
            print(f"文件已存在:{full_env_path.absolute().as_posix()}")

    @classmethod
    def _init_build_json(cls):
        """初始化构建配置文件 build.json

        build.json格式：
        vars: 变量列表
        sources: 源码列表
            path: 源码路径
            name: 源码名称
            cmakelist_subpath: CMakeLists.txt所在子路径
            cmake_prefix_path: CMake前缀路径列表
            other_build_params: 其他构建参数列表
        """
        import json

        pwd_dir = Path.cwd()
        build_json_path = pwd_dir.joinpath("build.json")
        if not build_json_path.exists():
            build_json = {
                "vars": {},
                "sources": [
                    {
                        "path": "test",
                        "name": "test",
                        "cmakelists_subpath": ".",
                        "cmake_prefix_path": [],
                        "other_build_params": [],
                    }
                ],
            }
            with open(build_json_path, "w", encoding="utf-8") as f:
                json.dump(build_json, f, indent=2, ensure_ascii=False)
                print(f"写入默认build.json文件:{build_json_path.absolute().as_posix()}")
        else:
            print(f"文件已存在:{build_json_path.absolute().as_posix()}")

    @classmethod
    def _gen_prefix_list(cls, prefixs: list) -> str:
        """
        生成CMake的CMAKE_PREFIX_PATH参数

        Args:
            prefixs (list): 前缀列表

        Returns:
            str: CMAKE_PREFIX_PATH参数字符串
        """

        if len(prefixs) == 0:
            return ""

        return f'''-DCMAKE_PREFIX_PATH="{';'.join(prefixs)}"'''

    @classmethod
    def _clean_screen(cls):
        """清理屏幕"""
        import sys

        if sys.platform == "win32":
            cls._execute_cmd("cls")
        else:
            cls._execute_cmd("clear")

    @classmethod
    def _execute_cmd(cls, cmd: str, cwd: str = ""):
        """执行命令

        Args:
            cmd (str): 要执行的命令
            cwd (str, optional): 命令执行的工作目录. Defaults to "".

        Raises:
            Exception: 命令执行失败
        """

        print(f"执行命令: {cmd}, 工作目录: {cwd}")

        pro = subprocess.run(
            cmd,
            shell=True,
            encoding=("gb2312" if sys.platform == "win32" else "utf-8"),
            text=True,
            check=True,
            cwd=cwd,
        )
        if pro.returncode != 0:
            cls._clean_screen()
            print(f"命令执行失败: {cmd}")
            if pro.stderr:
                raise Exception(f"错误信息: {pro.stderr.strip()}")
