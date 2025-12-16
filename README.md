# SuperClearChat Discord Bot

Bot Discord chuyên dụng để xóa tin nhắn của user theo thời gian với logging đầy đủ và giao diện đẹp mắt.

## 🚀 Tính Năng

- **Xóa tin nhắn theo user**: Xóa tin nhắn của user cụ thể bằng mention hoặc ID
- **Hỗ trợ voice channels**: Xóa tin nhắn trong kênh chat của voice channels
- **Xóa hàng loạt**: Xóa tin nhắn trong tất cả voice channels cùng lúc
- **Giới hạn thời gian**: Chỉ xóa tin nhắn trong khoảng thời gian được chỉ định (1-14 ngày)
- **Logging đầy màu**: Hệ thống log với màu sắc phù hợp, dễ theo dõi
- **Cấu trúc code rõ ràng**: Logic được tách riêng, dễ bảo trì và mở rộng
- **Xử lý lỗi tốt**: Thông báo lỗi rõ ràng và xử lý các trường hợp edge case
- **Help command đầy đủ**: Hướng dẫn chi tiết cách sử dụng

## 📁 Cấu Trúc Project

```
SuperClearChat/
├── main.py                 # File chính, khởi tạo bot
├── requirements.txt        # Dependencies
├── .env                   # Cấu hình bot (token, prefix, etc.)
├── .gitignore            # Git ignore file
├── README.md             # File này
├── utils/                # Utilities
│   ├── __init__.py
│   ├── logger.py         # Hệ thống logging với màu sắc
│   ├── config.py         # Xử lý cấu hình từ .env
│   └── helpers.py        # Các hàm tiện ích
├── core/                 # Logic chính
│   ├── __init__.py
│   └── message_cleaner.py # Logic xóa tin nhắn
└── commands/             # Discord commands
    ├── __init__.py
    ├── clear_commands.py # Lệnh clear
    └── help_commands.py  # Lệnh help
```

## ⚙️ Cài Đặt

### 1. Clone Repository
```bash
git clone <repository-url>
cd SuperClearChat
```

### 2. Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu Hình Bot
Chỉnh sửa file `.env`:
```properties
# Discord Bot Configuration
DISCORD_TOKEN=your_bot_token_here

# Bot Settings
BOT_PREFIX=SPC!
MAX_DAYS_LIMIT=14
MIN_DAYS_LIMIT=1

# Logging Settings
LOG_LEVEL=INFO
LOG_TO_FILE=true
```
MIN_DAYS_LIMIT=1
```

### 4. Chạy Bot
```bash
python main.py
```

## 🎮 Cách Sử Dụng

### Lệnh Clear
```
SPC!clear @user/user_id days [current|all]
```

**Ví dụ:**
- `SPC!clear @JohnDoe 7` - Xóa tin nhắn của @JohnDoe trong 7 ngày qua (kênh hiện tại)
- `SPC!clear @JohnDoe 7 current` - Xóa tin nhắn trong kênh hiện tại
- `SPC!clear @JohnDoe 7 all` - Xóa tin nhắn trong tất cả kênh của server
- `SPC!clear 123456789 3 all` - Xóa tin nhắn của user ID trong tất cả kênh

### Lệnh Help
```
SPC!help
```
Hiển thị hướng dẫn chi tiết cách sử dụng bot.

## 🔐 Quyền Cần Thiết

### Quyền cho User:
- **Manage Messages** - Để sử dụng lệnh clear

### Quyền cho Bot:
- **Read Message History** - Để đọc lịch sử tin nhắn
- **Manage Messages** - Để xóa tin nhắn
- **Send Messages** - Để gửi phản hồi
- **Embed Links** - Để gửi embed messages

## 📊 Logging

Bot sử dụng hệ thống logging với cả console và file:

### Console Logging (có màu sắc):
- **Trắng**: Ngày giờ và nội dung
- **Xanh lá**: INFO messages
- **Vàng**: WARNING messages  
- **Đỏ**: ERROR messages

### File Logging:
- **Location**: `logs/superclearchat.log`
- **Format**: Plain text không màu, dễ đọc
- **Rotation**: Tự động xoay file khi đạt 10MB (giữ 5 backup)
- **Session tracking**: Ghi log khi bot start/stop

**Cấu hình logging trong `.env`:**
```properties
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE=true        # true/false
```

**Ví dụ log output:**
```
2025-09-08 14:17:14 | INFO | ===============================================
2025-09-08 14:17:14 | INFO | 🚀 SuperClearChat Bot - Session Started
2025-09-08 14:17:14 | INFO | 📅 Start Time: 2025-09-08 14:17:14
2025-09-08 14:17:14 | INFO | ===============================================
2025-09-08 14:17:15 | INFO | Bot đã sẵn sàng: SuperClearChat (ID: 123456789)
2025-09-08 14:18:20 | INFO | Bắt đầu xóa tin nhắn của JohnDoe#1234 trong 7 ngày qua
2025-09-08 14:18:21 | INFO | Hoàn thành xóa tin nhắn: 25 tin nhắn đã xóa, 0 lỗi
```

## 🚨 Lưu Ý Quan Trọng

1. **Giới hạn thời gian**: Bot chỉ có thể xóa tin nhắn trong khoảng từ 1-14 ngày (có thể cấu hình)
2. **Tin nhắn cũ**: Tin nhắn cũ hơn 14 ngày sẽ được xóa từng cái một (chậm hơn do giới hạn của Discord API)
3. **Quyền hạn**: Bot cần đủ quyền để thực hiện xóa tin nhắn
4. **Phạm vi xóa**: 
   - `current`: Chỉ kênh hiện tại đang gọi lệnh
   - `all`: Tất cả kênh text và voice trong server
5. **Log files**: Tự động lưu trong thư mục `logs/`, có thể tắt bằng `LOG_TO_FILE=false`

## 🛠️ Tùy Chỉnh

### Thay đổi Prefix
Chỉnh sửa `BOT_PREFIX` trong file `.env`

### Thay đổi giới hạn ngày
Chỉnh sửa `MAX_DAYS_LIMIT` và `MIN_DAYS_LIMIT` trong file `.env`

### Thêm tính năng
1. Tạo file mới trong thư mục `commands/`
2. Load extension trong `main.py`
3. Thêm logic xử lý trong thư mục `core/` nếu cần

## 🐛 Troubleshooting

### Bot không phản hồi
- Kiểm tra token trong file `.env`
- Đảm bảo bot có quyền đọc và gửi tin nhắn trong kênh

### Lỗi "Missing Permissions"
- Kiểm tra quyền của bot trong server
- Đảm bảo user có quyền "Manage Messages"

### Bot không xóa được tin nhắn cũ
- Discord không cho phép xóa tin nhắn cũ hơn 14 ngày bằng bulk delete
- Bot sẽ tự động chuyển sang chế độ xóa từng tin nhắn (chậm hơn)

## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết.
