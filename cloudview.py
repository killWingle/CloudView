import sys
import time
import os
import subprocess
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon

# 自動pipインストール機能
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 必要なパッケージのインポート
try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtWebEngineWidgets import *
    from PyQt5.QtGui import QIcon
except ImportError as e:
    package_name = str(e).split("'")[1]
    print(f"{package_name}が見つかりません。インストールを試みます...")
    install(package_name)
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtWebEngineWidgets import *
    from PyQt5.QtGui import QIcon

# 設定を保存するファイル
SETTINGS_FILE = "settings.txt"

class Browser(QMainWindow):
    def __init__(self, darkmode="off"):
        super(Browser, self).__init__()
        self.setWindowTitle("Custom Browser")
        self.setGeometry(100, 100, 1200, 800)

        # アイコンを設定
        self.setWindowIcon(QIcon('app_icon.ico'))

        self.current_url = ""
        self.start_time = None
        self.search_engine = "https://search.yahoo.co.jp/search?p="  # デフォルトはGoogle
        self.start_page_url = "https://search.yahoo.co.jp/"  # スタートページのURL

        # 設定をファイルから読み込む
        self.load_settings()

        # ダークモード設定
        self.darkmode = darkmode

        # アドレスバーの設定（ここで初期化）
        self.url_bar = QLineEdit()
        self.url_bar.setReadOnly(True)
        self.url_bar.setStyleSheet("color: gray;")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.mousePressEvent = self.url_bar_clicked

        self.set_styles()  # スタイルを設定

        # ブラウザウィジェットの設定
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(self.start_page_url))

        # ユーザーエージェントを設定
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Chrome/119.0.0.0")

        self.browser.urlChanged.connect(self.update_url)
        self.browser.loadFinished.connect(self.update_title)
        self.browser.loadStarted.connect(self.start_timer)
        self.browser.loadProgress.connect(self.update_load_progress)

        # ナビゲーションバーの作成
        navbar = QToolBar()
        navbar.setMovable(False)
        self.addToolBar(navbar)

        # 戻るボタン
        back_btn = QAction('Back', self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        # 進むボタン
        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        # 更新ボタン
        reload_btn = QAction('Reload', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        # ホームボタン
        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        # アドレスバーをナビゲーションバーに追加
        navbar.addWidget(self.url_bar)

        # 全画面ボタンをアドレスバーの右に配置
        fullscreen_btn = QAction('Full Screen', self)
        fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        navbar.addAction(fullscreen_btn)

        # メインウィンドウにブラウザを設定
        self.setCentralWidget(self.browser)

        # 進捗バーの作成
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(False)

        # 進捗バーを下部に追加
        access_toolbar = QToolBar()
        access_toolbar.setMovable(False)
        access_toolbar.addWidget(self.progress_bar)
        self.addToolBar(Qt.BottomToolBarArea, access_toolbar)

        # ダウンロードマネージャーの設定
        profile.downloadRequested.connect(self.on_downloadRequested)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = f.readlines()
                for line in settings:
                    if line.startswith("darkmode"):
                        self.darkmode = line.split("=")[1].strip()
                    elif line.startswith("start_page"):
                        self.start_page_url = line.split("=")[1].strip()
                    elif line.startswith("search_engine"):
                        engine = line.split("=")[1].strip()
                        if engine == "Google":
                            self.search_engine = "https://www.google.com/search?q="
                        elif engine == "Yahoo Japan":
                            self.search_engine = "https://search.yahoo.co.jp/search?p="
                        elif engine == "Bing":
                            self.search_engine = "https://www.bing.com/search?q="

    def save_settings(self):
        with open(SETTINGS_FILE, 'w') as f:
            f.write(f"darkmode={self.darkmode}\n")
            f.write(f"start_page={self.start_page_url}\n")
            f.write(f"search_engine={self.search_engine}\n")

    def set_styles(self):
        if self.darkmode == "on":
            self.setStyleSheet("background-color: #222; color: white;")
            self.url_bar.setStyleSheet("color: white; background-color: #555;")
        else:
            self.setStyleSheet("background-color: white; color: black;")
            self.url_bar.setStyleSheet("color: gray;")

    def start_timer(self):
        self.start_time = time.time()

    def update_title(self):
        title = self.browser.page().title()
        self.setWindowTitle(title)
        self.url_bar.setText(self.current_url if self.current_url != self.start_page_url else "settings://start")
        self.url_bar.setReadOnly(True)

        if self.start_time:
            elapsed_time = time.time() - self.start_time
            self.progress_bar.setStyleSheet("QProgressBar { background-color: white; }")
            self.progress_bar.setFormat(f"{self.current_url} - Loaded in {elapsed_time:.2f} seconds")

    def update_url(self, q):
        self.current_url = q.toString()

    def url_bar_clicked(self, event):
        self.url_bar.setText(self.current_url)
        self.url_bar.setStyleSheet("color: black;")
        self.url_bar.setReadOnly(False)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if url == "settings://start":
            self.navigate_home()  # スタートページに移動
            return
        if url == "settings://now":
            self.show_settings()
            return

        if not url.startswith("http"):
            self.browser.setUrl(QUrl(self.search_engine + url))
        else:
            self.browser.setUrl(QUrl(url))

    def show_settings(self):
        settings_dialog = QDialog(self)
        settings_dialog.setWindowTitle("Settings")
        settings_dialog.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()

        # スタートページの設定
        start_page_label = QLabel("Start Page URL:")
        self.start_page_input = QLineEdit()
        self.start_page_input.setText(self.start_page_url)
        layout.addWidget(start_page_label)
        layout.addWidget(self.start_page_input)

        # 検索エンジンの選択
        search_engine_label = QLabel("Select Search Engine:")
        self.search_engine_combobox = QComboBox()
        self.search_engine_combobox.addItems(["Google", "Yahoo Japan", "Bing"])
        self.search_engine_combobox.currentIndexChanged.connect(self.change_search_engine)
        layout.addWidget(search_engine_label)
        layout.addWidget(self.search_engine_combobox)

        # ダークモード切替
        dark_mode_label = QLabel("Dark Mode:")
        self.dark_mode_checkbox = QCheckBox("Enable")
        self.dark_mode_checkbox.setChecked(self.darkmode == "on")
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        layout.addWidget(dark_mode_label)
        layout.addWidget(self.dark_mode_checkbox)

        # 保存ボタン
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        settings_dialog.setLayout(layout)
        settings_dialog.exec_()

    def change_search_engine(self, index):
        engines = ["Google", "Yahoo Japan", "Bing"]
        self.search_engine = f"https://{engines[index].lower()}.com/search?q="

    def toggle_dark_mode(self):
        if self.dark_mode_checkbox.isChecked():
            self.darkmode = "on"
        else:
            self.darkmode = "off"
        self.set_styles()
        self.save_settings()  # 設定を保存

    def navigate_home(self):
        self.browser.setUrl(QUrl(self.start_page_url))

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def update_load_progress(self, progress):
        self.progress_bar.setValue(progress)

    def on_downloadRequested(self, download):
        download_path = QFileDialog.getSaveFileName(self, "Save As", download.suggestedFilename())[0]
        if download_path:
            download.setPath(download_path)
            download.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())
