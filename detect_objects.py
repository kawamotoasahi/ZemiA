from ultralytics import YOLO
import cv2

# YOLOv8n (nano) モデルをロード (より高速だが精度は控えめ)
# より高精度なモデルを使いたい場合は 'yolov8s.pt' や 'yolov8m.pt' などに変更
model = YOLO('yolov8n.pt')

# 検出したい画像のパス
image_path = 'sample1.jpg' # ここにご自身の画像のパスを設定してください

# 画像を読み込む
img = cv2.imread(image_path)
if img is None:
    print(f"Error: Could not load image from {image_path}")
    exit()

# 物体検出を実行
results = model(img)

# 検出結果を処理
detected_objects_count = 0
object_counts = {}

for r in results:
    boxes = r.boxes # Bounding boxes
    names = r.names # Class names

    for box in boxes:
        cls = int(box.cls[0]) # クラスID
        conf = float(box.conf[0]) # 信頼度スコア

        # 信頼度がある程度高いものだけをカウント (例: 信頼度0.5以上)
        if conf > 0.5:
            class_name = names[cls]
            print(f"Detected: {class_name} with confidence {conf:.2f}")

            detected_objects_count += 1
            object_counts[class_name] = object_counts.get(class_name, 0) + 1

            # 検出された物体を画像に描画 (オプション)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{class_name} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

print(f"\nTotal objects detected: {detected_objects_count}")
print("Object breakdown:")
for name, count in object_counts.items():
    print(f"  {name}: {count}")

# 結果の画像を表示 (オプション)
cv2.imshow("Detected Objects", img)
cv2.waitKey(0)
cv2.destroyAllWindows()