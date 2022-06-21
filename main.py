import os

from window import MainWindow


def __check_update():
    try:
        import json
        import requests
        with open("update.json","r",encoding="utf-8") as rf:
            update_json_str = rf.read().strip()
            update_dict = json.loads(update_json_str)["config"]
            print(update_dict)
        ip,version = update_dict["ip"],update_dict["version"]
        header = "http://"+ip
        resp = requests.get(header+"/update.json")
        remote_update_dict = json.loads(resp.text)["config"]
        remote_version = remote_update_dict["version"]
        v1 = int(version[0])*100 + int(version[2]) * 10 + int(version[4]) * 1
        v2 = int(remote_version[0])*100 + int(remote_version[2]) * 10 + int(remote_version[4]) * 1
        if v2 > v1:
            pwd = os.path.dirname(os.path.realpath(sys.argv[0]))
            return header,pwd,remote_version
        return False
    except Exception as e:
        return False

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from view.update import dialog as update_dialog
    app = QApplication(sys.argv[1:])
    checked = __check_update()
    if checked:
        url, pwd, version = checked
        dialog = update_dialog(url, pwd, version)
        dialog.setGeometry(100, 50, 400, 100)
        dialog.setWindowTitle("更新程序")
        # dialog.close_emit.connect(__dialog_close_sgl)
    else:
        window = MainWindow()
        window.setGeometry(100,50,1350,800)
        window.setWindowTitle("nlp tools")
        window.show()
    sys.exit(app.exec_())