#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
屏幕OCR应用
使用Tesseract OCR进行屏幕截图文字识别并保存到剪贴板
"""

import tkinter as tk
from tkinter import messagebox
# import keyboard  # 在macOS上可能导致bus error，暂时禁用
import pyautogui
import pyperclip
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import threading
import time
import os
import sys

# 直接使用tesseract命令行工具，避免pytesseract的pandas依赖问题
import subprocess

def find_tesseract_path():
    """查找tesseract可执行文件路径"""
    possible_paths = [
        "/opt/homebrew/bin/tesseract",
        "/usr/local/bin/tesseract", 
        "/usr/bin/tesseract"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # 尝试使用which命令查找
    try:
        result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None

TESSERACT_PATH = find_tesseract_path()

class ScreenSelector:
    """屏幕区域选择器"""
    
    def __init__(self, callback):
        self.callback = callback
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.canvas = None
        self.root = None
        
    def start_selection(self):
        """开始屏幕选择"""
        # 获取屏幕截图
        screenshot = pyautogui.screenshot()
        
        # 创建全屏窗口
        self.root = tk.Toplevel()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        
        # 创建画布
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 设置背景图像
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        screenshot = screenshot.resize((screen_width, screen_height))
        self.bg_image = ImageTk.PhotoImage(screenshot)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
        
        # 绑定事件
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.root.bind('<Escape>', self.cancel_selection)
        
        # 添加提示文字
        self.canvas.create_text(
            screen_width // 2, 50,
            text="拖拽选择需要识别的区域，按ESC取消",
            fill="white",
            font=("Arial", 16),
            tags="instruction"
        )
        
        self.root.focus_set()
        
    def on_click(self, event):
        """鼠标点击事件"""
        self.start_x = event.x
        self.start_y = event.y
        
    def on_drag(self, event):
        """鼠标拖拽事件"""
        if self.start_x is not None and self.start_y is not None:
            # 删除之前的矩形
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            
            # 绘制新矩形
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline='red', width=2
            )
            
    def on_release(self, event):
        """鼠标释放事件"""
        if self.start_x is not None and self.start_y is not None:
            # 计算选择区域
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)
            
            # 确保区域有效
            if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
                self.root.destroy()
                self.callback((x1, y1, x2, y2))
            else:
                messagebox.showwarning("警告", "选择区域太小，请重新选择")
                self.cancel_selection()
                
    def cancel_selection(self, event=None):
        """取消选择"""
        if self.root:
            self.root.destroy()


class ScreenOCRApp:
    """屏幕OCR主应用"""
    
    def __init__(self):
        self.ocr = None
        self.root = None
        self.status_label = None
        self.result_text = None
        self.is_running = False
        self.hotkey_registered = False
        
        # 初始化OCR
        self.init_ocr()
        
    def init_ocr(self):
        """初始化Tesseract OCR"""
        try:
            print("正在初始化Tesseract OCR...")
            if not TESSERACT_PATH:
                raise Exception("未找到tesseract可执行文件，请确保已安装tesseract")
            print(f"找到tesseract路径: {TESSERACT_PATH}")
            self.tesseract_path = TESSERACT_PATH
            print("Tesseract OCR初始化完成")
        except Exception as e:
            print(f"Tesseract OCR初始化失败: {e}")
            messagebox.showerror("错误", f"Tesseract OCR初始化失败: {e}")
            sys.exit(1)
            
    def create_gui(self):
        """创建图形界面"""
        self.root = tk.Tk()
        self.root.title("屏幕OCR识别工具")
        self.root.geometry("600x500")
        
        # 创建主框架
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = tk.Label(
            main_frame,
            text="屏幕OCR识别工具",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # 说明文字
        info_text = """使用说明：
1. 点击"开始识别"按钮开始屏幕选择
2. 拖拽鼠标选择需要识别的屏幕区域
3. 松开鼠标后自动进行OCR识别
4. 识别结果会自动复制到剪贴板并显示在下方"""
        
        info_label = tk.Label(
            main_frame,
            text=info_text,
            justify=tk.LEFT,
            wraplength=550
        )
        info_label.pack(pady=(0, 10))
        
        # 按钮框架
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=(0, 10))
        
        # 开始识别按钮
        self.start_button = tk.Button(
            button_frame,
            text="开始识别",
            command=self.start_ocr,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空结果按钮
        clear_button = tk.Button(
            button_frame,
            text="清空结果",
            command=self.clear_result,
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            width=15
        )
        clear_button.pack(side=tk.LEFT)
        
        # 状态标签
        self.status_label = tk.Label(
            main_frame,
            text="就绪 - 点击按钮开始识别",
            fg="green",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=(0, 10))
        
        # 结果显示区域
        result_label = tk.Label(
            main_frame,
            text="识别结果：",
            font=("Arial", 12, "bold")
        )
        result_label.pack(anchor=tk.W)
        
        # 创建文本框和滚动条
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.result_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#f5f5f5"
        )
        
        scrollbar = tk.Scrollbar(text_frame, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 注册热键 (暂时禁用keyboard，避免macOS bus error)
        # self.register_hotkey()
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def register_hotkey(self):
        """注册全局热键 (暂时禁用以避免macOS bus error)"""
        print("全局热键暂时禁用，请使用界面按钮进行操作")
        # try:
        #     keyboard.add_hotkey('f9', self.start_ocr)
        #     self.hotkey_registered = True
        #     print("热键 F9 注册成功")
        # except Exception as e:
        #     print(f"热键注册失败: {e}")
        #     messagebox.showwarning("警告", f"热键注册失败: {e}")
            
    def unregister_hotkey(self):
        """注销热键"""
        # if self.hotkey_registered:
        #     try:
        #         keyboard.remove_hotkey('f9')
        #         self.hotkey_registered = False
        #         print("热键已注销")
        #     except Exception as e:
        #         print(f"热键注销失败: {e}")
        pass
                
    def start_ocr(self):
        """开始OCR识别"""
        if self.is_running:
            return
            
        self.is_running = True
        self.update_status("请选择屏幕区域...")
        
        # 隐藏主窗口
        if self.root:
            self.root.withdraw()
        
        # 短暂延迟以确保窗口隐藏
        time.sleep(0.2)
        
        # 开始屏幕选择
        selector = ScreenSelector(self.process_selection)
        selector.start_selection()
        
    def process_selection(self, region):
        """处理选择的区域"""
        try:
            x1, y1, x2, y2 = region
            
            # 显示主窗口
            if self.root:
                self.root.deiconify()
                
            self.update_status("正在截图...")
            
            # 截取选定区域
            screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
            
            # 转换为numpy数组
            img_array = np.array(screenshot)
            
            self.update_status("正在识别文字...")
            
            # 使用Tesseract OCR识别
            # 转换为PIL Image对象
            pil_image = Image.fromarray(img_array)
            
            # 图像预处理，提高识别准确率
            # 转换为灰度图
            pil_image = pil_image.convert('L')
            
            # 保存临时图像文件
            temp_image_path = "/tmp/temp_ocr_image.png"
            pil_image.save(temp_image_path)
            
            # 尝试识别中英文混合文本
            try:
                # 首先尝试中英文混合识别
                result = subprocess.run([
                    self.tesseract_path,
                    temp_image_path,
                    'stdout',
                    '-l', 'chi_sim+eng',
                    '--oem', '3',
                    '--psm', '6'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    recognized_text = result.stdout.strip()
                else:
                    raise Exception(f"Tesseract执行失败: {result.stderr}")
                    
            except:
                # 如果中文识别失败，降级到只识别英文
                try:
                    result = subprocess.run([
                        self.tesseract_path,
                        temp_image_path,
                        'stdout',
                        '-l', 'eng',
                        '--oem', '3',
                        '--psm', '6'
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        recognized_text = result.stdout.strip()
                    else:
                        recognized_text = ""
                except:
                    recognized_text = ""
            
            # 清理临时文件
            try:
                os.remove(temp_image_path)
            except:
                pass
            
            if recognized_text:
                # 清理识别结果，去除多余空行
                lines = [line.strip() for line in recognized_text.split('\n') if line.strip()]
                if lines:
                    recognized_text = '\n'.join(lines)
                    
                    # 复制到剪贴板
                    pyperclip.copy(recognized_text)
                    
                    # 显示结果
                    self.show_result(recognized_text)
                    self.update_status(f"识别完成，共识别出 {len(lines)} 行文字")
                else:
                    self.update_status("未识别到有效文字")
                    messagebox.showinfo("提示", "未识别到有效文字，请尝试选择更清晰的区域")
            else:
                self.update_status("未识别到文字")
                messagebox.showinfo("提示", "未识别到文字，请尝试选择更清晰的区域")
                
        except Exception as e:
            self.update_status(f"识别失败: {str(e)}")
            messagebox.showerror("错误", f"OCR识别失败: {str(e)}")
        finally:
            self.is_running = False
            
    def show_result(self, text):
        """显示识别结果"""
        if self.result_text:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, text)
            
    def clear_result(self):
        """清空结果"""
        if self.result_text:
            self.result_text.delete(1.0, tk.END)
        self.update_status("结果已清空")
        
    def update_status(self, message):
        """更新状态"""
        if self.status_label:
            self.status_label.config(text=message)
        print(message)
        
    def on_closing(self):
        """窗口关闭事件"""
        self.unregister_hotkey()
        self.root.destroy()
        
    def run(self):
        """运行应用"""
        self.create_gui()
        print("屏幕OCR应用已启动")
        print("按F9键或点击按钮开始识别")
        self.root.mainloop()


def main():
    """主函数"""
    try:
        # 检查依赖
        required_packages = ['pyautogui', 'pyperclip', 'pillow', 'numpy']
        missing_packages = []
        
        for package in required_packages:
            try:
                if package == 'pillow':
                    __import__('PIL')
                else:
                    __import__(package)
            except ImportError:
                missing_packages.append(package)
                
        if missing_packages:
            print("缺少以下依赖包:")
            for package in missing_packages:
                print(f"  - {package}")
            print("\n请运行以下命令安装依赖:")
            print(f"pip install {' '.join(missing_packages)}")
            return
            
        # 创建并运行应用
        app = ScreenOCRApp()
        print("屏幕OCR应用已启动")
        print("点击界面上的'开始识别'按钮进行操作")
        app.run()
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
        messagebox.showerror("错误", f"程序运行出错: {e}")


if __name__ == "__main__":
    main()