from pathlib import Path
from collections import Counter
from dataclasses import dataclass
import time
import shutil
from argparse import ArgumentParser


DEFAULT_PICS_ROOT_PATH = Path.home() / "matthias_mobile_photos"

DEFAULT_SOURCE_PATH = Path.home() / "Pictures"

PIC_DIR_PREFIX = "pics"

PIC_SUFFIXES = [".HEIC", ".JPG", ".jpg", ".PNG"]

VIDEO_DIR_PREFIX = "videos"

VIDEO_SUFFIXES = [".MOV", ".MP4", ".mp4"]


def get_directory_prefix(path: Path) -> str | None:
    suffix = path.suffix
    if suffix in PIC_SUFFIXES:
        return PIC_DIR_PREFIX
    elif suffix in VIDEO_SUFFIXES:
        return VIDEO_DIR_PREFIX
    else:
        return None


@dataclass(frozen=True)
class MonthAndYear:
    month: int  # 1 is Jan, 12 is Dec
    year: int
    directory_prefix: str
    pics_root_path: Path

    @staticmethod
    def from_path(
        path: Path,
        pics_root_path: Path,
    ) -> "MonthAndYear":
        """
        Creates object from ``path``. Month and year are taken from the last
        modified time of the file, ``directory_prefix`` is determined from the
        suffix.

        :param path: File path
        :param pics_root_path: Member value
        :return: New :class:`MonthAndYear` object
        """
        directory_prefix = get_directory_prefix(path)
        assert directory_prefix is not None, f"{path} has unsupported suffix, must be in {PIC_SUFFIXES + VIDEO_SUFFIXES}"
        gmtime = time.gmtime(path.stat().st_mtime)
        return MonthAndYear(
            month=gmtime.tm_mon,
            year=gmtime.tm_year,
            directory_prefix=directory_prefix,
            pics_root_path=pics_root_path,
        )

    def path_prefix(self) -> Path:
        subdir = self.directory_prefix + f"-{self.month:02d}{self.year % 100:02d}"
        return self.pics_root_path / str(self.year) / subdir


def live_mode_video_path(path: Path) -> Path | None:
    """
    In IPhone live mode, for every picture ``XYZ.HEIC``, there is also a short
    video ``XYZ.MOV``.

    :param path: File path
    :return: Path for short video if ``path`` is for a picture
    """
    if path.suffix == ".HEIC":
        return path.parent / (path.stem + ".MOV")
    else:
        return None


def filter_live_mode_videos(paths: list[Path]) -> list[Path]:
    """
    Remove all live mode video file paths from ``paths``.

    :param paths:
    :return: ``paths`` without live mode video files
    """
    unwanted_paths = set(live_mode_video_path(path) for path in paths)
    if None in unwanted_paths:
        unwanted_paths.remove(None)
    return [path for path in paths if path not in unwanted_paths]


def main(
    source_path: Path,
    pics_root_path: Path,
    skip_live_mode_videos: bool,
):
    allowed_suffixes = set(PIC_SUFFIXES + VIDEO_SUFFIXES)
    paths = [
        path for path in source_path.glob("*")
        if path.is_file() and path.suffix in allowed_suffixes
    ]
    # Filter out live mode videos (optional)
    if skip_live_mode_videos:
        paths = filter_live_mode_videos(paths)

    counter_copied = Counter()
    counter_exist = Counter()
    for src_path in paths:
        month_year = MonthAndYear.from_path(src_path, pics_root_path=pics_root_path)
        trg_prefix = month_year.path_prefix()
        trg_path = trg_prefix / src_path.name
        skip_prefix = len(str(trg_prefix.parents[1])) + 1
        key_counter = str(trg_prefix)[skip_prefix:]
        if trg_path.exists():
            # File already exists. Do not overwrite
            counter_exist.update([key_counter])
        else:
            # Copy file
            trg_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src_path), str(trg_path))
            counter_copied.update([key_counter])

    print("Files copied (or already exist):")
    maxlen = max(len(PIC_DIR_PREFIX), len(VIDEO_DIR_PREFIX)) + 10
    for key in sorted(set(counter_copied).union(counter_exist)):
        num_copied = counter_copied.get(key, 0)
        num_exist = counter_exist.get(key, 0)
        postfix = f" ({num_exist} already exist)" if num_exist > 0 else ""
        print(f"{key:{maxlen}}: {num_copied}" + postfix)


def path_or_default(path_str: str | None, def_path: Path) -> Path:
    return def_path if path_str is None else Path(path_str)


if __name__ == "__main__":
    parser = ArgumentParser(
        description=
            "Copies picture and video files from a source path to target "
            "folders. In IPhone live mode, short videos are stored with "
            "every picture, these are removed by default (but this can be "
            "switched off)."
    )
    parser.add_argument(
        "--src_path",
        type=str,
        default=DEFAULT_SOURCE_PATH,
        help="Source path for picture and video files, as downloaded from phone",
    )
    parser.add_argument(
        "--trg_root",
        type=str,
        default=DEFAULT_PICS_ROOT_PATH,
        help="Root path for folder structure the files are copied to",
    )
    parser.add_argument(
        "--keep_live_mode_videos",
        action="store_true",
        help="By default, XYZ.MOV (live mode video) is skipped if XYZ.HEIC "
             "(picture) is given. If set, live mode videos are copied as well"
    )
    args = parser.parse_args()
    source_path = path_or_default(args.src_path, DEFAULT_SOURCE_PATH)
    pics_root_path = path_or_default(args.trg_root, DEFAULT_PICS_ROOT_PATH)
    main(
        source_path=source_path,
        pics_root_path=pics_root_path,
        skip_live_mode_videos=not args.keep_live_mode_videos,
    )
