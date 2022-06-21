import zipfile
import signal

if __name__ == "__main__":
    import os
    import sys
    pid,zip_path = sys.argv[1:3]
    print(pid,zip_path)
    os.kill(int(pid),signal.SIGINT)
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
        print(int(now_size / all_size * 100) + 100)
    file_list.close()
    os.remove(zip_path)
    os.system("main.exe")
