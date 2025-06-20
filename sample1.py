import tkinter as tk

def draw_objects(canvas, objects):
    canvas.delete("all")
    canvas.create_rectangle(0, 0, 400, 300, fill="lightgray")  # 机の範囲

    for obj in objects:
        x, y, w, h = obj["x"], obj["y"], obj["width"], obj["height"]
        canvas.create_rectangle(x, y, x + w, y + h, fill="red")

root = tk.Tk()
root.title("机の状態可視化")

canvas = tk.Canvas(root, width=400, height=300)
canvas.pack()

# 仮の入力データ
sample_objects = [
    {"x": 100, "y": 120, "width": 60, "height": 40},
    {"x": 220, "y": 150, "width": 30, "height": 20}
]

draw_objects(canvas, sample_objects)
root.mainloop()
