import logging
import platform
import shutil
import string
from pathlib import Path

from fspacker.packers._base import BasePacker
from fspacker.settings import get_settings

logger = logging.getLogger(__name__)

# int file template
INT_TEMPLATE = string.Template(
    """\
import os
import site
import sys
from pathlib import Path

# setup env
cwd = Path.cwd()
site_dirs = [cwd / "site-packages", cwd / "lib"]
dirs = [cwd, cwd / "src", *$DEST_SRC_DIR, cwd / "runtime", *site_dirs]

for dir in dirs:
    sys.path.append(str(dir))

for dir in site_dirs:
    site.addsitedir(str(dir))

# main
from $SRC import main
main()
""",
)

INT_TEMPLATE_QT = string.Template(
    """\
import os
import site
import sys
from pathlib import Path

# setup env
cwd = Path.cwd()
site_dirs = [cwd / "site-packages", cwd / "lib"]
dirs = [cwd, cwd / "src", *$DEST_SRC_DIR, cwd / "runtime", *site_dirs]

for dir in dirs:
    sys.path.append(str(dir))

for dir in site_dirs:
    site.addsitedir(str(dir))

# for qt
import $LIB_NAME
qt_dir = os.path.dirname($LIB_NAME.__file__)
plugin_path = os.path.join(qt_dir, "plugins" , "platforms")
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path

# main
from $SRC import main
main()
""",
)


class EntryPacker(BasePacker):
    NAME = "入口程序打包"

    def pack(self) -> None:
        name = self.info.normalized_name

        if not self.info.source_file or not self.info.source_file.exists():
            logger.error(f"入口文件{self.info.source_file}无效")
            return

        if self.info.is_normal_project:
            source = f"{self.info.normalized_name}.{self.info.source_file.stem}"
            dest_src_dir = f'[cwd / "src" / "{self.info.normalized_name}"]'
        else:
            source = self.info.source_file.stem
            dest_src_dir = "[]"

        ext = ".exe" if platform.system() == "Windows" else ""
        mode = "w" if self.info.is_gui and not get_settings().mode.debug else ""
        exe_filename = f"fsl{mode}{ext}"

        env_filepath = shutil.which(exe_filename)
        if not env_filepath:
            logger.error(f"未找到可执行文件: {exe_filename}")
            return

        logger.debug(f"找到可执行文件: [green underline]{env_filepath}[/]")
        src_exe_path = Path(env_filepath)
        dst_exe_path = self.info.dist_dir / f"{name}.exe"
        logger.info(
            f"打包目标类型: {'[green bold]窗口' if self.info.is_gui else '[red bold]控制台'}[/]",  # noqa: E501
        )
        logger.info(
            f"复制可执行文件: [green underline]{src_exe_path.name} -> "
            f"{dst_exe_path.relative_to(self.info.project_dir)}[/]"
            f"[bold green]:heavy_check_mark:",
        )

        try:
            shutil.copy(src_exe_path, dst_exe_path)
        except OSError:
            logger.exception("复制文件失败.")

        dst_int_path = self.info.dist_dir / f"{name}.int"
        logger.info(
            f"创建 int 文件: [green underline]{name}.int -> "
            f"{dst_int_path.relative_to(self.info.project_dir)}"
            f"[/] [bold green]:heavy_check_mark:",
        )

        for lib_name in get_settings().qt_libs:
            if lib_name in self.info.ast_modules:
                logger.info(f"检测到目标库: {lib_name}")
                content = INT_TEMPLATE_QT.substitute(
                    SRC=f"src.{source}",
                    DEST_SRC_DIR=dest_src_dir,
                    LIB_NAME=lib_name,
                )
                break
        else:
            content = INT_TEMPLATE.substitute(
                SRC=f"src.{source}",
                DEST_SRC_DIR=dest_src_dir,
            )

        with dst_int_path.open("w", encoding="utf-8") as f:
            f.write(content)
