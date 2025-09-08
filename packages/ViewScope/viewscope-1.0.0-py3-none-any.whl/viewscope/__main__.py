"""
ViewScope命令行入口
"""

import sys
import signal
import threading
import subprocess
import webbrowser
import socket
import time
import uiautomator2 as u2
import uvicorn


def find_available_port(start_port=8060, max_attempts=10):
    """寻找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            # 尝试连接端口，如果连接失败说明端口可用
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result != 0:  # 连接失败，端口可用
                return port
        except Exception:
            # 异常也表示端口可用
            return port
    return None


def init_uiautomator2():
    """初始化uiautomator2到设备"""
    print("[INIT] 正在初始化uiautomator2...")

    try:
        # 检查设备连接
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        if result.returncode != 0:
            print("[ERROR] ADB不可用，请确保已安装Android SDK并配置环境变量")
            return False

        lines = result.stdout.strip().split('\n')[1:]
        devices = [line.split('\t')[0] for line in lines if line.strip() and '\t' in line]

        if not devices:
            print("[WARNING] 未发现连接的Android设备")
            print("[INFO] 请连接Android设备并开启USB调试")
            return True  # 继续启动，但提醒用户

        print(f"[DEVICE] 发现 {len(devices)} 个设备: {', '.join(devices)}")

        # 对每个设备初始化uiautomator2
        for device_id in devices:
            try:
                print(f"[INIT] 正在初始化设备 {device_id}...")
                # 使用uiautomator2的init方法
                u2.connect(device_id).healthcheck()
                print(f"[OK] 设备 {device_id} 初始化成功")
            except Exception as e:
                print(f"[WARNING] 设备 {device_id} 初始化失败: {e}")
                print("[INFO] 可能需要手动运行: python -m uiautomator2 init")

        return True

    except Exception as e:
        print(f"[ERROR] 初始化uiautomator2失败: {e}")
        return False


def open_browser(port):
    """打开浏览器"""
    def delayed_open():
        time.sleep(3)  # 等待服务启动
        try:
            webbrowser.open(f"http://localhost:{port}")
            print("[BROWSER] 已在浏览器中打开 ViewScope")
        except Exception as e:
            print(f"[WARNING] 无法自动打开浏览器: {e}")
            print(f"[INFO] 请手动访问: http://localhost:{port}")

    thread = threading.Thread(target=delayed_open)
    thread.daemon = True
    thread.start()


def signal_handler(signum, frame):
    """信号处理"""
    print("\n[SHUTDOWN] 正在关闭服务...")
    sys.exit(0)


def main():
    """主入口函数"""
    print("=" * 50)
    print("[INIT] ViewScope - Android Inspector")
    print("=" * 50)

    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)

    # 初始化uiautomator2
    if not init_uiautomator2():
        print("[ERROR] uiautomator2初始化失败，但仍将继续启动服务")

    # 寻找可用端口
    available_port = find_available_port()
    if not available_port:
        print("[ERROR] 无法找到可用端口 (8060-8069)")
        return 1
    
    if available_port != 8060:
        print(f"[INFO] 端口8060被占用，使用端口 {available_port}")

    # 显示访问信息
    print("\n" + "=" * 50)
    print("[Success] ViewScope 启动成功!")
    print(f"[Address] 前端界面: http://localhost:{available_port}")
    print(f"[Address] 后端API: http://localhost:{available_port}")
    print(f"[Address] API文档: http://localhost:{available_port}/docs")
    print("[System] 按 Ctrl+C 停止服务")
    print("=" * 50)

    # 自动打开浏览器
    open_browser(available_port)

    try:
        # 直接启动FastAPI应用
        uvicorn.run(
            "viewscope.main:app",
            host="0.0.0.0",
            port=available_port,
            reload=False,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] 收到停止信号")
        return 0
    except Exception as e:
        print(f"[ERROR] 启动失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())