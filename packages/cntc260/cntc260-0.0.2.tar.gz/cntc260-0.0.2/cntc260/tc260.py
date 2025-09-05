#  -*- coding: utf-8 -*-
# Copyright (c) 2025/9/4 cuba3. All rights reserved.
# @Time: 2025/9/4 16:34
# @Author: cuba3
# @Email: cuba3@163.com
# @File: tc260.py
# @Organizations: OPN48
# @Project: cntc260

import json

try:
    from libxmp import XMPFiles, XMPMeta
    from libxmp.consts import XMP_NS_DC
except:
    import os
    import sys
    if sys.platform == "darwin":
        cmd = 'brew install exempi'
    elif sys.platform == "linux":
        cmd = 'sudo apt-get install libexempi3'
    else:
        print("请手动安装 exempi / please install exempi")
    os.system(cmd)
    os.system('pip3 install python-xmp-toolkit')
    from libxmp import XMPFiles, XMPMeta
    from libxmp.consts import XMP_NS_DC  # 引入 Dublin Core 标准命名空间

class GBxmp:
    def __init__(self,filePath='',isTest=False):
        self.filePath = filePath
        # TC260-PG-20258A
        # 1. 注册自定义命名空间（前缀 AIGC，URI 为示例地址）
        self.AIGC_NS_URI = "http://www.tc260.org.cn/ns/AIGC/1.0/"
        self.AIGC_NS_PREFIX = "TC260"
        self.AIGC='AIGC'
        self.hashPrefix = 'cnTC260_'
        self.reservedCode1=''

        # 标准签名字符
        self.RESERVEDCODE1='ReservedCode1'

        self.OK='ok'

        self.isTest=isTest

        # 全局注册,文件写入时会更新
        XMPMeta.register_namespace(self.AIGC_NS_URI, self.AIGC_NS_PREFIX)
        # 2. 打开文件准备写入（open_forupdate=True 表示可写）
        self.xmpfile = XMPFiles(file_path=self.filePath, open_forupdate=True)
        # 3. 获取现有 XMP 元数据（若无则创建新实例）
        self.xmp = self.xmpfile.get_xmp()
        if self.xmp is None:
            # 若无现有元数据，创建新实例
            self.xmp = XMPMeta()
        # 打印调试
        if self.isTest:
            print('=== cntc260 === before===','\n',self.xmp,'\n')

    def setDC(self,key,value):
        try:
            self.xmp.set_property(XMP_NS_DC, key, value)
        except:
            print(f'XMP_NS_DC {key} is already exists')
    def setHashPrefix(self,prefix):
        self.hashPrefix=prefix
    def setDCDic(self,dic):
        for key in dic:
            self.setDC(key,dic[key])
        self.reservedCode1 = hash(self.hashPrefix + str(dic))
    def setAIGC(self,xmpAigcVal):
        # 5. 写入扩展 XMP 元数据（自定义 AIGC 命名空间）

        xmpAigcVal[self.RESERVEDCODE1]=self.reservedCode1
        self.xmp.set_property(self.AIGC_NS_URI, self.AIGC, json.dumps(xmpAigcVal, ensure_ascii=False))  # 基于 URI 写入
    def writeXmp(self):
        try:
            # 6. 保存修改到文件，成功返回1,失败打印结果，返回0
            self.xmpfile.put_xmp(self.xmp)
            if self.isTest:
                print('=== cntc260 === after ===', '\n', self.xmp, '\n')
            print(self.OK,self.filePath)
            return (1,self.OK)
        except Exception as e:
            print(e)
            return (0,e)
        finally:
            # 7. 关闭文件释放资源
            self.xmpfile.close_file()


