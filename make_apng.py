import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
from PIL import Image, ImageDraw, ImageFont
from apngasm_python.apngasm import APNGAsmBinder

selected_files = []
cover_file = None

# ------------------ 文件选择 ------------------
def select_files():
    global selected_files
    files = filedialog.askopenfilenames(
        title="选择图片文件（可多选）",
        filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )
    if files:
        for f in files:
            if f not in selected_files:
                selected_files.append(f)
        update_file_list()

def select_folder():
    global selected_files
    folder = filedialog.askdirectory(title="选择包含图片的文件夹")
    if folder:
        for filename in os.listdir(folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                full_path = os.path.join(folder, filename)
                if full_path not in selected_files:
                    selected_files.append(full_path)
        update_file_list()

def clear_files():
    global selected_files
    selected_files = []
    update_file_list()

def update_file_list():
    text_box.delete('1.0', tk.END)
    if not selected_files:
        text_box.insert(tk.END, "（还没有选择任何图片）")
    else:
        for idx, path in enumerate(selected_files, start=1):
            text_box.insert(tk.END, f"{idx}. {os.path.basename(path)}\n")

# ------------------ 封面相关 ------------------
def select_cover():
    global cover_file
    file = filedialog.askopenfilename(
        title="选择封面图片",
        filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )
    if file:
        cover_file = file
        update_cover_display()

def clear_cover():
    global cover_file
    cover_file = None
    update_cover_display()

def update_cover_display():
    if cover_file:
        if cover_file == os.path.join(os.path.dirname(__file__), "temp_cover.png"):
            cover_label.config(text="📝 文字封面")
        else:
            cover_label.config(text=os.path.basename(cover_file))
    else:
        cover_label.config(text="（未选择封面）")

# ------------------ 生成文字封面（带自动换行） ------------------
def generate_text_cover():
    global cover_file
    if not selected_files:
        messagebox.showwarning("提示", "请先选择至少一张图片，以确定封面尺寸")
        return

    try:
        max_width = int(size_entry.get())
        if max_width <= 0:
            raise ValueError
    except:
        messagebox.showerror("错误", "最大宽度设置无效")
        return

    # 获取统一尺寸
    first_img = Image.open(selected_files[0]).convert("RGBA")
    first_img = first_img.quantize(colors=256, method=Image.Quantize.FASTOCTREE).convert("RGBA")
    if first_img.width > max_width:
        ratio = max_width / first_img.width
        new_size = (max_width, int(first_img.height * ratio))
    else:
        new_size = first_img.size
    width, height = new_size

    text = simpledialog.askstring("输入封面文字", "请输入封面文字：", initialvalue="请下载或查看原图来查看")
    if text is None:
        return

    # 创建黑底图片
    cover_img = Image.new('RGBA', (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(cover_img)

    # 加载字体
    font = None
    font_size = int(min(width, height) / 12)
    try:
        font_paths = [
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/msyhbd.ttc",
        ]
        for fp in font_paths:
            if os.path.exists(fp):
                font = ImageFont.truetype(fp, font_size)
                break
        if font is None:
            font = ImageFont.load_default()
            messagebox.showwarning("字体警告", "未找到中文字体，使用默认字体，中文可能显示为方框")
    except:
        font = ImageFont.load_default()
        messagebox.showwarning("字体警告", "加载字体失败，使用默认字体，中文可能显示为方框")

    # 自动换行：根据宽度估算每行字符数
    try:
        bbox = draw.textbbox((0, 0), "中", font=font)
        char_width = bbox[2] - bbox[0]
    except:
        char_width = font_size * 0.8
    max_chars_per_line = max(1, int(width / char_width))
    lines = []
    for i in range(0, len(text), max_chars_per_line):
        lines.append(text[i:i+max_chars_per_line])

    total_height = len(lines) * (font_size + 5)
    y_start = (height - total_height) // 2

    for idx, line in enumerate(lines):
        y = y_start + idx * (font_size + 5)
        draw.text((width//2, y), line, fill="white", font=font, anchor="mt")

    # 保存临时封面
    temp_path = os.path.join(os.path.dirname(__file__), "temp_cover.png")
    cover_img.save(temp_path, "PNG")
    cover_file = temp_path
    update_cover_display()
    messagebox.showinfo("完成", "封面已生成并自动设置为当前封面")

# ------------------ 核心功能：生成APNG ------------------
def generate_apng():
    global selected_files, cover_file

    if not selected_files:
        messagebox.showwarning("提示", "你还没有选择任何图片，请先添加！")
        return

    try:
        delay_seconds = float(delay_entry.get())
        if delay_seconds <= 0:
            raise ValueError
    except:
        messagebox.showerror("错误", "请在“每帧秒数”框里输入一个正数，例如 0.1 或 0.5")
        return

    try:
        max_width = int(size_entry.get())
        if max_width <= 0:
            raise ValueError
    except:
        messagebox.showerror("错误", "请在“最大宽度”框里输入一个正整数，例如 800")
        return

    output_path = filedialog.asksaveasfilename(
        title="保存APNG动画为",
        defaultextension=".apng",
        filetypes=[("APNG动画", "*.apng")]
    )
    if not output_path:
        return

    try:
        gen_btn.config(state=tk.DISABLED)
        status_label.config(text="正在处理中，请稍候...")
        root.update()

        binder = APNGAsmBinder()

        # 确定统一尺寸（由 selected_files 的第一张图决定）
        base_img = Image.open(selected_files[0]).convert("RGBA")
        base_img = base_img.quantize(colors=256, method=Image.Quantize.FASTOCTREE).convert("RGBA")
        if base_img.width > max_width:
            ratio = max_width / base_img.width
            new_size = (max_width, int(base_img.height * ratio))
            base_img = base_img.resize(new_size, Image.Resampling.LANCZOS)
        target_size = base_img.size

        # 如果有封面，先添加封面
        if cover_file:
            cover_img = Image.open(cover_file).convert("RGBA")
            cover_img = cover_img.quantize(colors=256, method=Image.Quantize.FASTOCTREE).convert("RGBA")
            cover_img = cover_img.resize(target_size, Image.Resampling.LANCZOS)
            binder.add_frame_from_pillow(cover_img, delay_num=int(delay_seconds * 1000), delay_den=1000)

        # 添加所有已选图片
        for file_path in selected_files:
            img = Image.open(file_path).convert("RGBA")
            img = img.quantize(colors=256, method=Image.Quantize.FASTOCTREE).convert("RGBA")
            if img.size != target_size:
                img = img.resize(target_size, Image.Resampling.LANCZOS)
            binder.add_frame_from_pillow(img, delay_num=int(delay_seconds * 1000), delay_den=1000)
            root.update()

        binder.set_loops(0)
        binder.assemble(output_path)

        messagebox.showinfo("完成", f"APNG 制作成功！\n已保存到：\n{output_path}")
        status_label.config(text="处理完成，可以继续操作")

    except Exception as e:
        messagebox.showerror("出错了", f"制作过程中发生错误：\n{str(e)}")
        status_label.config(text="出错了，请检查图片是否损坏")
    finally:
        gen_btn.config(state=tk.NORMAL)

# ------------------ 程序退出时清理临时文件 ------------------
def on_closing():
    global cover_file
    if cover_file and cover_file == os.path.join(os.path.dirname(__file__), "temp_cover.png"):
        try:
            os.remove(cover_file)
        except:
            pass
    root.destroy()

# ------------------ 界面搭建 ------------------
root = tk.Tk()
root.title("APNG 动画制作器")
root.geometry("620x680")

# ---- 第一行：选择方式 ----
frame1 = tk.Frame(root)
frame1.pack(pady=10)

btn_select_files = tk.Button(frame1, text="📁 选择文件 (可多选)", command=select_files, width=18)
btn_select_files.pack(side=tk.LEFT, padx=5)

btn_select_folder = tk.Button(frame1, text="📂 选择文件夹", command=select_folder, width=18)
btn_select_folder.pack(side=tk.LEFT, padx=5)

btn_clear = tk.Button(frame1, text="🗑️ 清空列表", command=clear_files, width=18)
btn_clear.pack(side=tk.LEFT, padx=5)

# ---- 第二行：文件列表 ----
frame2 = tk.Frame(root)
frame2.pack(pady=5, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame2)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_box = scrolledtext.ScrolledText(frame2, height=12, yscrollcommand=scrollbar.set)
text_box.pack(fill=tk.BOTH, expand=True)
scrollbar.config(command=text_box.yview)
text_box.insert(tk.END, "（还没有选择任何图片）")

# ---- 第三行：封面选择 ----
frame_cover = tk.Frame(root)
frame_cover.pack(pady=5)

label_cover = tk.Label(frame_cover, text="封面图片：")
label_cover.pack(side=tk.LEFT, padx=5)

btn_select_cover = tk.Button(frame_cover, text="📸 选择封面", command=select_cover, width=12)
btn_select_cover.pack(side=tk.LEFT, padx=5)

btn_gen_text_cover = tk.Button(frame_cover, text="✏️ 生成文字封面", command=generate_text_cover, width=14)
btn_gen_text_cover.pack(side=tk.LEFT, padx=5)

cover_label = tk.Label(frame_cover, text="（未选择封面）", fg="gray", width=20, anchor="w")
cover_label.pack(side=tk.LEFT, padx=5)

btn_clear_cover = tk.Button(frame_cover, text="清除封面", command=clear_cover, width=10)
btn_clear_cover.pack(side=tk.LEFT, padx=5)

# ---- 第四行：延迟和宽度设置 ----
frame3 = tk.Frame(root)
frame3.pack(pady=10)

delay_frame = tk.Frame(frame3)
delay_frame.pack(pady=2)
label_delay = tk.Label(delay_frame, text="每帧停留秒数 (例如 0.1):")
label_delay.pack(side=tk.LEFT, padx=5)
delay_entry = tk.Entry(delay_frame, width=10)
delay_entry.pack(side=tk.LEFT)
delay_entry.insert(0, "0.1")

size_frame = tk.Frame(frame3)
size_frame.pack(pady=2)
label_size = tk.Label(size_frame, text="最大宽度 (像素):")
label_size.pack(side=tk.LEFT, padx=5)
size_entry = tk.Entry(size_frame, width=10)
size_entry.pack(side=tk.LEFT)
size_entry.insert(0, "800")

# ---- 第五行：生成按钮和状态 ----
frame4 = tk.Frame(root)
frame4.pack(pady=10)

gen_btn = tk.Button(frame4, text="🚀 开始生成 APNG", command=generate_apng, bg="lightblue", width=20, height=2)
gen_btn.pack()

status_label = tk.Label(root, text="就绪，请选择图片", fg="gray")
status_label.pack(pady=5)

# 初始更新
update_cover_display()

# 设置退出处理
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()