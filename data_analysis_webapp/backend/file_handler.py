import os
import uuid
import shutil
from typing import Optional
from fastapi import UploadFile, HTTPException


class FileHandler:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self._ensure_dir_exists()

    def _ensure_dir_exists(self):
        """确保上传目录存在"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    def _get_safe_filename(self, filename: str) -> str:
        """
        生成安全的文件名，防止覆盖和恶意路径
        使用 UUID 保证唯一性，保留原始扩展名
        """
        # 提取文件扩展名
        _, ext = os.path.splitext(filename)
        # 生成唯一文件名
        unique_name = f"{uuid.uuid4().hex}{ext}"
        return unique_name

    def save_upload_file(self, upload_file: UploadFile) -> tuple:
        """
        保存上传的文件
        返回: (saved_filename, file_path)
        """
        # 校验文件扩展名白名单
        allowed_extensions = {'.xlsx', '.xls', '.csv', '.json', '.txt'}
        _, ext = os.path.splitext(upload_file.filename)
        if ext.lower() not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {ext}。仅支持: {', '.join(allowed_extensions)}"
            )
        safe_filename = self._get_safe_filename(upload_file.filename)
        file_location = os.path.join(self.upload_dir, safe_filename)
        try:
            # 以二进制写入模式保存文件
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
        except Exception as e:
            # 发生IO错误时尝试清理可能残留的空文件
            if os.path.exists(file_location):
                os.remove(file_location)
            raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
        return safe_filename, file_location

    def get_file_path(self, filename: str) -> str:
        """
        根据文件名获取绝对路径
        防御路径遍历攻击
        """
        # os.path.basename 会去除路径中的目录部分，只保留文件名
        safe_filename = os.path.basename(filename)
        file_path = os.path.join(self.upload_dir, safe_filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件未找到")
        return file_path

    def delete_file(self, filename: str) -> bool:
        """删除指定文件"""
        try:
            file_path = self.get_file_path(filename)
            os.remove(file_path)
            return True
        except Exception:
            return False