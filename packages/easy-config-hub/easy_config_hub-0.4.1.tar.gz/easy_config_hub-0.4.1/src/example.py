import multiprocessing
import time
from easy_config_hub.config import MainConfigBase, ConfigBase
from easy_config_hub.directories_config import StdDirConfigBase, DirConfigBase
from easy_config_hub.enums_config import EnumsConfig, En, a
from easy_config_hub.setting import Setting, VersionSetting, RangeSetting, Level, SettingType

t = time.perf_counter()
class Config_(MainConfigBase):
    version = VersionSetting(0, 1, 0, 'alpha', name='Version', level=Level.USER | Level.READ_ONLY)
    dev_mode = Setting[bool](True, 'Dev Mode', level=Level.USER)
    debug_mode = Setting[bool](True, 'Debug Mode', level=Level.USER_DEV)
    
    class ImageDownloading(ConfigBase):
        convert_image = Setting[bool](True, 'Convert Image')
        preferable_format = Setting[str]('JXL', 'Converted Images Format')
        
        max_threads = RangeSetting[int](1, multiprocessing.cpu_count(), 1, multiprocessing.cpu_count(), 'Max Download Threads', set_to_closes_if_out_of_bounds=True)
        image_update_every = RangeSetting[int](5, 100, 5, 10, 'Image Update Percentage', '%')
        
        
        PIL_SUPPORTED_EXT = Setting[dict[str, str]]({
            'JPG':  'JPEG',
            'JPEG': 'JPEG',
            'PNG':  'PNG',
            'GIF':  'GIF',
            'BMP':  'BMP',
            'WEBP': 'WEBP',
            'ICO':  'ICO',
            'TIFF': 'TIFF',
            'TIF':  'TIFF'
        }, 'Formats that PIL supports', level=Level.READ_ONLY)
        
    class UI(ConfigBase):
        class MangaViewer(ConfigBase):
            cull_height_multiplier = RangeSetting[float](1, 10, .1, 2, 'Cull Viewport Height Multiplier', level=Level.USER | Level.ADVANCED, setting_type=SettingType.PERFORMANCE | SettingType.COSMETIC, strongly_typed=False)
            cull_scene_cooldown = Setting[int](250, 'Scene Culling Minimum Cooldown', 'ms', level=Level.USER | Level.ADVANCED, setting_type=SettingType.PERFORMANCE)
        
    class Scrolling(ConfigBase):
        step = RangeSetting[int](10, 500, 20, 150, 'Step', 'px', setting_type=SettingType.COSMETIC | SettingType.QOL)
        step_duration = Setting[int](200, 'Step Duration', 'ms', setting_type=SettingType.COSMETIC | SettingType.QOL)
        alt_multiplier = Setting[int](8, 'Alt Step Multiplier', setting_type=SettingType.QOL)
        
        scale_multiplier = Setting[float](1.5, 'Step Scale Multiplier', level=Level.DEVELOPER, setting_type=SettingType.PERFORMANCE)
        
    class Dirs(StdDirConfigBase):
        STD_DIR = StdDirConfigBase.STD_DIR
        
        IMG = 'images'
        LOL = 'lol/kek/s.json'
        
        class CACHE(DirConfigBase):
            JSON = 'cache.json'
            
    class Enums(EnumsConfig):
        class Foo(En):
            BAR = a()
            BAR2 = a()

Config = Config_('./setting.json')
Config.save()
print(Config.ImageDownloading.max_threads())
print(time.perf_counter() - t)