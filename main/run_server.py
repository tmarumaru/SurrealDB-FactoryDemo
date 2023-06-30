import streamlit.web.cli as stcli
import sys

"""
Pycharm 開発環境でDashboardを動作させるためのスクリプト
ここで起動した場合、SurrealDBの情報は arguments_parser.py のデフォルト値が使用される.
"""


def streamlit_run():
    sys.argv = ["streamlit", "run", ".\dashboard\dashboard_main.py", "--global.developmentMode=false"]
    sys.exit(stcli.main())


if __name__ == "__main__":
    streamlit_run()
