from BrandrdXMusic import app
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from os import environ
from typing import Union, Optional
from PIL import Image, ImageDraw, ImageFont
import asyncio
from datetime import datetime

# --------------------------------------------------------------------------------- #

get_font = lambda font_size, font_path: ImageFont.truetype(font_path, font_size)
resize_text = (
    lambda text_size, text: (text[:text_size] + "...").upper()
    if len(text) > text_size
    else text.upper()
)

# --------------------------------------------------------------------------------- #

async def get_userinfo_img(
    bg_path: str,
    font_path: str,
    user_id: Union[int, str],
    profile_path: Optional[str] = None
):
    bg = Image.open(bg_path)

    if profile_path:
        img = Image.open(profile_path)
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.pieslice([(0, 0), img.size], 0, 360, fill=255)

        circular_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask)
        resized = circular_img.resize((400, 400))
        bg.paste(resized, (440, 160), resized)

    img_draw = ImageDraw.Draw(bg)

    img_draw.text(
        (529, 627),
        text=str(user_id).upper(),
        font=get_font(46, font_path),
        fill=(255, 255, 255),
    )

    path = f"./userinfo_img_{user_id}.png"
    bg.save(path)
    return path

# --------------------------------------------------------------------------------- #

bg_path = "BrandrdXMusic/assets/userinfo.png"
font_path = "BrandrdXMusic/assets/hiroko.ttf"

# --------------------------------------------------------------------------------- #

@app.on_chat_member_updated(filters.group, group=20)
async def member_has_left(client: app, member: ChatMemberUpdated):
    if (
        not member.new_chat_member
        and member.old_chat_member.status not in {
            "banned", "left", "restricted"
        }
        and member.old_chat_member
    ):
        pass
    else:
        return

    user = (
        member.old_chat_member.user
        if member.old_chat_member
        else member.from_user
    )

    # Get last seen (approximate, based on available data)
    last_seen = "Unknown"
    if user.status:
        if user.status == "online":
            last_seen = "Online"
        elif user.status == "offline":
            last_seen = datetime.fromtimestamp(user.status.date).strftime("%Y-%m-%d %H:%M:%S")
    bio = getattr(user, 'bio', "None")  # Safely handle bio attribute

    # Check if the user has a profile photo
    if user.photo and user.photo.big_file_id:
        try:
            # Download profile photo
            photo = await app.download_media(user.photo.big_file_id)

            welcome_photo = await get_userinfo_img(
                bg_path=bg_path,
                font_path=font_path,
                user_id=user.id,
                profile_path=photo,
            )
        
            # Use username if available, otherwise use user_id link
            redirect_link = f"tg://resolve?domain={user.username}" if user.username else f"tg://openmessage?user_id={user.id}"
            button_text = "๏ ᴠɪᴇᴡ ᴜsᴇʀ ๏"

            caption = (
                f"➻ ᴜsᴇʀ ɪᴅ ‣ {user.id}\n"
                f"➻ ғɪʀsᴛ ɴᴀᴍᴇ ‣ {user.first_name}\n"
                f"➻ ʟᴀsᴛ ɴᴀᴍᴇ ‣ {user.last_name if user.last_name else 'None'}\n"
                f"➻ ᴜsᴇʀɴᴀᴍᴇ ‣ @{user.username if user.username else 'None'}\n"
                f"➻ ᴍᴇɴᴛɪᴏɴ ‣ {user.mention}\n"
                f"➻ ʟᴀsᴛ sᴇᴇɴ ‣ {last_seen}\n"
                f"➻ ᴅᴄ ɪᴅ ‣ {user.dc_id if user.dc_id else 'Unknown'}\n"
                f"➻ ʙɪᴏ ‣ {bio}\n"
                f"➻ ᴛᴇʟᴇɢʀᴀᴍ ᴘʀᴇᴍɪᴜᴍ ‣ {'True' if user.is_premium else 'False'}\n"
                f"➖➖➖➖➖➖➖➖➖➖➖\n"
                f"๏ 𝐌𝐀𝐃𝐄 𝐁𝐘 ➠ [Aʙнɪ 𓆩🇽𓆪 �_KI𝗡𝗚 📿](https://t.me/imagine_iq)"
            )

            # Send the message with the photo, caption, and button
            message = await client.send_photo(
                chat_id=member.chat.id,
                photo=welcome_photo,
                caption=caption,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(button_text, url=redirect_link)]
                ])
            )

            # Schedule a task to delete the message after 20 seconds
            async def delete_message():
                await asyncio.sleep(20)
                await message.delete()

            # Run the task
            asyncio.create_task(delete_message())
            
        except RPCError as e:
            print(e)
            return
    else:
        # Handle the case where the user has no profile photo
        print(f"User {user.id} has no profile photo.")