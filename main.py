import discord
from discord.ext import commands
import requests
import os
import time
import zipfile

# Lấy khóa API và token từ biến môi trường
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = "https://api.together.xyz/v1/images/generations"

# Đường dẫn lưu trữ trong Volume
STORAGE_PATH = "/app/storage"

# Tạo thư mục lưu trữ nếu chưa có
if not os.path.exists(STORAGE_PATH):
    os.makedirs(STORAGE_PATH)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def generate_image(prompt):
    timestamp = int(time.time())
    output_file = f"{STORAGE_PATH}/image_{timestamp}.png"
    
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "black-forest-labs/FLUX.1-schnell-Free",
        "prompt": prompt,
        "steps": 4,
        "n": 1,
        "width": 512,
        "height": 512,
        "response_format": "url"
    }

    print(f"Đang gửi yêu cầu đến Together AI: {payload}")
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=180)
        response.raise_for_status()
        
        result = response.json()
        image_url = result.get("data", [{}])[0].get("url")
        
        if image_url:
            img_data = requests.get(image_url).content
            with open(output_file, "wb") as f:
                f.write(img_data)
            print(f"Đã lưu ảnh vào {output_file}")
            return output_file
        return None
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tạo ảnh: {e}")
        return None

@bot.event
async def on_ready():
    print(f"Bot đã sẵn sàng: {bot.user}")

@bot.command()
async def generate(ctx, *, prompt):
    await ctx.send(f"Đang tạo ảnh cho: '{prompt}'...")
    
    image_file = generate_image(prompt)
    
    if image_file and os.path.exists(image_file):
        file_name = os.path.basename(image_file)
        with open(image_file, "rb") as f:
            picture = discord.File(f)
            await ctx.send(f"Ảnh đã lưu: `{file_name}`", file=picture)
    else:
        await ctx.send("Không thể tạo ảnh.")

@bot.command()
async def listfiles(ctx):
    files = [f for f in os.listdir(STORAGE_PATH) if f.endswith(".png")]
    if files:
        file_list = "\n".join(files)
        await ctx.send(f"Danh sách ảnh đã lưu:\n```\n{file_list}\n```\nDùng `!downloadall` để tải tất cả.")
    else:
        await ctx.send("Chưa có ảnh nào được lưu.")

@bot.command()
async def downloadall(ctx):
    await ctx.send("Đang nén tất cả ảnh thành ZIP...")
    
    # Lấy danh sách file .png
    files = [f for f in os.listdir(STORAGE_PATH) if f.endswith(".png")]
    if not files:
        await ctx.send("Không có ảnh nào để tải.")
        return
    
    # Tạo file ZIP tạm thời
    zip_path = f"{STORAGE_PATH}/images_all.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            file_path = os.path.join(STORAGE_PATH, file)
            zipf.write(file_path, file)
    
    # Gửi file ZIP
    if os.path.exists(zip_path):
        with open(zip_path, "rb") as f:
            zip_file = discord.File(f)
            await ctx.send("Đây là tất cả ảnh trong ZIP:", file=zip_file)
        os.remove(zip_path)  # Xóa file ZIP sau khi gửi
    else:
        await ctx.send("Lỗi khi tạo ZIP.")

bot.run(DISCORD_TOKEN)
