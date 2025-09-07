from telethon import types
from urllib.parse import urlparse, parse_qs
from typing import Dict, List
from .enums import ChatType


class FullUser:
    def __init__(self, user: types.User, user_full: types.UserFull):
        self.user = user
        self.user_full = user_full

    @property
    def id(self):
        return self.user.id
    
    @property
    def first_name(self):
        return self.user.first_name
    @property
    def last_name(self):
        return self.user.last_name
    

    @property
    def username(self):
        return self.user.username

    @property
    def phone(self):
        return self.user.phone if self.user.phone.startswith('+') else f"+{self.user.phone }" if self.user.phone else None

    @property
    def about(self):
        return self.user_full.about

    @property
    def blocked(self):
        return self.user_full.blocked



class FullChat:

    def __init__(self, channel: types.Channel|types.Chat, channel_full: types.ChannelFull|types.ChatFull):
        self.channel = channel
        self.channel_full = channel_full


    @property
    def id(self):
        return self.channel.id

    @property
    def title(self):
        return self.channel.title

    @property
    def username(self):
        return self.channel.username

    @property
    def photo(self):
        return self.channel.photo

    @property
    def about(self):
        return self.channel_full.about

    
    @property
    def left(self):
        return self.channel.left
    @property
    def join_to_send(self):
        return self.channel.join_to_send
    @property
    def join_request(self):
        return self.channel.join_request
  
    

    




class TelegramLinkParser:
    """
    telegram_link_parser.py

    TelegramLinkParser class for parsing Telegram links.
    Supports link types:
    - USERNAME
    - PUBLIC
    - PUBLIC_POST
    - PRIVATE
    - PRIVATE_POST
    - REFERRAL_LINK
    - CHANNEL_ID_POST
    Detects bots, private invite links, and extracts structured information.
    
    A class to parse Telegram links.

    Attributes:
        input_url (str): Input Telegram URL.
        link_type (ChatType): Type of the link.
        username (str): Channel or bot username.
        chat_url (str): Standard t.me chat URL.
        join_hash (str): Hash for private invite links.
        post_id (int): Post ID if the link points to a post.
        chat_id (int): Chat ID if applicable.
        is_bot (bool): Whether the link belongs to a bot.
    """

    def __init__(self, input_url: str):
        self.input_url = input_url.strip()
        self.link_type: ChatType = ChatType.NONE
        self.username: str = ""
        self.chat_url: str = ""
        self.join_hash: str = ""
        self.post_id: int = 0
        self.chat_id: int = 0
        self.is_bot: bool = False

        if self._is_valid_telegram_url(self.input_url):
            self._parse_link()

    def _is_valid_telegram_url(self, url: str) -> bool:
        """Check if the URL is a valid Telegram link."""
        return "t.me" in url or "telegram.me" in url

    def _normalize_url(self, url: str) -> str:
        """Normalize the URL for consistent parsing."""
        url = url.replace("telegram.me", "t.me")
        url = url.replace("http://", "").replace("https://", "")
        url = url.replace("www.", "")
        return "https://" + url

    def _parse_link(self) -> None:
        """Parse the URL and extract information."""
        parsed = urlparse(self._normalize_url(self.input_url))
        if parsed.netloc != "t.me":
            return

        path_parts = [p for p in parsed.path.split("/") if p]
        query_params = parse_qs(parsed.query)

        self._detect_link_type(path_parts, query_params)
        self._extract_username(path_parts)
        self._build_chat_url()
        self._detect_bot()

    def _detect_link_type(self, path: List[str], query: Dict[str, List[str]]) -> None:
        """Determine the type of Telegram link based on path and query."""
        if not path:
            return

        if path[0] == "c" and len(path) == 3 and path[1].isdigit() and path[2].isdigit():
            self.link_type = ChatType.CHANNEL_ID_POST
            self.chat_id = int(f"-100{path[1]}")
            self.post_id = int(path[2])
            return

        if path[0] == "s" and len(path) == 3:
            self.link_type = ChatType.PUBLIC_POST
            self.username = path[1]
            self.post_id = int(path[2]) if path[2].isdigit() else 0
            return

        if path[0].startswith("+") or path[0] == "joinchat":
            self.link_type = ChatType.PRIVATE
            self.join_hash = path[-1].replace("+", "")
            return

        if len(path) == 1:
            self.link_type = ChatType.REFERRAL_LINK if query else ChatType.USERNAME

        elif path[-1].isdigit() or "single" in query:
            self.post_id = int(path[-1]) if path[-1].isdigit() else 0
            if len(path) > 1 and path[-2].isdigit():
                self.link_type = ChatType.PRIVATE_POST
                self.chat_id = int(f"-100{path[-2]}") if path[-2].isdigit() else 0
            else:
                self.link_type = ChatType.PUBLIC_POST

        elif len(path) == 2:
            self.link_type = ChatType.REFERRAL_LINK if query else ChatType.PUBLIC

    def _extract_username(self, path: List[str]) -> None:
        """Extract the username from the path."""
        if self.link_type in [ChatType.USERNAME, ChatType.PUBLIC, ChatType.PUBLIC_POST]:
            if not self.username and path:
                self.username = (
                    path[1].replace("@", "") if path[0] == "s" and len(path) > 1
                    else path[0].replace("@", "")
                )
        elif self.link_type == ChatType.REFERRAL_LINK and path:
            self.username = path[0].replace("@", "")

    def _build_chat_url(self) -> None:
        """Construct the standard t.me chat URL."""
        if self.username:
            self.chat_url = f"https://t.me/{self.username}"
        elif self.join_hash:
            self.chat_url = f"https://t.me/+{self.join_hash}"
        elif self.link_type == ChatType.CHANNEL_ID_POST and self.chat_id:
            self.chat_url = f"https://t.me/c/{str(self.chat_id)[4:]}/{self.post_id}"

    def _detect_bot(self) -> None:
        """Detect if the link belongs to a bot."""
        if self.link_type == ChatType.REFERRAL_LINK or (
            self.username and self.username.lower().endswith("bot")
        ):
            self.is_bot = True

    def to_dict(self) -> dict:
        """Return parsed information as a dictionary."""
        return {
            "type": self.link_type.value,
            "username": self.username,
            "chat_url": self.chat_url,
            "join_hash": self.join_hash,
            "post_id": self.post_id,
            "chat_id": self.chat_id,
            "is_bot": self.is_bot,
        }

        return {
            "type": self.link_type.value,
            "username": self.username,
            "chat_url": self.chat_url,
            "join_hash": self.join_hash,
            "post_id": self.post_id,
            "chat_id": self.chat_id,
            "is_bot": self.is_bot,
        }