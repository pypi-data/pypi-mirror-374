#  -*- coding: utf-8 -*-
# Copyright (c) 2025/9/4$ cuba3. All rights reserved.
# @Time: 2025/9/4 16:38
# @Author: cuba3
# @Email: cuba3@163.com
# @File: demo.py
# @Organizations: OPN48
# @Project: cntc260

from tc260 import GBxmp

xmpAigcVal = {
    # GB45438—2025
    # https://www.xiongan.gov.cn/20250617/99e8309670814bdba91b3bcbfaca4e6c/2025061799e8309670814bdba91b3bcbfaca4e6c_38598ff9004470443c9195f1655adb29a0.pdf
    "Label": "1", #生成"1"，可能"2"，疑似"3"
    "ContentProducer": "公司名 或 备案号",
    "ProduceID": "A2012102390129310",
    "ReservedCode1": "",#本项目会自行根据xmpDcVal生成
    "ContentPropagator": "云空间服务商或你自己的服务器",
    "PropagateID": "此处传入空间名、文件名或唯一识别编号",
    "ReservedCode2": "computer,1|human,0|" #预留字段2可存储用于内容传播服务提供者自主开展安全防护,保护内容、标识完整性的信息;
}
xmpDcVal={"title":"标题cnTC260",
          "description":"作品描述cnTC260",
          "contentProducer":"工具或平台名称cnTC260",
          "creator":"作者cnTC260",
          "id": "100001",
          "rights":"Copyright 2025 作者/工具或平台名称 cntc260 保留所有权利。未经许可，不得商用。",
          "CreateDate":"2025-09-04T15:30:00+08:00"
          }

w = GBxmp("aigc.jpg", isTest=True)
# 这里可以自己加入哈希前缀，防止被竞争对手恶意伪造你的AIGC哈希签名
w.setHashPrefix('cnTC260_')
# 4. 写入标准元数据（可选，如 DC 命名空间的标题）,同时获取了ReservedCode1
w.setDCDic(xmpDcVal)
# 5. 写入扩展 XMP 元数据（自定义 AIGC 命名空间）
w.setAIGC(xmpAigcVal)
w.writeXmp()
