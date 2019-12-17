# image writer

## なにこれ

Raspbianのイメージとか/dev/zeroを、SDカードとかにddできるやつ

## いるもの

* Raspberry Pi
* [Waveshare 1.3 inch OLED HAT](https://www.waveshare.com/wiki/1.3inch_OLED_HAT)
* USB-MicroSD カードリーダー
* Ansible(セットアップに使う)

## セットアップ

Ansibleでセットアップする手順です。

* Waveshare 1.3 inch OLED HATをセットして起動します
* Raspbianをホームディレクトリにダウンロードします

```
(Raspbianの用意。お好みで)
pi@raspberrypi:~ $ wget https://downloads.raspberrypi.org/raspbian_latest
pi@raspberrypi:~ $ wget https://downloads.raspberrypi.org/raspbian_lite_latest
```

* SSH鍵を生成し、自分で自分にSSH鍵でログインできるようにします

```
pi@raspberrypi:~ $ ssh-keygen
(聞かれた内容はすべてそのままEnterを入力)
pi@raspberrypi:~ $ ssh-copy-id -i ~/.ssh/id_rsa pi@raspberrypi.local
(piユーザーのパスワードを聞かれるので入力)
pi@raspberrypi:~ $ ssh raspberrypi.local
pi@raspberrypi:~ $ exit
(※上記SSHから抜ける)
```

* 必要なパッケージをインストールします

```
pi@raspberrypi:~ $ sudo apt update
pi@raspberrypi:~ $ sudo apt install -y git ansible
```

* Githubからリポジトリをcloneします

```
pi@raspberrypi:~ $ git clone https://github.com/akkiesoft/imagewriter imagewriter-setup
```

* Ansible Playbookのディレクトリに移動して、Playbookを実行します

```
pi@raspberrypi:~ $ cd imagewriter-setup/ansible
pi@raspberrypi:~ $ ansible-playbook -i hosts main.yml
```

## 使い方

### イメージの選択の仕方

* KEY1をおします
* Select Image Fileにカーソルがあった状態で、ジョイスティックのセンターボタンを押します
* ジョイスティックの上下でカーソルを動かしてイメージを選択します
    * zeroはSDカードのゼロ消去モードです
* KEY1を押してメイン画面に戻るか、ジョイスティックのセンターボタンを押してメニューに戻ります

### SSH機能

* KEY1をおします
* SSH Configurationにカーソルがあった状態で、ジョイスティックのセンターボタンを押します
* Disable(デフォルト)かEnableを選択します
* KEY1を押してメイン画面に戻るか、ジョイスティックのセンターボタンを押してメニューに戻ります

### 書き込みの実行

* カードリーダーをRaspberry Piに接続します
* SDカードを挿入します
* /dev/sda detectedと表示された後、Press KEY2 to writeが表示されたらKEY2ボタンを押します
* 書き込み中は画面に書き込み状況が表示されます
* 書き込みが終わるとDone!と表示されたらSDカードを取り外します

## imagewriter-i2c.py

I2C接続のOLEDモジュール(SSD1306)とボタン2つを使ったバージョンです。

ボタンはGPIO16がイメージの選択、GPIO17が書き込み開始ボタンです。

SSHの有効化等は設定ファイルで記述してください（設定内容は共通です）。

## Credit, License

Copyright 2019 Akkiesoft (akkiesoft@marokun.net)

[The MIT License](https://opensource.org/licenses/mit-license.php)
