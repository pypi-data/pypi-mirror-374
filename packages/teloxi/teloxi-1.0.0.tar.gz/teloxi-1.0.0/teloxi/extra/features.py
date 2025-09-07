import re,inspect
from asyncio import sleep
from telethon import types,functions,events,errors
from .link_parser import LinkParser
from .objects import FullUser,FullChat
from typing import Union,Tuple


class Features:
    
    async def get_login_code(self, callback=None) -> str:
        """
        Retrieve the login code by interacting with Telegram's BotFather.

        This function waits for a login code message from Telegram (user 777000) 
        and extracts the numeric code automatically. Optionally, a callback 
        can be provided to handle the message and code.

        Args:
            callback (Callable[[str, Optional[str]], Awaitable] | None, optional):
                A function that will be called with two arguments:
                - message (str): the full message received
                - code (str | None): the extracted login code, or None if not found
                If the callback is asynchronous, it will be awaited.
                Defaults to None. If not provided, messages are printed to the console.

        Returns:
            str: The login code as a string, or an empty string if not found.

        Example usage:
            async def my_callback(message, code):
                if code:
                    print(f"Received login code: {code}")
                else:
                    print(f"Message received: {message}")

            code = await client.get_login_code(callback=my_callback)
            if code:
                print(f"Login code successfully retrieved: {code}")
            else:
                print("Failed to get login code.")
        """

        async def return_message(message,code=None):
            if callable(callback):
                result = callback(message,code)
                if inspect.isawaitable(result):
                    await result
            else: 
                print(message)
        
        def search_code(text: str) -> str:
            pattern_1 = re.compile(r'Login code: *(\d+)\s*\.?', re.IGNORECASE)
            pattern_2 = re.compile(r': *(\d+)\s*\.?', re.IGNORECASE)
            pattern_3 = re.compile(r'کد ورود[:：]?\s*(\d{5,6})')
            pattern_4 = re.compile(r'(\d{5,6})')

            for pattern in [pattern_1, pattern_2, pattern_3, pattern_4]:
                match = pattern.search(text)
                if match:
                    return match.group(1)
            return ''

        
        await return_message(f'Login to {self._phone or self._account.phone} now to grab your code!')


        async with self.conversation(777000) as conv:
            try:
                event:types.Message =await conv.wait_event(events.NewMessage(777000,func=lambda e: bool(search_code(e.message.message))) , timeout=300)
                code=search_code(event.message.message)
                await return_message(f'Login code: {code}',code)
                return code
            
            except TimeoutError:
                await return_message('TimeoutError')
                
        await return_message('Login code not found, there may be a problem.')
        return ''
    
    async def delete_password(self,current_password=None):
        """
        Deletes the 2FA password for the current account.

        If `current_password` is not given, it will use the `password` stored in the database.
        If `current_password` is given, it will use that to delete the current password.

        Returns `True` if the password was deleted, `False` if there was an error.

        There are two types of errors that can occur:

        - If the account doesn't have a password, it will return `True`.
        - If the account does have a password, it will return `False` if the wrong password was given.
        - If the account does have a password, it will return `False` if the password was not deleted due to a temporary error.

        If the deletion of the password fails due to a temporary error, it will print an error message with the retry date.
        """
        if not current_password:
            current_password=self._account.password or None
        result :types.account.Password=await self(functions.account.GetPasswordRequest())
        
        if not result.has_password:
            return True
        else:
            if current_password:
                res =await self.edit_2fa(current_password=current_password, new_password='')
                if res is True:
                    return True

            res = await self(functions.account.ResetPasswordRequest())
            if isinstance(res,types.account.ResetPasswordOk):
                self.database.update({"password":None})
                return True
            
            if isinstance(res,types.account.ResetPasswordRequestedWait):
                print(f"Reset password requested wait: {res.until_date.isoformat()}")
            
            if isinstance(res,types.account.ResetPasswordFailedWait):
                print(f"Reset password failed wait, retry date: {res.retry_date.isoformat()}")
            
            return False
 
    async def set_password(self,new_password='',current_password=''):
        """Set 2FA password for this account
        Args:
            new_password: the new password to set
            current_password: the current password to verify
        Returns:
            bool: True if successful, False otherwise
        """
        
        if not current_password:
            current_password=self._account.password 
        
        result =await self.edit_2fa(current_password=current_password, new_password=new_password)
        
        
        return result
    
    async def start_app(self,
                                   bot_username:str,
                                   is_miniapp:bool,
                                   short_name:str|None=None,
                                   app_url:str|None=None,
                                   peer:str|None=None,
                                   start_param:str|None=None
                                   )->types.WebViewResultUrl:
        
        
        """
        Start a miniapp or a bot on Telegram.

        Args:
            bot_username: Username of the bot to start.
            is_miniapp: If True, start a miniapp, otherwise start a bot.
            short_name: Short name of the miniapp.
            app_url: URL of the miniapp.
            peer: Peer to start the miniapp or bot, if not provided the bot_username will be used.
            start_param: Start parameter of the miniapp or bot.

        Returns:
            types.WebViewResultUrl

        Note:
            For miniapps, the bot must be already added to the chat.
            For bots, the bot must be already started.
        """

        if not peer:
            peer=bot_username
        
        
        
            
        if is_miniapp:
            entyty=await self.get_entity(bot_username)
            bot_app= types.InputBotAppShortName( bot_id=types.InputUser(user_id=entyty.id,access_hash= entyty.access_hash), short_name=short_name)
            await sleep(1)        
            return await self(functions.messages.RequestAppWebViewRequest(
                            peer= peer,
                            app= bot_app,
                            platform= 'android',
                            write_allowed=True,
                            start_param= start_param))
            
        else:
            return await self(functions.messages. RequestWebViewRequest(
                                peer=peer,
                                bot=bot_username,
                                platform='android',
                                from_bot_menu=False,
                                start_param=start_param,
                                url=app_url))
                    
        
    async def start_bot(self,bot,peer=None,start_param: str='',random_id: int = None)-> types.Updates | types.Message:
        """
        Start a bot on Telegram.

        Args:
            bot: The bot to start.
            peer: The peer to start the bot with.
            start_param: The start parameter to pass to the bot. Defaults to ''.
            random_id: The random ID to use. Defaults to None.

        Returns:
            Updates:
            Instance of either UpdatesTooLong, UpdateShortMessage, UpdateShortChatMessage, UpdateShort, UpdatesCombined, Updates, UpdateShortSentMessage.
        """
        if not start_param:
            return await self.send_message(bot,'/start')
        
        if not peer:
            peer=bot
        
        return await self(functions.messages.StartBotRequest(bot=bot,peer=peer,start_param=start_param,random_id=random_id))

    async def get_full_me(self, reload=False) -> FullUser:
        """
        Get full information about the current user.

        Args:
            reload: If set to `True`, the method will reload the full user information from the server. Defaults to `False`.

        Returns:
            A `FullUser` object containing the full information about the user.
        """
        if hasattr(self, '_full_me') and (self._full_me is not None) and (not reload):
            return self._full_me

        self._full_me = await self.get_full_user('me')
        return self._full_me 


    async def get_full_user(self, user_id) -> FullUser:
        """
        Get full information about a Telegram user.

        Args:
            user_id: The user ID to retrieve the information about.

        Returns:
            A `FullUser` object containing the full information about the user.
        """
        full_user:types.users.UserFull = await self(functions.users.GetFullUserRequest(user_id))
        return FullUser(full_user.users[0],full_user.full_user)
        
    async def get_full_chat(self, chat_id) -> FullChat:
        
        """
        Get full information about a Telegram chat.

        Args:
            chat_id: The chat ID to retrieve the information about.

        Returns:
            A `FullChat` object containing the full information about the chat.
        """
        full_chat:types.messages.ChatFull = await self(functions.channels.GetFullChannelRequest(chat_id))
        return FullChat(full_chat.chats[0],full_chat.full_chat)
    
    async def get_chat_preview(self, url: str) -> Tuple[Union[types.User, types.Channel, types.Chat, types.ChatInvite, None], Exception, bool]:
        """
        Get information about a Telegram chat or channel by URL.

        Args:
            url (str): Telegram link or username.

        Returns:
            Tuple[Union[types.User, types.Channel, types.Chat, types.ChatInvite, None], Exception, bool]:
                A tuple with the following items:

                1. The chat information if it can be retrieved. If the link is invalid, or if the chat is private and the client is not joined, this is None.
                2. An exception object if something went wrong during the retrieval. If nothing went wrong, this is None.
                3. A boolean indicating whether the client is joined to the chat or not. If the chat is private and the client is not joined, this is False. If the chat is public or if the client is joined, this is True.
        """

        parsed_url = LinkParser(url)
        chat_info, error, is_joined = None, None, False
        if not parsed_url.link_type:
            return chat_info, ValueError(f"Invalid Telegram link ({url})"), is_joined

        try:
            if parsed_url.username:
                chat_info = await self.get_entity(parsed_url.chat_url)
        except Exception as e:
            error = e

    
        if not chat_info and parsed_url.join_hash:
            e=None
            try:
                result = await self(functions.messages.CheckChatInviteRequest(hash=parsed_url.join_hash))
                if isinstance(result, types.ChatInviteAlready):
                    chat_info = result.chat
                if isinstance(result, types.ChatInvitePeek):
                    chat_info=result.chat
                    
            except Exception as e:
                error = e

        
        if isinstance(chat_info, types.ChatInvite):
            is_joined = False
        elif isinstance(chat_info, (types.Channel, types.Chat)):
            is_joined = not getattr(chat_info, "left", True)
        elif isinstance(chat_info, types.User):
            is_joined = True  

        return chat_info, error, is_joined

    async def join_chat(self, url: str) -> Tuple[ Union[types.User, types.Channel, types.Chat, types.ChatInvite, None], Exception, bool]:
        """
        Join a Telegram chat or channel by URL.

        Args:
            url (str): The Telegram URL to join.

        Returns:
            Tuple[Union[types.User, types.Channel, types.Chat, types.ChatInvite, None], Exception, bool]:
                A tuple of the joined chat information, an error if any, and a boolean indicating if the user is joined.

        Raises:
            ValueError: If the URL is invalid.
            TypeError: If the URL is not a string.
            errors.UserAlreadyParticipantError: If the user is already joined to the chat.
            Exception: If any other error occurs.
        """
        chat_info, error, is_joined = await self.get_chat_preview(url)

        
        if isinstance(chat_info, types.User):
            return chat_info, "Cannot join a User or Bot.", is_joined

       
        if not chat_info or is_joined:
            return chat_info, error, is_joined

        

        error=None
        
        try:
            parsed_url = LinkParser(url)
            if parsed_url.username:
                result = await self(functions.channels.JoinChannelRequest(parsed_url.username))
                if isinstance(result, types.Updates) and result.chats:
                    chat_info = result.chats[0]
                    is_joined = True
            elif parsed_url.join_hash:
                result = await self(functions.messages.ImportChatInviteRequest(hash=parsed_url.join_hash))
                if isinstance(result, types.Updates) and result.chats:
                    chat_info = result.chats[0]
                    is_joined = True
        except errors.UserAlreadyParticipantError:
            is_joined = True
       
            
        except Exception as e:
            error = e
            
            
        
        return chat_info, error, is_joined

