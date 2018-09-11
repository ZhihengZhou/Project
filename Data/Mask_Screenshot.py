import os
from PIL import Image
import matplotlib.pyplot as plt
import xml.etree.cElementTree as ET 
import re
import hashlib
from skimage import transform
import progressbar
    
def mask_and_save_image(box):
    """
    This function take a mask range and mask the range with wite block and save image.
    
    Parameter:
    box : A four element list which note a rectangle range of image. 
          Example: (upper-left x, upper-left y, botton-right x, botton-y)
    """
    
    global count
    
    width = box[2]-box[0]
    height = box[3]-box[1]
    
    if width >= 0 and height >= 0:
    
        try:
            im = Image.open(dir_name + "/" + img_name)
            img_names = img_name.split('.')
            region=im.crop(box)

            mask = Image.new("RGBA",(width,height),(255,255,255))

            im.paste(mask,box)
            im = im.crop((0,0,800,1216))
            
            im.save(save_dir +  img_names[0] + "-mask_" + str(count) + "-" + str(box) + "." + img_names[1])
            count += 1
        except Exception:
            pass
    
# Find node recursively
def find_all_element_by_attribute(node, element_name, attribute, find):
    """
    This function use preorder traversal to find the all the XML objects by its attributs value.
    
    Parameters:
    node        : XML object.
    element_name: Target object name (name of node).
    attribute   : Target attribut name in XML object.
    find        : Target attribute value which mean to find.
    """
    if attribute in node.attrib and node.attrib[attribute] == find:
        # Operations after find the target XML objects.
        bounds = node.attrib['bounds']
        bounds = re.findall(r'(\w*[0-9]+)\w*',bounds)
        bounds = [int(i) for i in bounds]
        mask_and_save_image(bounds)
    
    # Visit all the target objects in current object.
    for n in node.findall(element_name):
        find_all_element_by_attribute(n, element_name, attribute, find)

def get_file_md5(f):
    m = hashlib.md5()
    while True:
        #如果不用二进制打开文件，则需要先编码
        data = f.readline()
        data = delete_attributes_by_name(data,["class"]).encode('utf-8')
        # data = f.read(1024)  #将文件分块读取
        if not data:
            break
        m.update(data)
        # print(data)
    return m.hexdigest()

def delete_attributes_by_name(object_string, keep_list):
    """
    This function takes an XML objects string (a line) and the attributes name which user want to keep. Then return 
    the cleaned XML objects string with only the attributs in keep list. And keep the XML object hierarchy.
    
    Parameters:
    object_string : And XML object string (a line in xml file).
    keep_list : An list of attributes name which want to keep.
    
    Return:
        The cleaned XML object string.
    """
    
    object_string = object_string.replace("*", "#");
    
    attributes = re.findall(r' [^<|^"|^\']*?=["|\']', object_string)
    # print(attributes)
    attributes = [re.findall(r'[^ |^=]+', x) for x in attributes]
    # print(attributes)
    attributes = [x for x in attributes if x[0] not in keep_list]
    
    for attr in attributes:
        try:
            sub_attr = " " + attr[0] + "=" + attr[1] + ".*?" + attr[1]
            object_string = re.sub(sub_attr, "", object_string)
        except Exception:
            pass

    # print(object_string)
    return object_string

# Main
os.chdir("./UIdata") 
filenames = os.listdir("./")
dirs = [d for d in filenames if "-output" in d]

output_dir = "./Masked/"
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
    
# Progressbar
Max = 20000
pbar = progressbar.ProgressBar(maxval = Max).start()

image_count = 0
masked_count = 0
for app_dir in dirs:
    app_name = app_dir.split("-")[0]
    dir_name = os.path.join(app_dir, "stoat_fsm_output", "ui")
    save_dir = output_dir + app_name + "/"
    if not os.path.exists(save_dir):
            os.mkdir(save_dir)
    
    visited_screenshot = []
    visited_screenshot_md5 = []
    
    files_names = os.listdir(dir_name)
    imgs = [d for d in files_names if "png" in d]
    
    for i in imgs:
        
        xml_name = [d for d in files_names if d == i.split(".")[0] + ".xml"]
        if len(xml_name) > 0:
            
            tree = ET.parse(dir_name + "/" + xml_name[0]) 
            root = tree.getroot()
            
            # Mask specific screen diretion image
            # '0' for only vertical, '1' for only horizon, '2' for both
            if root.attrib['rotation'] != '0':
                continue
            
            # Check duplicate screenshot
            with open(dir_name + "/" + xml_name[0]) as f:
                file_md5 = get_file_md5(f)
                if file_md5 in visited_screenshot_md5:
                    continue
                else:
                    visited_screenshot.append((file_md5, app_dir, i))
                    visited_screenshot_md5.append(file_md5)
            
            # Start to mask screenshot
            count = 0
            img_name = i
            find_all_element_by_attribute(root, "node", "class", "android.widget.Button")
            
            # Save original image
            if count > 0:
                img = Image.open(dir_name + "/" + i)
                img = img.crop((0,0,800,1216))
                img.save(save_dir + i)
                image_count += 1
                masked_count += count
                
            pbar.update(image_count)
            if image_count >= Max:
                break
        elif len(xml_name) > 1:
            print(app_name, xml_name, "==============================================>")

print("Have masked " + str(image_count) + " screenshots, gets " + str(masked_count) + " masked screenshots.")
