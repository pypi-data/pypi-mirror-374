"""
Brief-Excel - 一个简单易用的 Excel 操作工具库

基于 openpyxl 封装，提供简洁的 API 来处理 Excel 文件的创建、读写和图片插入操作。

主要功能：
- 创建和加载 Excel 文件
- 工作表管理（添加、切换、复制、删除）
- 数据读写（单个单元格、整行、整列、区域）
- 图片插入（单张图片、多图片行插入、多图片列插入）
- 链式调用支持

示例用法：
>>> from brief_excel import BriefExcel
>>> excel = BriefExcel("test_file")
>>> excel.create().cell_write("Hello World").ws_append("Sheet2")
>>> excel.load().cell_row_read(1)
"""

try:
    from .module import BriefExcel
except ImportError:
    from module import BriefExcel

__version__ = "1.0.0"
__author__ = "hh66dw"
__all__ = ['BriefExcel', '__version__', '__author__']
