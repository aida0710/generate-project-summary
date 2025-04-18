import argparse
from history_manager import HistoryManager
from summary_generator import generate_project_summary


def main():
    parser = argparse.ArgumentParser(description='プロジェクトサマリーを生成します')
    parser.add_argument('path', nargs='?', help='プロジェクトディレクトリのパス')
    args = parser.parse_args()

    history_manager = HistoryManager()

    # パスが引数として提供された場合
    if args.path:
        project_path = args.path
    else:
        # 履歴を表示して選択を取得
        history = history_manager.show_history()

        if history:
            selection = input("\n選択番号またはパスを入力してください（空白の場合は終了）: ")

            if selection.strip():
                # 履歴の選択として解釈
                if selection.isdigit():
                    project_path = history_manager.get_path_from_selection(selection)
                else:
                    # 直接パスとして解釈
                    project_path = selection
            else:
                # 空白入力の場合は終了
                print("処理を中止しました。")
                return
        else:
            # 履歴がない場合はパスの入力のみを求める
            project_path = input("プロジェクトディレクトリのパスを入力してください: ")
            if not project_path.strip():
                print("パスが入力されていません。処理を中止します。")
                return

    # 有効なパスがあることを確認
    if project_path:
        # 履歴に追加
        history_manager.add_entry(project_path)

        # サマリーを生成
        print(f"サマリーを生成中: {project_path}")
        generate_project_summary(project_path)


if __name__ == '__main__':
    main()
