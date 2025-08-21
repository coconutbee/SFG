import os
import shutil

root = 'male_test'
output = 'male_sample'

os.makedirs(output, exist_ok=True)
count = 0
for base, sub, file in os.walk(root):
    for img in file:
        if count < 1: 
            img_path = os.path.join(base, img)
            output_path = os.path.join(output, img)
            # print(output_path)
            shutil.move(img_path, output_path)
            count += 1
        else:
            count = 0
            break