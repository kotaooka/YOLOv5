import cv2
import torch

# pip install torch torchvision
# pip install yolov5

# モデルのロード
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# カメラの設定
cap = cv2.VideoCapture(0)

while True:
    # フレームの取得
    ret, frame = cap.read()

    # YOLOv5で物体検出
    results = model(frame)

    # 検出結果の描画
    results.render()

    # 描画結果の表示
    cv2.imshow('YOLOv5', results.ims[0])

    # 'q'キーが押されたら終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# カメラのリリース
cap.release()

# ウィンドウのクローズ
cv2.destroyAllWindows()
