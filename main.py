"""
Main bot file - SuperClearChat Discord Bot
"""
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import logger, log_session_start, log_session_end
from utils.config import config

class SuperClearChatBot(commands.Bot):
    """Custom Bot class with additional functionality"""
    
    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        # Initialize bot
        super().__init__(
            command_prefix=config.BOT_PREFIX,
            intents=intents,
            help_command=None,  # We'll use our custom help command
            case_insensitive=True
        )
    
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        logger.info("Đang tải các module...")
        
        # Load command cogs
        try:
            await self.load_extension('commands.clear_commands')
            logger.info("✓ Đã tải module: clear_commands")
        except Exception as e:
            logger.error(f"✗ Lỗi tải clear_commands: {e}")
        
        try:
            await self.load_extension('commands.help_commands')
            logger.info("✓ Đã tải module: help_commands")
        except Exception as e:
            logger.error(f"✗ Lỗi tải help_commands: {e}")
        
        logger.info("Hoàn thành tải modules")
        
        # Sync slash commands
        try:
            logger.info("Đang sync slash commands...")
            synced = await self.tree.sync()
            logger.info(f"✓ Đã sync {len(synced)} slash command(s)")
        except Exception as e:
            logger.error(f"✗ Lỗi sync slash commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Bot đã sẵn sàng: {self.user.name} (ID: {self.user.id})")
        logger.info(f"Đang phục vụ {len(self.guilds)} server(s)")
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{config.BOT_PREFIX}help | /help | Xóa tin nhắn"
        )
        await self.change_presence(activity=activity)
        
        logger.info("Bot đã hoạt động hoàn toàn!")
    
    async def on_guild_join(self, guild):
        """Called when bot joins a guild"""
        logger.info(f"Đã tham gia server mới: {guild.name} (ID: {guild.id}, Members: {guild.member_count})")
    
    async def on_guild_remove(self, guild):
        """Called when bot leaves a guild"""
        logger.info(f"Đã rời khỏi server: {guild.name} (ID: {guild.id})")
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            # Ignore command not found errors
            return
        elif isinstance(error, commands.CheckFailure):
            # Check failures should be handled by local error handlers
            # Only handle if not already handled
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Thiếu Tham Số",
                description=f"Vui lòng sử dụng `{config.BOT_PREFIX}help` để xem hướng dẫn.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="❌ Tham Số Không Hợp Lệ",
                description=f"Vui lòng sử dụng `{config.BOT_PREFIX}help` để xem hướng dẫn.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            logger.error(f"Lỗi không xử lý được: {error}")
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def main():
    """Main function to run the bot"""
    # Log session start
    log_session_start()
    logger.info("Đang khởi động SuperClearChat Bot...")
    
    # Create bot instance
    bot = SuperClearChatBot()
    
    try:
        # Start the bot
        await bot.start(config.DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error("❌ Token Discord không hợp lệ!")
        return
    except Exception as e:
        logger.error(f"❌ Lỗi khi khởi động bot: {e}")
        return
    finally:
        # Log session end
        log_session_end()

if __name__ == "__main__":
    try:
        # Run the bot
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot đã được dừng bởi người dùng")
        log_session_end()
    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng: {e}")
        log_session_end()
        sys.exit(1)
