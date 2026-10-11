def read_code_file(file_path: str) -> str:
    """读取本地代码文件工具"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"【文件读取成功】\n{content}"
    except FileNotFoundError:
        return f"【工具错误】找不到文件:{file_path}"
    except Exception as e:
        return f"【工具错误】读取异常:{str(e)}"
