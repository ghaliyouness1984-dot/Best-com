import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8618381817:AAHvt4BAUONCzuFmSQiVjDvJHCg92RZW1cI"
ADMIN_ID = None
WHATSAPP = "0664530175"

PRODUCTS = [
    {"id": 1, "name": "عباية أنيقة فاخرة", "emoji": "🖤", "desc": "عباية أنيقة من قماش عالي الجودة", "price": 350},
    {"id": 2, "name": "عباية كيمونو", "emoji": "🦋", "desc": "عباية كيمونو بتطريز رائع", "price": 420},
    {"id": 3, "name": "عباية يومية خفيفة", "emoji": "🌿", "desc": "خفيفة ومريحة للاستخدام اليومي", "price": 280},
    {"id": 4, "name": "عباية مناسبات", "emoji": "✨", "desc": "للأعراس والمناسبات الخاصة", "price": 550},
    {"id": 5, "name": "عباية رياضية", "emoji": "🏃‍♀️", "desc": "مريحة وعملية للحياة النشيطة", "price": 320},
]

carts = {}
orders = {}
order_counter = [1]

def get_cart(user_id):
    if user_id not in carts:
        carts[user_id] = []
    return carts[user_id]

def get_cart_total(user_id):
    cart = get_cart(user_id)
    return sum(item["price"] * item["qty"] for item in cart)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛍️ المنتجات", callback_data="products")],
        [InlineKeyboardButton("🛒 سلتي", callback_data="cart"),
         InlineKeyboardButton("📦 طلباتي", callback_data="my_orders")],
        [InlineKeyboardButton("📞 تواصل معنا", callback_data="contact")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    text = (
        "🌟 *أهلاً بك في Best-Ecom* 🌟\n"
        "أفضل متجر للعبايات المغربية الفاخرة\n\n"
        "اختر ما تريد من القائمة أدناه 👇"
    )
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for p in PRODUCTS:
        keyboard.append([InlineKeyboardButton(
            f"{p['emoji']} {p['name']} - {p['price']} درهم",
            callback_data=f"product_{p['id']}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    await query.edit_message_text(
        "🛍️ *قائمة المنتجات*\n\nاختر منتجاً لمعرفة التفاصيل:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def show_product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int):
    query = update.callback_query
    await query.answer()
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        await query.edit_message_text("❌ المنتج غير موجود")
        return
    keyboard = [
        [InlineKeyboardButton("➕ أضف للسلة", callback_data=f"add_{product_id}")],
        [InlineKeyboardButton("🔙 رجوع للمنتجات", callback_data="products")],
    ]
    text = (
        f"{product['emoji']} *{product['name']}*\n\n"
        f"📝 {product['desc']}\n\n"
        f"💰 السعر: *{product['price']} درهم*"
    )
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return
    cart = get_cart(user_id)
    existing = next((item for item in cart if item["id"] == product_id), None)
    if existing:
        existing["qty"] += 1
    else:
        cart.append({"id": product_id, "name": product["name"], "price": product["price"], "qty": 1})
    keyboard = [
        [InlineKeyboardButton("🛒 عرض السلة", callback_data="cart")],
        [InlineKeyboardButton("🛍️ متابعة التسوق", callback_data="products")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
    ]
    await query.edit_message_text(
        f"✅ تم إضافة *{product['name']}* للسلة!\n\n💰 المجموع: *{get_cart_total(user_id)} درهم*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cart = get_cart(user_id)
    if not cart:
        keyboard = [[InlineKeyboardButton("🛍️ تسوق الآن", callback_data="products")],
                    [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]]
        await query.edit_message_text("🛒 سلتك فارغة!\n\nأضف بعض المنتجات 😊",
                                      reply_markup=InlineKeyboardMarkup(keyboard))
        return
    text = "🛒 *سلتك*\n\n"
    for item in cart:
        text += f"• {item['name']} × {item['qty']} = {item['price'] * item['qty']} درهم\n"
    text += f"\n💰 *المجموع: {get_cart_total(user_id)} درهم*"
    keyboard = [
        [InlineKeyboardButton("✅ تأكيد الطلب", callback_data="confirm_order")],
        [InlineKeyboardButton("🗑️ إفراغ السلة", callback_data="clear_cart")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    carts[user_id] = []
    keyboard = [[InlineKeyboardButton("🛍️ تسوق الآن", callback_data="products")],
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]]
    await query.edit_message_text("🗑️ تم إفراغ السلة", reply_markup=InlineKeyboardMarkup(keyboard))

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cart = get_cart(user_id)
    if not cart:
        await query.edit_message_text("❌ السلة فارغة!")
        return
    context.user_data["awaiting_address"] = True
    keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data="cart")]]
    await query.edit_message_text(
        "📍 *أدخل عنوانك للتوصيل:*\n\n"
        "مثال: الدار البيضاء، حي المحمدي، شارع...",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if context.user_data.get("awaiting_address"):
        context.user_data["awaiting_address"] = False
        address = update.message.text
        cart = get_cart(user_id)
        total = get_cart_total(user_id)
        order_id = order_counter[0]
        order_counter[0] += 1
        if user_id not in orders:
            orders[user_id] = []
        orders[user_id].append({
            "id": order_id,
            "items": cart.copy(),
            "total": total,
            "address": address,
            "status": "قيد المعالجة ⏳"
        })
        carts[user_id] = []
        wa_link = f"https://wa.me/212{WHATSAPP[1:]}?text=طلب جديد رقم {order_id}%0aالعنوان: {address}%0aالمجموع: {total} درهم"
        keyboard = [
            [InlineKeyboardButton("💬 تواصل واتساب", url=wa_link)],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
        ]
        await update.message.reply_text(
            f"✅ *تم تأكيد طلبك بنجاح!*\n\n"
            f"📦 رقم الطلب: *#{order_id}*\n"
            f"📍 العنوان: {address}\n"
            f"💰 المجموع: *{total} درهم*\n\n"
            f"سنتواصل معك قريباً 🙏",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

async def show_my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_orders = orders.get(user_id, [])
    if not user_orders:
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
        await query.edit_message_text("📦 ليس لديك طلبات بعد!", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    text = "📦 *طلباتي*\n\n"
    for order in user_orders[-5:]:
        text += f"🔹 طلب #{order['id']} — {order['total']} درهم\n"
        text += f"   الحالة: {order['status']}\n\n"
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    wa_link = f"https://wa.me/212{WHATSAPP[1:]}"
    keyboard = [
        [InlineKeyboardButton("💬 واتساب", url=wa_link)],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")],
    ]
    await query.edit_message_text(
        "📞 *تواصل معنا*\n\n"
        f"📱 واتساب: {WHATSAPP}\n\n"
        "نرد عليك في أقرب وقت 😊",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "main_menu":
        await show_main_menu(update, context)
    elif data == "products":
        await show_products(update, context)
    elif data.startswith("product_"):
        pid = int(data.split("_")[1])
        await show_product_detail(update, context, pid)
    elif data.startswith("add_"):
        pid = int(data.split("_")[1])
        await add_to_cart(update, context, pid)
    elif data == "cart":
        await show_cart(update, context)
    elif data == "clear_cart":
        await clear_cart(update, context)
    elif data == "confirm_order":
        await confirm_order(update, context)
    elif data == "my_orders":
        await show_my_orders(update, context)
    elif data == "contact":
        await show_contact(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت شغال!")
    app.run_polling()

if __name__ == "__main__":
    main()
