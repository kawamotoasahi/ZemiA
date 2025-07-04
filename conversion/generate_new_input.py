import json
import cv2
import os

def convert_to_new_input(score_file_path, output_path="data/new_input.json"):
    # score_output.json を読み込み
    with open(score_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 画像サイズを取得
    image_path = data.get("image_path")
    if not image_path or not os.path.exists(image_path):
        raise FileNotFoundError("画像ファイルが存在しません")

    img = cv2.imread(image_path)
    height, width = img.shape[:2]

    # bbox → (x, y, width, height) に変換
    objects = []
    for obj in data["objects"]:
        x1, y1, x2, y2 = obj["bbox"]
        objects.append({
            "x": x1,
            "y": y1,
            "width": x2 - x1,
            "height": y2 - y1
        })

    new_input = {
        "score": data["score"],
        "timestamp": data["timestamp"],
        "image_width": width,
        "image_height": height,
        "objects": objects
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(new_input, f, indent=4, ensure_ascii=False)

    print(f"✅ new_input.json を保存しました → {output_path}")

# 実行例
if __name__ == "__main__":
    convert_to_new_input("score_output.json")
