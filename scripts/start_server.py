#!/usr/bin/env python3
"""LangGraph API サーバー起動スクリプト"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from config.langgraph_config import LangGraphConfig


def start_development_server(config: LangGraphConfig, no_browser: bool = False) -> None:
    """開発サーバーを起動"""
    cmd = [
        'langgraph',
        'dev',
        '--port',
        str(config.server_port),
        '--host',
        '127.0.0.1',
        '--config',
        'langgraph.json',
    ]

    if no_browser:
        cmd.append('--no-browser')

    if config.enable_debugging:
        cmd.extend(['--debug-port', '8001'])

    if config.log_level == 'DEBUG':
        cmd.extend(['--server-log-level', 'DEBUG'])

    print(f'🚀 LangGraph開発サーバーを起動中... (ポート: {config.server_port})')
    print('📋 設定ファイル: langgraph.json')
    print(f'🔧 デバッグモード: {config.enable_debugging}')
    print(f'📊 ログレベル: {config.log_level}')
    print()

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f'❌ サーバー起動に失敗しました: {e}', file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print('\n🛑 サーバーを停止中...')
        sys.exit(0)


def start_production_server(config: LangGraphConfig, detach: bool = False) -> None:
    """本番サーバーを起動"""
    cmd = [
        'langgraph',
        'up',
        '-c',
        'langgraph.json',
        '--port',
        str(config.server_port),
    ]

    if detach:
        cmd.append('--wait')

    print(f'🚀 LangGraph本番サーバーを起動中... (ポート: {config.server_port})')
    print('📋 設定ファイル: langgraph.json')
    print('🐳 Docker環境: 有効')
    print()

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f'❌ サーバー起動に失敗しました: {e}', file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print('\n🛑 サーバーを停止中...')
        sys.exit(0)


def check_dependencies() -> bool:
    """依存関係チェック"""
    try:
        result = subprocess.run(['langgraph', '--version'], capture_output=True, text=True, check=True)
        print(f'✅ LangGraph CLI: {result.stdout.strip()}')
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print('❌ LangGraph CLIが見つかりません')
        print('   インストールコマンド: uv add "langgraph-cli[inmem]"')
        return False


def check_config_files() -> bool:
    """設定ファイルの存在確認"""
    config_files = [
        ('langgraph.json', 'LangGraphサーバー設定'),
        ('.langgraph/config.yaml', 'LangGraphプロジェクト設定'),
        ('.env.development', '開発環境変数'),
    ]

    all_exists = True
    for file_path, description in config_files:
        if Path(file_path).exists():
            print(f'✅ {description}: {file_path}')
        else:
            print(f'❌ {description}が見つかりません: {file_path}')
            all_exists = False

    return all_exists


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='LangGraph API サーバー起動スクリプト')
    parser.add_argument(
        '--env',
        choices=['development', 'production'],
        default='development',
        help='起動環境 (default: development)',
    )
    parser.add_argument('--port', type=int, help='ポート番号 (設定ファイルより優先)')
    parser.add_argument('--no-browser', action='store_true', help='ブラウザを自動起動しない (開発モードのみ)')
    parser.add_argument('--detach', action='store_true', help='バックグラウンドで起動 (本番モードのみ)')
    parser.add_argument('--check', action='store_true', help='依存関係と設定ファイルのチェックのみ実行')

    args = parser.parse_args()

    print('🔍 LangGraph Server セットアップチェック')
    print('=' * 50)

    # 依存関係チェック
    deps_ok = check_dependencies()
    config_ok = check_config_files()

    if not deps_ok or not config_ok:
        print('\n❌ セットアップに問題があります。上記のエラーを修正してください。')
        sys.exit(1)

    if args.check:
        print('\n✅ すべてのチェックが完了しました')
        return

    print('\n🚀 サーバー起動中...')
    print('=' * 50)

    # 設定読み込み
    if args.env == 'development':
        os.environ['LANGGRAPH_ENV'] = 'development'

    config = LangGraphConfig()

    # ポート番号の上書き
    if args.port:
        config.server_port = args.port

    # サーバー起動
    if args.env == 'development':
        start_development_server(config, args.no_browser)
    else:
        start_production_server(config, args.detach)


if __name__ == '__main__':
    main()
