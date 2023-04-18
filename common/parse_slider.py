from pathlib import Path
import PIL
import cv2
import numpy as np

def imshow(img,winname='test',delay=0):
    '''cv2展示图片'''
    cv2.imshow(winname,img)
    cv2.waitKey(delay)
    cv2.destroyAllWindows()

def pil_to_cv2(img):
    '''
    pil转cv2图片
    :param img:pil图像
    :return:cv2图像
    '''
    img = cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2BGR)
    return img

def bytes_to_cv2(img):
    '''
    二进制转图片cv2
    :param img:二进制图片数据
    :return:cv2图像
    '''
    #将图片字节码转为bytes，转换成一维的numpy数组到缓存中
    img_buffer_np = np.frombuffer(img,dtype=np.uint8)
    # 从指定的内存缓存中读取一维numpy数据，并把数据转换（解码）成图像矩阵格式
    img_np = cv2.imdecode(img_buffer_np,1)
    return img_np

def cv2_open(img,flag=None):
    '''
    统一输出格式为cv2图像
    :param img:
    :param flag:颜色空间转换类型
    :return:
    '''
    if isinstance(img,bytes):
        img = bytes_to_cv2(img)
    elif isinstance(img,(str,Path)):
        img = cv2.imread(str(img))
    elif isinstance(img,np.ndarray):
        img = img
    elif isinstance(img,PIL.Image):
        img = pil_to_cv2(img)
    else:
        raise ValueError('输入的图片类型无法解析: {}'.format(type(img)))
    if flag is not None:
        img = cv2.cvtColor(img,flag)
    return img

def get_distance(bg,tp,im_show=False,save_path = None):
    '''
    :param bg:背景图路径或者Path对象或图片二进制
    :param tb:缺口图路径或者Path对象或图片二进制
    :param im_show:是否显示结果
    :param save_path:保存路劲
    :return:缺口位置
    '''

    #读取图片
    bg_gray = cv2_open(bg,flag=cv2.COLOR_BGR2GRAY)
    tp_gray = cv2_open(tp,flag=cv2.COLOR_BGR2GRAY)
    # 边缘检测
    tp_gray = cv2.Canny(tp_gray,255,255)
    bg_gray = cv2.Canny(bg_gray,255,255)
    #目标匹配
    result = cv2.matchTemplate(bg_gray,tp_gray,cv2.TM_CCOEFF_NORMED)
    #解析匹配结果
    min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(result)

    distance = max_loc[0]
    # if save_path or im_show:
    #     # 需要绘制的方框的高度和宽度
    #     tp_height,tp_width = tp_gray.shape[:2]
    #     # 矩形左上点的位置
    #     x,y = max_loc
    #     # 矩形右下角点的位置
    #     _x,_y = x+ tp_width, y+tp_height
    #     # 绘制矩形
    #     bg_img = cv2_open(bg)
    #     cv2.rectangle(bg_img,(x,y),(_x,_y),(0,0,255),2)
    #     # 保存缺口识别结果到背景图
    #     if save_path:
    #         save_path = Path(save_path).resolve()
    #         save_path = save_path.parent / f"{save_path.stem}.{distance}{save_path.suffix}"
    #         save_path = save_path.__str__()
    #         cv2.imwrite(save_path,bg_img)
    #     # 显示缺口识别结果
    #     if im_show:
    #         imshow(bg_img)
    return distance

if __name__ == '__main__':
    d = get_distance(
        bg = './002.png',
        tp = './001.png',
        im_show = False,
        save_path='./003.png'
    )
    print('滑块距离为'+ str(d))