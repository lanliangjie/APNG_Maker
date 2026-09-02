# APNG Maker

一个基于 Python + tkinter 的可视化 APNG 动图生成工具，支持多图/文件夹导入、自定义封面、文字封面、帧延迟设置和输出宽度控制，并支持打包为独立的 `.exe` 应用程序。

## 功能特性

- ✅ 多图选择（支持 `png/jpg/jpeg/bmp/gif`）
- ✅ 文件夹批量导入（自动过滤图片文件）
- ✅ 自定义封面图片
- ✅ **生成文字封面**（支持中文字体、自动换行、居中显示）
- ✅ 自定义每帧停留时长（秒）
- ✅ 自定义输出最大宽度（高度自适应）
- ✅ 实时显示已选文件列表
- ✅ 打包为独立 `.exe` 文件，无需 Python 环境即可运行

## 依赖安装

本项目依赖以下 Python 库：

```bash
pip install pillow
pip install apngasm-python
```

> 注：`tkinter` 是 Python 标准库，无需额外安装。

## 使用方法

1. 点击 **“选择文件”** 或 **“选择文件夹”** 添加图片
2. （可选）点击 **“选择封面”** 或 **“生成文字封面”** 自定义首帧
3. 设置 **“每帧停留秒数”**（如 `0.1`）和 **“最大宽度”**（如 `800`）
4. 点击 **“开始生成 APNG”**，选择保存路径即可

## 打包为 exe

在项目根目录下执行：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name APNG_Maker main.py
```

生成的 `.exe` 文件位于 `dist/` 目录下。

## 文件结构

```
.
├── main.py          # 主程序入口
├── README.md        # 项目说明
└── requirements.txt # 依赖列表（可选）
```

## 运行截图

![Uploading 运行截图.png…]()

## 许可证

MIT License
