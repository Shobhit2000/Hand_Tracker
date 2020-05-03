from scipy.io import loadmat
import os
import shutil
import math
import pandas as pd
import csv
import cv2

# creating the csv file of annotations
def create_csv(csv_path, notations):
    with open(csv_path, 'w') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerows(notations)

    df = pd.read_csv(csv_path)
    os.remove(csv_path)
    df = df.fillna(0)
    df.to_csv(csv_path, index=False)

def optimize_data(notations):
    c = 1
    for x in notations:
        print(c)
        c += 1
        if x[0] == '' and x[1] != '' and x[2] != '' and x[3] != '' and x[4] != '' and x[5] == '' and x[6] == '' and x[7] == '':
            x[0] = x[1]
            x[1] = x[2]
            x[2] = x[3]
            x[3] = x[4]
            x[4] = ''

    return notations

# function to find the coordinates of the bounding box
def bbox(poly):
    min_x, min_y = poly[0][0], poly[0][1]
    max_x = max_y = 0
    a1 = []
    for i in range(1, len(poly)):
        x, y = poly[i][0], poly[i][1]
        max_x = x if (x > max_x) else max_x
        min_x = x if (x < min_x) else min_x
        max_y = y if (y > max_y) else max_y
        min_y = y if (y < min_y) else min_y

    a1.append(int(min_x))
    a1.append(int(min_y))
    a1.append(math.ceil(max_x))
    a1.append(math.ceil(max_y))
    return int(min_x/2), int(min_y/2), math.ceil(max_x/2), math.ceil(max_y/2)

# creates the Training and Test folder
def train_batch(path, dir, count, f):

    path = os.path.join(path, dir)
    poly_file = "polygons.mat"
    anno = loadmat(os.path.join(path, poly_file))
    polygons = anno["polygons"][0]
    poly_count = 0

    for _, _, filenames in os.walk(path):
        for filename in filenames:
            if filename != poly_file:
                img = cv2.imread(os.path.join(path, filename))
                img = cv2.resize(img, (640, 360))
                coor = []

                if f == 1:
                    # shutil.copy(path + "//" + str(filename), train_direc + str(count) + ".jpg")
                    dst = train_direc + str(count) + ".jpg"
                    cv2.imwrite(dst, img)
                if f == 0:
                    # shutil.copy(path + "//" + str(filename), test_direc + str(count) + ".jpg")
                    dst = test_direc + str(count) + ".jpg"
                    cv2.imwrite(dst, img)

                other_left = polygons[poly_count][2]
                other_right = polygons[poly_count][3]        # 2 denotes other left and 3 denotes other right

                if len(other_left) == 0 or len(other_left) == 1:
                    coor.append(None)
                else:
                    x1, y1, x2, y2 = bbox(other_left)
                    coor.append(x1)
                    coor.append(y1)
                    coor.append(x2)
                    coor.append(y2)


                if len(other_right) == 0 or len(other_right) == 1:
                    coor.append(None)
                else:
                    bbox(other_right)
                    x1, y1, x2, y2 = bbox(other_right)
                    coor.append(x1)
                    coor.append(y1)
                    coor.append(x2)
                    coor.append(y2)

                if f == 1:
                    annots.append(coor)
                if f == 0:
                    test_annots.append(coor)

                count += 1
                poly_count += 1

def directories(path):
    count = 1
    for root, dirs, filenames in os.walk(path):
        for dir in dirs:
            if dir != "PUZZLE_OFFICE_T_S":
                f = 1
                train_batch(ori_path, dir, count, f)
                print(annots)
                count += 100
            else:
                f = 0
                count = 1
                train_batch(ori_path, dir, count, f)
                print(test_annots)
                print("done")

annots = []
test_annots = []

# creating train and test directories
os.mkdir("dataset")
os.mkdir("dataset//train")
os.mkdir("dataset//test")

# paths
ori_path = "data//_LABELLED_SAMPLES//"
train_direc = "dataset//train//"
test_direc = "dataset//test//"
train_csv_path = train_direc + "annotations.csv"
test_csv_path = test_direc + "test_annotations.csv"

directories(ori_path)

annots = optimize_data(annots)
test_annots = optimize_data(test_annots)

print(len(annots))
print(len(test_annots))

if os.path.exists(train_csv_path):
    os.remove(train_csv_path)     # remove any csv file with that name in the training folder
else:
    create_csv(train_csv_path, annots)    # creating the final csv file of annotations for train folders

if os.path.exists(test_csv_path):
    os.remove(test_csv_path)      # remove any csv file with that name in the test folder
else:
    create_csv(test_csv_path, test_annots)     # creating the final csv file of annotations for test folders
