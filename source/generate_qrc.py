
import os

images = os.listdir("image")
head = '''<RCC>
	<qresource>
'''
content = ""
tail = '''	</qresource>
</RCC>
'''
for item in images:
    content += f"\t\t<file alias = '{item}'>/image/{item}</file>\n"
with open("image.qrc","w",encoding="utf-8") as wf:
    wf.write(head+content+tail)

os.system(r"pyrcc5 -o image.py image.qrc")
