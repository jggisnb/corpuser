import subprocess
import zipfile

if __name__ == "__main__":
    import os
    import sys
    pid,zip_path = sys.argv[1:3]
    try:
        subprocess.Popen('taskkill /f /im nlp_tools.exe', shell=False)
    except Exception as e:
        print(e)
    import time
    time.sleep(1)
    file_list = zipfile.ZipFile(zip_path)
    info = file_list.infolist()

    ''' 1 计算解压后的文件总大小（单位：字节B） '''
    all_size = 0
    for i in info:
        all_size += i.file_size

    ''' 2 当前已解压的文件总大小（单位：字节B） '''
    now_size = 0

    for i in info:
        file_list.extract(i, os.path.dirname(zip_path))
        now_size += i.file_size
        print(f"解压进度：{int(float(now_size/all_size)*100)}/100")
    file_list.close()
    os.remove(zip_path)
    subprocess.Popen("nlp_tools.exe", shell=False)
