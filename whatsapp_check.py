import requests
import time
import json
import sys

# ======================== 【这里修改成你的配置，其他不用动】 ========================
INPUT_FILE = "numbers.txt"       # 本地号码文件，一行一个号码
OUTPUT_FILE = "api_result.json"  # 生成的结果保存文件
API_KEY = "API_KEY"           # 替换成你真实的API KEY
UPLOAD_TASK_URL = "https://api.checknumber.ai/v1/tasks"
QUERY_STATUS_URL = "https://api.checknumber.ai/v1/gettasks"
# ==================================================================================

# 控制台彩色文字
class Color:
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    RED = "\033[31m"
    RESET = "\033[0m"

# 读取本地txt号码文件
def read_numbers_file():
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            numbers = [line.strip() for line in f if line.strip()]
        if not numbers:
            print(f"{Color.RED}❌ 错误：numbers.txt文件为空，请先填写号码{Color.RESET}")
            sys.exit(1)
        print(f"{Color.GREEN}✅ 成功读取文件，共 {len(numbers)} 个号码待处理{Color.RESET}")
        return numbers
    except FileNotFoundError:
        print(f"{Color.RED}❌ 错误：未找到 {INPUT_FILE} 文件，请确认文件在同目录{Color.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Color.RED}❌ 文件读取失败：{str(e)}{Color.RESET}")
        sys.exit(1)

# 调用API上传号码，获取任务ID
def upload_numbers_to_api():
    headers = {"X-API-Key": API_KEY}
    files = {"file": open(INPUT_FILE, "rb")}
    data = {"task_type": "ws"}
    try:
        res = requests.post(UPLOAD_TASK_URL, headers=headers, files=files, data=data, timeout=30)
        res.raise_for_status()
        task_data = res.json()
        task_id = task_data.get("task_id")
        if not task_id:
            print(f"{Color.RED}❌ API返回异常，未获取到任务ID{Color.RESET}")
            sys.exit(1)
        print(f"{Color.BLUE}📌 任务提交成功，任务ID：{task_id}{Color.RESET}")
        return task_id
    except Exception as e:
        print(f"{Color.RED}❌ 任务提交失败：{str(e)}{Color.RESET}")
        sys.exit(1)

# 动态进度条
def show_progress_bar(progress_percent, wait_seconds, bar_length=40):
    filled_length = int(bar_length * progress_percent / 100)
    bar = "▓" * filled_length + "░" * (bar_length - filled_length)
    sys.stdout.write(f"\r{Color.YELLOW}[{bar}] {progress_percent:.1f}% | 任务处理中 | 已等待: {wait_seconds} 秒 {Color.RESET}")
    sys.stdout.flush()

# 轮询API任务状态
def check_task_finish(task_id):
    headers = {"X-API-Key": API_KEY}
    post_data = {"task_id": task_id}
    start_time = time.time()
    max_progress = 100
    current_progress = 0
    progress_step = 2

    print(f"\n{Color.BLUE}⏳ 开始等待任务处理完成，进度实时更新中...{Color.RESET}")
    while True:
        try:
            res = requests.post(QUERY_STATUS_URL, headers=headers, data=post_data, timeout=20)
            res.raise_for_status()
            task_status = res.json()
            status = task_status.get("status", "processing")
            total_wait = int(time.time() - start_time)

            if current_progress < max_progress:
                current_progress += progress_step
                if current_progress > max_progress:
                    current_progress = max_progress
            show_progress_bar(current_progress, total_wait)

            # 关键修改：加入 exported 作为成功状态
            if status in ["success", "completed", "finish", "exported"]:
                sys.stdout.write(f"\n{Color.GREEN}✅ 任务处理完成！耗时：{total_wait} 秒{Color.RESET}\n")
                return task_status
            elif status in ["fail", "failure", "error"]:
                sys.stdout.write(f"\n{Color.RED}❌ 任务处理失败！{task_status.get('msg', '未知错误')}{Color.RESET}\n")
                sys.exit(1)
            elif status in ["pending", "processing", "running"]:
                time.sleep(3)
            else:
                sys.stdout.write(f"\n{Color.RED}⚠️  未知任务状态：{status}{Color.RESET}\n")
                sys.exit(1)
        except Exception as e:
            sys.stdout.write(f"\n{Color.RED}❌ 查询任务状态失败：{str(e)}{Color.RESET}\n")
            time.sleep(5)

# 保存结果到文件
def save_result_to_file(result):
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"{Color.GREEN}📥 结果已成功保存至：{OUTPUT_FILE}{Color.RESET}")
    except Exception as e:
        print(f"{Color.RED}❌ 结果保存失败：{str(e)}{Color.RESET}")

# 主程序
if __name__ == "__main__":
    print(f"{Color.BLUE}="*50)
    print(f"📢 WhatsApp号码批量检测工具 - Python3.9 适配版")
    print(f"="*50 + Color.RESET)
    read_numbers_file()
    task_id = upload_numbers_to_api()
    final_result = check_task_finish(task_id)
    save_result_to_file(final_result)
    print(f"\n{Color.GREEN}🎉 全部流程执行完毕！{Color.RESET}")