import base64
import zlib
import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== CUSTOM XOR =====
def xor(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

# ===== BYTE SHIFT =====
def shift(data):
    return bytes([(b + 3) % 256 for b in data])

KEY1 = b"ZEXY_KEY_1"
KEY2 = b"ZEXY_KEY_2"

# Store user states
user_files = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when /start is issued."""
    await update.message.reply_text(
        "🔒 *Zexy Encryption Bot* 🔒\n\n"
        "Send me a `.py` file and I'll encrypt it with multi-layer protection!\n\n"
        "*Features:*\n"
        "• Byte Shift\n"
        "• Double XOR Encryption\n"
        "• Compression\n"
        "• Reversal\n"
        "• Double Base64 Encoding\n\n"
        "Just send any `.py` file to get started!",
        parse_mode='Markdown'
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle uploaded files."""
    document = update.message.document
    
    # Check if it's a Python file
    if not document.file_name.endswith('.py'):
        await update.message.reply_text("❌ Please send a `.py` file only!")
        return
    
    # Send processing message
    status_msg = await update.message.reply_text("🔄 Encrypting your file...")
    
    try:
        # Download the file
        file = await context.bot.get_file(document.file_id)
        
        # Read the file content
        file_content = await file.download_as_bytearray()
        code = file_content.decode('utf-8')
        
        # Encrypt the code
        data = code.encode()
        
        # Layer 1: shift
        data = shift(data)
        
        # Layer 2: XOR 1
        data = xor(data, KEY1)
        
        # Layer 3: compress
        data = zlib.compress(data)
        
        # Layer 4: reverse
        data = data[::-1]
        
        # Layer 5: XOR 2
        data = xor(data, KEY2)
        
        # Layer 6: base64 x2
        data = base64.b64encode(base64.b64encode(data))
        
        # Create the final encrypted script
        final_code = f'''import base64, zlib

def xor(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def unshift(data):
    return bytes([(b - 3) % 256 for b in data])

KEY1 = {KEY1}
KEY2 = {KEY2}

data = {data}

# reverse process
data = base64.b64decode(base64.b64decode(data))
data = xor(data, KEY2)
data = data[::-1]
data = zlib.decompress(data)
data = xor(data, KEY1)
data = unshift(data)

code = data.decode()
exec(code)
'''
        
        # Save encrypted file temporarily
        output_filename = f"enc_{document.file_name}"
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(final_code)
        
        # Send the encrypted file back
        with open(output_filename, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=output_filename,
                caption="✅ *File encrypted successfully!*\n\n"
                       "🔐 Run it like a normal Python script.\n"
                       "⚡ The code will auto-execute when run.\n\n"
                       f"Original: `{document.file_name}`\n"
                       f"Encrypted: `{output_filename}`",
                parse_mode='Markdown'
            )
        
        # Clean up
        os.remove(output_filename)
        await status_msg.delete()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await status_msg.delete()
        await update.message.reply_text(f"❌ Error encrypting file: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    await update.message.reply_text(
        "*How to use:*\n\n"
        "1️⃣ Send me any `.py` file\n"
        "2️⃣ I'll encrypt it with 6 layers of protection\n"
        "3️⃣ Download the encrypted file\n"
        "4️⃣ Run it: `python encrypted_file.py`\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/info - Show encryption details",
        parse_mode='Markdown'
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show encryption details."""
    await update.message.reply_text(
        "🔐 *Encryption Layers:*\n\n"
        "1️⃣ *Byte Shift* (+3 to each byte)\n"
        "2️⃣ *XOR Layer 1* (Key: ZEXY_KEY_1)\n"
        "3️⃣ *zLib Compression*\n"
        "4️⃣ *Byte Reversal*\n"
        "5️⃣ *XOR Layer 2* (Key: ZEXY_KEY_2)\n"
        "6️⃣ *Double Base64 Encoding*\n\n"
        "The encrypted file contains a stub that:\n"
        "• Automatically decrypts the code\n"
        "• Executes it using `exec()`\n"
        "• Keeps the original functionality intact",
        parse_mode='Markdown'
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ An error occurred. Please try again or contact support."
        )

def main():
    """Start the bot."""
    # Your bot token
    BOT_TOKEN = "8759480783:AAHSN0aN5IpBd3nWXMtHCwidRewOWws2bOU"
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🤖 Bot is starting...")
    print("✅ Bot token loaded successfully!")
    print("📱 Bot is now running. Send a .py file to @ZexyEncryptionBot")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()