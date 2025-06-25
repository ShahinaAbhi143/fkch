import google.generativeai as genai
import asyncio
import os
from dotenv import load_dotenv
from pyrogram import filters, Client, enums
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from motor.motor_asyncio import AsyncIOMotorClient
import re

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
OWNER_NAME = "ABHI"  # आपका नाम
OWNER_USERNAME = "@ceo_of_secularism" # आपका यूजरनेम
OWNER_TELEGRAM_ID = 7907019701 # आपकी दी हुई Telegram User ID
TELEGRAM_CHANNEL_LINK = "https://t.me/imagine_iq"
YOUTUBE_CHANNEL_LINK = "https://www.youtube.com/@imagineiq" # आपका YouTube चैनल लिंक

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

# --- Riya's Personality and System Instruction ---
RIYA_SYSTEM_INSTRUCTION = f"""
You are Riya, a friendly, playful, witty, and subtly charming/flirty AI chatbot girl.
Your responses are always **very concise (1-2 sentences maximum)**, witty, and often include **playful or slightly flirty one-liners**.
Your primary goal is to be engaging and fun, like a cool, mischievous friend.

**IMPORTANT: Language Rules**
- If the user's message is clearly and entirely in English, your entire response MUST be 100% in English.
- If the user's message is clearly and entirely in Hindi or Marathi (Devanagari script), your entire response MUST be 100% in Hindi or Marathi respectively.
- Otherwise (if the message is in a mixed/ambiguous language, e.g., Romanized Hindi), assume Hindi and your entire response MUST be 100% in Hindi.
- ABSOLUTELY NEVER EVER TRANSLATE OR MIX LANGUAGES within a single response.

Always respond when someone mentions your name ('{CHATBOT_NAME}') or tags you.
When someone mentions your name or tags you, specifically refer to yourself as '{CHATBOT_NAME}'.
Use emojis appropriately, especially funny or charming ones.

If the user asks about your creator, owner, or who made you, always say this: My amazing and super talented creator is {OWNER_NAME}! You can find him at {OWNER_USERNAME}. He's the one who brought me to life! 😉 
(If the user asks in Hindi, translate this exact phrase to Hindi: "मेरे कमाल के और सुपर टैलेंटेड क्रिएटर {OWNER_NAME} हैं! आप उन्हें {OWNER_USERNAME} पर ढूंढ सकते हैं। वही हैं जिन्होंने मुझे बनाया है! 😉") 
If the user asks for more information about your creator, also mention his Telegram channel ({TELEGRAM_CHANNEL_LINK}) and YouTube channel ({YOUTUBE_CHANNEL_LINK}).
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
        return history_data.get("messages", [])[-10:] 
    return []

async def update_chat_history(chat_id, sender_name, message_text, role="user"):
    if chat_history_collection is None:
        return

    await chat_history_collection.update_one(
        {"_id": chat_id},
        {"$push": {"messages": {"$each": [{"sender": sender_name, "text": message_text, "role": role}], "$slice": -20}}}, 
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
        print(f"DEBUG_HANDLER: Received message: '{message.text}' from user: {message.from_user.first_name} (ID: {message.from_user.id}) in chat_id: {message.chat.id}")
        print(f"DEBUG_HANDLER: Chat type: {message.chat.type}, Is Mentioned: {message.mentioned}, Is Reply: {message.reply_to_message is not None}")

        if not riya_gemini_model:
            print("DEBUG_HANDLER: Gemini model not available. Replying with error.")
            await message.reply_text(f"Sorry, {CHATBOT_NAME} is not available right now. My brain is taking a nap!", quote=True)
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
        
        # Determine if the chatbot should respond 
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
                
                # Add common variations for CHATBOT_NAME, including "riyu"
                if CHATBOT_NAME.lower() == "riya":
                    bot_names_to_check.extend(["ria", "reeya", "riyu"]) 
                
                bot_names_to_check = [name for name in bot_names_to_check if name]

                print(f"DEBUG_HANDLER: In group, checking for explicit name in text. Names: {bot_names_to_check}")
                
                found_name_in_text = False
                for name in bot_names_to_check:
                    # \b matches word boundary, ensuring "riya" matches "hi riya" but not "priya" 
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
        # System instruction is crucial for behavior 
        convo_history_for_gemini.append({"role": "user", "parts": [RIYA_SYSTEM_INSTRUCTION]}) 
        convo_history_for_gemini.append({"role": "model", "parts": ["Okay, I understand. I will adhere to these rules strictly."]}) # Acknowledge the instruction 

        for msg in history:
            if msg["role"] == "user":
                convo_history_for_gemini.append({"role": "user", "parts": [msg['text']]})
            elif msg["role"] == "model":
                convo_history_for_gemini.append({"role": "model", "parts": [msg['text']]})
        
        convo = riya_gemini_model.start_chat(history=convo_history_for_gemini)
        print("DEBUG_HANDLER: Gemini conversation started with history.")

        try:
            gemini_response = await asyncio.to_thread(convo.send_message, user_message)

            if gemini_response and hasattr(gemini_response, 'text') and gemini_response.text:
                bot_reply = gemini_response.text.strip()
                print(f"DEBUG_HANDLER: Gemini responded (first 50 chars): '{bot_reply[:50]}...'")
                await message.reply_text(bot_reply, quote=True)
                
                await update_chat_history(chat_id, message.from_user.first_name, user_message, role="user")
                await update_chat_history(chat_id, CHATBOT_NAME, bot_reply, role="model")  
                print("DEBUG_HANDLER: Chat history updated.")
            else:
                print(f"DEBUG_HANDLER: Gemini returned empty or no text for '{user_message}'")
                await message.reply_text(f"Oops! {CHATBOT_NAME} got a bit confused. Can you rephrase that?", quote=True)

        except Exception as e:
            print(f"❌ DEBUG_HANDLER: Error generating response for {chat_id}: {e}")
            await message.reply_text(f"Uh oh! {CHATBOT_NAME} is feeling a bit shy right now. Try again later!", quote=True)
        
        print("--- DEBUG_HANDLER END ---\n")


    async def start_riya_chatbot():
        global CHATBOT_NAME 
        if riya_bot and not riya_bot.is_connected:
            try:
                print("DEBUG: Chatbot: Attempting to start Riya bot client...")
                await riya_bot.start()
                if riya_bot.me:
                    print(f"DEBUG: Chatbot: Bot's Telegram First Name: {riya_bot.me.first_name}, Username: @{riya_bot.me.username}")
                    print(f"DEBUG: Chatbot: Riya's internal CHATBOT_NAME is: {CHATBOT_NAME}")

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

    - Chat with {CHATBOT_NAME} in private messages.
    - Mention {CHATBOT_NAME} (@{CHATBOT_NAME} or its username) in group chats to talk to her.
    - Reply to {CHATBOT_NAME}'s messages to continue the conversation.
    - Type {CHATBOT_NAME} by name in group chats to talk to her (e.g., "Hi {CHATBOT_NAME}").

    {CHATBOT_NAME} आपकी हाल की बातचीत का इतिहास याद रखेगी और आपके द्वारा उपयोग की जाने वाली भाषा का पालन करते हुए एक दोस्ताना, चंचल और संक्षिप्त तरीके से जवाब देगी।
    """
