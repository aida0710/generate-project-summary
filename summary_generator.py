import os
import fnmatch


def is_binary(file_path):
    """ファイルがバイナリかどうかを確認"""
    try:
        with open(file_path, 'rb') as file:
            return b'\0' in file.read(1024)
    except Exception as e:
        print(f"ファイルがバイナリかどうかの確認エラー: {e}")
        return True


def read_file_contents(file_path):
    """異なるエンコーディングでファイル内容を読み込む"""
    encodings = ['utf-8', 'shift_jis', 'latin-1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                print(f'ファイル読み込み中: {file_path}')
                return file.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"ファイル読み込みエラー: {e}")
            return ''
    return ''


def read_ignore_file(project_dir, filename):
    """無視ファイル（.gitignoreまたは.summaryignore）からパターンを読み込む"""
    ignore_path = os.path.join(project_dir, filename)
    if os.path.exists(ignore_path):
        try:
            with open(ignore_path, 'r', encoding='utf-8') as file:
                patterns = [line.strip() for line in file if line.strip() and not line.startswith('#')]
                expanded_patterns = []
                for pattern in patterns:
                    expanded_patterns.append(pattern)
                    if '/' in pattern:
                        expanded_patterns.append(pattern.replace('/', '\\'))
                    if '\\' in pattern:
                        expanded_patterns.append(pattern.replace('\\', '/'))
                return expanded_patterns
        except Exception as e:
            print(f"{filename}の読み込みエラー: {e}")
    return []


def read_gitignore(project_dir):
    """.gitignoreからパターンを読み込む"""
    return read_ignore_file(project_dir, '.gitignore')


def read_summaryignore(project_dir):
    """.summaryignoreからパターンを読み込む"""
    return read_ignore_file(project_dir, '.summaryignore')


def is_ignored(path, project_dir, gitignore_patterns, summaryignore_patterns, additional_ignore_patterns):
    """パスが無視すべきかどうかを確認"""
    if os.path.isabs(path):
        # パスが絶対パスの場合、共通の接頭辞をチェック
        if os.path.commonprefix([os.path.abspath(path), os.path.abspath(project_dir)]) != os.path.abspath(project_dir):
            return False
        relative_path = os.path.relpath(path, project_dir)
    else:
        # すでに相対パスの場合
        relative_path = path

    for pattern in gitignore_patterns + summaryignore_patterns + additional_ignore_patterns:
        pattern = f"*{pattern}*"
        if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(f'{os.sep}{relative_path}', pattern):
            return True
    return False


def generate_project_summary(project_dir, output_file=None):
    """プロジェクトサマリーを生成"""
    try:
        project_dir = os.path.abspath(project_dir)
        project_name = os.path.basename(project_dir)

        if not output_file:
            output_file = f'{project_name}_project_summary.txt'

        summary = f'# {project_name}\n\n## Directory Structure\n\n'

        gitignore_patterns = read_gitignore(project_dir)
        print(f"gitignore_patterns: {gitignore_patterns}")

        summaryignore_patterns = read_summaryignore(project_dir)
        print(f"summaryignore_patterns: {summaryignore_patterns}")

        additional_ignore_patterns = ['generate_project_summary.py', '.summaryignore',
                                      f'{project_name}_project_summary.txt', '.git',
                                      'project_summary_history.txt']

        file_contents_section = "\n## File Contents\n\n"

        def traverse_directory(root, level):
            nonlocal summary, file_contents_section
            indent = '  ' * level
            relative_path = os.path.relpath(root, project_dir)

            if is_ignored(relative_path, project_dir, gitignore_patterns, summaryignore_patterns,
                          additional_ignore_patterns):
                return

            summary += f'{indent}- {os.path.basename(root)}/\n'

            subindent = '  ' * (level + 1)
            try:
                items = os.listdir(root)
            except PermissionError:
                summary += f'{subindent}- (アクセス拒否)\n'
                return
            except Exception as e:
                summary += f'{subindent}- (エラー: {e})\n'
                return

            for item in items:
                item_path = os.path.join(root, item)
                if os.path.isdir(item_path):
                    if not is_ignored(item_path, project_dir, gitignore_patterns, summaryignore_patterns,
                                      additional_ignore_patterns):
                        traverse_directory(item_path, level + 1)
                else:
                    if not is_ignored(item_path, project_dir, gitignore_patterns, summaryignore_patterns,
                                      additional_ignore_patterns):
                        if not is_binary(item_path):
                            summary += f'{subindent}- {item}\n'
                            content = read_file_contents(item_path)
                            if content.strip():
                                # プロジェクトディレクトリからの相対パスでファイルパスを表示
                                relative_file_path = os.path.relpath(item_path, project_dir)
                                file_contents_section += f'### {relative_file_path}\n\n```\n{content}\n```\n\n'
                        else:
                            summary += f'{subindent}- {item} (バイナリファイル)\n'

        traverse_directory(project_dir, 0)

        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(summary + file_contents_section)

        print(f"プロジェクトサマリーを生成しました: {os.path.abspath(output_file)}")
        return True
    except Exception as e:
        print(f"プロジェクトサマリー生成エラー: {e}")
        return False
