import glob
import os
import cv2
import numpy as np
import re
from PIL import Image
import progressbar


ratio = 0.95

image_size1 = 160
image_size2 = 256

max_elements = 20000

x = []

os.chdir("./UIdata/Masked/") 
paths = os.listdir('./')
paths = [d for d in paths if not os.path.isfile(d)]

pbar = progressbar.ProgressBar()

for path in pbar(paths):
    
    imgs = os.listdir(path)
    imgs_original = [i for i in imgs if "mask" not in i]
    imgs_masked = [i for i in imgs if "mask" in i]
    for img_masked in imgs_masked:
        
        img_id = img_masked.split("-")[0]
        img_original = [i for i in imgs_original if i.split(".")[0] == img_id][0]
        mask_bounds = img_masked.split("-")[-1].split(".")[0]
        mask_bounds = re.findall(r'(\w*[0-9]+)\w*',mask_bounds)
        mask_bounds = [float(i) for i in mask_bounds]
        
        mask_bounds[1] = mask_bounds[1] + (mask_bounds[1]/1280)*(1280-1216)
        mask_bounds[3] = mask_bounds[3] + (mask_bounds[3]/1280)*(1280-1216)

#        mask_bounds[1] = mask_bounds[1]*1280/1216
#        mask_bounds[3] = mask_bounds[3]*1280/1216

        mask_bounds = [int(i/5) for i in mask_bounds]
        mask_bounds = np.array(mask_bounds, dtype=np.uint8)

        img1 = Image.open(os.path.join(path, img_original))
        img1 = img1.resize((image_size1, image_size2), Image.ANTIALIAS)
        img1 = (np.array(img1))
        # img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
        
#         img2 = Image.open(os.path.join(path, img_masked))
#         img2 = img2.resize((image_size1, image_size2), Image.ANTIALIAS)
#         img2 = (np.array(img2))
#         # img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

        x.append((img1, mask_bounds))


x = np.array(x)
np.random.shuffle(x)

p = int(ratio * len(x))
x_train = x[:p]
x_test = x[p:]

os.chdir("../") 

if not os.path.exists('./npy'):
    os.mkdir('./npy')
    
if len(x_test) > max_elements:
    for count in range(int(len(x_test)/max_elements)):
        np.save('./npy/x_test_' + str(count) + '.npy', x_test[count*max_elements : (count+1)*max_elements])
    np.save('./npy/x_test_' + str(count+1) + '.npy', x_train[(count+1)*max_elements :])
else:
    np.save('./npy/x_test.npy', x_test)

if len(x_train) > max_elements:
    for count in range(int(len(x_train)/max_elements)):
        np.save('./npy/x_train_' + str(count) + '.npy', x_train[count*max_elements : (count+1)*max_elements])
    np.save('./npy/x_train_' + str(count+1) + '.npy', x_train[(count+1)*max_elements :])
else:
    np.save('./npy/x_train.npy', x_train)

pbar.finish()

print("Done.")
