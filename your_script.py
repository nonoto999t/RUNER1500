import concurrent.futures
import subprocess
import time
import ipaddress

COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_CYAN = "\033[96m"
COLOR_RESET = "\033[0m"

MAX_RETRIES = 5


def reconnect(ip):
    disconnect_command = ["adb", "disconnect", f"{ip}:5555"]
    subprocess.run(disconnect_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)

    retries = 0
    while retries < MAX_RETRIES:
        connect_command = ["adb", "connect", f"{ip}:5555"]
        result = subprocess.run(connect_command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if result.returncode == 0:
            break
        else:
            retries += 1
            print(f"การเชื่อมต่อล้มเหลว. กำลังลองใหม่... ({retries}/{MAX_RETRIES})")
            time.sleep(2)  # รอเวลาสักครู่ก่อนลองใหม่

    if retries == MAX_RETRIES:
        print(
            f"{COLOR_RED}เกิดข้อผิดพลาดในการเชื่อมต่อ {ip} ไปยัง ADB{COLOR_RESET}")


def execute_adb_command(ip):
    reconnect(ip)

    adb_command_open_browser = [
        "adb", "-s", f"{ip}:5555", "shell", "am", "start", "-a",
        "android.intent.action.VIEW", "-d", "https://movievip.pages.dev/home"
    ]

    try:
        subprocess.run(adb_command_open_browser, check=True)
        print(f"{COLOR_CYAN}Successfully opened browser for {ip}{COLOR_RESET}")
        print(f"{COLOR_CYAN}Starting: {adb_command_open_browser}{COLOR_RESET}")

        time.sleep(5)  # รอเวลา 5 วินาทีหลังจากเปิดบราวเซอร์

        # Get screen dimensions
        adb_command_get_screen_size = [
            "adb", "-s", f"{ip}:5555", "shell", "wm", "size"
        ]
        result = subprocess.run(adb_command_get_screen_size,
                                stdout=subprocess.PIPE)
        screen_size = result.stdout.decode("utf-8").strip().split()[-1]
        screen_width, screen_height = map(int, screen_size.split("x"))

        # Calculate coordinates for the bottom right corner
        bottom_right_x = screen_width - 1  # ปรับค่าตามต้องการสำหรับอุปกรณ์เฉพาะ
        bottom_right_y = screen_height - 1  # ปรับค่าตามต้องการ

        adb_command_click_bottom_right = [
            "adb", "-s", f"{ip}:5555", "shell", "input", "tap",
            str(bottom_right_x),
            str(bottom_right_y)
        ]

        # Click the bottom right corner
        subprocess.run(adb_command_click_bottom_right, check=True)
        print(f"{COLOR_GREEN}Successfully clicked bottom right for {ip}{COLOR_RESET}")
        print(f"{COLOR_CYAN}Starting: {adb_command_click_bottom_right}{COLOR_RESET}")

    except subprocess.CalledProcessError as e:
        print(f"{COLOR_RED}Error executing command for {ip}: {e}{COLOR_RESET}")


def connect_to_adb(ip_group):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_adb_command, ip) for ip in ip_group]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"{COLOR_RED}Error in connect_to_adb: {e}{COLOR_RESET}")


