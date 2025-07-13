from discord import Interaction
from discord.ext import commands
from discord import app_commands

from mcrcon import MCRcon
from loadEnv import get_mcrcon_pass


DEFAULT_GAMERULES = {
    "keepInventory": 'true',
    "mobGriefing": 'false',
    "doInsomnia": 'false',
    "snowAccumulationHeight": '4',
}


class McrconCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.host = "127.0.0.1"       # mc server's IP
        self.port = 25575             # RCON port

    @app_commands.command(name="ping", description="Check bot latency.")
    async def ping(self, interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="set", description="Set server ip and port")
    async def set_hostport(
        self, interaction: Interaction,
        host: str, port: str,
    ):
        print(host, port)
        self.host = host
        self.port = port

        await interaction.response.send_message(
            f"Set mcrcon adress to {self.host}:{self.port}",
            ephemeral=True
        )

    @app_commands.command(name="rcon", description="Send command to mc server")
    async def rcon(self, interaction: Interaction, cmd: str):
        password = get_mcrcon_pass()

        with MCRcon(self.host, password, port=self.port) as mcr:
            mcr.command(
                f"/say {interaction.user.name}({interaction.user.id})" +
                # f"@{interaction.channel.name}:" +
                f" {cmd}"
            )
            response = mcr.command(f"/{cmd}")
        if len(response) < 1700:
            await interaction.response.send_message(
                f"Server response: {response}"
            )
            return

        await interaction.response.send_message(
            "Response too long, sending DM."
        )
        await interaction.user.send(
            f"Original command: /{cmd}"
        )

        split = response.split('\n')
        part = "Server response: \n"
        curr_len = 0
        for s in split:
            s_len = len(s)
            if curr_len + s_len > 1800:
                await interaction.user.send(
                    f"{part}"
                )
                part = ""
                curr_len = 0
            part = part + s + '\n'
            curr_len += s_len
        if part:
            await interaction.user.send(
                f"{part}"
            )

    @app_commands.command(
        name="set_gamerules",
        description="Set default gamerules"
    )
    async def default_gamerules(self, interaction: Interaction):
        password = get_mcrcon_pass()

        with MCRcon(self.host, password, port=self.port) as mcr:
            responses: list = []
            for key, value in DEFAULT_GAMERULES.items():
                result = mcr.command(f"/gamerule {key} {value}")
                responses.append(result)
        await interaction.response.send_message(
            f"Server responses: \n- {'- '.join(responses)}"
        )


async def setup(bot):
    await bot.add_cog(McrconCog(bot))
