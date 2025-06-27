# 散らかり可視化GUI：データ連携仕様書

このリポジトリは、画像解析結果（散らかり情報）を可視化するためのWeb GUIを提供します。  

---

## 🔗 データの連携方法（概要）

- GUIは `data/new_input.json` を入力として受け取ります。
- `/refresh` ルートまたは画面上の「データを更新」ボタンを押すと、`new_input.json` の内容が `log.json` に変換されます。
- GUI表示は `log.json` のデータをもとに行われます。

---

## 📁 ディレクトリ構成（抜粋）

```
project_root/
├── app.py                  # Flaskアプリ本体
├── update_log.py           # 入力変換処理（new_input → log）
├── templates/
│   └── index.html          # GUI表示テンプレート
├── data/
│   ├── new_input.json      # ← 画像解析側が出力するファイル
│   └── log.json            # ← GUI表示用履歴ファイル（更新される）
```

---

## 📄 new_input.json の仕様（入力形式）

GUIが受け取る `new_input.json` は以下の形式です：

```json
{
  "score": 38,
  "timestamp": "2025-06-20 14:10:20",
  "image_width": 1280,
  "image_height": 720,
  "objects": [
    { "x": 100, "y": 200, "width": 150, "height": 100 },
    { "x": 400, "y": 600, "width": 80, "height": 120 }
  ]
}
```

### 各フィールドの意味：

| フィールド       | 型     | 内容                                                         |
|------------------|--------|--------------------------------------------------------------|
| `score`          | int    | 散らかりスコア（0〜100を想定）                              |
| `timestamp`      | str    | 計測または生成時刻（例："2025-06-20 14:10:20"）             |
| `image_width`    | int    | 元画像の横幅（回転処理のために使用）                         |
| `image_height`   | int    | 元画像の縦幅                                                 |
| `objects`        | list   | 物体の矩形（x, y, width, height）。中心点もGUIで可視化される |

---

## 🔄 自動回転処理（縦長画像対応）

- `image_height > image_width` の場合、自動で 90° 回転した座標に変換された上で `log.json` に保存されます。
- GUI側では常に横向きの画像とみなして表示されるため、**画像処理側で縦横比を調整する必要はありません。**

---

## ✅ 解析側のToDoまとめ

- `new_input.json` を上記の形式で出力すること。
- スコアや物体の矩形情報は、GUIで視覚的に違和感のない範囲に収めること。
- タイムスタンプは `"YYYY-MM-DD HH:MM:SS"` 形式で記録すること。
  - 例：`datetime.now().strftime("%Y-%m-%d %H:%M:%S")`
- GUIに渡す前に `new_input.json` を `data/` に上書き保存すること。
- テストの際は `/refresh` を実行する（画面のボタンでも可）。

---

## ⚠ 注意点

- `log.json` に同じ timestamp のデータがすでにある場合、重複とみなして更新されません。
- スコアは 0〜100 を基準としたヒートマップ色分けに使われます。
- `log.json` に記録される履歴は最大10件まで（GUI側で最新10件を表示）。
