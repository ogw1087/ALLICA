# A.L.L.I.C.A.

> **Ai for Language & Logical Inference with Cyberactive Assistance**

A.L.L.I.C.A.(アリカ)は、Google Geminiと連携したDiscordBOTです。<br>
スラッシュコマンドによって、ユーザーの指示に応じて言語理解・論理推論・Web検索を通じたアシスタンスを行います。

プロンプトやモデル選択の切り替え、トークン制御、思考モードのON/OFFなど、細やかなチューニングを行いながらの運用が可能です。

LLMの汎用的な情報処理能力を十全に活用し、音声入出力による自然な対話やその他機能との統合を見据えて開発中です。

---

## 主な機能

- Gemini API を利用した自然言語応答
- プロンプトテンプレートのカスタマイズ(.txt ファイルによる管理)
- モデル選択(例：gemini-2.0-flash、gemini-2.5-flush-thinking など)
- スラッシュコマンド`/`での制御

---

## 動作環境

- Python 3.10 +
- Windows 11 / macOS / Linux(OS 非依存設計)
- Discord API キー (環境変数`DISCORD_TOKEN`にて指定)
- Gemini API キー (環境変数`GEMINI_API_KEY`にて指定)

---

## ファイル構成

```
discord_gemini_bot/
├── bot.py                        # エントリーポイント(Botの起動)
├── commands/
│   ├── ask.py                    # /ask コマンドの処理
│   ├── toggle.py                 # ON/OFF切り替えコマンド(管理者用)
│   └── limiter.py                # トークン・使用回数制限(未実装)
├── gemini/
│   └── client.py                 # Gemini APIとのやりとり
├── voice/
│   ├── input.py                  # 音声入力(Whisperなど)(未実装)
│   └── output.py                 # 音声出力(TTSなど)(未実装)
├──prompts/
│   └── ask.txt                   # チャットへの回答の生成
├── data/
│   ├── logs.json                 # ログや使用履歴(JSON形式)(未実装)
│   ├── config.json               # プロンプトなどのBotの設定ファイル
│   └── toggle_state.json         # On/Offの状態保存ファイル
├──img/
│   └── icon.png                  # Discordのアイコン画像
├── .env                          # APIキーやトークン(環境変数)
├── requirements.txt              # 必要ライブラリ
└── README.md                     # 説明書
```

---

## セットアップ・実行方法

1. **リポジトリのクローン**

```bash
git clone https://github.com/ogw1087/ALLICA.git
cd ALLICA
```

### 2. 仮想環境を作成(任意)

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows
```

3. **必要パッケージのインストール**

```bash
pip install -r requirements.txt
```

4. **APIキー、トークンの取得**

- **Gemini APIキーを取得する**
[Google AI for Developers](https://ai.google.dev/gemini-api/docs/api-key?hl=ja)<br>
上記サイトより、"Google AI StudioでGemini APIキーを取得する" ボタンからAPIキーを発行する。

- **Discord**
[Discord Developer Portal](https://discord.com/developers/applications)<br>
上記サイトより、"NewApplication"から新しいbotを作成し、トークンを取得する。
    1. 名前を入力し、規約を呼んだ後同意して新規アプリケーション作成を進める。
    2. Installation > Install Link をプルダウンメニューより"None"に変更する。
    3. Bot > PUBLIC BOT をスイッチをクリックしてOFFにする。
    4. Bot > Reset Token よりトークンを初期化してコピーする。

5. **APIキーの設定**

プロジェクトのディレクトリに`.env`を作成し、`DISCORD_TOKEN=your_discord_`および`GEMINI_API_KEY=your_api_key`の形式で取得したAPIキーとトークンを記述して保存する。

6. **Discord Botの設定と招待**
[Discord Developer Portal](https://discord.com/developers/applications)にアクセスして先ほど作成したアプリケーションの設定画面を開く。<br>
General Information で名称と説明を記述する。(botのプロフィールに反映される。)<br>
OAuth2 > OAuth2 URL Generator > SCOPES にて "bot" にチェックすると、下部に Bot Permissions が現れる。<br>
Text Permissions の Send Messages(メッセージ送信), Attach Files(画像等の添付), Read Message History(メッセージ履歴の参照), Use Slash Commands(スラッシュコマンドの利用)<br>
Voice Permissions の Connect(ボイスチャンネルへの参加), Speak(ボイスチャンネルへの音声出力)にチェックを入れる。<br>
下部のGENERATED URLよりコピーしたリンクを適当なブラウザで開き、Botを任意のサーバーへ招待する。<br>
(リンクに`permissions=2150729728`が含まれていれば上記の権限が適切に選択できている。)

招待したBotに`Bot`タグを追加する。

7. **実行(Botを起動)**
```bash
python bot.py
```

招待したDiscordサーバー上でオンラインになったことを確認する。<br>
テキストチャットで`/`を入力すると、コマンドの候補が出る。

---

## 🐾 現在のキャラクタイメージ (A.L.L.I.C.A.)

> 電脳猫耳メイドアシスタント。ちょっぴり気まぐれで、でも本当はご主人想い。
> テーマカラーは `#96CFFF (RGB=[150, 207, 255])`

---

## 今後の開発実装予定
- discordサーバー管理者によるトークン制御
- トークン使用量の詳細トラッキング表示
- 対話履歴の保存・読み込み・参照
- 音声入力・音声出力モード(コマンドによる制御)
- 他DiscordBOTとの機能統合(ゲーム戦績トラッキング, 独自称号管理)
- ネット検索機能との統合(SERP API 等)
- ユーザーによるプロンプトテンプレートの追加・編集
- 個別キャラクタープリセットによるプロンプトテンプレート管理