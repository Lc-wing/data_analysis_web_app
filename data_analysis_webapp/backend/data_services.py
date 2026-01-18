import pandas as pd
import numpy as np
import json
import os
from typing import List, Dict, Union, Any, Optional


class DataAnalysisService:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

    def load_data(self, file_path: str, file_type: str) -> pd.DataFrame:
        """根据格式导入数据到内存"""
        try:
            if file_type in ['xlsx', 'xls']:
                df = pd.read_excel(file_path)
            elif file_type == 'csv':
                df = pd.read_csv(file_path)
            elif file_type == 'json':
                df = pd.read_json(file_path)
            elif file_type == 'txt':
                df = pd.read_csv(file_path, sep='\t')
            else:
                raise ValueError("不支持的文件格式")
            return df
        except Exception as e:
            raise RuntimeError(f"数据解析失败: {str(e)}")

    def clean_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """功能1: 数据清洗"""
        original_rows = len(df)
        df_cleaned = df.drop_duplicates()
        df_cleaned = df_cleaned.dropna()
        removed_rows = original_rows - len(df_cleaned)
        for col in df_cleaned.columns:
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='ignore')
            if df_cleaned[col].dtype == 'object':
                df_cleaned[col] = df_cleaned[col].astype(str).str.strip().str.lower()
                try:
                    temp_date = pd.to_datetime(df_cleaned[col], errors='ignore')
                    if not temp_date.isna().all():
                        df_cleaned[col] = temp_date.dt.strftime('%Y-%m-%d')
                except:
                    pass
        return {
            "status": "success",
            "original_rows": original_rows,
            "cleaned_rows": len(df_cleaned),
            "removed_rows": removed_rows,
            "preview": df_cleaned.head(100).to_dict(orient='records')
        }

    def sort_data(self, df: pd.DataFrame, column: str, ascending: bool = False) -> List[Dict]:
        if column not in df.columns:
            raise ValueError(f"列名 {column} 不存在")
        try:
            df_sorted = df.sort_values(by=column, ascending=ascending)
        except Exception:
            df_sorted = df.astype(str).sort_values(by=column, ascending=ascending)
        return df_sorted.to_dict(orient='records')

    def calculate_statistics(self, df: pd.DataFrame, column: str) -> Dict:
        if column not in df.columns:
            raise ValueError(f"列名 {column} 不存在")
        col_data = pd.to_numeric(df[column], errors='coerce').dropna()
        if col_data.empty:
            return {"error": "该列不包含有效数值"}
        stats = {
            "count": int(col_data.count()),
            "mean": float(col_data.mean()),
            "median": float(col_data.median()),
            "max": float(col_data.max()),
            "min": float(col_data.min()),
            "std": float(col_data.std()),
            "variance": float(col_data.var())
        }
        return stats

    def calculate_correlation(self, df: pd.DataFrame) -> Dict:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            return {"error": "数值列少于2列，无法计算相关性"}
        corr_matrix = numeric_df.corr()
        columns = list(corr_matrix.columns)
        data = corr_matrix.values.tolist()
        return {"columns": columns, "data": data}

    def group_and_aggregate(self, df: pd.DataFrame, group_col: str, agg_col: str, method: str = 'sum') -> List[Dict]:
        if group_col not in df.columns or agg_col not in df.columns:
            raise ValueError("列名错误")
        if method != 'count':
            df[agg_col] = pd.to_numeric(df[agg_col], errors='coerce')
        try:
            grouped = df.groupby(group_col)[agg_col].agg(method)
            result_df = grouped.reset_index()
            result_df.columns = [group_col, f"{agg_col}_{method}"]
            return result_df.to_dict(orient='records')
        except Exception as e:
            raise RuntimeError(f"分组聚合失败: {str(e)}")

    def generate_visualization_data(self, df: pd.DataFrame, label_col: Optional[str], value_col: Optional[str],
                                    chart_type: str = 'bar'):
        if chart_type == 'heatmap':
            corr_data = self.calculate_correlation(df)
            if "error" in corr_data:
                return {"type": chart_type, "error": corr_data["error"]}
            # --- 微调部分：将相关性矩阵转换为 ECharts 需要的 [x, y, value] 格式 ---
            flat_data = []
            rows = corr_data["data"]
            cols = corr_data["columns"]
            for i, row_data in enumerate(rows):
                for j, val in enumerate(row_data):
                    # i 是行索引(对应y轴), j 是列索引(对应x轴), val 是数值
                    flat_data.append([j, i, round(val, 4)])
                    # -------------------------------------------------------------
            return {
                "type": chart_type,
                "x_axis": cols,
                "y_axis": cols,
                "data": flat_data
            }
        if not label_col or not value_col:
            raise ValueError("该图表类型需要指定 label_col 和 value_col")
        if label_col not in df.columns or value_col not in df.columns:
            raise ValueError("列名错误")
        df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
        chart_df = df.groupby(label_col)[value_col].sum().reset_index()
        chart_df = chart_df.sort_values(by=label_col)
        data = []
        if chart_type == 'pie':
            for _, row in chart_df.iterrows():
                data.append({"name": row[label_col], "value": row[value_col]})
        elif chart_type == 'line':
            for _, row in chart_df.iterrows():
                data.append([row[label_col], row[value_col]])
        elif chart_type == 'bar':
            for _, row in chart_df.iterrows():
                data.append({"name": row[label_col], "value": row[value_col]})
        else:
            raise ValueError("不支持的图表类型")
        return {
            "type": chart_type,
            "data": data,
            "xAxis": label_col,
            "yAxis": value_col
        }