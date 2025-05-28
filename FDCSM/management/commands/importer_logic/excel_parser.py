# FDCSM/management/commands/importer_logic/excel_parser.py
import os
from typing import Dict, List, Union

import pandas as pd
from django.core.management.base import CommandError  # 或自定义异常


def read_and_map_excel(
    file_path: str,
    column_map: Dict[str, str],
    required_excel_keys: List[str],
    sheet_name: Union[int, str] = 0,
) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise CommandError(f'Excel文件 "{file_path}" 未找到。')
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
        df = df.fillna("")

        actual_headers = [str(col).strip() for col in df.columns]

        missing_required = [
            req_key for req_key in required_excel_keys if req_key not in actual_headers
        ]
        if missing_required:
            msg = (
                f"文件 '{os.path.basename(file_path)}' 的表头中缺少【必填】列或与预期不符。\n"
                f"缺失或不符的必填表头: {', '.join(missing_required)}\n"
                f"文件中的实际表头 (已去除首尾空格): {actual_headers}\n"
                f"预期的必填表头: {required_excel_keys}\n"
            )
            raise CommandError(msg)

        rename_map_for_df = {}
        for excel_header_in_map, internal_key in column_map.items():
            if excel_header_in_map in actual_headers:
                rename_map_for_df[excel_header_in_map] = internal_key

        df.rename(columns=rename_map_for_df, inplace=True)

        internal_keys_to_keep = [
            key for key in column_map.values() if key in df.columns
        ]

        mapped_internal_keys_for_required_cols = []
        for req_key in required_excel_keys:
            if req_key not in column_map:
                raise CommandError(
                    f"配置错误: 必需的 Excel 表头 '{req_key}' 未在 column_map 中定义。"
                )
            mapped_internal_keys_for_required_cols.append(column_map[req_key])

        if not all(key in df.columns for key in mapped_internal_keys_for_required_cols):
            problematic_req_keys = []
            for req_key in required_excel_keys:
                internal_key = column_map.get(req_key)
                if not internal_key or internal_key not in df.columns:
                    problematic_req_keys.append(req_key)

            actual_df_cols_after_rename = list(df.columns)
            raise CommandError(
                f"文件 '{os.path.basename(file_path)}' 中的必需列未能正确映射或在重命名后丢失。\n"
                f"有问题的原始Excel表头 (来自必填列表): {problematic_req_keys}\n"
                f"column_map 定义: {column_map}\n"
                f"重命名后的DataFrame列 (可用的内部键): {actual_df_cols_after_rename}"
            )

        df = df[internal_keys_to_keep]
        df.dropna(how="all", inplace=True)
        return df
    except CommandError:
        raise
    except Exception as e:
        raise CommandError(f'读取或处理Excel文件 "{file_path}" 时发生错误: {e}')
