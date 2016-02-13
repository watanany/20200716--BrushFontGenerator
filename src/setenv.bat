@echo off
REM Shift_JIS
REM このファイルが存在する場所を python が検索できるように環境変数をセットする。
REM フォント生成器やキャンバスをコマンドプロンプトから起動する時、予め使う必要がある。
REM ファイルをダブルクリックして起動したい場合は同様に環境変数をセットする必要がある。

set PYTHONPATH=%PYTHONPATH%;%~dp0%lib

