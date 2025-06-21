import time
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from BrandrdXMusic import app
from BrandrdXMusic.misc import _boot_
from BrandrdXMusic.plugins.sudo.sudoers import sudoers_list
from BrandrdXMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from BrandrdXMusic.utils.decorators.language import LanguageStart
from BrandrdXMusic.utils.formatters import get_readable_time
from BrandrdXMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    await message.react("❤️")  # Changed to a Telegram-supported emoji

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            await message.reply_sticker("CAACAgUAAxkBAAEQI1RlTLnRAy4h9lOS6jgS5FYsQoruOAAC1gMAAg6ryVcldUr_lhPexzME")
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
            return
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
    else:
        try:
            out = private_panel(_)
            # Initial welcome animation with more emojis
            lol = await message.reply_text(f"💕 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐌𝐲 𝐋𝐨𝐯𝐞 {message.from_user.mention} 💕 ❣️")
            await lol.edit_text(f"🌸 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐌𝐲 𝐋𝐨𝐯𝐞 {message.from_user.mention} 🌸 🥳")
            await lol.edit_text(f"💖 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐌𝐲 𝐋𝐨𝐯𝐞 {message.from_user.mention} 💖 💥")
            await lol.edit_text(f"✨ 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐌𝐲 𝐋𝐨𝐯𝐞 {message.from_user.mention} ✨ 🤩")
            await lol.edit_text(f"💞 W𝐞𝐥𝐜𝐨𝐦𝐞 𝐌𝐲 𝐋𝐨𝐯𝐞 {message.from_user.mention} 💞 💌")
            await lol.edit_text(f"🌟 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐌𝐲 𝐋𝐨𝐯𝐞 {message.from_user.mention} 🌟 💕")
            await lol.delete()

            # Gradient-style starting animation
            lols = await message.reply_text("✨💖")
            await asyncio.sleep(0.1)
            await lols.edit_text("✨💖 𝐒")
            await asyncio.sleep(0.1)
            await lols.edit_text("🌟💕 𝐒𝐭")
            await asyncio.sleep(0.1)
            await lols.edit_text("💫❤️ 𝐒𝐭𝐚")
            await asyncio.sleep(0.1)
            await lols.edit_text("🌸💞 𝐒𝐭𝐚𝐫")
            await asyncio.sleep(0.1)
            await lols.edit_text("💖✨ 𝐒𝐭𝐚𝐫𝐭")
            await asyncio.sleep(0.1)
            await lols.edit_text("🌟💕 𝐒𝐭𝐚𝐫𝐭𝐢")
            await asyncio.sleep(0.1)
            await lols.edit_text("💫❤️ 𝐒𝐭𝐚𝐫𝐭𝐢𝐧")
            await asyncio.sleep(0.1)
            await lols.edit_text("🌸💞 S𝐭𝐚𝐫𝐭𝐢𝐧𝐠")
            await asyncio.sleep(0.1)
            await lols.edit_text("💖✨ 𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠 🌟")
            await asyncio.sleep(0.1)
            await lols.edit_text("🌟💕 𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠 ✨")
            await asyncio.sleep(0.1)
            await lols.edit_text("💫❤️ 𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠 💖")
            await lols.edit_text("🌸💞 𝐒𝐭𝐚𝐫𝐭𝐢n𝐠 💞")

            # Father is coming animation
            father = await message.reply_text("⚡")
            await asyncio.sleep(0.1)
            await father.edit_text("⚡ W")
            await asyncio.sleep(0.1)
            await father.edit_text("✨ Wᴀ")
            await asyncio.sleep(0.1)
            await father.edit_text("🔥 Wᴀɪ")
            await asyncio.sleep(0.1)
            await father.edit_text("⚡ Wᴀɪᴛ")
            await asyncio.sleep(0.1)
            await father.edit_text("✨ Wᴀɪᴛ...")
            await asyncio.sleep(0.1)
            await father.edit_text("🔥 Wᴀɪᴛ... F")
            await asyncio.sleep(0.1)
            await father.edit_text("⚡ Wᴀɪᴛ... Fᴀ")
            await asyncio.sleep(0.1)
            await father.edit_text("✨ Wᴀɪᴛ... Fᴀᴛ")
            await asyncio.sleep(0.1)
            await father.edit_text("🔥 Wᴀɪᴛ... Fᴀᴛʜ")
            await asyncio.sleep(0.1)
            await father.edit_text("⚡ Wᴀɪᴛ... Fᴀᴛʜᴇ")
            await asyncio.sleep(0.1)
            await father.edit_text("✨ Wᴀɪᴛ... Fᴀᴛʜᴇʀ")
            await asyncio.sleep(0.1)
            await father.edit_text("🔥 Wᴀɪᴛ... Fᴀᴛʜᴇʀ I")
            await asyncio.sleep(0.1)
            await father.edit_text("⚡ Wᴀɪᴛ... Fᴀᴛʜᴇʀ Iꜱ")
            await asyncio.sleep(0.1)
            await father.edit_text("✨ Wᴀɪᴛ... Fᴀᴛʜᴇʀ Iꜱ C")
            await asyncio.sleep(0.1)
            await father.edit_text("🔥 Wᴀɪᴛ... Fᴀᴛʜᴇʀ Iꜱ Cᴏ")
            await asyncio.sleep(0.1)
            await father.edit_text("⚡ Wᴀɪᴛ... Fᴀᴛʜᴇʀ Iꜱ Cᴏᴍ")
            await asyncio.sleep(0.1)
            await father.edit_text("✨ Wᴀɪᴛ... Fᴀᴛʜᴇʀ Iꜱ Cᴏᴍɪ")
            await asyncio.sleep(0.1)
            await father.edit_text("🔥 Wᴀɪᴛ... Fᴀᴛʜᴇʀ Iꜱ Cᴏᴍɪɴ")
            await asyncio.sleep(0.1)
            await father.edit_text("⚡ Wᴀɪᴛ... Fᴀᴛʜᴇʀ Iꜱ Cᴏᴍɪɴɢ")
            await asyncio.sleep(0.1)
            await father.edit_text("✨ Wᴀɪᴛ... Fᴀᴛʜᴇʀ Iꜱ Cᴏᴍɪɴɢ 🔥")
            await asyncio.sleep(0.1)
            await father.edit_text("🔥 Wᴀɪᴛ... Fᴀᴛʜᴇʀ Iꜱ Cᴏᴍɪɴɢ ⚡")
            await asyncio.sleep(0.1)
            await father.edit_text("⚡ Wᴀɪᴛ... Fᴀᴛʜᴇʀ Iꜱ Cᴏᴍɪɴɢ ✨")
            await asyncio.sleep(0.1)
            await father.delete()

            # Sparkle and heart animation
            sparkle = await message.reply_text("✨💖✨")
            await asyncio.sleep(0.5)
            await sparkle.edit_text("💖💫💖")
            await asyncio.sleep(0.5)
            await sparkle.edit_text("💞🌸💞")
            await asyncio.sleep(0.5)
            await sparkle.delete()

            # Sticker
            m = await message.reply_sticker("CAACAgUAAxkBAAEQI1BlTLmx7PtOO3aPNshEU2gCy7iAFgACNQUAApqMuVeA6eJ50VbvmDME")

            # Get user photo or default
            if message.chat.photo:
                userss_photo = await app.download_media(
                    message.chat.photo.big_file_id,
                )
            else:
                userss_photo = "assets/nodp.png"
            if userss_photo:
                chat_photo = userss_photo
            chat_photo = userss_photo if userss_photo else config.START_IMG_URL

        except AttributeError:
            chat_photo = "assets/nodp.png"

        await lols.delete()
        await m.delete()

        # Final welcome message with dynamic user mention and animation text
        photo_caption = (
            f"нєу {message.from_user.mention}, 🥀\n\n"
            f"๏ ᴛʜɪs ɪs test !\n\n"
            f"➻ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.\n\n"
            f"Sᴜᴘᴘᴏʀᴛᴇᴅ Pʟᴀᴛғᴏʀᴍs : ʏᴏᴜᴛᴜʙᴇ, sᴘᴏᴛɪғʏ, ʀᴇssᴏ, ᴀᴘᴘʟᴇ ᴍᴜsɪᴄ ᴀɴᴅ sᴏᴜɴᴅᴄʟᴏᴜᴅ.\n"
            f"──────────────────\n"
            f"⚡ Wᴀɪᴛ... Fᴀᴛʜᴇʀ Iꜱ Cᴏᴍɪɴɢ ✨\n"
            f"๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs."
        )
        await message.reply_photo(
            photo=chat_photo,
            caption=photo_caption,
            reply_markup=InlineKeyboardMarkup(out),
        )

        # Skip logging if LOGGER_ID is not defined
        if hasattr(config, 'LOGGER_ID') and await is_on_off(2):
            sender_id = message.from_user.id
            sender_name = message.from_user.first_name
            return await app.send_message(
                config.LOGGER_ID,
                f"{message.from_user.mention} ʜᴀs sᴛᴀʀᴛᴇᴅ ʙᴏᴛ. \n\n**ᴜsᴇʀ ɪᴅ :** {sender_id}\n**ᴜsᴇʀ ɴᴀᴍᴇ:** {sender_name}",
            )

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)
