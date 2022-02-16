import discord
from discord.ext import commands


# The modal subclass
class SupportForm(discord.ui.Modal):
    def __init__(self):
        # Set the fields that the user will be asked to fill
        fields = [
            discord.TextInput(
                label='One-line Summary',
                placeholder='Enter a one liner description...'
            ),
            discord.TextInput(
                label='Description',
                placeholder='Enter a detailed description...',
                style=discord.TextInputStyle.paragraph, # the paragraph style takes multiline input from the user
                max_length=1024
            )
        ]
        super().__init__(title='Support Form', fields=fields)

    async def callback(self, interaction: discord.Interaction):
        # the callback function is called when the user submits the modal
        # all the field's "value" attribute would be set to what the user typed
        await interaction.response.send_message(
            'Our helpers have received the form, and are on the case!'
        )

        helper_channel = bot.get_channel(HELPER_CHANNEL_ID)
        embed = discord.Embed(title=f'Support Form Submitted by {interaction.user}')
        embed.add_field(name='Summary', value=self.fields[0].value, inline=False)
        embed.add_field(name='Description', value=self.fields[1].value, inline=False)
        await helper_channel.send(embed=embed)


class SupportView(discord.ui.View):
    @discord.ui.button(label='get support')
    async def get_support(self, button: discord.ui.Button, interaction: discord.Interaction):
        # prompt the modal to the user using the interaction object
        # this responds to the interaction
        await interaction.response.prompt(SupportForm())


class ModalBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('$'))

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = ModalBot()

@bot.command()
async def support(ctx: commands.Context):
    await ctx.send(
        'Need help? Click on the button and fill out the form, '
        + 'and we\'ll get back to you as soon as possible!',
        view=SupportView()
    )

bot.run(TOKEN)