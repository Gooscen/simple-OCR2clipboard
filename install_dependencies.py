#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖安装脚本
自动安装Tesseract OCR和相关Python包
"""

import subprocess
import sys
import os
import platform

def run_command(command):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def install_tesseract():
    """安装Tesseract OCR"""
    system = platform.system().lower()
    
    print("正在安装Tesseract OCR...")
    
    if system == "darwin":  # macOS
        print("检测到macOS系统，尝试使用Homebrew安装...")
        
        # 检查是否安装了Homebrew
        success, _, _ = run_command("which brew")
        if not success:
            print("未检测到Homebrew，请先安装Homebrew:")
            print("访问 https://brew.sh/ 获取安装说明")
            return False
        
        # 安装tesseract
        success, stdout, stderr = run_command("brew install tesseract")
        if success:
            print("Tesseract安装成功!")
            
            # 安装中文语言包
            print("正在安装中文语言包...")
            run_command("brew install tesseract-lang")
            return True
        else:
            print(f"Tesseract安装失败: {stderr}")
            return False
            
    elif system == "linux":
        print("检测到Linux系统，尝试使用包管理器安装...")
        
        # 尝试使用apt-get (Ubuntu/Debian)
        success, _, _ = run_command("which apt-get")
        if success:
            commands = [
                "sudo apt-get update",
                "sudo apt-get install -y tesseract-ocr",
                "sudo apt-get install -y tesseract-ocr-chi-sim"  # 中文语言包
            ]
            for cmd in commands:
                success, stdout, stderr = run_command(cmd)
                if not success:
                    print(f"命令执行失败: {cmd}")
                    print(f"错误: {stderr}")
                    return False
            print("Tesseract安装成功!")
            return True
        
        # 尝试使用yum (CentOS/RHEL)
        success, _, _ = run_command("which yum")
        if success:
            commands = [
                "sudo yum install -y epel-release",
                "sudo yum install -y tesseract",
                "sudo yum install -y tesseract-langpack-chi_sim"
            ]
            for cmd in commands:
                success, stdout, stderr = run_command(cmd)
                if not success:
                    print(f"命令执行失败: {cmd}")
                    print(f"错误: {stderr}")
                    return False
            print("Tesseract安装成功!")
            return True
            
        print("未找到支持的包管理器，请手动安装Tesseract")
        return False
        
    elif system == "windows":
        print("检测到Windows系统")
        print("请手动下载并安装Tesseract:")
        print("1. 访问 https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. 下载Windows安装程序")
        print("3. 安装时确保选择中文语言包")
        print("4. 安装后将Tesseract路径添加到系统PATH")
        return False
    
    else:
        print(f"不支持的操作系统: {system}")
        return False

def install_python_packages():
    """安装Python包"""
    packages = [
        'pytesseract',
        'keyboard', 
        'pyautogui', 
        'pyperclip', 
        'pillow', 
        'numpy'
    ]
    
    print("正在安装Python依赖包...")
    
    for package in packages:
        print(f"安装 {package}...")
        success, stdout, stderr = run_command(f"{sys.executable} -m pip install {package}")
        if success:
            print(f"✓ {package} 安装成功")
        else:
            print(f"✗ {package} 安装失败: {stderr}")
            return False
    
    print("所有Python包安装完成!")
    return True

def check_installation():
    """检查安装结果"""
    print("\n检查安装结果...")
    
    # 检查Tesseract
    success, stdout, stderr = run_command("tesseract --version")
    if success:
        print("✓ Tesseract已正确安装")
        version_line = stdout.strip().split('\n')[0] if stdout.strip() else "版本信息获取失败"
        print(f"  版本信息: {version_line}")
    else:
        print("✗ Tesseract未正确安装")
        print(f"  错误信息: {stderr}")
        return False
    
    # 检查Python包
    try:
        import pytesseract
        import keyboard
        import pyautogui
        import pyperclip
        from PIL import Image
        import numpy
        print("✓ 所有Python依赖包已正确安装")
    except ImportError as e:
        print(f"✗ Python包导入失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("屏幕OCR工具依赖安装脚本")
    print("=" * 50)
    
    # 安装Tesseract
    if not install_tesseract():
        print("\nTesseract安装失败，请手动安装后再运行此脚本")
        return
    
    # 安装Python包
    if not install_python_packages():
        print("\nPython包安装失败")
        return
    
    # 检查安装结果
    if check_installation():
        print("\n🎉 所有依赖安装完成!")
        print("现在可以运行 'python screen_ocr_app.py' 启动OCR工具")
    else:
        print("\n❌ 安装验证失败，请检查错误信息")

if __name__ == "__main__":
    main() 