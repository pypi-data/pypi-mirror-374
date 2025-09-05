

import logging
import os
from pathlib import Path
from typing import Optional


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """設定並返回logger實例"""

    logger = logging.getLogger(name or __name__)

    # 如果logger已經有處理器，直接返回
    if logger.handlers:
        return logger

    # 設定日誌格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 添加控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 添加檔案處理器 - 使用用戶目錄而不是專案目錄
    try:
        # 獲取用戶應用程式資料目錄
        if os.name == 'nt':  # Windows
            app_data = os.environ.get(
                'APPDATA', Path.home() / 'AppData' / 'Roaming')
            log_dir = Path(app_data) / 'myepubapp' / 'logs'
        else:  # Unix-like systems (Linux, macOS)
            log_dir = Path.home() / '.local' / 'share' / 'myepubapp' / 'logs'

        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'myepubapp.log'

        file_handler = logging.FileHandler(
            log_file,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    except (OSError, PermissionError) as e:
        # 如果無法創建日誌檔案，只使用控制台日誌
        logger.warning(f"無法創建日誌檔案，將只使用控制台日誌: {e}")

    # 設定日誌層級
    logger.setLevel(logging.INFO)

    return logger

