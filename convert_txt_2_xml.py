from lxml import etree
from PIL import Image
import csv
import os

# (필독1)
# 맥 사용자의 경우 .DS_Store 파일이 폴더 내에 자동으로 생성되어있는 경우가 있습니다.
# 이 경우 맥 터미널을 통해 .DS_Store 파일을 삭제해야합니다.
# Ref : http://leechoong.com/posts/2018/ds_store/

# (필독2)             -- 저는 윈도우사용자니까 여기만 봅니다 ^*^ 맥은 둘 다 봐야됨.
# 각자 환경에 맞게 경로 설정하세요.
# IMG_PATH, txt_folder, labels 세 군데만 수정해주면 됨! 체크한 곳 <여기!> 바로 아랫줄만 수정하기!!
# path 예시 : "/Users/desktop/dev/190902/data"
## 이 py파일이 위치한 폴더에 xml파일들이 저장된다. 저장할 폴더에 이 소스파일을 옮긴 뒤 실행하는 게 좋을듯!

##### 여기! #####
IMG_PATH = "YOUR_IMG_FOLDER_PATH"
fw = os.listdir(IMG_PATH)
# path of save xml file
save_path = '' # keep it blank

##### 여기! #####
# txt_folder is txt file root that using darknet rectbox
txt_folder = 'YOUR_TXT_FOLDER_PATH'

##### 여기! #####
# 라벨 수정
labels = ['sleep_front', 'sleep_bread', 'sleep_side', 'sleep_face', 'sleep_comfort']
global label
label = ''

def csvread(fn):
    with open(fn, 'r') as csvfile:
        list_arr = []
        reader = csv.reader(csvfile, delimiter=' ')

        for row in reader:
            list_arr.append(row)
    return list_arr


def convert_label(txt_file):
    global label
    for i in range(len(labels)):
        if txt_file[0] == str(i):
            label = labels[i]
            return label

    return label

# core code = convert the yolo txt file to the x_min,x_max...


def extract_coor(txt_file, img_width, img_height):
    x_rect_mid = float(txt_file[1])
    y_rect_mid = float(txt_file[2])
    width_rect = float(txt_file[3])
    height_rect = float(txt_file[4])

    x_min_rect = ((2 * x_rect_mid * img_width) - (width_rect * img_width)) / 2
    x_max_rect = ((2 * x_rect_mid * img_width) + (width_rect * img_width)) / 2
    y_min_rect = ((2 * y_rect_mid * img_height) -
                  (height_rect * img_height)) / 2
    y_max_rect = ((2 * y_rect_mid * img_height) +
                  (height_rect * img_height)) / 2

    return x_min_rect, x_max_rect, y_min_rect, y_max_rect


for line in fw:
    root = etree.Element("annotation")

    # try debug to check your path
    img_style = IMG_PATH.split('/')[-1]
    img_name = line
    image_info = IMG_PATH + "/" + line
    img_txt_root = txt_folder + "/" + line[:-4]
    # print(img_txt_root)
    txt = ".txt"

    txt_path = img_txt_root + txt
    # print(txt_path)
    txt_file = csvread(txt_path)
    ######################################

    # read the image  information
    img_size = Image.open(image_info).size

    img_width = img_size[0]
    img_height = img_size[1]
    img_depth = Image.open(image_info).layers
    ######################################

    folder = etree.Element("folder")
    folder.text = "%s" % (img_style)

    filename = etree.Element("filename")
    filename.text = "%s" % (img_name)

    path = etree.Element("path")
    path.text = "%s" % (IMG_PATH)

    source = etree.Element("source")
    ##################source - element##################
    source_database = etree.SubElement(source, "database")
    source_database.text = "Unknown"
    ####################################################

    size = etree.Element("size")
    ####################size - element##################
    image_width = etree.SubElement(size, "width")
    image_width.text = "%d" % (img_width)

    image_height = etree.SubElement(size, "height")
    image_height.text = "%d" % (img_height)

    image_depth = etree.SubElement(size, "depth")
    image_depth.text = "%d" % (img_depth)
    ####################################################

    segmented = etree.Element("segmented")
    segmented.text = "0"

    root.append(folder)
    root.append(filename)
    root.append(path)
    root.append(source)
    root.append(size)
    root.append(segmented)

    for ii in range(len(txt_file)):
        label = convert_label(txt_file[ii][0])
        x_min_rect, x_max_rect, y_min_rect, y_max_rect = extract_coor(
            txt_file[ii], img_width, img_height)

        object = etree.Element("object")
        ####################object - element##################
        name = etree.SubElement(object, "name")
        name.text = "%s" % (label)

        pose = etree.SubElement(object, "pose")
        pose.text = "Unspecified"

        truncated = etree.SubElement(object, "truncated")
        truncated.text = "0"

        difficult = etree.SubElement(object, "difficult")
        difficult.text = "0"

        bndbox = etree.SubElement(object, "bndbox")
        #####sub_sub########
        xmin = etree.SubElement(bndbox, "xmin")
        xmin.text = "%d" % (x_min_rect)
        ymin = etree.SubElement(bndbox, "ymin")
        ymin.text = "%d" % (y_min_rect)
        xmax = etree.SubElement(bndbox, "xmax")
        xmax.text = "%d" % (x_max_rect)
        ymax = etree.SubElement(bndbox, "ymax")
        ymax.text = "%d" % (y_max_rect)
        #####sub_sub########

        root.append(object)
        ####################################################

    file_output = etree.tostring(root, pretty_print=True, encoding='UTF-8')
    # print(file_output.decode('utf-8'))
    ff = open('%s.xml' % (img_name[:-4]), 'w', encoding="utf-8")
    ff.write(file_output.decode('utf-8'))
