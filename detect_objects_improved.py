import argparse
import cv2
import json
import os
from ultralytics import YOLO

def run_object_detection():
    """
    コマンドライン引数から設定を読み込み、YOLOv8を用いて物体検出を実行するスクリプト。
    検出結果は画像として保存され、詳細なログはJSONファイルとして出力される。
    """
    # 1. コマンドライン引数の設定
    parser = argparse.ArgumentParser(description="YOLOv8を用いた物体検出スクリプト。")
    parser.add_argument('image_path', type=str,
                        help='検出対象の画像ファイルパス。')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                        help='使用するYOLOv8モデルのパスまたは名前（例: yolov8n.pt, yolov8s.pt）。')
    parser.add_argument('--conf', type=float, default=0.5,
                        help='検出結果の信頼度閾値。この値以上の信頼度のオブジェクトのみを検出とみなす。')
    parser.add_argument('--output_image', type=str,
                        help='検出結果を描画した画像の保存パス。指定しない場合、元のファイル名に "_detected" を付加して保存する。')
    parser.add_argument('--output_log', type=str,
                        help='検出結果の詳細ログ（JSON形式）の保存パス。指定しない場合、元のファイル名に "_log.json" を付加して保存する。')
    parser.add_argument('--show_window', action='store_true',
                        help='結果画像を表示するウィンドウを開くかどうか。デフォルトでは開かない。')
    args = parser.parse_args()

    # パスが絶対パスでない場合、現在の作業ディレクトリからの相対パスとして扱う
    # ただし、Ultralyticsは内部でパスを解決するため、ここでは特に処理しない

    # 2. YOLOv8モデルのロード
    try:
        print(f"Loading YOLO model: {args.model}")
        model = YOLO(args.model)
    except Exception as e:
        print(f"Error: Could not load YOLO model '{args.model}'. Please check the model path/name and your Ultralytics installation.")
        print(f"Details: {e}")
        return # スクリプトを終了

    # 3. 画像の読み込み
    print(f"Loading image: {args.image_path}")
    img = cv2.imread(args.image_path)
    if img is None:
        print(f"Error: Could not load image from '{args.image_path}'.")
        print("Please check if the file exists and is a valid image format.")
        return # スクリプトを終了

    # 4. 物体検出の実行
    print("Running object detection...")
    # conf引数をYOLOモデルに直接渡すことで、モデルの内部で閾値処理が行われる
    results = model(img, conf=args.conf)

    # 5. 検出結果の処理と集計
    detected_objects_count = 0
    object_counts = {}
    detection_log_data = [] # JSON出力用のリスト

    # YOLOv8のresultsオブジェクトは、描画済みのBGR画像も提供する
    # r.plot()は、検出結果が描画されたNumpy配列（BGR形式）を返す
    # ただし、描画はresultsオブジェクトのリストの最初の要素に対して行う
    # 複数画像を入力した場合、resultsはリストになる
    rendered_img = img.copy() # 描画用に画像をコピー

    for i, r in enumerate(results):
        # バッチ処理の場合、各画像の結果を個別に処理する必要がある
        # 今回は単一画像入力なので、iは0となる
        boxes = r.boxes # Bounding boxes (ultralytics.engine.results.Boxes object)
        names = r.names # Class names (dict mapping class_id to name)

        # 検出結果が描画された画像を生成 (YOLOv8のplot機能を使用)
        # 自分で描画する場合はこの行を削除し、下記の描画コードを有効にする
        rendered_img = r.plot() # BGR image with detections drawn

        print(f"\n--- Detections for {os.path.basename(args.image_path)} (Confidence > {args.conf:.2f}) ---")
        if len(boxes) == 0:
            print("No objects detected above the confidence threshold.")
            
        for box in boxes:
            cls = int(box.cls[0])    # クラスID
            conf = float(box.conf[0]) # 信頼度スコア
            xyxy = box.xyxy[0].tolist() # [x1, y1, x2, y2] 形式のバウンディングボックス座標

            class_name = names[cls]

            print(f"  Detected: {class_name} (Confidence: {conf:.2f}, BBox: [{int(xyxy[0])},{int(xyxy[1])},{int(xyxy[2])},{int(xyxy[3])}])")

            detected_objects_count += 1
            object_counts[class_name] = object_counts.get(class_name, 0) + 1

            # JSONログ用のデータを追加
            detection_log_data.append({
                "class_name": class_name,
                "confidence": round(conf, 4), # 精度を4桁に丸める
                "bbox": [int(coord) for coord in xyxy] # 整数に変換
            })

            # 古い手動描画コード（YOLOv8のplot()を使用しない場合）
            # x1, y1, x2, y2 = map(int, xyxy)
            # cv2.rectangle(rendered_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # cv2.putText(rendered_img, f"{class_name} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


    print(f"\nTotal objects detected: {detected_objects_count}")
    print("Object breakdown:")
    if not object_counts:
        print("  No objects counted.")
    else:
        for name, count in object_counts.items():
            print(f"  {name}: {count}")

    # 6. 結果画像の保存
    output_image_path = args.output_image
    if output_image_path is None:
        base_name, ext = os.path.splitext(args.image_path)
        output_image_path = f"{base_name}_detected{ext}"

    try:
        cv2.imwrite(output_image_path, rendered_img)
        print(f"Detection results image saved to '{output_image_path}'")
    except Exception as e:
        print(f"Error: Could not save the output image to '{output_image_path}'.")
        print(f"Details: {e}")

    # 7. 検出ログのJSON保存
    output_log_path = args.output_log
    if output_log_path is None:
        base_name, _ = os.path.splitext(args.image_path)
        output_log_path = f"{base_name}_log.json"

    try:
        with open(output_log_path, 'w', encoding='utf-8') as f:
            json.dump(detection_log_data, f, indent=4, ensure_ascii=False)
        print(f"Detection log saved to '{output_log_path}'")
    except Exception as e:
        print(f"Error: Could not save the detection log to '{output_log_path}'.")
        print(f"Details: {e}")

    # 8. 結果画像の表示（オプション）
    if args.show_window:
        try:
            cv2.imshow("Detected Objects", rendered_img)
            print("Press any key to close the display window...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Warning: Could not display the image. This might happen in environments without a graphical interface.")
            print(f"Details: {e}")

if __name__ == "__main__":
    run_object_detection()