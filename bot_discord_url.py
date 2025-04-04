import os
import discord
import qrcode
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

# ฟังก์ชันสร้าง QR Code
def generate_qr_code(url: str, filename: str = "qrcode.png") -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    return filename

# ==========================
# ⌨️ Slash command: /compiler
# ==========================
@bot.tree.command(name="compiler", description="สร้าง QR Code จาก URL")
@app_commands.describe(protocol="โปรโตคอล (http หรือ https)", url="ลิงก์ที่ต้องการสร้าง QR Code")
async def slash_compiler(interaction: discord.Interaction, protocol: str, url: str):
    if protocol not in ["http", "https"]:
        await interaction.response.send_message("❌ โปรโตคอลไม่ถูกต้อง! เลือกได้แค่ `http` หรือ `https`", ephemeral=True)
        return

    full_url = f"{protocol}://{url}"

    # สร้าง QR Code
    qr_filename = generate_qr_code(full_url)

    # ส่ง QR Code กลับไปยังผู้ใช้
    file = discord.File(qr_filename, filename="qrcode.png")
    embed = discord.Embed(
        title="🔗 QR Code สำหรับ URL ของคุณ",
        description=f"URL: {full_url}",
        color=discord.Color.blue()
    )
    embed.set_image(url="attachment://qrcode.png")
    embed.set_footer(text="โดยคำสั่ง: /compiler")
    await interaction.response.send_message(embed=embed, file=file)

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
    embed.add_field(name="/compiler [protocol] [URL]", value="สร้าง QR Code จาก URL (Slash command).", inline=False)
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
    embed.add_field(name="/compiler [protocol] [URL]", value="สร้าง QR Code จาก URL (Slash command).", inline=False)
    embed.set_footer(text="สำหรับคำสั่งอื่นๆ สามารถติดต่อผู้ดูแลบอท.")
    await interaction.response.send_message(embed=embed)

# ==========================
# Add the protocol choices to the command
# ==========================
@slash_compiler.autocomplete('protocol')
async def protocol_autocomplete(interaction: discord.Interaction, current: str):
    choices = ['http', 'https']
    return [app_commands.Choice(name=choice, value=choice) for choice in choices if current.lower() in choice.lower()]

server_on()
bot.run(os.getenv("TOKEN"))
