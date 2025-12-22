# > override
# >> append

# file = open('logs.txt','w')
#
# if file.writable():
#     file.write('or\n')
#     file.write('roman')
#
# file.close()
# file = open('logs.txt', 'r+')
# lines = ['hga', 'fafa']
# print(file.tell())  # where is the cursor
# file.seek(0)
# for f in file.readlines():
#     print(f)
# # if file.writable():
# #     file.write('this is the r+ babyyyyy\n')
# file.close()

# with open('log.txt') as file:
# file.write()

import datetime


class Logger:

    def __init__(self, file):
        self.file = file

    def log(self, data):
        with open(self.file, 'a+') as f:
            f.write(f'[{datetime.datetime.now().hour}:{datetime.datetime.now().minute}]  {data} \n')