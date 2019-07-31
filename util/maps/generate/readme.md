#road network
##数据集
OSM数据文件：interpreter

##路网生成代码组成
- xml2json.py 处理osm文件，从xml格式中提取way和node，得到*_node.josn和*_way.json
  + 只保留带Highway/Railway/Waterway/Aerialway (不包括Aeroway)，计算包含在这个范围内的Way比例，打印所有Way Tag值的集合
- linearRoadGenerator.py 根据*_node.json和*_way.json得到路网，保存在way.json
  + 计算每个Way的中间节点线段斜率，以及每个Way的所有线段斜率的方差系数，看是否都是直线(大部分不是，方差35度)
  + 将每个Way切分为多个小段，每个小段内部方向角度不超过一个范围(宽度为10度)
- roadNetworkGenerator.py 根据way.json生成路网，保存为road-network.json

##运行环境
python3

###运行方法
依次运行上述代码文件