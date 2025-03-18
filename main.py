import discord
from discord.ext import commands
import requests
import os

# Lấy khóa API và token từ biến môi trường
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = "https://api.together.xyz/v1/images/generations"

# Khởi tạo bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def generate_image(prompt, output_file="generated_image.png"):
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
        print(f"Phản hồi từ API: {result}")
        
        image_url = result.get("data", [{}])[0].get("url")
        
        if image_url:
            img_data = requests.get(image_url).content
            with open(output_file, "wb") as f:
                f.write(img_data)
            print(f"Đã lưu ảnh vào {output_file}")
            return output_file
        else:
            print("Không tìm thấy URL ảnh trong phản hồi")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tạo ảnh: {e}")
        if hasattr(e.response, "text"):
            print(f"Chi tiết lỗi: {e.response.text}")
        return None

@bot.event
async def on_ready():
    print(f"Bot đã sẵn sàng: {bot.user}")

@bot.command()
async def generate(ctx, *, prompt):
    await ctx.send(f"Đang tạo ảnh cho: '{prompt}'...")
    
    image_file = generate_image(prompt)
    
    if image_file and os.path.exists(image_file):
        print(f"File ảnh tồn tại: {image_file}")
        with open(image_file, "rb") as f:
            picture = discord.File(f)
            await ctx.send(file=picture)
        os.remove(image_file)
    else:
        print("Không tìm thấy file ảnh")
        await ctx.send("Không thể tạo ảnh. Vui lòng kiểm tra lại prompt hoặc thử lại sau!")

# Chạy bot
bot.run(DISCORD_TOKEN)
