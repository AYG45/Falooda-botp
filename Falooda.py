import instaloader
import os
import shutil
import re
import telebot

BOT_TOKEN = "7937100699:AAEbrT47jhKwcsLxtL7lAV4-2NjpnHQDuCk"
bot = telebot.TeleBot(BOT_TOKEN)

down = instaloader.Instaloader(
    download_video_thumbnails=False, 
    download_geotags=False, 
    download_comments=False, 
    save_metadata=False
)

def extract_shortcode(url):
    url = url.split('?')[0]
    match = re.search(r"instagram\.com\/(?:p|reel|tv)\/([A-Za-z0-9_-]+)", url)
    
    if match:
        shortcode = match.group(1)
        print(f"Extracted Shortcode: {shortcode}")
        return shortcode
    else:
        print("Shortcode not found. Please check the URL format.")
        return None

def download_post(url):
    try:
        post_shortcode = extract_shortcode(url)
        if post_shortcode is None:
            return None, "Invalid URL or shortcode not found."

        post = instaloader.Post.from_shortcode(down.context, post_shortcode)

        os.makedirs("temp", exist_ok=True)  

        print("Downloading post, please wait...")

        down.download_post(post, target="temp")

        downloaded_files = os.listdir("temp")
        print(f"Files in temp/: {downloaded_files}")

        media_files = [f"temp/{file}" for file in downloaded_files if file.endswith((".mp4", ".jpg")) and not file.startswith("thumbnail")]

        if not media_files:
            return None, "No images or videos found in the post."
        
        return media_files, None

    except Exception as e:
        print(f"Error: {e}")
        return None, f"Error: {e}"

#Bot Handling

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to FaloodaBot! Send me an Instagram post URL, and I'll download the media for you.")

@bot.message_handler(func=lambda message: "instagram.com" in message.text)
def handle_instagram_url(message):
    bot.reply_to(message, "Downloading the media, please wait...")

    url = message.text.strip()
    media_paths, error = download_post(url)

    if error:
        bot.reply_to(message, error)
    else:
        for media_path in media_paths:
            with open(media_path, "rb") as media:
                if media_path.endswith(".mp4"):
                    bot.send_video(message.chat.id, media)
                elif media_path.endswith(".jpg"):
                    bot.send_photo(message.chat.id, media)

            os.remove(media_path)

        shutil.rmtree("temp", ignore_errors=True)

print("Bot is running...")
bot.polling()
