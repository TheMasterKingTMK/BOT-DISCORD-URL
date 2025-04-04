import os
import discord
import base64
import qrcode
from io import BytesIO
from discord.ext import commands
from discord import app_commands
from MyServer import server_on

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    synced = await bot.tree.sync()
    print(f"✅ Bot {bot.user.name} พร้อมใช้งาน! | ซิงค์คำสั่ง {len(synced)} รายการ")

# ฟังก์ชันเข้ารหัส
def encode_url(protocol: str, url: str) -> str:
    if not (url.startswith("http://") or url.startswith("https://")):
        url = protocol + "://" + url
    encoded_bytes = base64.urlsafe_b64encode(url.encode('utf-8'))
    return encoded_bytes.decode('utf-8')

# ฟังก์ชันถอดรหัส
def decode_url(message: str) -> str:
    try:
        decoded_bytes = base64.urlsafe_b64decode(message)
        return decoded_bytes.decode('utf-8')
    except Exception:
        return "❌ ข้อความที่ให้มาไม่สามารถถอดรหัสได้!"

# ==========================
# ⌨️ Slash command: /compiler
# ==========================
@bot.tree.command(name="compiler", description="เข้ารหัส URL หรือสร้าง QR Code")
@app_commands.describe(protocol="โปรโตคอล (http, https, qr)", url="ลิงก์ที่ต้องการเข้ารหัส")
async def slash_compiler(interaction: discord.Interaction, protocol: str, url: str):
    if protocol not in ["http", "https", "qr"]:
        await interaction.response.send_message("❌ โปรโตคอลไม่ถูกต้อง! เลือกได้แค่ `http`, `https` หรือ `qr`", ephemeral=True)
        return

    if protocol == "qr":
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url  # default ถ้าไม่มี protocol
        img = qrcode.make(url)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        file = discord.File(buffer, filename="qrcode.png")
        await interaction.response.send_message(content="🧾 สร้าง QR Code สำเร็จ!", file=file)
    else:
        encoded = encode_url(protocol, url)
        embed = discord.Embed(
            title="🔒 เข้ารหัส URL สำเร็จ!",
            description=f"```\n{encoded}\n```",
            color=discord.Color.green()
        )
        embed.set_footer(text="โดยคำสั่ง: /compiler")
        await interaction.response.send_message(embed=embed)

# ==========================
# Autocomplete สำหรับ protocol
# ==========================
@slash_compiler.autocomplete('protocol')
async def protocol_autocomplete(interaction: discord.Interaction, current: str):
    choices = ['http', 'https', 'qr']
    return [app_commands.Choice(name=choice, value=choice) for choice in choices if current.lower() in choice.lower()]

# ==========================
# (คงเดิม) /decompiler
# ==========================
@bot.tree.command(name="decompiler", description="ถอดรหัส URL จากข้อความ")
@app_commands.describe(message="ข้อความที่เข้ารหัสไว้")
async def slash_decompiler(interaction: discord.Interaction, message: str):
    decoded = decode_url(message)
    embed = discord.Embed(
        title="🔓 ถอดรหัส URL สำเร็จ!" if not decoded.startswith("❌") else "❌ ไม่สามารถถอดรหัสได้",
        description=f"```\n{decoded}\n```",
        color=discord.Color.blue() if not decoded.startswith("❌") else discord.Color.red()
    )
    embed.set_footer(text="โดยคำสั่ง: /decompiler")
    await interaction.response.send_message(embed=embed)

# ==========================
# 📜 คำสั่ง !commands
# ==========================
@bot.command(name="commands")
async def commands_cmd(ctx):
    embed = discord.Embed(
        title="🆘 คำสั่งทั้งหมดของบอท:",
        description="ใช้คำสั่งเพื่อเข้าถึงฟังก์ชันต่างๆ ของบอท",
        color=discord.Color.orange()
    )
    embed.add_field(name="/compiler [protocol] [URL]", value="เข้ารหัส URL หรือสร้าง QR Code", inline=False)
    embed.add_field(name="/decompiler [ข้อความที่เข้ารหัส]", value="ถอดรหัสข้อความที่เข้ารหัส", inline=False)
    embed.set_footer(text="สำหรับคำสั่งอื่นๆ สามารถติดต่อผู้ดูแลบอท.")
    await ctx.send(embed=embed)

# ==========================
# 📜 Slash command: /commands
# ==========================
@bot.tree.command(name="commands", description="แสดงรายการคำสั่ง")
async def slash_commands(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🆘 คำสั่งทั้งหมดของบอท:",
        description="ใช้คำสั่งเพื่อเข้าถึงฟังก์ชันต่างๆ ของบอท",
        color=discord.Color.orange()
    )
    embed.add_field(name="/compiler [protocol] [URL]", value="เข้ารหัส URL หรือสร้าง QR Code", inline=False)
    embed.add_field(name="/decompiler [ข้อความที่เข้ารหัส]", value="ถอดรหัสข้อความที่เข้ารหัส", inline=False)
    embed.set_footer(text="สำหรับคำสั่งอื่นๆ สามารถติดต่อผู้ดูแลบอท.")
    await interaction.response.send_message(embed=embed)

server_on()
bot.run(os.getenv("TOKEN"))