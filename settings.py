import os

# 実行ファイルのディレクトリ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 静的配信するファイルをおくディレクトリ
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# 静的配信するファイルを置くディレクトリ
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")