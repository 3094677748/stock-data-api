# diagnose.py - 诊断Vercel部署问题
import sys
import os
import subprocess


def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def check_python():
    """检查Python环境"""
    print("=" * 60)
    print("检查Python环境")
    print("=" * 60)

    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"当前目录: {os.getcwd()}")
    print(f"文件列表: {os.listdir('.')}")

    # 检查api目录
    if os.path.exists('api'):
        print("✓ api目录存在")
        print(f"api目录内容: {os.listdir('api')}")
    else:
        print("✗ api目录不存在")


def check_imports():
    """检查模块导入"""
    print("\n" + "=" * 60)
    print("检查模块导入")
    print("=" * 60)

    modules = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("yfinance", "yfinance"),
        ("requests", "requests"),
    ]

    for name, import_name in modules:
        try:
            __import__(import_name)
            print(f"✓ {name} 导入成功")
        except ImportError as e:
            print(f"✗ {name} 导入失败: {e}")


def check_files():
    """检查关键文件"""
    print("\n" + "=" * 60)
    print("检查关键文件")
    print("=" * 60)

    files = [
        "vercel.json",
        "requirements.txt",
        "api/index.py",
        "api/health.py",
        "stock_code.py",
        "kline_fetcher.py",
    ]

    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✓ {file} 存在 ({size} bytes)")
        else:
            print(f"✗ {file} 不存在")


def test_vercel_local():
    """本地模拟Vercel"""
    print("\n" + "=" * 60)
    print("本地模拟Vercel")
    print("=" * 60)

    # 尝试运行健康检查
    print("启动健康检查API...")
    return_code, stdout, stderr = run_command("cd api && python -c \"import health; print('✓ 健康检查API可以导入')\"")

    if return_code == 0:
        print(stdout)
    else:
        print(f"✗ 导入失败: {stderr}")


if __name__ == "__main__":
    print("Vercel部署诊断工具")
    print("=" * 60)

    check_python()
    check_imports()
    check_files()
    test_vercel_local()

    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)