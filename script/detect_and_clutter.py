import argparse
import cv2
import json
import os
from ultralytics import YOLO
from datetime import datetime

# 画像が配置されているディレクトリの相対パスまたは絶対パスを定義
BASE_PHOTO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'photo'))

def calculate_clutter_score(total_objects: int, object_counts: dict) -> tuple[int, str]:
    """
    検出された物体の数に基づいて散らかり具合のスコア（0-100）と評価メッセージを算出します。
    
    Args:
        total_objects (int): 検出された物体の総数。
        object_counts (dict): 各物体クラスごとの検出数。

    Returns:
        tuple[int, str]: (散らかりスコア, 散らかり具合の評価メッセージ)
    """
    MIN_OBJECTS = 0 
    MAX_OBJECTS = 20 # この値は必要に応じて調整してください

    # スコアを0-100に正規化。今回は小数点以下1桁のスコアが希望なので float で計算
    clutter_score = round(min(total_objects / MAX_OBJECTS, 1.0) * 100, 1) # 小数点以下1桁に丸める

    clutter_message = "散らかり具合: "
    if clutter_score == 0:
        clutter_message += "非常に整理されており、物体は検出されませんでした。"
    elif clutter_score < 25:
        clutter_message += "整理されています。少数の物体が検出されました。"
    elif clutter_score < 50:
        clutter_message += "やや散らかりが見られます。いくつかの物体が検出されました。"
    elif clutter_score < 75:
        clutter_message += "散らかっています。多くの物体が検出されました。"
    else:
        clutter_message += "非常に散らかっています。大量の物体が検出されました。"
    
    return clutter_score, clutter_message

def run_object_detection():
    """
    コマンドライン引数から設定を読み込み、YOLOv8を用いて物体検出を実行するスクリプト。
    検出結果は画像として保存され、詳細なログはJSONファイルとして出力される。
    さらに、物体の数に基づいて散らかり具合を算出し、表示・ログ出力する。
    """
    # 1. コマンドライン引数の設定
    parser = argparse.ArgumentParser(description="YOLOv8を用いた物体検出スクリプト。")
    parser.add_argument('image_filename', type=str,
                        help='検出対象の画像ファイル名（例: image_cf2b64.jpg）。')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                        help='使用するYOLOv8モデルのパスまたは名前（例: yolov8n.pt, yolov8s.pt）。')
    parser.add_argument('--conf', type=float, default=0.5,
                        help='検出結果の信頼度閾値。この値以上の信頼度のオブジェクトのみを検出とみなす。')
    parser.add_argument('--output_image', type=str, default=None,
                        help='検出結果を描画した画像の保存パス。指定しない場合、元のファイル名に "_detected" を付加して保存する。')
    parser.add_argument('--output_log', type=str, default=None,
                        help='検出結果の詳細ログ（JSON形式）の保存パス。指定しない場合、元のファイル名に "_log.json" を付加して保存する。')
    parser.add_argument('--show_window', action='store_true',
                        help='結果画像を表示するウィンドウを開くかどうか。デフォルトでは開かない。')
    args = parser.parse_args()

    # 画像ファイルの完全なパスを構築
    image_path_full = os.path.join(BASE_PHOTO_DIR, args.image_filename)

    # 2. YOLOv8モデルのロード
    try:
        print(f"Loading YOLO model: {args.model}")
        model = YOLO(args.model)
    except Exception as e:
        print(f"Error: Could not load YOLO model '{args.model}'. Please check the model path/name and your Ultralytics installation.")
        print(f"Details: {e}")
        return # スクリプトを終了

    # 3. 画像の読み込み
    print(f"Loading image: {image_path_full}")
    img = cv2.imread(image_path_full)
    if img is None:
        print(f"Error: Could not load image from '{image_path_full}'.")
        print("Please check if the file exists and is a valid image format.")
        return # スクリプトを終了

    # 画像の幅と高さを取得
    # img.shape は (height, width, channels) の順
    image_height, image_width, _ = img.shape

    # 4. 物体検出の実行
    print("Running object detection...")
    results = model(img, conf=args.conf)

    # 5. 検出結果の処理と集計
    detected_objects_count = 0
    object_counts = {}
    formatted_objects_for_json = []

    rendered_img = img.copy() 

    for i, r in enumerate(results):
        boxes = r.boxes 
        names = r.names 

        rendered_img = r.plot() 

        print(f"\n--- Detections for {os.path.basename(image_path_full)} (Confidence > {args.conf:.2f}) ---")
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

            x1, y1, x2, y2 = [int(coord) for coord in xyxy]
            width = x2 - x1
            height = y2 - y1
            
            # widthとheightは整数値の指定だったので、ここでは丸めずにint()に戻します
            formatted_objects_for_json.append({
                "x": x1,
                "y": y1,
                "width": width,
                "height": height
            })

    print(f"\nTotal objects detected: {detected_objects_count}")
    print("Object breakdown:")
    if not object_counts:
        print("  No objects counted.")
    else:
        for name, count in object_counts.items():
            print(f"  {name}: {count}")

    # --- 散らかり具合の算出と表示 ---
    clutter_score, clutter_message = calculate_clutter_score(detected_objects_count, object_counts)
    print(f"\n--- Clutter Assessment ---")
    print(f"Clutter Score (0-100): {clutter_score}")
    print(f"Assessment: {clutter_message}")
    # --- ここまで ---

    # 6. 結果画像の保存パスを自動生成 (コマンドライン引数で指定がなければ)
    output_image_path = args.output_image
    if output_image_path is None:
        base_filename_without_ext = os.path.splitext(args.image_filename)[0]
        output_image_path = os.path.join(BASE_PHOTO_DIR, f"{base_filename_without_ext}_detected.jpg")

    try:
        cv2.imwrite(output_image_path, rendered_img)
        print(f"Detection results image saved to '{output_image_path}'")
    except Exception as e:
        print(f"Error: Could not save the output image to '{output_image_path}'.")
        print(f"Details: {e}")

    # 7. 検出ログのJSON保存パスを自動生成 (コマンドライン引数で指定がなければ)
    output_log_path = args.output_log
    if output_log_path is None:
        base_filename_without_ext = os.path.splitext(args.image_filename)[0]
        output_log_path = os.path.join(BASE_PHOTO_DIR, f"{base_filename_without_ext}_log.json")

    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    output_json_data = {
        "image_width": image_width,    # 追加
        "image_height": image_height,  # 追加
        "score": clutter_score,        # 小数点以下1桁のfloat
        "timestamp": current_timestamp,
        "objects": formatted_objects_for_json
    }

    try:
        with open(output_log_path, 'w', encoding='utf-8') as f:
            json.dump(output_json_data, f, indent=2, ensure_ascii=False)
        print(f"Detection log saved to '{output_log_path}' in the specified format.")
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