# image writer

## なにこれ

Raspbianのイメージとか/dev/zeroを、SDカードとかにddできるやつ

## いるもの

* Raspberry Pi
* [Waveshare 1.3 inch OLED HAT](https://www.waveshare.com/wiki/1.3inch_OLED_HAT)
* Ansible(セットアップに使う)

## セットアップ

* Ansibleでガッとやるといい感じになります(TODO)

## 使い方

### 準備

* /home/piにRaspbianのイメージファイルをzipファイルの状態で放り込みます
* Raspberry Piを再起動します

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

## Credit, License

Copyright 2019 Akkiesoft (akkiesoft@marokun.net)

[The MIT License](https://opensource.org/licenses/mit-license.php)
