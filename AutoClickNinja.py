import tkinter as tk
from tkinter import ttk, messagebox
import win32gui
import win32api
import win32con
import keyboard
import threading
import time
import pygetwindow as gw
import mouse


class AutoClickTool:
    def __init__(self, root):
        self.root = root
        self.root.title("智能后台点击工具")
        self.running = False
        self.target_window = None
        self.click_thread = None
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self.root, text="目标窗口:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.window_entry = ttk.Entry(self.root, width=30)
        self.window_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="选择窗口", command=self.select_window).grid(row=0, column=2, padx=5, pady=5)

        self.coord_method = tk.StringVar(value="manual")
        ttk.Label(self.root, text="坐标获取方式:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(self.root, text="手动输入", variable=self.coord_method, value="manual").grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(self.root, text="点击获取", variable=self.coord_method, value="click").grid(row=1, column=2, sticky="w")

        ttk.Label(self.root, text="点击坐标(X,Y):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.pos_x = ttk.Spinbox(self.root, from_=0, to=9999, width=8)
        self.pos_x.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.pos_y = ttk.Spinbox(self.root, from_=0, to=9999, width=8)
        self.pos_y.grid(row=2, column=1, padx=5, pady=5, sticky="e")
        ttk.Button(self.root, text="获取坐标", command=self.get_coordinates).grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(self.root, text="点击间隔(秒):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.interval = ttk.Spinbox(self.root, from_=0.1, to=60, increment=0.1, width=8)
        self.interval.set(1.0)
        self.interval.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(self.root, text="开始(F10)", command=self.start_clicking).grid(row=4, column=0, padx=5, pady=10)
        ttk.Button(self.root, text="停止(F10)", command=self.stop_clicking).grid(row=4, column=1, padx=5, pady=10)

        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪 - 按F10开始/停止")
        ttk.Label(self.root, textvariable=self.status_var).grid(row=5, column=0, columnspan=3, pady=5)

        keyboard.add_hotkey('f10', self.toggle_clicking)

        self.pos_x.set(100)
        self.pos_y.set(100)

    def select_window(self):
        try:
            windows = gw.getAllTitles()
            select_win = tk.Toplevel(self.root)
            select_win.title("选择窗口")

            tree = ttk.Treeview(select_win, columns=("title",), show="headings")
            tree.heading("title", text="窗口标题")
            tree.column("title", width=300)

            for title in windows:
                if title:
                    tree.insert("", "end", values=(title,))

            tree.pack(fill="both", expand=True)

            def on_select():
                selected = tree.focus()
                if selected:
                    title = tree.item(selected, "values")[0]
                    self.target_window = gw.getWindowsWithTitle(title)[0]
                    self.window_entry.delete(0, tk.END)
                    self.window_entry.insert(0, title)
                    select_win.destroy()
                    self.status_var.set(f"已选择窗口: {title}")

            ttk.Button(select_win, text="选择", command=on_select).pack(pady=5)

        except Exception as e:
            messagebox.showerror("错误", f"获取窗口列表失败: {str(e)}")

    def get_coordinates(self):
        if not self.target_window:
            messagebox.showwarning("警告", "请先选择目标窗口！")
            return

        if self.coord_method.get() == "click":
            threading.Thread(target=self.get_coordinates_by_click, daemon=True).start()

    def get_coordinates_by_click(self):
        """通过点击获取坐标 - 非阻塞、线程安全版本"""
        if not self.target_window:
            return

        self.status_var.set("请点击目标窗口获取坐标...")
        self.root.update()

        try:
            rect = win32gui.GetWindowRect(self.target_window._hWnd)
            left, top = rect[0], rect[1]

            def on_click():
                try:
                    abs_x, abs_y = win32api.GetCursorPos()
                    rel_x = abs_x - left
                    rel_y = abs_y - top

                    if 0 <= rel_x <= rect[2] - rect[0] and 0 <= rel_y <= rect[3] - rect[1]:
                        self.pos_x.set(rel_x)
                        self.pos_y.set(rel_y)
                        self.status_var.set(f"已记录坐标: ({rel_x}, {rel_y})")
                    else:
                        self.status_var.set("点击超出窗口区域")
                finally:
                    mouse.unhook_all()

            mouse.unhook_all()
            mouse.on_click(on_click)
        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")

    def send_click(self, x, y):
        if not self.target_window:
            return False
        try:
            hwnd = self.target_window._hWnd
            lParam = win32api.MAKELONG(x, y)
            win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
            win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
            return True
        except:
            return False

    def click_loop(self):
        while self.running:
            try:
                x = int(self.pos_x.get())
                y = int(self.pos_y.get())

                if self.send_click(x, y):
                    self.status_var.set(f"点击中: ({x}, {y})")
                else:
                    self.status_var.set("点击失败 - 窗口可能已关闭")
                    self.running = False

                time.sleep(float(self.interval.get()))
            except:
                self.running = False

    def start_clicking(self):
        if not self.target_window:
            messagebox.showwarning("警告", "请先选择目标窗口！")
            return

        if not self.running:
            self.running = True
            self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
            self.click_thread.start()
            self.status_var.set("点击已开始 - 按F10停止")

    def stop_clicking(self):
        if self.running:
            self.running = False
            self.status_var.set("点击已停止 - 按F10开始")

    def toggle_clicking(self):
        if self.running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def on_close(self):
        self.stop_clicking()
        keyboard.unhook_all()
        mouse.unhook_all()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickTool(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
