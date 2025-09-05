# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-08-31 17:41
# @Author : 毛鹏
import json
from mangoautomation.uidrive import *
from mangotools.decorator import func_info

print(json.dumps(func_info, ensure_ascii=False, indent=4))
with open('ope.json', 'w') as f:
    f.write(json.dumps(func_info, ensure_ascii=False, indent=4))
