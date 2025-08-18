import sys
import os
import traceback
sys.path.insert(0, os.path.dirname(__file__))

try:
    from main_client import main
    print("开始运行客户端...")
    main()
except Exception as e:
    print(f"客户端启动失败: {e}")
    print("详细错误信息:")
    traceback.print_exc()