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


# 示例调用：写入到 ./aigc.jpg

xmpDcVal={"title":"标题cnTC260",
          "description":"作品描述cnTC260",
          "contentProducer":"工具或平台名称cnTC260",
          "creator":"作者cnTC260",
          "id": "100001",
          "rights":"Copyright 2025 作者/工具或平台名称 cntc260 保留所有权利。未经许可，不得商用。",
          "CreateDate":"2025-09-04T15:30:00+08:00"
          }
xmpAigcVal = {
    # GB45438—2025
    # https://www.xiongan.gov.cn/20250617/99e8309670814bdba91b3bcbfaca4e6c/2025061799e8309670814bdba91b3bcbfaca4e6c_38598ff9004470443c9195f1655adb29a0.pdf
    # 生成合成标签要素由 Label表示,取值为value1,应符合以下要求。
    # 1) 存储内容属于、可能、疑似为人工智能生成合成的属性信息:
    # 属于人工智能生成合成内容的,value1 的值取1;
    # 可能为人工智能生成合成内容的,value1 的值取2;
    # 疑似为人工智能生成合成内容的,value1 的值取3。
    # 2) 类型为字符串。
    "Label": "1",
    # ) 生成合成服务提供者要素由 ContentProducer表示,取值为value2,应符合以下要求:
    # 1) 存储生成合成服务提供者的名称或编码;
    # 2) 类型为字符串。
    "ContentProducer": "公司名 或 备案号",
    # 内容制作编号要素由 ProduceID表示,取值为value3,应符合以下要求:
    # 1) 存储生成合成服务提供者对该【内容的唯一编号】;
    # 2) 类型为字符串。
    "ProduceID": "A2012102390129310",

    # 预留字段1由 ReservedCode1表示,取值为value4,要求如下:
    # 1) 可存储用于生成合成服务提供者自主开展安全防护,保护内容、标识完整性的信息;
    # 2) 类型应为字符串。
    # 注2:生成合成服务提供者使用预留字段1进行文件元数据隐式标识安全防护的示例见附录 F的 F.4。
    # 生成合成服务提供者使用杂凑算法对文件元数据信息进行数字签名,并将结果存储在预留字段1
    # 中的示例如下所示。
    # "ReservedCode1":"e862483430d978cbf828b8b24296ef9328d843a0"
    # by cuba3 建议杂凑算法（SHA-256，性能有问题可以考虑降低为MD5）
    "ReservedCode1": "",

    # g) 内容传播服务提供者要素由 ContentPropagator表示,取值为value5,应符合以下要求:
    # 1) 存储内容传播服务提供者的名称或编码;
    # 2) 类型为字符串。
    "ContentPropagator": "云空间服务商或你自己的服务器",

    # h) 内容传播编号要素由 PropagateID表示,取值为value6,应符合以下要求:
    # 1) 存储内容传播服务提供者对该内容的唯一编号;
    # 2) 类型为字符串。
    "PropagateID": "此处传入空间名、文件名或唯一识别编号",

    # ) 预留字段2由 ReservedCode2表示,取值为value7,要求如下:
    # 1) 可存储用于内容传播服务提供者自主开展安全防护,保护内容、标识完整性的信息;
    # 2) 类型应为字符串。
    "ReservedCode2": "computer,1|human,0|"
}

# if __name__ == "__main__":
#     w = GBxmp("./aigc.jpg")
#     # 4. 写入标准元数据（可选，如 DC 命名空间的标题）,同时获取了ReservedCode1
#     w.setDCDic(xmpDcVal)
#     # 这里可以自己加入哈希前缀，防止被竞争对手恶意伪造你的AIGC哈希签名
#     w.setHashPrefix('cnTC260_')
#     # 5. 写入扩展 XMP 元数据（自定义 AIGC 命名空间）
#     w.setAIGC(xmpAigcVal)
#     w.writeXmp()

