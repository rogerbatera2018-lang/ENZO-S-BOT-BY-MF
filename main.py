import discord
from discord.ext import commands
import json, os, random, asyncio
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

# ============ MANTER ONLINE 24H ============
app = Flask('')
@app.route('/')
def home(): return "Bot 24H Online - ENZO'S BOT"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# ================= CONFIG =================
TOKEN = "MTU1ODI4MDcwNjk4NjA4MjQxNw.G0rqWD.4ugHkVc6Lo1TZMzSnD-hkT6YqZ0YsdGjumil3c"
PREFIX = "!"

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

try:
    with open("enzos_bot_db.json", "r") as f:
        db = json.load(f)
except:
    db = {"convites": {}, "confiaveis": [], "vitrine_data": "", "vitrine_user": "", "rpg_sessoes": {}, "tickets": {}, "casamentos": {}}

def salvar():
    with open("enzos_bot_db.json", "w") as f:
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
    casado_id = db["casamentos"].get(str(membro.id))
    status = f"💍 Casado com <@{casado_id}>" if casado_id else "💔 Solteiro(a)"
    await ctx.send(f"💎 Perfil de {membro.mention}\nSelo: {selo}\nConvites: {total}\n{status}")

@bot.command()
async def ticket(ctx):
    guild = ctx.guild
    cat = discord.utils.get(guild.categories, name="🎫 TICKETS")
    if not cat: cat = await guild.create_category("🎫 TICKETS")
    overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True), guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
    canal = await guild.create_text_channel(f"🎫・ticket-{ctx.author.name}", category=cat, overwrites=overwrites)
    # Mensagem gravada original mantida + novos motivos adicionados
    await canal.send(f"{ctx.author.mention} Qual motivo? 1️⃣ VIP 2️⃣ Parceria 3️⃣ Denúncia 4️⃣ Dúvidas 5️⃣ Suporte 6️⃣ Sugestões 7️⃣ Bug 8️⃣ Outros")
    await ctx.send(f"✅ Ticket criado em {canal.mention}")

@bot.command()
async def fechar(ctx):
    if "ticket-" in ctx.channel.name:
        await ctx.send("🔒 Fechando...")
        await asyncio.sleep(2)
        await ctx.channel.delete()

# ============ NOVOS COMANDOS ENZO'S BOT - 50 COMANDOS ============
@bot.command()
async def beijar(ctx, membro: discord.Member = None):
    if not membro:
        await ctx.send(f"{ctx.author.mention} ❌ Use: `!beijar @usuario`")
        return
    await ctx.send(f"😘 {ctx.author.mention} DEU UM BEIJO APAIXONADO EM {membro.mention}! 💋")

@bot.command()
async def casar(ctx, membro: discord.Member = None):
    if not membro:
        await ctx.send(f"{ctx.author.mention} ❌ Use: `!casar @usuario`")
        return
    if membro.id == ctx.author.id or membro.bot:
        await ctx.send(f"{ctx.author.mention} ❌ Não pode casar com você mesmo ou com bot!")
        return
    id1 = str(ctx.author.id)
    id2 = str(membro.id)
    if id1 in db["casamentos"]:
        await ctx.send(f"{ctx.author.mention} ❌ Você já está casado com <@{db['casamentos'][id1]}>! Use `!divorcio`")
        return
    if id2 in db["casamentos"]:
        await ctx.send(f"{ctx.author.mention} ❌ {membro.mention} já está casado!")
        return
    db["casamentos"][id1] = id2
    db["casamentos"][id2] = id1
    salvar()
    await ctx.send(f"💍 {ctx.author.mention} se casou com {membro.mention}! Felicidades aos pombinhos! 💖")

@bot.command()
async def divorcio(ctx):
    id1 = str(ctx.author.id)
    if id1 not in db["casamentos"]:
        await ctx.send(f"{ctx.author.mention} ❌ Você não está casado!")
        return
    id2 = db["casamentos"][id1]
    del db["casamentos"][id1]
    if id2 in db["casamentos"]:
        del db["casamentos"][id2]
    salvar()
    await ctx.send(f"💔 Que pena, <@{id1}> e <@{id2}> se separaram! Esses dois pombinhos se separaram! 🕊️")

@bot.command()
async def casal(ctx, membro: discord.Member = None):
    alvo = membro or ctx.author
    cid = db["casamentos"].get(str(alvo.id))
    if cid:
        await ctx.send(f"💍 {alvo.mention} está casado com <@{cid}>! 💖")
    else:
        await ctx.send(f"💔 {alvo.mention} está solteiro(a)!")

@bot.command()
async def abracar(ctx, membro: discord.Member = None):
    if not membro: await ctx.send(f"{ctx.author.mention} ❌ Use `!abracar @user`"); return
    await ctx.send(f"🤗 {ctx.author.mention} DEU UM ABRAÇO EM {membro.mention}! 💖")

@bot.command()
async def socar(ctx, membro: discord.Member = None):
    if not membro: await ctx.send(f"{ctx.author.mention} ❌ Use `!socar @user`"); return
    await ctx.send(f"👊 {ctx.author.mention} SOCOU {membro.mention}! 💥")

@bot.command()
async def tapa(ctx, membro: discord.Member = None):
    if not membro: await ctx.send(f"{ctx.author.mention} ❌ Use `!tapa @user`"); return
    await ctx.send(f"👋 {ctx.author.mention} DEU UM TAPA EM {membro.mention}! 😬")

@bot.command()
async def cafune(ctx, membro: discord.Member = None):
    if not membro: await ctx.send(f"{ctx.author.mention} ❌ Use `!cafune @user`"); return
    await ctx.send(f"🥰 {ctx.author.mention} fez cafuné em {membro.mention}! 💆")

@bot.command()
async def morder(ctx, membro: discord.Member = None):
    if not membro: await ctx.send(f"{ctx.author.mention} ❌ Use `!morder @user`"); return
    await ctx.send(f"😏 {ctx.author.mention} mordeu {membro.mention}! 🦷")

@bot.command()
async def lamber(ctx, membro: discord.Member = None):
    if not membro: await ctx.send(f"{ctx.author.mention} ❌ Use `!lamber @user`"); return
    await ctx.send(f"👅 {ctx.author.mention} lambeu {membro.mention}! 🤤")

@bot.command()
async def cheirar(ctx, membro: discord.Member = None):
    if not membro: await ctx.send(f"{ctx.author.mention} ❌ Use `!cheirar @user`"); return
    await ctx.send(f"👃 {ctx.author.mention} cheirou {membro.mention}! 🌸")

@bot.command()
async def chutar(ctx, membro: discord.Member = None):
    if not membro: await ctx.send(f"{ctx.author.mention} ❌ Use `!chutar @user`"); return
    await ctx.send(f"🦶 {ctx.author.mention} chutou {membro.mention}! 💥")

@bot.command()
async def matar(ctx, membro: discord.Member = None):
    if not membro: await ctx.send(f"{ctx.author.mention} ❌ Use `!matar @user`"); return
    await ctx.send(f"🔪 {ctx.author.mention} matou {membro.mention}! 💀")

@bot.command()
async def roubar(ctx, membro: discord.Member = None):
    if not membro: await ctx.send(f"{ctx.author.mention} ❌ Use `!roubar @user`"); return
    await ctx.send(f"🥷 {ctx.author.mention} roubou {membro.mention}! 💰")

@bot.command()
async def carinho(ctx, membro: discord.Member = None):
    if not membro: await ctx.send(f"{ctx.author.mention} ❌ Use `!carinho @user`"); return
    await ctx.send(f"🥺 {ctx.author.mention} fez carinho em {membro.mention}! 💕")

@bot.command()
async def ship(ctx, m1: discord.Member = None, m2: discord.Member = None):
    if not m1 or not m2: await ctx.send("❌ Use `!ship @user1 @user2`"); return
    await ctx.send(f"💘 {m1.mention} + {m2.mention} = {random.randint(0,100)}% compatíveis! 💖")

@bot.command()
async def amor(ctx, membro: discord.Member = None):
    if not membro: await ctx.send("❌ Use `!amor @user`"); return
    await ctx.send(f"💝 {ctx.author.mention} ama {membro.mention} {random.randint(0,100)}%! 😍")

@bot.command()
async def sorte(ctx):
    await ctx.send(f"🍀 {ctx.author.mention} sua sorte: {random.choice(['Boa!','Ruim!','Mais ou menos','Incrível!'])} ✨")

@bot.command(name="8ball")
async def _8ball(ctx, *, pergunta=""):
    await ctx.send(f"🎱 {random.choice(['Sim','Não','Talvez','Com certeza','Nunca'])}! 🔮")

@bot.command()
async def dado(ctx):
    await ctx.send(f"🎲 {ctx.author.mention} tirou {random.randint(1,6)}! 🎯")

@bot.command()
async def moeda(ctx):
    await ctx.send(f"🪙 {random.choice(['Cara','Coroa'])}! ✨")

@bot.command()
async def piada(ctx):
    await ctx.send(f"😂 {random.choice(['Por que o livro foi ao médico? Tava com dor de lombada!','O que o pato disse pra pata? Vem quá!'])} 🤣")

@bot.command()
async def cantada(ctx, membro: discord.Member = None):
    c = random.choice(["Você é Wi-Fi? Que conexão! 📶","Caiu do céu? 😇"])
    if membro: await ctx.send(f"😏 {ctx.author.mention} para {membro.mention}: {c} 💘")
    else: await ctx.send(f"😏 {c} 💘")

@bot.command()
async def elogiar(ctx, membro: discord.Member = None):
    if not membro: return
    await ctx.send(f"🌟 {ctx.author.mention} elogiou {membro.mention}: Você é incrível! ✨")

@bot.command()
async def xingar(ctx, membro: discord.Member = None):
    if not membro: return
    await ctx.send(f"🤬 {ctx.author.mention} xingou {membro.mention} de brincadeira! 😂")

@bot.command()
async def fofo(ctx, membro: discord.Member = None):
    alvo = membro or ctx.author
    await ctx.send(f"🥰 {alvo.mention} é muito fofo(a)! 💖")

@bot.command()
async def feio(ctx, membro: discord.Member = None):
    alvo = membro or ctx.author
    await ctx.send(f"😜 {alvo.mention} é feinho mas a gente ama! 😂💖")

@bot.command()
async def gay(ctx, membro: discord.Member = None):
    alvo = membro or ctx.author
    await ctx.send(f"🏳️‍🌈 {alvo.mention} é {random.randint(0,100)}% gay! 😂")

@bot.command()
async def sorteio(ctx, *, texto=""):
    if not texto: await ctx.send("❌ Use `!sorteio @user1 @user2`"); return
    await ctx.send(f"🎉 Vencedor: {random.choice(texto.split())}! 🥳")

@bot.command()
async def ppt(ctx, escolha=""):
    if escolha.lower() not in ["pedra","papel","tesoura"]: await ctx.send("Use `!ppt pedra/papel/tesoura`"); return
    await ctx.send(f"✊ Você: {escolha} | ENZO'S BOT: {random.choice(['pedra','papel','tesoura'])} 🎮")

@bot.command()
async def curiosidade(ctx):
    await ctx.send(f"🤓 {random.choice(['Polvo tem 3 corações 🐙','ENZO\'S BOT é brabo 💖'])}")

@bot.command()
async def fato(ctx):
    await ctx.send(f"📚 Fato: Água quente congela mais rápido! 🧊")

@bot.command()
async def conselho(ctx):
    await ctx.send(f"💡 Conselho: Beba água! 💧")

@bot.command()
async def frase(ctx):
    await ctx.send(f"💬 \"Você consegue!\" - ENZO'S BOT ✨")

@bot.command()
async def id(ctx, membro: discord.Member = None):
    m = membro or ctx.author
    await ctx.send(f"🆔 ID de {m.mention}: {m.id}")

@bot.command()
async def avatar(ctx, membro: discord.Member = None):
    m = membro or ctx.author
    e = discord.Embed(title=f"Avatar de {m.name}", color=0x2b2d31)
    e.set_image(url=m.display_avatar.url)
    await ctx.send(embed=e)

@bot.command()
async def say(ctx, *, texto=""):
    if texto: await ctx.send(texto)

@bot.command()
async def abraco(ctx, membro: discord.Member = None):
    if not membro: return
    await ctx.send(f"🫂 {ctx.author.mention} abraçou {membro.mention}! 💞")

@bot.command()
async def beijo(ctx, membro: discord.Member = None):
    if not membro: return
    await ctx.send(f"💋 {ctx.author.mention} mandou um beijo pra {membro.mention}! 😘")

@bot.command()
async def sapeca(ctx, membro: discord.Member = None):
    if not membro: return
    await ctx.send(f"😈 {ctx.author.mention} deu uma sapecada em {membro.mention}! 🔥")

@bot.command()
async def cutucar(ctx, membro: discord.Member = None):
    if not membro: return
    await ctx.send(f"👉 {ctx.author.mention} cutucou {membro.mention}! 😜")

@bot.command()
async def dormir(ctx):
    await ctx.send(f"😴 {ctx.author.mention} foi dormir! 🌙💤")

@bot.command()
async def acordar(ctx):
    await ctx.send(f"⏰ {ctx.author.mention} acordou! ☀️")

@bot.command()
async def dancar(ctx):
    await ctx.send(f"💃 {ctx.author.mention} está dançando! 🕺✨")

@bot.command()
async def cantar(ctx):
    await ctx.send(f"🎤 {ctx.author.mention} cantando! 🎶✨")

@bot.command()
async def chorar(ctx):
    await ctx.send(f"😭 {ctx.author.mention} chorando! 💔🤗")

@bot.command()
async def rir(ctx):
    await ctx.send(f"😂 {ctx.author.mention} rindo muito! 🤣")

@bot.command()
async def raiva(ctx):
    await ctx.send(f"😡 {ctx.author.mention} com raiva! 💢")

@bot.command()
async def vergonha(ctx):
    await ctx.send(f"😳 {ctx.author.mention} com vergonha! 🫣")

@bot.command()
async def feliz(ctx):
    await ctx.send(f"😊 {ctx.author.mention} feliz! 💖")

@bot.command()
async def triste(ctx):
    await ctx.send(f"😢 {ctx.author.mention} triste! 💔")

@bot.command()
async def roleta(ctx):
    await ctx.send(f"🔫 {ctx.author.mention} roleta: {random.choice(['Sobreviveu 😅','Morreu 💀'])}")

@bot.command()
async def pp(ctx, membro: discord.Member = None):
    alvo = membro or ctx.author
    await ctx.send(f"🍆 {alvo.mention} tem {random.randint(0,20)}cm! 😂")

# ============ 3 COMANDOS NOVOS - ENZO'S BOT ============
@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban_cmd(ctx, membro: discord.Member = None, *, motivo="Sem motivo"):
    if not membro:
        await ctx.send(f"{ctx.author.mention} ❌ Use: `!ban @usuario motivo`")
        return
    if membro.id == ctx.author.id:
        await ctx.send("❌ Você não pode se banir!")
        return
    try:
        await membro.ban(reason=f"{motivo} | Por: {ctx.author}")
        await ctx.send(f"🔨 {membro.mention} foi **banido permanentemente**! Motivo: {motivo}")
    except Exception as e:
        await ctx.send(f"❌ Erro ao banir: {e}")

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick_cmd(ctx, membro: discord.Member = None, *, motivo="Sem motivo"):
    if not membro:
        await ctx.send(f"{ctx.author.mention} ❌ Use: `!kick @usuario motivo`")
        return
    try:
        await membro.kick(reason=f"{motivo} | Por: {ctx.author}")
        await ctx.send(f"👢 {membro.mention} foi **expulso (kick)**! Ele pode voltar com convite. Motivo: {motivo}")
    except Exception as e:
        await ctx.send(f"❌ Erro ao expulsar: {e}")

@bot.command(name="castigo")
@commands.has_permissions(moderate_members=True)
async def castigo_cmd(ctx, membro: discord.Member = None, tempo: int = 10, *, motivo="Sem motivo"):
    """!castigo @user tempo(min) motivo - Deixa a pessoa de castigo (timeout clássico do Discord)"""
    if not membro:
        await ctx.send(f"{ctx.author.mention} ❌ Use: `!castigo @usuario tempo motivo`\nEx: `!castigo @enzo 10 flood`")
        return
    try:
        duracao = timedelta(minutes=tempo)
        await membro.timeout(duracao, reason=f"{motivo} | Por: {ctx.author}")
        await ctx.send(f"🔇 {membro.mention} está **de castigo por {tempo} minutos!** ⏰\nMotivo: {motivo}\n\n*Você está de castigo!*")
    except Exception as e:
        await ctx.send(f"❌ Erro ao dar castigo: {e}\nDica: O bot precisa ter cargo acima do membro e permissão 'Moderar Membros'")

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
    embed = discord.Embed(title="💎 COMANDOS DO ENZO'S BOT", description="Bot ENZO'S BOT - 50 comandos + moderação!", color=0x2b2d31)
    embed.add_field(name="📢!divulgar", value="Valida divulgação", inline=False)
    embed.add_field(name="🏆!convites /!perfil /!avaliar", value="Rank e perfil (agora mostra casamento 💍)", inline=False)
    embed.add_field(name="💎!vitrine /!ticket /!fechar /!confiavel", value="!ticket agora: VIP, Parcerias, Denúncias, Dúvidas, Suporte, Sugestões, Bug, Outros 🎫", inline=False)
    embed.add_field(name="💍!casar @user /!divorcio /!casal", value="Sistema de casamento que GRAVA no sistema! Só pode casar com 1 pessoa 💖", inline=False)
    embed.add_field(name="🔨 MODERAÇÃO NOVA", value="`!ban @user motivo` - Bane permanente\n`!kick @user motivo` - Expulsa mas pode voltar\n`!castigo @user tempo motivo` - Mute clássico 'Você está de castigo' ⏰\nEx: `!castigo @user 10 flood`", inline=False)
    embed.add_field(name="😍 Interação - 50 NOVOS", value="`!beijar` `!abracar` `!abraco` `!beijo` `!socar` `!tapa` `!cafune` `!morder` `!lamber` `!cheirar` `!chutar` `!matar` `!roubar` `!carinho` `!sapeca` `!cutucar` `!dormir` `!acordar` `!dancar` `!cantar` `!chorar` `!rir` `!raiva` `!vergonha` `!feliz` `!triste`", inline=False)
    embed.add_field(name="💘 Ship / Amor", value="`!ship @1 @2` `!amor @user` `!elogiar` `!xingar` `!fofo` `!feio` `!gay`", inline=False)
    embed.add_field(name="🎲 Diversão", value="`!sorte` `!8ball` `!dado` `!moeda` `!piada` `!cantada` `!sorteio` `!ppt` `!roleta` `!pp` `!curiosidade` `!fato` `!conselho` `!frase`", inline=False)
    embed.add_field(name="🔧 Util", value="`!id` `!avatar` `!say` `!ajuda`", inline=False)
    embed.add_field(name="🎲 RPG", value="`vamos fazer um rpg`", inline=False)
    embed.set_footer(text="ENZO'S BOT 💖 | 50+ comandos")
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"BOT ONLINE 24H COMO {bot.user} - ENZO'S BOT")

keep_alive()
bot.run(TOKEN)