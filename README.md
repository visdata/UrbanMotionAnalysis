## 说明文档 Description

状态预测数据处理以及可视化查询后段接口说明文档。




### 离线处理部分 Offline processing section
```
# 在原始数据上清洗成分天存储的数据，并添加属性
# -d 输入文件夹
# -p 输出文件夹
# -i 原始文件个数（从0开始编号）
python segRawData.py -d /datahouse/zhtan/datasets/VIS-rawdata-region-c-sample  -p /datahouse/tao.jiang -i 3999

# 在分天存储的基础上作了进一步处理
python segDayDataForTripFlow.py

# trip 切分与聚类以及种子方向挑选工作
# [spaceInterval 为实际的距离参数，选择包括0, 200, 400, 800, 1600, 3200]
# -d 输入文件夹
# -p 输出文件夹
# -e 密度数
# -x 时段编号
# -k 总边数除以该值得到 min_samples
python tripFlowCal.py -d /tripflow/spaceInterval/ -p /tripflow/spaceInterval/ -e 2 -x 9 -k 24000
```

### 在线调用部分 Online call section

```
# 生成 treeMap 脚本
# [本脚本运行不再设置提示参数名 直接从参数数组中顺序读取]
# [参数意义如下，按顺序填入，不可空缺]
# 输入文件夹
# 输出文件夹
# 处理的小时 ID
# treeMap 比例
# search_angle
# seed_strength
# tree_width
# jump_length
# seed_unit
# grid_dirnum
python treeMapCal.py /datahouse/tripflow/200 /datahouse/tripflow/200 9 0.01 60 0.1 1 3 basic -1
```

```
# 在线生成 angleCluster 脚本
python angleClusterCal.py /datahouse/tripflow/200 /datahouse/tripflow/200 9 0.01 100
```

