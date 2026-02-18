# 次の目標

## 🔥 次の課題: SIM AIとの連携

### 概要
MetalClawとSIM AIを連携させ、より高度なAIエージェント機能を追加する。

### 参照
- **SIM AI GitHub:** https://github.com/simstudioai/sim

### 研究事項
- SIM AIのAPIと通信方法を調査
- MetalClawへの統合方法を検討
- 既存のAgent Zeroツールとの共通点を分析
- ユースケースの特定

### 実装方針（未定）
- SIM AIがHTTP APIを提供しているか？
- 認証方式（APIキー、OAuthなど）
- 通信プロトコル（HTTP、WebSocketなど）
- レスポンス形式

### 優先度
- ⭐⭐⭐ 高（次回のセッションで優先）

---

## 📋 その他の課題

### 1. スラッシュコマンドの実装（保留中）
- `/zero` - Agent Zeroモード
- `/opencode` - OpenCode CLIモード
- `/local` - ローカルシェルモード
- `/default` - デフォルトLLMチャットモード

### 2. OpenCodeツールの実装
- `opencode.py`の完成
- GLM-5-Freeモデルとの統合
- ワークスペース設定の確認

### 3. コンテキスト管理の改善
- コンテキストIDの永続化
- 会話履歴の管理
- 複数コンテキストの切り替え

---

_作成日: 2026年2月19日_
_次回のセッションで取り組むこと_ 😈
