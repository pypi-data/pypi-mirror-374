"""
腾讯云 DNSPod 服务包
"""

from .server import serve

def main():
    """
    命令行入口点
    """
    import asyncio
    asyncio.run(serve())
    

__all__ = ["main"]
