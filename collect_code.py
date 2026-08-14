import os
import fnmatch

# مسیر پروژه (همان d:\MangaTranslator)
PROJECT_PATH = r"d:\MangaTranslator"

# پسوندهایی که می‌خواهیم جمع‌آوری کنیم
EXTENSIONS = [
    "*.py",      # فایل‌های پایتون
    "*.pyi",     # stub files
    "*.txt",     # فایل‌های متنی
    "*.md",      # مارک‌داون
    "*.json",    # کانفیگ‌ها
    "*.yaml",    # کانفیگ‌ها
    "*.yml",     # کانفیگ‌ها
    "*.cfg",     # کانفیگ‌ها
    "*.conf",    # کانفیگ‌ها
    "*.html",    # تمپلیت‌ها
    "*.qml",     # فایل‌های QML
    "*.js",      # جاوااسکریپت
]

# پوشه‌هایی که نباید اسکن شوند (باینری، venv، lib)
EXCLUDE_DIRS = [
    "ocr_venv",      # محیط مجازی OCR
    "Lib",           # کتابخانه‌های پایتون
    "Include",       # هدر فایل‌ها
    "__pycache__",   # کش پایتون
    ".git",          # گیت
    "logs",          # لاگ‌ها
    "models",        # مدل‌های سنگین (اختیاری)
    "PIL",           # کتابخانه PIL
    "numpy",         # کتابخانه numpy
    "pandas",        # کتابخانه pandas
    "paddle",        # کتابخانه paddle
    "PySide6",       # کتابخانه PySide6
    "cv2",           # کتابخانه OpenCV
    "huggingface_hub", # کتابخانه
    "accelerate",    # کتابخانه
    "aiohttp",       # کتابخانه
    "anyio",         # کتابخانه
    "charset_normalizer", # کتابخانه
    "click",         # کتابخانه
    "colorama",      # کتابخانه
    "filelock",      # کتابخانه
    "fsspec",        # کتابخانه
    "httpx",         # کتابخانه
    "idna",          # کتابخانه
    "jinja2",        # کتابخانه
    "markdown_it",   # کتابخانه
    "markupsafe",    # کتابخانه
    "mdurl",         # کتابخانه
    "modelscope",    # کتابخانه
    "networkx",      # کتابخانه
    "opt_einsum",    # کتابخانه
    "packaging",     # کتابخانه
    "paddlex",       # کتابخانه
    "pydantic",      # کتابخانه
    "requests",      # کتابخانه
    "torch",         # کتابخانه
    "tqdm",          # کتابخانه
    "transformers",  # کتابخانه
    "yaml",          # کتابخانه
]

OUTPUT_FILE = "all_code.txt"

def should_include_file(filepath):
    for ext in EXTENSIONS:
        if fnmatch.fnmatch(os.path.basename(filepath), ext):
            return True
    return False

def should_exclude_dir(dirpath):
    dir_name = os.path.basename(dirpath)
    for exclude in EXCLUDE_DIRS:
        if exclude in dirpath.split(os.sep):
            return True
    return False

def collect_files(root_dir):
    files = []
    for root, dirs, filenames in os.walk(root_dir):
        # حذف دایرکتوری‌های نامطلوب
        dirs[:] = [d for d in dirs if not should_exclude_dir(os.path.join(root, d))]
        
        for filename in filenames:
            filepath = os.path.join(root, filename)
            if should_include_file(filepath):
                files.append(filepath)
    return files

def write_output(files, output_path):
    with open(output_path, "w", encoding="utf-8", errors="ignore") as out:
        out.write(f"=== COLLECTED CODE FROM: {PROJECT_PATH} ===\n")
        out.write(f"Total files: {len(files)}\n\n")
        
        for i, filepath in enumerate(files):
            relative_path = os.path.relpath(filepath, PROJECT_PATH)
            out.write(f"\n{'='*80}\n")
            out.write(f"FILE {i+1}/{len(files)}: {relative_path}\n")
            out.write(f"{'='*80}\n\n")
            
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    out.write(content)
                    out.write("\n\n")
            except Exception as e:
                out.write(f"ERROR: Could not read file - {e}\n\n")

if __name__ == "__main__":
    print("Scanning project files...")
    files = collect_files(PROJECT_PATH)
    print(f"Found {len(files)} files.")
    print(f"Writing to {OUTPUT_FILE}...")
    write_output(files, OUTPUT_FILE)
    print("Done!")