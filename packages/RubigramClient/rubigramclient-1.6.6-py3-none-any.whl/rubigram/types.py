from typing import Optional, Any
from pydantic import BaseModel
from rubigram import enums


class DataManager(BaseModel):
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True

    @classmethod
    def from_dict(cls, data: dict):
        return cls.model_validate(data or {})

    def asdict(self, exclude_none: bool = True) -> dict:
        return self.model_dump(exclude_none=exclude_none, exclude={"client"})

    def asjson(self, exclude_none: bool = True) -> str:
        return self.model_dump_json(indent=4, exclude_none=exclude_none, exclude={"client"})


class Chat(DataManager):
    chat_id: Optional[str] = None
    chat_type: Optional[enums.ChatType] = None
    user_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    username: Optional[str] = None


class File(DataManager):
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    size: Optional[str] = None


class ForwardedFrom(DataManager):
    type_from: Optional[enums.ForwardedFrom] = None
    message_id: Optional[str] = None
    from_chat_id: Optional[str] = None
    from_sender_id: Optional[str] = None


class PaymentStatus(DataManager):
    payment_id: Optional[str] = None
    status: Optional[enums.PaymentStatus] = None


class MessageTextUpdate(DataManager):
    message_id: Optional[str] = None
    text: Optional[str] = None


class Bot(DataManager):
    bot_id: Optional[str] = None
    bot_title: Optional[str] = None
    avatar: Optional[File] = None
    description: Optional[str] = None
    username: Optional[str] = None
    start_message: Optional[str] = None
    share_url: Optional[str] = None


class BotCommand(DataManager):
    command: Optional[str] = None
    description: Optional[str] = None


class Sticker(DataManager):
    sticker_id: Optional[str] = None
    file: Optional[File] = None
    emoji_character: Optional[str] = None


class ContactMessage(DataManager):
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class PollStatus(DataManager):
    state: Optional[enums.PollStatus] = None
    selection_index: Optional[int] = None
    percent_vote_options: Optional[list[int]] = None
    total_vote: Optional[int] = None
    show_total_votes: Optional[bool] = None


class Poll(DataManager):
    question: Optional[str] = None
    options: Optional[list[str]] = None
    poll_status: Optional[PollStatus] = None


class Location(DataManager):
    longitude: Optional[str] = None
    latitude: Optional[str] = None


class LiveLocation(DataManager):
    start_time: Optional[str] = None
    live_period: Optional[int] = None
    current_location: Optional[Location] = None
    user_id: Optional[str] = None
    status: Optional[enums.LiveLocationStatus] = None
    last_update_time: Optional[str] = None


class ButtonSelectionItem(DataManager):
    text: Optional[str] = None
    image_url: Optional[str] = None
    type: Optional[enums.ButtonSelectionType] = None


class ButtonSelection(DataManager):
    selection_id: Optional[str] = None
    search_type: Optional[str] = None
    get_type: Optional[str] = None
    items: Optional[list[ButtonSelectionItem]] = None
    is_multi_selection: Optional[bool] = None
    columns_count: Optional[str] = None
    title: Optional[str] = None


class ButtonCalendar(DataManager):
    default_value: Optional[str] = None
    type: Optional[enums.ButtonCalendarType] = None
    min_year: Optional[str] = None
    max_year: Optional[str] = None
    title: Optional[str] = None


class ButtonNumberPicker(DataManager):
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    default_value: Optional[str] = None
    title: Optional[str] = None


class ButtonStringPicker(DataManager):
    items: Optional[list[str]] = None
    default_value: Optional[str] = None
    title: Optional[str] = None


class ButtonTextbox(DataManager):
    type_line: Optional[enums.ButtonTextboxTypeLine] = None
    type_keypad: Optional[enums.ButtonTextboxTypeKeypad] = None
    place_holder: Optional[str] = None
    title: Optional[str] = None
    default_value: Optional[str] = None


class ButtonLocation(DataManager):
    default_pointer_location: Optional[Location] = None
    default_map_location: Optional[Location] = None
    type: Optional[enums.ButtonLocationType] = None
    title: Optional[str] = None
    location_image_url: Optional[str] = None


class OpenChatData(DataManager):
    object_guid: Optional[str] = None
    object_type: Optional[enums.ChatType] = None


class JoinChannelData(DataManager):
    username: Optional[str] = None
    ask_join: bool = False


class ButtonLink(DataManager):
    type: Optional[enums.ButtonLinkType] = None
    link_url: Optional[str] = None
    joinchannel_data: Optional[JoinChannelData] = None
    open_chat_data: Optional[OpenChatData] = None


class AuxData(DataManager):
    start_id: Optional[str] = None
    button_id: Optional[str] = None


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


class KeypadRow(DataManager):
    buttons: list[Button]


class Keypad(DataManager):
    rows: list[KeypadRow]
    resize_keyboard: bool = True
    on_time_keyboard: bool = False


class MessageKeypadUpdate(DataManager):
    message_id: Optional[str] = None
    inline_keypad: Optional[Keypad] = None


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


class MessageId(DataManager):
    message_id: Optional[str] = None
    file_id: Optional[str] = None
    chat_id: Optional[str] = None
    client: Optional[Any] = None

    async def delete(self):
        return await self.client.delete_message(self.chat_id, self.message_id)

    async def edit_text(self, text: str):
        return await self.client.edit_message_text(self.chat_id, self.message_id, text)

    async def edit_message_keypad(self, keypad: Keypad):
        return await self.client.edit_message_keypad(self.chat_id, self.message_id, keypad)

    async def forward(self, chat_id: str):
        return await self.client.forward_message(self.chat_id, self.message_id, chat_id)


class Update(DataManager):
    client: Optional[Any] = None
    type: Optional[enums.UpdateType] = None
    chat_id: Optional[str] = None
    removed_message_id: Optional[str] = None
    new_message: Optional[Message] = None
    updated_message: Optional[Message] = None
    updated_payment: Optional[PaymentStatus] = None

    async def download(self, file_name: str):
        return await self.client.download_file(self.new_message.file.file_id, file_name)

    async def forward(self, chat_id: str):
        return await self.client.forward_message(self.chat_id, self.new_message.message_id, chat_id)

    async def reply(
        self,
        text: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = None,
    ) -> "MessageId":
        return await self.client.send_message(
            self.chat_id,
            text,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id,
        )

    async def reply_poll(
        self,
        question: str,
        options: list[str],
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_poll(
            self.chat_id,
            question,
            options,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id,
        )

    async def reply_location(
        self,
        latitude: str,
        longitude: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_location(
            self.chat_id,
            latitude,
            longitude,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id,
        )

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
        return await self.client.send_location(
            self.chat_id,
            first_name,
            last_name,
            phone_number,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id,
        )

    async def reply_sticker(
        self,
        sticker_id: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_message(
            self.chat_id,
            sticker_id,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id,
        )

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
        return await self.client.send_file(
            self.chat_id,
            file,
            file_name,
            caption,
            type,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id,
        )

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


class Updates(DataManager):
    updates: Optional[list[Update]] = None
    next_offset_id: Optional[str] = None


class InlineMessage(DataManager):
    client: Optional[Any] = None
    sender_id: Optional[str] = None
    text: Optional[str] = None
    message_id: Optional[str] = None
    chat_id: Optional[str] = None
    file: Optional[File] = None
    location: Optional[Location] = None
    aux_data: Optional[AuxData] = None