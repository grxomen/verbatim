import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio

class LockedEmojiPollView(View):
    def __init__(self, emoji_options, timeout=60):
        super().__init__(timeout=timeout)
        self.votes = {}  # user_id: emoji
        self.emoji_options = emoji_options
        for emoji in emoji_options:
            self.add_item(LockedPollButton(emoji, self))

    def get_results(self):
        results = {emoji: 0 for emoji in self.emoji_options}
        for emoji in self.votes.values():
            results[emoji] += 1
        return results


class LockedPollButton(Button):
    def __init__(self, emoji: str, view: LockedEmojiPollView):
        super().__init__(emoji=emoji, style=discord.ButtonStyle.primary)
        self.view = view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id in self.view.votes:
            return await interaction.response.send_message("❌ You've already voted!", ephemeral=True)

        self.view.votes[interaction.user.id] = self.emoji
        await interaction.response.send_message(f"✅ You voted for {self.emoji}", ephemeral=True)


@bot.command(name="emojipoll")
async def emojipoll(ctx, question: str, *emoji_options: str):
    """🔘 Create a locked emoji-button poll (vote-once only)."""
    if not (2 <= len(emoji_options) <= 5):
        return await ctx.send("Provide 2–5 emoji options.")

    embed = discord.Embed(
        title=f"🧠 {question}",
        description="Click a button below to cast your vote. You can only vote once.",
        color=0x5865F2
    )
    embed.set_footer(text="Poll will close in 60 seconds.")

    view = LockedEmojiPollView(emoji_options)
    await ctx.send(embed=embed, view=view)

    await asyncio.sleep(view.timeout)

    results = view.get_results()
    result_lines = [f"{emoji} — `{count} vote(s)`" for emoji, count in results.items()]
    await ctx.send(f"📊 **Final Results for:** *{question}*\n" + "\n".join(result_lines))
