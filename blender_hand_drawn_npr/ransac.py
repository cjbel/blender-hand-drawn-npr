# coding: utf-8

import matplotlib.pyplot as plt
import numpy as np


# compute ransac for a straight line
# x: input pts
# y: output pts to fit
#
# fit: a function of the form (x,y) that returns parameters that estimate y given x
#
# predict: a function of the form (params, x) which returns the estimates for y
#
# prob: a function of the form (y, y_prime) that outputs the probabilty of "accepting" y_prime as an inlier
# fraction: fraction of points to include in each subsample
# iters: number of iterations to run
def ransac(x, y, fit, predict, prob, iters=20, fraction=0.1):
    models = []
    fixed_ix = np.arange(len(x))
    k = int(np.ceil(fraction * len(x)))  # number of points in each subsample
    best_inliers = -1  # always choose at least one model
    best_model = None
    for i in range(iters):
        # randomly choose k matched points from x and y, without repeats        
        ix = np.random.choice(fixed_ix, size=k)
        x_pts, y_pts = x[ix], y[ix]
        # fit to the subsample
        params = fit(x_pts, y_pts)
        # compute the inliers
        inlier_distances = prob(predict(params, x), y)
        test_var = np.random.uniform(0, 1, inlier_distances.shape)
        inliers = np.sum(test_var < inlier_distances)
        # check if winning model
        if inliers > best_inliers:
            best_inliers = inliers
            best_model = params
    return best_model


if __name__ == "__main__":
    # example: robust linear regression
    np.random.seed(387145)


    def linear_fit(x, y):
        return np.polyfit(x, y, 1)

    def cubic_fit(x, y):
        return np.polyfit(x, y, 3)

    def linear_predict(params, x):
        return np.polyval(params, x)

    # probability of accepting a point
    # inv. sqr. exponential
    def sqr_distance(y, y_pred, tol):
        return np.exp(-(y - y_pred) ** 2 / (2 * tol ** 2))


    points = [[658, 301], [658, 301], [660, 302], [660, 302], [661, 302], [663, 303], [663, 303], [665, 304], [665, 304], [668, 305], [668, 305], [670, 306], [670, 306], [672, 307], [672, 307], [675, 308], [675, 308], [677, 309], [677, 309], [679, 310], [679, 310], [680, 310], [682, 311], [682, 311], [684, 312], [684, 312], [686, 313], [687, 313], [687, 313], [689, 314], [689, 314], [691, 315], [691, 315], [694, 316], [694, 316], [696, 317], [696, 317], [698, 318], [698, 318], [701, 319], [701, 319], [703, 320], [703, 320], [705, 321], [706, 321], [706, 321], [708, 322], [708, 322], [710, 323], [710, 323], [713, 324], [713, 324], [715, 325], [715, 325], [717, 326], [717, 326], [720, 327], [720, 327], [722, 328], [722, 328], [724, 329], [724, 329], [725, 329], [727, 330], [727, 330], [729, 331], [729, 331], [731, 332], [732, 332], [732, 332], [734, 333], [734, 333], [736, 334], [736, 334], [739, 335], [739, 335], [741, 336], [741, 336], [743, 337], [743, 337], [744, 337], [746, 338], [746, 338], [748, 339], [748, 339], [750, 340], [751, 340], [751, 340], [753, 341], [753, 341], [755, 342], [755, 342], [758, 343], [758, 343], [760, 344], [762, 345], [762, 345], [765, 346], [765, 346], [767, 347], [767, 347], [769, 348], [769, 348], [770, 348], [772, 349], [772, 349], [774, 350], [774, 350], [777, 351], [777, 351], [779, 352], [779, 352], [781, 353], [781, 353], [784, 354], [784, 354], [786, 355], [786, 355], [788, 356], [788, 356], [789, 356], [791, 357], [791, 357], [793, 358], [795, 359], [795, 359], [797, 360], [797, 360], [799, 361], [799, 361], [801, 362], [801, 362], [802, 362], [803, 363], [804, 363], [804, 363], [805, 364], [805, 364], [806, 364], [807, 365], [807, 365], [808, 365], [809, 366], [809, 366], [811, 367], [811, 367], [813, 368], [813, 368], [815, 369], [817, 370], [817, 370], [819, 371], [819, 371], [820, 372], [820, 372], [821, 372], [822, 373], [822, 373], [824, 374], [824, 374], [826, 375], [826, 375], [827, 376], [827, 376], [828, 376], [829, 377], [829, 377], [831, 378], [831, 378], [832, 379], [833, 379], [833, 379], [834, 380], [834, 380], [836, 381], [836, 381], [838, 382], [838, 382], [839, 383], [839, 383], [841, 384], [841, 384], [843, 385], [843, 385], [844, 386], [844, 386], [846, 387], [846, 387], [847, 388], [848, 388], [848, 388], [849, 389], [849, 389], [851, 390], [851, 390], [852, 391], [852, 391], [854, 392], [854, 392], [856, 393], [856, 393], [857, 394], [857, 394], [859, 395], [859, 395], [860, 396], [860, 396], [861, 396], [862, 397], [862, 397], [864, 398], [864, 398], [865, 399], [865, 399], [867, 400], [867, 400], [868, 401], [869, 401], [869, 401], [870, 402], [870, 402], [872, 403], [872, 403], [873, 404], [873, 404], [875, 405], [875, 405], [876, 406], [877, 406], [877, 406], [878, 407], [878, 407], [880, 408], [880, 408], [881, 409], [881, 409], [882, 409], [883, 410], [883, 410], [885, 411], [885, 411], [886, 412], [886, 412], [887, 412], [888, 413], [888, 413], [890, 414], [890, 414], [891, 415], [891, 415], [892, 415], [893, 416], [893, 416], [895, 417], [895, 417], [896, 418], [896, 418], [897, 418], [898, 419], [898, 419], [900, 420], [900, 420], [901, 421], [901, 421], [902, 421], [903, 422], [903, 422], [905, 423], [905, 423], [907, 424], [907, 424], [908, 425], [908, 425], [909, 425], [910, 426], [910, 426], [912, 427], [914, 428], [914, 428], [915, 429], [916, 429], [916, 429], [917, 430], [917, 430], [918, 430], [919, 431], [919, 431], [921, 432], [921, 432], [923, 433], [923, 433], [925, 434], [925, 434], [927, 435], [927, 435], [928, 436], [929, 436], [929, 436], [930, 437], [931, 437], [931, 437], [932, 438], [933, 438], [933, 438], [934, 439], [935, 439], [935, 439], [936, 440], [937, 440], [937, 440], [938, 441], [939, 441], [939, 441], [940, 442], [941, 442], [941, 442], [942, 443], [943, 443], [943, 443], [945, 444], [945, 444], [947, 445], [947, 445], [949, 446], [949, 446], [951, 447], [951, 447], [952, 447], [953, 448], [954, 448], [954, 448], [956, 449], [956, 449], [958, 450], [958, 450], [959, 450], [960, 451], [961, 451], [961, 451], [963, 452], [963, 452], [965, 453], [965, 453], [966, 453], [967, 454], [968, 454], [968, 454], [970, 455], [970, 455], [971, 455], [972, 456], [973, 456], [973, 456], [975, 457], [976, 457], [976, 457], [978, 458], [978, 458], [979, 458], [980, 459], [981, 459], [981, 459], [983, 460], [984, 460], [984, 460], [986, 461], [987, 461], [987, 461], [989, 462], [989, 462], [990, 462], [992, 463], [992, 463], [993, 463], [995, 464], [995, 464], [996, 464], [998, 465], [999, 465], [999, 465], [1001, 466], [1002, 466], [1002, 466], [1004, 467], [1005, 467], [1006, 467], [1008, 468], [1008, 468], [1009, 468], [1011, 469], [1012, 469], [1012, 469], [1015, 470], [1015, 470], [1016, 470], [1018, 471], [1019, 471], [1019, 471], [1022, 472], [1022, 472], [1023, 472], [1025, 473], [1026, 473], [1027, 473], [1029, 474], [1030, 474], [1030, 474], [1033, 475], [1034, 475], [1034, 475], [1037, 476], [1037, 476], [1038, 476], [1041, 477], [1041, 477], [1042, 477], [1045, 478], [1045, 478], [1046, 478], [1049, 479], [1049, 479], [1050, 479], [1053, 480], [1053, 480], [1054, 480], [1057, 481], [1057, 481], [1058, 481], [1061, 482], [1061, 482], [1062, 482], [1065, 483], [1065, 483], [1066, 483], [1069, 484], [1069, 484], [1070, 484], [1073, 485], [1073, 485], [1074, 485], [1077, 486], [1077, 486], [1078, 486], [1080, 487], [1081, 487], [1081, 487], [1082, 487], [1084, 488], [1085, 488], [1085, 488], [1088, 489], [1089, 489], [1089, 489], [1092, 490], [1092, 490], [1093, 490], [1096, 491], [1099, 492], [1100, 492], [1100, 492], [1103, 493], [1103, 493], [1104, 493], [1106, 494], [1107, 494], [1107, 494], [1110, 495], [1110, 495], [1113, 496], [1113, 496], [1114, 496], [1116, 497], [1117, 497], [1117, 497], [1119, 498], [1120, 498], [1120, 498], [1123, 499], [1123, 499], [1126, 500], [1126, 500], [1129, 501], [1129, 501], [1132, 502], [1132, 502], [1134, 503], [1135, 503], [1135, 503], [1137, 504], [1138, 504], [1138, 504], [1140, 505], [1140, 505], [1141, 505], [1143, 506], [1145, 507], [1146, 507], [1146, 507], [1148, 508], [1148, 508], [1151, 509], [1151, 509], [1153, 510], [1153, 510], [1155, 511], [1156, 511], [1156, 511], [1158, 512], [1158, 512], [1160, 513], [1160, 513], [1161, 513], [1163, 514], [1163, 514], [1165, 515], [1165, 515], [1167, 516], [1168, 516], [1168, 516], [1170, 517], [1170, 517], [1172, 518], [1172, 518], [1173, 518], [1174, 519], [1175, 519], [1175, 519], [1177, 520], [1177, 520], [1179, 521], [1179, 521], [1180, 521], [1182, 522], [1182, 522], [1184, 523], [1184, 523], [1186, 524], [1187, 524], [1187, 524], [1189, 525], [1189, 525], [1191, 526], [1191, 526], [1193, 527], [1194, 527], [1194, 527], [1196, 528], [1198, 529], [1198, 529], [1199, 529], [1201, 530], [1201, 530], [1203, 531], [1203, 531], [1205, 532], [1205, 532], [1206, 532], [1208, 533], [1208, 533], [1210, 534], [1210, 534], [1212, 535], [1213, 535], [1213, 535], [1215, 536], [1215, 536], [1217, 537], [1217, 537], [1218, 537], [1219, 538], [1220, 538], [1220, 538], [1222, 539], [1222, 539], [1224, 540], [1224, 540], [1225, 540], [1227, 541], [1227, 541], [1229, 542], [1229, 542], [1231, 543], [1232, 543], [1232, 543], [1234, 544], [1234, 544], [1236, 545], [1236, 545], [1237, 545], [1238, 546], [1239, 546], [1239, 546], [1241, 547], [1241, 547], [1243, 548], [1243, 548], [1244, 548], [1246, 549], [1246, 549], [1248, 550], [1248, 550], [1250, 551], [1251, 551], [1251, 551], [1253, 552], [1253, 552], [1255, 553], [1255, 553], [1257, 554], [1258, 554], [1258, 554], [1260, 555], [1260, 555], [1262, 556], [1262, 556], [1263, 556], [1264, 557], [1265, 557], [1265, 557], [1267, 558], [1267, 558], [1269, 559], [1269, 559], [1270, 559], [1272, 560], [1272, 560], [1274, 561], [1274, 561], [1276, 562], [1277, 562], [1277, 562], [1279, 563], [1279, 563], [1281, 564], [1281, 564], [1282, 564], [1283, 565], [1284, 565], [1284, 565], [1286, 566], [1286, 566], [1288, 567], [1288, 567], [1289, 567], [1291, 568], [1291, 568], [1293, 569], [1293, 569], [1295, 570], [1296, 570], [1296, 570], [1298, 571], [1298, 571], [1300, 572], [1300, 572], [1302, 573], [1303, 573], [1303, 573], [1305, 574], [1307, 575], [1307, 575], [1308, 575], [1309, 576], [1310, 576], [1310, 576], [1312, 577], [1312, 577], [1314, 578], [1314, 578], [1315, 578], [1317, 579], [1317, 579], [1319, 580], [1319, 580], [1321, 581], [1322, 581], [1322, 581], [1324, 582], [1324, 582], [1326, 583], [1326, 583], [1327, 583], [1328, 584], [1329, 584], [1329, 584], [1331, 585], [1331, 585], [1333, 586], [1333, 586], [1334, 586], [1336, 587], [1336, 587], [1338, 588], [1338, 588], [1340, 589], [1341, 589], [1341, 589], [1343, 590], [1343, 590], [1345, 591], [1345, 591], [1346, 591], [1347, 592], [1348, 592], [1348, 592], [1350, 593], [1352, 594], [1352, 594], [1353, 594], [1354, 595], [1355, 595], [1355, 595], [1357, 596], [1357, 596], [1359, 597], [1360, 597], [1360, 597], [1362, 598], [1362, 598], [1364, 599], [1364, 599], [1366, 600], [1367, 600], [1367, 600], [1369, 601], [1369, 601], [1371, 602], [1371, 602], [1372, 602], [1373, 603], [1374, 603], [1374, 603], [1376, 604], [1376, 604], [1378, 605], [1378, 605]]
    # points = [[869, 401], [869, 401], [850, 400], [870, 402], [870, 402], [872, 403], [872, 403], [873, 404], [873, 404], [875, 405], [875, 405], [876, 406], [877, 406], [877, 406], [878, 407], [878, 407], [880, 408], [880, 408], [881, 409], [881, 409], [882, 409], [883, 410], [883, 410], [885, 411], [885, 411], [886, 412], [886, 412], [887, 412], [888, 413], [888, 413], [890, 414], [890, 414], [891, 415], [891, 415], [892, 415], [893, 416], [893, 416], [895, 417], [895, 417], [896, 418], [896, 418], [897, 418], [898, 419], [898, 419], [900, 420], [900, 420], [901, 421]]
    x = np.array([point[1] for point in points])
    y = np.array([point[0] for point in points])

    # x = np.random.uniform(0, 50, 50)
    # y = x * 10 + 5 + np.random.normal(0, 20, x.shape)
    # # add some nasty outliers
    # y[np.random.uniform(0, 1, y.shape) < 0.25] = 0

    plt.figure()

    ## apply RANSAC
    best_fit = ransac(x, y, fit=cubic_fit, predict=linear_predict,
                      prob=lambda y, yp: sqr_distance(y, yp, 1), iters=20)

    plt.scatter(x, y)
    xs = np.linspace(np.min(x), np.max(x), 100)

    plt.plot(xs, linear_predict(best_fit, xs), label="RANSAC")
    plt.plot(xs, linear_predict(linear_fit(x, y), xs), label="Non-RANSAC")
    plt.legend()

    plt.show()