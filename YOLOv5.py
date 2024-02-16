import cv2
import torch
import time
import os
import configparser
from tkinter import Tk, filedialog

def get_setting_from_console(setting_name, prompt_message, input_type=str):
    while True:
        user_input = input(prompt_message)
        try:
            return input_type(user_input)
        except ValueError:
            print(f"Invalid input for {setting_name}. Please enter a valid value.")

def get_photo_directory():
    while True:
        choice = input("画像を保存するディレクトリを指定しますか？ (yes/no): ").lower()
        if choice in ['yes', 'no']:
            break
        else:
            print("有効な入力ではありません。 'yes' または 'no' を入力してください。")

    if choice == 'yes':
        photo_dir = input("画像を保存するディレクトリのパスを入力してください: ")
        while not os.path.exists(photo_dir):
            print("指定されたディレクトリが存在しません。")
            photo_dir = input("画像を保存するディレクトリのパスを入力してください: ")
    else:
        photo_dir = os.path.join(os.path.dirname(__file__), 'photo')
        print("画像をPythonスクリプトと同じディレクトリに保存します。")

    return photo_dir

def choose_image_file():
    root = Tk()
    root.withdraw()  # メインウィンドウを表示しないように設定

    file_path = filedialog.askopenfilename()
    if file_path == '':
        print("ファイルが選択されませんでした。")
        return None
    else:
        return file_path

# キー操作の説明をウィンドウに表示する関数
def show_instructions(image, instructions):
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (10, 30)  # 説明の表示位置を調整
    fontScale = 1
    color = (255, 255, 255)
    thickness = 2
    image = cv2.putText(image, instructions, org, font, fontScale, color, thickness, cv2.LINE_AA)
    return image

# スクリプトのディレクトリを取得
script_dir = os.path.dirname(__file__)

# 設定ファイルのパス
config_file = os.path.join(script_dir, 'config.ini')

# 設定の読み込みまたは新規作成
config = configparser.ConfigParser()

if os.path.exists(config_file):
    config.read(config_file)
else:
    print("config.iniファイルが見つかりませんでした。新しいファイルを作成します。")

    # 新しいセクションを追加
    config['Settings'] = {}

    # プロキシの設定
    while True:
        proxy_enabled = input("プロキシを使用しますか？ (yes/no): ").lower()
        if proxy_enabled in ['yes', 'no']:
            break
        else:
            print("有効な入力ではありません。 'yes' または 'no' を入力してください。")

    if proxy_enabled == 'yes':
        proxy_address = input("プロキシのアドレスを入力してください（例: http://proxy.example.com:8080）: ")
    else:
        proxy_address = ""

    # ウィンドウのサイズ
    window_size_x = get_setting_from_console("window size x", "ウィンドウの横幅を入力してください: ", int)
    window_size_y = get_setting_from_console("window size y", "ウィンドウの縦幅を入力してください: ", int)

    # 画像保存間隔
    save_interval_minutes = get_setting_from_console("save interval", "画像を保存する間隔（分）を入力してください: ", int)

    # 画像保存ディレクトリ
    photo_dir = get_photo_directory()

    # 設定をconfigに追加
    config['Settings'] = {
        'ProxyEnabled': str(proxy_enabled == 'yes'),
        'ProxyAddress': proxy_address,
        'WindowSizeX': str(window_size_x),
        'WindowSizeY': str(window_size_y),
        'SaveIntervalMinutes': str(save_interval_minutes),
        'PhotoDirectory': photo_dir
    }

    # 設定をファイルに保存
    with open(config_file, 'w') as configfile:
        config.write(configfile)

# プロキシ設定
proxy_enabled = config.getboolean('Settings', 'ProxyEnabled')
if proxy_enabled:
    proxy_address = config.get('Settings', 'ProxyAddress')
    os.environ['http_proxy'] = proxy_address
    os.environ['https_proxy'] = proxy_address

# ウィンドウサイズの設定
window_size_x = config.getint('Settings', 'WindowSizeX')
window_size_y = config.getint('Settings', 'WindowSizeY')

# 画像保存間隔の設定
save_interval_minutes = config.getint('Settings', 'SaveIntervalMinutes')
next_save_time = time.time() + save_interval_minutes * 60

# 画像保存用のディレクトリを設定
photo_dir = config.get('Settings', 'PhotoDirectory')

# モデルのダウンロードディレクトリを設定
download_dir = os.path.join(script_dir, 'models')  # モデルを保存するディレクトリ名を指定
torch.hub.set_dir(download_dir)

# モデルのロード
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# 画像ファイルまたはカメラの選択
choice = input("カメラを使いますか？ 画像ファイルを使いますか？ (camera/file): ").lower()
if choice == 'camera':
    # カメラの設定
    cap = cv2.VideoCapture(0)
else:
    # 画像ファイルの選択
    image_file = choose_image_file()
    if image_file is None:
        print("プログラムを終了します。")
        exit()
    cap = cv2.VideoCapture(image_file)

# ウィンドウの名前を指定
window_name = 'YOLOv5'

# ウィンドウの作成
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# ウィンドウのサイズを設定
cv2.resizeWindow(window_name, window_size_x, window_size_y)

while True:
    # フレームの取得
    ret, frame = cap.read()

    if ret:  # フレームの取得に成功した場合のみ処理を続行
        # YOLOv5で物体検出
        results = model(frame)

        # 検出結果の描画
        results.render()

        # キー操作の説明を画面に表示
        frame = show_instructions(results.ims[0], "Press C for camera,F for file,Q to exit")

        # 描画結果の表示
        cv2.imshow(window_name, frame)

        # 現在の時間が次の保存時刻を超えていたら画像を保存
        if time.time() > next_save_time:
            # jpgファイル名（現在のUNIX時間）
            filename = os.path.join(photo_dir, f"{int(time.time())}.jpg")
            # 画像を保存
            cv2.imwrite(filename, results.ims[0])
            # 次の保存時刻を更新
            next_save_time += save_interval_minutes * 60

    # キー入力を待ち、'c'が押されたらカメラ、'f'が押されたら画像ファイルを選択
    key = cv2.waitKey(1)
    if key & 0xFF == ord('c'):
        choice = 'camera'
        cap.release()
        cap = cv2.VideoCapture(0)
    elif key & 0xFF == ord('f'):
        choice = 'file'
        cap.release()
        image_file = choose_image_file()
        if image_file is None:
            print("プログラムを終了します。")
            exit()
        cap = cv2.VideoCapture(image_file)
    # 'q'キーが押されたら終了
    elif key & 0xFF == ord('q'):
        break

# カメラのリリース
cap.release()

# ウィンドウのクローズ
cv2.destroyAllWindows()
