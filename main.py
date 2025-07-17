import discord
from discord.ext import commands
from loadEnv import get_discord_token

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)
DC_TOKEN = get_discord_token()


# This is for the example purposes only and should only be used for debugging
@bot.command(name="sync")
async def sync(ctx: commands.Context):
    # sync to the guild where the command was used
    bot.tree.copy_global_to(guild=ctx.guild)
    await bot.tree.sync(guild=ctx.guild)

    await ctx.send(content="Success")


@bot.tree.command(name="load", description="Loads a specific cog")
async def load_cog(interaction: discord.Interaction, extension: str):
    await bot.load_extension(f"cogs.{extension}")
    await interaction.response.send_message(f"Cog '{extension}' loaded.")


@bot.tree.command(name="hello", description="Says hello to user")
async def _hello(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Hello, {interaction.user.display_name}"
    )


@bot.event
async def on_ready():
    # Load cogs
    # await bot.load_extension("cogs.mcrcon")

    # Sync commands
    await bot.tree.sync()
    print(f'Bot is online as {bot.user}')
    print("Commands have been synced")


bot.run(DC_TOKEN)
