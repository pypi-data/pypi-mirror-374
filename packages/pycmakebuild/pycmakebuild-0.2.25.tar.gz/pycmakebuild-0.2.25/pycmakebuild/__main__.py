def main():
    from .api import PyCMakeBuild, BuildType
    from pathlib import Path
    import argparse

    parser = argparse.ArgumentParser(
        description="pycmakebuild - 批量构建CMake工程的Python工具",
        prog="pycmakebuild",
    )
    parser.add_argument(
        "--env", type=str, default=".env", help="指定环境变量文件，默认为.env"
    )
    parser.add_argument(
        "--build",
        type=str,
        nargs="?",
        const="Release",
        default=None,
        choices=["Debug", "Release"],
        help="根据 build.json 批量构建，支持 --build=Debug 或 --build=Release，默认Release",
    )
    parser.add_argument(
        "--json",
        type=str,
        default="build.json",
        help="指定配置json文件，默认为build.json",
    )
    parser.add_argument(
        "--init", action="store_true", help="初始化环境(.env)和 build.json 模板"
    )
    parser.add_argument(
        "--clean", action="store_true", help="清理所有项目的源代码（git）"
    )
    parser.add_argument("--version", "-v", action="store_true", help="显示版本号")

    parser.add_argument(
        "--emcmake", action="store_true", help="使用emcmake前缀调用CMake（适用于Emscripten编译）"
    )
    # argparse自带--help/-h
    args = parser.parse_args()

    try:
        if args.version:
            PyCMakeBuild.print_version()
            return
        if args.init:
            PyCMakeBuild.init_envs()
            return
        if args.clean:
            PyCMakeBuild(Path(args.env), Path(args.json)).update_git_source()
            return
        if args.build:
            PyCMakeBuild(Path(args.env), Path(args.json)).build(BuildType[args.build], emcmake=args.emcmake)
        else:
            PyCMakeBuild(Path(args.env), Path(args.json)).build(BuildType["Release"], emcmake=args.emcmake)
    except Exception as e:
        print(f"错误: {e}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
