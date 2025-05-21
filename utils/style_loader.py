def load_qss(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"無法讀取樣式檔: {e}")
        return ""
