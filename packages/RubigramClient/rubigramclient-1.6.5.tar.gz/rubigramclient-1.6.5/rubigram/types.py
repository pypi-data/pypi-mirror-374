from dataclasses import dataclass, is_dataclass, fields
from typing import Type, TypeVar, Union, Optional, get_origin, get_args
from json import dumps
from enum import Enum
from . import enums
import rubigram


T = TypeVar("T", bound="DataManager")


@dataclass
class DataManager:
    def to_dict(self) -> dict:
        data = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if isinstance(value, Enum):
                data[field.name] = value.value
            elif is_dataclass(value):
                data[field.name] = value.to_dict()
            elif isinstance(value, list):
                data[field.name] = [i.to_dict() if is_dataclass(i) else i for i in value]
            else:
                data[field.name] = value
        return data


    @classmethod
    def from_dict(Class: Type[T], data: dict) -> T:
        data = data or {}
        init_data = {}

        for field in fields(Class):
            value = data.get(field.name)
            field_type = field.type
            origin = get_origin(field_type)

            if isinstance(value, dict) and isinstance(field_type, type) and issubclass(field_type, DataManager):
                init_data[field.name] = field_type.from_dict(value)

            elif origin == list:
                inner_type = get_args(field_type)[0]
                if isinstance(inner_type, type) and issubclass(inner_type, DataManager):
                    init_data[field.name] = [inner_type.from_dict(
                        v) if isinstance(v, dict) else v for v in (value or [])]
                else:
                    init_data[field.name] = value or []

            elif origin == Union:
                args = get_args(field_type)
                dict_type = next((a for a in args if isinstance(
                    a, type) and issubclass(a, DataManager)), None)
                if dict_type and isinstance(value, dict):
                    init_data[field.name] = dict_type.from_dict(value)
                else:
                    init_data[field.name] = value

            else:
                init_data[field.name] = value

        return Class(**init_data)

    def json(self):
        def clear(object):
            if isinstance(object, dict):
                return {key: clear(value) for key, value in object.items() if value is not None}
            elif isinstance(object, list):
                return [clear(i) for i in object if i is not None]
            else:
                return object

        data = self.to_dict()
        data.pop("client", None)
        clean_data = clear(data)
        return dumps(clean_data, ensure_ascii=False, indent=4)


@dataclass
class Chat(DataManager):
    chat_id: Optional[str] = None
    chat_type: Optional[enums.ChatType] = None
    user_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    username: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class File(DataManager):
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    size: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class ForwardedFrom(DataManager):
    type_from: Optional[enums.ForwardedFrom] = None
    message_id: Optional[str] = None
    from_chat_id: Optional[str] = None
    from_sender_id: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class PaymentStatus(DataManager):
    payment_id: Optional[str] = None
    status: Optional[enums.PaymentStatus] = None

    def __repr__(self):
        return self.json()


@dataclass
class MessageTextUpdate(DataManager):
    message_id: Optional[str] = None
    text: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class Bot(DataManager):
    bot_id: Optional[str] = None
    bot_title: Optional[str] = None
    avatar: Optional[File] = None
    description: Optional[str] = None
    username: Optional[str] = None
    start_message: Optional[str] = None
    share_url: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class BotCommand(DataManager):
    command: Optional[str] = None
    description: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class Sticker(DataManager):
    sticker_id: Optional[str] = None
    file: Optional[File] = None
    emoji_character: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class ContactMessage(DataManager):
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class PollStatus(DataManager):
    state: Optional[enums.PollStatus] = None
    selection_index: Optional[int] = None
    percent_vote_options: Optional[list[int]] = None
    total_vote: Optional[int] = None
    show_total_votes: Optional[bool] = None

    def __repr__(self):
        return self.json()


@dataclass
class Poll(DataManager):
    question: Optional[str] = None
    options: Optional[list[str]] = None
    poll_status: Optional[PollStatus] = None

    def __repr__(self):
        return self.json()


@dataclass
class Location(DataManager):
    longitude: Optional[str] = None
    latitude: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class LiveLocation(DataManager):
    start_time: Optional[str] = None
    live_period: Optional[int] = None
    current_location: Optional[Location] = None
    user_id: Optional[str] = None
    status: Optional[enums.LiveLocationStatus] = None
    last_update_time: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class ButtonSelectionItem(DataManager):
    text: Optional[str] = None
    image_url: Optional[str] = None
    type: Optional[enums.ButtonSelectionType] = None

    def __repr__(self):
        return self.json()


@dataclass
class ButtonSelection(DataManager):
    selection_id: Optional[str] = None
    search_type: Optional[str] = None
    get_type: Optional[str] = None
    items: Optional[list[ButtonSelectionItem]] = None
    is_multi_selection: Optional[bool] = None
    columns_count: Optional[str] = None
    title: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class ButtonCalendar(DataManager):
    default_value: Optional[str] = None
    type: Optional[enums.ButtonCalendarType] = None
    min_year: Optional[str] = None
    max_year: Optional[str] = None
    title: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class ButtonNumberPicker(DataManager):
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    default_value: Optional[str] = None
    title: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class ButtonStringPicker(DataManager):
    items: Optional[list[str]] = None
    default_value: Optional[str] = None
    title: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class ButtonTextbox(DataManager):
    type_line: Optional[enums.ButtonTextboxTypeLine] = None
    type_keypad: Optional[enums.ButtonTextboxTypeKeypad] = None
    place_holder: Optional[str] = None
    title: Optional[str] = None
    default_value: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class ButtonLocation(DataManager):
    default_pointer_location: Optional[Location] = None
    default_map_location: Optional[Location] = None
    type: Optional[enums.ButtonLocationType] = None
    title: Optional[str] = None
    location_image_url: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class OpenChatData(DataManager):
    object_guid: Optional[str] = None
    object_type: Optional[enums.ChatType] = None

    def __repr__(self):
        return self.json()


@dataclass
class JoinChannelData(DataManager):
    username: Optional[str] = None
    ask_join: bool = False

    def __repr__(self):
        return self.json()


@dataclass
class ButtonLink(DataManager):
    type: Optional[enums.ButtonLinkType] = None
    link_url: Optional[str] = None
    joinchannel_data: Optional[JoinChannelData] = None
    open_chat_data: Optional[OpenChatData] = None

    def __repr__(self):
        return self.json()


@dataclass
class AuxData(DataManager):
    start_id: Optional[str] = None
    button_id: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class Button(DataManager):
    id: Optional[str] = None
    button_text: Optional[str] = None
    type: enums.ButtonType = enums.ButtonType.Simple
    button_selection: Optional[ButtonSelection] = None
    button_calendar: Optional[ButtonCalendar] = None
    button_number_picker: Optional[ButtonNumberPicker] = None
    button_string_picker: Optional[ButtonStringPicker] = None
    button_location: Optional[ButtonLocation] = None
    button_textbox: Optional[ButtonTextbox] = None
    button_link: Optional[ButtonLink] = None


@dataclass
class KeypadRow(DataManager):
    buttons: list[Button]

    def __repr__(self):
        return self.json()


@dataclass
class Keypad(DataManager):
    rows: list[KeypadRow]
    resize_keyboard: bool = True
    on_time_keyboard: bool = False

    def __repr__(self):
        return self.json()


@dataclass
class MessageKeypadUpdate(DataManager):
    message_id: Optional[str] = None
    inline_keypad: Optional[Keypad] = None

    def __repr__(self):
        return self.json()


@dataclass
class Message(DataManager):
    message_id: Optional[str] = None
    text: Optional[str] = None
    time: Optional[str] = None
    is_edited: Optional[bool] = None
    sender_type: Optional[enums.MessageSender] = None
    sender_id: Optional[str] = None
    aux_data: Optional[AuxData] = None
    file: Optional[File] = None
    reply_to_message_id: Optional[str] = None
    forwarded_from: Optional[ForwardedFrom] = None
    forwarded_no_link: Optional[str] = None
    location: Optional[Location] = None
    sticker: Optional[Sticker] = None
    contact_message: Optional[ContactMessage] = None
    poll: Optional[Poll] = None
    live_location: Optional[LiveLocation] = None

    def __repr__(self):
        return self.json()


@dataclass
class MessageId(DataManager):
    message_id: Optional[str] = None
    file_id: Optional[str] = None
    chat_id: Optional[str] = None
    client: Optional["rubigram.Client"] = None

    def __repr__(self):
        return self.json()

    async def delete(self):
        return await self.client.delete_message(self.chat_id, self.message_id)

    async def edit_text(self, text: str):
        return await self.client.edit_message_text(self.chat_id, self.message_id, text)

    async def edit_message_keypad(self, keypad: Keypad):
        return await self.client.edit_message_keypad(self.chat_id, self.message_id, keypad)

    async def forward(self, chat_id: str):
        return await self.client.forward_message(self.chat_id, self.message_id, chat_id)


@dataclass
class Update(DataManager):
    client: Optional["rubigram.Client"] = None
    type: Optional[enums.UpdateType] = None
    chat_id: Optional[str] = None
    removed_message_id: Optional[str] = None
    new_message: Optional[Message] = None
    updated_message: Optional[Message] = None
    updated_payment: Optional[PaymentStatus] = None

    def __repr__(self):
        return self.json()

    async def download(self, file_name: str):
        return await self.client.download_file(self.new_message.file.file_id, file_name)

    async def reply(
        self,
        text: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = None,
    ) -> "MessageId":
        return await self.client.send_message(self.chat_id, text, chat_keypad, inline_keypad, chat_keypad_type, disable_notification, self.new_message.message_id)
    
    async def reply_poll(
        self,
        question: str,
        options: list[str],
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False
    ) -> "MessageId":
        return await self.client.send_poll(self.chat_id, question, options, chat_keypad, inline_keypad, chat_keypad_type, disable_notification, self.new_message.message_id)
    
    async def reply_location(
        self,
        latitude: str,
        longitude: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_location(self.chat_id, latitude, longitude, chat_keypad, inline_keypad, chat_keypad_type, disable_notification, self.new_message.message_id)
    
    async def reply_contact(
        self,
        first_name: str,
        last_name: str,
        phone_number: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_location(self.chat_id, first_name, last_name, phone_number, chat_keypad, inline_keypad, chat_keypad_type, disable_notification, self.new_message.message_id)
    
    async def reply_sticker(
        self,
        sticker_id: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_message(self.chat_id, sticker_id, chat_keypad, inline_keypad, chat_keypad_type, disable_notification, self.new_message.message_id)

    async def reply_file(
        self,
        file: str,
        file_name: str,
        caption: str = None,
        type: enums.FileType = enums.FileType.File,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_file(self.chat_id, file, file_name, caption, type, chat_keypad, inline_keypad, chat_keypad_type, disable_notification, self.new_message.message_id)

    async def reply_document(self, document: str, name: str, caption: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(document, name, caption, "File", **kwargs)

    async def reply_photo(self, photo: str, name: str, caption: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(photo, name, caption, "Image", **kwargs)

    async def reply_video(self, video: str, name: str, caption: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(video, name, caption, "Video", **kwargs)

    async def reply_gif(self, gif: str, name: str, caption: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(gif, name, caption, "Gif", **kwargs)

    async def reply_music(self, music: str, name: str, caption: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(music, name, caption, "Music", **kwargs)

    async def reply_voice(self, voice: str, name: str, caption: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(voice, name, caption, "Voice", **kwargs)


@dataclass
class Updates(DataManager):
    updates: list[Update] = None
    next_offset_id: Optional[str] = None

    def __repr__(self):
        return self.json()


@dataclass
class InlineMessage(DataManager):
    client: Optional["rubigram.Client"] = None
    sender_id: Optional[str] = None
    text: Optional[str] = None
    message_id: Optional[str] = None
    chat_id: Optional[str] = None
    file: Optional[File] = None
    location: Optional[Location] = None
    aux_data: Optional[AuxData] = None

    def __repr__(self):
        return self.json()