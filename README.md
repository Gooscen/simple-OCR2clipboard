# 屏幕 OCR 识别工具

## 以下是 ai 生成的，其实还没开发出来这些功能，但我困了，醒了再改

一个基于 Tesseract OCR 的屏幕文字识别工具，支持中英文混合识别，可以快速截取屏幕区域并识别其中的文字。

## 主要特性

- 🖱️ 鼠标拖拽选择识别区域
- 🔤 支持中英文混合文字识别
- ⌨️ 全局热键支持 (F9)
- 📋 自动复制识别结果到剪贴板
- 🖼️ 图像预处理优化识别准确率
- 💻 跨平台支持 (macOS/Linux/Windows)

## 快速开始

### 1. 自动安装依赖

运行安装脚本自动安装所有依赖：

```bash
python install_dependencies.py
```

### 2. 手动安装依赖

如果自动安装失败，可以手动安装：

#### macOS

```bash
# 安装Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Tesseract和中文语言包
brew install tesseract tesseract-lang

# 安装Python依赖
pip install pytesseract keyboard pyautogui pyperclip pillow numpy
```

#### Linux (Ubuntu/Debian)

```bash
# 安装Tesseract和中文语言包
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# 安装Python依赖
pip install pytesseract keyboard pyautogui pyperclip pillow numpy
```

#### Windows

1. 下载 Tesseract Windows 安装程序: https://github.com/UB-Mannheim/tesseract/wiki
2. 安装时确保选择中文语言包
3. 将 Tesseract 路径添加到系统 PATH
4. 安装 Python 依赖: `pip install pytesseract keyboard pyautogui pyperclip pillow numpy`

### 3. 运行应用

```bash
python screen_ocr_app.py
```

## 使用方法

### 图形界面模式

1. 运行程序后会打开图形界面
2. 点击"开始识别"按钮
3. 拖拽鼠标选择需要识别的屏幕区域
4. 松开鼠标后自动进行 OCR 识别
5. 识别结果会显示在界面中并自动复制到剪贴板

### 热键模式

1. 程序运行后，按 `F9` 键快速开始识别
2. 其他步骤与图形界面模式相同

## 功能说明

### OCR 识别

- 使用 Tesseract OCR 引擎
- 支持中文简体和英文混合识别
- 自动图像预处理(灰度化)提高识别准确率
- 智能降级：如果中文识别失败，自动切换到英文识别

### 屏幕选择

- 全屏截图覆盖层
- 实时矩形选择框
- 最小选择区域限制
- ESC 键取消选择

### 结果处理

- 自动去除空行和多余空白
- 结果自动复制到剪贴板
- 界面显示识别统计信息
- 支持清空结果功能

## 常见问题

### Q: 提示找不到 Tesseract 命令

A: 请确保 Tesseract 已正确安装并添加到系统 PATH，或运行安装脚本自动配置。

### Q: 中文识别效果不好

A: 请确保安装了中文语言包 (chi_sim)，并选择清晰的文字区域。

### Q: macOS 权限问题

A:

1. 系统偏好设置 → 安全性与隐私 → 隐私
2. 在"屏幕录制"中添加终端或 Python
3. 在"辅助功能"中添加终端或 Python

### Q: Linux 热键不工作

A: 请确保当前用户有足够权限访问输入设备，可能需要以 root 权限运行。

## 技术架构

- **OCR 引擎**: Tesseract OCR
- **GUI 框架**: Tkinter
- **图像处理**: PIL/Pillow
- **屏幕截图**: PyAutoGUI
- **全局热键**: keyboard
- **剪贴板**: pyperclip

## 系统要求

- Python 3.6+
- Tesseract OCR 4.0+
- 支持的操作系统: macOS 10.12+, Ubuntu 16.04+, Windows 10+

## 许可证

MIT License

## 更新日志

### v2.0.0

- 🔄 替换 PaddleOCR 为 Tesseract OCR
- ⚡ 提升启动速度和稳定性
- 🛠️ 优化图像预处理流程
- 📦 简化依赖安装
- 🐛 修复 macOS 兼容性问题

---

**版本**: 2.0.0  
**更新日期**: 2025 年 6 月  
**作者**: Claude AI Assistant
