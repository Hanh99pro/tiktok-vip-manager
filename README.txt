Cách dùng:

1. Cài Flask:
   pip install flask

2. Đặt các file này trong thư mục tiktok_2:
   app.py
   gui/index.html
   gui/style.css
   gui/script.js

3. Đảm bảo cùng thư mục có:
   vip_manager.py
   nick1_token.txt
   nick2_token.txt
   nick3_token.txt
   folders/thoitrang/videos
   folders/thoitrang/pending
   folders/thoitrang/uploaded
   folders/thoitrang/captions.txt

4. Trong vip_manager.py phải có:
   TOPIC_FOLDER = os.environ.get("SELECTED_TOPIC", "thoitrang")
   WAIT_SECONDS = int(os.environ.get("WAIT_SECONDS", "240"))

5. Chạy:
   python app.py

6. Mở trình duyệt:
   http://127.0.0.1:5000