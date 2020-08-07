import asyncio

import discord

import utils


class RealmSelect:
    letters = ["🇦", "🇧", "🇨", "🇨", "🇾", "🇿"]

    def __init__(self, client, ctx):
        self.client = client
        self.ctx = ctx


    async def start(self):
        servers = await utils.get_good_realms(self.client)
        server_opts = {}
        if servers:
            desc = ""
            num = 0

            for s in servers[0]:
                desc += f"{self.letters[num]} - {s} | Population: **{servers[0][s]['Population']}** | Events: **{servers[0][s]['Events']}**\n"
                server_opts[self.letters[num]] = s
                num += 1
            embed = discord.Embed(title="Location Selection", description="Choose a realm or press 🔄 to manually enter a location.", color=discord.Color.gold())
            embed.add_field(name="Top US Servers", value=desc, inline=False)
            num = 3
            for s in servers[1]:
                desc += f"{self.letters[num]} - {s} | Population: **{servers[1][s]['Population']}** | Events: **{servers[1][s]['Events']}**\n"
                server_opts[self.letters[num]] = s
                num += 1
            embed.add_field(name="Top EU Servers", value=desc, inline=False)
            msg = await self.ctx.send(embed=embed)
            for r in server_opts:
                await msg.add_reaction(r)
            await msg.add_reaction("🔄")

            def check(react, usr):
                return usr == self.ctx.author and react.message.id == msg.id and (str(react.emoji) in server_opts.keys() or str(react.emoji) == "🔄")

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=120, check=check)
            except asyncio.TimeoutError:
                try:
                    embed = discord.Embed(title="Timed out!", description="You didn't choose a realm in time!", color=discord.Color.red())
                    await msg.clear_reactions()
                    await msg.edit(embed=embed)
                    return None
                except discord.NotFound:
                    await self.ctx.send("Timed out while selecting channel.")
                    return None
            else:
                if str(reaction.emoji) == '🔄':
                    await msg.delete()
                    return await self.manual_location()
                else:
                    return server_opts[str(reaction.emoji)]

        else:
            return await self.manual_location(not_found=True)

    async def manual_location(self, not_found=False):
        desc = "No suitable locations were found automatically.\n" if not_found else ""
        desc += "Please enter the location for this run."
        embed = discord.Embed(title="Manual Location Selection", description=desc, color=discord.Color.gold())
        msg = await self.ctx.send(embed=embed)

        def check(m):
            return m.author == self.ctx.author and m.channel == self.ctx.channel

        # Wait for author to select a location
        while True:
            try:
                msg = await self.client.wait_for('message', timeout=600, check=check)
            except asyncio.TimeoutError:
                embed = discord.Embed(title="Timed out!", description="You didn't choose a location in time!", color=discord.Color.red())
                await msg.clear_reactions()
                await msg.edit(embed=embed)
                return None

            if not ('us' in str(msg.content).lower() or 'eu' in str(msg.content).lower()):
                await self.ctx.send("Please choose a US or EU location!", delete_after=7)
                continue
            else:
                return str(msg.content)