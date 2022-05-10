
print("a"+str(chr(95)))

# import subprocess
# cmd = 'ping www.baidu.com'
# screenData = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
# aa = []
# while True:
#     line = screenData.stdout.readline()
#     a = line.decode("gbk").strip("b'").strip()
#     if len(a):
#         aa.append(a)
#     if line == b'' or subprocess.Popen.poll(screenData) == 0:
#         screenData.stdout.close()
#         break
#
# print(aa)

# import re
# with open(r"D:\Users\Administrator\Desktop\github\lawyee_ner_predict\ner\engines\model.py","r",encoding="utf-8") as rf:
#     code = rf.read()
#     class_name = re.findall("class\s+([\w\d_]+?)\(",code)
#
#
#     # def call(self, inputs, inputs_length, targets, training=None):
#     params = re.findall("def\s+call\s*\(\s*self([\w\W]+?)\)",code)
#     if len(params):
#         pass
#     print(class_name)

