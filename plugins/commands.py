from pyrogram import Client, filters

# /start command
@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text(
        "🎬 **Movie Name Corrector Bot**\n\n"
        "गलत movie name भेजो,\n"
        "मैं IMDb से सही नाम बता दूँगा ✅\n\n"
        "**Example:**\n"
        "`Dhurandar`\n"
        "`Pathan`\n"
        "`Bhool Bhulaiya`",
        quote=True
    )
