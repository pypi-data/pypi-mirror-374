#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime
from typing import Dict, List, Optional, Union

import pyrogram
from pyrogram import raw, types, utils, enums

from ..object import Object


class Gift(Object):
    """A star gift.

    Parameters:
        id (``int``):
            Unique star gift identifier.

        sticker (:obj:`~pyrogram.types.Sticker`, *optional*):
            Information about the star gift sticker.

        caption (``str``, *optional*):
            Text message.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            For text messages, special entities like usernames, URLs, bot commands, etc. that appear in the text.

        message_id (``int``, *optional*):
            Unique message identifier.

        upgrade_message_id (``int``, *optional*):
            Unique message identifier.
            For unique gifts only.

        name (``str``, *optional*):
            Unique name of the upgraded gift that can be used with :meth:`~pyrogram.Client.send_resold_gift`.

        title (``str``, *optional*):
            The title of the upgraded gift

        collectible_id (``int``, *optional*):
            Collectible number of the star gift.
            For unique gifts only.

        attributes (List of :obj:`~pyrogram.types.GiftAttribute`, *optional*):
            Attributes of the star gift.
            For unique gifts only.

        date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the star gift was received.

        first_sale_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the star gift was first purchased.

        last_sale_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the star gift was last purchased.

        from_user (:obj:`~pyrogram.types.User`, *optional*):
            User who sent the star gift.

        owner (:obj:`~pyrogram.types.Chat`, *optional*):
            Current gift owner.

        owner_name (``str``, *optional*):
            Name of the user who received the star gift.

        owner_address (``str``, *optional*):
            Address of the gift owner in TON blockchain.

        gift_address (``str``, *optional*):
            Address of the gift in TON blockchain.

        price (``int``, *optional*):
            Price of this gift in stars.

        convert_price (``int``, *optional*):
            The number of stars you get if you convert this gift.

        upgrade_price (``int``, *optional*):
            The number of stars you need to upgrade this gift.

        transfer_price (``int``, *optional*):
            The number of stars you need to transfer this gift.

        resale_price (``int``, *optional*):
            Number of Telegram Stars that must be paid to buy the gift and send it to someone else.

        last_resale_star_count (``int``, *optional*):
            Number of Telegram Stars that were paid by the sender for the gift.

        last_resale_ton_count (``int``, *optional*):
            Number of TON that were paid by the sender for the gift.

        number (``int``, *optional*):
            Unique number of the upgraded gift among gifts upgraded from the same gift.

        available_resale_amount (``int``, *optional*):
            The number of gifts available for resale.
            Returned only if is_limited is True.

        available_amount (``int``, *optional*):
            The number of gifts available for purchase.
            Returned only if is_limited is True.

        total_amount (``int``, *optional*):
            Total amount of gifts.
            Returned only if is_limited is True.

        publisher_chat (:obj:`~pyrogram.types.Chat`, *optional*):
            Information about the chat that published the gift.

        can_upgrade (``bool``, *optional*):
            True, if the gift can be upgraded.

        can_export_at (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift can be exported via blockchain.

        can_transfer_at (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift can be transferred to another user.

        can_resell_at (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift can be resold.

        is_limited (``bool``, *optional*):
            True, if the number of gifts is limited.

        is_name_hidden (``bool``, *optional*):
            True, if the sender's name is hidden.

        is_saved (``bool``, *optional*):
            True, if the star gift is saved in profile.

        is_sold_out (``bool``, *optional*):
            True, if the star gift is sold out.

        is_converted (``bool``, *optional*):
            True, if the gift was converted to Telegram Stars.
            Only for the receiver of the gift.

        is_upgraded (``bool``, *optional*):
            True, if the gift was upgraded.

        is_refunded (``bool``, *optional*):
            True, if the gift was refunded.

        is_transferred (``bool``, *optional*):
            True, if the gift was transferred.

        is_birthday (``bool``, *optional*):
            True, if the gift is a birthday gift.

        is_pinned (``bool``, *optional*):
            True, if the gift is pinned.

        raw (:obj:`~pyrogram.raw.base.StarGift`, *optional*):
            The raw object as received from the server.

        link (``str``, *property*):
            A link to the gift.
            For unique gifts only.
    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        id: int,
        sticker: "types.Sticker" = None,
        caption: Optional[str] = None,
        caption_entities: List["types.MessageEntity"] = None,
        message_id: Optional[int] = None,
        date: Optional[datetime] = None,
        first_sale_date: Optional[datetime] = None,
        last_sale_date: Optional[datetime] = None,
        from_user: Optional["types.User"] = None,
        owner: Optional["types.Chat"] = None,
        owner_name: Optional[str] = None,
        owner_address: Optional[str] = None,
        gift_address: Optional[str] = None,
        price: Optional[int] = None,
        convert_price: Optional[int] = None,
        upgrade_price: Optional[int] = None,
        transfer_price: Optional[int] = None,
        resale_price: Optional[int] = None,
        last_resale_star_count: Optional[int] = None,
        last_resale_ton_count: Optional[int] = None,
        upgrade_message_id: Optional[int] = None,
        name: Optional[str] = None,
        title: Optional[str] = None,
        collectible_id: Optional[int] = None,
        attributes: Optional[List["types.GiftAttribute"]] = None,
        number: Optional[int] = None,
        available_resale_amount: Optional[int] = None,
        available_amount: Optional[int] = None,
        total_amount: Optional[int] = None,
        publisher_chat: Optional["types.Chat"] = None,
        can_upgrade: Optional[bool] = None,
        can_export_at: Optional[datetime] = None,
        can_transfer_at: Optional[datetime] = None,
        can_resell_at: Optional[datetime] = None,
        is_limited: Optional[bool] = None,
        is_name_hidden: Optional[bool] = None,
        is_saved: Optional[bool] = None,
        is_sold_out: Optional[bool] = None,
        is_converted: Optional[bool] = None,
        is_upgraded: Optional[bool] = None,
        is_refunded: Optional[bool] = None,
        is_transferred: Optional[bool] = None,
        is_birthday: Optional[bool] = None,
        is_pinned: Optional[bool] = None,
        raw: Optional["raw.base.StarGift"] = None
    ):
        super().__init__(client)

        self.id = id
        self.sticker = sticker
        self.caption = caption
        self.caption_entities = caption_entities
        self.message_id = message_id
        self.date = date
        self.first_sale_date = first_sale_date
        self.last_sale_date = last_sale_date
        self.from_user = from_user
        self.owner = owner
        self.owner_name = owner_name
        self.owner_address = owner_address
        self.gift_address = gift_address
        self.price = price
        self.convert_price = convert_price
        self.upgrade_price = upgrade_price
        self.transfer_price = transfer_price
        self.resale_price = resale_price
        self.last_resale_star_count = last_resale_star_count
        self.last_resale_ton_count = last_resale_ton_count
        self.upgrade_message_id = upgrade_message_id
        self.name = name
        self.title = title
        self.collectible_id = collectible_id
        self.attributes = attributes
        self.number = number
        self.available_resale_amount = available_resale_amount
        self.available_amount = available_amount
        self.total_amount = total_amount
        self.publisher_chat = publisher_chat
        self.can_upgrade = can_upgrade
        self.can_export_at = can_export_at
        self.can_transfer_at = can_transfer_at
        self.can_resell_at = can_resell_at
        self.is_limited = is_limited
        self.is_name_hidden = is_name_hidden
        self.is_saved = is_saved
        self.is_sold_out = is_sold_out
        self.is_converted = is_converted
        self.is_upgraded = is_upgraded
        self.is_refunded = is_refunded
        self.is_transferred = is_transferred
        self.is_birthday = is_birthday
        self.is_pinned = is_pinned
        self.raw = raw

    @staticmethod
    async def _parse(client, gift, users: Dict[int, "raw.base.User"] = {}, chats: Dict[int, "raw.base.Chat"] = {}):
        if isinstance(gift, raw.types.StarGift):
            return await Gift._parse_regular(client, gift, users, chats)
        elif isinstance(gift, raw.types.StarGiftUnique):
            return await Gift._parse_unique(client, gift, users, chats)
        elif isinstance(gift, raw.types.StarGiftSaved):
            return await Gift._parse_saved(client, gift, users, chats)

    @staticmethod
    async def _parse_regular(
        client,
        star_gift: "raw.types.StarGift",
        users: Dict[int, "raw.base.User"],
        chats: Dict[int, "raw.base.Chat"]
    ) -> "Gift":
        if not isinstance(star_gift, raw.types.StarGift):
            return

        doc = star_gift.sticker
        attributes = {type(i): i for i in doc.attributes}

        # TODO: resell_min_stars
        return Gift(
            id=star_gift.id,
            title=star_gift.title,
            sticker=await types.Sticker._parse(client, doc, attributes),
            price=star_gift.stars,
            convert_price=star_gift.convert_stars,
            upgrade_price=star_gift.upgrade_stars,
            available_amount=star_gift.availability_remains,
            available_resale_amount=star_gift.availability_resale,
            total_amount=star_gift.availability_total,
            is_limited=star_gift.limited,
            is_sold_out=star_gift.sold_out,
            is_birthday=star_gift.birthday,
            first_sale_date=utils.timestamp_to_datetime(star_gift.first_sale_date),
            last_sale_date=utils.timestamp_to_datetime(star_gift.last_sale_date),
            publisher_chat=types.Chat._parse_chat(client, chats.get(utils.get_raw_peer_id(star_gift.released_by))),
            raw=star_gift,
            client=client
        )

    @staticmethod
    async def _parse_unique(
        client,
        star_gift: "raw.types.StarGiftUnique",
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {}
    ) -> "Gift":
        if not isinstance(star_gift, raw.types.StarGiftUnique):
            return

        owner_id = utils.get_raw_peer_id(star_gift.owner_id)

        last_resale_star_count = None
        last_resale_ton_count = None

        if star_gift.resell_amount:
            for currency in star_gift.resell_amount:
                if isinstance(currency, raw.types.StarsAmount):
                    last_resale_star_count = currency.amount
                elif isinstance(currency, raw.types.StarsTonAmount):
                    last_resale_ton_count = currency.amount

        return Gift(
            id=star_gift.id,
            name=star_gift.slug,
            title=star_gift.title,
            collectible_id=star_gift.num,
            attributes=types.List(
                [await types.GiftAttribute._parse(client, attr, users, chats) for attr in star_gift.attributes]
            ) or None,
            number=star_gift.availability_issued,
            total_amount=star_gift.availability_total,
            owner=types.Chat._parse_chat(client, users.get(owner_id) or chats.get(owner_id)),
            owner_name=star_gift.owner_name,
            owner_address=star_gift.owner_address,
            gift_address=star_gift.gift_address,
            last_resale_star_count=last_resale_star_count,
            last_resale_ton_count=last_resale_ton_count,
            publisher_chat=types.Chat._parse_chat(client, chats.get(utils.get_raw_peer_id(star_gift.released_by))),
            is_upgraded=True,
            raw=star_gift,
            client=client
        )

    @staticmethod
    async def _parse_saved(
        client,
        saved_gift: "raw.types.SavedStarGift",
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {}
    ) -> "Gift":
        if not isinstance(saved_gift, raw.types.SavedStarGift):
            return

        caption, caption_entities = (
            utils.parse_text_with_entities(
                client, saved_gift.message, users
            )
        ).values()

        if isinstance(saved_gift.gift, raw.types.StarGift):
            parsed_gift = await Gift._parse_regular(client, saved_gift.gift, users, chats)
        elif isinstance(saved_gift.gift, raw.types.StarGiftUnique):
            parsed_gift = await Gift._parse_unique(client, saved_gift.gift, users, chats)

        parsed_gift.date = utils.timestamp_to_datetime(saved_gift.date)
        parsed_gift.is_name_hidden = saved_gift.name_hidden
        parsed_gift.is_saved = not saved_gift.unsaved
        parsed_gift.is_refunded = saved_gift.refunded
        parsed_gift.is_pinned = saved_gift.pinned_to_top
        parsed_gift.can_upgrade = saved_gift.can_upgrade
        parsed_gift.from_user = types.User._parse(client, users.get(utils.get_raw_peer_id(saved_gift.from_id)))
        parsed_gift.caption = caption
        parsed_gift.caption_entities = caption_entities
        parsed_gift.message_id = saved_gift.msg_id or saved_gift.saved_id
        parsed_gift.can_export_at = utils.timestamp_to_datetime(saved_gift.can_export_at)
        parsed_gift.convert_price = parsed_gift.convert_price or saved_gift.convert_stars
        parsed_gift.upgrade_price = parsed_gift.upgrade_price or saved_gift.upgrade_stars
        parsed_gift.transfer_price = parsed_gift.transfer_price or saved_gift.transfer_stars

        return parsed_gift

    @staticmethod
    async def _parse_action(
        client,
        message: "raw.base.Message",
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {}
    ) -> "Gift":
        action = message.action

        if isinstance(action, raw.types.MessageActionStarGift):
            parsed_gift = await Gift._parse_regular(client, action.gift, users, chats)

            caption, caption_entities = (
                utils.parse_text_with_entities(
                    client, action.message, users
                )
            ).values()

            parsed_gift.is_name_hidden = action.name_hidden
            parsed_gift.is_saved = action.saved
            parsed_gift.is_converted = action.converted
            parsed_gift.is_upgraded = action.upgraded
            parsed_gift.is_refunded = action.refunded
            parsed_gift.can_upgrade = action.can_upgrade
            parsed_gift.caption = caption
            parsed_gift.caption_entities = caption_entities
            parsed_gift.convert_price = action.convert_stars
            parsed_gift.upgrade_price = action.upgrade_stars
            parsed_gift.upgrade_message_id = action.upgrade_msg_id
        elif isinstance(action, raw.types.MessageActionStarGiftUnique):
            parsed_gift = await Gift._parse_unique(client, action.gift, users, chats)

            parsed_gift.is_upgraded = action.upgrade
            parsed_gift.is_transferred = action.transferred
            parsed_gift.is_saved = action.saved
            parsed_gift.is_refunded = action.refunded
            parsed_gift.can_export_at = utils.timestamp_to_datetime(action.can_export_at)
            parsed_gift.can_transfer_at = utils.timestamp_to_datetime(action.can_transfer_at)
            parsed_gift.can_resell_at = utils.timestamp_to_datetime(action.can_resell_at)
            parsed_gift.transfer_price = action.transfer_stars

            if action.resale_amount:
                if isinstance(action.resale_amount, raw.types.StarsAmount):
                    parsed_gift.last_resale_star_count = action.resale_amount.amount
                elif isinstance(action.resale_amount, raw.types.StarsTonAmount):
                    parsed_gift.last_resale_ton_count = action.resale_amount.amount

            parsed_gift.upgrade_message_id = message.id


        parsed_gift.date = utils.timestamp_to_datetime(message.date)
        parsed_gift.message_id = message.id

        return parsed_gift

    @property
    def link(self) -> Optional[str]:
        if not self.name:
            return None

        return f"https://t.me/nft/{self.name}"

    @property
    def owned_gift_id(self) -> Optional[str]:
        if self.owner and self.owner.type != enums.ChatType.PRIVATE:
            return f"{self.owner.id}_{self.message_id}"
        elif self.message_id:
            return str(self.message_id)

    async def show(self) -> bool:
        """Bound method *show* of :obj:`~pyrogram.types.Gift`.

        Use as a shortcut for:

        .. code-block:: python

            await client.show_gift(
                owned_gift_id="message_id"
            )

        Example:
            .. code-block:: python

                await gift.show()

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self._client.show_gift(
            owned_gift_id=self.owned_gift_id
        )

    async def hide(self) -> bool:
        """Bound method *hide* of :obj:`~pyrogram.types.Gift`.

        Use as a shortcut for:

        .. code-block:: python

            await client.hide_gift(
                owned_gift_id="message_id"
            )

        Example:
            .. code-block:: python

                await gift.hide()

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self._client.hide_gift(
            owned_gift_id=self.owned_gift_id
        )

    async def convert(self) -> bool:
        """Bound method *convert* of :obj:`~pyrogram.types.Gift`.

        .. note::

            For regular gifts only.

        Use as a shortcut for:

        .. code-block:: python

            await client.convert_gift_to_stars(
                owned_gift_id="message_id"
            )

        Example:
            .. code-block:: python

                await gift.convert()

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self._client.convert_gift_to_stars(
            owned_gift_id=self.owned_gift_id
        )

    async def upgrade(self, keep_original_details: Optional[bool] = None, star_count: Optional[int] = None) -> Optional["types.Message"]:
        """Bound method *upgrade* of :obj:`~pyrogram.types.Gift`.

        .. note::

            For regular gifts only.

        Use as a shortcut for:

        .. code-block:: python

            await client.upgrade_gift(
                owned_gift_id="message_id"
            )

        Example:
            .. code-block:: python

                await gift.upgrade()

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.
        """
        return await self._client.upgrade_gift(
            owned_gift_id=self.owned_gift_id,
            keep_original_details=keep_original_details,
            star_count=star_count
        )

    async def transfer(self, to_chat_id: Union[int, str]) -> Optional["types.Message"]:
        """Bound method *transfer* of :obj:`~pyrogram.types.Gift`.

        .. note::

            For upgraded gifts only.

        Use as a shortcut for:

        .. code-block:: python

            await client.transfer_gift(
                owned_gift_id="message_id",
                new_owner_chat_id=to_chat_id
            )

        Example:
            .. code-block:: python

                await gift.transfer(to_chat_id=123)

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.
        """
        return await self._client.transfer_gift(
            owned_gift_id=self.owned_gift_id,
            new_owner_chat_id=to_chat_id
        )

    async def wear(self) -> bool:
        """Bound method *wear* of :obj:`~pyrogram.types.Gift`.

        .. note::

            For upgraded gifts only.

        Use as a shortcut for:

        .. code-block:: python

            await client.set_emoji_status(types.EmojiStatus(gift_id=123))

        Example:
            .. code-block:: python

                await gift.wear()

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self._client.set_emoji_status(
            emoji_status=types.EmojiStatus(
                gift_id=self.id
            )
        )

    async def buy(self, new_owner_chat_id: Optional[Union[int, str]] = None, star_count: Optional[int] = None) -> Optional["types.Message"]:
        """Bound method *buy* of :obj:`~pyrogram.types.Gift`.

        .. note::

            For upgraded gifts from market only.

        Use as a shortcut for:

        .. code-block:: python

            await app.send_resold_gift(gift_link="https://t.me/nft/NekoHelmet-9215", new_owner_chat_id="me")

        Example:
            .. code-block:: python

                await gift.buy()

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.
        """
        if new_owner_chat_id is None:
            new_owner_chat_id = "me"

        return await self._client.send_resold_gift(
            gift_link=self.link,
            new_owner_chat_id=new_owner_chat_id,
            star_count=star_count
        )

    async def send(
        self,
        chat_id: Union[int, str],
        text: Optional[str] = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: Optional[List["types.MessageEntity"]] = None,
        is_private: Optional[bool] = None,
        pay_for_upgrade: Optional[bool] = None,
    ) -> Optional["types.Message"]:
        """Bound method *send* of :obj:`~pyrogram.types.Gift`.

        .. note::

            For regular gifts only.
            May return an error with a message "STARGIFT_USAGE_LIMITED" if the gift was sold out.

        Use as a shortcut for:

        .. code-block:: python

            await client.send_gift(
                chat_id="me",
                gift_id=gift.id
            )

        Example:
            .. code-block:: python

                await gift.send("me")

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.
        """
        return await self._client.send_gift(
            chat_id=chat_id,
            gift_id=self.id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            is_private=is_private,
            pay_for_upgrade=pay_for_upgrade
        )
