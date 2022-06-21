

if __name__ == "__main__":
    import os
    import sys
    import subprocess
    import zipfile
    import signal
    pid,zip_path = sys.argv[1:3]
    print(f"pid:{pid},zip path:{zip_path}")
    os.kill(int(pid),signal.SIGINT)

    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    subprocess.call('taskkill /f /t /im ' + "nlptools.exe", startupinfo=si)
    file_list = zipfile.ZipFile(zip_path)
    info = file_list.infolist()

    ''' 1 计算解压后的文件总大小（单位：字节B） '''
    all_size = 0
    for i in info:
        all_size += i.file_size
    all_size_str = str(int(all_size / 1024 / 1024)) + 'MB'
    ''' 2 当前已解压的文件总大小（单位：字节B） '''
    now_size = 0
    for i in info:
        file_list.extract(i, os.path.dirname(zip_path))
        now_size += i.file_size
        now_size_str = str(int(now_size / 1024 / 1024)) + 'MB'
        print(f'解压进度：{int(now_size / all_size * 100)}% ({now_size_str}/{all_size_str})')
    file_list.close()
    os.remove(zip_path)
    subprocess.call("nlptools.exe", startupinfo=si)
    exit(0)
