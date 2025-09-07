# Brief Excel

一个强大的Python Excel处理工具包，基于openpyxl封装，提供简洁的API来处理Excel文件的创建、读写和图片插入操作。

## 功能特性

- ✅ 创建和加载Excel文件
- ✅ 工作表管理（创建、定位、移动、复制、删除）
- ✅ 单元格操作（读写单个单元格）
- ✅ 行操作（读写整行数据）
- ✅ 列操作（读写整列数据）
- ✅ 区域操作（读写指定区域数据）
- ✅ 图片插入（支持单张图片、行插入、列插入、URL图片插入）
- ✅ 高级样式设置（字体、颜色、边框、对齐）
- ✅ 公式支持
- ✅ 条件格式
- ✅ 自动创建目录结构
- ✅ 链式调用语法

## 安装

从pip安装：

```bash
pip install brief_excel
```

## 快速开始

### 基本使用

```python
from brief_excel import BriefExcel

# 创建Excel对象
excel = BriefExcel(name="example", pic_paths=["image1.jpg", "image2.png"])

# 创建Excel文件
excel.create("my_file", row=1, col=1)

# 写入数据
excel.cell_location(1, 1).cell_write("Hello World")
excel.cell_row_write(2, 1, ["Data1", "Data2", "Data3"])
excel.cell_col_write(3, 1, ["Col1", "Col2", "Col3"])

# 插入图片
excel.insert_pic(5, 1, "image1.jpg")
excel.insert_pic_row(7, 1, ["image1.jpg", "image2.png"])
```

### 高级功能示例

```python
from brief_excel import BriefExcel

# 1. 创建Excel实例
excel = BriefExcel(name="sales_report", pic_paths=["./images/chart1.png", "./images/chart2.png"])

# 2. 创建新文件
excel.create("monthly_report", row=1, col=1)

# 3. 添加工作表
excel.ws_append("Summary", 2)  # 添加2个名为Summary的工作表
excel.ws_append("Details", 1)  # 添加1个名为Details的工作表

# 4. 切换到指定工作表
excel.ws_location("Summary")  # 按名称切换
excel.ws_location(0)         # 按索引切换

# 5. 写入数据
# 单个单元格
excel.cell_location(1, 1).cell_write("销售报表")

# 整行数据
excel.cell_row_write(2, 1, ["产品", "数量", "单价", "总价"])

# 整列数据  
excel.cell_col_write(3, 1, ["产品A", "产品B", "产品C"])

# 区域数据
data = [
    ["2024-01", 100, 50, 5000],
    ["2024-02", 120, 55, 6600],
    ["2024-03", 150, 60, 9000]
]
excel.cell_area_write(3, 2, length=4, width=3, datas=data)

# 6. 设置样式
excel.set_cell_style(1, 1, font_name="Arial", font_size=14, font_bold=True, bg_color="FFCC00", align="center")
excel.set_column_width(1, 20)
excel.set_row_height(1, 30)
excel.set_number_format(4, 3, "¥#,##0.00")

# 7. 设置公式
excel.set_formula(7, 4, "=SUM(D3:D6)")
excel.set_formula(8, 4, "=AVERAGE(D3:D6)")

# 8. 插入图片
excel.insert_pic(10, 1, "./images/chart1.png", width=800, height=600)
excel.insert_pic_row(12, 1, ["./images/chart1.png", "./images/chart2.png"])

# 9. 从URL插入图片
excel.insert_pic_from_url(15, 1, "https://example.com/image.jpg", max_width=200)

# 10. 加载现有文件并读取数据
excel2 = BriefExcel()
try:
    excel2.load("monthly_report")  # 加载之前创建的文件
    excel2.cell_row_read(2)  # 读取第二行数据
    print(f"第二行数据: {excel2.pending_data}")
except FileNotFoundError:
    print("文件不存在，请先创建文件")
except Exception as e:
    print(f"文件加载失败: {e}")
```

## API文档

### BriefExcel 类

主要的Excel操作类，支持链式调用。

#### 初始化
- `__init__(name: str = None, pic_paths: list = None)`: 构造函数，可设置文件名和图片路径
- `set_name(name: str)`: 设置文件名
- `set_pic_paths(pic_paths: list)`: 设置图片路径

#### 文件操作
- `create(fpn: str = None, row: int = 15, col: int = 15)`: 创建新Excel文件
- `load(fpn: str = None, row: int = 1, col: int = 1)`: 加载现有Excel文件（支持文件存在性检查）

#### 工作表操作
- `ws_append(name: str = 'Sheet', num: int = 1)`: 添加工作表
- `ws_location(title_or_num)`: 定位到指定工作表（按名称或索引）
- `ws_move(num: int)`: 移动当前工作表位置
- `ws_copy(title_or_num)`: 复制工作表
- `ws_delete()`: 删除当前工作表

#### 数据操作
- `cell_location(row, col: int = 0)`: 定位到指定单元格
- `cell_write(data: str)`: 写入单个单元格数据
- `cell_row_write(row, col: int = 0, datas: list = None)`: 写入整行数据
- `cell_row_read(row)`: 读取整行数据
- `cell_col_write(row, col: int = 0, datas: list = None)`: 写入整列数据
- `cell_col_read(col)`: 读取整列数据
- `cell_area_write(row, col: int = 0, length: int = 2, width: int = 2, datas: list = None)`: 写入区域数据
- `cell_area_read(row, col: int = 0, length: int = 2, width: int = 2)`: 读取区域数据

#### 图片操作
- `insert_pic(row: int, col: int = 0, path: str = None, width: int = 720, height: int = 1280)`: 插入单张图片
- `insert_pic_row(row: int, col: int = 0, paths: str = None, width: int = 720, height: int = 1280)`: 在行中插入多张图片
- `insert_pic_col(row: int, col: int = 0, paths: str = None, width: int = 720, height: int = 1280)`: 在列中插入多张图片
- `insert_pic_from_url(row: int, col: int = 0, url: str = None, max_width: int = None, max_height: int = None)`: 从URL插入图片
- `insert_pic_advanced(row: int, col: int = 0, path: str = None, max_width: int = None, max_height: int = None, scale: float = 1.0, keep_aspect_ratio: bool = True)`: 高级图片插入功能

#### 样式和格式操作
- `set_cell_style(row: int, col: int, font_name: str = None, font_size: int = None, font_bold: bool = False, bg_color: str = None, font_color: str = None, border: bool = False, align: str = None)`: 设置单元格样式
- `set_column_width(col: int, width: float)`: 设置列宽
- `set_row_height(row: int, height: float)`: 设置行高
- `set_number_format(row: int, col: int, format_str: str)`: 设置数字格式
- `merge_cells(range_str: str)`: 合并单元格
- `freeze_panes(row: int = None, col: int = None)`: 冻结窗格
- `apply_conditional_formatting(range_str: str, formula: str, bg_color: str = None, font_color: str = None)`: 应用条件格式
- `set_formula(row: int, col: int, formula: str)`: 设置单元格公式

## 项目结构

```
brief_excel/           # 项目根目录
├── src/              # 源代码目录
│   └── brief_excel/   # 包目录
│       ├── __init__.py     # 包初始化文件
│       └── module.py       # 主代码模块
├── tests/            # 测试目录
│   ├── final_test.py       # 综合测试文件
│   └── test_images/        # 测试图片资源目录
├── pyproject.toml    # 现代打包配置文件
├── README.md         # 项目说明文档
├── LICENSE           # 许可证文件
├── .gitignore        # Git忽略文件
├── requirements.txt  # 开发依赖文件
└── data/             # 自动生成的Excel文件存储目录
```

## 注意事项

1. Excel文件默认保存在 `data/` 目录下
2. 插入图片时，图片路径需要是绝对路径或相对于项目根目录的相对路径
3. 所有操作都支持链式调用
4. 文件操作会自动处理目录创建和非法字符替换
5. URL图片插入功能需要安装 `requests` 库
6. 高级图片处理功能需要安装 `Pillow` 库

## 测试

项目包含完整的测试套件，运行以下命令进行测试：

```bash
python -m unittest discover tests
```

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。在提交代码前请确保：
1. 所有现有测试通过
2. 新增功能包含相应的测试用例
3. 代码风格符合项目规范

## 许可证

MIT License

## 版本信息

当前版本: 1.0.0
Python要求: >= 3.7
