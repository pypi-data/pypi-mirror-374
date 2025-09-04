import multiprocessing
from config import Config
from directories_config import DirectoriesConfig
from setting import Setting, Level, SettingType


class AppConfig(Config):
    version = Setting[str]('0.1.0', 'Version', level=Level.USER | Level.READ_ONLY)
    dev_mode = Setting[bool](True, 'Dev Mode', level=Level.USER)
    debug_mode = Setting[bool](True, 'Debug Mode', level=Level.USER_DEV)
    
    class ImageDownloading(Config):
        convert_image = Setting[bool](True, 'Convert Image')
        preferable_format = Setting[str]('WEBP', 'Converted Images Format')
        
        max_threads = Setting[int](multiprocessing.cpu_count(), 'Max Download Threads')
        image_update_every = Setting[int](10, 'Image Update Percentage', '%')
        
        
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
        }, 'Formats that PIL supports')
        
    class UI(Config):
        class MangaViewer(Config):
            image_loading_intervals = Setting[int](100, 'Load Images in UI with Intervals', 'ms')
            placeholder_loading_intervals = Setting[int](5, 'Load Placeholders in UI with Intervals', 'ms')
            
            set_size_with_every_placeholder = Setting[bool](True, 'Set MangaViewer\'s Scene Size with Every Placeholder Added', level=Level.USER | Level.ADVANCED)
            cull_height_multiplier = Setting[float](2.0, 'Cull Viewport Height Multiplier', level=Level.USER | Level.ADVANCED, type_=SettingType.PERFORMANCE | SettingType.COSMETIC)
            cull_scene_cooldown = Setting[int](250, 'Scene Culling Minimum Cooldown', 'ms', level=Level.USER | Level.ADVANCED, type_=SettingType.PERFORMANCE)
        
    class Scrolling(Config):
        step = Setting[int](150, 'Step', 'px', type_=SettingType.COSMETIC | SettingType.QOL)
        step_duration = Setting[int](200, 'Step Duration', 'ms', type_=SettingType.COSMETIC | SettingType.QOL)
        alt_multiplier = Setting[int](8, 'Alt Step Multiplier', type_=SettingType.QOL)
        
        scale_multiplier = Setting[float](1.5, 'Step Scale Multiplier', level=Level.DEVELOPER, type_=SettingType.PERFORMANCE)
        
    class Dirs(DirectoriesConfig):
        STD_DIR = DirectoriesConfig.STD_DIR
        
        IMG = STD_DIR / 'images'
        CACHE = STD_DIR / 'cache'