from .api import  Device,DeviceData


def select_api(device_name: str):
    api_map = {
        'TelegramAndroid'       : Device.TelegramAndroid,
        'TelegramAndroidX'      : Device.TelegramAndroidX,
        'TelegramWindows'       : Device.TelegramWindows,
        'TelegramIOS'           : Device.TelegramIOS,
        'TelegramLinux'         : Device.TelegramLinux,
        'TelegramMacOS'         : Device.TelegramMacOS,
        'TelegramMacosDesktop'  : Device.TelegramMacosDesktop,
    }

    return api_map.get(device_name, Device.TelegramAndroid)
def update_app_version(device: DeviceData):
    
    default_versions = {
        'tdesktop': '6.1.2 x64',
        'ios': '12.0',
        'macos': '11.15.1'
    }

   
    android_versions = {
        'TelegramAndroidX': "0.27.10.1752-arm64-v8a",
        'TelegramAndroid': '12.0.1 (6166)'
    }

    if device.lang_pack == 'android':
        device.app_version = android_versions.get(device.__class__.__name__, device.app_version)
    else:
        device.app_version = default_versions.get(device.lang_pack, device.app_version)

    return device

