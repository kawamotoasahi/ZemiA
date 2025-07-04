import cv2
import json
import datetime
from ultralytics import YOLO
import argparse
import os

def generate_score_output(image_path, output_path="input/score_output.json", model_path='yolov8n.pt', conf_thresh=0.5):
    model = YOLO(model_path)
    results = model(image_path, conf=conf_thresh)

    objects = []
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            class_name = r.names[cls_id]

            objects.append({
                "class_name": class_name,
                "confidence": round(conf, 4),
                "bbox": [x1, y1, x2, y2]
            })

    # 仮スコア（例：個数×10で最大100）
    score = min(len(objects) * 10, 100)

    output = {
        "score": score,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_path": image_path,
        "objects": objects
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print(f"✅ score_output.json を保存しました → {output_path}")

# CLIとして使えるようにする
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLOv8を用いた物体検出スクリプト。")
    parser.add_argument("image_path", type=str, help="入力画像パス")
    parser.add_argument("--output", type=str, default="input/score_output.json", help="出力JSONパス")
    parser.add_argument("--model", type=str, default="yolov8m.pt", help="YOLOモデルパス")
    parser.add_argument("--conf", type=float, default=0.5, help="信頼度閾値")

    args = parser.parse_args()

    generate_score_output(
        image_path=args.image_path,
        output_path=args.output,
        model_path=args.model,
        conf_thresh=args.conf
    )
