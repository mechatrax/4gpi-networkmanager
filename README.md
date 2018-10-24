4gpi-networkmanager
===================

4GPi を NetworkManager から使用するためのツール群を提供します。

## 提供ファイル
次のファイルがパッケージに含まれています。

### /usr/sbin/4gpi-dbus-watcher
4GPi を NetworkManager で使用するために dbus のメッセージを扱う実行ファイルです。

### /usr/sbin/4gpi-nm-helper
4GPi を NetworkManager で使用するための設定を行う実行ファイルです。  
使用可能なパラメータを次に示します。

+ set default _&lt;CONNECTION_NAME&gt;_  
  4GPi のデフォルトの通信設定を _&lt;CONNECTION_NAME&gt;_ に設定します。  
  _&lt;CONNECTION_NAME&gt;_ には NetworkManager の設定名を指定します。

+ show default [apn|user|password|all]  
  4GPi のデフォルト設定の値を表示します。  
  表示可能なパラメータは次のとおりです。
  - apn  
    APN を表示します。
  - user  
    ユーザー名を表示します。
  - password  
    パスワードを表示します。
  - all  
    APN, ユーザー名, パスワードを表示します。

+ clear default  
  4GPi のデフォルトの設定を消去します。

+ version
  バージョンを表示します。  

+ help
  ヘルプを表示します。

### /usr/share/bash-completion/completions/4gpi-nm-helper
4gpi-nm-helper のコマンド補完を行うための設定ファイルです。

### /lib/systemd/system/4gpi-networkmanager-helper.service
4GPi を NetworkManager で使用するために設定の補助を行うサービスの設定ファイルです。

### /lib/udev/rules.d/81-4gpi-mm-candidate.rules
4GPi を認識させるための設定ファイルです。

### /usr/share/doc/4gpi-networkmanager/changelog.gz
パッケージの変更履歴を記録したファイルです。

### /usr/share/doc/4gpi-networkmanager/copyright
ソースコードの著作権とライセンスを記載したファイルです。
