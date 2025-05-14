# verbatim.py
import os
import asyncio
import discord
from discord.ext import commands, tasks

# ─── Bot Setup ─────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.members = True      # for userinfo, roleinfo, moderation
intents.guild_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
MOD_LOG_CHANNEL = 123456789012345678  # ← replace with your mod-log channel ID
VERIFIED_ROLE_ID = 111111111111111111
CROSS_VERIFIED_ROLE_ID = 222222222222222222

# ─── UTILITIES ────────────────────────────────────────────────────────────────

def mod_log():
    return bot.get_channel(MOD_LOG_CHANNEL)

async def log_action(action: str):
    ch = mod_log()
    if ch:
        await ch.send(action)

# ─── 1. ping ─────────────────────────────────────────────────────────────────

@bot.command()
async def ping(ctx):
    """🏓 Pong!"""
    ms = int(bot.latency * 1000)
    await ctx.send(f"Pong! Latency is {ms}ms.")

# ─── 2. serverinfo ────────────────────────────────────────────────────────────

@bot.command()
async def serverinfo(ctx):
    """🏰 Show basic server stats."""
    g = ctx.guild
    embed = discord.Embed(title=f"{g.name} — Server Info", color=0x2f3136)
    embed.add_field("Members", g.member_count)
    embed.add_field("Roles", len(g.roles))
    embed.add_field("Channels", len(g.channels))
    embed.add_field("Boost Level", g.premium_tier)
    embed.add_field("Region", getattr(g, "region", "unknown"))
    await ctx.send(embed=embed)

# ─── 3. userinfo ──────────────────────────────────────────────────────────────

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    """👤 Show user info."""
    member = member or ctx.author
    roles = ", ".join(r.name for r in member.roles if r.name != "@everyone")
    joined = member.joined_at.strftime("%Y-%m-%d")
    await ctx.send(f"User **{member}**:\n• Joined: {joined}\n• Roles: {roles}")

# ─── 4. roleinfo ──────────────────────────────────────────────────────────────

@bot.command()
async def roleinfo(ctx, role: discord.Role):
    """🎭 Show role info."""
    members = ", ".join(m.display_name for m in role.members) or "nobody"
    perms = [p[0] for p in role.permissions if p[1]]
    created = role.created_at.strftime("%Y-%m-%d")
    await ctx.send(f"Role **{role.name}**:\n• Created: {created}\n• Members: {members}\n• Perms: {', '.join(perms)}")

# ─── 5. verify ─────────────────────────────────────────────────────────────────

@bot.command()
async def verify(ctx):
    """🛡️ Start ID-verification flow."""
    await ctx.send("Check your DMs for a secure verification link…")
    # TODO: DM a KYC widget link, await webhook, grant role on pass
    # e.g., await ctx.author.add_roles(ctx.guild.get_role(VERIFIED_ROLE_ID))

# ─── 6. crossverify ────────────────────────────────────────────────────────────

@bot.command()
async def crossverify(ctx):
    """🔗 Cross-verify via partner server."""
    await ctx.send("Please upload a screenshot or enter partner-server user ID.")
    # TODO: Accept screenshot → OCR or call partner API → grant CROSS_VERIFIED_ROLE_ID

# ─── 7. ban ───────────────────────────────────────────────────────────────────

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = None):
    """🚫 Ban a user."""
    await member.ban(reason=reason)
    await ctx.send(f"Banned {member.mention}.")
    await log_action(f"🔨 {ctx.author} banned {member} | Reason: {reason}")

# ─── 8. kick ──────────────────────────────────────────────────────────────────

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = None):
    """👢 Kick a user."""
    await member.kick(reason=reason)
    await ctx.send(f"Kicked {member.mention}.")
    await log_action(f"👢 {ctx.author} kicked {member} | Reason: {reason}")

# ─── 9. mute & 10. unmute ─────────────────────────────────────────────────────

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: str = None, *, reason: str = None):
    """🤐 Mute (text only)."""
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f"Muted {member.mention}.")
    await log_action(f"🤐 {ctx.author} muted {member} | {duration or 'indefinite'} | {reason}")
    if duration:
        # crude duration parsing: '10m', '2h'
        unit = duration[-1]
        val = int(duration[:-1])
        secs = val * (60 if unit == 'm' else 3600)
        await asyncio.sleep(secs)
        await member.remove_roles(muted_role)
        await ctx.send(f"Auto-unmuted {member.mention} after {duration}.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    """🔊 Unmute."""
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(muted_role)
    await ctx.send(f"Unmuted {member.mention}.")
    await log_action(f"🔊 {ctx.author} unmuted {member}")

# ─── 11. timeout ───────────────────────────────────────────────────────────────

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, duration: str, *, reason: str = None):
    """⏱️ Timeout a member."""
    # discord.py v2.6+: member.timeout(dt, reason)
    unit = duration[-1]; val = int(duration[:-1])
    secs = val * (60 if unit == 'm' else 3600)
    until = discord.utils.utcnow() + discord.timedelta(seconds=secs)
    await member.timeout(until, reason=reason)
    await ctx.send(f"⏱️ Timed out {member.mention} for {duration}.")
    await log_action(f"⏱️ {ctx.author} timed out {member} for {duration} | {reason}")

# ─── 12. purge ─────────────────────────────────────────────────────────────────

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int, member: discord.Member = None):
    """🗑️ Bulk-delete messages."""
    def predicate(m):
        return m.author == member if member else True
    deleted = await ctx.channel.purge(limit=amount, check=predicate)
    await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)
    await log_action(f"🗑️ {ctx.author} purged {len(deleted)} msgs in {ctx.channel}")

# ─── 13. poll ──────────────────────────────────────────────────────────────────

@bot.command()
async def poll(ctx, question: str, *options: str):
    """📊 Reaction-free poll."""
    if len(options) < 2 or len(options) > 10:
        return await ctx.send("Need 2–10 options.")
    results = {opt: 0 for opt in options}
    msg = await ctx.send(f"**POLL:** {question}\n" + "\n".join(f"{i+1}. {opt}" for i,opt in enumerate(options)))
    await asyncio.sleep(60)  # auto-close in 1m; adjust as you like
    # TODO: Keep track of DMs or reactions if you want more robust counting
    await ctx.send("Poll closed! (tallying manually…)")
    # Manual tally stub:
    await ctx.send("\n".join(f"{opt}: {count} votes" for opt,count in results.items()))

# ─── 14. announce ──────────────────────────────────────────────────────────────

@bot.command()
@commands.has_permissions(mention_everyone=True)
async def announce(ctx, channel: discord.TextChannel, *, message: str):
    """📣 Styled announcement."""
    await channel.send(f"📢 **ANNOUNCEMENT:** {message}")
    await ctx.send(f"Sent announcement to {channel.mention}.")

# ─── 15. reactionrole ───────────────────────────────────────────────────────────

@bot.command()
@commands.has_permissions(manage_roles=True)
async def reactionrole(ctx, message_id: int, emoji: str, role: discord.Role):
    """🎟️ Set up a reaction-role."""
    msg = await ctx.channel.fetch_message(message_id)
    await msg.add_reaction(emoji)
    # TODO: save (message_id, emoji, role.id) in your DB
    await ctx.send(f"✅ When users react with {emoji}, I'll give them {role.name}.")

# ─── 16. addemoji ──────────────────────────────────────────────────────────────

@bot.command()
@commands.has_permissions(manage_emojis=True)
async def addemoji(ctx, name: str, url: str):
    """😃 Add a server emoji from URL."""
    async with ctx.session.get(url) as resp:
        img = await resp.read()
    emoji = await ctx.guild.create_custom_emoji(name=name, image=img)
    await ctx.send(f"Added emoji {emoji}")

# ─── 17. addsticker ────────────────────────────────────────────────────────────

@bot.command()
@commands.has_permissions(manage_emojis=True)
async def addsticker(ctx, name: str, url: str):
    """🏷️ Add a server sticker from URL."""
    async with ctx.session.get(url) as resp:
        img = await resp.read()
    sticker = await ctx.guild.create_sticker(name=name, description="", tags=[name], file=img)
    await ctx.send(f"Added sticker {sticker.name}")

# ─── 18. threadstart ───────────────────────────────────────────────────────────

@bot.command()
async def threadstart(ctx, mode: str, *, title: str):
    """🧵 Start a thread."""
    public = mode.lower() == "public"
    thread = await ctx.channel.create_thread(name=title, type=discord.ChannelType.public_thread if public else discord.ChannelType.private_thread)
    await ctx.send(f"Started {'public' if public else 'private'} thread: {thread.mention}")

# ─── 19. cleanuplogs ───────────────────────────────────────────────────────────

@bot.command()
@commands.has_permissions(manage_messages=True)
async def cleanuplogs(ctx, amount: int = 50):
    """📜 Cleanup old bot/mod-log posts."""
    def is_bot_or_mod(m): return m.author == bot.user or m.channel.id == MOD_LOG_CHANNEL
    deleted = await ctx.channel.purge(limit=amount, check=is_bot_or_mod)
    await ctx.send(f"Cleaned up {len(deleted)} log messages.", delete_after=5)

# ─── 20. reload (dev) ──────────────────────────────────────────────────────────

@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, module: str):
    """🔄 Reload a module on the fly."""
    try:
        bot.reload_extension(f"cogs.{module}")
        await ctx.send(f"🔄 Reloaded `{module}`")
    except Exception as e:
        await ctx.send(f"❌ Could not reload `{module}`: {e}")

# ─── RUN ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
