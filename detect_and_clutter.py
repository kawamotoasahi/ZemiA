import argparse
import cv2
import json
import os
from ultralytics import YOLO
from datetime import datetime # datetimeモジュールをインポート

def calculate_clutter_score(total_objects: int, object_counts: dict) -> tuple[int, str]:
    """
    検出された物体の数に基づいて散らかり具合のスコア（0-100）と評価メッセージを算出します。
    
    Args:
        total_objects (int): 検出された物体の総数。
        object_counts (dict): 各物体クラスごとの検出数。

    Returns:
        tuple[int, str]: (散らかりスコア, 散らかり具合の評価メッセージ)
    """
    # --- スコア正規化のための設定 ---
    # 想定される最小物体数（完全に整理されている状態）
    MIN_OBJECTS = 0 
    # 想定される最大物体数（最も散らかっていると見なす上限）
    # この値は、検出対象の環境や用途に合わせて調整してください。
    # 例：机の上なら15-20、広い部屋なら50-100など。
    MAX_OBJECTS = 20 # 仮に20個で最大（スコア100）と設定

    # スコアを0-100に正規化
    clutter_score = int(min(total_objects / MAX_OBJECTS, 1.0) * 100)
    
    # 散らかり具合の評価メッセージを生成 (表示用。JSONには直接含めないが、ここでは残す)
    clutter_message = "散らかり具合: "
    if clutter_score == 0:
        clutter_message += "非常に整理されており、物体は検出されませんでした。"
    elif clutter_score < 25: # 0-24
        clutter_message += "整理されています。少数の物体が検出されました。"
    elif clutter_score < 50: # 25-49
        clutter_message += "やや散らかりが見られます。いくつかの物体が検出されました。"
    elif clutter_score < 75: # 50-74
        clutter_message += "散らかっています。多くの物体が検出されました。"
    else: # 75-100
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
    results = model(img, conf=args.conf)

    # 5. 検出結果の処理と集計
    detected_objects_count = 0
    object_counts = {}
    
    # 新しいJSON形式に対応するためのリスト
    formatted_objects_for_json = []

    rendered_img = img.copy() 

    for i, r in enumerate(results):
        boxes = r.boxes 
        names = r.names 

        rendered_img = r.plot() 

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

            # 新しいJSON形式用のオブジェクトデータを追加
            x1, y1, x2, y2 = [int(coord) for coord in xyxy]
            width = x2 - x1
            height = y2 - y1
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

    # 現在のタイムスタンプを取得
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 新しいJSON出力形式のデータ
    output_json_data = {
        "score": round(clutter_score, 1), # スコアを小数点以下1桁に丸める
        "timestamp": current_timestamp,
        "objects": formatted_objects_for_json
    }

    try:
        with open(output_log_path, 'w', encoding='utf-8') as f:
            json.dump(output_json_data, f, indent=2, ensure_ascii=False) # indent=2で見やすく、ensure_ascii=Falseで日本語もそのまま出力
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