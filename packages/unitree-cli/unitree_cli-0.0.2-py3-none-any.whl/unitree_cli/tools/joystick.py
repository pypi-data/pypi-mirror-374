import rich_click as click
import paramiko
import signal
import time
import sys

ssh_client = None

def ssh_run(cmd):
    """
    在远程执行命令，自动处理 sudo 密码输入
    """
    # 如果命令本身就有 sudo
    needs_sudo = cmd.strip().startswith("sudo")

    # 如果需要密码，就加上 -S 让 sudo 从 stdin 读取密码
    if needs_sudo and "-S" not in cmd:
        cmd = cmd.replace("sudo", "sudo -S", 1)

    stdin, stdout, stderr = ssh_client.exec_command(cmd)

    # 如果有 sudo，就把密码写进去
    if needs_sudo:
        stdin.write("123" + "\n")
        stdin.flush()

    out = stdout.read().decode("utf-8", errors="ignore").strip()
    err = stderr.read().decode("utf-8", errors="ignore").strip()
    if err:
        print(f"[ERR] {err}")
    return out

@click.command(short_help="登录PC1, 临时用当前遥控器替换该机器的遥控器; 需打调试patch")
@click.option(
    "-d",
    "--device",
    type=str,
    required=True,
    help="Your joystick device ID (6 words, e.g. 34533Y)"
)
def joystick(device):
    # 登录PC1, 临时用当前遥控器替换该机器的遥控器
    # 维持一个终端，退出时恢复

    global original_device, ssh_client
    print(f"Joystick command invoked with device: {device}")

    # 建立 SSH 连接
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect("192.168.123.161", username="unitree", password="123")

    # 读取原始遥控器设备号
    original_device = ssh_run("cat /unitree/robot/basic/rfcode")
    print(f"[INFO] Original device ID: {original_device}")

    # 设置新的设备号
    ssh_run(f"sudo /unitree/robot/tool/basic_demarcate --setupwirelesshandleid {device}")
    print(f"[INFO] Temporary device ID set to: {device}")


    # 捕获 Ctrl+C 信号，恢复设备号
    def restore_and_exit(sig, frame):
        print("\n[INFO] Restoring original device ID...")
        ssh_run(f"sudo /unitree/robot/tool/basic_demarcate --setupwirelesshandleid {original_device}")
        ssh_client.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, restore_and_exit)

    # 持续保持终端
    try:
        print("临时替换遥控器，按 Ctrl+C 退出并恢复原本遥控器")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        restore_and_exit(None, None)