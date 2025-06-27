import json
import os

def rotate_data_if_needed(data):
    """縦長画像なら90度回転した形に変換する"""
    if data["image_height"] > data["image_width"]:
        rotated_objects = []
        for obj in data["objects"]:
            new_x = obj["y"]
            new_y = data["image_width"] - obj["x"] - obj["width"]
            new_width = obj["height"]
            new_height = obj["width"]
            rotated_objects.append({
                "x": new_x,
                "y": new_y,
                "width": new_width,
                "height": new_height
            })
        # imageサイズとobject座標を入れ替えたものに置き換え
        data["objects"] = rotated_objects
        data["image_width"], data["image_height"] = data["image_height"], data["image_width"]
    return data

def update_log(input_path="data/new_input.json", log_path="data/log.json", max_history=10):
    if not os.path.exists(input_path):
        return False, "new_input.json not found"

    with open(input_path, "r") as f:
        new_data = json.load(f)

    # タイムスタンプチェック用
    new_timestamp = new_data.get("timestamp")
    try:
        with open(log_path, "r") as f:
            log_data = json.load(f)
            last_timestamp = log_data.get("timestamp")
    except FileNotFoundError:
        log_data = {"history": []}
        last_timestamp = None

    if new_timestamp == last_timestamp:
        return False, "すでに最新のデータです（更新しません）"

    # ✅ 縦長なら事前に回転
    new_data = rotate_data_if_needed(new_data)

    # log.jsonの更新
    log_data["score"] = new_data["score"]
    log_data["timestamp"] = new_data["timestamp"]
    log_data["image_width"] = new_data["image_width"]
    log_data["image_height"] = new_data["image_height"]
    log_data["objects"] = new_data["objects"]

    log_data.setdefault("history", [])
    log_data["history"].append({
        "timestamp": new_data["timestamp"],
        "score": new_data["score"]
    })
    log_data["history"] = log_data["history"][-max_history:]

    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=2)

    return True, "log.json を更新しました"
