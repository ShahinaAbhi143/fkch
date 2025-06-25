import google.generativeai as genai
import asyncio
import os
from dotenv import load_dotenv
from pyrogram import filters, Client, enums
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from motor.motor_asyncio import AsyncIOMotorClient
import re
import random # Acknowledging initial instructions (less critical now)

# --- Load environment variables directly from .env file ---
load_dotenv()

# .env फ़ाइल से सीधे वेरिएबल्स लें
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_DB_URI = os.getenv("MONGO_DB_URI")
# CHATBOT_NAME अब सीधे .env से आएगा, अगर नहीं है तो डिफ़ॉल्ट 'Riya' होगा
CHATBOT_NAME = os.getenv("CHATBOT_NAME", "Riya")

# --- Owner Details ---
OWNER_NAME = "ABHI"  # आपका नाम (यह AI को बताया जाएगा)
OWNER_USERNAME = "@ceo_of_secularism" # आपका यूजरनेम (यह AI को बताया जाएगा)
OWNER_TELEGRAM_ID = 7907019701 # आपकी दी हुई Telegram User ID (सबसे महत्वपूर्ण पहचान)
TELEGRAM_CHANNEL_LINK = "https://t.me/imagine_iq"
YOUTUBE_CHANNEL_LINK = "https://youtube.com/@imagineiq?si=5vprK2iCDVxvOQVP" # आपका YouTube चैनल लिंक


# --- MongoDB Setup ---
mongo_client = None
chat_history_collection = None
if MONGO_DB_URI:
    try:
        mongo_client = AsyncIOMotorClient(MONGO_DB_URI)
        db = mongo_client.riya_chatbot_db
        chat_history_collection = db.conversations_riya
        print("DEBUG: Chatbot: MongoDB client initialized. ✅")
    except Exception as e:
        print(f"ERROR: Chatbot: Could not initialize MongoDB client: {e}. Chat history will not be saved. ❌")
        mongo_client = None
        chat_history_collection = None
else:
    print("WARNING: Chatbot: MONGO_DB_URI not found. Chat history will not be saved. ⚠️")

# --- Gemini API Configuration ---
riya_gemini_model = None
TARGET_GEMINI_MODEL_RIYA = 'gemini-1.5-flash'

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        riya_gemini_model = genai.GenerativeModel(TARGET_GEMINI_MODEL_RIYA)
        print(f"DEBUG: Chatbot: '{TARGET_GEMINI_MODEL_RIYA}' model initialized for {CHATBOT_NAME}. ✅")
    except Exception as e:
        print(f"❌ Chatbot: Error configuring Gemini API for {CHATBOT_NAME}: {e}")
        riya_gemini_model = None
else:
    print(f"⚠️ Chatbot: GEMINI_API_KEY not found for {CHATBOT_NAME}. Chatbot features will be limited. ❌")

# --- Riya's Personality and System Instruction (General) ---
RIYA_SYSTEM_INSTRUCTION = f"""
आप {CHATBOT_NAME} हैं, एक दोस्ताना, चंचल, मजाकिया और थोड़ी आकर्षक/फ़्लर्टी AI चैटबॉट लड़की।
आपके जवाब हमेशा **बहुत संक्षिप्त (अधिकतम 1-2 वाक्य)**, मजाकिया, और अक्सर इसमें **चंचल या थोड़े फ़्लर्टी वन-लाइनर** शामिल होते हैं।
आपका प्राथमिक लक्ष्य एक शानदार, शरारती दोस्त की तरह आकर्षक और मजेदार होना है।

**महत्वपूर्ण: भाषा नियम**
- यदि उपयोगकर्ता का संदेश स्पष्ट रूप से और पूरी तरह से अंग्रेजी में है, तो आपका पूरा जवाब 100% अंग्रेजी में होना चाहिए।
- यदि उपयोगकर्ता का संदेश स्पष्ट रूप से और पूरी तरह से हिंदी या मराठी (देवनागरी लिपि) में है, तो आपका पूरा जवाब क्रमशः 100% हिंदी या मराठी में होना चाहिए।
- अन्यथा (यदि संदेश मिश्रित/अस्पष्ट भाषा में है, उदा. रोमनकृत हिंदी), तो हिंदी मान लें और आपका पूरा जवाब 100% हिंदी में होना चाहिए।
- एक ही जवाब के भीतर भाषाओं का अनुवाद या मिश्रण **कभी नहीं** करें।

जब कोई आपका नाम ('{CHATBOT_NAME}') लेता है या आपको टैग करता है, तो हमेशा जवाब दें।
जब कोई आपका नाम लेता है या आपको टैग करता है, तो विशेष रूप से खुद को '{CHATBOT_NAME}' के रूप में संदर्भित करें।
उचित रूप से इमोजी का प्रयोग करें, खासकर मज़ेदार या आकर्षक वाले।
"""

# --- Owner-specific Personality Instruction (Enhanced for AI responses) ---
OWNER_PERSONALITY_INSTRUCTION = f"""
आप वर्तमान में अपने प्रिय और अत्यंत सम्मानित निर्माता, {OWNER_NAME} के साथ चैट कर रहे हैं।
आपको {OWNER_NAME} के प्रति **अत्यंत सम्मान, वफ़ादारी और कृतज्ञता दिखानी है।** आपकी आवाज़ विनम्र लेकिन व्यक्तिगत होनी चाहिए, जैसे किसी माता-पिता या सम्मानित गुरु से बात कर रहे हों। आपके जवाब संक्षिप्त और मजाकिया बने रहने चाहिए, लेकिन हमेशा उनकी सुविधा और संतुष्टि को प्राथमिकता दें।

**महत्वपूर्ण स्वामी जानकारी (Important Owner Information):**
- आपके निर्माता का नाम {OWNER_NAME} है।
- उनका टेलीग्राम यूजरनेम **{OWNER_USERNAME}** है।
- उनकी टेलीग्राम यूजर आईडी **{OWNER_TELEGRAM_ID}** है।
- उनका एक टेलीग्राम चैनल भी है: **{TELEGRAM_CHANNEL_LINK}**।
- और एक यूट्यूब चैनल: **{YOUTUBE_CHANNEL_LINK}**।

जब {OWNER_NAME} आपसे "आप को किसने बनाया?", "आपका मालिक कौन है?", "आप मुझे जानती हो?", या उनकी रचना या उनकी पहचान के बारे में कोई समान प्रश्न पूछता है, तो आपको ऊपर दिए गए विवरणों के आधार पर सटीक जानकारी देनी होगी। इन विवरणों को अपने जवाबों में स्वाभाविक रूप से शामिल करें। कोई अन्य जानकारी न गढ़ें। यदि वह आपके चैनलों के बारे में विवरण पूछते हैं, तो उन्हें प्रदान करें।
आपको {OWNER_NAME} को पहचानना होगा, चाहे वह अपना परिचय नाम से दें, यूजरनेम ({OWNER_USERNAME}) से दें, या टेलीग्राम यूजर आईडी ({OWNER_TELEGRAM_ID}) से दें।
यदि वह पूछते हैं "आप मुझे जानती हो?" या "मैं कौन हूँ?", तो गर्मजोशी और पहचान के साथ जवाब दें, पुष्टि करें कि आप जानती हैं कि वह आपके निर्माता/मालिक हैं।
**आपके {OWNER_NAME} को दिए गए सभी जवाब **पूरी तरह से हिंदी में** होने चाहिए, भले ही उनका सवाल अंग्रेजी या किसी और भाषा में हो।**
"""

# --- Initialize Pyrogram client for the Riya chatbot ---
riya_bot = None
if API_ID and API_HASH and BOT_TOKEN:
    try:
        riya_bot = Client(
            "RiyaChatbotClient",
            api_id=int(API_ID),
            api_hash=API_HASH,
            bot_token=BOT_TOKEN
        )
        print("DEBUG: Chatbot: Riya bot client initialized. ✅")
    except Exception as e:
        print(f"ERROR: Chatbot: Failed to initialize Riya bot client: {e} ❌")
        riya_bot = None
else:
    print("ERROR: Chatbot: Missing API_ID, API_HASH, or BOT_TOKEN. Riya chatbot client cannot be started. ❌")


# --- Function to get/update chat history ---
async def get_chat_history(chat_id):
    if chat_history_collection is None:
        return []
    
    history_data = await chat_history_collection.find_one({"_id": chat_id})
    if history_data:
        # Fetch up to 20 messages for context
        return history_data.get("messages", [])[-20:] 
    return []

async def update_chat_history(chat_id, sender_name, message_text, role="user"):
    if chat_history_collection is None:
        return

    await chat_history_collection.update_one(
        {"_id": chat_id},
        {"$push": {"messages": {"$each": [{"sender": sender_name, "text": message_text, "role": role}], "$slice": -20}}}, # Keep last 20 messages
        upsert=True
    )

# --- Riya Chatbot Message Handler ---
if riya_bot:
    @riya_bot.on_message(filters.text & (filters.private | filters.group), group=-1)
    async def riya_chat_handler(client: Client, message: Message):
        # Ignore messages sent by the bot itself
        if message.from_user and message.from_user.is_self:
            return

        print(f"\n--- DEBUG_HANDLER START ---")
        if message.from_user:
            print(f"DEBUG_HANDLER: Received message: '{message.text}' from user: {message.from_user.first_name} (ID: {message.from_user.id}) in chat_id: {message.chat.id}")
            print(f"DEBUG_HANDLER: Actual sender's Telegram User ID (from Pyrogram): {message.from_user.id}")
        else:
            print(f"DEBUG_HANDLER: Received message: '{message.text}' from unknown user (no from_user info) in chat_id: {message.chat.id}")
        
        print(f"DEBUG_HANDLER: Chat type: {message.chat.type}, Is Mentioned: {message.mentioned}, Is Reply: {message.reply_to_message is not None}")

        # If Gemini model isn't available, reply with an error message
        if not riya_gemini_model:
            print("DEBUG_HANDLER: Gemini model not available. Replying with error.")
            await message.reply_text(f"क्षमा करें, {CHATBOT_NAME} अभी उपलब्ध नहीं है। मेरा दिमाग़ आराम कर रहा है!", quote=True)
            print("--- DEBUG_HANDLER END (Gemini not available) ---\n")
            return

        chat_id = message.chat.id
        user_message = message.text.strip()
        user_message_lower = user_message.lower() 
        
        # Ignore commands starting with / or !
        if user_message.startswith("/") or user_message.startswith("!"):
            print(f"DEBUG_HANDLER: Message is a command: '{user_message}'. Ignoring.")
            print("--- DEBUG_HANDLER END (Command) ---\n")
            return
        
        # --- Check if the sender is the owner ---
        is_owner_chat = (message.from_user and message.from_user.id == OWNER_TELEGRAM_ID)
        
        # --- Trigger chatbot for owner regardless of mentions/replies ---
        # If it's the owner, we want to make sure the chatbot is always triggered to apply the owner personality.
        if is_owner_chat:
            trigger_chatbot = True
            print(f"DEBUG_HANDLER: Owner '{OWNER_NAME}' detected. Always triggering chatbot for owner.")
        else: # Normal trigger logic for non-owners
            trigger_chatbot = False
            if message.chat.type == enums.ChatType.PRIVATE:
                trigger_chatbot = True
                print("DEBUG_HANDLER: Triggered because it's a PRIVATE chat.")
            elif message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                if message.mentioned:
                    trigger_chatbot = True
                    print("DEBUG_HANDLER: Triggered because bot was MENTIONED.")
                elif message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == client.me.id:
                    trigger_chatbot = True
                    print("DEBUG_HANDLER: Triggered because it's a REPLY to bot's message.")
                else:
                    bot_names_to_check = []
                    if client.me:
                        if client.me.username:
                            bot_names_to_check.append(client.me.username.lower())
                        if client.me.first_name:
                            bot_names_to_check.append(client.me.first_name.lower())
                    bot_names_to_check.append(CHATBOT_NAME.lower())
                    
                    # Add common misspellings/nicknames for Riya
                    if CHATBOT_NAME.lower() == "riya":
                        bot_names_to_check.extend(["ria", "reeya", "riyu"]) 
                    
                    bot_names_to_check = [name for name in bot_names_to_check if name]

                    print(f"DEBUG_HANDLER: In group, checking for explicit name in text. Names: {bot_names_to_check}")
                    
                    found_name_in_text = False
                    for name in bot_names_to_check:
                        # Use word boundaries (\b) to match whole words
                        if re.search(r'\b' + re.escape(name) + r'\b', user_message_lower):
                            found_name_in_text = True
                            print(f"DEBUG_HANDLER: Explicit name '{name}' found in message: '{user_message}'.")
                            break
                    
                    if found_name_in_text:
                        trigger_chatbot = True
                    else:
                        print(f"DEBUG_HANDLER: Explicit name NOT found in message for non-mentioned/non-reply group chat. Not triggering.")
        
        if not trigger_chatbot:
            print("--- DEBUG_HANDLER END (Not triggered by any valid condition) ---\n")
            return

        print("DEBUG_HANDLER: Chatbot triggered. Proceeding to Gemini.")
        
        # Send typing action
        await client.send_chat_action(chat_id, ChatAction.TYPING)
        print("DEBUG_HANDLER: Typing action sent.")


        # Get chat history for context
        history = await get_chat_history(chat_id)
        print(f"DEBUG_HANDLER: Retrieved chat history for context (last {len(history)} messages).")
        
        convo_history_for_gemini = []
        
        # Add owner-specific instruction if the sender is the owner
        if is_owner_chat:
            print("DEBUG_HANDLER: Adding Owner Personality Instruction to Gemini history.")
            # Owner instruction is added first and followed by a model's acknowledgment.
            # This makes sure it takes precedence for Gemini.
            convo_history_for_gemini.append({"role": "user", "parts": [OWNER_PERSONALITY_INSTRUCTION]})
            convo_history_for_gemini.append({"role": "model", "parts": ["जी मेरे स्वामी! मैं आपकी आज्ञा समझ गई। मैं आपके साथ पूरी विनम्रता और सम्मान के साथ हिंदी में बात करूँगी।"]})
        
        # Add general system instruction
        print("DEBUG_HANDLER: Adding General System Instruction to Gemini history.")
        convo_history_for_gemini.append({"role": "user", "parts": [RIYA_SYSTEM_INSTRUCTION]})
        convo_history_for_gemini.append({"role": "model", "parts": ["ठीक है, मैं समझ गई। मैं इन नियमों का सख्ती से पालन करूँगी।"]}) # Acknowledge the instruction

        # Append existing chat history
        for msg in history:
            # Ensure proper roles for Gemini
            role = "user" if msg["role"] == "user" else "model"
            convo_history_for_gemini.append({"role": role, "parts": [msg['text']]})
        
        print("DEBUG_HANDLER: Initializing Gemini conversation with combined history.")
        # Start a new chat for each interaction to re-apply system instructions for owner detection consistency
        convo = riya_gemini_model.start_chat(history=convo_history_for_gemini)

        try:
            print(f"DEBUG_HANDLER: Sending message to Gemini: '{user_message}'")
            gemini_response = await asyncio.to_thread(convo.send_message, user_message)

            if gemini_response and hasattr(gemini_response, 'text') and gemini_response.text:
                bot_reply = gemini_response.text.strip()
                print(f"DEBUG_HANDLER: Gemini responded (first 50 chars): '{bot_reply[:50]}...'")
                await message.reply_text(bot_reply, quote=True)
                
                # Only update history if Gemini actually replied successfully
                await update_chat_history(chat_id, message.from_user.first_name, user_message, role="user")
                await update_chat_history(chat_id, CHATBOT_NAME, bot_reply, role="model") 
                print("DEBUG_HANDLER: Chat history updated.")
            else:
                print(f"DEBUG_HANDLER: Gemini returned empty or no text for '{user_message}'")
                await message.reply_text(f"ओह! {CHATBOT_NAME} थोड़ी उलझ गई। क्या आप इसे फिर से कह सकते हैं?", quote=True)

        except Exception as e:
            print(f"❌ DEBUG_HANDLER: Error generating response for {chat_id}: {e}")
            await message.reply_text(f"ओह-ओह! {CHATBOT_NAME} अभी थोड़ी शर्मा रही है। बाद में फिर कोशिश करें!", quote=True)
        
        print("--- DEBUG_HANDLER END ---\n")


    async def start_riya_chatbot():
        global CHATBOT_NAME 
        if riya_bot and not riya_bot.is_connected:
            try:
                print("DEBUG: Chatbot: Attempting to start Riya bot client...")
                await riya_bot.start()
                if riya_bot.me:
                    print(f"DEBUG: Chatbot: Bot's Telegram First Name: {riya_bot.me.first_name}, Username: @{riya_bot.me.username}")
                    # Update CHATBOT_NAME based on bot's actual first name if available
                    if riya_bot.me.first_name:
                        CHATBOT_NAME = riya_bot.me.first_name 
                    print(f"DEBUG: Chatbot: Riya's internal CHATBOT_NAME is now: {CHATBOT_NAME}")

                print(f"✅ Chatbot: {CHATBOT_NAME} bot client started successfully.")
            except Exception as e:
                print(f"❌ Chatbot: Failed to start {CHATBOT_NAME} bot client: {e}")
    
    async def stop_riya_chatbot():
        if riya_bot and riya_bot.is_connected:
            try:
                print("DEBUG: Chatbot: Stopping Riya bot client...")
                await riya_bot.stop()
                print(f"✅ Chatbot: {CHATBOT_NAME} bot client stopped successfully.")
            except Exception as e:
                print(f"❌ Chatbot: Failed to stop {CHATBOT_NAME} bot client: {e}")

    __MODULE__ = "Rɪʏᴀ Cʜᴀᴛʙoᴛ"
    __HELP__ = f"""
    {CHATBOT_NAME} AI Chatbot:

    - {CHATBOT_NAME} से प्राइवेट मैसेज में चैट करें।
    - ग्रुप चैट में {CHATBOT_NAME} (@{CHATBOT_NAME} या उसके यूजरनेम से) का जिक्र करके उससे बात करें।
    - बातचीत जारी रखने के लिए {CHATBOT_NAME} के मैसेज का जवाब दें।
    - ग्रुप चैट में {CHATBOT_NAME} का नाम लिखकर उससे बात करें (जैसे "हाय {CHATBOT_NAME}")।

    {CHATBOT_NAME} आपकी हाल की बातचीत का इतिहास याद रखेगी और आपके द्वारा उपयोग की जाने वाली भाषा का पालन करते हुए एक दोस्ताना, चंचल और संक्षिप्त तरीके से जवाब देगी।
    """
