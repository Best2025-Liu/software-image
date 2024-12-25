import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, Listbox, Scrollbar, Button, Menu, Toplevel, Text
from tkinter.constants import END
import sqlite3
import os
import shutil
from PIL import Image, ImageTk
from tkinter import messagebox
import json
import tkinter.font as tkFont
from PIL import Image, UnidentifiedImageError  # 确保导入 UnidentifiedImageError

# 初始化数据库
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY,
        image_name TEXT,
        image_path TEXT,
        json_name TEXT,
        json_path TEXT,
        std_image_name TEXT,
        std_image_path TEXT,
        tag1 TEXT,
        tag2 TEXT,
        tag3 TEXT,
        tag4 TEXT,
        extend1 TEXT,
        extend2 TEXT
    )
    ''')
    conn.commit()
    conn.close()

# 标签文件路径
FILE_PATH = 'start_tags.json'

# 默认标签列表
DEFAULT_TAGS = [
    ("偏移", "pink"),
    ("少锡", "lightyellow"),
    ("多件", "lightcoral"),
    ("少件", "lightcyan"),
    ("短路", "lavender"),
    ("极反", "lightgrey"),
    ("侧立", "peachpuff"),
    ("错件", "lightpink"),
    ("空焊", "lightgoldenrod"),
    ("翘脚", "lightseagreen"),
    ("极反", "lightsalmon"),
    ("沾锡", "lightsteelblue"),
    ("立碑", "lightblue"),
    ("异物", "lightgreen"),
    ("破损", "lightyellow"),
    ("OK", "lightgreen")
]

# 静态颜色列表
STATIC_COLORS = [
    "aliceblue", "antiquewhite", "aqua", "aquamarine", "azure", "beige", "bisque",
    "black", "blanchedalmond", "blue", "blueviolet", "brown", "burlywood", "cadetblue",
    "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan",
    "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgrey", "darkgreen",
    "darkkhaki", "darkmagenta", "darkolivegreen", "darkorange", "darkorchid",
    "darkred", "darksalmon", "darkseagreen", "darkslateblue", "darkslategray",
    "darkslategrey", "darkturquoise", "darkviolet", "deeppink", "deepskyblue",
    "dimgray", "dimgrey", "dodgerblue", "firebrick", "floralwhite", "forestgreen",
    "fuchsia", "gainsboro", "ghostwhite", "gold", "goldenrod", "gray", "grey",
    "green", "greenyellow", "honeydew", "hotpink", "indianred", "indigo", "ivory",
    "khaki", "lavender", "lavenderblush", "lawngreen", "lemonchiffon", "lightblue",
    "lightcoral", "lightcyan", "lightgoldenrodyellow", "lightgray", "lightgrey",
    "lightgreen", "lightpink", "lightsalmon", "lightseagreen", "lightskyblue",
    "lightslategray", "lightslategrey", "lightsteelblue", "lightyellow", "lime",
    "limegreen", "linen", "magenta", "maroon", "mediumaquamarine", "mediumblue",
    "mediumorchid", "mediumpurple", "mediumseagreen", "mediumslateblue",
    "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue",
    "mintcream", "mistyrose", "moccasin", "navajowhite", "navy", "oldlace",
    "olive", "olivedrab", "orange", "orangered", "orchid", "palegoldenrod",
    "palegreen", "paleturquoise", "palevioletred", "papayawhip", "peachpuff",
    "peru", "pink", "plum", "powderblue", "purple", "rebeccapurple", "red",
    "rosybrown", "royalblue", "saddlebrown", "salmon", "sandybrown", "seagreen",
    "seashell", "sienna", "silver", "skyblue", "slateblue", "slategray", "slategrey",
    "snow", "springgreen", "steelblue", "tan", "teal", "thistle", "tomato",
    "turquoise", "violet", "wheat", "white", "whitesmoke", "yellow", "yellowgreen"
]



# 刷新图像列表
def refresh_image_list():
    list_images.delete(0, tk.END)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, image_name, tag1 FROM images')  # 也获取tag1
    for row in c.fetchall():
        list_images.insert(END, f"{row[0]}: {row[1]} (标签1: {row[2]})")  # 显示标签1
    conn.close()

# 加载数据库
def load_database():
    refresh_image_list()

# 清除数据库中没有对应图像的条目
def clear_database():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT image_name FROM images")
    existing_images = {row[0] for row in c.fetchall()}

    images_dir = os.path.join(project_path_global, 'images')
    for image_name in os.listdir(images_dir):
        if image_name.endswith(('.png', '.jpg', '.jpeg')):
            existing_images.discard(image_name)

    for image_name in existing_images:
        c.execute("DELETE FROM images WHERE image_name = ?", (image_name,))

    conn.commit()
    conn.close()
    refresh_image_list()
    messagebox.showinfo("信息", "已清除数据库中无对应图像的条目。")

# 退出搜索功能
def exit_search():
    refresh_image_list()

def get_paths_from_db(tag):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        # 查询带有特定标签的所有记录
        c.execute("SELECT image_path, json_path, std_image_path FROM images WHERE tag1 = ?", (tag,))
        rows = c.fetchall()

        # 将查询结果转换为字典列表，方便后续使用
        paths_list = [{'image': row[0], 'json': row[1], 'stdimage': row[2]} for row in rows]

        return paths_list
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        conn.close()

def download_images(tag):
    if not tag:
        messagebox.showwarning("警告", "未输入标签")
        return

    paths = get_paths_from_db(tag)

    if not paths:
        messagebox.showinfo("信息", "没有找到带有该标签的图像")
        return

    download_dir = filedialog.askdirectory(title="选择下载目录")
    if not download_dir:
        return

    # 创建必要的子目录
    images_dir = os.path.join(download_dir, 'images')
    jsons_dir = os.path.join(download_dir, 'jsons')
    stdimages_dir = os.path.join(download_dir, 'stdimages')

    for dir_path in [images_dir, jsons_dir, stdimages_dir]:
        os.makedirs(dir_path, exist_ok=True)

    for path_dict in paths:
        try:
            image_path = path_dict['image']
            json_path = path_dict['json']
            stdimage_path = path_dict['stdimage']

            # Check if paths are not None and files exist before copying
            if image_path and os.path.exists(image_path):
                shutil.copy(image_path, os.path.join(images_dir, os.path.basename(image_path)))
            if json_path and os.path.exists(json_path):
                shutil.copy(json_path, os.path.join(jsons_dir, os.path.basename(json_path)))
            if stdimage_path and os.path.exists(stdimage_path):
                shutil.copy(stdimage_path, os.path.join(stdimages_dir, os.path.basename(stdimage_path)))

        except FileNotFoundError as e:
            messagebox.showwarning("警告", f"文件未找到: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"发生了一个错误: {e}")
    messagebox.showinfo("完成", "所有选定的图片已成功下载！")


def add_columns_if_not_exist():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # 查询当前列名
    c.execute("PRAGMA table_info(images)")
    columns = [row[1] for row in c.fetchall()]

    # 添加 tag2, tag3, tag4 列（如果不存在）
    if 'tag2' not in columns:
        c.execute("ALTER TABLE images ADD COLUMN tag2 TEXT")
    if 'tag3' not in columns:
        c.execute("ALTER TABLE images ADD COLUMN tag3 TEXT")
    if 'tag4' not in columns:
        c.execute("ALTER TABLE images ADD COLUMN tag4 TEXT")

    conn.commit()
    conn.close()
# 加载项目
def load_project(project_path):
    global list_images, project_path_global

    # 将路径转换为绝对路径，并替换正斜杠为双反斜杠
    project_path = os.path.abspath(project_path).replace('/', '\\')
    print("Absolute Project Path:", project_path)
    project_path_global = project_path
    print("Global Project Path:", project_path_global)

    # 确保新列存在
    add_columns_if_not_exist()

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    images_dir = os.path.join(project_path, 'images').replace('/', '\\')
    jsons_dir = os.path.join(project_path, 'jsons').replace('/', '\\')
    stdimages_dir = os.path.join(project_path, 'stdimages').replace('/', '\\')

    for image_name in os.listdir(images_dir.replace('\\', '/')):  # 使用正斜杠来确保正确列出文件
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.abspath(os.path.join(images_dir.replace('\\', '/'), image_name)).replace('/', '\\')
            json_name = image_name.rsplit('.', 1)[0] + '.json'
            json_path = os.path.abspath(os.path.join(jsons_dir.replace('\\', '/'), json_name)).replace('/', '\\')
            std_image_name = image_name.rsplit('.', 1)[0] + '_std.' + image_name.rsplit('.', 1)[1]
            std_image_path = os.path.abspath(os.path.join(stdimages_dir.replace('\\', '/'), std_image_name)).replace('/', '\\')

            # 检查是否已存在记录
            c.execute('SELECT id FROM images WHERE image_name = ?', (image_name,))
            result = c.fetchone()

            # 从 JSON 文件提取 tag2, tag3, tag4
            tag2, tag3, tag4 = None, None, None
            if os.path.exists(json_path.replace('\\', '/')):  # 使用正斜杠来检查文件存在性
                try:
                    with open(json_path, 'r', encoding='utf-8') as json_file:
                        data = json.load(json_file)
                        tag2 = data.get('requestparams', {}).get('Fault')
                        tag3 = data.get('fault')
                        tag4 = data.get('real_fault')
                except json.JSONDecodeError:
                    print(f"无法解析 JSON 文件: {json_path}")
                except Exception as e:
                    print(f"读取 JSON 文件时发生错误: {e}")

            if result:
                # 更新现有记录
                c.execute('''
                UPDATE images SET image_path = ?, json_name = ?, json_path = ?, std_image_name = ?, std_image_path = ?, tag2 = ?, tag3 = ?, tag4 = ?
                WHERE id = ?
                ''', (image_path, json_name, json_path, std_image_name, std_image_path, tag2, tag3, tag4, result[0]))
                print(f"更新记录 ID {result[0]}: tag2 = {tag2}, tag3 = {tag3}, tag4 = {tag4}")
            else:
                # 插入新记录
                c.execute('''
                INSERT INTO images (image_name, image_path, json_name, json_path, std_image_name, std_image_path, tag1, tag2, tag3, tag4)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (image_name, image_path, json_name, json_path, std_image_name, std_image_path, '', tag2, tag3, tag4))

    conn.commit()
    conn.close()

    # 清空列表框并加载项目
    list_images.delete(0, END)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, image_name, tag1 FROM images')  # 也获取tag1
    for row in c.fetchall():
        list_images.insert(END, f"{row[0]}: {row[1]} (标签1: {row[2]})")  # 显示标签1
    conn.close()

class ImageViewer(tk.Toplevel):
    def __init__(self, master, image_path, std_image_path, image_name, image_id):
        super().__init__(master)
        self.image_path = image_path
        self.std_image_path = std_image_path
        self.image_name = image_name
        self.image_id = image_id
        self.title("Image Viewer ")
        self.image_id = int(image_id)
        self.scale_factor = 1.0
        self.imgid = None

        # 加载图像
        self.detection_image = Image.open(image_path)
        self.std_image = Image.open(std_image_path)
        self.concatenated_image = self.concatenate_images(self.detection_image, self.std_image)

        self.current_tag = ""
        self.geometry("1200x700")
        self.center_window()

        # 显示图像 ID 和名称
        self.info_label = tk.Label(self, text=f"图片序号: {self.image_id}, 名称: {image_name}", bg='lightgray',
                                   font=("Arial", 12))
        self.info_label.pack(fill=tk.X)

        # 创建用于显示图像的帧
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True)

        # Canvas 用于显示图像
        self.canvas = tk.Canvas(frame, bg='white')
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)

        # 创建字体对象
        button_font = tkFont.Font(size=12)  # 设定字体大小为12，可以根据需要调整

        # 按钮框架
        button_frame = tk.Frame(frame, width=200, height=700)  # 增大宽度和高度
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建一个容器来居中按钮
        center_frame = tk.Frame(button_frame)
        center_frame.pack(expand=True, padx=5, pady=5)

        # 缩放按钮
        zoom_in_button = tk.Button(center_frame, text="功能:放大", command=lambda: self.on_zoom(1.2),
                                   height=2, width=9, font=button_font, bg='lightblue')
        zoom_out_button = tk.Button(center_frame, text="功能:缩小", command=lambda: self.on_zoom(0.8),
                                    height=2, width=9, font=button_font, bg='lightgreen')
        zoom_in_button.pack(pady=5)
        zoom_out_button.pack(pady=5)

        # 标签按钮及其背景色
        tags = [
            ("偏移", "pink"),
            ("少锡", "lightyellow"),
            ("多件", "lightcoral"),
            ("少件", "lightcyan"),
            ("短路", "lavender"),
            ("极反", "lightgrey"),
            ("侧立", "peachpuff"),
            ("错件", "lightpink"),
            ("空焊", "lightgoldenrod"),
            ("翘脚", "lightseagreen"),
            ("极反", "lightsalmon"),
            ("沾锡", "lightsteelblue"),
            ("立碑", "lightblue"),
            ("异物", "lightgreen"),
            ("破损", "lightyellow"),
            ("OK", "lightgreen")
        ]

        for tag, color in tags:
            btn = tk.Button(center_frame, text=tag, command=lambda t=tag: self.add_tag(t), height=2,
                            width=9, font=button_font, bg=color)
            btn.pack(pady=2)

        # 用于显示当前标签的标签
        self.tag_label = tk.Label(self, text="标签1: ", bg='lightgray', font=("Arial", 12))
        self.tag_label.pack(fill=tk.X, pady=10)

        # 加载当前标签
        self.load_current_tag()

        # 绑定键盘事件
        self.bind("<Key>", self.on_key_press)

        # 调整窗口大小时更新图像
        self.bind("<Configure>", self.on_resize)

        # 添加鼠标拖拽功能
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)

        # 显示初始图像
        self.update_image()

    def on_key_press(self, event):
        if event.keysym == 'Up':
            self.load_image(self.image_id - 1)  # 加载上一条记录
        elif event.keysym == 'Down':
            self.load_image(self.image_id + 1)  # 加载下一条记录

    def load_image(self, new_image_id):
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("SELECT image_name, image_path, std_image_path, tag1 FROM images WHERE id = ?", (new_image_id,))
            result = c.fetchone()

            if result:
                image_name, image_path, std_image_path, tag1 = result
                self.image_id = new_image_id

                # 检查文件是否存在
                if not os.path.exists(image_path) or not os.path.exists(std_image_path):
                    raise FileNotFoundError(f"指定路径下的文件不存在: {image_path} 或 {std_image_path}")

                # 尝试打开图像文件
                self.detection_image = Image.open(image_path)
                self.std_image = Image.open(std_image_path)

                # 拼接图像
                self.concatenated_image = self.concatenate_images(self.detection_image, self.std_image)

                # 更新UI元素
                self.info_label.config(text=f"图片序号: {self.image_id}, 名称: {image_name}")
                self.current_tag = tag1
                self.update_tag_display()
                self.update_image()

            else:
                messagebox.showwarning("警告", "超出数据库的查询范围!")

        except FileNotFoundError as e:
            messagebox.showwarning("文件不存在", str(e))
        except UnidentifiedImageError:
            messagebox.showwarning("无法识别图像文件",
                                   f"PIL 无法识别图像文件，请检查文件{image_path}是否损坏或格式不支持。")
        except Exception as e:
            messagebox.showwarning("发生未知错误", f"加载图像时发生了一个未知错误: {e}")
        finally:
            # 确保数据库连接关闭
            conn.close()

    def load_current_tag(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT tag1 FROM images WHERE id = ?", (self.image_id,))
        result = c.fetchone()

        # 检查 result 是否为 None 或空
        if result is None or len(result) == 0:
            self.current_tag = ""
        else:
            self.current_tag = result[0] if result[0] is not None else ""

        conn.close()
        self.update_tag_display()

    def update_tag_display(self):
        # 从数据库中获取 tag2, tag3, tag4
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT tag2, tag3, tag4 FROM images WHERE id = ?', (self.image_id,))
        result = c.fetchone()

        if result:
            tag2, tag3, tag4 = result
            self.tag_label.config(text=f"AOI结果: {tag2}，   人复判结果: {tag4}，   AI结果: {tag3}，   标签1: {self.current_tag}")
        else:
            self.tag_label.config(text=f"AOI结果: 无，人复判结果: 无，AI结果: 无，标签1: {self.current_tag}")

        conn.close()

    def add_tag(self, tag):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute("UPDATE images SET tag1 = ? WHERE id = ?", (tag, self.image_id))
            conn.commit()
            self.load_current_tag()
        except Exception as e:
            messagebox.showerror("错误", "未能添加标签!")
        finally:
            conn.close()

    def center_window(self):
        window_width = 1200
        window_height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

    def concatenate_images(self, img1, img2):
        # 确保两个图像都转换为 'RGB' 模式以确保兼容性
        img1 = img1.convert('RGB')
        img2 = img2.convert('RGB')

        width1, height1 = img1.size
        width2, height2 = img2.size
        new_height = max(height1, height2)

        # 使用绿色 (0, 255, 0) 作为背景颜色创建新的图像
        new_image = Image.new('RGB', (width1 + width2, new_height), (0, 255, 0))

        new_image.paste(img1, (0, 0))
        new_image.paste(img2, (width1, 0))

        return new_image

    def update_image(self):
        canvas_width = self.canvas.winfo_width()
        if canvas_width > 0:
            new_width = int(self.concatenated_image.width * self.scale_factor)
            new_height = int(self.concatenated_image.height * self.scale_factor)

            if new_width > 0 and new_height > 0:
                resized_image = self.concatenated_image.resize((new_width, new_height), Image.LANCZOS)
                self.image_tk = ImageTk.PhotoImage(resized_image)

                if self.imgid is not None:
                    self.canvas.delete(self.imgid)

                x_pos = (self.canvas.winfo_width() - new_width) // 2
                y_pos = (self.canvas.winfo_height() - new_height) // 2

                self.imgid = self.canvas.create_image(x_pos, y_pos, image=self.image_tk, anchor='nw')

    def on_zoom(self, factor):
        self.scale_factor *= factor
        self.update_image()

    def on_resize(self, event):
        self.update_image()

    def on_drag_start(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag_motion(self, event):
        delta_x = event.x - self.drag_start_x
        delta_y = event.y - self.drag_start_y
        self.canvas.move(self.imgid, delta_x, delta_y)
        self.drag_start_x = event.x
        self.drag_start_y = event.y

# 辅助函数：根据给定的扩展名列表分割图像路径
def _split_image_path(item, extensions):
    for ext in extensions:
        temp_parts = item.strip().split(ext, 1)
        if len(temp_parts) > 1:
            return temp_parts[0].strip() + ext, True
    return item.strip(), False


def fetch_image_data(image_id):
    """
    根据 image_id 从数据库中获取图片的相关信息。

    :param image_id: 图片的 ID。
    :return: 包含图片路径和其他相关信息的元组，如果没有找到则返回 None。
    """
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT image_name, image_path, std_image_path FROM images WHERE id=?", (image_id,))
    result = c.fetchone()
    conn.close()
    return result


def show_image(event):
    global popup_window

    selection = list_images.curselection()
    if selection:
        index = selection[0]
        item = list_images.get(index)

        # 使用maxsplit=1来确保只拆分一次
        parts = item.split(':', 1)
        if len(parts) == 2:
            try:
                image_id = int(parts[0].strip())  # 假设ID是整数

                # 从数据库中获取图片路径
                image_data = fetch_image_data(image_id)
                if not image_data:
                    messagebox.showwarning("警告", "选择的项在数据库中不存在!")
                    return

                image_name, image_path, std_image_path = image_data

                print(f"尝试打开图片：{image_path}")  # Debug 输出
                print(f"尝试打开标准图片：{std_image_path}")

                if 'popup_window' in globals():
                    popup_window.destroy()

                try:
                    popup_window = ImageViewer(root, image_path, std_image_path, image_name=image_name,
                                               image_id=image_id)

                except Exception as e:
                    messagebox.showerror("错误", f"无法打开图片: {e}，请注意标准图目录的路径是不是stdimages？")
            except ValueError:
                messagebox.showwarning("警告", "选择的项包含无效的图片ID!")
        else:
            messagebox.showwarning("警告", "选择的项格式错误!")

def search_images():
    query = simpledialog.askstring("搜索", "输入搜索关键词:")
    if query:
        list_images.delete(0, END)
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id, image_name FROM images WHERE image_name LIKE ?", ('%' + query + '%',))
        for row in c.fetchall():
            list_images.insert(END, f"{row[0]}: {row[1]}")
        conn.close()

def delete_filtered_images():
    # 选择源目录
    source_dir = filedialog.askdirectory(title="选择源文件的目录")
    if not source_dir:
        print("没有选择源目录")
        return

    # 选择目标目录
    target_dir = filedialog.askdirectory(title="选择目标文件的目录")
    if not target_dir:
        print("没有选择目标目录")
        return

    # 定义子目录名称
    subdirs = ['images', 'jsons', 'stdimages']

    # 遍历每个子目录
    for subdir in subdirs:
        source_subdir_path = os.path.join(source_dir, subdir)
        target_subdir_path = os.path.join(target_dir, subdir)

        # 检查子目录是否存在
        if not (os.path.exists(source_subdir_path) and os.path.exists(target_subdir_path)):
            print(f"源或目标目录下不存在{subdir}子目录")
            continue

        # 获取源目录下的所有文件名（不包含路径）
        source_files = set(os.listdir(source_subdir_path))

        # 删除目标目录中与源目录同名的文件
        for filename in os.listdir(target_subdir_path):
            if filename in source_files:
                file_path = os.path.join(target_subdir_path, filename)
                try:
                    os.remove(file_path)
                    print(f"已删除: {file_path}")
                except Exception as e:
                    print(f"删除失败: {file_path}, 错误信息: {e}")

    print("操作完成")

# 自动管理图片的功能
def auto_manage_images():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # 查询所有不同的 tag1
    c.execute("SELECT DISTINCT tag1 FROM images")
    tags = c.fetchall()

    for tag_tuple in tags:
        tag = tag_tuple[0]
        if tag:  # 只处理非空字符串的标签
            # 创建目录
            directory_path = os.path.join(os.getcwd(), tag)
            images_dir = os.path.join(directory_path, 'images')
            jsons_dir = os.path.join(directory_path, 'jsons')
            stdimages_dir = os.path.join(directory_path, 'stdimages')

            # 创建子目录
            os.makedirs(images_dir, exist_ok=True)
            os.makedirs(jsons_dir, exist_ok=True)
            os.makedirs(stdimages_dir, exist_ok=True)

            # 获取所有具有该 tag1 的图像路径
            c.execute("SELECT image_path, json_path, std_image_path FROM images WHERE tag1 = ?", (tag,))
            image_paths = c.fetchall()
            print(image_paths)

            for image_path_tuple in image_paths:
                image_path, json_path, std_image_path = image_path_tuple

                # 调试输出：打印每个路径
                print(f"处理标签: {tag}")
                print(f"图像路径: {image_path}")
                print(f"JSON路径: {json_path}")
                print(f"标准图像路径: {std_image_path}")

                # 复制文件到新目录
                if image_path and os.path.exists(image_path):
                    target_image_path = os.path.join(images_dir, os.path.basename(image_path))
                    print(f"复制图像: {image_path} 到 {target_image_path}")
                    shutil.copy(image_path, target_image_path)
                else:
                    print(f"图像文件不存在: {image_path}")

                if json_path and os.path.exists(json_path):
                    target_json_path = os.path.join(jsons_dir, os.path.basename(json_path))
                    print(f"复制 JSON: {json_path} 到 {target_json_path}")
                    shutil.copy(json_path, target_json_path)

                if std_image_path and os.path.exists(std_image_path):
                    target_std_image_path = os.path.join(stdimages_dir, os.path.basename(std_image_path))
                    print(f"复制标准图像: {std_image_path} 到 {target_std_image_path}")
                    shutil.copy(std_image_path, target_std_image_path)

    conn.close()
    messagebox.showinfo("完成", "图片管理完成！")


# 主窗口
root = tk.Tk()
root.title("图片查看与打标签软件 图片对比 标签工具V1.3 小窗版本1200X700  Build241223")
root.geometry("1200x700")


def prompt_for_license_key(attempts=3):
    while attempts > 0:
        # 计算输入框位置，使其居中
        x = root.winfo_x() + (root.winfo_width() // 2) - 100  # 输入框宽度的一半
        y = root.winfo_y() + (root.winfo_height() // 2) - 50  # 输入框高度的一半

        # 创建一个简单对话框，要求用户输入授权码
        license_key = simpledialog.askstring("授权码", "请输入您的授权码:", parent=root)


        # 检查授权码
        if license_key is None or license_key.strip() == "":  # 用户点击了取消或输入为空
            messagebox.showerror("错误", "未输入授权码，程序将退出。")
            root.destroy()  # 退出程序
            return
        elif license_key != "谁":  # 替换为您实际的授权码
            attempts -= 1
            if attempts > 0:
                messagebox.showwarning("警告", f"授权码无效！您还有 {attempts} 次机会。")
            else:
                messagebox.showerror("错误", "授权码无效，您已用完所有机会。程序将退出。")
                root.destroy()  # 退出程序
        else:
            messagebox.showinfo("成功", "授权码验证成功！")
            return  # 验证成功，退出循环

# 显示授权码输入框
prompt_for_license_key()

# 菜单栏
menubar = tk.Menu(root)
root.config(menu=menubar)

# 文件菜单
file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="文件", menu=file_menu)
file_menu.add_command(label="打开项目", command=lambda: load_project(filedialog.askdirectory()))
file_menu.add_command(label="加载数据库", command=load_database)
file_menu.add_command(label="清除数据库", command=clear_database)
file_menu.add_separator()
file_menu.add_command(label="退出", command=root.quit)

# 操作菜单
action_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="操作", menu=action_menu)
action_menu.add_command(label="下载图片", command=lambda: download_images(simpledialog.askstring("输入", "输入标签:")))
action_menu.add_command(label="搜索图片", command=search_images)
action_menu.add_command(label="退出搜索", command=exit_search)
action_menu.add_command(label="自动管理图片", command=auto_manage_images)

# 筛选菜单
filter_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="筛选", menu=filter_menu)
filter_menu.add_command(label="筛选删除图片", command=delete_filtered_images)

# 列表框
# 创建垂直滚动条
yscrollbar = tk.Scrollbar(root)
yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
# 创建水平滚动条
xscrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL)
xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
# 创建列表框，并同时设置垂直和水平滚动条命令
list_images = tk.Listbox(root, yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
list_images.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
# 配置垂直滚动条以控制列表框的垂直滚动
yscrollbar.config(command=list_images.yview)
# 配置水平滚动条以控制列表框的水平滚动
xscrollbar.config(command=list_images.xview)
# 绑定选择事件到 show_image 函数
list_images.bind('<<ListboxSelect>>', show_image)

# 初始化数据库和全局变量
init_db()
project_path_global = ''

# 启动主循环
root.mainloop()

