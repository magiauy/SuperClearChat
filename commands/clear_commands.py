"""
Discord bot commands - Both prefix and slash commands
Modified to support clearing messages of users who left the server
"""
import discord
from discord.ext import commands
from discord import app_commands
from utils.logger import logger
from utils.config import config
from utils.helpers import parse_user_mention, validate_days, get_user_from_guild, format_user_display
from core.message_cleaner import clear_user_messages, clear_user_messages_all_channels

class ClearCommands(commands.Cog):
    """Commands cog for message clearing functionality"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # Helper nội bộ để xử lý việc tìm user hoặc lấy ID
    async def _resolve_user(self, guild, user_id_or_mention):
        user_id = parse_user_mention(user_id_or_mention)
        if not user_id:
            return None, "invalid_id"

        # 1. Thử tìm trong Server (Member)
        member = guild.get_member(user_id)
        if member:
            return member, None
        
        # 2. Nếu không có trong server, thử tìm global (User)
        try:
            user = await self.bot.fetch_user(user_id)
            return user, None
        except discord.NotFound:
            # 3. Nếu không tìm thấy info (ví dụ user xóa acc), dùng luôn ID (Int)
            return int(user_id), None
        except discord.HTTPException:
            return int(user_id), None

    # Helper để hiển thị tên đẹp (xử lý cả trường hợp là int)
    def _get_display_name(self, user_obj):
        if isinstance(user_obj, int):
            return f"User ID: {user_obj} (Đã rời server)"
        return format_user_display(user_obj)

    @commands.command(name='clear', help='Xóa tin nhắn của user trong số ngày được chỉ định')
    @commands.check(lambda ctx: ctx.author == ctx.guild.owner)
    async def clear_messages(self, ctx, user_mention: str = None, days: str = None, scope: str = "current"):
        """
        Usage: {prefix}clear @user/user_id days [current|all]
        """
        # Validate parameters
        if not user_mention or not days:
            embed = discord.Embed(
                title="❌ Lỗi Cú Pháp",
                description=f"**Cách sử dụng:** `{config.BOT_PREFIX}clear @user/user_id days [current|all]`\n"
                           f"**Ví dụ:** `{config.BOT_PREFIX}clear 123456789 7 all`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Validate scope
        scope = scope.lower()
        if scope not in ['current', 'all']:
            await ctx.send("❌ Scope phải là `current` hoặc `all`.")
            return
        
        # Validate days
        days_int = validate_days(days, config.MIN_DAYS_LIMIT, config.MAX_DAYS_LIMIT)
        if not days_int:
            await ctx.send(f"❌ Số ngày phải từ {config.MIN_DAYS_LIMIT} đến {config.MAX_DAYS_LIMIT}.")
            return
        
        # --- XỬ LÝ QUAN TRỌNG: Lấy User hoặc ID ---
        target_user, error = await self._resolve_user(ctx.guild, user_mention)
        
        if not target_user:
            await ctx.send(f"❌ ID User không hợp lệ.")
            return

        # Check if trying to clear bot's own messages
        target_id = target_user if isinstance(target_user, int) else target_user.id
        if target_id == self.bot.user.id:
            await ctx.send("❌ Không thể xóa tin nhắn của chính bot.")
            return
        
        user_display = self._get_display_name(target_user)

        # Send confirmation message
        if scope == "all":
            embed = discord.Embed(
                title="🔄 Đang Xóa Tin Nhắn Trong Tất Cả Kênh...",
                description=f"Đang xóa tin nhắn của **{user_display}** trong **{days_int} ngày** qua...",
                color=discord.Color.blue()
            )
            embed.add_field(name="Phạm vi", value="Tất cả kênh trong server", inline=True)
        else:
            channel_type = "voice chat" if isinstance(ctx.channel, discord.VoiceChannel) else "text chat"
            embed = discord.Embed(
                title="🔄 Đang Xóa Tin Nhắn...",
                description=f"Đang xóa tin nhắn của **{user_display}** trong **{days_int} ngày** qua...",
                color=discord.Color.blue()
            )
            embed.add_field(name="Kênh", value=f"#{ctx.channel.name} ({channel_type})", inline=True)
        
        embed.add_field(name="Yêu cầu bởi", value=format_user_display(ctx.author), inline=True)
        status_message = await ctx.send(embed=embed)
        
        # Perform the clearing operation
        if scope == "all":
            result = await clear_user_messages_all_channels(ctx.guild, target_user, days_int, ctx.author)
        else:
            result = await clear_user_messages(ctx.channel, target_user, days_int, ctx.author)
        
        # Update status message with results
        if result['success']:
            if scope == "all":
                embed = discord.Embed(
                    title="✅ Hoàn Thành",
                    description=f"Đã xóa tin nhắn của **{user_display}** trong tất cả kênh",
                    color=discord.Color.green()
                )
                embed.add_field(name="Tổng tin nhắn đã xóa", value=f"`{result['total_deleted']}`", inline=True)
                embed.add_field(name="Kênh xử lý", value=f"`{result['channels_processed']}`", inline=True)
                
                # Show details
                if result['channels_with_messages']:
                    channels_info = "\n".join([
                        f"• **{ch['name']}** ({ch['type']}): {ch['deleted']} tin nhắn"
                        for ch in result['channels_with_messages'][:10] # Tăng giới hạn hiển thị lên 10
                    ])
                    if len(result['channels_with_messages']) > 10:
                        channels_info += f"\n• ... và {len(result['channels_with_messages']) - 10} kênh khác"
                    embed.add_field(name="Chi tiết", value=channels_info, inline=False)
            else:
                embed = discord.Embed(
                    title="✅ Hoàn Thành",
                    description=f"Đã xóa tin nhắn của **{user_display}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="Tin nhắn đã xóa", value=f"`{result['deleted_count']}`", inline=True)
                embed.add_field(name="Kênh", value=f"#{ctx.channel.name}", inline=True)
        else:
            embed = discord.Embed(
                title="❌ Lỗi",
                description=f"Lỗi: {result.get('error', 'Unknown')}",
                color=discord.Color.red()
            )
        
        await status_message.edit(embed=embed)
    
    @clear_messages.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ Chỉ có **Server Owner** mới được sử dụng lệnh này.")
        else:
            logger.error(f"Lỗi lệnh clear: {error}")
            await ctx.send(f"❌ Lỗi hệ thống: {error}")

    # Slash Commands
    @app_commands.command(name="clear", description="Xóa tin nhắn của user (kể cả đã out server)")
    @app_commands.describe(
        user="User cần xóa (Tag hoặc dán ID)",
        days="Số ngày (1-14)",
        scope="Phạm vi: current hoặc all"
    )
    @app_commands.choices(scope=[
        app_commands.Choice(name="Kênh hiện tại", value="current"),
        app_commands.Choice(name="Tất cả kênh", value="all")
    ])
    async def slash_clear(self, interaction: discord.Interaction, user: str, days: int, scope: str = "current"):
        # Check permissions
        if interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ Chỉ Server Owner mới dùng được lệnh này.", ephemeral=True)
            return
        
        # Validate days
        if not validate_days(str(days), config.MIN_DAYS_LIMIT, config.MAX_DAYS_LIMIT):
            await interaction.response.send_message(f"❌ Số ngày phải từ {config.MIN_DAYS_LIMIT} đến {config.MAX_DAYS_LIMIT}.", ephemeral=True)
            return
        
        # Defer response (vì xử lý tìm user có thể tốn thời gian mạng)
        await interaction.response.defer()

        # Resolve User/ID
        target_user, error = await self._resolve_user(interaction.guild, user)
        
        if not target_user:
            await interaction.followup.send(f"❌ ID User không hợp lệ.")
            return
        
        target_id = target_user if isinstance(target_user, int) else target_user.id
        if target_id == self.bot.user.id:
            await interaction.followup.send("❌ Không thể xóa tin nhắn của bot.")
            return

        user_display = self._get_display_name(target_user)
        
        # Logic y hệt prefix command (có thể tách ra hàm chung để gọn code hơn, nhưng để thế này cho dễ hiểu)
        if scope == "all":
            result = await clear_user_messages_all_channels(interaction.guild, target_user, days, interaction.user)
        else:
            result = await clear_user_messages(interaction.channel, target_user, days, interaction.user)
            
        if result['success']:
            msg = f"✅ **Hoàn tất xóa tin nhắn của {user_display}**\n"
            if scope == 'all':
                msg += f"• Tổng đã xóa: `{result['total_deleted']}`\n• Số kênh quét: `{result['channels_processed']}`"
            else:
                msg += f"• Đã xóa: `{result['deleted_count']}` tại kênh này."
            await interaction.followup.send(msg)
        else:
            await interaction.followup.send(f"❌ Lỗi: {result.get('error')}")

async def setup(bot):
    await bot.add_cog(ClearCommands(bot))