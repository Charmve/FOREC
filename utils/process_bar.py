'''
Author: Charmve yidazhang1@gmail.com
Date: 2023-04-16 23:43:21
LastEditors: Charmve yidazhang1@gmail.com
LastEditTime: 2023-04-16 23:43:27
FilePath: /FOREC/utils/process_bar.py
Version: 1.0.1
Blogs: charmve.blog.csdn.net
GitHub: https://github.com/Charmve
Description: 

Copyright (c) 2023 by Charmve, All Rights Reserved. 
Licensed under the MIT License.
'''
import sys
import time

def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()

    
for i in progressbar(range(15), "Computing: ", 40):
    # do_something()
    time.sleep(0.1)