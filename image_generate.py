import io
import cv2
import base64
import requests
import os
from PIL import Image

#####################################
# Stable Diffusion API URL
url = "http://127.0.0.1:7860"
#####################################

# Function to read prompts from folder
def read_prompts_from_folder(folder_path):
    prompts = {}
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if os.path.isfile(file_path) and file_name.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    print(f"Reading prompt file: {file_path}")
                    prompt = file.read().strip()
                    base_name = os.path.splitext(file_name)[0]
                    prompts[base_name] = prompt
    return prompts

# Function to generate Canny edge image and encode to base64
def generate_canny_edge(input_image_path, low_threshold=100, high_threshold=200):
    img = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error reading image: {input_image_path}")
        return None, None

    edges = cv2.Canny(img, low_threshold, high_threshold)
    canny_output_dir = "./canny_edges"
    os.makedirs(canny_output_dir, exist_ok=True)
    canny_output_path = os.path.join(canny_output_dir, f"{os.path.splitext(os.path.basename(input_image_path))[0]}_canny.png")
    cv2.imwrite(canny_output_path, edges)
    print(f"Canny edge image saved: {canny_output_path}")

    _, buffer = cv2.imencode('.png', edges)
    encoded_edges = base64.b64encode(buffer).decode('utf-8')
    return encoded_edges, canny_output_path

# Function to generate image using txt2img API with ControlNet
def generate_image_from_prompt(prompt, image_name, canny_image_base64, canny_image_path):
    print(f"Currently using input image: {image_name} and Canny edge image: {os.path.basename(canny_image_path)}")

    payload = {
        "prompt": prompt,
        "negative_prompt": "cropped, easynegative, censored, furry, 3d, photo, monochrome, elven ears, anime, extra legs, extra hands, mutated legs, mutated hands, extra fingers",
        "width": 512,
        "height": 512,
        "steps": 40,
        "batch_size": 1,
        "cfg_scale": 7,
        "sampler_name": "DDIM",
        "override_settings": {
            "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors"
        },
        "alwayson_scripts": {
            "controlnet": {
                "args": [
                    {
                        "enabled": True,
                        "image": canny_image_base64,
                        "module": "canny",
                        "model": "control_v11p_sd15_canny [d14c016b]",
                        "weight": 0.5
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
        response.raise_for_status()
        r = response.json()
        result = r['images'][0]
        generated_image = Image.open(io.BytesIO(base64.b64decode(result.split(",", 1)[0])))
        output = output_dir
        if not os.path.exists(output):
            os.makedirs(output)
        output_path = os.path.join(output_dir, f"{image_name}.png")
        generated_image.save(output_path)
        print(f"Generated image saved: {output_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error generating image: {e}")

if __name__ == '__main__':
    prompt_folder = "test"
    image_folder = "female_sample"
    output_dir = 'female_gen'
    os.makedirs(output_dir, exist_ok=True)

    prompts = read_prompts_from_folder(prompt_folder)
    image_files = []
    for root, _, files in os.walk(image_folder):
        for f in files:
            if f.endswith('.png') or f.endswith('.jpg'):
                image_files.append(os.path.join(root, f))

    for image_file in image_files:
        path_parts = os.path.normpath(image_file).split(os.sep)
        # sub = path_parts[-2]
        # race = path_parts[-3]

        image_name = os.path.splitext(os.path.basename(image_file))[0]  # Only the base name
        prompt_key = image_name  # No need for additional formatting

        if prompt_key in prompts:
            prompt = prompts[prompt_key]
            image_path = image_file  # image_file already contains the full path
            print(f"Generating image: {image_name} with prompt: {prompt}")

            canny_image_base64, canny_image_path = generate_canny_edge(image_path)
            
            if canny_image_base64:
                generate_image_from_prompt(prompt, image_name, canny_image_base64, canny_image_path)
        else:
            print(f"No prompt found for image {image_name}")
