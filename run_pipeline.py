import os
import subprocess
from conversion.generate_new_input import convert_to_new_input

def run_pipeline(image_path):
    # 1. スコア出力用のパス設定
    score_output_path = "input/score_output.json"

    # 2. YOLO + スコア算出の解析スクリプト実行
    command = [
        "python3", "analysis/generate_score_output.py",
        image_path,
        "--output", score_output_path
    ]
    print("🔍 Running object detection and score calculation...")
    subprocess.run(command, check=True)

    # 3. score_output.json → new_input.json 変換
    print("🛠️  Converting score_output.json to new_input.json...")
    convert_to_new_input(score_output_path)

    print("✅ Pipeline complete: new_input.json is ready!")

# 使用例
if __name__ == "__main__":
    run_pipeline("data/images/sample.jpg")
