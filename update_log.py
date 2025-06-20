import json
import os

def update_log(input_path="data/new_input.json", log_path="data/log.json", max_history=10):
    if not os.path.exists(input_path):
        return False, "new_input.json not found"

    with open(input_path, "r") as f:
        new_data = json.load(f)

    try:
        with open(log_path, "r") as f:
            log_data = json.load(f)
    except FileNotFoundError:
        log_data = {"history": []}

    # 上書き保存するデータ
    log_data["score"] = new_data["score"]
    log_data["timestamp"] = new_data["timestamp"]
    log_data["objects"] = new_data["objects"]
    log_data["image_width"] = new_data.get("image_width", 640)
    log_data["image_height"] = new_data.get("image_height", 480)

    # 履歴の更新
    log_data["history"].append({
        "timestamp": new_data["timestamp"],
        "score": new_data["score"]
    })
    log_data["history"] = log_data["history"][-max_history:]

    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=2)

    return True, "log.json updated successfully"
