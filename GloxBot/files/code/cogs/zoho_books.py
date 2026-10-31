import os
import logging
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands

logger = logging.getLogger("GloxBot.ZohoBooks")

class ZohoBooksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = "https://www.zohoapis.com/books/v3"
        self.auth_url = "https://accounts.zoho.com/oauth/v2/token"

    async def get_access_token(self) -> str:
        """Exchanges a refresh token for a fresh access token from Zoho Accounts."""
        client_id = os.getenv("ZOHO_CLIENT_ID")
        client_secret = os.getenv("ZOHO_CLIENT_SECRET")
        refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")

        if not all([client_id, client_secret, refresh_token]):
            raise ValueError("Missing Zoho OAuth credentials in environment variables.")

        payload = {
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.auth_url, data=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("access_token")
                else:
                    text = await resp.text()
                    logger.error(f"❌ Failed to refresh Zoho Access Token: {text}")
                    raise Exception("Zoho Token Refresh Failed")

    zoho_group = app_commands.Group(name="zoho", description="Manage and query Zoho Books financial operations")

    @zoho_group.command(name="invoices", description="List recent invoices from Zoho Books")
    @app_commands.describe(status="Filter by status (e.g., unpaid, sent, overdue)")
    @app_commands.checks.has_any_role("core-ops", "Admin", "Founder")
    async def zoho_invoices(self, interaction: discord.Interaction, status: str = "unpaid"):
        await interaction.response.defer(thinking=True, ephemeral=True)

        org_id = os.getenv("ZOHO_ORGANIZATION_ID")
        if not org_id:
            await interaction.followup.send("❌ Error: `ZOHO_ORGANIZATION_ID` is not configured.", ephemeral=True)
            return

        try:
            access_token = await self.get_access_token()
        except Exception as e:
            await interaction.followup.send(f"❌ Authentication Error: {e}", ephemeral=True)
            return

        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}"
        }
        params = {
            "organization_id": org_id,
            "status": status
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/invoices", headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    invoices = data.get("invoices", [])[:5]  # Top 5 invoices

                    embed = discord.Embed(
                        title=f"🧾 Zoho Books Invoices ({status.capitalize()})",
                        color=discord.Color.from_rgb(74, 107, 108)  # Copper Oxidation (#4a6b6c)
                    )

                    if invoices:
                        for inv in invoices:
                            customer = inv.get("customer_name", "Unknown Client")
                            number = inv.get("invoice_number", "INV-XXXX")
                            total = inv.get("total", 0.00)
                            inv_status = inv.get("status", "unknown").upper()
                            
                            embed.add_field(
                                name=f"{number} • {customer}",
                                value=f"**Amount:** ${total} | **Status:** {inv_status}",
                                inline=False
                            )
                    else:
                        embed.description = f"No invoices found matching status: `{status}`."

                    embed.set_footer(text="Zerg Temple PHX • Up To A Boil Financial Operations")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    err_text = await resp.text()
                    logger.error(f"Zoho API Error: {err_text}")
                    await interaction.followup.send("⚠️ Failed to retrieve invoice data from Zoho Books API.", ephemeral=True)

    @zoho_group.command(name="expenses", description="Log a new business expense directly into Zoho Books")
    @app_commands.describe(
        vendor="Name of the vendor",
        amount="Expense total in USD",
        account="Expense account (e.g., Software, Hardware, Logistics)"
    )
    @app_commands.checks.has_any_role("core-ops", "Admin", "Founder")
    async def zoho_log_expense(self, interaction: discord.Interaction, vendor: str, amount: float, account: str = "General Expense"):
        await interaction.response.defer(thinking=True, ephemeral=True)

        org_id = os.getenv("ZOHO_ORGANIZATION_ID")
        if not org_id:
            await interaction.followup.send("❌ Error: `ZOHO_ORGANIZATION_ID` is not configured.", ephemeral=True)
            return

        try:
            access_token = await self.get_access_token()
        except Exception as e:
            await interaction.followup.send(f"❌ Authentication Error: {e}", ephemeral=True)
            return

        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "vendor_name": vendor,
            "amount": amount,
            "date": discord.utils.utcnow().strftime("%Y-%m-%d"),
            "expense_account_name": account,
            "description": f"Logged via GloxBot Discord Ops by {interaction.user.name}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/expenses?organization_id={org_id}", headers=headers, json=payload) as resp:
                if resp.status in [200, 201]:
                    embed = discord.Embed(
                        title="✅ Expense Successfully Logged to Zoho Books",
                        color=discord.Color.from_rgb(82, 183, 136)  # Bioluminescent Emitter (#52b788)
                    )
                    embed.add_field(name="Vendor", value=vendor, inline=True)
                    embed.add_field(name="Amount", value=f"${amount:.2f}", inline=True)
                    embed.add_field(name="Account", value=account, inline=True)
                    embed.set_footer(text="Up To A Boil HR & Financial Services")
                    
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    err_text = await resp.text()
                    logger.error(f"Zoho Expense Log Error: {err_text}")
                    await interaction.followup.send(f"❌ Failed to record expense in Zoho Books: `{err_text}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ZohoBooksCog(bot))
