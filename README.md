# A.L.L.I.C.A.

> **Ai for Language & Logical Inference with Cyberactive Assistance**

A.L.L.I.C.A.(アリカ)は、Google Geminiと連携したDiscordBOTです。<br>
スラッシュコマンドによって、ユーザーの指示に応じて言語理解・論理推論・Web検索を通じたアシスタンスを行います。

プロンプトやモデル選択の切り替え、トークン制御など、細やかなチューニングを行いながらの運用が可能なBotを目指しています。

LLMの汎用的な情報処理能力を十全に活用し、音声入出力による自然な対話やその他機能との統合までを見据えて開発中です。

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
- Discord アプリケーショントークン (環境変数`DISCORD_TOKEN`にて指定)
- Gemini API キー (環境変数`GEMINI_API_KEY`にて指定)

---

## 🐾 現在のキャラクタイメージ (A.L.L.I.C.A.)

> 電脳猫耳メイドアシスタント。ちょっぴり気まぐれで、でも本当はご主人想い。
> テーマカラーは `#96CFFF (RGB=[150, 207, 255])`。

<img width="200" src="https://github.com/ogw1087/ALLICA/blob/main/img/icon.png">

---

## セットアップ・実行方法

### 1. **リポジトリのクローン**

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

### 3. **必要パッケージのインストール**

```bash
pip install -r requirements.txt
```

### 4. **APIキー、トークンの取得**

- **Gemini APIキーを取得する**
[Google AI for Developers](https://ai.google.dev/gemini-api/docs/api-key?hl=ja)<br>
上記サイトより、"Google AI StudioでGemini APIキーを取得する" ボタンからAPIキーを発行する。

- **Discord**
[Discord Developer Portal](https://discord.com/developers/applications)<br>
上記サイトより、"NewApplication"から新しいアプリケーションを作成し、トークンを取得する。
    1. 名前を入力し、規約を呼んだ後同意して新規アプリケーション作成を進める。
    2. Installation > Install Link をプルダウンメニューより"None"に変更する。
    3. Bot > PUBLIC BOT をスイッチをクリックしてOFFにする。
    4. Bot > Reset Token よりトークンを初期化してコピーする。

### 5. **APIキーの設定**

プロジェクトのディレクトリに`.env`を作成し、`DISCORD_TOKEN=your_discord_`および`GEMINI_API_KEY=your_api_key`の形式で取得したAPIキーとトークンを記述して保存する。

### 6. **Discord Botの設定と招待**
[Discord Developer Portal](https://discord.com/developers/applications)にアクセスして先ほど作成したアプリケーションの設定画面を開く。<br>
General Information で名称と説明を記述する。(botのプロフィールに反映される。)<br>
OAuth2 > OAuth2 URL Generator > SCOPES にて "bot" にチェックすると、下部に Bot Permissions が現れる。<br>
Text Permissions の Send Messages(メッセージ送信), Attach Files(画像等の添付), Read Message History(メッセージ履歴の参照), Use Slash Commands(スラッシュコマンドの利用)<br>
Voice Permissions の Connect(ボイスチャンネルへの参加), Speak(ボイスチャンネルへの音声出力)にチェックを入れる。<br>
下部のGENERATED URLよりコピーしたリンクを適当なブラウザで開き、Botを任意のサーバーへ招待する。<br>
(リンクに`permissions=2150729728`が含まれていれば上記の権限が適切に選択できている。)

招待したBotに`Bot`タグを追加する。

### 7. **実行(Botを起動)**
```bash
python bot.py
```

招待したDiscordサーバー上でオンラインになったことを確認する。<br>
テキストチャットで`/`を入力すると、コマンドの候補が出る。

---

## 現在利用可能なコマンド

- チャットによる対話
`/ask question:質問内容 model:Geminiのモデル`

- 機能のON/OFFの切り替え(管理者)
`/toggle`

---

## ファイル構成(予定)

```
discord_gemini_bot/
├── bot.py                        # エントリーポイント(Botの起動)
├── commands/
│   ├── ask.py                    # 一問一答コマンド(/ask)の処理
│   ├── newsession.py             # 会話の開始コマンド
│   ├── talk.py                   # セッション内での会話用コマンド
│   ├── toggle.py                 # ON/OFF切り替えコマンド(管理者用)
│   └── limiter.py                # トークン・使用回数制限管理(未実装)
├── gemini/
│   └── client.py                 # Gemini APIとのやりとり
├── voice/
│   ├── input.py                  # 音声入力(Whisperなど)(未実装)
│   └── output.py                 # 音声出力(ボイスチャンネル内でのTTS)(未実装)
├── context/
│   ├── context_builder.py        # sessionID, DiscordIDから該当の会話の要約と記憶データから現在の"文脈"を構築
|   ├── memory_utils.py           # 文脈データ、ユーザーごとにパーソナライズされた記憶データの保存・読み込み
|   └── session_manager.py        # スレッドとセッションの管理(スレッド作成, 削除(未実装), メタデータの保存と更新)
├── listeners/
|   └── mention_listener.py       # セッション内でのメンション検知
├──prompts/
│   ├── ask.txt                   # 一問一答用プロンプトテンプレート
│   ├── newsession.txt            # 新規会話用プロンプトテンプレート
|   └── talk.txt                  # 文脈と記憶を利用した会話のプロンプトテンプレート
├── data/
│   ├── memory/
│   │   ├{userID}.json            # セッションを跨いだユーザーごとの長期記憶情報
│   │   └...
│   ├── session/
│   │   ├{userID}_{sessionID}.json# セッションごとの文脈情報
│   │   ├session_threads.json     # セッションごとのメタデータ
│   │   └...
│   ├── config.json               # プロンプトのパスなどのBotの設定ファイル
│   ├── toggle_state.json         # On/Offの状態保存
│   └── topics.json               # 会話のタグ一覧と分類情報
├──img/
│   └── icon.png                  # Discordのアイコン画像
├── .env                          # APIキーやトークン(環境変数)
├── requirements.txt              # 必要ライブラリ
└── README.md                     # 説明書
```

---

## 各モジュールの詳細
編集中

---

## 高度な文脈理解のシステムのアイデア(開発中)
ユーザーとの対話において、主題タグ(トピック)ごとに文脈を保存・呼び出すセッション管理システムをDiscord Bot上に構築する。

対話はセッション(主題)単位で管理される。最終的な開発段階において、各セッションはBotによってスレッドとして作成・紐づけられる。

### 目的
- 単発の質問回答に留まらず、過去の会話(文脈)や記憶(会話を横断した長期記憶)を参照した一貫性のある応答を可能にすること。
- 主題タグに基づいてセッション管理と切り替えを容易にすること。
- スレッドを用いた可視的・永続的なセッション単位の管理を可能とすること。

### 要件分類
A. 文脈保持(直近の発話)
- ユーザーごとに直近のn回の発話と回答を保持。
- GPTでいう「context window」にあたる領域。主に一時的な対話の流れを形成する。

B. メモリ機能(長期記憶)
- セッション横断的に有効な情報(ユーザー設定・プロジェクト名・重要な一言など)を圧縮(要約)して保存。
- 必要時に明示的な記憶・忘却指示(例: /remember, /forget)も可能にする。

C. 主題管理(セッション分離)
- 会話を主題ごとに分離・整理して記録・参照。
- タグ付けされた主題でセッションの分類を行い、過去の会話の再参照や新規開始が容易になる。

D. プロンプト拡張構造
- 各回答生成時には以下をプロンプトに統合：
```makefile
system: 設定と回答形式など(prompts/ask.txt等を参照)
主題タグ: #ExampleTopic
直近の発話要約: 会話履歴の要約形式(n件)
長期記憶: 今後の回答生成に必要なユーザー情報
発話本文: ユーザーの今回の入力
```

E. スレッド管理
- 新規セッション追加時、主題タグによって一意に管理されるスレッドを作成。
- スレッド作成時、先頭にメタデータを記録。
- ユーザーによるスレッド操作をコマンドによるbot経由に限定。管理者用コマンドにより可視性と保守性を確保。

### 各種関係コマンド一覧
|機能カテゴリ|コマンド名|引数|説明|
|----|----|----|----|
|新規セッション開始|/newsession|main_text,model|発話から主題タグを抽出し、スレッドを新規作成または再利用し、文脈管理を開始|
|セッション内会話|/talk|main_text,model|スレッドIDからセッション情報を読み込み、返答と文脈情報および記憶情報の更新を行う|
|セッション終了・削除|/delete_session|sesseion|指定したセッション(タグ)を削除。対応スレッドも閉鎖または削除|
|セッション表示|/allsessions|None|自身が所属するセッション(タグ・スレッド)一覧を表示|
|セッション共有|/share_session|session, user|指定ユーザーを該当スレッドに招待し、対話を共有|
|セッション移動|/switch_session|session|明示的にセッションを切り替え(スレッド管理前のみの実装)|
|スレッド作成チャンネルの指定|/select_session_channel|channel|スレッドを作成するテキストチャンネルの指定(管理者ユーザーのみ)|
|文脈保存|自動|None|各セッションごとにユーザーの発話を蓄積し、文脈を継続学習・反映|
|文脈応答|自動|None|ユーザーの発話に応じ、該当セッションの文脈をもとに応答を生成|

### セッションの定義
|項目|内容|
|----|----|
|セッションID|Discord上のスレッドIDと1:1で対応|
|主題タグ|発話から抽出される主題を表す単語または句(例: 旅行計画, 転職活動, BOT作成)|
|文脈履歴|過去のユーザー発話・応答履歴を簡略化して保存(トークン制限を考慮)
|作成者|セッションの作成元ユーザーID|
|参加者|スレッドに参加している他のユーザーIDリスト|

### セッション管理による対話フロー
```mermaid
graph TD;
    A[ユーザーが/newsessionを使用] --> B[引数main_textをBotが受け取る]
    B --> C[生成AIによる主題タグ抽出(例:AI開発)]
    C --> D{既存セッションに類似タグあり？}
    D -- Yes --> E[同ユーザーの既存スレッドの利用提案]
    D -- No --> F[新しいセッション作成]
    D -- Yes --> G[既存スレッドへ移動]
    E -- No --> F
    F --> H[プライベートスレッド作成・ユーザーを招待]
    H --> I[セッション情報保存(JSON/DB)]
```

### 文脈処理とフォーマット
- 文脈情報はスレッドごとに蓄積(最大トークン制限を超えないように圧縮 or 要約)
- 最新の数ラウンド分のみをBot応答時に読み込み。

#### フォーマット(暫定的にJSONで実装予定。各機能追加後のブラッシュアップでDB移行を検討。)
- data/session/session_threads.json
```JSON
{
  "スレッドID": {
    "session_id": "内部管理用セッションID",
    "user_id": "ユーザーID",
    "topic": "会話の主題",
    "model": "Geminiのモデル名(例:gemini-2.5-flash)"
  }
}
```
- data/session/{userID}_{sessionID}.json
```JSON
[
  "1つ目の会話の要約",
  "2つ目の会話の要約",
  ...
]
```

### スレッド権限管理ポリシー
|操作|実行者|説明|
|----|----|----|
|スレッド作成|Botのみ|主題タグベースで命名。#[tag]|
|スレッド招待|Bot|/share_session経由のみで追加|
|スレッド削除|Bot・管理者|/delete_session実行時、または管理者判断で|
|ユーザー編集|不可|スレッド名・構造をBot専用領域とし、改名や離脱は制限|

### 対応モジュールと役割
```
discord_gemini_bot/
├── context/
│   ├── history_manager.py        # ユーザー/チャンネルごとの直近履歴のロード・保存・取得(短期記憶)
│   ├── memory_manager.py         # 長期記憶の読み書き、記憶更新(パーソナリティ、好みなど)
│   ├── topic_manager.py          # トピック分類・タグ付け・会話の話題管理(将来拡張)
│   └── context_builder.py        # 現在の質問・履歴・記憶を組み合わせた文脈生成ロジック
```

#### 各モジュールの役割(編集中)
##### 1. context/history_manager.py

##### 2. context/memory_manager.py

##### 3. context/topic_manager.py

##### 4. context/context_builder.py

---

## 音声入出力
実装予定。技術選定中。Bert-VITS2やF5-TTS?
自由度、音質はBert-VITS2が良さそう。
F5-TTSは2024年の論文で情報が少ないが、python動作でAPI連携が容易であることや動作が他TTSより高速である可能性がある。

---

## 今後の開発実装予定
- 対話履歴の保存・読み込み・参照による文脈理解
- discordサーバー管理者によるトークン制御
- トークン使用量の詳細トラッキング表示
- 音声入力・音声出力モード(コマンドによる制御)
- 他DiscordBOTとの機能統合(ゲーム戦績トラッキング, 独自称号管理)
- ネット検索機能との統合(SERP API 等)
- ユーザーによるプロンプトテンプレートの追加・編集
- 個別キャラクタープリセットによるプロンプトテンプレート管理