from PIL import ImageGrab
import numpy as np
import cv2
from glob import glob
import os
import time


#Python将数字转换成大写字母
def getChar(number):
    factor, moder = divmod(number, 26) # 26 字母个数
    modChar = chr(moder + 65)          # 65 -> 'A'
    if factor != 0:
        modChar = getChar(factor-1) + modChar # factor - 1 : 商为有效值时起始数为 1 而余数是 0
    return modChar
def getChars(length):
    return [getChar(index) for index in range(length)]



"""  "*******************************************************************************************
*函数功能 ：统计二值化图片黑色像素点百分比
*输入参数 ：输入裁剪后图像，
*返 回 值 ：返回黑色像素点占比0-1之间
*编写时间 ： 2021.6.30
*作    者 ： diyun
********************************************************************************************"""
def Heise_zhanbi(img):
    [height, width, tongdao] = img.shape
    #print(width, height, tongdao)
    # cv2.imshow("3", img)
    # cv2.waitKey(20)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("binary", gray)
    # cv2.waitKey(100)

    # etVal, threshold = cv2.threshold(gray, 125, 255, cv2.THRESH_BINARY)
    # # cv2.imshow("threshold", threshold)
    # # cv2.waitKey(200)
    # a = 0
    # b = 0
    # for row in range(height):
    #     for col in range(width):
    #         val = threshold[row][col]
    #         if (val) == 0:#黑色
    #             a = a + 1
    #         else:
    #             b = b + 1

    a = np.sum(gray < 125)
    zhanbi = (float)(a) / (float)(height*width)
    #print("黑色像素个数", a, "黑色像素占比", zhanbi)
    return zhanbi


"""  "*******************************************************************************************
*函数功能 ：统计二值化图片白色像素点百分比
*输入参数 ：输入裁剪后图像，
*返 回 值 ：返回白色像素点占比0-1之间
*编写时间 ： 2021.6.30
*作    者 ： diyun
********************************************************************************************"""
def Baise_zhanbi(img):
    [height, width, tongdao] = img.shape
    #print(width, height, tongdao)
    # cv2.imshow("3", img)
    # cv2.waitKey(20)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("binary", gray)
    # cv2.waitKey(100)

    # etVal, threshold = cv2.threshold(gray, 235, 255, cv2.THRESH_BINARY)
    # # cv2.imshow("threshold", threshold)
    # # cv2.waitKey(200)
    # a = 0
    # b = 0
    # for row in range(height):
    #     for col in range(width):
    #         val = threshold[row][col]
    #         if (val) == 0:#黑色
    #             a = a + 1
    #         else:
    #             b = b + 1
    b=np.sum(gray>235)
    zhanbi = (float)(b) / (float)(height*width)
    #print("白色像素个数", b, "白色像素占比", zhanbi)
    return zhanbi

"""  "*******************************************************************************************
*函数功能 ：定位棋盘位置
*输入参数 ：截图
*返 回 值 ：裁剪后的图像
*编写时间 ： 2021.6.30
*作    者 ： diyun
********************************************************************************************"""
def dingweiqizi_weizhi(img):
    '''********************************************
    1、定位棋盘位置
    ********************************************'''
    #img = cv2.imread("./screen/1.jpg")

    image = img.copy()
    w, h, c = img.shape
    img2 = np.zeros((w, h, c), np.uint8)
    img3 = np.zeros((w, h, c), np.uint8)
    # img = ImageGrab.grab() #bbox specifies specific region (bbox= x,y,width,height *starts top-left)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([10, 0, 0])
    upper = np.array([40, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    erodeim = cv2.erode(mask, None, iterations=2)  # 腐蚀
    dilateim = cv2.dilate(erodeim, None, iterations=2)

    img = cv2.bitwise_and(img, img, mask=dilateim)
    frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, dst = cv2.threshold(frame, 100, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(dst, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)



    #cv2.imshow("0", img)

    i = 0
    maxarea = 0
    nextarea = 0
    maxint = 0
    for c in contours:
        if cv2.contourArea(c) > maxarea:
            maxarea = cv2.contourArea(c)
            maxint = i
        i += 1

    # 多边形拟合
    epsilon = 0.02 * cv2.arcLength(contours[maxint], True)
    if epsilon < 1:
        print("error :   epsilon < 1")
        pass

    # 多边形拟合
    approx = cv2.approxPolyDP(contours[maxint], epsilon, True)
    [[x1, y1]] = approx[0]
    [[x2, y2]] = approx[2]

    checkerboard = image[y1:y2, x1:x2]
    # cv2.imshow("1", checkerboard)
    # cv2.waitKey(1000)
    #cv2.destroyAllWindows()
    return checkerboard

"""  "*******************************************************************************************
*函数功能 ：定位棋子颜色及位置
*输入参数 ：裁剪后的图像
*返 回 值 ：棋子颜色及位置列表
*编写时间 ： 2021.6.30
*作    者 ： diyun
********************************************************************************************"""
def dingweiqizi_yanse_weizhi(img):
    '''********************************************
    2、识别棋盘棋子位置及颜色及序号；
    ********************************************'''
    #img = cv2.imread("./checkerboard/checkerboard_1.jpg")
    img = cv2.resize(img, (724,724), interpolation=cv2.INTER_AREA)
    #cv2.imshow("src",img)
    #cv2.waitKey(1000)

    #变量定义
    small_length=38  #每个小格宽高
    qizi_zhijing=38#棋子直径

    list = [[0 for i in range(19)] for j in range(19)]
    #print(list)

    for i in range(19):
        for j in range(19):

            lie = i
            hang = j

            Tp_x = small_length * lie
            Tp_y = small_length * hang
            Tp_width = qizi_zhijing
            Tp_height = qizi_zhijing

            img_temp=img[Tp_y:Tp_y+Tp_height, Tp_x:Tp_x+Tp_width]#参数含义分别是：y、y+h、x、x+w

            heise_zhanbi=Heise_zhanbi(img_temp)
            if heise_zhanbi>0.5:
                list[hang][lie]=2#黑色
                print("第", j+1, "行，第", i+1, "列棋子为黑色")
                #print("当前棋子为黑色")
            else:
                baise_zhanbi = Baise_zhanbi(img_temp)
                if baise_zhanbi > 0.15:
                    list[hang][lie] = 1  # 白色
                    print("第", j+1, "行，第",i+1 , "列棋子为白色")
                    #print("当前棋子为白色")
                else:
                    list[hang][lie] = 0  # 无棋子
                    #print("当前位置没有棋子")
            #print(heise_zhanbi)
    #cv2.imshow("2",img)
    #print("\n")
    #print(list)
    return  list



if __name__ =="__main__":
    list0 = [[0 for i in range(19)] for j in range(19)]
    list_finall = []
    img = cv2.imread("./screen/9.jpg")
    start_time = time.time()
    '''********************************************
    1、定位棋盘位置
    ********************************************'''
    img_after=dingweiqizi_weizhi(img)
    time1= time.time()
    print(time1- start_time )
    #cv2.imshow("src",img)

    '''********************************************
    2、识别棋盘棋子位置及颜色及序号；
    ********************************************'''
    list1=dingweiqizi_yanse_weizhi(img_after)
    time2= time.time()
    print(time2 - time1)
    print(time2- start_time )
    print(list1)




