import discord
from discord.ext import commands
import os
import json
from discord import app_commands
import asyncio
import time
import random
import string
from discord.ext import tasks

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='+', intents=intents, help_command=None)

def load_settings():
    with open("settings.json", "r") as f:
        return json.load(f)

def load_stock():
    with open("stock.json", "r") as f:
        return json.load(f)

def load_keys():
    if not os.path.exists("keys.json"):
        with open("keys.json", "w") as f:
            json.dump({}, f)
    with open("keys.json", "r") as f:
        return json.load(f)

def save_keys(keys):
    with open("keys.json", "w") as f:
        json.dump(keys, f, indent=4)

def load_cooldowns():
    if not os.path.exists("cooldowns.json"):
        with open("cooldowns.json", "w") as f:
            json.dump({}, f)
    with open("cooldowns.json", "r") as f:
        return json.load(f)

def save_cooldowns(cooldowns):
    with open("cooldowns.json", "w") as f:
        json.dump(cooldowns, f, indent=4)

def is_premium(user_id: str):
    config = load_settings()
    if not config["premium"]["sys_enabled"]:
        return False
    keys = load_keys()
    for key, data in keys.items():
        if data.get("user_id") == user_id:
            if data["expires_at"] == -1 or data["expires_at"] > time.time():
                return True
    return False

config = load_settings()
color = int(config["couleur"], 16)


class RedeemModal(discord.ui.Modal, title="🔑 Redeem Premium Key"):
    key_input = discord.ui.TextInput(label="Your Key", placeholder="XXXX-XXXX-XXXX-XXXX", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        config = load_settings()
        if not config["premium"]["sys_enabled"]:
            await interaction.response.send_message(embed=discord.Embed(
                title="`❌` - Premium Disabled",
                description="> *The premium system is currently disabled.*",
                color=0xff0000
            ), ephemeral=True)
            return

        keys = load_keys()
        key = self.key_input.value.strip()
        user_id = str(interaction.user.id)

        if key not in keys:
            await interaction.response.send_message(embed=discord.Embed(
                title="`🚫` - Invalid Key",
                description="> *This key does not exist.*",
                color=0xff0000
            ), ephemeral=True)
            return

        key_data = keys[key]

        if key_data.get("used"):
            await interaction.response.send_message(embed=discord.Embed(
                title="`🚫` - Key Already Used",
                description="> *This key has already been redeemed.*",
                color=0xff0000
            ), ephemeral=True)
            return

        duration = key_data["duration"]
        expires_at = -1 if duration == -1 else time.time() + duration

        keys[key]["used"] = True
        keys[key]["user_id"] = user_id
        keys[key]["expires_at"] = expires_at
        save_keys(keys)

        role_id = int(config["premium"]["role_id"])
        guild = interaction.guild
        role = guild.get_role(role_id)
        if role:
            await interaction.user.add_roles(role)

        duration_text = "Permanent" if duration == -1 else f"{duration // 86400} day(s)"
        await interaction.response.send_message(embed=discord.Embed(
            title="`⭐` - Premium Activated",
            description=f"> Valid key! Premium activated for **{duration_text}**.",
            color=int(config["couleur"], 16)
        ), ephemeral=True)


class RedeemButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔑 Redeem Key", style=discord.ButtonStyle.blurple, custom_id="redeem_button")
    async def redeem_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RedeemModal())


@bot.event
async def on_ready():
    bot.add_view(RedeemButton())
    await bot.tree.sync()
    check_expired_premium.start()
    print(f"""
╔══════════════════════════════════════╗
║         Account Gen - Online         ║
╠══════════════════════════════════════╣
║  Bot    : {bot.user}
║  Dev    : g1p9                       ║
║  Prefix : +                          ║
╚══════════════════════════════════════╝
    """)


@bot.command(name="stock")
async def stock_cmd(ctx):
    stock_data = load_stock()
    config = load_settings()
    color = int(config["couleur"], 16)

    embed = discord.Embed(title="`📦` - Stock", color=color)
    total = 0
    for categorie, items in stock_data.items():
        total += len(items)
        embed.add_field(name=" ", value=f"> {categorie.capitalize()}: **{len(items)}** available", inline=False)
    embed.set_footer(text=f"Total: {total} account(s)")
    await ctx.send(embed=embed)


async def gen_autocomplete(interaction: discord.Interaction, current: str):
    stock_data = load_stock()
    return [
        app_commands.Choice(name=categorie.capitalize(), value=categorie)
        for categorie in stock_data.keys()
        if current.lower() in categorie.lower() and len(stock_data[categorie]) > 0
    ]

@bot.tree.command(name="gen", description="Generate an account")
@app_commands.describe(type="The type of account to generate")
@app_commands.autocomplete(type=gen_autocomplete)
async def gen_slash(interaction: discord.Interaction, type: str):
    await handle_gen(interaction=interaction, type=type.lower())

@bot.command(name="gen")
async def gen_prefix(ctx, type: str):
    await handle_gen(ctx=ctx, type=type.lower())

async def handle_gen(type: str, ctx=None, interaction=None):
    stock_data = load_stock()
    config = load_settings()
    color = int(config["couleur"], 16)
    user = interaction.user if interaction else ctx.author
    user_id = str(user.id)

    cooldowns = load_cooldowns()
    premium_enabled = config["premium"]["sys_enabled"]
    user_is_premium = premium_enabled and is_premium(user_id)
    cooldown_time = int(config["premium"]["cooldown"]) if user_is_premium else int(config["cooldown"])
    last_gen = cooldowns.get(user_id, 0)
    remaining = cooldown_time - (time.time() - last_gen)

    if remaining > 0:
        embed_cd = discord.Embed(
            title="`⏳` - Cooldown",
            description=f"> *Available* <t:{int(time.time() + remaining)}:R>",
            color=0xff0000
        )
        if interaction:
            await interaction.response.send_message(embed=embed_cd, ephemeral=True)
        else:
            msg = await ctx.reply(embed=embed_cd)
            await asyncio.sleep(10)
            await msg.delete()
            await ctx.message.delete()
        return

    if type not in stock_data or len(stock_data[type]) == 0:
        embed_no = discord.Embed(
            title="`🚫` - No Account Available",
            description="> *Please try again later.*",
            color=0xff0000
        )
        if interaction:
            await interaction.response.send_message(embed=embed_no, ephemeral=True)
        else:
            msg = await ctx.reply(embed=embed_no)
            await asyncio.sleep(10)
            await msg.delete()
            await ctx.message.delete()
        return

    compte = stock_data[type].pop(0)
    with open("stock.json", "w") as f:
        json.dump(stock_data, f, indent=4)

    cooldowns[user_id] = time.time()
    save_cooldowns(cooldowns)

    id_acc, mdp = compte.split(":")

    embed_dm = discord.Embed(title="`🪄` - Account Generated", color=color)
    embed_dm.add_field(name="Full Combo", value=f"```{compte}```", inline=False)
    embed_dm.add_field(name="Username", value=f"```{id_acc}```", inline=True)
    embed_dm.add_field(name="Password", value=f"```{mdp}```", inline=True)

    try:
        await user.send(embed=embed_dm)
        dm_ok = True
    except discord.Forbidden:
        dm_ok = False

    embed = discord.Embed(
        title="`🪄` - Account Generated",
        description="> *Please check your DMs.*" if dm_ok else "> *Unable to send DM, please open your DMs.*",
        color=color
    )
    if interaction:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        msg = await ctx.reply(embed=embed)
        await asyncio.sleep(10)
        await msg.delete()
        await ctx.message.delete()


@bot.command(name="createkey")
async def createkey(ctx, duration: int):
    config = load_settings()
    if str(ctx.author.id) != str(config["owner_id"]):
        return

    key = "-".join("".join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(4))
    keys = load_keys()
    keys[key] = {
        "duration": duration * 86400 if duration != -1 else -1,
        "used": False,
        "user_id": None,
        "expires_at": None
    }
    save_keys(keys)

    await ctx.reply(embed=discord.Embed(
        title="`✅` - Key Created",
        description=f"```{key}```\nDuration: **{'Permanent' if duration == -1 else f'{duration} day(s)'}**",
        color=color
    ))
    await ctx.message.delete()


@tasks.loop(minutes=2)
async def check_expired_premium():
    config = load_settings()
    keys = load_keys()
    role_id = int(config["premium"]["role_id"])

    for guild in bot.guilds:
        role = guild.get_role(role_id)
        if not role:
            continue
        for key, data in keys.items():
            if not data.get("used") or data["expires_at"] == -1:
                continue
            if data["expires_at"] < time.time():
                user_id = data.get("user_id")
                if not user_id:
                    continue
                member = guild.get_member(int(user_id))
                if member and role in member.roles:
                    await member.remove_roles(role)


@bot.command(name="send_redeem")
async def send_redeem(ctx):
    config = load_settings()
    if str(ctx.author.id) != str(config["owner_id"]):
        return

    embed = discord.Embed(
        title="`⭐` - Premium Access",
        description="> *Click the button below to activate your premium key.*",
        color=color
    )
    await ctx.send(embed=embed, view=RedeemButton())
    await ctx.message.delete()


bot.run(config["token"])