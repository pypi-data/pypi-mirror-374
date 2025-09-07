"""打包运行时环境."""

import logging
import shutil
import time

from packaging.specifiers import SpecifierSet
from packaging.version import parse

from fspacker.exceptions import ProjectPackError
from fspacker.packers._base import BasePacker
from fspacker.settings import get_settings
from fspacker.utils.checksum import calc_checksum
from fspacker.utils.url import safe_read_url_data

logger = logging.getLogger(__name__)


class RuntimePacker(BasePacker):
    NAME = "运行时打包"

    def pack(self) -> None:
        if (self.info.runtime_dir / "python.exe").exists():
            logger.warning(
                "目标文件夹 [[purple]runtime[/]] 已存在, "
                "跳过 [bold green]:heavy_check_mark:",
            )
            return

        specs = SpecifierSet(self.info.python_specifiers)
        if parse(self.info.min_python_version) not in specs:
            logger.error(
                f"当前环境python版本: [green bold]"
                f"{self.info.min_python_version}[/], 与项目要求"
                f"[green bold]{self.info.python_specifiers}[/] 不匹配",
            )

        if self.info.embed_filepath.exists():
            logger.info("找到本地 [green bold]embed 压缩包")

            if not get_settings().mode.offline:
                logger.info(
                    f"非离线模式, 检查校验和: [green underline]"
                    f"{self.info.embed_filepath.name}"
                    " [bold green]:heavy_check_mark:",
                )
                src_checksum = get_settings().dirs.checksum
                dst_checksum = calc_checksum(self.info.embed_filepath)

                if src_checksum == dst_checksum:
                    logger.info(
                        "校验和一致, 使用[bold green] "
                        "本地运行时 :heavy_check_mark:",
                    )
                else:
                    logger.info("校验和不一致, 重新下载")
                    self._fetch_runtime()
        elif not get_settings().mode.offline:
            logger.info("非离线模式, 获取运行时")
            self._fetch_runtime()
        else:
            msg = f"离线模式且本地运行时不存在, {self.info.embed_filepath}"
            raise ProjectPackError(msg)

        try:
            shutil.unpack_archive(
                self.info.embed_filepath,
                self.info.runtime_dir,
                "zip",
            )
        except shutil.ReadError:
            logger.exception(
                f"解压文件失败: [red underline]"
                f"{self.info.embed_filepath.name}[/]. "
                f"[bold red]:white_exclamation_mark:",
            )
            logger.info(
                f"删除损坏的文件: [red underline]{self.info.embed_filepath}",
            )
            self.info.embed_filepath.unlink(missing_ok=True)
            msg = "请重新打包项目"
            raise ProjectPackError(msg) from None
        else:
            logger.info(
                f"解压 runtime 文件成功: [green underline]"
                f"{self.info.embed_filepath.name} -> "
                f"{self.info.runtime_dir.relative_to(self.info.project_dir)}"
                f"[/] [bold green]:heavy_check_mark:",
            )

    def _fetch_runtime(self) -> None:
        fastest_embed_url = get_settings().urls.fastest_embed_url
        archive_url = f"{fastest_embed_url}{self.info.min_python_version}/{self.info.embed_filename}"  # noqa: E501

        if not archive_url.startswith("https://"):
            logger.error(f"url无效: {archive_url}")
            return

        content = safe_read_url_data(archive_url)
        if content is None:
            logger.error("下载运行时失败")
            return

        logger.info(f"从地址下载运行时: [[green bold]{archive_url}[/]]")
        t0 = time.perf_counter()

        if not get_settings().dirs.embed.exists():
            get_settings().dirs.embed.mkdir(parents=True)

        with self.info.embed_filepath.open("wb") as f:
            f.write(content)

        download_time = time.perf_counter() - t0
        logger.info(f"下载完成, 用时: [green bold]{download_time:.2f}s")

        checksum = calc_checksum(self.info.embed_filepath)
        logger.info(f"更新校验和 [{checksum}]")
        get_settings().dirs.checksum = checksum
