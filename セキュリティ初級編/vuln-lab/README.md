
# vuln-lab (Minimal) - OWASP Top10 教材テンプレート（最小構成）

## 概要
このテンプレートはローカル学習用の最小限の脆弱環境を提供する。Flaskアプリに「脆弱版」と「対策版」を同梱し、差分で学べるようにしている。

**重要**: 学習はローカル環境で行うこと。企業ネットワークやクラウドで実行する場合は必ず管理者に許可を取ること。

## 構成
- docker-compose.yml: サービス定義（webのみ）
- web/: Flaskアプリ（脆弱 + 対策エンドポイント）

## 起動方法 (ローカル)
1. Docker と docker-compose を準備する（Windows は WSL2 推奨）
2. リポジトリ直下で以下を実行:
   ```bash
   docker compose up --build -d
   ```
3. ブラウザで `http://localhost:8080` にアクセスする

## 停止
```bash
docker compose down
```

## 各モジュール（概要）
- /module_sql : SQL Injection 脆弱版
- /module_sql/secure : SQL Injection 対策版
- /module_xss : Reflected XSS 脆弱版
- /module_xss/secure : XSS 対策版（エスケープ）
- /admin : 管理画面の脆弱版（認可チェックなし）
- /login and /admin/secure : 簡易認証の対策版
- /module_ssrf : SSRF 脆弱版（外部URLを直接取得）
- /module_ssrf/secure : SSRF 対策版（ホワイトリスト）

## 教員への注意事項
- 環境は学習用であり、意図的に脆弱なコードが含まれる。
- 学習者に配布する前に、必ず実行環境がローカルのみであることを確認すること。
- 必要に応じて `ALLOWED_HOSTS` を調整し、外部アクセスを厳しく制限すること。
