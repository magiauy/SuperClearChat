"""
Help command for the bot - Both prefix and slash commands
"""
import discord
from discord.ext import commands
from discord import app_commands
from utils.config import config
from utils.logger import logger

class HelpCommands(commands.Cog):
    """Help commands cog"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='help', aliases=['h'], help='Hiển thị hướng dẫn sử dụng bot')
    async def help_command(self, ctx):
        """
        Display help information
        """
        embed = discord.Embed(
            title="🤖 SuperClearChat Bot - Hướng Dẫn",
            description="Bot chuyên dụng để xóa tin nhắn của user theo thời gian\n"
                       "**Hỗ trợ cả Prefix Commands và Slash Commands!**",
            color=discord.Color.blue()
        )
        
        # Main commands
        embed.add_field(
            name=f"📝 **Prefix Command: {config.BOT_PREFIX}clear**",
            value=f"```{config.BOT_PREFIX}clear @user/user_id days [current|all]```\n"
                  f"**Ví dụ:**\n"
                  f"• `{config.BOT_PREFIX}clear @JohnDoe 7` - Xóa trong kênh hiện tại\n"
                  f"• `{config.BOT_PREFIX}clear @JohnDoe 7 all` - Xóa trong tất cả kênh",
            inline=False
        )
        
        embed.add_field(
            name="⚡ **Slash Command: /clear**",
            value="```/clear user:@JohnDoe days:7 scope:current```\n"
                  f"**Ưu điểm:**\n"
                  f"• Giao diện đẹp với dropdown menu\n"
                  f"• Autocomplete và validation\n"
                  f"• Không cần nhớ syntax",
            inline=False
        )
        
        # Parameters
        embed.add_field(
            name="⚙️ **Tham Số**",
            value=f"• **@user/user_id**: Mention (@user) hoặc ID của user cần xóa tin nhắn\n"
                  f"• **days**: Số ngày (từ {config.MIN_DAYS_LIMIT} đến {config.MAX_DAYS_LIMIT})\n"
                  f"• **scope**: `current` (kênh hiện tại) hoặc `all` (tất cả kênh) - mặc định là `current`",
            inline=False
        )
        
        # Requirements
        embed.add_field(
            name="🔐 **Yêu Cầu Quyền**",
            value="• **Server Owner** - Chỉ chủ server mới được sử dụng lệnh clear\n"
                  "• Bot cần quyền **Read Message History** và **Manage Messages**",
            inline=False
        )
        
        # Additional info
        embed.add_field(
            name="ℹ️ **Lưu Ý**",
            value="• **current**: Xóa tin nhắn chỉ trong kênh hiện tại (text/voice channel)\n"
                  "• **all**: Xóa tin nhắn trong TẤT CẢ kênh của server (text + voice)\n"
                  "• Tin nhắn cũ hơn 14 ngày sẽ được xóa từng cái một (chậm hơn)\n"
                  "• Bot không thể xóa tin nhắn của chính nó thông qua lệnh này\n"
                  "• Scope `all` có thể mất nhiều thời gian hơn",
            inline=False
        )
        
        # Footer
        embed.set_footer(
            text=f"Prefix: {config.BOT_PREFIX} | SuperClearChat v1.0",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        await ctx.send(embed=embed)
        logger.info(f"Help command được sử dụng bởi {ctx.author.name} trong {ctx.guild.name}")
    
    @app_commands.command(name="help", description="Hiển thị hướng dẫn sử dụng bot SuperClearChat")
    async def slash_help(self, interaction: discord.Interaction):
        """Slash command version of help"""
        embed = discord.Embed(
            title="🤖 SuperClearChat Bot - Hướng Dẫn",
            description="Bot chuyên dụng để xóa tin nhắn của user theo thời gian\n"
                       "**Hỗ trợ cả Prefix Commands và Slash Commands!**",
            color=discord.Color.blue()
        )
        
        # Main commands
        embed.add_field(
            name=f"📝 **Prefix Command: {config.BOT_PREFIX}clear**",
            value=f"```{config.BOT_PREFIX}clear @user/user_id days [current|all]```\n"
                  f"**Ví dụ:**\n"
                  f"• `{config.BOT_PREFIX}clear @JohnDoe 7` - Xóa trong kênh hiện tại\n"
                  f"• `{config.BOT_PREFIX}clear @JohnDoe 7 all` - Xóa trong tất cả kênh",
            inline=False
        )
        
        embed.add_field(
            name="⚡ **Slash Command: /clear**",
            value="```/clear user:@JohnDoe days:7 scope:current```\n"
                  f"**Ưu điểm:**\n"
                  f"• Giao diện đẹp với dropdown menu\n"
                  f"• Autocomplete và validation\n"
                  f"• Không cần nhớ syntax",
            inline=False
        )
        
        # Parameters
        embed.add_field(
            name="⚙️ **Tham Số**",
            value=f"• **@user/user_id**: Mention (@user) hoặc ID của user cần xóa tin nhắn\n"
                  f"• **days**: Số ngày (từ {config.MIN_DAYS_LIMIT} đến {config.MAX_DAYS_LIMIT})\n"
                  f"• **scope**: `current` (kênh hiện tại) hoặc `all` (tất cả kênh) - mặc định là `current`",
            inline=False
        )
        
        # Requirements
        embed.add_field(
            name="🔐 **Yêu Cầu Quyền**",
            value="• **Server Owner** - Chỉ chủ server mới được sử dụng lệnh clear\n"
                  "• Bot cần quyền **Read Message History** và **Manage Messages**",
            inline=False
        )
        
        # Additional info
        embed.add_field(
            name="ℹ️ **Lưu Ý**",
            value="• **current**: Xóa tin nhắn chỉ trong kênh hiện tại (text/voice channel)\n"
                  "• **all**: Xóa tin nhắn trong TẤT CẢ kênh của server (text + voice)\n"
                  "• Tin nhắn cũ hơn 14 ngày sẽ được xóa từng cái một (chậm hơn)\n"
                  "• Bot không thể xóa tin nhắn của chính nó thông qua lệnh này\n"
                  "• Scope `all` có thể mất nhiều thời gian hơn",
            inline=False
        )
        
        # Footer
        embed.set_footer(
            text=f"Prefix: {config.BOT_PREFIX} | SuperClearChat v1.0",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Slash help command được sử dụng bởi {interaction.user.name} trong {interaction.guild.name}")

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(HelpCommands(bot))
