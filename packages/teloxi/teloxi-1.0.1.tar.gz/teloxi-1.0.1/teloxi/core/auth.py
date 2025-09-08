
import sys,os,inspect,typing
import warnings
from time import time
from telethon._updates import SessionState
import asyncio
from .imports import (
    utils, 
    helpers, 
    errors, 
    pwd_mod,
    types, 
    functions, 
    custom,
   
    )


if typing.TYPE_CHECKING:
    from .client import TelegramClient

from ..profile import NameFactory
import random
from ..storage import Account
from ..utils import send_code_text
from .exception import (PaymentRequiredError)
class AuthMethods:

    # region Public methods

    def start(
            self: 'TelegramClient',
            phone: typing.Union[typing.Callable[[], str], str] = lambda: input('Please enter your phone (or bot token): '),
            password: typing.Union[typing.Callable[[], str], str] = lambda: input('Please enter your password: '),
            *,
            bot_token: str = None,
            code_callback: typing.Callable[[], typing.Union[str, int]] = None,
            first_name: str = 'New User',
            last_name: str = '',
            max_attempts: int = 3) -> 'TelegramClient':
       
        """
        Starts the client (connects and logs in if necessary).

        By default, this method will be interactive (asking for
        user input if needed), and will handle 2FA if enabled too.

        If the event loop is already running, this method returns a
        coroutine that you should await on your own code; otherwise
        the loop is ran until said coroutine completes.

        Arguments
            phone (`str` | `int` | `callable`):
                The phone (or callable without arguments to get it)
                to which the code will be sent. If a bot-token-like
                string is given, it will be used as such instead.
                The argument may be a coroutine.

            password (`str`, `callable`, optional):
                The password for 2 Factor Authentication (2FA).
                This is only required if it is enabled in your account.
                The argument may be a coroutine.

            bot_token (`str`):
                Bot Token obtained by `@BotFather <https://t.me/BotFather>`_
                to log in as a bot. Cannot be specified with ``phone`` (only
                one of either allowed).

            

            code_callback (`callable`, optional):
                A callable that will be used to retrieve the Telegram
                login code. Defaults to `input()`.
                The argument may be a coroutine.

            first_name (`str`, optional):
                The first name to be used if signing up. This has no
                effect if the account already exists and you sign in.

            last_name (`str`, optional):
                Similar to the first name, but for the last. Optional.

            max_attempts (`int`, optional):
                How many times the code/password callback should be
                retried or switching between signing in and signing up.

        Returns
            This `TelegramClient`, so initialization
            can be chained with ``.start()``.

        Example
            .. code-block:: python

                client = TelegramClient('anon', api_id, api_hash)

                # Starting as a bot account
                await client.start(bot_token=bot_token)

                # Starting as a user account
                await client.start(phone)
                # Please enter the code you received: 12345
                # Please enter your password: *******
                # (You are now logged in)

                # Starting using a context manager (this calls start()):
                with client:
                    pass
        """
        if code_callback is None:
            def code_callback():
                return input('Please enter the code you received: ')
        
        elif not callable(code_callback):
            raise ValueError('The code_callback parameter needs to be a callable function that returns the code you received by Telegram.' )

        if not phone and not bot_token:
            raise ValueError('No phone number or bot token provided.')

        if phone and bot_token and not callable(phone):
            raise ValueError('Both a phone and a bot token provided, must only provide one of either')

        
        
        
        coro = self._start(
            phone=phone,
            password=password,
            bot_token=bot_token,
            code_callback=code_callback,
            first_name=first_name,
            last_name=last_name,
            max_attempts=max_attempts
        )
        return ( coro if self.loop.is_running() else self.loop.run_until_complete(coro))

    async def _start(self: 'TelegramClient', phone, password, bot_token, code_callback, first_name, last_name, max_attempts):
        
        
        
        if not self.is_connected():
            await self.connect()

        # Rather than using `is_user_authorized`, use `get_me`. While this is
        # more expensive and needs to retrieve more data from the server, it
        # enables the library to warn users trying to login to a different
        # account. See #1172.
        
        me = await self.get_me()
        if me is not None:
            # The warnings here are on a best-effort and may fail.
            if bot_token:
                # bot_token's first part has the bot ID, but it may be invalid
                # so don't try to parse as int (instead cast our ID to string).
                if bot_token[:bot_token.find(':')] != str(me.id):
                    warnings.warn(
                        'the session already had an authorized user so it did '
                        'not login to the bot account using the provided bot_token; '
                        'if you were expecting a different user, check whether '
                        'you are accidentally reusing an existing session'
                    )
            elif phone and not callable(phone) and utils.parse_phone(phone) != me.phone:
                warnings.warn(
                    'the session already had an authorized user so it did '
                    'not login to the user account using the provided phone; '
                    'if you were expecting a different user, check whether '
                    'you are accidentally reusing an existing session'
                )
           
            return self

        if not bot_token:
            # Turn the callable into a valid phone number (or bot token)
            while callable(phone):
                value = phone()
                if inspect.isawaitable(value):
                    value = await value

                if ':' in value:
                    # Bot tokens have 'user_id:access_hash' format
                    bot_token = value
                    break

                phone = utils.parse_phone(value) or phone

        if bot_token:
            await self.sign_in(bot_token=bot_token)
            return self

        me = None
        attempts = 0
        two_step_detected = False

        await self.send_code_request(phone)
        
        
        sign_up = False  # assume login
        while attempts < max_attempts:
            try:
                value = code_callback()
                if inspect.isawaitable(value):
                    value = await value

                # Since sign-in with no code works (it sends the code)
                # we must double-check that here. Else we'll assume we
                # logged in, and it will return None as the User.
                
                if not value:
                    _phone = utils.parse_phone(phone) or self._phone
                    next_type = self._phone_code_hash.get(f"{_phone}-next")
                    timeout=self._phone_code_hash.get(f"{_phone}-timeout")
                    
                    if next_type:
                        remaining=timeout-int(time())
                        if   remaining <= 0:
                            await self.send_code_request(phone)
                        else:
                            print(f'Wait {remaining}s, then Enter to resend via {send_code_text(next_type.__class__.__name__)}')
                    else:
                        attempts += 1
                    continue
                    # raise errors.PhoneCodeEmptyError(request=None)

                if sign_up:
                    me = await self.sign_up(value, first_name, last_name)
                else:
                    # Raises SessionPasswordNeededError if 2FA enabled
                    me = await self.sign_in(phone, code=value)
                break
                
            except errors.SessionPasswordNeededError:
                two_step_detected = True
                break
            
            except errors.PhoneNumberOccupiedError:
                sign_up = False
            
            except errors.PhoneNumberUnoccupiedError:
                sign_up = True
            
            except (errors.PhoneCodeEmptyError,
                    errors.PhoneCodeExpiredError,
                    errors.PhoneCodeHashEmptyError,
                    errors.PhoneCodeInvalidError):
                print('Invalid code. Please try again.', file=sys.stderr)
            
            attempts += 1
        else:
            raise RuntimeError('{} consecutive sign-in attempts failed. Aborting'.format(max_attempts))

        if two_step_detected:
            if not password:
                raise ValueError("Two-step verification is enabled for this account. ""Please provide the 'password' argument to 'start()'.")

            if callable(password):
                for _ in range(max_attempts):
                    try:
                        value = password()
                        if inspect.isawaitable(value):
                            value = await value

                        me = await self.sign_in(phone=phone, password=value)
                        break
                    except errors.PasswordHashInvalidError:
                        print('Invalid password. Please try again',
                              file=sys.stderr)
                else:
                    raise errors.PasswordHashInvalidError(request=None)
            else:
                me = await self.sign_in(phone=phone, password=password)

        # We won't reach here if any step failed (exit by exception)
        signed, name = 'Signed in successfully as ', utils.get_display_name(me)
        tos ="" #'; remember to not break the ToS or you will risk an account ban!'
        try:
            print(signed, name, tos, sep='')
        except UnicodeEncodeError:
            # Some terminals don't support certain characters
            print(signed, name.encode('utf-8', errors='ignore').decode('ascii', errors='ignore'), tos, sep='')

        return self

    def _parse_phone_and_hash(self, phone, phone_hash):
        """
        Helper method to both parse and validate phone and its hash.
        """
        phone = utils.parse_phone(phone) or self._phone
        if not phone:
            raise ValueError(
                'Please make sure to call send_code_request first.'
            )

        phone_hash = phone_hash or self._phone_code_hash.get(phone, None)
        if not phone_hash:
            raise ValueError('You also need to provide a phone_code_hash.')

        return phone, phone_hash

    async def sign_in(
            self: 'TelegramClient',
            phone: str = None,
            code: typing.Union[str, int] = None,
            *,
            password: str = None,
            bot_token: str = None,
            phone_code_hash: str = None) -> 'typing.Union[types.User, types.auth.SentCode]':
        """
        Logs in to Telegram to an existing user or bot account.

        You should only use this if you are not authorized yet.

        This method will send the code if it's not provided.

        .. note::

            In most cases, you should simply use `start()` and not this method.

        Arguments
            phone (`str` | `int`):
                The phone to send the code to if no code was provided,
                or to override the phone that was previously used with
                these requests.

            code (`str` | `int`):
                The code that Telegram sent. Note that if you have sent this
                code through the application itself it will immediately
                expire. If you want to send the code, obfuscate it somehow.
                If you're not doing any of this you can ignore this note.

            password (`str`):
                2FA password, should be used if a previous call raised
                ``SessionPasswordNeededError``.

            bot_token (`str`):
                Used to sign in as a bot. Not all requests will be available.
                This should be the hash the `@BotFather <https://t.me/BotFather>`_
                gave you.

            phone_code_hash (`str`, optional):
                The hash returned by `send_code_request`. This can be left as
                `None` to use the last hash known for the phone to be used.

        Returns
            The signed in user, or the information about
            :meth:`send_code_request`.

        Example
            .. code-block:: python

                phone = '+34 123 123 123'
                await client.sign_in(phone)  # send code

                code = input('enter code: ')
                await client.sign_in(phone, code)
        """
        me = await self.get_me()
        if me:
            return me

        if phone and not code and not password:
            return await self.send_code_request(phone)
        elif code:
            phone, phone_code_hash = self._parse_phone_and_hash(phone, phone_code_hash)

            # May raise PhoneCodeEmptyError, PhoneCodeExpiredError,
            # PhoneCodeHashEmptyError or PhoneCodeInvalidError.
            request = functions.auth.SignInRequest(phone, phone_code_hash, str(code))
        elif password:
            pwd = await self(functions.account.GetPasswordRequest())
            request = functions.auth.CheckPasswordRequest(pwd_mod.compute_check(pwd, password))
        elif bot_token:
            request = functions.auth.ImportBotAuthorizationRequest(flags=0, bot_auth_token=bot_token,api_id=self.api_id, api_hash=self.api_hash)
        else:
            raise ValueError('You must provide a phone and a code the first time, and a password only if an RPCError was raised before.')

        try:
            result = await self(request)
        except errors.PhoneCodeExpiredError:
            self._phone_code_hash.pop(phone, None)
            raise

        if isinstance(result, types.auth.AuthorizationSignUpRequired):
            # Emulate pre-layer 104 behaviour
            self._tos = result.terms_of_service
            raise errors.PhoneNumberUnoccupiedError(request=request)

        return await self._on_login(result.user,password)

    async def sign_up(
            self: 'TelegramClient',
            code: typing.Union[str, int],
            first_name: str,
            last_name: str = '',
            *,
            phone: str = None,
            phone_code_hash: str = None) -> 'types.User':
        """
        Signs up to Telegram as a new user account.

        Use this if you don't have an account yet.

        You must call `send_code_request` first.

        **By using this method you're agreeing to Telegram's
        Terms of Service. This is required and your account
        will be banned otherwise.** See https://telegram.org/tos
        and https://core.telegram.org/api/terms.

        Arguments
            code (`str` | `int`):
                The code sent by Telegram

            first_name (`str`):
                The first name to be used by the new account.

            last_name (`str`, optional)
                Optional last name.

            phone (`str` | `int`, optional):
                The phone to sign up. This will be the last phone used by
                default (you normally don't need to set this).

            phone_code_hash (`str`, optional):
                The hash returned by `send_code_request`. This can be left as
                `None` to use the last hash known for the phone to be used.

        Returns
            The new created :tl:`User`.

        Example
            .. code-block:: python

                phone = '+34 123 123 123'
                await client.send_code_request(phone)

                code = input('enter code: ')
                await client.sign_up(code, first_name='Anna', last_name='Banana')
        """
        me = await self.get_me()
        if me:
            return me

        # To prevent abuse, one has to try to sign in before signing up. This
        # is the current way in which Telegram validates the code to sign up.
        #
        # `sign_in` will set `_tos`, so if it's set we don't need to call it
        # because the user already tried to sign in.
        #
        # We're emulating pre-layer 104 behaviour so except the right error:
        if not self._tos:
            try:
                return await self.sign_in(
                    phone=phone,
                    code=code,
                    phone_code_hash=phone_code_hash,
                )
            except errors.PhoneNumberUnoccupiedError:
                pass  # code is correct and was used, now need to sign in

        if self._tos and self._tos.text:
            if self.parse_mode:
                t = self.parse_mode.unparse(self._tos.text, self._tos.entities)
            else:
                t = self._tos.text
            sys.stderr.write("{}\n".format(t))
            sys.stderr.flush()

        phone, phone_code_hash = self._parse_phone_and_hash(phone, phone_code_hash)
        if not first_name:
            name=NameFactory.generate_random()
            lang=random.choice(['en','fa']) if name.persian else 'en'
            first_name=name.fa_name     if lang=='fa'   else name.en_name
            last_name=name.fa_surname   if lang=='fa'   else name.en_surname

        result = await self(functions.auth.SignUpRequest(
            phone_number=phone,
            phone_code_hash=phone_code_hash,
            first_name=first_name,
            last_name=last_name
        ))

        if self._tos:
            await self(functions.help.AcceptTermsOfServiceRequest(self._tos.id))

        return await self._on_login(result.user)
    
    async def send_code_request(
        self: 'TelegramClient',
        phone: str,
        *,
        retry_count: int = 3
    ) -> 'types.auth.SentCode':
        """
        Sends the Telegram code needed to login to the given phone number.

        Arguments:
            phone (`str` | `int`): The phone to which the code will be sent.
            

        Returns:
            An instance of :tl:`SentCode`.
        """
        
        result = None
        last_error = None
        
        
        
        code_settings = types.CodeSettings()

        for attempt in range(retry_count):
            phone = utils.parse_phone(phone) or self._phone
            phone_hash = self._phone_code_hash.get(phone)
            try:
                if not phone_hash:
                    result = await self(functions.auth.SendCodeRequest(phone_number=phone,api_id=self.api_id,api_hash=self.api_hash,settings=code_settings))
                else:
                    result = await self(functions.auth.ResendCodeRequest(phone_number=phone,phone_code_hash=phone_hash))

                
                
                if isinstance(result, types.auth.SentCode):
                    self._phone_code_hash[phone] = result.phone_code_hash
                    phone_hash = result.phone_code_hash

                if isinstance(result, types.auth.SentCodeSuccess):
                    raise RuntimeError('Logged in right after resending the code', file=sys.stderr)

                if isinstance(result, types.auth.SentCodePaymentRequired):
                    if 'telegram_premium.one_week.auth' in result.store_product:
                        msg='Login requires Payment for 1 week Telegram Premium.'
                    else:
                        msg=f'Payment "{result.store_product}" required.'
                    self.UpdateSession(data={'phone':phone if phone.startswith('+') else f'+{phone}'})
                    raise PaymentRequiredError(msg, result.store_product)
                
                
                if not isinstance(result, types.auth.SentCode):
                    print("Traying to send code again ...", file=sys.stderr)
                    await asyncio.sleep(3)
                    continue
                
                code_type = result.type
                timeout = result.timeout or 0
                self._phone_code_hash[f"{phone}-timeout"] =int(time()) + timeout
                self._phone_code_hash[f"{phone}-next"] = result.next_type
                
                
                
                if isinstance(result.type, types.auth.SentCodeTypeSetUpEmailRequired):
                    print("Email verification required.", file=sys.stderr)
                    await self.verify_email(phone, phone_hash, retry_count=retry_count)





                
                _phone=phone.strip().replace(' ','') if phone.startswith('+') else '+'+phone.strip().replace(' ','')
                print(f"Verification code sent via {send_code_text(code_type.__class__.__name__)}.", file=sys.stderr)
                if result.next_type:
                    print(f'Wait {timeout}s, then Enter to resend via {send_code_text(result.next_type.__class__.__name__)}.', file=sys.stderr)
                

                
                
                
                await asyncio.sleep(1)
                break

            except (errors.AuthRestartError, errors.PhoneCodeExpiredError) as e:
                if hasattr(self, '_log'):
                    self._log.info("Phone code expired or AuthRestartError, requesting a new code")
                self._phone_code_hash.pop(phone, None)
                self._phone_code_hash.pop(f"{phone}-timeout", 0)
                self._phone_code_hash.pop(f"{phone}-next", None)
                phone_hash = None
                last_error = e
                continue
            except PaymentRequiredError as e:
                print(e.msg)
                sys.exit(1)
        if result is None:
            if last_error:
                raise last_error
            raise RuntimeError("Failed to send or resend code after all retries")

        return result
    

    async def verify_email(self: 'TelegramClient', phone: str, phone_code_hash: str, 
                           email: typing.Union[typing.Callable[[], str], str] = lambda: input('Please enter your email address: '),
                           email_code: typing.Callable[[], str] = lambda: input('Please enter your email code: '),retry_count=3) -> types.account.SentEmailCode:
        
        for attempt in range(retry_count) :
            if callable(email):
                email = email()
                if inspect.isawaitable(email):
                    email = await email
            elif isinstance(email, str):
                email = email
            
            
            else:
                raise TypeError('email must be a string or a function returning a string')
            
            if not email:
                continue
            try: 
                send_verify_email_code = await self(functions.account.SendVerifyEmailCodeRequest(
                                                                purpose=types.EmailVerifyPurposeLoginSetup(phone_number=phone, phone_code_hash=phone_code_hash),
                                                                email=email
                                                                
                                                                ) )
                
                
                if isinstance(send_verify_email_code, types.account.SentEmailCode):
                    _phone=phone.strip().replace(' ','') if phone.startswith('+') else '+'+phone.strip().replace(' ','')
                    print(f"Verification code for {_phone} sent via Email: {send_verify_email_code.email_pattern}.", file=sys.stderr)
                    if callable(email_code):
                        email_code = email_code()
                        if inspect.isawaitable(email_code):
                            email_code = await email_code
                    else:
                        email_code = input('Please enter your email code: ')
                    
                    await asyncio.sleep(1)
                
                    verify_email =await self(functions.account.VerifyEmailRequest(
                                                        purpose=types.EmailVerifyPurposeLoginSetup(phone_number=phone,phone_code_hash=phone_code_hash),
                                                        verification=types.EmailVerificationCode( code=email_code ))
                                                        )
                else:
                    print(send_verify_email_code.stringify())
                
                if isinstance(verify_email, types.account.EmailVerifiedLogin):
                    self.UpdateSession(data={'phone':phone if phone.startswith('+') else f'+{phone}'})
                    if isinstance(verify_email.sent_code, types.auth.SentCodePaymentRequired):
                        if 'telegram_premium.one_week.auth' in verify_email.sent_code.store_product:
                            msg='Login requires Payment for 1 week Telegram Premium.'
                        else:
                            msg=f'Payment "{verify_email.sent_code.store_product}" required.'
                        
                        raise PaymentRequiredError(msg, verify_email.sent_code.store_product)
                
                else:
                    print(send_verify_email_code.stringify())
                
                return verify_email
            
            except (errors.EmailInvalidError,errors.BadRequestError) as e:
                print(e)
                continue



     
    async def _on_login(self:'TelegramClient', user:types.User,password:str=None):
        """
        Callback called whenever the login or sign up process completes.

        Returns the input user parameter.
        """
        self._mb_entity_cache.set_self_user(user.id, user.bot, user.access_hash)
        self._authorized = True

        state = await self(functions.updates.GetStateRequest())
        # the server may send an old qts in getState
        difference = await self(functions.updates.GetDifferenceRequest(pts=state.pts, date=state.date, qts=state.qts))

        if isinstance(difference, types.updates.Difference):
            state = difference.state
        elif isinstance(difference, types.updates.DifferenceSlice):
            state = difference.intermediate_state
        elif isinstance(difference, types.updates.DifferenceTooLong):
            state.pts = difference.pts

        self._message_box.load(SessionState(0, 0, 0, state.pts, state.qts, int(state.date.timestamp()), state.seq, 0), [])

        
        
        
        phone= f"+{user.phone}" if user.phone else ''
        data={"phone":phone }
        if password:
            data['password']=password
        
        self.UpdateSession(me=user, data=data)
        
        self._phone=phone
        return user

    
    async def edit_2fa(
            self: 'TelegramClient',
            current_password: str = None,
            new_password: str = None,
            *,
            hint: str = '',
            email: str = None,
            email_code_callback: typing.Callable[[int], str] = None) -> bool:
        """
        Changes the 2FA settings of the logged in user.

        Review carefully the parameter explanations before using this method.

        Note that this method may be *incredibly* slow depending on the
        prime numbers that must be used during the process to make sure
        that everything is safe.

        Has no effect if both current and new password are omitted.

        Arguments
            current_password (`str`, optional):
                The current password, to authorize changing to ``new_password``.
                Must be set if changing existing 2FA settings.
                Must **not** be set if 2FA is currently disabled.
                Passing this by itself will remove 2FA (if correct).

            new_password (`str`, optional):
                The password to set as 2FA.
                If 2FA was already enabled, ``current_password`` **must** be set.
                Leaving this blank or `None` will remove the password.

            hint (`str`, optional):
                Hint to be displayed by Telegram when it asks for 2FA.
                Leaving unspecified is highly discouraged.
                Has no effect if ``new_password`` is not set.

            email (`str`, optional):
                Recovery and verification email. If present, you must also
                set `email_code_callback`, else it raises ``ValueError``.

            email_code_callback (`callable`, optional):
                If an email is provided, a callback that returns the code sent
                to it must also be set. This callback may be asynchronous.
                It should return a string with the code. The length of the
                code will be passed to the callback as an input parameter.

                If the callback returns an invalid code, it will raise
                ``CodeInvalidError``.

        Returns
            `True` if successful, `False` otherwise.

        Example
            .. code-block:: python

                # Setting a password for your account which didn't have
                await client.edit_2fa(new_password='I_<3_Telethon')

                # Removing the password
                await client.edit_2fa(current_password='I_<3_Telethon')
        """
        if new_password is None and current_password is None:
            return False

        if email and not callable(email_code_callback):
            raise ValueError('email present without email_code_callback')

        pwd = await self(functions.account.GetPasswordRequest())
        pwd.new_algo.salt1 += os.urandom(32)
        assert isinstance(pwd, types.account.Password)
        if not pwd.has_password and current_password:
            current_password = None

        if current_password:
            password = pwd_mod.compute_check(pwd, current_password)
        else:
            password = types.InputCheckPasswordEmpty()

        if new_password:
            new_password_hash = pwd_mod.compute_digest(pwd.new_algo, new_password)
        else:
            new_password_hash = b''

        try:
            await self(functions.account.UpdatePasswordSettingsRequest(
                password=password,
                new_settings=types.account.PasswordInputSettings(
                    new_algo=pwd.new_algo,
                    new_password_hash=new_password_hash,
                    hint=hint,
                    email=email,
                    new_secure_settings=None
                )
            ))
        except errors.EmailUnconfirmedError as e:
            code = email_code_callback(e.code_length)
            if inspect.isawaitable(code):
                code = await code

            code = str(code)
            await self(functions.account.ConfirmPasswordEmailRequest(code))
        self.UpdateSession(data= {"password":new_password or ''})
        return True
    
           
 
    async def qr_login(self: 'TelegramClient', ignored_ids: typing.List[int] = None) -> custom.QRLogin:
        """
        Initiates the QR login procedure.

        Note that you must be connected before invoking this, as with any
        other request.

        It is up to the caller to decide how to present the code to the user,
        whether it's the URL, using the token bytes directly, or generating
        a QR code and displaying it by other means.

        See the documentation for `QRLogin` to see how to proceed after this.

        Arguments
            ignored_ids (List[`int`]):
                List of already logged-in user IDs, to prevent logging in
                twice with the same user.

        Returns
            An instance of `QRLogin`.

        Example
            .. code-block:: python

                def display_url_as_qr(url):
                    pass  # do whatever to show url as a qr to the user

                qr_login = await client.qr_login()
                display_url_as_qr(qr_login.url)

                # Important! You need to wait for the login to complete!
                await qr_login.wait()

                # If you have 2FA enabled, `wait` will raise `telethon.errors.SessionPasswordNeededError`.
                # You should except that error and call `sign_in` with the password if this happens.
        """
        qr_login = custom.QRLogin(self, ignored_ids or [])
        await qr_login.recreate()
        return qr_login

    async def log_out(self: 'TelegramClient') -> bool:
        """
        Logs out Telegram and deletes the current ``*.session`` file.

        The client is unusable after logging out and a new instance should be created.

        Returns
            `True` if the operation was successful.

        Example
            .. code-block:: python

                # Note: you will need to login again!
                await client.log_out()
        """
        try:
            await self(functions.auth.LogOutRequest())
        except errors.RPCError:
            return False

        self._mb_entity_cache.set_self_user(None, None, None)
        self._authorized = False

        await self.disconnect()
        self.database.delete([Account.session_id==self._session_id])
        self.session = None
        return True

    
    # endregion

    # region with blocks

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.disconnect()

    __enter__ = helpers._sync_enter
    __exit__ = helpers._sync_exit

    # endregion
