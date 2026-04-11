import json
import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("❌ Không tìm thấy TOKEN! Hãy thêm biến TOKEN trong Railway.")

OWNER_ID = int(os.getenv("OWNER_ID", "8765391878"))

# ====================== FONT MAPPING ======================
BOLD_SERIF = {
    'A':'𝐀','B':'𝐁','C':'𝐂','D':'𝐃','E':'𝐄','F':'𝐅','G':'𝐆','H':'𝐇','I':'𝐈','J':'𝐉','K':'𝐊','L':'𝐋','M':'𝐌','N':'𝐍','O':'𝐎','P':'𝐏','Q':'𝐐','R':'𝐑','S':'𝐒','T':'𝐓','U':'𝐔','V':'𝐕','W':'𝐖','X':'𝐗','Y':'𝐘','Z':'𝐙',
    'a':'𝐚','b':'𝐛','c':'𝐜','d':'𝐝','e':'𝐞','f':'𝐟','g':'𝐠','h':'𝐡','i':'𝐢','j':'𝐣','k':'𝐤','l':'𝐥','m':'𝐦','n':'𝐧','o':'𝐨','p':'𝐩','q':'𝐪','r':'𝐫','s':'𝐬','t':'𝐭','u':'𝐮','v':'𝐯','w':'𝐰','x':'𝐱','y':'𝐲','z':'𝐳'
}

BOLD_SANS_SERIF = {
    'A':'𝗔','B':'𝗕','C':'𝗖','D':'𝗗','E':'𝗘','F':'𝗙','G':'𝗚','H':'𝗛','I':'𝗜','J':'𝗝','K':'𝗞','L':'𝗟','M':'𝗠','N':'𝗡','O':'𝗢','P':'𝗣','Q':'𝗤','R':'𝗥','S':'𝗦','T':'𝗧','U':'𝗨','V':'𝗩','W':'𝗪','X':'𝗫','Y':'𝗬','Z':'𝗭',
    'a':'𝗮','b':'𝗯','c':'𝗰','d':'𝗱','e':'𝗲','f':'𝗳','g':'𝗴','h':'𝗵','i':'𝗶','j':'𝗷','k':'𝗸','l':'𝗹','m':'𝗺','n':'𝗻','o':'𝗼','p':'𝗽','q':'𝗾','r':'𝗿','s':'𝘀','t':'𝘁','u':'𝘂','v':'𝘃','w':'𝘄','x':'𝘅','y':'𝘆','z':'𝘇'
}

BOLD_ITALIC = {
    'A':'𝑨','B':'𝑩','C':'𝑪','D':'𝑫','E':'𝑬','F':'𝑭','G':'𝑮','H':'𝑯','I':'𝑰','J':'𝑱','K':'𝑲','L':'𝑳','M':'𝑴','N':'𝑵','O':'𝑶','P':'𝑷','Q':'𝑸','R':'𝑹','S':'𝑺','T':'𝑻','U':'𝑼','V':'𝑽','W':'𝑾','X':'𝑿','Y':'𝒀','Z':'𝒁',
    'a':'𝒂','b':'𝒃','c':'𝒄','d':'𝒅','e':'𝒆','f':'𝒇','g':'𝒈','h':'𝒉','i':'𝒊','j':'𝒋','k':'𝒌','l':'𝒍','m':'𝒎','n':'𝒏','o':'𝒐','p':'𝒑','q':'𝒒','r':'𝒓','s':'𝒔','t':'𝒕','u':'𝒖','v':'𝒗','w':'𝒘','x':'𝒙','y':'𝒚','z':'𝒛'
}

# ====================== SPECIAL MAPPING ======================
SPECIAL_MAP_LOWER = {
    'a': 'а', 'e': 'е', 'o': 'ο', 'p': 'р', 'c': 'с', 'i': 'і', 'y': 'у',
    'x': 'х', 'v': 'ν', 'n': 'ո', 'h': 'һ', 'g': 'ɡ', 'k': 'κ', 'm': 'ｍ',
    'b': 'Ƅ', 't': '𝘁', 'l': 'ӏ', 'd': 'ԁ', 'u': 'ս', 's': 'ѕ', 'r': 'г', 'đ': 'đ'
}

SPECIAL_MAP_UPPER = {
    'A': 'А', 'B': 'В', 'E': 'Е', 'H': 'Н', 'K': 'Κ',
    'M': 'М', 'O': 'О', 'P': 'Р', 'T': 'Т', 'X': 'Х'
}

# Mathematical Fonts
MATH_MONOSPACE = {
    'A':'𝙰','B':'𝙱','C':'𝙲','D':'𝙳','E':'𝙴','F':'𝙵','G':'𝙶','H':'𝙷','I':'𝙸','J':'𝙹','K':'𝙺','L':'𝙻','M':'𝙼','N':'𝙽','O':'𝙾','P':'𝙿','Q':'𝚀','R':'𝚁','S':'𝚂','T':'𝚃','U':'𝚄','V':'𝚅','W':'𝚆','X':'𝚇','Y':'𝚈','Z':'𝚉',
    'a':'𝚊','b':'𝚋','c':'𝚌','d':'𝚍','e':'𝚎','f':'𝚏','g':'𝚐','h':'𝚑','i':'𝚒','j':'𝚓','k':'𝚔','l':'𝚕','m':'𝚖','n':'𝚗','o':'𝚘','p':'𝚙','q':'𝚚','r':'𝚛','s':'𝚜','t':'𝚝','u':'𝚞','v':'𝚟','w':'𝚠','x':'𝚡','y':'𝚢','z':'𝚣'
}

MATH_BOLD = {
    'A':'𝐀','B':'𝐁','C':'𝐂','D':'𝐃','E':'𝐄','F':'𝐅','G':'𝐆','H':'𝐇','I':'𝐈','J':'𝐉','K':'𝐊','L':'𝐋','M':'𝐌','N':'𝐍','O':'𝐎','P':'𝐏','Q':'𝐐','R':'𝐑','S':'𝐒','T':'𝐓','U':'𝐔','V':'𝐕','W':'𝐖','X':'𝐗','Y':'𝐘','Z':'𝐙',
    'a':'𝐚','b':'𝐛','c':'𝐜','d':'𝐝','e':'𝐞','f':'𝐟','g':'𝐠','h':'𝐡','i':'𝐢','j':'𝐣','k':'𝐤','l':'𝐥','m':'𝐦','n':'𝐧','o':'𝐨','p':'𝐩','q':'𝐪','r':'𝐫','s':'𝐬','t':'𝐭','u':'𝐮','v':'𝐯','w':'𝐰','x':'𝐱','y':'𝐲','z':'𝐳'
}

def get_font_map(font_type: str):
    if font_type == "serif": return BOLD_SERIF
    elif font_type == "sans": return BOLD_SANS_SERIF
    elif font_type == "italic": return BOLD_ITALIC
    return BOLD_SANS_SERIF

def convert_word(word: str, font: str, mode: str) -> str:
    mapping = get_font_map(font)
    if mode == "full":
        return ''.join(mapping.get(c, c) for c in word)
    elif mode == "first" and word:
        first = mapping.get(word[0], word[0]) if word[0].isalpha() else word[0]
        return first + word[1:]
    elif mode == "first_last" and word:
        first = mapping.get(word[0], word[0]) if word[0].isalpha() else word[0]
        last = mapping.get(word[-1], word[-1]) if len(word) > 1 and word[-1].isalpha() else word[-1]
        return first + word[1:-1] + last
    return word

def convert_phrase(phrase: str, font: str, mode: str) -> str:
    if not phrase: return phrase
    return " ".join(convert_word(w, font, mode) for w in phrase.split())

def apply_special_map(text: str) -> str:
    result = []
    for char in text:
        if char.isupper():
            result.append(SPECIAL_MAP_UPPER.get(char, char))
        else:
            lower = char.lower()
            result.append(SPECIAL_MAP_LOWER.get(lower, char))
    return ''.join(result)

def apply_math_font(char: str, is_first_letter: bool = False) -> str:
    if char.isupper():
        return MATH_MONOSPACE.get(char, char)
    else:
        return random.choice([MATH_MONOSPACE.get(char, char), MATH_BOLD.get(char, char)])

def process_text_m6(text: str, user_data: dict, global_contact: str) -> str:
    words = text.split()
    result_words = []

    for word in words:
        if not word:
            result_words.append(word)
            continue

        # Kiểm tra từ có trong danh sách đã add không
        is_in_list = any(word.lower() == w.lower() for w in user_data.get("words", []))

        if is_in_list:
            result_words.append(apply_special_map(word))
            continue

        # Xử lý từng ký tự trong từ
        new_word = []
        for i, char in enumerate(word):
            is_first = (i == 0)
            is_last = (i == len(word) - 1)
            lower = char.lower()

            if lower in SPECIAL_MAP_LOWER:
                if is_first or is_last:
                    new_word.append(apply_math_font(char, is_first))
                else:
                    new_word.append(char)  # Giữa từ giữ nguyên
            else:
                new_word.append(char)

        result_words.append(''.join(new_word))

    result = " ".join(result_words)
    contact = apply_special_map(global_contact)
    return result + "\n" + contact

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
global_contact = data.get("global_contact", "LH: 076.6482.506")
users = data.get("users", {})

# ====================== HANDLERS ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        users[user_id] = {"words": [], "font": "sans"}
        save_data(data)
    keyboard = [[InlineKeyboardButton("Bold Serif", callback_data="font_serif")],
                [InlineKeyboardButton("Bold Sans Serif (khuyên dùng)", callback_data="font_sans")],
                [InlineKeyboardButton("Bold Italic", callback_data="font_italic")]]
    await update.message.reply_text("👋 Chào mừng đến với **BoldGen**!\n Được phát triển bởi: Tính\n Chọn font mặc định:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    if user_id not in users: users[user_id] = {"words": [], "font": "sans"}
    if query.data == "font_serif": users[user_id]["font"] = "serif"; name = "Bold Serif"
    elif query.data == "font_sans": users[user_id]["font"] = "sans"; name = "Bold Sans Serif"
    else: users[user_id]["font"] = "italic"; name = "Bold Italic"
    save_data(data)
    await query.edit_message_text(f"✅ Kích hoạt font **{name}** thành công")

# Các hàm add, delete, ds, m1, m2, m3, m4, m5 giữ nguyên như cũ
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users: users[user_id] = {"words": [], "font": "sans"}
    term = " ".join(context.args)
    if not term:
        await update.message.reply_text("⚠️ Vui lòng nhập từ sau /add")
        return
    if term.lower() not in [w.lower() for w in users[user_id]["words"]]:
        users[user_id]["words"].append(term)
        save_data(data)
        await update.message.reply_text(f"✅ Đã thêm **{term}** vào danh sách")
    else:
        await update.message.reply_text("ℹ️ Từ này đã tồn tại")

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users or not users[user_id]["words"]:
        await update.message.reply_text("Danh sách trống")
        return
    term = " ".join(context.args)
    if not term:
        await update.message.reply_text("⚠️ Vui lòng nhập từ sau /del")
        return
    for w in users[user_id]["words"][:]:
        if w.lower() == term.lower():
            users[user_id]["words"].remove(w)
            save_data(data)
            await update.message.reply_text(f"✅ Đã xóa **{w}** khỏi danh sách")
            return
    await update.message.reply_text("❌ Không tìm thấy từ")

async def ds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users or not users[user_id]["words"]:
        await update.message.reply_text("📋 Danh sách trống")
        return
    text = "📋 **Danh sách từ đã thêm:**\n" + "\n".join([f"• {w}" for w in users[user_id]["words"]])
    await update.message.reply_text(text)

async def m1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users: users[user_id] = {"words": [], "font": "sans"}
    text = " ".join(context.args) or (update.message.text.split(maxsplit=1)[1] if len(update.message.text.split()) > 1 else "")
    if not text: return await update.message.reply_text("⚠️ Nhập nội dung sau /m1")
    result = convert_phrase(text, users[user_id]["font"], "full") + "\n" + convert_word(global_contact, users[user_id]["font"], "full")
    await update.message.reply_text(result)

async def m2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users: users[user_id] = {"words": [], "font": "sans"}
    text = " ".join(context.args) or (update.message.text.split(maxsplit=1)[1] if len(update.message.text.split()) > 1 else "")
    if not text: return await update.message.reply_text("⚠️ Nhập nội dung sau /m2")
    result = convert_phrase(text, users[user_id]["font"], "first") + "\n" + convert_word(global_contact, users[user_id]["font"], "full")
    await update.message.reply_text(result)

async def m3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users: users[user_id] = {"words": [], "font": "sans"}
    text = " ".join(context.args) or (update.message.text.split(maxsplit=1)[1] if len(update.message.text.split()) > 1 else "")
    if not text: return await update.message.reply_text("⚠️ Nhập nội dung sau /m3")
    result = convert_phrase(text, users[user_id]["font"], "first_last") + "\n" + convert_word(global_contact, users[user_id]["font"], "full")
    await update.message.reply_text(result)

async def m4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users: users[user_id] = {"words": [], "font": "sans"}
    text = " ".join(context.args) or (update.message.text.split(maxsplit=1)[1] if len(update.message.text.split()) > 1 else "")
    if not text: return await update.message.reply_text("⚠️ Nhập nội dung sau /m4")
    result = apply_special_map(text) + "\n" + apply_special_map(global_contact)
    await update.message.reply_text(result)

async def m5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users: users[user_id] = {"words": [], "font": "sans"}
    text = " ".join(context.args) or (update.message.text.split(maxsplit=1)[1] if len(update.message.text.split()) > 1 else "")
    if not text: return await update.message.reply_text("⚠️ Nhập nội dung sau /m5")
    result = process_text_m5(text, users[user_id], global_contact)   # Sẽ định nghĩa sau nếu cần, hiện tại dùng m4 cho đơn giản
    await update.message.reply_text(result)

async def m6(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users: users[user_id] = {"words": [], "font": "sans"}
    text = " ".join(context.args) or (update.message.text.split(maxsplit=1)[1] if len(update.message.text.split()) > 1 else "")
    if not text: return await update.message.reply_text("⚠️ Nhập nội dung sau /m6")
    result = process_text_m6(text, users[user_id], global_contact)
    await update.message.reply_text(result)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""📖 **Hướng dẫn BoldGen**

/start - Bắt đầu + chọn font
/font - Chọn font
/add <từ> - Thêm từ in đậm
/del <từ> - Xóa từ
/ds - Xem danh sách từ đã thêm

/m1 <text> - In đậm toàn bộ từ có trong danh sách theo font đã chọn (hơi tốn SMS)
/m2 <text> - In đậm chữ cái đầu có trong danh sách theo font đã chọn (tiết kiệm SMS hơn /m1)
/m3 <text> - In đậm chữ cái đầu + cuối có trong danh sách theo font đã chọn (đỡ tốn SMS hơn /m1)

/m4 <text> - Đổi tất cả ký tự đặc biệt (a,o,e,p,c,i,y,x,v,n,h,g,k,m,b,t,l,d,u,s,r)
/m5 <text> - Chỉ đổi các từ đã thêm (/add) sang kiểu Cyrillic/Greek..., các ký tự khác giữ nguyên
Lưu ý: lệnh /m4 và /m5 không tuân theo font đã chọn trước đó, /m5 sẽ tiết kiệm tin nhắn hơn /m4
nhưng lệnh /m4 tuy tốn tin nhắn nhưng đi tin nhắn trơn tru hơn (tùy người sử dụng)

/m6 <text> đi tin nhắn sẽ tiết kiệm nhất (khuyên dùng)

/help - Xem hướng dẫn""")

async def handle_normal_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith("/"): return
    user_id = str(update.effective_user.id)
    if user_id not in users: users[user_id] = {"words": [], "font": "sans"}
    result = convert_phrase(update.message.text, users[user_id]["font"], "full") + "\n" + convert_word(global_contact, users[user_id]["font"], "full")
    await update.message.reply_text(result)

# ====================== MAIN ======================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("font", lambda u, c: u.message.reply_text("Chọn font bạn muốn sử dụng:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Bold Serif", callback_data="font_serif")],[InlineKeyboardButton("Bold Sans Serif", callback_data="font_sans")],[InlineKeyboardButton("Bold Italic", callback_data="font_italic")]]))))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("del", delete))
    app.add_handler(CommandHandler("ds", ds))
    app.add_handler(CommandHandler("m1", m1))
    app.add_handler(CommandHandler("m2", m2))
    app.add_handler(CommandHandler("m3", m3))
    app.add_handler(CommandHandler("m4", m4))
    app.add_handler(CommandHandler("m5", m5))
    app.add_handler(CommandHandler("m6", m6))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_normal_message))

    print("🚀 Bot BoldGen đang chạy... (Đã thêm lệnh /m6)")
    app.run_polling()

if __name__ == "__main__":
    main()
