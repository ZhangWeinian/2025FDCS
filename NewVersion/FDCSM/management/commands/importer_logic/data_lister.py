# FDCSM/management/commands/importer_logic/data_lister.py
from typing import Any, Dict

from django.core.management.base import CommandError, OutputWrapper

from FDCSM import models  # 假设 models 在上层 FDCSM 包中

from .print_style import style_ERROR, style_NOTICE, style_SUCCESS, style_WARNING


def list_professors(
    stdout: OutputWrapper, stderr: OutputWrapper
):  # 传入 stdout, stderr
    stdout.write(style_NOTICE(stdout, "--- 导师数据 ---"))
    professors = models.FDC_PFS_INFO.objects.all().order_by("PFS_NBR")
    if not professors.exists():
        stdout.write("  数据库中没有导师数据。")
    else:
        for pfs in professors:
            tel_info = (
                f", 电话: {pfs.PFS_TEL_NBR}"
                if hasattr(pfs, "PFS_TEL_NBR") and pfs.PFS_TEL_NBR
                else ""
            )
            intro_info = (
                f", 简介: {pfs.PFS_INTRO}"
                if hasattr(pfs, "PFS_INTRO") and pfs.PFS_INTRO
                else ""
            )
            stdout.write(
                f"  导师号: {pfs.PFS_NBR}, 姓名: {pfs.PFS_NAM}, 数学可选: {pfs.PFS_NUM_MATH}, 物理可选: {pfs.PFS_NUM_PSC}, 系统科学可选: {pfs.PFS_NUM_SCI}, 应用统计可选: {pfs.PFS_NUM_AST}, 纳米可选: {pfs.PFS_NUM_NANO}{intro_info}{tel_info}"
            )
        stdout.write(
            style_SUCCESS(stdout, f"  共列出 {professors.count()} 条导师数据。")
        )
    stdout.write("")


def list_students(stdout: OutputWrapper, stderr: OutputWrapper):
    stdout.write(style_NOTICE(stdout, "--- 学生数据 ---"))
    students = models.FDC_STU_INFO.objects.all().order_by("STU_NBR")
    if not students.exists():
        stdout.write("  数据库中没有学生数据。")
    else:
        db_code_to_display_text: Dict[Any, str] = {}
        if hasattr(models.FDC_STU_INFO, "stu_pro_choices"):
            try:
                for code, text in models.FDC_STU_INFO.stu_pro_choices:
                    db_code_to_display_text[code] = str(text).strip()
            except (TypeError, ValueError):
                stderr.write(
                    style_WARNING(
                        stderr,
                        "  学生专业的 stu_pro_choices 定义不规范，无法用于显示文本。",
                    )
                )
        for stu in students:
            pro_display = db_code_to_display_text.get(
                stu.STU_PRO, str(stu.STU_PRO) if stu.STU_PRO is not None else "未指定"
            )
            tel_info = (
                f", 电话: {stu.STU_TEL_NBR}"
                if hasattr(stu, "STU_TEL_NBR") and stu.STU_TEL_NBR
                else ""
            )
            stdout.write(
                f"  学号: {stu.STU_NBR}, 姓名: {stu.STU_NAM}, 专业: {pro_display}{tel_info}"
            )
        stdout.write(style_SUCCESS(stdout, f"  共列出 {students.count()} 条学生数据。"))
    stdout.write("")


def list_admins(stdout: OutputWrapper, stderr: OutputWrapper):
    stdout.write(style_NOTICE(stdout, "--- 管理员数据 ---"))
    admins = models.FDC_ADM_INFO.objects.all().order_by("ADM_NBR")
    if not admins.exists():
        stdout.write("  数据库中没有管理员数据。")
    else:
        for adm in admins:
            stdout.write(f"  登录账号: {adm.ADM_NBR}, 姓名: {adm.ADM_NAM}")
        stdout.write(style_SUCCESS(stdout, f"  共列出 {admins.count()} 条管理员数据。"))
    stdout.write("")
