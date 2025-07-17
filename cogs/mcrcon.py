from discord import Interaction, Role, Member
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


allowed_roles = ["mcrcon"]


def _dynamic_role_check(interaction: Interaction) -> bool:
    # This function is called every time the command is run
    if not isinstance(interaction.user, Member):
        return False  # Not in a guild
    user_roles = [role.name for role in interaction.user.roles]
    result = any(role in allowed_roles for role in user_roles)
    print([role in allowed_roles for role in user_roles])
    print(f'user roles: {user_roles}\nallowed roles: {allowed_roles}')
    if not result:
        raise commands.MissingAnyRole(missing_roles=allowed_roles)
    return result


class McrconCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.host = "127.0.0.1"       # mc server's IP
        self.port = 25575             # RCON port

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(
        name="add_role",
        description="Allows a role to use mc console"
    )
    async def add_role(self, interaction: Interaction, role: Role):
        if role.name in allowed_roles:
            await interaction.response.send_message(
                f"Role {role.name} is already allowed.",
            )
            return
        allowed_roles.append(role.name)
        await interaction.response.send_message(
            f"Role {role.name} has been added to whitelist.",
        )

    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(
        name="remove_role",
        description="Disallows a role to use mc console"
    )
    async def del_role(self, interaction: Interaction, role: Role):
        if role.id not in allowed_roles:
            await interaction.response.send_message(
                f"Role {role.name} is already not allowed.",
            )
            return
        allowed_roles.remove(role.id)
        await interaction.response.send_message(
            f"Role {role.name} has been removed from whitelist.",
        )

    @app_commands.check(_dynamic_role_check)
    @app_commands.command(
        name="set_address",
        description="Set server ip and port"
    )
    async def set_hostport(
        self, interaction: Interaction,
        host: str, port: str,
    ):
        if not app_commands.checks.has_any_role(*allowed_roles):
            raise commands.CheckFailure
        self.host = host
        self.port = port

        await interaction.response.send_message(
            f"Set mcrcon adress to {self.host}:{self.port}",
            ephemeral=True
        )

    @app_commands.check(_dynamic_role_check)
    @app_commands.command(name="rcon", description="Send command to mc server")
    async def rcon(self, interaction: Interaction, cmd: str):
        password = get_mcrcon_pass()

        try:
            with MCRcon(self.host, password, port=self.port) as mcr:
                mcr.command(
                    f"/say {interaction.user.name}({interaction.user.id})" +
                    # f"@{interaction.channel.name}:" +
                    f" {cmd}"
                )
                response = mcr.command(f"/{cmd}")
        except ConnectionRefusedError as e:
            await interaction.response.send_message(
                f"Server did not respond [{e}]"
            )
            return

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

    @app_commands.check(_dynamic_role_check)
    @app_commands.command(
        name="set_gamerules",
        description="Set default gamerules"
    )
    async def default_gamerules(self, interaction: Interaction):
        password = get_mcrcon_pass()

        try:
            with MCRcon(self.host, password, port=self.port) as mcr:
                responses: list = []
                for key, value in DEFAULT_GAMERULES.items():
                    result = mcr.command(f"/gamerule {key} {value}")
                    responses.append(result)
        except ConnectionRefusedError as e:
            await interaction.response.send_message(
                f"Server did not respond [{e}]"
            )
            return

        await interaction.response.send_message(
            f"Server responses: \n- {'- '.join(responses)}"
        )

    @add_role.error
    @del_role.error
    async def _role_whitelist_error(self, interaction: Interaction, error):
        if not isinstance(error, commands.CheckFailure):
            await interaction.response.send_message(
                f"Unknown error - {error}",
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"These commands must be executed as Administrator ({error})",
            ephemeral=True
        )

    @set_hostport.error
    @rcon.error
    @default_gamerules.error
    async def _cmd_error(self, interaction: Interaction, error):
        if not allowed_roles:
            await interaction.response.send_message(
                "Set permisions for console interaction with /add_role."
            )
        else:
            await interaction.response.send_message(
                f"Missing at least one role from {allowed_roles}.",
                ephemeral=True
            )
        print(allowed_roles)
        print(interaction.user.roles)
        pass


async def setup(bot):
    await bot.add_cog(McrconCog(bot))
