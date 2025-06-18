# FDCSM/management/commands/import_initial_users.py
import os
from typing import Any, Dict, List, Optional, cast

from django.core.management.base import BaseCommand, CommandError, OutputWrapper

from FDCSM import models  # 假设 models 在 FDCSM 包的顶层

# 从新的逻辑包中导入函数
from .importer_logic import (
    read_and_map_excel,
)  # 虽然导入函数可能直接调用它，但主命令可能不需要直接用
from .importer_logic.data_deleter import delete_data_with_confirmation

# 从 importer_logic 包下的 data_importers 模块导入这些函数
from .importer_logic.data_importers import (
    import_admins_logic,
    import_professors_logic,
    import_students_logic,
)
from .importer_logic.data_lister import list_admins, list_professors, list_students

# 同时，也需要从其他模块导入：
from .importer_logic.excel_parser import (
    read_and_map_excel,
)  # 如果主命令直接用，否则由 importer 调用
from .importer_logic.print_style import (
    style_ERROR,
    style_NOTICE,
    style_SUCCESS,
    style_WARNING,
)


class Command(BaseCommand):
    help = (
        "从指定的Excel文件导入初始用户数据，或列出、删除数据库中已有的用户数据。"
        "（密码明文存储 - 仅限测试）。"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--professor_file",
            type=str,
            help="导师用户Excel文件路径 (用于导入)。",
            default=None,
        )
        parser.add_argument(
            "--student_file",
            type=str,
            help="学生用户Excel文件路径 (用于导入)。",
            default=None,
        )
        parser.add_argument(
            "--admin_file",
            type=str,
            help="管理员用户Excel文件路径 (用于导入)。",
            default=None,
        )
        parser.add_argument(
            "--list_data",
            nargs="+",
            choices=["all", "professors", "students", "admins"],
            help="在其他操作后列出指定类型的用户数据。",
            required=False,
        )
        parser.add_argument(
            "--delete_before_import",
            action="store_true",
            help="如果提供相应文件，则在导入前删除该类型所有数据。",
        )
        parser.add_argument(
            "--delete_only",
            nargs="+",
            choices=["all", "professors", "students", "admins"],
            help="只执行删除操作，然后退出。",
            required=False,
        )
        parser.add_argument(
            "--no-input",
            action="store_false",
            dest="interactive",
            default=True,
            help="跳过删除操作前的用户确认提示。",
        )

    def handle(self, *args, **options: Dict[str, Any]) -> None:

        self.stdout.write(
            style_WARNING(
                self.stdout,
                "警告：此脚本将以明文形式存储密码。这非常不安全，请仅用于受控的测试环境。",
            )
        )
        self.stdout.write("-" * 50)

        professor_file: Optional[str] = cast(Optional[str], options["professor_file"])
        student_file: Optional[str] = cast(Optional[str], options["student_file"])
        admin_file: Optional[str] = cast(Optional[str], options["admin_file"])

        delete_only_types: Optional[List[str]] = cast(
            Optional[List[str]], options.get("delete_only")
        )
        delete_before_import_flag: bool = bool(
            options.get("delete_before_import", False)
        )
        list_data_types: Optional[List[str]] = cast(
            Optional[List[str]], options.get("list_data")
        )
        interactive: bool = cast(bool, options["interactive"])

        # --- 处理 --delete_only (最高优先级) ---
        if delete_only_types:
            self.stdout.write(
                style_WARNING(self.stdout, "--- 单独执行数据删除操作 ---")
            )
            if "all" in delete_only_types or "professors" in delete_only_types:
                delete_data_with_confirmation(
                    self.stdout,
                    self.stderr,
                    models.FDC_PFS_INFO,
                    "导师",
                    interactive,
                    "因 --delete_only 删除导师数据",
                )
            if "all" in delete_only_types or "students" in delete_only_types:
                delete_data_with_confirmation(
                    self.stdout,
                    self.stderr,
                    models.FDC_STU_INFO,
                    "学生",
                    interactive,
                    "因 --delete_only 删除学生数据",
                )
            if "all" in delete_only_types or "admins" in delete_only_types:
                delete_data_with_confirmation(
                    self.stdout,
                    self.stderr,
                    models.FDC_ADM_INFO,
                    "管理员",
                    interactive,
                    "因 --delete_only 删除管理员数据",
                )
            self.stdout.write(style_SUCCESS(self.stdout, "--- 指定的删除操作完成 ---"))
            self.stdout.write("-" * 50)
            return  # 执行完 delete_only 后直接退出

        # --- 处理 --delete_before_import ---
        if delete_before_import_flag:
            self.stdout.write(
                style_WARNING(self.stdout, "--- 数据删除阶段 (导入前) ---")
            )
            if professor_file:
                delete_data_with_confirmation(
                    self.stdout,
                    self.stderr,
                    models.FDC_PFS_INFO,
                    "导师",
                    interactive,
                    f"为导入 '{os.path.basename(professor_file)}' 删除现有导师数据",
                )
            if student_file:
                delete_data_with_confirmation(
                    self.stdout,
                    self.stderr,
                    models.FDC_STU_INFO,
                    "学生",
                    interactive,
                    f"为导入 '{os.path.basename(student_file)}' 删除现有学生数据",
                )
            if admin_file:
                delete_data_with_confirmation(
                    self.stdout,
                    self.stderr,
                    models.FDC_ADM_INFO,
                    "管理员",
                    interactive,
                    f"为导入 '{os.path.basename(admin_file)}' 删除现有管理员数据",
                )
            self.stdout.write(
                style_WARNING(self.stdout, "--- 数据删除阶段 (导入前) 结束 ---")
            )
            self.stdout.write("-" * 50)

        # --- 导入逻辑 ---
        any_import_attempted = False
        if professor_file or student_file or admin_file:
            self.stdout.write(style_NOTICE(self.stdout, "--- 数据导入阶段 ---"))

        if professor_file:
            self.stdout.write(
                style_NOTICE(self.stdout, f"开始处理导师文件: {professor_file}")
            )
            import_professors_logic(self.stdout, self.stderr, professor_file)
            any_import_attempted = True
        if student_file:
            self.stdout.write(
                style_NOTICE(self.stdout, f"开始处理学生文件: {student_file}")
            )
            import_students_logic(self.stdout, self.stderr, student_file)
            any_import_attempted = True
        if admin_file:
            self.stdout.write(
                style_NOTICE(self.stdout, f"开始处理管理员文件: {admin_file}")
            )
            import_admins_logic(self.stdout, self.stderr, admin_file)
            any_import_attempted = True

        if any_import_attempted:
            self.stdout.write(
                style_SUCCESS(self.stdout, "所有指定的初始用户数据导入操作完成。")
            )
            self.stdout.write("-" * 50)
        elif (
            not list_data_types
            and not delete_before_import_flag
            and not delete_only_types
        ):
            self.stdout.write(style_NOTICE(self.stdout, "没有指定任何要导入的文件。"))

        # --- 列出数据逻辑 ---
        if list_data_types:
            self.stdout.write(
                style_SUCCESS(self.stdout, "--- 开始列出数据库中的用户数据 ---")
            )
            if "all" in list_data_types or "professors" in list_data_types:
                list_professors(self.stdout, self.stderr)
            if "all" in list_data_types or "students" in list_data_types:
                list_students(self.stdout, self.stderr)
            if "all" in list_data_types or "admins" in list_data_types:
                list_admins(self.stdout, self.stderr)
            self.stdout.write(style_SUCCESS(self.stdout, "--- 数据列出完成 ---"))
            self.stdout.write("-" * 50)

        if (
            not any_import_attempted
            and not list_data_types
            and not delete_before_import_flag
            and not delete_only_types
        ):
            self.stdout.write(
                style_NOTICE(
                    self.stdout, "提示：没有执行任何操作。使用 --help 查看可用选项。"
                )
            )
        self.stdout.write("")
