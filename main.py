import telebot
import re
import os

# Replace with your bot token
BOT_TOKEN = "7480299117:AAEXx39TuEuZljNjADE7UTJMxI4S0dVxkH0"
CHANNEL_USERNAME = "TAL4_U"  # Replace with your channel's username (without '@')
ADMIN_CHAT_ID = 1517013110  # Replace with your admin chat ID
bot = telebot.TeleBot(BOT_TOKEN)

# Dictionaries to store user data and public data
user_data = {}
public_data = {}
notified_users = set()  # To track users who have already triggered notifications
all_users = set()  # To track all users for the total count

# Function to clean and extract Email:Password
def extract_email_pass(text):
    pattern = r"([\w\.-]+@[\w\.-]+):([^\s]+)"
    matches = re.findall(pattern, text)
    return matches

# Function to check if the user is a member of the channel
def is_user_member(user_id):
    try:
        status = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id).status
        return status in ["member", "administrator", "creator"]
    except Exception:
        return False

# Command: Start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    username = message.from_user.username or "No Username"
    first_name = message.from_user.first_name or "Unknown"

    # Check channel membership
    if not is_user_member(user_id):
        bot.reply_to(
            message,
            f"❌ **You must join our channel to use this bot.**\n\n"
            f"👉 [Join Channel](https://t.me/{CHANNEL_USERNAME})\n\n** Click /start After Join The Channel** ",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return

    # Add the user to the all_users set to track total users
    all_users.add(user_id)

    # Notify the admin about the new user
    if user_id not in notified_users:
        notified_users.add(user_id)
        bot.send_message(
            ADMIN_CHAT_ID,
            f"👤 **New User Alert!**\n\n"
            f"🔹 **User ID:** {user_id}\n"
            f"🔹 **Username:** @{username}\n"
            f"🔹 **Name:** {first_name}\n"
            f"🔢 **Total Users:** {len(all_users)}",
            parse_mode="Markdown"
        )

    # Welcome message for the user
    bot.reply_to(
        message,
        "🎉 **Welcome to Combo Maker!** 🎉\n\n"
        "🚀 **Features:**\n"
        "🔹 *Clean and store Email:Password combos.*\n"
        "🔹 *Retrieve your private Combos by using* /gethits.\n"
        "🔹 *Get Public Combos with* /publichits.\n\n"
        "💡 Type /help  *for detailed instructions.*\n\n"
        "📌 *Just Send  mail mass in Any Format*\n"
        "I will make a Combo for you!",
        parse_mode="Markdown"
    )

# Command: Help
@bot.message_handler(commands=['help'])
def send_help(message):
    user_id = message.chat.id

    # Check channel membership
    if not is_user_member(user_id):
        bot.reply_to(
            message,
            f"❌ **You must join our channel to use this bot.**\n\n Click /start After Join The Channel"
            f"👉 [Join Channel](https://t.me/{CHANNEL_USERNAME})",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return

    bot.reply_to(
        message,
        "📚 **Help Menu**\n\n"
        "🔹 **Send Accounts:**\n"
        "*Just send a list of accounts in any format. I will make combos from it:*\n\n"
        "🔹 **Retrieve Accounts:**\n"
        "Type /gethits to download your private Combo as a file.\n\n"
        "🔹 **Access Public Combo:**\n"
        "Type /publichits to get public Combos.\n\n"
        "🔸 *Use this bot responsibly.*",
        parse_mode="Markdown"
    )

# Handle Messages with Accounts
@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def process_message(message):
    user_id = message.chat.id

    # Check channel membership
    if not is_user_member(user_id):
        bot.reply_to(
            message,
            f"❌ **You must join our channel to use this bot.**\n\n"
            f"👉 [Join Channel](https://t.me/{CHANNEL_USERNAME})",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return

    raw_text = message.text
    cleaned_accounts = extract_email_pass(raw_text)

    if cleaned_accounts:
        # Store accounts in user data
        if user_id not in user_data:
            user_data[user_id] = []

        user_data[user_id].extend(cleaned_accounts)
        public_data[user_id] = public_data.get(user_id, []) + cleaned_accounts
        total = len(user_data[user_id])

        bot.reply_to(
            message,
            f"✅ **{len(cleaned_accounts)} accounts added successfully!**\n"
            f"📦 **Your Total Stored Accounts:** {total}\n\n"
            "🚀 *Keep sending accounts to store more!*",
            parse_mode="Markdown"
        )
    else:
        bot.reply_to(
            message,
            "❌ *No valid Email:Password combos found.*\n\n"
            "📌 **Tip:** Send accounts in this format:\n"
            "`example@mail.com:password123`",
            parse_mode="Markdown"
        )

# Command: Retrieve Accounts
@bot.message_handler(commands=['gethits'])
def retrieve_accounts(message):
    user_id = message.chat.id

    # Check channel membership
    if not is_user_member(user_id):
        bot.reply_to(
            message,
            f"❌ **You must join our channel to use this bot.**\n\n"
            f"👉 [Join Channel](https://t.me/{CHANNEL_USERNAME})",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return

    if user_id not in user_data or not user_data[user_id]:
        bot.reply_to(
            message,
            "❌ *No Combo stored yet.*\n\n"
            "💡 *Send your accounts to store them!*",
            parse_mode="Markdown"
        )
        return

    # Retrieve and save accounts to a text file
    accounts = user_data[user_id]
    file_path = f"{user_id}_accounts.txt"
    with open(file_path, "w") as file:
        for email, password in accounts:
            file.write(f"{email}:{password}\n")

    # Send the file to the user
    with open(file_path, "rb") as file:
        bot.send_document(
            message.chat.id, file, caption="📄 **Here are your stored accounts!**",
            parse_mode="Markdown"
        )

    os.remove(file_path)  # Clean up the file after sending

# Command: Public Hits
@bot.message_handler(commands=['publichits'])
def public_hits(message):
    user_id = message.chat.id

    # Check channel membership
    if not is_user_member(user_id):
        bot.reply_to(
            message,
            f"❌ **You must join our channel to use this bot.**\n\n"
            f"👉 [Join Channel](https://t.me/{CHANNEL_USERNAME})",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return

    all_accounts = []
    for accounts in public_data.values():
        all_accounts.extend(accounts)

    if not all_accounts:
        bot.reply_to(
            message,
            "❌ *No public Combo available yet.*\n\n"
            "💡 *Start sending accounts to contribute!*",
            parse_mode="Markdown"
        )
        return

    # Split public data into chunks of 200
    chunk_size = 200
    chunks = [all_accounts[i:i + chunk_size] for i in range(0, len(all_accounts), chunk_size)]

    for i, chunk in enumerate(chunks):
        file_path = f"public_accounts_part_{i + 1}.txt"
        with open(file_path, "w") as file:
            for email, password in chunk:
                file.write(f"{email}:{password}\n")

        # Send the file to the user
        with open(file_path, "rb") as file:
            bot.send_document(
                message.chat.id, file,
                caption=f"📄 **Public Accounts (Part {i + 1})**\n\n"
                        "💡 *Use these accounts responsibly.*",
                parse_mode="Markdown"
            )

        os.remove(file_path)  # Clean up the file after sending

# Command: Total Users
@bot.message_handler(commands=['totalusers'])
def total_users(message):
    bot.reply_to(
        message.chat.id,
        f"🔢 **Total Users:** {len(all_users)}",
        parse_mode="Markdown"
    )

# Run the bot
print("🚀 Bot is running...")
bot.infinity_polling()
