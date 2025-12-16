"""
Message clearing logic - Updated for Kicked/Banned Users
"""
import discord
from datetime import datetime
from typing import List, Union, Optional
from utils.logger import logger
from utils.helpers import get_date_cutoff, format_user_display

async def clear_user_messages(
    channel: Union[discord.TextChannel, discord.VoiceChannel],
    user: Union[discord.Member, discord.User, int], # Update: Chấp nhận thêm int (ID)
    days: int,
    requester: discord.Member
) -> dict:
    """
    Clear messages from a specific user (or user ID) in a channel
    
    Args:
        channel: Discord text channel or voice channel
        user: Target user object OR user ID (int) if user left server
        days: Number of days to look back
        requester: Member who requested the clear
    """
    cutoff_date = get_date_cutoff(days)
    deleted_count = 0
    errors = 0
    
    # Xử lý lấy ID mục tiêu và tên hiển thị cho Log
    if isinstance(user, int):
        target_user_id = user
        target_display_name = f"User ID: {user} (Left/Kicked)"
    else:
        target_user_id = user.id
        target_display_name = format_user_display(user)

    # Determine channel type
    channel_type = "voice chat" if isinstance(channel, discord.VoiceChannel) else "text chat"
    
    logger.info(f"Bắt đầu xóa tin nhắn của {target_display_name} trong {days} ngày qua")
    logger.info(f"Được yêu cầu bởi: {format_user_display(requester)}")
    logger.info(f"Kênh: #{channel.name} ({channel.id}) - {channel_type}")
    
    try:
        # Get messages from the channel
        messages_to_delete: List[discord.Message] = []
        
        async for message in channel.history(limit=None, after=cutoff_date):
            # QUAN TRỌNG: So sánh ID thay vì so sánh object
            if message.author.id == target_user_id:
                messages_to_delete.append(message)
                
                # Discord allows bulk delete for messages younger than 14 days
                if len(messages_to_delete) >= 100:  # Process in batches
                    batch_deleted, batch_errors = await _delete_message_batch(
                        channel, messages_to_delete
                    )
                    deleted_count += batch_deleted
                    errors += batch_errors
                    messages_to_delete.clear()
        
        # Delete remaining messages
        if messages_to_delete:
            batch_deleted, batch_errors = await _delete_message_batch(
                channel, messages_to_delete
            )
            deleted_count += batch_deleted
            errors += batch_errors
        
        logger.info(f"Hoàn thành xóa tin nhắn: {deleted_count} tin nhắn đã xóa, {errors} lỗi")
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'errors': errors,
            'user': user,
            'days': days,
            'channel': channel,
            'channel_type': channel_type
        }
        
    except discord.Forbidden:
        logger.error("Không có quyền xóa tin nhắn trong kênh này")
        return {
            'success': False,
            'error': 'Không có quyền xóa tin nhắn trong kênh này',
            'deleted_count': deleted_count,
            'errors': errors + 1
        }
    except Exception as e:
        logger.error(f"Lỗi khi xóa tin nhắn: {e}")
        return {
            'success': False,
            'error': str(e),
            'deleted_count': deleted_count,
            'errors': errors + 1
        }

async def _delete_message_batch(
    channel: Union[discord.TextChannel, discord.VoiceChannel],
    messages: List[discord.Message]
) -> tuple[int, int]:
    """
    Delete a batch of messages
    (Giữ nguyên logic cũ vì logic này xử lý Message object lấy từ history, không phụ thuộc user còn trong sv hay không)
    """
    deleted_count = 0
    error_count = 0
    
    # Separate messages by age (Discord bulk delete only works for messages < 14 days old)
    now = datetime.now()
    bulk_deletable = []
    individual_delete = []
    
    for message in messages:
        # Cần check message.created_at có timezone hay không để tránh lỗi so sánh
        msg_created = message.created_at
        if msg_created.tzinfo is not None:
            msg_created = msg_created.replace(tzinfo=None)
            
        message_age = now - msg_created
        if message_age.days < 14:
            bulk_deletable.append(message)
        else:
            individual_delete.append(message)
    
    # Bulk delete recent messages
    if bulk_deletable:
        try:
            await channel.delete_messages(bulk_deletable)
            deleted_count += len(bulk_deletable)
            logger.info(f"Đã xóa {len(bulk_deletable)} tin nhắn (bulk delete)")
        except discord.HTTPException as e:
            logger.warning(f"Lỗi bulk delete, chuyển sang xóa từng tin nhắn: {e}")
            # If bulk delete fails, delete individually
            for message in bulk_deletable:
                try:
                    await message.delete()
                    deleted_count += 1
                except discord.HTTPException:
                    error_count += 1
    
    # Delete old messages individually
    for message in individual_delete:
        try:
            await message.delete()
            deleted_count += 1
        except discord.HTTPException as e:
            logger.warning(f"Không thể xóa tin nhắn {message.id}: {e}")
            error_count += 1
    
    if individual_delete:
        logger.info(f"Đã xóa {len(individual_delete) - error_count}/{len(individual_delete)} tin nhắn cũ")
    
    return deleted_count, error_count

async def clear_user_messages_all_channels(
    guild: discord.Guild,
    user: Union[discord.Member, discord.User, int], # Update: Chấp nhận int
    days: int,
    requester: discord.Member
) -> dict:
    """
    Clear messages from a specific user in all channels of a guild
    """
    total_deleted = 0
    total_errors = 0
    channels_processed = 0
    channels_with_messages = []
    
    # Xử lý hiển thị log
    target_display_name = f"User ID: {user}" if isinstance(user, int) else format_user_display(user)

    logger.info(f"Bắt đầu xóa tin nhắn của {target_display_name} trong tất cả kênh")
    logger.info(f"Server: {guild.name} ({guild.id})")
    logger.info(f"Được yêu cầu bởi: {format_user_display(requester)}")
    
    try:
        # Get all text and voice channels in the guild
        all_channels = []
        for channel in guild.channels:
            if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                all_channels.append(channel)
        
        if not all_channels:
            return {
                'success': True,
                'total_deleted': 0,
                'total_errors': 0,
                'channels_processed': 0,
                'channels_with_messages': [],
                'message': 'Không có kênh nào trong server'
            }
        
        logger.info(f"Tìm thấy {len(all_channels)} kênh(s)")
        
        # Process each channel
        for channel in all_channels:
            try:
                permissions = channel.permissions_for(guild.me)
                if not permissions.read_message_history:
                    # Bỏ qua warning log để đỡ spam console nếu server lớn
                    continue
                
                # Gọi hàm clear_user_messages (đã update ở trên)
                result = await clear_user_messages(channel, user, days, requester)
                channels_processed += 1
                
                if result['success']:
                    total_deleted += result['deleted_count']
                    total_errors += result['errors']
                    
                    if result['deleted_count'] > 0:
                        channel_type = "voice" if isinstance(channel, discord.VoiceChannel) else "text"
                        channels_with_messages.append({
                            'name': channel.name,
                            'id': channel.id,
                            'type': channel_type,
                            'deleted': result['deleted_count'],
                            'errors': result['errors']
                        })
                else:
                    total_errors += 1
                    
            except Exception as e:
                logger.error(f"Lỗi khi xử lý kênh '{channel.name}': {e}")
                total_errors += 1
        
        logger.info(f"Hoàn thành xóa tin nhắn trong {channels_processed} kênh(s)")
        logger.info(f"Tổng cộng: {total_deleted} tin nhắn đã xóa, {total_errors} lỗi")
        
        return {
            'success': True,
            'total_deleted': total_deleted,
            'total_errors': total_errors,
            'channels_processed': channels_processed,
            'channels_with_messages': channels_with_messages,
            'user': user,
            'days': days,
            'guild': guild
        }
        
    except Exception as e:
        logger.error(f"Lỗi khi xử lý tất cả kênh: {e}")
        return {
            'success': False,
            'error': str(e),
            'total_deleted': total_deleted,
            'total_errors': total_errors + 1,
            'channels_processed': channels_processed
        }