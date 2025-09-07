# DepChecker

一个轻量级的Python库，用于快速检测和安装项目所需的依赖包。

## 功能特性

- ✅ **依赖检测** - 检查包是否安装及版本是否符合要求
- 🔧 **自动安装** - 一键安装所有缺失或需要更新的包
- 📊 **详细报告** - 清晰的检查结果和状态显示
- 🚀 **简单易用** - 提供类接口和便捷函数两种使用方式
- 🔄 **版本控制** - 支持最低版本要求检查

## 安装

```bash
pip install depchecker
```

## 快速开始

### 方式一：使用便捷函数

```python
from depchecker import quick_check

# 定义项目依赖
REQUIREMENTS = {
    "requests": "2.31.0",
    "numpy": "1.21.0", 
    "pandas": "1.3.0",
    "matplotlib": "3.4.0"
}

# 快速检查并自动安装
ready = quick_check(REQUIREMENTS, auto_install=True, verbose=True)

if ready:
    print("✅ 环境准备就绪！")
else:
    print("❌ 环境准备失败")
```

### 方式二：使用类接口

```python
from depchecker import DependencyChecker

# 创建检测器实例
checker = DependencyChecker({
    "flask": "2.0.0",
    "sqlalchemy": "1.4.0",
    "redis": "4.0.0"
})

# 检查所有依赖
results = checker.check_all()
print("检查结果:", results)

# 安装缺失的包
if not checker.is_ready():
    checker.install_all(verbose=True)
```

## API 参考

### `DependencyChecker` 类

#### `__init__(requirements: Dict[str, str])`
初始化依赖检测器。

- `requirements`: 依赖包字典，格式为 `{包名: 最低版本}`

#### `check_package(package_name: str, min_version: Optional[str] = None) -> Tuple[bool, str, str]`
检查单个包的安装状态。

- 返回: `(是否安装, 当前版本, 状态信息)`

#### `check_all() -> Dict[str, Tuple[bool, str, str]]`
检查所有要求的依赖包。

- 返回: 字典格式的检查结果 `{包名: (是否安装, 版本, 状态)}`

#### `install_all(verbose: bool = False) -> Dict[str, bool]`
安装所有缺失和需要更新的包。

- 返回: 安装结果字典 `{包名: 是否成功}`

#### `is_ready() -> bool`
检查所有依赖是否都已满足。

### `quick_check(requirements: Dict[str, str], auto_install: bool = False, verbose: bool = False) -> bool`
快速检查依赖的便捷函数。

- `auto_install`: 是否自动安装缺失的包
- `verbose`: 是否显示详细输出
- 返回: 所有依赖是否就绪

## 示例输出

```
📦 依赖库检查:
--------------------------------------------------
requests      2.28.0       ✓ (需要: 2.31.0+)
numpy         1.20.0       ✗ 需要版本 >= 1.21.0 (需要: 1.21.0+)
pandas        未安装       ✗ (需要: 1.3.0+)
--------------------------------------------------
🔧 自动安装缺失的库...
安装 numpy>=1.21.0...
✓ numpy 安装成功
安装 pandas>=1.3.0...
✓ pandas 安装成功
🎉 所有依赖库安装完成！
✅ 环境准备就绪，可以开始开发！
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 支持版本

- Python 3.7+
- 支持 Windows、macOS、Linux