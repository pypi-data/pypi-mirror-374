from __future__ import annotations
from typing import Any, List, Dict, Type, TypeVar, Union, Optional,Callable
import typing,platform,os
from .devices import *
from ..core.exception import *



_T = TypeVar("_T")
_RT = TypeVar("_RT")
_F = TypeVar("_F", bound=Callable[..., Any])

class sharemethod(type):
    def __get__(self, obj, cls):
        self.__owner__ = obj if obj else cls
        return self

    def __call__(self, *args) -> Any:
        return self.__fget__.__get__(self.__owner__)(*args)  # type: ignore

    def __set_name__(self, owner, name):
        self.__owner__ = owner

    def __new__(cls: Type[_T], func: _F) -> Type[_F]:

        clsName = func.__class__.__name__
        bases = func.__class__.__bases__
        attrs = func.__dict__
        # attrs = dict(func.__class__.__dict__)
        result = super().__new__(cls, clsName, bases, attrs)
        result.__fget__ = func

        return result

class BaseAPIMetaClass(BaseMetaClass):
    """Super high level tactic metaclass"""

    def __new__(
        cls: Type[_T], clsName: str, bases: Tuple[type], attrs: Dict[str, Any]
    ) -> _T:

        result = super().__new__(cls, clsName, bases, attrs)
        result._clsMakePID()  # type: ignore
        result.__str__ = BaseAPIMetaClass.__str__  # type: ignore

        return result

    @sharemethod
    def __str__(glob) -> str:

        if isinstance(glob, type):
            cls = glob
            result = f"{cls.__name__} {{\n"
        else:
            cls = glob.__class__
            result = f"{cls.__name__}() = {{\n"

        for attr, val in glob.__dict__.items():

            if (
                attr.startswith(f"_{cls.__base__.__name__}__")
                or attr.startswith(f"_{cls.__name__}__")
                or attr.startswith("__")
                and attr.endswith("__")
                or type(val) == classmethod
                or callable(val)
            ):
                continue

            result += f"    {attr}: {val}\n"

        return result + "}"


class DeviceData(object, metaclass=BaseAPIMetaClass):
    """
    Device configuration to connect to `TelegramClient` and `TDesktop`

    ### Attributes:
        api_id (`int`):
            [API_ID](https://core.telegram.org/api/obtaining_api_id#obtaining-api-id)

        api_hash (`str`):
            [API_HASH](https://core.telegram.org/api/obtaining_api_id#obtaining-api-id)

        device_model (`str`):
            Device model name

        system_version (`str`):
            Operating System version

        app_version (`str`):
            Current app version

        lang_code (`str`):
            Language code of the client

        system_lang_code (`str`):
            Language code of operating system

        lang_pack (`str`):
            Language pack

    ### Methods:
        `Generate()`: Generate random device model and system version
    """

    CustomInitConnectionList: List[Union[Type[DeviceData], DeviceData]] = []

    api_id: int = None  # type: ignore
    api_hash: str = None  # type: ignore
    device_model: str = None  # type: ignore
    system_version: str = None  # type: ignore
    app_version: str = None  # type: ignore
    lang_code: str = None  # type: ignore
    system_lang_code: str = None  # type: ignore
    lang_pack: str = None  # type: ignore

    @typing.overload
    def __init__(self, api_id: int, api_hash: str) -> None:
        pass

    @typing.overload
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        device_model: str = None,
        system_version: str = None,
        app_version: str = None,
        lang_code: str = None,
        system_lang_code: str = None,
        lang_pack: str = None,
    ) -> None:
        """
        Create your own customized Device

        ### Arguments:
            api_id (`int`):
                [API_ID](https://core.telegram.org/api/obtaining_api_id#obtaining-api-id)

            api_hash (`str`):
                [API_HASH](https://core.telegram.org/api/obtaining_api_id#obtaining-api-id)

            device_model (`str`, default=`None`):
                `[Device model name](Device.device_model)`

            system_version (`str`, default=`None`):
                `[Operating System version](Device.system_version)`

            app_version (`str`, default=`None`):
                `[Current app version](Device.app_version)`

            lang_code (`str`, default=`"en"`):
                `[Language code of the client](Device.app_version)`

            system_lang_code (`str`, default=`"en"`):
                `[Language code of operating system](Device.system_lang_code)`

            lang_pack (`str`, default=`""`):
                `[Language pack](Device.lang_pack)`

        ### Warning:
            Use at your own risk!:
                Using the wrong Device can lead to your account banned.
                If the session was created using an official Device, you must continue using official APIs for that session.
                Otherwise that account is at risk of getting banned.
        """

    def __init__(
        self,
        api_id: int = None,
        api_hash: str = None,
        device_model: str = None,
        system_version: str = None,
        app_version: str = None,
        lang_code: str = None,
        system_lang_code: str = None,
        lang_pack: str = None,
    ) -> None:

        Expects(
            (self.__class__ != DeviceData) or (api_id != None and api_hash != None),
            NoInstanceMatched("No instace of Device matches the arguments"),
        )

        cls = self.get_cls()

        self.api_id = api_id if api_id else cls.api_id
        self.api_hash = api_hash if api_hash else cls.api_hash
        self.device_model = device_model if device_model else cls.device_model
        self.system_version = system_version if system_version else cls.system_version
        self.app_version = app_version if app_version else cls.app_version
        self.system_lang_code = (
            system_lang_code if system_lang_code else cls.system_lang_code
        )
        self.lang_pack = lang_pack if lang_pack else cls.lang_pack
        self.lang_code = lang_code if lang_code else cls.lang_code

        if self.device_model == None:
            system = platform.uname()

            if system.machine in ("x86_64", "AMD64"):
                self.device_model = "PC 64bit"
            elif system.machine in ("i386", "i686", "x86"):
                self.device_model = "PC 32bit"
            else:
                self.device_model = system.machine

        self._makePID()

    @sharemethod
    def copy(glob: Union[Type[_T], _T] = _T) -> _T:  # type: ignore

        cls = glob if isinstance(glob, type) else glob.__class__

        return cls(
            glob.api_id,  # type: ignore
            glob.api_hash,  # type: ignore
            glob.device_model,  # type: ignore
            glob.system_version,  # type: ignore
            glob.app_version,  # type: ignore
            glob.lang_code,  # type: ignore
            glob.system_lang_code,  # type: ignore
            glob.lang_pack,  # type: ignore
        )  # type: ignore

    @sharemethod
    def get_cls(glob: Union[Type[_T], _T]) -> Type[_T]:  # type: ignore
        return glob if isinstance(glob, type) else glob.__class__

    @sharemethod
    def destroy(glob: Union[Type[_T], _T]):  # type: ignore
        if isinstance(glob, type):
            return

        # might cause conflict, disabled for now, it won"t be a problem
        # if (Device.findData(self.pid) != None):
        #     Device.CustomInitConnectionList.remove(self)

    def __eq__(self, __o: DeviceData) -> bool:
        if not isinstance(__o, DeviceData):
            return False
        return self.pid == __o.pid

    def __del__(self):
        self.destroy()

    @classmethod
    def _makePIDEnsure(cls) -> int:
        while True:
            pid = int.from_bytes(os.urandom(8), "little")
            if cls.findData(pid) == None:
                break
        return pid

    @classmethod
    def _clsMakePID(cls: Type[DeviceData]):
        cls.pid = cls._makePIDEnsure()
        cls.CustomInitConnectionList.append(cls)

    def _makePID(self):
        self.pid = self.get_cls()._makePIDEnsure()
        self.get_cls().CustomInitConnectionList.append(self)

    @classmethod
    def Generate(cls: Type[_T], unique_id: str = None) -> _T:
        """
        Generate random device model and system version

        ### Arguments:
            unique_id (`str`, default=`None`):
                The unique ID to generate - can be anything.\\
                This will be used to ensure that it will generate the same data everytime.\\
                If not set then the data will be randomized each time we runs it.
        
        ### Raises:
            `NotImplementedError`: Not supported for web browser yet

        ### Returns:
            `DeviceData`: Return a copy of the api with random device data

        ### Examples:
            Create a `TelegramClient` with custom Device:
        ```python
            api = Device.TelegramIOS.Generate(unique_id="new.session")
            client = TelegramClient(session="new.session" api=api)
            client.start()
        ```
        """
        if cls == Device.TelegramAndroid or cls == Device.TelegramAndroidX:
            deviceInfo = AndroidDevice.RandomDevice(unique_id)

        elif cls == Device.TelegramIOS:
            deviceInfo = iOSDeivce.RandomDevice(unique_id)

        elif cls == Device.TelegramMacOS or cls == Device.TelegramMacosDesktop:
            deviceInfo = macOSDevice.RandomDevice(unique_id)

        elif cls == Device.TelegramWindows:
            deviceInfo = WindowsDevice.RandomDevice(unique_id)
        
        elif cls == Device.TelegramLinux:
            deviceInfo = LinuxDevice.RandomDevice(unique_id)
        # elif cls == Device.TelegramWeb_K or cls == Device.TelegramWeb_Z or cls == Device.Webogram:
        else:
            raise NotImplementedError(
                f"{cls.__name__} device not supported for randomize yet"
            )

        return cls(device_model=deviceInfo.model, system_version=deviceInfo.version)

    @classmethod
    def findData(cls: Type[_T], pid: int) -> Optional[_T]:
        for x in cls.CustomInitConnectionList:  # type: ignore
            if x.pid == pid:
                return x
        return None


class Device(BaseObject):
    """
    #### Built-in templates for Telegram Device
    - **`opentele`** offers the ability to use **`official APIs`**, which are used by `official apps`.
    - According to [Telegram TOS](https://core.telegram.org/api/obtaining_api_id#using-the-api-id): *all accounts that sign up or log in using unofficial Telegram Device clients are automatically put under observation to avoid violations of the Terms of Service*.
    - It also uses the **[lang_pack](https://core.telegram.org/method/initConnection)** parameter, of which [telethon can't use](https://github.com/LonamiWebs/Telethon/blob/master/telethon/_client/telegrambaseclient.py#L192) because it's for official apps only.
    - Therefore, **there are no differences** between using `opentele` and `official apps`, the server can't tell you apart.
    - You can use `TelegramClient.PrintSessions()` to check this out.

    ### Attributes:
        TelegramDesktop (`Device`):
            Official Telegram for Desktop (Windows, macOS and Linux) [View on GitHub](https://github.com/telegramdesktop/tdesktop)

        TelegramAndroid (`Device`):
            Official Telegram for Android [View on GitHub](https://github.com/DrKLO/Telegram)

        TelegramAndroidX (`Device`):
            Official TelegramX for Android [View on GitHub](https://github.com/DrKLO/Telegram)

        TelegramIOS (`Device`):
            Official Telegram for iOS [View on GitHub](https://github.com/TelegramMessenger/Telegram-iOS)

        TelegramMacOS (`Device`):
            Official Telegram-Swift For MacOS [View on GitHub](https://github.com/overtake/TelegramSwift)

        TelegramWeb_Z (`Device`):
            Default Official Telegram Web Z For Browsers [View on GitHub](https://github.com/Ajaxy/telegram-tt) | [Visit on Telegram](https://web.telegram.org/z/)

        TelegramWeb_K (`Device`):
            Official Telegram Web K For Browsers [View on GitHub](https://github.com/morethanwords/tweb) | [Visit on Telegram](https://web.telegram.org/k/)

        Webogram (`Device`):
            Old Telegram For Browsers [View on GitHub](https://github.com/zhukov/webogram) | [Vist on Telegram](https://web.telegram.org/?legacy=1#/im)
    """

    
    
    
    
    
    class TelegramWindows(DeviceData):
        """
        Official Telegram for Desktop Windows
        [View on GitHub](https://github.com/telegramdesktop/tdesktop)

        ### Attributes:
            api_id (`int`)           : `2040`
            api_hash (`str`)         : `"b18441a1ff607e10a989891a5462e627"`
            device_model (`str`)     : `"Desktop"`
            system_version (`str`)   : `"Windows 11"`
            app_version (`str`)      : `"5.4.1 x64"`
            lang_code (`str`)        : `"en"`
            system_lang_code (`str`) : `"en-US"`
            lang_pack (`str`)        : `"tdesktop"`

        ### Methods:
            `Generate()`: Generate random device data for `Windows`, `macOS` and `Linux`
        """

        api_id = 2040
        api_hash = "b18441a1ff607e10a989891a5462e627"
        device_model = "Z370P D3-CF"
        system_version = "Windows 11"
        app_version = "5.4.1 x64"
        lang_code = "en"
        system_lang_code = "en-US"
        lang_pack = "tdesktop"

    class TelegramLinux(DeviceData):
        """
        Official Telegram for Desktop  Linux
        [View on GitHub](https://github.com/telegramdesktop/tdesktop)

        ### Attributes:
            api_id (`int`)           : `2040`
            api_hash (`str`)         : `"b18441a1ff607e10a989891a5462e627"`
            device_model (`str`)     : `"PRIME Z490-V"`
            system_version (`str`)   : `"Linux ubuntu X11 glibc 2.32"`
            app_version (`str`)      : `"5.4.1 x64"`
            lang_code (`str`)        : `"en"`
            system_lang_code (`str`) : `"en-US"`
            lang_pack (`str`)        : `"tdesktop"`

        ### Methods:
            `Generate()`: Generate random device data for `Linux`
        """

        api_id          = 2040
        api_hash        = 'b18441a1ff607e10a989891a5462e627'
        device_model    = 'PRIME Z490-V'
        system_version  = 'Linux ubuntu X11 glibc 2.32'
        app_version     = '5.4.1 x64'
        system_lang_code= 'en-US'
        lang_pack       = 'tdesktop'
        lang_code       = 'en'
 
    class TelegramMacosDesktop(DeviceData):
        """
        Official Telegram for Desktop  Macos
        [View on GitHub](https://github.com/telegramdesktop/tdesktop)

        ### Attributes:
            api_id (`int`)           : `2040`
            api_hash (`str`)         : `"b18441a1ff607e10a989891a5462e627"`
            device_model (`str`)     : `"PRIME Z490-V"`
            system_version (`str`)   : `"Linux ubuntu X11 glibc 2.32"`
            app_version (`str`)      : `"5.4.1 x64"`
            lang_code (`str`)        : `"en"`
            system_lang_code (`str`) : `"en-US"`
            lang_pack (`str`)        : `"tdesktop"`

        ### Methods:
            `Generate()`: Generate random device data for `Linux`
        """

        api_id          = 2040
        api_hash        = 'b18441a1ff607e10a989891a5462e627'
        device_model    = 'MacBook'
        system_version  = 'macOS 11.5.1'
        app_version     = '5.4.1 x64'
        system_lang_code= 'en-US'
        lang_pack       = 'tdesktop'
        lang_code       = 'en'
 
    
    

    class TelegramAndroid(DeviceData):
        """
        Official Telegram for Android
        [View on GitHub](https://github.com/DrKLO/Telegram)

        ### Attributes:
            api_id (`int`)           : `6`
            api_hash (`str`)         : `"eb06d4abfb49dc3eeb1aeb98ae0f581e"`
            device_model (`str`)     : `"Samsung SM-G998B"`
            system_version (`str`)   : `"SDK 31"`
            app_version (`str`)      : `"11.13.3 (6081)"`
            lang_code (`str`)        : `"en"`
            system_lang_code (`str`) : `"en-US"`
            lang_pack (`str`)        : `"android"`
        """

        api_id = 6
        api_hash = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
        device_model = "Samsung SM-S926B/DS"
        system_version = "SDK 31"
        app_version = "11.13.3 (6081)"
        lang_code = "en"
        system_lang_code = "en-US"
        lang_pack = "android"

    class TelegramAndroidX(DeviceData):
        """
        Official TelegramX for Android
        [View on GitHub](https://github.com/DrKLO/Telegram)

        ### Attributes:
            api_id (`int`)           : `21724`
            api_hash (`str`)         : `"3e0cb5efcd52300aec5994fdfc5bdc16"`
            device_model (`str`)     : `"Samsung SM-G998B"`
            system_version (`str`)   : `"SDK 31"`
            app_version (`str`)      : `"0.27.10.1752-arm64-v8a"`
            lang_code (`str`)        : `"en"`
            system_lang_code (`str`) : `"en-US"`
            lang_pack (`str`)        : `"android"`
        """

        api_id = 21724
        api_hash = "3e0cb5efcd52300aec5994fdfc5bdc16"
        device_model = "Samsung SM-G998B"
        system_version = "SDK 31"
        app_version = "0.27.10.1752-arm64-v8a"
        lang_code = "en"
        system_lang_code = "en-US"
        lang_pack = "android"

    class TelegramIOS(DeviceData):
        """
        Official Telegram for iOS
        [View on GitHub](https://github.com/TelegramMessenger/Telegram-iOS)

        ### Attributes:
            api_id (`int`)           : `10840`
            api_hash (`str`)         : `"33c45224029d59cb3ad0c16134215aeb"`
            device_model (`str`)     : `"iPhone 13 Pro Max"`
            system_version (`str`)   : `"14.8.1"`
            app_version (`str`)      : `"8.4"`
            lang_code (`str`)        : `"en"`
            system_lang_code (`str`) : `"en-US"`
            lang_pack (`str`)        : `"ios"`
        """

        # api_id           = 8
        # api_hash         = "7245de8e747a0d6fbe11f7cc14fcc0bb"
        api_id = 10840
        api_hash = "33c45224029d59cb3ad0c16134215aeb"
        device_model = "iPhone 13 Pro Max"
        system_version = "14.8.1"
        app_version = "8.4"
        lang_code = "en"
        system_lang_code = "en-US"
        lang_pack = "ios"

    class TelegramMacOS(DeviceData):
        """
        Official Telegram-Swift For MacOS
        [View on GitHub](https://github.com/overtake/TelegramSwift)

        ### Attributes:
            api_id (`int`)           : `2834`
            api_hash (`str`)         : `"68875f756c9b437a8b916ca3de215815"`
            device_model (`str`)     : `"MacBook Pro"`
            system_version (`str`)   : `"macOS 12.0.1"`
            app_version (`str`)      : `"8.4"`
            lang_code (`str`)        : `"en"`
            system_lang_code (`str`) : `"en-US"`
            lang_pack (`str`)        : `"macos"`
        """

        api_id = 2834
        api_hash = "68875f756c9b437a8b916ca3de215815"
        # api_id = 9                                    |
        # api_hash = "3975f648bb682ee889f35483bc618d1c" | Telegram for macOS uses this api, but it"s unofficial api, why?
        device_model = "MacBook Pro"
        system_version = "macOS 12.0.1"
        app_version = "8.4"
        lang_code = "en"
        system_lang_code = "en-US"
        lang_pack = "macos"
    
        







