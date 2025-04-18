import os


class HistoryManager:
    def __init__(self, history_file="project_summary_history.txt"):
        self.history_file = history_file
        self.history = self._load_history()

    def _load_history(self):
        """履歴ファイルから実行履歴を読み込む"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"履歴の読み込みエラー: {e}")
                return []
        return []

    def _save_history(self):
        """実行履歴をファイルに保存する"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                for path in self.history:
                    f.write(f"{path}\n")
        except Exception as e:
            print(f"履歴の保存エラー: {e}")

    def add_entry(self, path):
        """新しいパスを履歴に追加（重複を避ける）"""
        # 一貫性のために絶対パスに変換
        abs_path = os.path.abspath(path)

        # すでに存在する場合は削除（先頭に移動するため）
        if abs_path in self.history:
            self.history.remove(abs_path)

        # 履歴の先頭に追加
        self.history.insert(0, abs_path)

        # 履歴のサイズを20エントリーに制限
        self.history = self.history[:20]

        # 更新された履歴を保存
        self._save_history()

    def show_history(self):
        """インデックス付きで履歴エントリーを表示"""
        if not self.history:
            print("履歴がありません。")
            return None

        print("履歴からプロジェクトディレクトリを選択してください:")
        for i, path in enumerate(self.history, 1):
            print(f"[{i}] {path}")

        return self.history

    def get_path_from_selection(self, selection):
        """ユーザー選択からパスを取得"""
        try:
            index = int(selection) - 1
            if 0 <= index < len(self.history):
                return self.history[index]
            else:
                print("無効な選択です。")
                return None
        except ValueError:
            print("数字を入力してください。")
            return None
