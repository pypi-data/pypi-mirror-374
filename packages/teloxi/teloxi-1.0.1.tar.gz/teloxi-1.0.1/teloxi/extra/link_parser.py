import re
from urllib.parse import urlparse, parse_qs
import json
from .enums import ChatType


class LinkParser:
    """
    TelegramLinkParser parses and validates different types of Telegram links.

    Supported types:
    - USERNAME: simple username input or @username
    - PUBLIC: public Telegram channel/group link
    - PUBLIC_POST: public post link /s/username/post_id
    - PRIVATE: private invite link (+hash or joinchat)
    - PRIVATE_POST: private channel post link /c/channel_number/post_id
    - REFERRAL_LINK: link with ?start=referral_code

    Attributes:
        input_url (str): The original input URL.
        link_type (ChatType): Detected type of the link.
        username (str): Extracted username if available.
        chat_url (str): Constructed chat URL.
        join_hash (str): Private join hash for private links.
        post_id (int): Post ID if applicable.
        chat_id (int): Channel ID if applicable (for private posts).
        is_bot (bool): True if the link points to a bot username.
        referral_code (str): Referral code if link contains ?start=.
    """

    def __init__(self, input_url: str):
        """
        Initialize the parser with a Telegram URL or username.

        Args:
            input_url (str): Telegram link or username.
        """
        self.input_url = input_url.strip()
        self.link_type: ChatType = ChatType.NONE
        self.username: str = ""
        self.chat_url: str = ""
        self.join_hash: str = ""
        self.post_id: int = 0
        self.chat_id: int = 0
        self.is_bot: bool = False
        self.referral_code: str = ""

        if self.input_url:
            self._parse_link()

    # --------------------- Validation Methods ---------------------

    def _is_valid_username(self, username: str, relax_for_post: bool = False) -> bool:
        """
        Validate Telegram username.

        Args:
            username (str): The username to validate.
            relax_for_post (bool): If True, allow shorter usernames for posts.

        Returns:
            bool: True if valid, False otherwise.
        """
        if not username:
            return False
        if relax_for_post:
            return re.match(r'^[a-zA-Z][a-zA-Z0-9_]{0,31}$', username) is not None
        return re.match(r'^[a-zA-Z][a-zA-Z0-9_]{4,31}$', username) is not None

    def _is_valid_channel_number(self, channel_number: str) -> bool:
        """
        Validate private channel number.

        Args:
            channel_number (str): Numeric channel ID.

        Returns:
            bool: True if valid channel number, else False.
        """
        if not channel_number.isdigit():
            return False
        length = len(channel_number)
        return 8 <= length <= 12

    # --------------------- URL Parsing ---------------------

    def _normalize_url(self, url: str) -> str:
        """
        Normalize Telegram URL to standard format starting with https://t.me/

        Args:
            url (str): Input URL.

        Returns:
            str: Normalized URL.
        """
        url = url.replace("telegram.me", "t.me")
        url = url.replace("http://", "").replace("https://", "")
        url = url.replace("www.", "")
        return "https://" + url

    def _parse_link(self) -> None:
        """
        Main parser logic to detect link type, extract username, post_id, chat_id, referral code, etc.
        """
        # Handle simple username input
        if "/" not in self.input_url and self.input_url.replace("@","").strip():
            username = self.input_url.replace("@", "").strip()
            if self._is_valid_username(username):
                self.link_type = ChatType.USERNAME
                self.username = username
                self.chat_url = f"https://t.me/{self.username}"
                return

        parsed = urlparse(self._normalize_url(self.input_url))
        if parsed.netloc != "t.me":
            return

        path_parts = [p for p in parsed.path.split("/") if p]
        query_params = parse_qs(parsed.query)

        # Private invite link
        if path_parts and (path_parts[0].startswith("+") or path_parts[0] == "joinchat"):
            self.link_type = ChatType.PRIVATE
            self.join_hash = path_parts[-1].replace("+", "")
            self._build_chat_url()
            return

        # Referral link
        if "start" in query_params and path_parts:
            candidate = path_parts[0].replace("@","").strip()
            if self._is_valid_username(candidate):
                self.username = candidate
                self.referral_code = query_params["start"][0]
                self.link_type = ChatType.REFERRAL_LINK
                self._build_chat_url()
                self._detect_bot()
                return

        # Public post /s/username/post_id
        if len(path_parts) == 3 and path_parts[0] == "s":
            candidate = path_parts[1].replace("@","").strip()
            if self._is_valid_username(candidate, relax_for_post=True):
                self.username = candidate
                self.post_id = int(path_parts[2]) if path_parts[2].isdigit() else 0
                self.link_type = ChatType.PUBLIC_POST
                self._build_chat_url()
                return

        # Private post /c/channel_number/post_id
        if len(path_parts) == 3 and path_parts[0] == "c":
            channel_number, post_id = path_parts[1], path_parts[2]
            if self._is_valid_channel_number(channel_number) and post_id.isdigit():
                self.chat_id = int(f"-100{channel_number}")
                self.post_id = int(post_id)
                self.link_type = ChatType.PRIVATE_POST
                self._build_chat_url()
                return

        # Single path -> PUBLIC
        if len(path_parts) == 1:
            candidate = path_parts[0].replace("@","").strip()
            if self._is_valid_username(candidate):
                self.username = candidate
                self.link_type = ChatType.PUBLIC
                self._build_chat_url()
                self._detect_bot()
                return

    # --------------------- Build URL & Detect Bot ---------------------

    def _build_chat_url(self) -> None:
        """Construct chat URL based on available information."""
        if self.username:
            self.chat_url = f"https://t.me/{self.username}"
        elif self.join_hash:
            self.chat_url = f"https://t.me/+{self.join_hash}"
        elif self.link_type == ChatType.PRIVATE_POST and self.chat_id:
            self.chat_url = f"https://t.me/c/{str(self.chat_id)[4:]}/{self.post_id}"

    def _detect_bot(self) -> None:
        """Detect if the username belongs to a bot."""
        if self.username and self.username.lower().endswith("bot"):
            self.is_bot = True

    # --------------------- Public Methods ---------------------

    def to_dict(self) -> dict:
        """
        Return parsed link data as a dictionary.

        Returns:
            dict: Parsed information including type, username, URLs, IDs, bot status, referral code.
        """
        return {
            "type": self.link_type,
            "username": self.username,
            "chat_url": self.chat_url,
            "join_hash": self.join_hash,
            "post_id": self.post_id,
            "chat_id": self.chat_id,
            "is_bot": self.is_bot,
            "referral_code": self.referral_code,
        }

    def to_json(self) -> str:
        """
        Return parsed link data as a JSON string.

        Returns:
            str: JSON formatted parsed data.
        """
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

    def __str__(self) -> str:
        return self.to_json()