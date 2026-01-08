"""
主入口文件
"""

import uvicorn
from .api import app


def main():
    """主函数"""
    # 监听所有地址，确保 localhost 和 127.0.0.1 都能访问
    uvicorn.run(app, host="0.0.0.0", port=1216)


if __name__ == "__main__":
    main()