#!/usr/bin/env python3
"""LangGraph Server ヘルスチェックスクリプト"""

import sys
import urllib.error
import urllib.request


def health_check():
    """LangGraph Serverのヘルスチェックを実行"""
    try:
        # LangGraph Serverのヘルスエンドポイントにアクセス
        with urllib.request.urlopen('http://localhost:8000/', timeout=5) as response:
            if response.getcode() == 200:
                print('Health check passed')
                return True
            else:
                print(f'Health check failed with status code: {response.getcode()}')
                return False
    except urllib.error.URLError as e:
        print(f'Health check failed: {e}')
        return False
    except Exception as e:
        print(f'Unexpected error during health check: {e}')
        return False


if __name__ == '__main__':
    if health_check():
        sys.exit(0)
    else:
        sys.exit(1)
