"""
Utility functions for the bot
"""
import re
import discord
from typing import Optional, Union
from datetime import datetime, timedelta
from utils.logger import logger

def parse_user_mention(mention_or_id: str) -> Optional[int]:
    """
    Parse user mention or ID to get user ID
    
    Args:
        mention_or_id: User mention (<@123456>) or user ID (123456)
    
    Returns:
        User ID as integer or None if invalid
    """
    # Check if it's a mention format <@123456> or <@!123456>
    mention_pattern = r'<@!?(\d+)>'
    match = re.match(mention_pattern, mention_or_id)
    
    if match:
        return int(match.group(1))
    
    # Check if it's a direct user ID
    if mention_or_id.isdigit():
        return int(mention_or_id)
    
    return None

def validate_days(days: str, min_days: int, max_days: int) -> Optional[int]:
    """
    Validate days parameter
    
    Args:
        days: Days string to validate
        min_days: Minimum allowed days
        max_days: Maximum allowed days
    
    Returns:
        Days as integer or None if invalid
    """
    try:
        days_int = int(days)
        if min_days <= days_int <= max_days:
            return days_int
        return None
    except ValueError:
        return None

def get_date_cutoff(days: int) -> datetime:
    """
    Get the cutoff date for message deletion
    
    Args:
        days: Number of days to go back
    
    Returns:
        Cutoff datetime
    """
    return datetime.now() - timedelta(days=days)

async def get_user_from_guild(guild: discord.Guild, user_id: int) -> Optional[Union[discord.Member, discord.User]]:
    """
    Get user from guild by ID
    
    Args:
        guild: Discord guild
        user_id: User ID to find
    
    Returns:
        Member or User object, or None if not found
    """
    try:
        # Try to get member from guild first
        member = guild.get_member(user_id)
        if member:
            return member
        
        # If not found in guild, try to fetch user
        user = await guild.client.fetch_user(user_id)
        return user
    except discord.NotFound:
        logger.warning(f"Không tìm thấy user với ID: {user_id}")
        return None
    except Exception as e:
        logger.error(f"Lỗi khi tìm user {user_id}: {e}")
        return None

def format_user_display(user: Union[discord.Member, discord.User]) -> str:
    """
    Format user display name
    
    Args:
        user: Discord user or member
    
    Returns:
        Formatted display name
    """
    if isinstance(user, discord.Member) and user.nick:
        return f"{user.nick} ({user.name}#{user.discriminator})"
    return f"{user.name}#{user.discriminator}"
