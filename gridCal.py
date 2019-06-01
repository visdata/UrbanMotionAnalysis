__author__ = 'lenovo'
from util.tripFlow.base import getFormatGID
import numpy as np
import json
#point = [116.31929397583009,39.8959420035726]

#print(getFormatGID(point)['gid'])

# point1 = [116.3235855102539, 39.89317623884907]
# point2 = [116.42074584960939, 40.00322665241964]
# point3 = [116.2185287475586, 40.227711007715136]
# point4 = [116.69815063476564, 39.78980820192016]
# point5 = [116.45507812500001,39.91097066634995]
# point6 = [116.28890991210939,39.96204017008559]
# point7 = [116.38092041015626,39.86407956071788]
# point8 = [115.97442626953126,40.48109956299565]
# point9 = [ 116.33525848388673,39.953265311384946]
# point10 = [116.43379211425783,39.977999795258164]
# point11 = [116.60828590393068,39.975775866942584]
# point12 = [116.60828590393068,39.974970137530484]
# point13 =[116.55749559402467,  39.94529952809171]
# point14 = [116.3978409538867,39.90590128660034]
point15 = [116.4556, 39.9095]
#points = [point1, point2, point3, point4, point5, point6, point7, point8, point9, point10]
points = [point15]

gridIds = [getFormatGID(point)['gid'] for point in points]
#gridIds = [i for i in range(104000)]
#print(gridIds)
hourIds = [12]
#hourIds = [i for i in range(24)]

startIndex = 167
endIndex = 2088
readPath = '/datahouse/tripflow/Anomaly/bj-byhour-statics/'



#stay_arr = [[[] for j in range(len(points))] for i in range(len(hourIds))]
travel_arr = [[[] for j in range(len(gridIds))] for i in range(len(hourIds))]
#total_arr = [[[] for j in range(len(points))] for i in range(len(hourIds))]
#travel_arr = [0 for j in range(len(gridIds))]
for i in range(len(hourIds)):
    hourId = hourIds[i]
    j = 7;
    while j * 24 + hourId < endIndex and j * 24 + hourId > startIndex:
        filename = str(hourId) + '-' + str(j*24+hourId)
        print(filename)
        content=file(readPath+filename, 'r').read();
        records = content.split('\n')
        recodslen = len(records)
        for k in range(len(gridIds)):
            gridId = gridIds[k]
            if gridId < recodslen:
                record = records[gridId].split(',')
                #stay_arr[i][k].append(int(record[1]))
                #print(int(record[2]))
                #travel_arr[k] += int(record[2])
                travel_arr[i][k].append(int(record[2]))
                #total_arr[i][k].append(int(record[3]))
            else:
                break
        j += 1

print(travel_arr)
#travel_arr = [float(num)/1944.0 for num in travel_arr]
#np.save('totalTravelByGrid.npy', travel_arr)

# stay_arr = [70, 68, 69, 67, 51, 53, 59, 79, 75, 92, 79, 45, 40, 64, 80, 84, 70, 79, 54, 64, 86, 2, 68, 68, 69, 38, 55, 31, 55, 76, 50, 65, 49, 55, 85, 77, 68, 80, 72, 57, 50, 77, 57, 62, 61, 35, 26, 55, 40, 62, 57, 59, 54, 43, 41, 71, 60, 77, 62, 68, 52, 59, 75, 53, 71, 59, 73, 45, 59, 73, 70, 67, 40, 42, 54, 57, 33, 58, 77, 83, 72, 41, 60, 48, 53, 57, 72]
# travel_arr = [34, 51, 33, 11, 12, 8, 8, 6, 5, 10, 3, 2, 7, 3, 3, 1, 2, 5, 2, 3, 3, 0, 0, 4, 6, 4, 7, 0, 5, 3, 2, 4, 10, 3, 1, 6, 4, 4, 2, 6, 2, 4, 1, 2, 4, 2, 5, 6, 1, 5, 3, 1, 4, 5, 2, 5, 0, 7, 2, 3, 5, 3, 2, 2, 5, 2, 2, 4, 4, 3, 4, 2, 3, 4, 5, 0, 3, 4, 3, 2, 4, 1, 6, 4, 6, 4, 5]
# total_arr = [392, 421, 402, 360, 279, 286, 335, 334, 329, 349, 357, 244, 230, 312, 303, 413, 332, 310, 249, 271, 346, 7, 315, 315, 345, 241, 237, 146, 272, 296, 297, 264, 202, 222, 278, 266, 297, 305, 317, 233, 223, 282, 196, 285, 295, 179, 126, 242, 170, 274, 250, 303, 202, 240, 174, 278, 295, 318, 304, 270, 201, 218, 256, 246, 292, 271, 282, 219, 232, 275, 278, 284, 176, 189, 227, 269, 167, 290, 286, 313, 299, 196, 236, 202, 284, 290, 283]
# [3085774, 3097490, 3099197, 3007144, 2802600, 2981782, 3061578, 3046288, 3089583, 3097873, 3038368, 2855170, 2895919, 2441258, 2916664, 3653481, 3157109, 3062632, 3009666, 3089949, 2912505, 2054273, 3130849, 3090402, 3075008, 2772223, 3532582, 1365327, 2648552, 2715777, 2426246, 2743018, 2577223, 2729382, 2661231, 2740109, 2742770, 2727896, 2877120, 2759495, 2778266, 2616579, 2056785, 2124329, 1948375, 1415278, 1654379, 2823287, 1679333, 2710126, 2246501, 2102284, 1742531, 2761402, 2812930, 2877015, 2950217, 2859007, 2879119, 2792191, 2803651, 2984347, 2817885, 2830159, 2922031, 2804830, 2820979, 2887897, 2965933, 2779127, 2868710, 2930589, 2623765, 2844192, 2947138, 2924409, 2782822, 2892554, 2956497, 3215323, 2958552, 3242741, 3277601, 2907596, 2944177, 2874085, 2808475]
# with open("/datahouse/tripflow/Anomaly/bj-flowcount/flowcount.json", 'r') as stream:
#     flowCountDict = json.load(stream);
# flowCount = [];
# for x in xrange(87):
#     flowCount.append(sum(flowCountDict[x]['flowCount']));
# print(flowCount)
# stay_arr = [float(stay_arr[i])/flowCount[i] for i in range(len(stay_arr))]
# travel_arr = [float(travel_arr[i])/flowCount[i] for i in range(len(travel_arr))]
# print(stay_arr)
# print(travel_arr)
# print(total_arr)
#[3017091, 3079464, 2341253, 1105912, 942812, 861798, 678729, 485585, 439755, 377746, 383609, 334801, 287347, 288225, 298070, 216024, 287907, 326979, 287998, 243554, 250751, 225615, 261078, 400467, 299005, 262642, 596285, 15632, 313895, 286369, 273502, 291229, 250148, 226073, 245735, 266241, 277620, 279245, 274064, 228869, 211610, 249618, 210304, 185583, 160124, 170066, 169382, 211488, 162954, 238501, 217114, 195491, 180058, 236925, 213008, 241262, 250298, 238528, 247382, 247343, 219246, 204859, 229598, 237077, 232662, 245931, 258256, 230268, 190823, 228247, 247483, 239138, 170640, 159494, 149006, 186815, 200218, 212313, 212776, 204559, 216250, 194112, 179885, 191778, 214985, 214574, 178696]
