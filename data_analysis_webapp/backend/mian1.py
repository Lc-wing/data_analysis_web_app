from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from data_services import DataAnalysisService
from schema import (
    SortRequest, StatsRequest, ChartRequest,
    CleanRequest, CorrelationRequest, GroupRequest
)

# 导入 FileHandler，假设该类定义在项目根目录的 file_handler.py 中
# 如果 FileHandler 定义在其他位置，请相应修改 import 路径
try:
    from file_handler import FileHandler
except ImportError:
    # 如果找不到模块，这里为了演示方便打印警告，实际运行中请确保 file_handler.py 可用
    print("Warning: file_handler.py not found. Please ensure FileHandler is available.")
    raise
app = FastAPI(title="DataAnalyst API", version="1.0.0")
# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# 实例化服务类和文件处理类
# 确保 FileHandler 的 upload_dir 和 DataAnalysisService 的 upload_dir 一致
service = DataAnalysisService(upload_dir="uploads")
file_handler = FileHandler(upload_dir="uploads")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """功能1: 文件上传与存储 (使用 FileHandler)"""
    try:
        # 使用 FileHandler 保存文件，它会自动处理 UUID 重命名和扩展名校验
        saved_filename, file_path = file_handler.save_upload_file(file)
        # 解析文件前几行验证
        # 注意：file_path 已经是绝对路径，可以直接传给 load_data
        # file.filename.split('.')[-1] 用于获取原始文件的扩展名以判断格式
        df = service.load_data(file_path, file.filename.split('.')[-1])
        # 返回保存后的 UUID 文件名，供后续接口使用
        return {
            "status": "success",
            "filename": saved_filename,  # 必须返回 UUID 名称，否则后续接口找不到文件
            "original_filename": file.filename,  # 可选：保留原名供前端展示
            "columns": list(df.columns),
            "rows": len(df)
        }
    except HTTPException as he:
        # 捕获 FileHandler 抛出的异常（如文件格式不支持）
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze/clean")
async def clean_data(req: CleanRequest):
    """数据清洗接口"""
    try:
        # 使用 FileHandler 安全获取文件路径
        file_path = file_handler.get_file_path(req.filename)
        df = service.load_data(file_path, req.filename.split('.')[-1])
        result = service.clean_data(df)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze/sort")
async def sort_data(req: SortRequest):
    """数据排序接口"""
    try:
        file_path = file_handler.get_file_path(req.filename)
        df = service.load_data(file_path, req.filename.split('.')[-1])
        asc = True if req.order == "asc" else False
        result = service.sort_data(df, req.column, asc)
        return {"status": "success", "data": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze/stats")
async def get_stats(req: StatsRequest):
    """基础统计接口"""
    try:
        file_path = file_handler.get_file_path(req.filename)
        df = service.load_data(file_path, req.filename.split('.')[-1])
        result = service.calculate_statistics(df, req.column)
        return {"status": "success", "stats": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze/correlation")
async def get_correlation(req: CorrelationRequest):
    """相关性分析接口"""
    try:
        file_path = file_handler.get_file_path(req.filename)
        df = service.load_data(file_path, req.filename.split('.')[-1])
        result = service.calculate_correlation(df)
        return {"status": "success", "correlation": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze/group")
async def group_data(req: GroupRequest):
    """分组聚合接口"""
    try:
        file_path = file_handler.get_file_path(req.filename)
        df = service.load_data(file_path, req.filename.split('.')[-1])
        result = service.group_and_aggregate(df, req.group_col, req.agg_col, req.method)
        return {"status": "success", "data": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze/chart")
async def get_chart(req: ChartRequest):
    """图表生成接口 (支持 bar, pie, line, heatmap)"""
    try:
        file_path = file_handler.get_file_path(req.filename)
        df = service.load_data(file_path, req.filename.split('.')[-1])
        result = service.generate_visualization_data(df, req.label_col, req.value_col, req.type)
        return {"status": "success", "chart_config": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))