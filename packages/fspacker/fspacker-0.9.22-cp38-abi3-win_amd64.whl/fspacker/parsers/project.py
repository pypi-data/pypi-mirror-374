"""Config file parser for project, support poetry and PEP621 format.

Usage example:
    >>> from fspacker.parsers.project import Project
    >>> from pathlib import Path
    >>> project = Project(Path("."))
    >>> project.name
    'fspacker'
    >>> project.python_specifiers
    '>=3.8'
    >>> project.authors
    [{'name': 'gooker_young', 'email': 'gooker_young@qq.com'}]
    >>> project.description
    'Fast & Simple Packer toolset for python.'
"""

from __future__ import annotations

import ast
import logging
import platform
import re
import sys
from functools import cached_property
from pathlib import Path

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import parse

from fspacker.compat import tomllib
from fspacker.exceptions import ProjectParseError
from fspacker.settings import get_settings

__all__ = ["Project"]


logger = logging.getLogger(__name__)


class Project:
    """项目构建信息."""

    # 忽视清单
    IGNORE_ENTRIES = frozenset([
        "dist-info",
        "site-packages",
        "runtime",
        "dist",
    ])

    def __init__(self, project_dir: Path) -> None:
        # project name
        self.name = ""

        if not project_dir or not project_dir.is_dir():
            msg = f"Invalid project directory: {project_dir}"
            raise ProjectParseError(msg)

        # project directory
        self.project_dir: Path = project_dir

        # python specifiers
        self.python_specifiers = ""

        # project version
        self.version: str = ""

        # project metadata
        self.authors: list[str] = []
        self.description: str = ""
        self.license: str = ""
        self.source_file: Path | None = None
        self.dependencies: list[str] = []

        # Imported modules parsed from source file
        self.ast_modules: set[str] = set()

        # Project data
        self.data: dict = {}

        self._parse()

    def __repr__(self) -> str:
        """字符串表示.

        Returns:
            str: 项目名称.
        """
        return f"[green bold]{self.name}[/]"

    def _parse(self) -> None:
        """解析项目目录下的 pyproject.toml 文件, 获取项目信息."""
        self._parse_config()
        self._parse_source()
        self._parse_ast()
        self._parse_dependencies()

    @property
    def dist_dir(self) -> Path:
        """打包目录."""
        return self.project_dir / "dist"

    @property
    def dest_src_dir(self) -> Path:
        """目标源代码目录."""
        if self.is_normal_project:
            return self.dist_dir / "src" / self.normalized_name
        return self.dist_dir / "src"

    @property
    def license_file(self) -> Path | None:
        """LICENSE 文件路径."""
        pattern = re.compile(r"^(LICENSE|COPYING)(?:\..+)?$")
        for file in self.project_dir.glob("*"):
            if pattern.match(file.name):
                return file

        return None

    @property
    def runtime_dir(self) -> Path:
        """运行时目录."""
        return self.dist_dir / "runtime"

    @property
    def exe_file(self) -> Path:
        """可执行文件."""
        return self.dist_dir / f"{self.normalized_name}.exe"

    @cached_property
    def min_python_version(self) -> str:
        """Calculate the minimum Python version.

        Returns:
            str: minimum Python version.
        """
        specifiers = SpecifierSet(self.python_specifiers)

        # Find all matching specifiers with `>=` or `>`
        min_versions = [
            specifier.version
            for specifier in specifiers
            if specifier.operator in {">=", ">"}
        ]

        if min_versions:
            # Find the minimum version
            min_version = min(parse(v) for v in min_versions)
            # Return version with three parts (major.minor.patch)
            version_parts = str(min_version).split(".")

            # If we have a full version specified, return as is
            if len(version_parts) >= 3:  # noqa: PLR2004
                return ".".join(version_parts[:3])

            # If we have only major.minor, map to latest patch version
            if len(version_parts) == 2:  # noqa: PLR2004
                major, minor = version_parts[0], version_parts[1]
                # Mapping of Python versions to their latest patch versions
                latest_patches = {
                    # Python 3.6.x
                    "3.6": "3.6.8",  # Last officially supported version
                    # Python 3.7.x
                    "3.7": "3.7.9",
                    # Python 3.8.x
                    "3.8": "3.8.10",
                    # Python 3.9.x
                    "3.9": "3.9.5",
                    # Python 3.10.x
                    "3.10": "3.10.11",
                    # Python 3.11.x
                    "3.11": "3.11.9",
                    # Python 3.12.x
                    "3.12": "3.12.10",
                    # Python 3.13.x
                    "3.13": "3.13.5",
                }

                version_key = f"{major}.{minor}"
                if version_key in latest_patches:
                    return latest_patches[version_key]
                # Default to x.x.0 if not in our mapping
                return f"{major}.{minor}.0"

            # If we only have major version, pad with zeros
            if len(version_parts) == 1:
                return f"{version_parts[0]}.0.0"

        # If not found, use the default minimum version
        return "3.8.10"

    @cached_property
    def embed_filename(self) -> str:
        """嵌入文件名."""
        machine_code = platform.machine().lower()
        return f"python-{self.min_python_version}-embed-{machine_code}.zip"

    @cached_property
    def embed_filepath(self) -> Path:
        """嵌入文件路径."""
        return get_settings().dirs.embed / self.embed_filename

    @property
    def is_gui(self) -> bool:
        """判断是否为 GUI 项目."""
        if get_settings().mode.gui:
            return True

        return bool(self.ast_modules & get_settings().gui_libs)

    @property
    def is_normal_project(self) -> bool:
        """判断是否为普通项目."""
        return self.normalized_dir is not None and self.normalized_dir.is_dir()

    @property
    def normalized_dir(self) -> Path | None:
        """项目常规目录."""
        return self.project_dir / "src" / self.normalized_name

    @property
    def normalized_name(self) -> str:
        """名称归一化, 替换所有'-'为'_'."""
        return self.name.replace("-", "_")

    def is_valid_entry(self, filepath: Path) -> bool:
        """判断文件是否有效.

        Args:
            filepath: 文件路径.

        Returns:
            是否有效.
        """
        # 检查文件路径中是否包含需要忽略的目录
        if any(x in str(filepath) for x in self.IGNORE_ENTRIES):
            return False

        # 检查文件路径中是否包含需要忽略的文件夹
        if any(
            p.name in get_settings().ignore_folders for p in filepath.parents
        ):
            return False

        # 检查文件名是否以.或_开头
        return not (
            filepath.stem.startswith(".") or filepath.stem.startswith("_")
        )

    def _parse_config(self) -> None:
        """读取配置文件.

        Raises:
            ProjectParseError: 项目配置文件解析错误.
        """
        config_path = self.project_dir / "pyproject.toml"
        if not config_path.is_file():
            msg = f"路径下未找到 pyproject.toml: {self.project_dir}"
            raise ProjectParseError(msg)

        try:
            with config_path.open("rb") as f:
                self.data = tomllib.load(f)
        except tomllib.TOMLDecodeError:
            logger.exception(
                f"TOML解析错误, 路径: [red]{self.project_dir}",
            )
        except Exception:
            logger.exception(
                f"未知错误, 路径: [red]{self.project_dir}",
            )

    def _parse_source(self) -> None:
        """Parse source file."""
        source_files = [
            file
            for file in self.project_dir.rglob("*.py")
            if self.is_valid_entry(file)
        ]

        pattern = re.compile(
            # match `def main` with any parameters including complex ones
            r"(def\s+main\s*\([^)]*(?:\)[^:]*)?:)|"
            # match `if __name__ == '__main__':`
            r'(if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:)',
            flags=re.MULTILINE | re.DOTALL,
        )

        for source_file in source_files:
            with source_file.open(encoding="utf8") as f:
                content = "\n".join(f.readlines())

            matches = pattern.findall(content)
            if len(matches):
                logger.info(
                    f"入口 Python 文件: [[green bold]{source_file}[/]]",
                )
                self.source_file = source_file
                break
        else:
            logger.error("未找到入口 Python 文件")
            return

    def _parse_ast(self) -> None:
        """解析项目导入模块."""
        builtin_modules = set(sys.builtin_module_names)

        for py_file in self.project_dir.rglob("*.py"):
            # 跳过无效目录
            if any(
                p.name in get_settings().ignore_folders for p in py_file.parents
            ):
                continue

            # 解析AST语法树
            with py_file.open("r", encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read())
                except SyntaxError:
                    logger.exception(
                        f"源文件解析语法错误, 文件: [red]{py_file}[/], "
                        f"路径: [red]{self.project_dir}",
                    )
                    continue

            # 遍历Import节点
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split(".", 1)[0]
                        if module.lower() not in builtin_modules:
                            self.ast_modules.add(module)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module.split(".", 1)[0] if node.module else ""
                    if module.lower() not in builtin_modules:
                        self.ast_modules.add(module)

    def _parse_dependencies(self) -> None:
        """解析依赖项."""
        if not self.data:
            logger.error(f"项目配置文件解析错误, 路径: [red]{self.project_dir}")
            return

        if "project" in self.data:
            self._parse_pep621(self.data["project"])
        elif "tool" in self.data and "poetry" in self.data["tool"]:
            poetry_data = self.data.get("tool", {}).get("poetry", None)
            self._parse_poetry(poetry_data)
        else:
            logger.error(
                f"pyproject.toml 配置项无效, 路径: [red]{self.project_dir}",
            )

    def _parse_pep621(self, project_data: dict) -> None:
        """解析 PEP 621 格式的 pyproject.toml."""
        if not project_data:
            logger.error(
                f"未找到项目PEP621配置项, 路径: [red]{self.project_dir}",
            )
            return

        # 获取项目基本信息
        self._parse_project_config(project_data)

        self.dependencies = project_data.get("dependencies", [])
        if not isinstance(self.dependencies, list):
            logger.error(
                f"依赖项格式错误: {self.dependencies}, "
                f"路径: [red]{self.project_dir}",
            )

        self.dependencies = [_.lower() for _ in self.dependencies]

    def _parse_poetry(self, project_data: dict) -> None:
        """解析 Poetry 格式的 pyproject.toml."""
        if not project_data:
            logger.error(
                f"未找到项目poetry配置项, 路径: [red]{self.project_dir}",
            )
            return

        # 获取项目基本信息
        self._parse_project_config(project_data)

        dependencies = project_data.get("dependencies", {})

        # 移除python版本声明
        if "python" in dependencies:
            self.python_specifiers = _convert_poetry_specifiers(
                dependencies.get("python"),
            )
            dependencies.pop("python")
        else:
            logger.error(f"未指定python版本, 路径: [red]{self.project_dir}")

        # 处理依赖项
        self.dependencies = _convert_dependencies(dependencies)

    def _parse_project_config(self, project_data: dict) -> None:
        """解析项目配置项."""
        logger.info("解析项目配置项...")
        self._get_config(project_data, "name", "")
        self._get_config(
            project_data,
            "python_specifiers",
            "requires-python",
            "",
        )
        self._get_config(project_data, "version", "version", "")
        self._get_config(project_data, "authors", "authors", "")
        self._get_config(project_data, "description", "description", "")

    def _get_config(
        self,
        data: dict,
        name: str,
        key: str = "",
        default: object | None = None,
    ) -> None:
        """获取项目配置信息.

        Args:
            data (dict): pyproject.toml 配置项
            name (str): 配置项名称
            key (str): 配置项键名
            default (object, optional): 默认值. Defaults to None.
        """
        config_key = key or name
        if config_key and config_key not in data:
            logger.warning(
                f"未设置项目参数: [[red]{config_key}[/]], "
                f"路径: [[red]{self.project_dir}[/]]",
            )
            return

        val = data.get(config_key, default)
        setattr(self, name, val)


def _convert_dependencies(deps: dict) -> list:
    """将 Poetry 的依赖语法转换为 PEP 621 兼容格式.

    Args:
        deps (dict): Poetry 依赖项

    Returns:
        list: PEP 621 兼容格式的依赖项
    """
    converted = []
    for pkg, constraint in deps.items():
        req = Requirement(pkg)
        req.specifier = SpecifierSet(_convert_poetry_specifiers(constraint))
        converted.append(str(req))
    return converted


def _convert_poetry_specifiers(constraint: str) -> str:
    """处理 Poetry 的版本约束符号.

    Args:
        constraint (str): 版本约束符号

    Returns:
        str: PEP 621 兼容版本约束符号
    """
    if constraint.startswith("^"):
        base_version = constraint[1:]
        return f">={base_version},<{_next_major_version(base_version)}"
    if constraint.startswith("~"):
        base_version = constraint[1:]
        return f">={base_version},<{_next_minor_version(base_version)}"
    return constraint  # 直接传递 >=, <= 等标准符号


def _next_major_version(version: str) -> str:
    """计算下一个主版本号.

    如: 1.2.3 → 1.3.0.

    Args:
        version (str): 版本号

    Returns:
        str: 下一个次版本号
    """
    parts = list(map(int, version.split(".")))
    parts[0] += 1
    parts[1:] = [0] * (len(parts) - 1)
    return ".".join(map(str, parts))


def _next_minor_version(version: str) -> str:
    """计算下一个次版本号.

    如: 1.2.3 → 1.3.0.

    Args:
        version (str): 版本号

    Returns:
        str: 下一个次版本号
    """
    parts = list(map(int, version.split(".")))
    if len(parts) < 2:  # noqa: PLR2004
        parts += [0]
    parts[1] += 1
    parts[2:] = [0] * (len(parts) - 2) if len(parts) > 2 else []  # noqa: PLR2004
    return ".".join(map(str, parts))
