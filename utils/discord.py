import random
import string

import discord

from config.settings import BOT_ACCOUNT_NUMBER


async def send_embed(*, ctx, title, description):
    """
    send a simple embed with a title and description
    """

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Colour.red()
    )

    await ctx.send(embed=embed)


def generate_verification_code():
    """
    Generate a random verification code
    """
    chars = string.ascii_uppercase + string.digits

    return ''.join(random.choice(chars) for c in range(8))


async def send_verification_message(*, ctx, verification_account_number, verification_code):
    """
    Send a complete verification message privately to the user who created or
    updated an account number
    """

    embed = discord.Embed(
        title='Account Registration',
        description='To complete registration please send the following transaction.',
        color= discord.Colour.purple()
    )

    embed.add_field(
        name='From',
        value=verification_account_number,
        inline=False
    )

    embed.add_field(
        name='To',
        value=BOT_ACCOUNT_NUMBER,
        inline=False
    )

    embed.add_field(
        name='Memo',
        value=verification_code,
        inline=False
    )

    embed.add_field(
        name='Amount',
        value='0.00002',
        inline=False
    )

    await ctx.author.send(embed=embed)
