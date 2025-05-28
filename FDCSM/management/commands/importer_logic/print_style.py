import sys  # 用于 sys.stdout, sys.stderr 以便检查 isatty()


# 定义ANSI颜色和样式代码
class AnsiStyles:
    # 颜色
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"  # 用于 NOTICE
    CYAN = "\033[96m"  # 备用 NOTICE

    # 样式
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"  # 不常用，但备用

    # 重置
    RESET = "\033[0m"  # 重置所有颜色和样式


def _is_tty(stream_obj) -> bool:
    """检查给定的流对象是否是TTY（终端）"""
    return hasattr(stream_obj, "isatty") and stream_obj.isatty()


def style_SUCCESS(stdout, message: str) -> str:
    """
    设置成功消息的输出格式。
    例如: ✅ [SUCCESS] Your operation was successful. (绿色)
    """
    prefix_icon = "✅"
    prefix_text = "[SUCCESS]"

    if _is_tty(stdout):
        # 前缀部分：绿色加粗
        # 消息部分：绿色
        return (
            f"{AnsiStyles.GREEN}{AnsiStyles.BOLD}{prefix_icon} {prefix_text}{AnsiStyles.RESET}"
            f" {AnsiStyles.GREEN}{message}{AnsiStyles.RESET}"
        )
    else:
        return f"{prefix_icon} {prefix_text} {message}"


def style_WARNING(stdout, message: str) -> str:
    """
    设置警告消息的输出格式。
    例如: ⚠️ [WARNING] Disk space is low. (黄色)
    """
    prefix_icon = "⚠️"
    prefix_text = "[WARNING]"

    if _is_tty(stdout):
        # 前缀部分：黄色加粗
        # 消息部分：黄色
        return (
            f"{AnsiStyles.YELLOW}{AnsiStyles.BOLD}{prefix_icon} {prefix_text}{AnsiStyles.RESET}"
            f" {AnsiStyles.YELLOW}{message}{AnsiStyles.RESET}"
        )
    else:
        return f"{prefix_icon} {prefix_text} {message}"


def style_ERROR(stdout, message: str) -> str:
    """
    设置错误消息的输出格式。
    例如: ❌ [ERROR] File not found. (红色)
    """
    prefix_icon = "❌"
    prefix_text = "[ERROR]"

    if _is_tty(stdout):
        # 前缀部分：红色加粗
        # 消息部分：红色
        return (
            f"{AnsiStyles.RED}{AnsiStyles.BOLD}{prefix_icon} {prefix_text}{AnsiStyles.RESET}"
            f" {AnsiStyles.RED}{message}{AnsiStyles.RESET}"
        )
    else:
        return f"{prefix_icon} {prefix_text} {message}"


def style_NOTICE(stdout, message: str) -> str:
    """
    设置通知消息的输出格式。
    例如: ℹ️ [NOTICE] System update available. (蓝色)
    """
    prefix_icon = "ℹ️"  # Unicode 信息符号
    prefix_text = "[NOTICE]"

    if _is_tty(stdout):
        # 前缀部分：蓝色加粗
        # 消息部分：蓝色
        return (
            f"{AnsiStyles.BLUE}{AnsiStyles.BOLD}{prefix_icon} {prefix_text}{AnsiStyles.RESET}"
            f" {AnsiStyles.BLUE}{message}{AnsiStyles.RESET}"
        )
    else:
        return f"{prefix_icon} {prefix_text} {message}"
