from src.easy_config_hub import ConfigBase, Setting, Level
import pytest


@pytest.fixture
def Config():
    class Config_(ConfigBase):
        version = Setting[str]('0.1.0', 'Version', level=Level.USER | Level.READ_ONLY)
        dev_mode = Setting[bool](True, 'Dev Mode', level=Level.USER)
        debug_mode = Setting[bool](True, 'Debug Mode', level=Level.USER_DEV)
        
        class ImageDownloading(ConfigBase):
            convert_image = Setting[bool](True, 'Convert Image')
            preferable_format = Setting[str]('WEBP', 'Converted Images Format')
    
    return Config_()

def test_config_init():
    class Config_(ConfigBase):
        setting = Setting[str]('difj')
    assert isinstance(Config_(), ConfigBase)
    
def test_nested_config_init(Config):
    assert isinstance(Config, ConfigBase)
    
