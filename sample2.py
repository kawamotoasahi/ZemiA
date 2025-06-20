import matplotlib.pyplot as plt
from datetime import datetime

# 仮のスコア履歴データ
history = [
    {"timestamp": "2025-06-06 14:00", "score": 25},
    {"timestamp": "2025-06-06 14:10", "score": 42},
    {"timestamp": "2025-06-06 14:20", "score": 68},
    {"timestamp": "2025-06-06 14:30", "score": 38}
]

times = [datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M") for d in history]
scores = [d["score"] for d in history]

plt.figure(figsize=(8, 4))
plt.plot(times, scores, marker='o')
plt.title("散らかりスコアの履歴")
plt.xlabel("時刻")
plt.ylabel("スコア")
plt.grid(True)
plt.tight_layout()
plt.show()
