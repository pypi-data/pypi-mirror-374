"""
通用辅助函数模块

包含系统、网络、Docker、.env 文件操作等相关的可重用函数。
"""
import os
import secrets
import shutil
import string
import subprocess
import sys
import time
import urllib.request
from typing import Optional

from conf.settings import BASE_URLS
from utils.i18n import get_message as _

# --- 系统与命令 ---

def is_running_from_source():
    """检查当前是否从源码运行还是从已安装的包运行。
    
    返回:
        bool: 如果从源码运行返回 True，如果从已安装的包运行返回 False。
    """
    # 获取当前脚本的绝对路径
    current_script = os.path.abspath(sys.argv[0])
    script_name = os.path.basename(current_script)
    
    # 1. 最直接的判断：如果命令名称就是 nekro-agent-toolkit，肯定是安装版本
    if script_name == 'nekro-agent-toolkit':
        return False
    
    # 2. 检查脚本路径是否包含典型的安装路径
    installed_indicators = [
        '.local/bin/',        # pipx 安装路径
        'site-packages/',     # pip 安装路径
        '/usr/bin/',         # 系统安装路径
        '/usr/local/bin/',   # 本地安装路径
    ]
    for indicator in installed_indicators:
        if indicator in current_script:
            return False
    
    # 3. 如果脚本名称为 app.py，很可能是从源码运行
    if script_name == 'app.py':
        return True
    
    # 4. 检查当前工作目录是否包含项目源码文件
    current_dir = os.getcwd()
    source_indicators = [
        'setup.py',        # Python 包设置文件
        'pyproject.toml',  # 现代 Python 包配置
        'app.py',          # 主入口文件
        'module',          # 项目模块目录
        'utils',           # 工具目录
        'conf'             # 配置目录
    ]
    
    source_file_count = sum(1 for indicator in source_indicators 
                           if os.path.exists(os.path.join(current_dir, indicator)))
    
    # 如果有4个或以上的源码指标文件，很可能是从源码运行
    if source_file_count >= 4:
        return True
    
    # 5. 检查脚本所在目录是否包含源码文件
    script_dir = os.path.dirname(current_script)
    if script_dir and script_dir != '/usr/bin' and script_dir != '/usr/local/bin':
        script_dir_source_count = sum(1 for indicator in source_indicators 
                                     if os.path.exists(os.path.join(script_dir, indicator)))
        if script_dir_source_count >= 3:
            return True
    
    # 6. 特殊情况：交互式运行或测试（sys.argv[0] 为 '-c' 或类似）
    if script_name in ['-c', '<stdin>', '<string>']:
        # 基于当前工作目录判断
        return source_file_count >= 3
    
    # 默认假设是安装版本（更保守的判断）
    return False

def get_version_info():
    """获取版本信息。
    
    根据运行环境返回不同的版本信息：
    - 源码运行：显示 Git SHA
    - 包安装运行：显示版本号
    
    返回:
        str: 版本信息字符串
    """
    if is_running_from_source():
        # 从源码运行，尝试获取 Git SHA
        try:
            # 尝试获取当前的 Git commit SHA
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], 
                capture_output=True, 
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            if result.returncode == 0:
                sha = result.stdout.strip()[:8]  # 只取前8位
                
                # 检查是否有未提交的更改
                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
                dirty = " (dirty)" if status_result.stdout.strip() else ""
                
                return f"nekro-agent-toolkit (源码) {sha}{dirty}"
            else:
                return "nekro-agent-toolkit (源码) unknown"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "nekro-agent-toolkit (源码) unknown"
    else:
        # 从包安装运行，返回版本号
        try:
            # 尝试从已安装的包获取版本（Python 3.8+ 优先使用 importlib.metadata）
            try:
                from importlib.metadata import version
                pkg_version = version("nekro-agent-toolkit")
                return f"nekro-agent-toolkit {pkg_version}"
            except ImportError:
                # 兼容 Python 3.7 及以下版本
                import pkg_resources
                pkg_version = pkg_resources.get_distribution("nekro-agent-toolkit").version
                return f"nekro-agent-toolkit {pkg_version}"
        except Exception:
            # 如果无法获取已安装版本，回退到硬编码版本
            return "nekro-agent-toolkit 1.0.3"

def get_command_prefix():
    """获取当前运行环境的命令前缀。
    
    返回:
        str: 'python3 app.py' (源码运行) 或 'nekro-agent-toolkit' (包安装)
    """
    if is_running_from_source():
        return "python3 app.py"
    else:
        return "nekro-agent-toolkit"

def command_exists(command):
    """检查指定命令是否存在于系统的 PATH 中。

    参数:
        command (str): 需要检查的命令名称。

    返回:
        bool: 如果命令存在则返回 True，否则返回 False。
    """
    return shutil.which(command) is not None

def get_docker_compose_cmd() -> Optional[str]:
    """确定要使用的正确 docker-compose 命令（v1 或 v2）。

    检查系统中是否存在 'docker-compose' (v1) 或 'docker compose' (v2)，
    并返回可用的命令。

    返回:
        Optional[str]: 如果找到，返回 'docker-compose' 或 'docker compose' 字符串；
                    如果两者都未找到，则返回 None。
    """
    if command_exists("docker-compose"):
        return "docker-compose"
    try:
        subprocess.run("docker compose version", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "docker compose"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def run_sudo_command(command, description, env=None):
    """尝试以当前用户权限运行命令，如果失败则使用 sudo 提权后重试。

    参数:
        command (str): 需要执行的命令。
        description (str): 对正在执行的操作的简短描述。
        env (dict, optional): 为命令设置的环境变量。
    """
    print(f"正在执行: {description}")
    
    # 准备环境
    cmd_env = os.environ.copy()
    if env:
        cmd_env.update(env)

    try:
        # 1. 尝试直接运行
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=cmd_env)
        print("使用当前用户权限执行成功。")
        return
    except subprocess.CalledProcessError:
        # 2. 如果失败，则尝试 sudo
        print("当前用户权限不足，尝试使用 sudo 提权...")
        
        # 构建 sudo 命令
        sudo_command = f"sudo -E {command}"

        try:
            # 使用 `shell=True`，并传递合并后的环境
            subprocess.run(sudo_command, shell=True, check=True, env=cmd_env)
            print(_("sudo_elevation_success"))
        except subprocess.CalledProcessError as e:
            print(f"错误: 使用 sudo 提权后，{description} 仍然失败.\n{e}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print(_("error_sudo_not_found"), file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        cmd_name = command.split()[0]
        print(_("error_command_not_found", cmd_name), file=sys.stderr)
        sys.exit(1)


def check_dependencies():
    """检查并确认所有必需的系统依赖（如 docker, docker-compose）都已安装。

    如果缺少依赖，则打印错误信息并退出脚本。

    返回:
        str: 可用的 docker-compose 命令（'docker-compose' 或 'docker compose'）。
    """
    print(_("checking_dependencies"))
    if not command_exists("docker"):
        print(_("error_docker_not_found"), file=sys.stderr)
        sys.exit(1)

    docker_compose_cmd = get_docker_compose_cmd()
    if not docker_compose_cmd:
        print(_("error_docker_compose_not_found"), file=sys.stderr)
        sys.exit(1)
    
    print(_("dependencies_check_passed"))
    print(_("using_docker_compose_cmd", docker_compose_cmd))
    return docker_compose_cmd

# --- 网络 ---

def get_remote_file(filename, output_path):
    """从 BASE_URLS 列表中定义的远程源下载文件。

    会依次尝试每个 URL，直到成功下载文件或所有源都失败。

    参数:
        filename (str): 要下载的文件名。
        output_path (str): 文件在本地的保存路径。

    返回:
        bool: 如果成功下载则返回 True，否则返回 False。
    """
    for base_url in BASE_URLS:
        url = f"{base_url}/{filename}"
        try:
            print(f"正在从 {url} 下载...")
            urllib.request.urlretrieve(url, output_path)
            print(f"下载成功: {filename}")
            return True
        except Exception as e:
            print(f"下载失败，尝试其他源... (错误: {e})")
            time.sleep(1)
    return False

# --- .env 文件操作 ---

def update_env_file(env_path, key, value):
    """在 .env 文件中更新或添加一个键值对。

    如果键已存在，则更新其值；如果不存在，则在文件末尾添加新的键值对。

    参数:
        env_path (str): .env 文件的路径。
        key (str): 要更新或添加的配置项名称。
        value (str): 要设置的配置项的值。
    """
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            found = True
            break
    
    if not found:
        lines.append(f"{key}={value}\n")

    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def get_env_value(env_path, key):
    """从 .env 文件中获取指定键的值。

    参数:
        env_path (str): .env 文件的路径。
        key (str): 要获取的配置项的名称。

    返回:
        str: 找到的配置项的值，如果未找到或文件不存在则返回空字符串。
    """
    if not os.path.exists(env_path):
        return ""
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith(f"{key}="):
                return line.strip().split('=', 1)[1].strip()
    return ""

def populate_env_secrets(env_path):
    """确保 .env 文件中包含所有必需的随机生成值。

    如果 .env 文件中缺少 ONEBOT_ACCESS_TOKEN, NEKRO_ADMIN_PASSWORD, 或 QDRANT_API_KEY，
    此函数会为它们生成新的随机值并更新文件。

    参数:
        env_path (str): .env 文件的路径。
    """
    print("正在检查并生成必要的访问凭证...")
    for key, length in [("ONEBOT_ACCESS_TOKEN", 32), ("NEKRO_ADMIN_PASSWORD", 16), ("QDRANT_API_KEY", 32)]:
        if not get_env_value(env_path, key):
            print(f"正在生成随机 {key}...")
            update_env_file(env_path, key, generate_random_string(length))

# --- 其他 ---

def generate_random_string(length):
    """生成指定长度的随机字母数字字符串。

    参数:
        length (int): 要生成的字符串的长度。

    返回:
        str: 生成的随机字符串。
    """
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))