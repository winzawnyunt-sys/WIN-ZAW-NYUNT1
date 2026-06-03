# -*- coding: utf-8 -*-
# Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os, string, logging, random, asyncio, time, datetime, re, sys, json, base64
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import *
from database.ia_filterdb import col, sec_col, get_file_details, unpack_new_file_id, get_bad_files
from database.users_chats_db import db, delete_all_referal_users, get_referal_users_count, get_referal_all_users, referal_add_user
from database.join_reqs import JoinReqs
from info import CLONE_MODE, OWNER_LNK, REACTIONS, CHANNELS, REQUEST_TO_JOIN_MODE, TRY_AGAIN_BTN, ADMINS, SHORTLINK_MODE, PREMIUM_AND_REFERAL_MODE, STREAM_MODE, AUTH_CHANNEL, REFERAL_PREMEIUM_TIME, REFERAL_COUNT, PAYMENT_TEXT, PAYMENT_QR, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, CHNL_LNK, GRP_LNK, REQST_CHANNEL, SUPPORT_CHAT, MAX_B_TN, VERIFY, SHORTLINK_API, SHORTLINK_URL, TUTORIAL, VERIFY_TUTORIAL, IS_TUTORIAL, URL
from utils import get_settings, pub_is_subscribed, get_size, is_subscribed, save_group_settings, temp, verify_user, check_token, check_verification, get_token, get_shortlink, get_tutorial, get_seconds
from database.connections_mdb import active_connection
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
logger = logging.getLogger(__name__)

BATCH_FILES = {}
join_db = JoinReqs

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [[
            InlineKeyboardButton('⤬ Groupထဲသို့ ထည့်ရန် ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ],[
            InlineKeyboardButton('အကူအညီ', url=f'https://t.me/{SUPPORT_CHAT}'),
            InlineKeyboardButton('ရုပ်ရှင်Group', url=GRP_LNK)
        ],[
            InlineKeyboardButton('ချန်နယ်သို့ Join ရန်', url=CHNL_LNK)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup, disable_web_page_preview=True)
        await asyncio.sleep(2)
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        if PREMIUM_AND_REFERAL_MODE == True:
            buttons = [[
                InlineKeyboardButton('⤬ Groupထဲသို့ ထည့်ရန် ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
                InlineKeyboardButton('ငွေရှာရန်', callback_data="shortlink_info"),
                InlineKeyboardButton('ရုပ်ရှင်Group', url=GRP_LNK)
            ],[
                InlineKeyboardButton('အကူအညီ', callback_data='help'),
                InlineKeyboardButton('အကြောင်း', callback_data='about')
            ],[
                InlineKeyboardButton('ပရီမီယံနှင့် ရည်ညွှန်းချက်', callback_data='subscription')
            ],[
                InlineKeyboardButton('ချန်နယ်သို့ Join ရန်', url=CHNL_LNK)
            ]]
        else:
            buttons = [[
                InlineKeyboardButton('⤬ Groupထဲသို့ ထည့်ရန် ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
                InlineKeyboardButton('ငွေရှာရန်', callback_data="shortlink_info"),
                InlineKeyboardButton('ရုပ်ရှင်Group', url=GRP_LNK)
            ],[
                InlineKeyboardButton('အကူအညီ', callback_data='help'),
                InlineKeyboardButton('အကြောင်း', callback_data='about')
            ],[
                InlineKeyboardButton('ချန်နယ်သို့ Join ရန်', url=CHNL_LNK)
            ]]
        if CLONE_MODE == True:
            buttons.append([InlineKeyboardButton('ကိုယ်ပိုင်ဘော့တ် ဖန်တီးရန်', callback_data='clone')])
        reply_markup = InlineKeyboardMarkup(buttons)
        m=await message.reply_sticker("CAACAgUAAxkBAAEKVaxlCWGs1Ri6ti45xliLiUeweCnu4AACBAADwSQxMYnlHW4Ls8gQMAQ") 
        await asyncio.sleep(1)
        await m.delete()
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            if REQUEST_TO_JOIN_MODE == True:
                invite_link = await client.create_chat_invite_link(chat_id=(int(AUTH_CHANNEL)), creates_join_request=True)
            else:
                invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except Exception as e:
            print(e)
            await message.reply_text("ဘော့တ်ကို Channel မှာ Admin အရင်ပေးထားပါဦး။")
            return
        try:
            btn = [[InlineKeyboardButton("Backup Channel", url=invite_link.invite_link)]]
            if message.command[1] != "subscribe":
                if REQUEST_TO_JOIN_MODE == True:
                    if TRY_AGAIN_BTN == True:
                        try:
                            kk, file_id = message.command[1].split("_", 1)
                            btn.append([InlineKeyboardButton("↻ ပြန်ကြိုးစားရန်", callback_data=f"checksub#{kk}#{file_id}")])
                        except (IndexError, ValueError):
                            btn.append([InlineKeyboardButton("↻ ပြန်ကြိုးစားရန်", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
                else:
                    try:
                        kk, file_id = message.command[1].split("_", 1)
                        btn.append([InlineKeyboardButton("↻ ပြန်ကြိုးစားရန်", callback_data=f"checksub#{kk}#{file_id}")])
                    except (IndexError, ValueError):
                        btn.append([InlineKeyboardButton("↻ ပြန်ကြိုးစားရန်", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
            if TRY_AGAIN_BTN == True:
                text = "**🕵️ မင်းငါ့ရဲ့ Backup Channel ကို မ Join ရသေးဘူး။ အရင် Join ပြီးမှ ပြန်ကြိုးစားကြည့်ပါ။**"
            else:
                await db.set_msg_command(message.from_user.id, com=message.command[1])
                text = "**🕵️ မင်းငါ့ရဲ့ Backup Channel ကို မ Join ရသေးဘူး။ အရင် Join လိုက်ဦးနော်။**"
            await client.send_message(
                chat_id=message.from_user.id,
                text=text,
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        except Exception as e:
            print(e)
            return await message.reply_text("Force Subscribe မှာ အမှားတစ်ခုခု ဖြစ်နေတယ်။")
            
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        await message.reply_photo(photo=random.choice(PICS), caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME), reply_markup=None)
        return

    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("<b>ကျေးဇူးပြု၍ စောင့်ဆိုင်းပေးပါ...</b>")
        await sts.delete()
        k = await client.send_message(
            chat_id=message.from_user.id, 
            text=f"<blockquote><b><u>❗️❗️❗️အရေးကြီးသတိပေးချက်❗️❗️❗️</u></b>\n\n"
                 f"ဒီမက်ဆေ့ချ်ကို Copyright ပြဿနာကြောင့် <b><u>၁၀ မိနစ်</u></b> အတွင်း အလိုအလျောက် ဖျက်ပစ်မှာ ဖြစ်ပါတယ်။ 🫥\n\n"
                 f"<b><i>မပျောက်သွားအောင် မင်းရဲ့ Saved Messages (သို့) တခြား Private Chat တစ်ခုခုဆီသို့ အခုပဲ Forward လုပ်ထားပါ။</i></b></blockquote>"
        )
        await asyncio.sleep(600)
        for x in filesarr:
            await x.delete()
        await k.edit_text("<b>✅ မက်ဆေ့ချ်ကို အောင်မြင်စွာ ဖျက်လိုက်ပါပြီ။</b>")
        return
