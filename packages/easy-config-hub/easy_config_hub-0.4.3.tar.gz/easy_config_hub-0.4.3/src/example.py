import multiprocessing
import time
from easy_config_hub.config import MainConfigBase, ConfigBase
from easy_config_hub.directories_config import StdDirConfigBase, DirConfigBase
from easy_config_hub.enums_config import EnumsConfig, En, a
from easy_config_hub.setting import Setting, VersionSetting, RangeSetting, Level, SettingType

t = time.perf_counter()
class Config_(MainConfigBase):
    version = Setting[str]("0.0.1-alpha", "Version", level=Level.USER | Level.READ_ONLY)
    dev_mode = Setting[bool](True, "Dev Mode", level=Level.USER)
    debug_mode = Setting[bool](True, "Debug Mode", level=Level.USER_DEV)

    class Downloading(ConfigBase):
        max_retries = Setting[int](3, "Maximum Download Retries")
        min_wait_time = Setting[int](1, "Minimum Time between Retries")
        
        class Chapter(ConfigBase):
            time_wait_before_loading = Setting[int](300, "Time to Wait before Attempting to Download Chapter", 'ms')
        
        class Image(ConfigBase):
            convert_image = Setting[bool](True, "Convert Image")
            preferable_format = Setting[str]("WEBP", "Converted Images Format")

            max_threads = Setting[int](multiprocessing.cpu_count(), "Max Download Threads")
            # chunk_size = Setting[StorageSize](
            #     8 * SU.KB, "Image chunk size", strongly_typed=False
            # )
            image_update_every = Setting[int](
                10, "Image Update Percentage", "%"
            )  # After image downloaded image_update_every% of size, update

            PIL_SUPPORTED_EXT = Setting[dict[str, str]](
                {
                    "JPG": "JPEG",
                    "JPEG": "JPEG",
                    "PNG": "PNG",
                    "GIF": "GIF",
                    "BMP": "BMP",
                    "WEBP": "WEBP",
                    "ICO": "ICO",
                    "TIFF": "TIFF",
                    "TIF": "TIFF",
                },
                "Formats that PIL supports",
            )

    class UI(ConfigBase):
        class Scrolling(ConfigBase):
            step = Setting[int](
                150, "Step", "px", setting_type=SettingType.COSMETIC | SettingType.QOL
            )
            step_duration = Setting[int](
                200, "Step Duration", "ms", setting_type=SettingType.COSMETIC | SettingType.QOL
            )
            alt_multiplier = Setting[int](8, "Alt Step Multiplier", setting_type=SettingType.QOL)

            scale_multiplier = Setting[float](
                1.5,
                "Step Scale Multiplier",
                level=Level.DEVELOPER,
                setting_type=SettingType.PERFORMANCE,
            )

        class MangaViewer(ConfigBase):
            debug_gap = Setting[int](5, unit='px')
            
    class Performance(ConfigBase):
        class MangaViewer(ConfigBase):
            cull_height_multiplier = Setting[float](
                2.0,
                "Cull Viewport Height Multiplier",
                level=Level.USER | Level.ADVANCED,
                setting_type=SettingType.PERFORMANCE | SettingType.COSMETIC,
            )
            default_strip_height = Setting[int](256)
            
            min_strip_height = Setting[int](128)
            max_strip_height = Setting[int](2048)
            detection_confidence_threshold = Setting[float](.8)
            strip_mode = Setting[str]('adaptive')
            
            gutter_threshold = Setting[float](.8)
            min_gutter_height = Setting[int](10)
            

    class Caching(ConfigBase):
        class Image(ConfigBase): ...
            # max_ram = Setting[StorageSize](00 * SU.MB, "Max Ram for Images")
            # max_disc = Setting[StorageSize](500 * SU.MB, "Max Disc Space for Images")
            
    class DataProcessing(ConfigBase):
        class UrlParsing(ConfigBase):
            replace_symbols = Setting[dict[str, str]]({
                ' ': '-',
                "'": '',
            })

    class Dirs(StdDirConfigBase):
        """=== CONFIGS ==="""
        class CONF(DirConfigBase):
            JSON = "config.json"
            NOVELS = "novels"

        """=== LOGS ==="""
        LOGS = 'logs'

        """=== CACHE ==="""
        class CACHE(DirConfigBase):
            IMAGES = "images"

        """=== DATA ==="""
        class DATA(DirConfigBase):
            DATA = "data"

            class NOVELS(DirConfigBase):
                DRAFT = "draft.md"
            class MANGA(DirConfigBase): ...
            class STATE(DirConfigBase): ...

            NOVELS_JSON = "novels.json"
            MANGA_JSON = "manga.json"
            SITES_JSON = "sites.json"

        """=== RESOURCES ==="""
        class RESOURCES(DirConfigBase):
            ICONS = "icons"
            IMAGES = "img"
            BACKGROUNDS = "background"

Config = Config_('./setting.json')
Config.save()
print(Config.Dirs.DATA.NOVELS / 'sdkfj')
print(time.perf_counter() - t)