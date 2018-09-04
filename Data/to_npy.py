import glob
import os
import cv2
import numpy as np

ratio = 0.95

image_size1 = 160
image_size2 = 256

x = []
paths = glob.glob('./Masked/*')
for path in paths:
    
    imgs = os.listdir(path)
    imgs_original = [i for i in imgs if "mask" not in i]
    imgs_masked = [i for i in imgs if "mask" in i]
    for img_masked in imgs_masked:
        
        img_id = img_masked.split("-")[0]
        img_original = [i for i in imgs_original if i.split(".")[0] == img_id][0]
        mask_bounds = img_masked.split("-")[-1].split(".")[0]
        mask_bounds = re.findall(r'(\w*[0-9]+)\w*',mask_bounds)
        mask_bounds = [int(i) for i in mask_bounds]
        mask_bounds = np.array(mask_bounds, dtype=np.uint8)

        img1 = Image.open(os.path.join(path, img_original))
        img1 = img1.resize((image_size1, image_size2), Image.ANTIALIAS)
        img1 = (np.array(img1))
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
        
        img2 = Image.open(os.path.join(path, img_masked))
        img2 = img2.resize((image_size1, image_size2), Image.ANTIALIAS)
        img2 = (np.array(img2))
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        
        x.append((img1, img2, mask_bounds))


x = np.array(x)
np.random.shuffle(x)

p = int(ratio * len(x))
x_train = x[:p]
x_test = x[p:]

if not os.path.exists('./npy'):
    os.mkdir('./npy')
np.save('./npy/x_train.npy', x_train)
np.save('./npy/x_test.npy', x_test)
