<br />
<div align="center">
    <img src="https://static.topcv.vn/company_logos/RADXYxB5wXIZIx1ekdEm4vA019ZfBLEc_1633420623____f1c5c08d7d5695fdfa86c2e8c294ced8.png" alt="Logo" width="113" height="80">

  <h3 align="center">AUTO SEND MAIL</h3>

  <p align="center">
    HACHIX 従業員向けのテンプレートを含む電子メールの自動送信
  </p>
</div>

## プロジェクトについて

* 社名の顧客への自動送信メール
* AWS SESを使用する

## はじめる
### 設定ファイル
* `exe_folder/_internal/configs/config.ini` にて、以下の項目を設定してください。
  * [email]
    * cc: CCメールアドレス (複数の場合はカンマ区切り)
    * subject: メール件名 (テンプレートの変数を使用可能)

* テンプレートを変更する必要がある場合は、`exe_folder/_internal/configs/email_template.html`のファイルを変更してください。

### exeファイル
<div align="center">
    <img src="imgs\Apps.png" alt="Logo" width="113" height="80">
</div>

* 「CSVテンプレートファイルをダウンロード」を押してテンプレートファイルをダウンロードします
* 「CSVファイルを選択」をクリックしてファイルをアプリにアップロードします
* 「メール送信」をクリックしてメールを送信します
* メール送信後、4列目に「×」マークが表示され、メールが送信されたかどうかが確認されます。

## コードフォルダー
### 要件
* Python
* boto3
* PyQt5
* pyinstaller

### exeファイルを作成する
`pyinstaller --onedir --windowed --add-data "configs;configs" .\send_mail.py`


