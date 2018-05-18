# TimeCard
slackのスラッシュコマンドで勤怠管理をします。

### コマンド
- `/start memo` : 勤務開始
- `/rests memo` : 休憩開始
- `/reste memo` : 休憩終了
- `/restm HH:MM~HH:MM` : 休憩時間を追加 HH(hour):MM(minute)形式で入力
- `/end memo` : 勤務終了

### 説明
`/restm`コマンド以外は任意で一緒にメモを残すことができます

### 環境
- python3.6
- falcon + gunicorn + nginx + MongoDB + Ubuntu16.04
- その他ライブラリ類はpip-requirements.txtに

Dockerfileあるけどまだ機能してないです

restbコマンド実装しました。
