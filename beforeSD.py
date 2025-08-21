import re
import os

# 指定 .md 文件的資料夾路徑
# num = 0

# race = 'asian'
# file_path = f"./male_{race}/{num}"
# output_path = f"./male_selected/{race}_{num}"
output_path = "test"
file_path = "female_prompt" # md檔的位置

# 如果目標輸出目錄不存在，則創建
if not os.path.exists(output_path):
    os.makedirs(output_path)

# 遍歷指定資料夾中的所有文件
for filename in os.listdir(file_path):
    # 確保只處理 .md 文件
    if filename.endswith(".md"):
        full_file_path = os.path.join(file_path, filename)
        
        # 讀取文件內容
        with open(full_file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()
            image_name = os.path.basename(filename).split('.')[0]
            
            # 用於存儲結果的列表
            results = []

            # 逐行處理文件內容
            for line in content:
                line = line.strip()  # 去除首尾空格
                print(f"正在處理行: '{line}'")  # 調試輸出每一行的內容

                # 修改正則表達式來匹配行中的加粗和數字序號
                match = re.match(r'^\d+\.\s*\*\*(\w+)\*\*:\s*(.*)$', line)
                if match:
                    key = match.group(1).strip()  # 提取key
                    value = match.group(2).strip()  # 提取value
                    results.append(f"{value}")
                    # results.append(f"{key}:{value}")
                else:
                    print(f"無法匹配: '{line}'")
            # 確保有提取到的結果
            if results:
                # 將結果列表轉換為逗號分隔的字符串
                result_str = ', '.join(results)
                print(f"處理文件: {filename} -> {result_str}")

                # 寫入數據
                txt_file_path = os.path.join(output_path, f"{image_name}.txt")
                with open(txt_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(result_str + '\n')
            else:
                print(f"無法從文件 {filename} 中提取到任何內容。")
