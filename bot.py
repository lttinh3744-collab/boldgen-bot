import json
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("❌ Không tìm thấy TOKEN! Hãy thêm biến TOKEN trong Railway.")

OWNER_ID = int(os.getenv("OWNER_ID", "8765391878"))

# ====================== MAPPING FONT ======================
BOLD_SERIF = {'A':'𝐀','B':'𝐁','C':'𝐂','D':'𝐃','E':'𝐄','F':'𝐅','G':'𝐆','H':'𝐇','I':'𝐈','J':'𝐉','K':'𝐊','L':'𝐋','M':'𝐌','N':'𝐍','O':'𝐎','P':'𝐏','Q':'𝐐','R':'𝐑','S':'𝐒','T':'𝐓','U':'𝐔','V':'𝐕','W':'𝐖','X':'𝐗','Y':'𝐘','Z':'𝐙',
              'a':'𝐚','b':'𝐛','c':'𝐜','d':'𝐝','e':'𝐞','f':'𝐟','g':'𝐠','h':'𝐡','i':'𝐢','j':'𝐣','k':'𝐤','l':'𝐥','m':'𝐦','n':'𝐧','o':'𝐨','p':'𝐩','q':'𝐪','r':'𝐫','s':'𝐬','t':'𝐭','u':'𝐮','v':'𝐯','w':'𝐰','x':'𝐱','y':'𝐲','z':'𝐳'}

BOLD_SANS_SERIF = {'A':'𝗔','B':'𝗕','C':'𝗖','D':'𝗗','E':'𝗘','F':'𝗙','G':'𝗚','H':'𝗛','I':'𝗜','J':'𝗝','K':'𝗞','L':'𝗟','M':'𝗠','N':'𝗡','O':'𝗢','P':'𝗣','Q':'𝗤','R':'𝗥','S':'𝗦','T':'𝗧','U':'𝗨','V':'𝗩','W':'𝗪','X':'𝗫','Y':'𝗬','Z':'𝗭',
                   'a':'𝗮','b':'𝗯','c':'𝗰','d':'𝗱','e':'𝗲','f':'𝗳','g':'𝗴','h':'𝗵','i':'𝗶','j':'𝗷','k':'𝗸','l':'𝗹','m':'𝗺','n':'𝗻','o':'𝗼','p':'𝗽','q':'𝗾','r':'𝗿','s':'𝘀','t':'𝘁','u':'𝘂','v':'𝘃','w':'𝘄','x':'𝘅','y':'𝘆','z':'𝘇'}

BOLD_ITALIC = {'A':'𝑨','B':'𝑩','C':'𝑪','D':'𝑫','E':'𝑬','F':'𝑭','G':'𝑮','H':'𝑯','I':'𝑰','J':'𝑱','K':'𝑲','L':'𝑳','M':'𝑴','N':'𝑵','O':'𝑶','P':'𝑷','Q':'𝑸','R':'𝑹','S':'𝑺','T':'𝑻','U':'𝑼','V':'𝑽','W':'𝑾','X':'𝑿','Y':'𝒀','Z':'𝒁',
               'a':'𝒂','b':'𝒃','c':'𝒄','d':'𝒅','e':'𝒆','f':'𝒇','g':'𝒈','h':'𝒉','i':'𝒊','j':'𝒋','k':'𝒌','l':'𝒍','m':'𝒎','n':'𝒏','o':'𝒐','p':'𝒑','q':'𝒒','r':'𝒓','s':'𝒔','t':'𝒕','u':'𝒖','v':'𝒗','w':'𝒘','x':'𝒙','y':'𝒚','z':'𝒛'}

def get_font_map(font_type):
    if font_type == "serif": return BOLD_SERIF
    elif font_type == "sans": return BOLD_SANS_SERIF
    elif font_type == "italic": return BOLD_ITALIC
    return BOLD_SANS_SERIF

def convert_word(word, font, mode):
    mapping = get_font_map(font)
    if mode == "full":
        return ''.join(mapping.get(c, c) for c in word)
    elif mode == "first" and word:
        first = mapping.get(word[0], word[0]) if word and word[0].isalpha() else word[0]
        return first + word[1:]
    elif mode == "first_last" and word:
        first = mapping.get(word[0], word[0]) if word and word[0].isalpha() else word[0]
        last = mapping.get(word[-1], word[-1]) if len(word) > 1 and word[-1].isalpha() else word[-1]
        return first + word[1:-1] + last
    return word

def convert_phrase(phrase, font, mode):
    if not phrase:
        return phrase
    words = phrase.split()
    converted = [convert_word(w, font, mode) for w in words]
    return " ".join(converted)

def process_text(text, user_data, mode="full", global_contact="LH: 076.6482.506"):
    phrases = sorted(user_data.get("words", []), key=len, reverse=True)
    result = text
    for phrase in phrases:
        if phrase:
            converted = convert_phrase(phrase, user_data["font"], mode)
            result = result.replace(phrase, converted)
    
    bold_contact = convert_word(global_contact, user_data["font"], "full")
    return result + "\n" + bold_contact

# ====================== DATA ======================
def load_data():
    if os.path.exists("bot_data.json"):
        with open("bot_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"global_contact": "LH: 076.6482.506", "users": {}}

def save_data(data):
    with open("bot_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()
global_contact = data["global_contact"]
users = data["users"]

# ====================== HANDLERS ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        users[user_id] = {"words": [], "font": "sans"}
        save_data(data)
    
    keyboard = [
        [InlineKeyboardButton("Bold Serif", callback_data="font_serif")],
        [InlineKeyboardButton("Bold Sans Serif", callback_data="font_sans")],
        [InlineKeyboardButton("Bold Italic", callback_data="font_italic")]
    ]
    await update.message.reply_text("👋 Chào mừng đến với **BoldGen**!\nChọn font mặc định:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    if user_id not in users:
        users[user_id] = {"words": [], "font": "sans"}
    
    if query.data == "font_serif":
        users[user_id]["font"] = "serif"
        name = "Bold Serif"
    elif query.data == "font_sans":
        users[user_id]["font"] = "sans"
        name = "Bold Sans Serif"
    else:
        users[user_id]["font"] = "italic"
        name = "Bold Italic"
    
    save_data(data)
    await query.edit_message_text(f"✅ Kích hoạt font **{name}** thành công")

# (các hàm add, delete, ds, m1, m2, m3, setlh, help_command, handle_normal_message giữ nguyên như code cũ của bạn)

# ====================== MAIN ======================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("font", lambda u, c: u.message.reply_text("Chọn font:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Bold Serif", callback_data="font_serif")], [InlineKeyboardButton("Bold Sans Serif", callback_data="font_sans")], [InlineKeyboardButton("Bold Italic", callback_data="font_italic")]]))))
    app.add_handler(CallbackQueryHandler(button))
    # Thêm các handler còn lại tương tự...

    print("🚀 Bot BoldGen đang chạy...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
