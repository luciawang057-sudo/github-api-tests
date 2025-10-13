import logging
from pathlib import Path

def set_up_logging():

    # 配置日志
    log_dir = Path("logs")# 指向当前目录下的logs文件夹
    log_dir.mkdir(exist_ok=True) # ✅ 创建logs目录
    log_file = log_dir / "github_api_tests.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]  # 先只输出到控制台
        )

