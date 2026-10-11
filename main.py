import discord
from discord.ext import commands
import json, os, random, asyncio
from datetime import datetime
from flask import Flask
from threading import Thread

# ============ MANTER ONLINE 24H ============
app = Flask('')
@app.route('/')
def home(): return "Bot 24H Online - Enzo"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# ================= CONFIG =================
TOKEN = "MTU1ODI4MDcwNjk4NjA4MjQxNw.GW6i4i.3tLmi1ewDajVS1gsOnptffjfCLH7DH4e3c2NuY"
PREFIX = "!"

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

try:
    with open("enzo_db.json", "r") as f:
        db = json.load(f)
except:
    db = {"convites": {}, "confiaveis": [], "vitrine_data": "", "vitrine_user": "", "rpg_sessoes": {}, "tickets": {}}

def salvar():
    with open("enzo_db.json", "w") as f:
        json.dump(db, f)

@bot.command(name="divulgar")
async def divulgar(ctx, *, texto=""):
    if not ctx.message.attachments and "https://" not in texto:
        await ctx.send(f"{ctx.author.mention} ❌ Mande o print/prova!")
        return
    db["convites"][str(ctx.author.id)] = db["convites"].get(str(ctx.author.id), 0) + 1
    salvar()
    embed = discord.Embed(title="✅ Divulgação Validada", description=texto[:1000], color=0x2b2d31)
    embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)
    await ctx.message.add_reaction("💎")

@bot.event
async def on_member_join(member):
    try:
        invs = await member.guild.invites()
        for inv in invs:
            if inv.uses > 0:
                inviter_id = str(inv.inviter.id)
                db["convites"][inviter_id] = db["convites"].get(inviter_id, 0) + 1
                salvar()
    except: pass

@bot.command()
async def convites(ctx, membro: discord.Member = None):
    membro = membro or ctx.author
    total = db["convites"].get(str(membro.id), 0)
    await ctx.send(f"💎 {membro.mention} já convidou **{total} pessoas**!")

@bot.command()
async def avaliar(ctx):
    guild = ctx.guild
    nota = min(5 + (2 if len(guild.members) > 100 else 0) + (1 if len(guild.channels) > 10 else 0), 10)
    embed = discord.Embed(title=f"📊 Avaliação do {guild.name}", color=0x00ff00)
    embed.add_field(name="Nota", value=f"**{nota}/10**", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def vitrine(ctx, *, divulgacao=""):
    hoje = datetime.now().strftime("%d/%m/%Y")
    if db["vitrine_data"] == hoje:
        await ctx.send(f"❌ Vitrine já pega por <@{db['vitrine_user']}>!")
        return
    if not divulgacao:
        await ctx.send("Use: `!vitrine SEU LINK`")
        return
    db["vitrine_data"] = hoje
    db["vitrine_user"] = str(ctx.author.id)
    salvar()
    canal = discord.utils.get(ctx.guild.channels, name="💎・vitrine-do-dia")
    if not canal: canal = await ctx.guild.create_text_channel("💎・vitrine-do-dia")
    embed = discord.Embed(title="💎 VITRINE DO DIA", description=divulgacao, color=0xff0000)
    await canal.send(f"@everyone 🔥 DESTAQUE DO DIA DE {ctx.author.mention} 🔥", embed=embed)
    await ctx.send(f"✅ Foi pra vitrine em {canal.mention}!")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def confiavel(ctx, membro: discord.Member):
    cargo = discord.utils.get(ctx.guild.roles, name="✅ CONFIÁVEL")
    if not cargo:
        cargo = await ctx.guild.create_role(name="✅ CONFIÁVEL", colour=discord.Colour.green(), hoist=True)
    await membro.add_roles(cargo)
    if str(membro.id) not in db["confiaveis"]:
        db["confiaveis"].append(str(membro.id))
        salvar()
    await ctx.send(f"✅ {membro.mention} agora é CONFIÁVEL!")

@bot.command()
async def perfil(ctx, membro: discord.Member = None):
    membro = membro or ctx.author
    selo = "✅ CONFIÁVEL" if str(membro.id) in db["confiaveis"] else "❌ Sem selo"
    total = db["convites"].get(str(membro.id), 0)
    await ctx.send(f"💎 Perfil de {membro.mention}\nSelo: {selo}\nConvites: {total}")

@bot.command()
async def ticket(ctx):
    guild = ctx.guild
    cat = discord.utils.get(guild.categories, name="🎫 TICKETS")
    if not cat: cat = await guild.create_category("🎫 TICKETS")
    overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True), guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
    canal = await guild.create_text_channel(f"🎫・ticket-{ctx.author.name}", category=cat, overwrites=overwrites)
    await canal.send(f"{ctx.author.mention} Qual motivo? 1️⃣ VIP 2️⃣ Parceria 3️⃣ Denúncia")
    await ctx.send(f"✅ Ticket criado em {canal.mention}")

@bot.command()
async def fechar(ctx):
    if "ticket-" in ctx.channel.name:
        await ctx.send("🔒 Fechando...")
        await asyncio.sleep(2)
        await ctx.channel.delete()

GATILHOS_RPG = ["vamos fazer um rpg", "fazer um rpg", "quero rpg", "bora rpg"]

@bot.event
async def on_message(message):
    if message.author.bot: return
    msg_lower = message.content.lower()
    user_id = str(message.author.id)
    is_rpg_channel = "rpg" in message.channel.name.lower() if hasattr(message.channel, 'name') else False
    if user_id in db["rpg_sessoes"] and (is_rpg_channel or isinstance(message.channel, discord.DMChannel)):
        sessao = db["rpg_sessoes"][user_id]
        if sessao["etapa"] == "esperando_tema":
            sessao["tema"] = message.content
            sessao["etapa"] = "jogando"
            salvar()
            await message.channel.send(f"🔥 Tema **{message.content}**! Cena: 3 caminhos - 1 Vermelho, 2 Dourado, 3 Escuro. O que faz?")
            return
        elif sessao["etapa"] == "jogando":
            if "sair" in msg_lower:
                del db["rpg_sessoes"][user_id]
                salvar()
                await message.channel.send("RPG finalizado!")
                return
            await message.channel.send(f"[{sessao.get('tema')}] Você fez {message.content}! O que acontece depois? Você `pega`, `corre` ou `investiga`?")
            return
    for gatilho in GATILHOS_RPG:
        if gatilho in msg_lower:
            await message.channel.send(f"Olá {message.author.mention}! Qual tema de RPG? Ex: terror, magia...")
            db["rpg_sessoes"][user_id] = {"tema": "", "etapa": "esperando_tema"}
            salvar()
            return
    await bot.process_commands(message)

@bot.command()
async def ajuda(ctx):
    embed = discord.Embed(title="💎 COMANDOS", color=0x2b2d31)
    embed.add_field(name="📢 !divulgar", value="Valida divulgação", inline=False)
    embed.add_field(name="🏆 !convites / !perfil / !avaliar", value="Rank", inline=False)
    embed.add_field(name="💎 !vitrine / !ticket / !fechar / !confiavel", value="Gerenciar", inline=False)
    embed.add_field(name="🎲 RPG", value="`vamos fazer um rpg`", inline=False)
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"BOT ONLINE 24H COMO {bot.user}")

keep_alive()
bot.run(TOKEN)