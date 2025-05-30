# FDCSM/management/commands/importer_logic/data_importers.py
import os
from typing import Any, Dict, List, Optional

import pandas as pd
from django.core.management.base import CommandError  # 用于 stdout/stderr
from django.core.management.base import OutputWrapper
from django.db import transaction

from FDCSM import models

# 从同级包导入 excel_parser
from .excel_parser import read_and_map_excel  # 注意这里的相对导入
from .print_style import style_ERROR, style_NOTICE, style_SUCCESS, style_WARNING


# _parse_excel_integer 可以作为此模块的私有辅助函数
def _parse_excel_integer(
    stderr: OutputWrapper,  # 需要 stderr 来打印错误
    val_str: str,
    field_name: str,
    owner_id: str,
    row_num: int,
) -> Optional[int]:
    try:
        num_val_float = float(val_str)
        if num_val_float < 0:
            stderr.write(
                style_ERROR(
                    stderr,
                    f"记录 {owner_id} (行 {row_num}) 的 '{field_name}' 值 '{val_str}' 为负数，无效。",
                )
            )
            return None
        if num_val_float.is_integer():
            return int(num_val_float)
        else:
            stderr.write(
                style_ERROR(
                    stderr,
                    f"记录 {owner_id} (行 {row_num}) 的 '{field_name}' 值 '{val_str}' 包含小数，但期望为整数。",
                )
            )
            return None
    except ValueError:
        stderr.write(
            style_ERROR(
                stderr,
                f"记录 {owner_id} (行 {row_num}) 的 '{field_name}' 值 '{val_str}' 不是有效的数字。",
            )
        )
        return None


@transaction.atomic
def import_professors_logic(
    stdout: OutputWrapper, stderr: OutputWrapper, file_path: str
) -> None:
    column_map: Dict[str, str] = {
        "导师登录号码": "pfs_nbr",
        "导师姓名": "pfs_nam",
        "导师登录密码": "pfs_pwd",
        "数学专业可选人数": "pfs_num_math",
        "物理专业可选人数": "pfs_num_psc",
        "系统科学专业可选人数": "pfs_num_sci",
        "应用统计专业可选人数": "pfs_num_ast",
        "纳米科学与工程专业可选人数": "pfs_num_nano",
        "导师简介": "pfs_intro",
        "导师电话号码": "pfs_tel_nbr",
    }
    required_excel_keys: List[str] = [
        "导师登录号码",
        "导师姓名",
        "导师登录密码",
        "数学专业可选人数",
        "物理专业可选人数",
        "系统科学专业可选人数",
        "应用统计专业可选人数",
        "纳米科学与工程专业可选人数",
    ]
    df = read_and_map_excel(file_path, column_map, required_excel_keys)  # 调用辅助函数

    stdout.write(
        f"  在导师文件 '{os.path.basename(file_path)}' 中找到 {len(df)} 行数据进行处理..."
    )
    created, skipped, errors = 0, 0, 0
    for i, (_idx, r) in enumerate(df.iterrows()):
        rn = i + 2
        nbr = str(r.get("pfs_nbr", "")).strip()
        if not nbr:
            stderr.write(
                style_ERROR(stderr, f"    导师文件行 {rn}: 登录号码为空，跳过。")
            )
            errors += 1
            continue
        if models.FDC_PFS_INFO.objects.filter(PFS_NBR=nbr).exists():
            stdout.write(
                style_WARNING(stdout, f"    导师 {nbr} (行 {rn}) 已存在，跳过。")
            )
            skipped += 1
            continue
        nam, pwd = str(r.get("pfs_nam", "")).strip(), str(r.get("pfs_pwd", "")).strip()
        if not nam:
            stderr.write(
                style_ERROR(stderr, f"    导师 {nbr} (行 {rn}): 姓名为空，跳过。")
            )
            errors += 1
            continue
        if not pwd:
            stderr.write(
                style_ERROR(stderr, f"    导师 {nbr} (行 {rn}): 密码为空，跳过。")
            )
            errors += 1
            continue
        data: Dict[str, Any] = {"PFS_NBR": nbr, "PFS_NAM": nam, "PFS_PWD": pwd}
        if "pfs_tel_nbr" in df.columns and pd.notna(r.get("pfs_tel_nbr")):
            data["PFS_TEL_NBR"] = str(r.get("pfs_tel_nbr", "")).strip()
        if "pfs_intro" in df.columns and pd.notna(r.get("pfs_intro")):
            data["PFS_INTRO"] = str(r.get("pfs_intro", "")).strip()
        num_map = {
            "pfs_num_math": "PFS_NUM_MATH",
            "pfs_num_psc": "PFS_NUM_PSC",
            "pfs_num_sci": "PFS_NUM_SCI",
            "pfs_num_ast": "PFS_NUM_AST",
            "pfs_num_nano": "PFS_NUM_NANO",
        }
        valid_nums = True
        for ik, mf in num_map.items():
            if ik not in df.columns:
                style_ERROR(
                    stderr,
                    f"    导师 {nbr} (行 {rn}): 必需数字段列 '{column_map.get(ik,ik)}' 未找到。跳过。",
                )
                valid_nums = False
                break
            val_s = str(r.get(ik, "")).strip()
            excel_col_name = next((k for k, v in column_map.items() if v == ik), ik)
            if not val_s:
                style_ERROR(
                    stderr,
                    f"    导师 {nbr} (行 {rn}): 必填数字段 '{excel_col_name}' 为空。跳过。",
                )
                valid_nums = False
                break
            num = _parse_excel_integer(
                stderr, val_s, excel_col_name, nbr, rn
            )  # 传递 stderr
            if num is None:
                valid_nums = False
                break
            data[mf] = num
        if not valid_nums:
            errors += 1
            continue
        try:
            models.FDC_PFS_INFO.objects.create(**data)
            created += 1
        except Exception as e:
            style_ERROR(stderr, f"    创建导师 {nbr} (行 {rn}) 错误: {e}")
            errors += 1
    style_SUCCESS(
        stdout,
        f"  导师文件处理完毕。成功创建: {created} 条，跳过: {skipped} 条，错误: {errors} 条.",
    )
    stdout.write("")


@transaction.atomic
def import_students_logic(
    stdout: OutputWrapper, stderr: OutputWrapper, file_path: str
) -> None:
    column_map: Dict[str, str] = {
        "学生登录账号": "stu_nbr",
        "学生姓名": "stu_nam",
        "学生登录密码": "stu_pwd",
        "学生专业（物理专业/数学专业/系统科学专业/应用统计专业/纳米科学与工程专业）": "stu_pro_text",
        "联系电话": "stu_tel_nbr",
    }
    required_excel_keys: List[str] = [
        "学生登录账号",
        "学生姓名",
        "学生登录密码",
        "学生专业（物理专业/数学专业/系统科学专业/应用统计专业/纳米科学与工程专业）",
    ]
    df = read_and_map_excel(file_path, column_map, required_excel_keys)  # 调用辅助函数

    excel_val_to_db_code: Dict[str, int] = {}
    valid_excel_vals: List[str] = []
    if hasattr(models.FDC_STU_INFO, "stu_pro_choices"):
        try:
            for db_c, disp_t in models.FDC_STU_INFO.stu_pro_choices:
                db_c_int = int(db_c)
                txt_s = str(disp_t).strip()
                excel_val_to_db_code[txt_s] = db_c_int
                if txt_s not in valid_excel_vals:
                    valid_excel_vals.append(txt_s)
                code_s = str(db_c)
                excel_val_to_db_code[code_s] = db_c_int
                if code_s not in valid_excel_vals:
                    valid_excel_vals.append(code_s)
        except Exception as e:
            style_ERROR(stderr, f"  处理 stu_pro_choices 错误: {e}")
    else:
        style_WARNING(stderr, "  FDC_STU_INFO 未定义 stu_pro_choices")

    stdout.write(
        f"  在学生文件 '{os.path.basename(file_path)}' 中找到 {len(df)} 行数据进行处理..."
    )
    created, skipped, errors = 0, 0, 0
    for i, (_idx, r) in enumerate(df.iterrows()):
        rn = i + 2
        nbr = str(r.get("stu_nbr", "")).strip()
        if not nbr:
            style_ERROR(stderr, f"    学生文件行 {rn}: 学号为空，跳过。")
            errors += 1
            continue
        if models.FDC_STU_INFO.objects.filter(STU_NBR=nbr).exists():
            style_WARNING(stdout, f"    学生 {nbr} (行 {rn}) 已存在，跳过。")
            skipped += 1
            continue
        nam, pwd = str(r.get("stu_nam", "")).strip(), str(r.get("stu_pwd", "")).strip()
        pro_txt_key = "stu_pro_text"
        if pro_txt_key not in df.columns:
            style_ERROR(stderr, f"    学生 {nbr} (行 {rn}): 专业列丢失。跳过。")
            errors += 1
            continue
        pro_val = str(r.get(pro_txt_key, "")).strip()
        excel_col_stu_pro_display_name = next(
            (k for k, v in column_map.items() if v == pro_txt_key), pro_txt_key
        )

        if not nam:
            style_ERROR(stderr, f"    学生 {nbr} (行 {rn}): 姓名为空，跳过。")
            errors += 1
            continue
        if not pwd:
            style_ERROR(stderr, f"    学生 {nbr} (行 {rn}): 密码为空，跳过。")
            errors += 1
            continue
        if not pro_val:
            style_ERROR(stderr, f"    学生 {nbr} (行 {rn}): 专业为空，跳过。")
            errors += 1
            continue

        db_code = excel_val_to_db_code.get(pro_val)
        if db_code is None:
            if not excel_val_to_db_code and pro_val.isdigit():
                try:
                    db_code = int(pro_val)
                except ValueError:
                    pass
            if db_code is None:
                style_ERROR(
                    stderr,
                    f"    学生 {nbr} (行 {rn}): 专业值 '{pro_val}' 无效。有效值: {valid_excel_vals if valid_excel_vals else '[映射未加载]'} 跳过。",
                )
                errors += 1
                continue

        data: Dict[str, Any] = {
            "STU_NBR": nbr,
            "STU_NAM": nam,
            "STU_PWD": pwd,
            "STU_PRO": db_code,
        }
        if "stu_tel_nbr" in df.columns and pd.notna(r.get("stu_tel_nbr")):
            data["STU_TEL_NBR"] = str(r.get("stu_tel_nbr", "")).strip()
        try:
            models.FDC_STU_INFO.objects.create(**data)
            created += 1
        except Exception as e:
            style_ERROR(stderr, f"    创建学生 {nbr} (行 {rn}) 错误: {e}")
            errors += 1
    style_SUCCESS(
        stdout,
        f"  学生文件处理完毕。成功创建: {created} 条，跳过: {skipped} 条，错误: {errors} 条。",
    )
    stdout.write("")


@transaction.atomic
def import_admins_logic(
    stdout: OutputWrapper, stderr: OutputWrapper, file_path: str
) -> None:
    AdminModel = models.FDC_ADM_INFO
    column_map: Dict[str, str] = {
        "登录账号": "adm_nbr",
        "姓名": "adm_nam",
        "登录密码": "adm_pwd",
    }
    required_excel_keys: List[str] = ["登录账号", "姓名", "登录密码"]
    df = read_and_map_excel(file_path, column_map, required_excel_keys)  # 调用辅助函数

    stdout.write(
        f"  在管理员文件 '{os.path.basename(file_path)}' 中找到 {len(df)} 行数据进行处理..."
    )
    created, skipped, errors = 0, 0, 0
    for i, (_idx, r) in enumerate(df.iterrows()):
        rn = i + 2
        nbr = str(r.get("adm_nbr", "")).strip()
        if not nbr:
            style_ERROR(stderr, f"    管理员文件行 {rn}: 登录账号为空，跳过。")
            errors += 1
            continue
        if AdminModel.objects.filter(ADM_NBR=nbr).exists():
            style_WARNING(stdout, f"    管理员 {nbr} (行 {rn}) 已存在，跳过。")
            skipped += 1
            continue
        nam, pwd = str(r.get("adm_nam", "")).strip(), str(r.get("adm_pwd", "")).strip()
        if not nam:
            style_ERROR(stderr, f"    管理员 {nbr} (行 {rn}): 姓名为空，跳过。")
            errors += 1
            continue
        if not pwd:
            style_ERROR(stderr, f"    管理员 {nbr} (行 {rn}): 密码为空，跳过。")
            errors += 1
            continue
        try:
            AdminModel.objects.create(ADM_NBR=nbr, ADM_NAM=nam, ADM_PWD=pwd)
            created += 1
        except Exception as e:
            style_ERROR(stderr, f"    创建管理员 {nbr} (行 {rn}) 错误: {e}")
            errors += 1
    style_SUCCESS(
        stdout,
        f"  管理员文件处理完毕。成功创建: {created} 条，跳过: {skipped} 条，错误: {errors} 条。",
    )
    stdout.write("")
