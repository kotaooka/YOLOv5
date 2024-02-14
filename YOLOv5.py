import cv2
import torch
import time

# pip install torch torchvision
# pip install yolov5

# モデルのロード
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# カメラの設定
cap = cv2.VideoCapture(0)

# ウィンドウの名前を指定
window_name = 'YOLOv5 - Press q key to exit'

# ウィンドウの作成とサイズの指定
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 800, 600)  # ウィンドウのサイズを800x600に設定

# 次の保存時刻
next_save_time = time.time()

while True:
    # フレームの取得
    ret, frame = cap.read()

    # YOLOv5で物体検出
    results = model(frame)

    # 検出結果の描画
    results.render()

    # 描画結果の表示
    cv2.imshow(window_name, results.ims[0])

    # 現在の時間が次の保存時刻を超えていたら画像を保存
    if time.time() > next_save_time:
        # jpgファイル名（現在のUNIX時間）
        filename = f"{int(time.time())}.jpg"
        # 画像を保存
        cv2.imwrite(filename, results.ims[0])
        # 次の保存時刻を更新（現在時刻+1分）
        next_save_time = time.time() + 1 * 60

    # 'q'キーが押されたら終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# カメラのリリース
cap.release()

# ウィンドウのクローズ
cv2.destroyAllWindows()
