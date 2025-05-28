# FDCSM/management/commands/importer_logic/data_deleter.py
from django.core.management.base import CommandError  # 用于 stdout/stderr
from django.core.management.base import OutputWrapper
from django.db import transaction

from .print_style import style_ERROR, style_NOTICE, style_SUCCESS, style_WARNING


def delete_data_with_confirmation(
    stdout: OutputWrapper,  # 传入 stdout 和 stderr 以便打印
    stderr: OutputWrapper,
    model_class,
    model_name_display: str,
    interactive: bool,
    context_msg: str = "",
) -> bool:
    if context_msg:
        stdout.write(style_NOTICE(stdout, message=context_msg))

    if model_class.objects.exists():
        if interactive:
            stdout.write("")
            confirm = input(
                f"警告：你选择了删除所有【{model_name_display}】数据。这个操作不可逆！\n"
                f"确定要继续吗？ (yes/no): "
            )
            if confirm.lower() != "yes":
                stdout.write(
                    style_WARNING(
                        stdout, message=f"取消删除【{model_name_display}】数据。"
                    )
                )
                return False
        else:
            stdout.write(
                style_WARNING(
                    stdout,
                    message=f"根据 --no-input 参数，将自动删除【{model_name_display}】数据。",
                )
            )

        stdout.write(
            style_WARNING(
                stdout, message=f"正在删除所有【{model_name_display}】数据..."
            )
        )
        try:
            with transaction.atomic():
                count, _ = model_class.objects.all().delete()
            stdout.write(
                style_SUCCESS(
                    stdout, message=f"成功删除 {count} 条【{model_name_display}】数据。"
                )
            )
            return True
        except Exception as e:
            raise CommandError(f"删除【{model_name_display}】数据时出错: {e}")
    else:
        stdout.write(
            style_NOTICE(
                stdout, message=f"数据库中没有【{model_name_display}】数据可供删除。"
            )
        )
        return True
    # stdout.write("") # 调用者可以决定是否加空行
