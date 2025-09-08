from __future__ import annotations
from ..storage import Storage ,Account ,or_
import logging
import warnings
from typing import Awaitable
from ..device import DeviceData,Device,select_api,update_app_version


import uuid


from .imports import *
from .extend import *



@extend_override_class
class CustomInitConnectionRequest(functions.InitConnectionRequest):
    def __init__(
        self,
        api_id: int,
        device_model: str,
        system_version: str,
        app_version: str,
        system_lang_code: str,
        lang_pack: str,
        lang_code: str,
        query,
        proxy: TypeInputClientProxy = None,
        params: TypeJSONValue = None,
    ):

        # our hook pass pid as device_model
        data = DeviceData.findData(device_model)  # type: ignore
        if data != None:
            self.api_id = data.api_id
            self.device_model = data.device_model if data.device_model else device_model
            self.system_version = (data.system_version if data.system_version else system_version)
            self.app_version = data.app_version if data.app_version else app_version
            self.system_lang_code = (data.system_lang_code if data.system_lang_code else system_lang_code)
            self.lang_pack = data.lang_pack if data.lang_pack else lang_pack
            self.lang_code = data.lang_code if data.lang_code else lang_code
            data.destroy()
        else:
            self.api_id = api_id
            self.device_model = device_model
            self.system_version = system_version
            self.app_version = app_version
            self.system_lang_code = system_lang_code
            self.lang_pack = lang_pack
            self.lang_code = lang_code

        self.query = query
        self.proxy = proxy
        self.params = params


@extend_class
class TelegramClient(TelethonClient, BaseObject):
    """
    Extended version of [telethon.TelegramClient](https://github.com/LonamiWebs/Telethon/blob/master/telethon/_client/telegramclient.py#L23)

    ### Methods:
        FromTDesktop():
            Create an instance of `TelegramClient` from `TDesktop`.

        ToTDesktop():
            Convert this `TelegramClient` instance to `TDesktop`.

        QRLoginToNewClient():
            Return `True` if logged-in using an `[official Device](Device)`.

        GetSessions():
            Get all logged in sessions.

        GetCurrentSession():
            Get current logged-in session.

        TerminateSession():
            Terminate a specific session.

        TerminateAllSessions():
            Terminate all other sessions.

        PrintSessions():
            Pretty-print all logged-in sessions.

        is_official_app():
            Return `True` if logged-in using an `[official Device](Device)`.

    """
    
    
        
        
       

    @typing.overload
    def __init__(
        self,
        session_id: str,
        device: Union[Type[DeviceData], DeviceData] = None,
        database: Storage = None,
       
        *,
        
        connection: typing.Type[Connection] =ConnectionTcpFull,
        use_ipv6: bool = False,
        proxy: Union[tuple, dict] = None,
        local_addr: Union[str, tuple] = None,
        timeout: int = 10,
        request_retries: int = 5,
        connection_retries: int = 5,
        retry_delay: int = 1,
        auto_reconnect: bool = True,
        sequential_updates: bool = False,
        flood_sleep_threshold: int = 60,
        raise_last_call_error: bool = False,
        lang_code: str = "en",
        system_lang_code: str = "en",
        loop: asyncio.AbstractEventLoop = None,
        base_logger: Union[str, logging.Logger] = None,
        receive_updates: bool = True,
       
    ):
        """
        !skip
        This is the abstract base class for the client. It defines some
        basic stuff like connecting, switching data center, etc, and
        leaves the `__call__` unimplemented.

        ### Arguments:
            session_id (str): 
                Unique string identifying the session.

            device (`Device`, default= 'TelegramAndroid'):
                Use custom api_id and api_hash for better experience.\n
                These arguments will be ignored if it is set in the Device: `api_id`, `api_hash`, `device_model`, `system_version`, `app_version`, `lang_code`, `system_lang_code`
                Import from telum.
                

            database (Storage, optional): 
                Database used for storing account sessions. 
                Defaults to `Storage()`.


            connection (`telethon.network.connection.common.Connection`, default=ConnectionTcpFull):
                The connection instance to be used when creating a new connection
                to the servers. It **must** be a type.

                Defaults to `telethon.network.connection.tcpfull.ConnectionTcpFull`.

            use_ipv6 (`bool`, default=False):
                Whether to connect to the servers through IPv6 or not.
                By default this is `False` as IPv6 support is not
                too widespread yet.

            proxy (`tuple` | `list` | `dict`, default=None):
                An iterable consisting of the proxy info. If `connection` is
                one of `MTProxy`, then it should contain MTProxy credentials:
                ``('hostname', port, 'secret')``. Otherwise, it's meant to store
                function parameters for PySocks, like ``(type, 'hostname', port)``.
                See https://github.com/Anorov/PySocks#usage-1 for more.

            local_addr (`str` | `tuple`, default=None):
                Local host address (and port, optionally) used to bind the socket to locally.
                You only need to use this if you have multiple network cards and
                want to use a specific one.

            timeout (`int` | `float`, default=10):
                The timeout in seconds to be used when connecting.
                This is **not** the timeout to be used when ``await``'ing for
                invoked requests, and you should use ``asyncio.wait`` or
                ``asyncio.wait_for`` for that.

            request_retries (`int` | `None`, default=5):
                How many times a request should be retried. Request are retried
                when Telegram is having internal issues (due to either
                ``errors.ServerError`` or ``errors.RpcCallFailError``),
                when there is a ``errors.FloodWaitError`` less than
                `flood_sleep_threshold`, or when there's a migrate error.

                May take a negative or `None` value for infinite retries, but
                this is not recommended, since some requests can always trigger
                a call fail (such as searching for messages).

            connection_retries (`int` | `None`, default=5):
                How many times the reconnection should retry, either on the
                initial connection or when Telegram disconnects us. May be
                set to a negative or `None` value for infinite retries, but
                this is not recommended, since the program can get stuck in an
                infinite loop.

            retry_delay (`int` | `float`, default=1):
                The delay in seconds to sleep between automatic reconnections.

            auto_reconnect (`bool`, default=True):
                Whether reconnection should be retried `connection_retries`
                times automatically if Telegram disconnects us or not.

            sequential_updates (`bool`, default=False):
                By default every incoming update will create a new task, so
                you can handle several updates in parallel. Some scripts need
                the order in which updates are processed to be sequential, and
                this setting allows them to do so.

                If set to `True`, incoming updates will be put in a queue
                and processed sequentially. This means your event handlers
                should *not* perform long-running operations since new
                updates are put inside of an unbounded queue.

            flood_sleep_threshold (`int` | `float`, default=60):
                The threshold below which the library should automatically
                sleep on flood wait and slow mode wait errors (inclusive). For instance, if a
                ``FloodWaitError`` for 17s occurs and `flood_sleep_threshold`
                is 20s, the library will ``sleep`` automatically. If the error
                was for 21s, it would ``raise FloodWaitError`` instead. Values
                larger than a day (like ``float('inf')``) will be changed to a day.

            raise_last_call_error (`bool`, default=False):
                When Device calls fail in a way that causes Telethon to retry
                automatically, should the RPC error of the last attempt be raised
                instead of a generic ValueError. This is mostly useful for
                detecting when Telegram has internal issues.


            lang_code (`str`, default='en'):
                "Language code" to be sent when creating the initial connection.
                Defaults to ``'en'``.

            system_lang_code (`str`, default='en'):
                "System lang code"  to be sent when creating the initial connection.
                Defaults to `lang_code`.

            loop (`asyncio.AbstractEventLoop`, default=None):
                Asyncio event loop to use. Defaults to `asyncio.get_event_loop()`.
                This argument is ignored.

            base_logger (`str` | `logging.Logger`, default=None):
                Base logger name or instance to use.
                If a `str` is given, it'll be passed to `logging.getLogger()`. If a
                `logging.Logger` is given, it'll be used directly. If something
                else or nothing is given, the default logger will be used.

            receive_updates (`bool`, default=True):
                Whether the client will receive updates or not. By default, updates
                will be received from Telegram as they occur.

                Turning this off means that Telegram will not send updates at all
                so event handlers, conversations, and QR login will not work.
                However, certain scripts don't need updates, so this will reduce
                the amount of bandwidth used.
                
        """
        
        

    @override
    def __init__(
                self,
                session_id: str ,
                device: Union[Type[DeviceData], DeviceData] = None,
                database: Storage = None,
                **kwargs,
                ):
        

        
        if not database:
            database=Storage()
        
        self.database=database
        self.database.delete(conditions=[ Account.status.in_(['',None])])
        account=None
        self._user_id = None
        



        
        if session_id:
            conditions=[or_(Account.session_id==session_id ,Account.phone==session_id)]
            result:List[Account]=self.database.get(limit=1,conditions=conditions) 
            if result:
                account=result[0]
                session_id=account.session_id
                if account.device_name:
                    device=select_api(account.device_name)(
                        api_id=account.api_id,
                        api_hash=account.api_hash,
                        app_version=account.app_version,
                        system_version=account.system_version,
                        device_model=account.device_model
                        
                        )
                    
          
        self._session_id = session_id or generate_unique_session_id()
        
        if isinstance(device, DeviceData) or (isinstance(device, type) and DeviceData.__subclasscheck__(device) and device is not DeviceData):
            api_id = device.api_id
            api_hash = device.api_hash
        else:
            device = Device.TelegramAndroid.Generate()
            api_id = device.api_id
            api_hash = device.api_hash

        
        
       
        kwargs["device_model"] = device.pid


            

        device=update_app_version(device)
        
                    
        
        if account:
            if not account.device_name:
                self.UpdateSession( data={'device_name':device.__class__.__name__},save_session=False)

            self._phone=account.phone
            self.__TelegramClient____init__(StringSession(account.session), api_id, api_hash, **kwargs)
        
        else:

            data={
                "session_id"        : self._session_id,
                "api_id"            : api_id,
                "api_hash"          : api_hash,
                "device_model"      : device.device_model       if device else kwargs.get("device_model"),
                "system_version"    : device.system_version     if device else kwargs.get("system_version"),
                "app_version"       : device.app_version        if device else kwargs.get("app_version"),
                'device_name'       : device.__class__.__name__ if device else None
                }
            
            
            self.database.insert(data)
            
            
            self.__TelegramClient____init__(None, api_id, api_hash, **kwargs)
        
        
        
    
    def account(self, reload=False):
        if hasattr(self, '_account') and self._account and not reload:
            return self._account

        
        result:List[Account] = self.database.get(limit=1, conditions=[Account.session_id == self._session_id])

        if result:
            self._account = result[0]
            return self._account

        return None  # یا raise Exception("Account not found")



    @property
    def UserId(self):
        
        
        return self._self_id if self._self_id else self._user_id

    @UserId.setter
    def UserId(self, id):
        self._user_id = id


    @override
    async def get_me(self, input_peer: bool = False) -> 'typing.Union[types.User, types.InputPeerUser]':
        """
        Gets "me", the current :tl:`User` who is logged in.

        If the user has not logged in yet, this method returns `None`.

        Arguments
            input_peer (`bool`, optional):
                Whether to return the :tl:`InputPeerUser` version or the normal
                :tl:`User`. This can be useful if you just need to know the ID
                of yourself.

        Returns
            Your own :tl:`User`.

        Example
            .. code-block:: python

                me = await client.get_me()
                print(me.username)
        """
        if input_peer and self._mb_entity_cache.self_id:
            return self._mb_entity_cache.get(self._mb_entity_cache.self_id)._as_input_peer()

        try:
            me = (await self(functions.users.GetUsersRequest([types.InputUserSelf()])))[0]
            
            

            if not self._mb_entity_cache.self_id:
                self._mb_entity_cache.set_self_user(me.id, me.bot, me.access_hash)
            
            self.UserId=me.id
            self.UpdateSession(me=me)

            return utils.get_input_peer(me, allow_self=False) if input_peer else me
        except errors.UnauthorizedError:
            self.UpdateSession(data={'status':'INACTIVE'})
            return None
    
    
    
    
    def UpdateSession(self, me: types.User = None, data: dict = None, save_session: bool = True):
        account = self.account()
        
        def clean_phone(phone: str) -> str | None:
            if not phone or not phone.strip():
                return None
            number = phone.strip().replace(" ", "")
            return number if number.startswith("+") else "+" + number
        
        if not account:
            return 
        
        
        data = data if isinstance(data, dict) else {}
        
    
        if data.get("phone"):
            data["phone"] = clean_phone(data["phone"])
        
        
        if save_session:
            data.setdefault("session", StringSession.save(self.session))
            data.setdefault("dc_id", self.session.dc_id)
        
        
        if me:
            data.update({
                "phone": clean_phone(me.phone),
                "user_id": me.id,
                "username": me.username,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "status": "ACTIVE",
                "is_bot": me.bot
            })
        
        
        self.database.update([Account.session_id == account.session_id], data)

   

    
    async def GetSessions(self) -> Optional[types.account.Authorizations]:
        """
        Get all logged-in sessions.

        ### Returns:
            - Return an instance of `Authorizations` on success
        """
        return await self(functions.account.GetAuthorizationsRequest())  # type: ignore

    async def GetCurrentSession(self) -> Optional[types.Authorization]:
        """
        Get current logged-in session.

        ### Returns:
            Return `telethon.types.Authorization` on success.
            Return `None` on failure.
        """
        results = await self.GetSessions()

        return (
            next((auth for auth in results.authorizations if auth.current), None)
            if results != None
            else None
        )

    async def TerminateSession(self, hash: int):
        """
        Terminate a specific session

        ### Arguments:
            hash (`int`):
                The `session`'s hash to terminate

        ### Raises:
            `FreshResetAuthorisationForbiddenError`: You can't log out other `sessions` if less than `24 hours` have passed since you logged on to the `current session`.
            `HashInvalidError`: The provided hash is invalid.
        """

        try:
            await self(functions.account.ResetAuthorizationRequest(hash))

        except errors.FreshResetAuthorisationForbiddenError as e:
            raise errors.FreshResetAuthorisationForbiddenError(
                "You can't logout other sessions if less than 24 hours have passed since you logged on the current session."
            )

        except errors.HashInvalidError as e:
            raise errors.HashInvalidError("The provided hash is invalid.")

    async def TerminateAllSessions(self) -> bool:
        """
        Terminate all other sessions.
        """
        sessions = await self.GetSessions()
        if sessions == None:
            return False

        for ss in sessions.authorizations:
            if not ss.current:
                await self.TerminateSession(ss.hash)

        return True

    async def PrintSessions(self, sessions: types.account.Authorizations = None):
       
        """
        Pretty-print all logged-in sessions.

        ### Arguments:
            sessions (`Authorizations`, default=`None`):
                `Sessions` that return by `GetSessions()`, if `None` then it will `GetSessions()` first.

        ### Returns:
            On success, it should prints the sessions table as the code below.
        ```
            |---------+-----------------------------+----------+----------------+--------+----------------------------+--------------|
            |         |           Device            | Platform |     System     | API_ID |          App name          | Official App |
            |---------+-----------------------------+----------+----------------+--------+----------------------------+--------------|
            | Current |         MacBook Pro         |  macOS   |    10.15.6     |  2834  |     Telegram macOS 8.4     |      ✔       |
            |---------+-----------------------------+----------+----------------+--------+----------------------------+--------------|
            |    1    |          Chrome 96          | Windows  |                |  2496  |   Telegram Web 1.28.3 Z    |      ✔       |
            |    2    |            iMac             |  macOS   |     11.3.1     |  2834  |     Telegram macOS 8.4     |      ✔       |
            |    3    |         MacBook Pro         |  macOS   |     10.12      |  2834  |     Telegram macOS 8.4     |      ✔       |
            |    4    |       Huawei Y360-U93       | Android  | 7.1 N MR1 (25) | 21724  |  Telegram Android X 8.4.1  |      ✔       |
            |    5    |    Samsung Galaxy Spica     | Android  |   6.0 M (23)   |   6    |   Telegram Android 8.4.1   |      ✔       |
            |    6    |     Xiaomi Redmi Note 8     | Android  |   10 Q (29)    |   6    |   Telegram Android 8.4.1   |      ✔       |
            |    7    | Samsung Galaxy Tab A (2017) | Android  |   7.0 N (24)   |   6    |   Telegram Android 8.4.1   |      ✔       |
            |    8    |  Samsung Galaxy XCover Pro  | Android  |   8.0 O (26)   |   6    |   Telegram Android 8.4.1   |      ✔       |
            |    9    |          iPhone X           |   iOS    |     13.1.3     | 10840  |      Telegram iOS 8.4      |      ✔       |
            |   10    |        iPhone XS Max        |   iOS    |    12.11.0     | 10840  |      Telegram iOS 8.4      |      ✔       |
            |   11    |      iPhone 11 Pro Max      |   iOS    |     14.4.2     | 10840  |      Telegram iOS 8.4      |      ✔       |
            |---------+-----------------------------+----------+----------------+--------+----------------------------+--------------|
        ```

        """
        if (sessions == None) or not isinstance(sessions, types.account.Authorizations):
            sessions = await self.GetSessions()

        assert sessions

        table = []

        index = 0
        for session in sessions.authorizations:
            table.append(
                {
                    " ": "Current" if session.current else index,
                    "Device": session.device_model,
                    "Platform": session.platform,
                    "System": session.system_version,
                    "API_ID": session.api_id,
                    "App name": "{} {}".format(session.app_name, session.app_version),
                    "Official App": "✔" if session.official_app else "✖",
                }
            )
            index += 1

        print(PrettyTable(table, [1]))

    async def is_official_app(self) -> bool:
        """
        Return `True` if this session was logged-in using an official app (`Device`).
        """
        auth = await self.GetCurrentSession()

        return False if auth == None else bool(auth.official_app)

    @typing.overload
    async def QRLoginToNewClient(
        self,
        session_id: str= None,
        device: Union[Type[DeviceData], DeviceData] = Device.TelegramAndroid,
        password: str = None,
    ) -> TelegramClient:
        """
        Create a new session using the current session.

        ### Arguments:
            session (`str`, `Account`, default=`None`):
                description

            device (`Device`, default=`TelegramDesktop`):
                Which Device to use. Read more `[here](Device)`.

            password (`str`, default=`None`):
                Two-step verification password, set if needed.

        ### Raises:
            - `NoPasswordProvided`: The account's two-step verification is enabled and no `password` was provided. Please set the `password` parameters.
            - `PasswordIncorrect`: The two-step verification `password` is incorrect.
            - `TimeoutError`: Time out waiting for the client to be authorized.

        ### Returns:
            - Return an instance of `TelegramClient` on success.

        ### Examples:
            Use to current session to authorize a new session:
        ```python
            # Using the Device that we've generated before. Please refer to method Device.Generate() to learn more.
            oldAPI = Device.TelegramDesktop.Generate(system="windows", unique_id="old.session")
            oldclient = TelegramClient("old.session", device=oldAPI)
            await oldClient.connect()

            # We can safely authorize the new client with a different Device.
            newAPI = Device.Device.TelegramAndroid.Generate(unique_id="new.session")
            newClient = await client.QRLoginToNewClient(session="new.session", device=newAPI)
            await newClient.connect()
            await newClient.PrintSessions()
        ```
        """

    @typing.overload
    async def QRLoginToNewClient(
        self,
        session_id: str= None,
        device: Union[Type[DeviceData], DeviceData] = Device.TelegramAndroid,
        password: str = None,
        *,
        connection: typing.Type[Connection] = ConnectionTcpFull,
        use_ipv6: bool = False,
        proxy: Union[tuple, dict] = None,
        local_addr: Union[str, tuple] = None,
        timeout: int = 10,
        request_retries: int = 5,
        connection_retries: int = 5,
        retry_delay: int = 1,
        auto_reconnect: bool = True,
        sequential_updates: bool = False,
        flood_sleep_threshold: int = 60,
        raise_last_call_error: bool = False,
        loop: asyncio.AbstractEventLoop = None,
        base_logger: Union[str, logging.Logger] = None,
        receive_updates: bool = True,
    ) -> TelegramClient:
        pass

    async def QRLoginToNewClient(
        self,
        session_id: str= None,
        device: Union[Type[DeviceData], DeviceData] = None,
        password: str = None,
        **kwargs) -> TelegramClient:

        newClient = TelegramClient(session_id, device=device, **kwargs)
       

        try:
            await newClient.connect()
            # switch DC for now because i can't handle LoginTokenMigrateTo...
            if newClient.session.dc_id != self.session.dc_id:
                await newClient._switch_dc(self.session.dc_id)
        except OSError as e:
            raise BaseException("Cannot connect")

        if await newClient.is_user_authorized():  # nocov

            currentAuth = await newClient.GetCurrentSession()
            if currentAuth != None:

                if currentAuth.api_id == device.api_id:
                    warnings.warn("\nCreateNewSession - a session file with the same name is already existed, returning the old session")
                else:
                    warnings.warn("\nCreateNewSession - a session file with the same name is already existed, but its api_id is different from the current one, it will be overwritten")

                    disconnect = newClient.disconnect()
                    if disconnect:
                        await disconnect
                        await newClient.disconnected

                    newClient.session.close()
                    newClient.session.delete()
                    self.database.delete(conditions=[Account.session_id==session_id])
                    


                    newClient = await self.QRLoginToNewClient(session=session_id, device=device, password=password, **kwargs)

                return newClient

        if not self._self_id:
            oldMe = await self.get_me()

        timeout_err = None

        # try to generate the qr token muiltiple times to work around timeout error.
        # this happens when we're logging in from a mismatched DC.
        request_retries = (kwargs["request_retries"] if "request_retries" in kwargs else 5 )  # default value for request_retries
        for attempt in range(request_retries):  # nocov

            try:
                # we could have been already authorized, but it still raised an timeouterror (??!)
                if attempt > 0 and await newClient.is_user_authorized():
                    break

                qr_login = await newClient.qr_login()

                # if we encountered timeout error in the first try, it might be because of mismatched DcId, we're gonna have to switch_dc
                if isinstance(qr_login._resp, types.auth.LoginTokenMigrateTo):
                    await newClient._switch_dc(qr_login._resp.dc_id)
                    qr_login._resp = await newClient(functions.auth.ImportLoginTokenRequest(qr_login._resp.token))

                # for the above reason, we should check if we're already authorized
                if isinstance(qr_login._resp, types.auth.LoginTokenSuccess):
                    coro = newClient._on_login(qr_login._resp.authorization.user)
                    if isinstance(coro, Awaitable):
                        await coro
                    break

                # calculate when will the qr token expire
                import datetime

                time_now = datetime.datetime.now(datetime.timezone.utc)
                time_out = (qr_login.expires - time_now).seconds + 5

                resp = await self(functions.auth.AcceptLoginTokenRequest(qr_login.token))

                await qr_login.wait(time_out)

                # break the loop on success
                break

            except (errors.AuthTokenAlreadyAcceptedError,errors.AuthTokenExpiredError,errors.AuthTokenInvalidError,) as e:
                # AcceptLoginTokenRequest exception handler
                raise e

            except (TimeoutError, asyncio.TimeoutError) as e:

                warnings.warn("\nQRLoginToNewClient attemp {} failed because {}".format(attempt + 1, type(e)))
                timeout_err = TimeoutError("Something went wrong, i couldn't perform the QR login process")

            except errors.SessionPasswordNeededError as e:
                password = password or self.account().password
                
                # requires an 2fa password

                Expects(password not in [None,''] ,NoPasswordProvided("Two-step verification is enabled for this account.\nYou need to provide the `password` to argument"))

                # two-step verification
                try:
                    pwd: types.account.Password = await newClient(functions.account.GetPasswordRequest())  # type: ignore
                    result = await newClient(functions.auth.CheckPasswordRequest(pwd_mod.compute_check(pwd, password)  ))

                    # successful log in
                    coro = newClient._on_login( result.user,password=password)  # type: ignore
                    if isinstance(coro, Awaitable):
                        await coro
                    break

                except errors.PasswordHashInvalidError as e:
                    raise PasswordIncorrect(e.__str__()) from e

            warnings.warn("\nQRLoginToNewClient attemp {} failed. Retrying..".format(attempt + 1))

        if timeout_err:
            raise timeout_err

        return newClient

  
    
    

def PrettyTable(table: List[Dict[str, Any]], addSplit: List[int] = []):

    # ! Warning: SUPER DIRTY CODE AHEAD
    padding = {}

    result = ""

    for label in table[0]:
        padding[label] = len(label)

    for row in table:
        for label, value in row.items():
            text = str(value)
            if padding[label] < len(text):
                padding[label] = len(text)

    def addpadding(text: str, spaces: int):
        if not isinstance(text, str):
            text = text.__str__()
        spaceLeft = spaces - len(text)
        padLeft = spaceLeft / 2
        padLeft = round(padLeft - (padLeft % 1))
        padRight = spaceLeft - padLeft
        return padLeft * " " + text + " " * padRight

    header = "|".join(
        addpadding(label, spaces + 2) for label, spaces in padding.items()
    )
    splitter = "+".join(("-" * (spaces + 2)) for label, spaces in padding.items())
    rows = []
    for row in table:
        rows.append(
            "|".join(
                addpadding(row[label], spaces + 2) for label, spaces in padding.items()
            )
        )

    result += f"|{splitter}|\n"
    result += f"|{header}|\n"
    result += f"|{splitter}|\n"

    index = 0
    for row in rows:
        if index in addSplit:
            result += f"|{splitter}|\n"
        result += f"|{row}|\n"
        index += 1

    result += f"|{splitter}|"

    return result



def generate_unique_session_id():
    return uuid.uuid4().hex[:16]




