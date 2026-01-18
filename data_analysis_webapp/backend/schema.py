from typing import List, Optional, Literal, Any, Dict
from pydantic import BaseModel, Field


# --- 请求模型 ---
class SortRequest(BaseModel):
    """排序请求参数"""
    filename: str = Field(..., description="目标文件名")
    column: str = Field(..., description="排序列名")
    order: Literal['asc', 'desc'] = Field(default='desc', description="排序方式：asc升序, desc降序")


class StatsRequest(BaseModel):
    """统计请求参数"""
    filename: str = Field(..., description="目标文件名")
    column: str = Field(..., description="统计列名")


class CleanRequest(BaseModel):
    """数据清洗请求参数"""
    filename: str = Field(..., description="目标文件名")


class CorrelationRequest(BaseModel):
    """相关性分析请求参数"""
    filename: str = Field(..., description="目标文件名")


class GroupRequest(BaseModel):
    """分组聚合请求参数"""
    filename: str = Field(..., description="目标文件名")
    group_col: str = Field(..., description="分组列名（类别）")
    agg_col: str = Field(..., description="数值列名")
    method: Literal['sum', 'mean', 'count', 'max', 'min'] = Field(default='sum', description="聚合方式")


class ChartRequest(BaseModel):
    """图表生成请求参数"""
    filename: str = Field(..., description="目标文件名")
    label_col: Optional[str] = Field(None, description="标签列（X轴/分类），热力图时可为空")
    value_col: Optional[str] = Field(None, description="数值列（Y轴/大小），热力图时可为空")
    # 扩展支持 line 和 heatmap
    type: Literal['bar', 'pie', 'line', 'heatmap'] = Field(default='bar', description="图表类型")


# --- 响应模型 ---
class FileUploadResponse(BaseModel):
    """文件上传响应"""
    status: str
    filename: str
    columns: List[str]
    rows: int


class AnalysisResponse(BaseModel):
    """通用分析响应基类"""
    status: str = "success"
    message: Optional[str] = None


class SortResponse(AnalysisResponse):
    """排序结果响应"""
    data: List[Dict[str, Any]]


class StatsResponse(AnalysisResponse):
    """统计结果响应"""
    stats: Dict[str, float]


class ChartResponse(AnalysisResponse):
    """图表数据响应"""
    chart_config: Dict[str, Any]


class CleanResponse(AnalysisResponse):
    """清洗结果响应"""
    original_rows: int
    cleaned_rows: int
    removed_rows: int
    preview: List[Dict[str, Any]]


class CorrelationResponse(AnalysisResponse):
    """相关性结果响应"""
    correlation: Dict[str, Any]


class GroupResponse(AnalysisResponse):
    """分组聚合结果响应"""
    data: List[Dict[str, Any]]