#!/usr/bin/env python

#conda activate google_vision_api

from IPython.display import display
import io
import os
import numpy as np
from google.cloud import vision
from google.cloud.vision_v1 import types
from google.protobuf.json_format import MessageToJson
import pandas as pd
from PIL import Image
import tempfile
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO
#ignore warning, can be remove
import warnings
#warnings.filterwarnings("ignore")
from PIL import Image, ImageFilter, ImageEnhance
import requests
import json
import urllib.request
import csv
import yaml
import PyPDF2
import logging

# Set up basic configuration for logging
'''
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
'''

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('application.log'),  # Log to this file
        logging.StreamHandler()  # Log to console
    ]
)

try:
    config_file_path = 'config.yml'
    with open(config_file_path, 'r') as file:
        config = yaml.safe_load(file)
        logging.info("Config data successfully read from path.")
except Exception as e:
    logging.error("Failed to load configuration: %s", e)
    raise SystemExit(e)

# Accessing configuration data
csv_input_file = config['csv_input_file']
csv_output_file = config['csv_split_output_file']
font_path = config['font_path']
image_directory_path = config['image_directory_path']
GOOGLE_APPLICATION_CREDENTIALS = config['GOOGLE_APPLICATION_CREDENTIALS']
img_quality = config['img_quality']
HAVE_OCR = config['HAVE_OCR']
# please see the google_API_intro.pdf to see how to get api key json file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS

# read csv from input node and return link
def read_csv_from_node(csv_input_file):
    try:
        data = pd.read_csv(csv_input_file)
        logging.info("CSV data successfully read from node.")
        return(data)
    except Exception as e:
        logging.error("Error reading CSV data from node: %s", e)
        raise SystemExit(e)
# return Example
'''
   Node_id                 Title          Language
0    16264             Sushi One  English,Japanese
1    16267  Harden & L. C. Corp.   English,Chinese
2    16270              Sung Lin   English,Chinese
'''

# process data from node
def process_node(node_id):
    res = {}
    res[node_id] = {}
    try:
        with urllib.request.urlopen("https://menus.digital.utsc.utoronto.ca/node/" + str(node_id) + "/children_rest") as url:
            node_data_from_link = json.loads(url.read().decode())
            # if node id is incorrect (unable to access) skip
            # from the web end the page will return []
            if len(node_data_from_link) >= 1:
                for node_data in node_data_from_link:
                    res[node_id][node_data['nid']] = {'Media_id': node_data['field_islandora_object_media'], 'Title': node_data['title'], "field_weight": node_data['field_weight']}
                logging.info("Node %s processed successfully.", node_id)
                return res
            logging.warning("Node %s returned an empty or insufficient data response.", node_id)
            return 0
    except urllib.error.URLError as e:
        logging.error("URL error occurred while processing node %s: %s", node_id, e.reason)
        return {}
    except json.JSONDecodeError as e:
        logging.error("JSON decode error occurred while processing node %s: %s", node_id, e.msg)
        return {}
    except Exception as e:
        logging.error("Unexpected error occurred while processing node %s: %s", node_id, str(e))
        return {}

'''
{16264: 
{'16266': {'Media_id': '36086', 'Title': 'Sushi One - Page 1'}, 
'16265': {'Media_id': '36085', 'Title': 'Sushi One - Page 2'}}}
'''
# access link after read_csv_from_node 
def access_node(data):
    # access from node
    res = {}
    for node_id in data['Node_id']:
        # if def process_node return is not equal 0 update data to res
        if process_node(node_id) != 0:
            res.update(process_node(node_id))
            logging.info("Node %s accessed and processed successfully.", node_id)
        else:
            logging.warning("Node %s processing returned 0, indicating a possible issue or empty data.", node_id)
    return res


# example return
'''
{'16266': {'Media_id': '36086', 'Title': 'Sushi One - Page 1'}, 
'16265': {'Media_id': '36085', 'Title': 'Sushi One - Page 2'}, 
'16268': {'Media_id': '36087', 'Title': 'Harden &amp; L. C. Corp. - Page 1'}, 
'16269': {'Media_id': '36088', 'Title': 'Harden &amp; L. C. Corp. - Page 2'}, 
'16272': {'Media_id': '36090', 'Title': 'Sung Lin - Page 1'}, 
'16271': {'Media_id': '36089', 'Title': 'Sung Lin - Page 2'}}
'''

# process media after we have the result for access_node
import urllib.error

def process_media(nid_title_media_id):
    for nodeid in list(nid_title_media_id.keys()):
        for node in list(nid_title_media_id[nodeid].keys()):
            media_url = "https://menus.digital.utsc.utoronto.ca/media/" + str(nid_title_media_id[nodeid][node]['Media_id']) + "?_format=json"
            try:
                with urllib.request.urlopen(media_url) as url:
                    media_data_from_link = json.load(url)
                    target_id = media_data_from_link.get('field_media_image')[0]['target_id']
                    # if target_id is not empty add target_id else remove node id
                    if target_id > 0:
                        nid_title_media_id[nodeid][node]['target_id'] = target_id
                        logging.info("Media processed for node %s, media %s with target ID %s.", nodeid, node, target_id)
                    else:
                        del nid_title_media_id[nodeid][node]
                        logging.warning("No target ID for node %s, media %s. Media removed.", nodeid, node)
            except urllib.error.URLError as e:
                logging.error("URL error occurred while accessing media for node %s, media %s: %s", nodeid, node, e.reason)
            except json.JSONDecodeError as e:
                logging.error("JSON decode error occurred while processing media for node %s, media %s: %s", nodeid, node, e.msg)
            except Exception as e:
                logging.error("Unexpected error occurred while processing media for node %s, media %s: %s", nodeid, node, str(e))
    return nid_title_media_id
# return example
'''
{'16266': {'Media_id': '36086', 'Title': 'Sushi One - Page 1', 'target_id': 59809}, 
'16265': {'Media_id': '36085', 'Title': 'Sushi One - Page 2', 'target_id': 59806}, 
'16268': {'Media_id': '36087', 'Title': 'Harden &amp; L. C. Corp. - Page 1', 'target_id': 59812}, 
'16269': {'Media_id': '36088', 'Title': 'Harden &amp; L. C. Corp. - Page 2', 'target_id': 59815}, 
'16272': {'Media_id': '36090', 'Title': 'Sung Lin - Page 1', 'target_id': 59821},
'16271': {'Media_id': '36089', 'Title': 'Sung Lin - Page 2', 'target_id': 59818}}
'''

def process_file(mid_data):
    for nodeid in list(mid_data.keys()):
        for node in list(mid_data[nodeid].keys()):
            try:
                base_dir = os.path.expanduser(image_directory_path + 'pdf/' + str(nodeid) + '/' + str(node))
                if not os.path.exists(base_dir):
                    os.makedirs(base_dir)

                file_url = "https://menus.digital.utsc.utoronto.ca/file/" + str(mid_data[nodeid][node]['target_id']) + "?_format=json"
                with urllib.request.urlopen(file_url) as url:
                    media_data_from_link = json.load(url)
                    url_link = media_data_from_link['uri'][0]['url']
                    local_file_name = url_link.split('/')[-1]
                    title_name = mid_data[nodeid][node]['Title'].replace(" ", "").replace("-", "")
                    local_file_name = f"{nodeid}_{node}_{title_name}_{local_file_name}"
                    full_path = os.path.join(base_dir, local_file_name)
                    mid_data[nodeid][node]['local_path'] = full_path

                    response = requests.get("https://menus.digital.utsc.utoronto.ca" + url_link)
                    if response.status_code == 200:
                        with open(full_path, 'wb') as file:
                            file.write(response.content)
                        logging.info("Successfully downloaded and saved file: %s", full_path)
                    else:
                        logging.warning("Failed to download file from %s. Status code: %s", url_link, response.status_code)
            except urllib.error.URLError as e:
                logging.error("URL error occurred while processing file for node %s, node %s: %s", nodeid, node, e.reason)
            except json.JSONDecodeError as e:
                logging.error("JSON decode error occurred while processing file for node %s, node %s: %s", nodeid, node, e.msg)
            except Exception as e:
                logging.error("Unexpected error occurred while processing file for node %s, node %s: %s", nodeid, node, str(e))
                    #image = Image.open(BytesIO(response.content))
                    #image.save(full_path, 'JPEG', quality=85)

# save file to local path and full out format csv. Input csv
def get_mid_data(csv_input_file):
    node_data = read_csv_from_node(csv_input_file)
    nid_title_media_id = access_node(node_data)
    mid_data =  process_media(nid_title_media_id)
    return mid_data

def download_file(csv_input_file):
    mid_data = get_mid_data(csv_input_file)
    process_file(mid_data)

# read all the images from directory or local path
def find_all_img_path(image_directory_path):
    abs_path = os.path.join(image_directory_path, 'pdf')
    image_extensions = ['.jpg', '.png', '.jp2', '.tiff', '.tif']
    image_paths = []
    desired_prefix = 'OBJ'
    # Walk through the directory
    try:
        for root, dirs, files in os.walk(abs_path):
            for file in files:
                full_path = os.path.join(root, file)
                #if any(file.endswith(ext) for ext in image_extensions) and desired_prefix in file:

                if any(file.endswith(ext) for ext in image_extensions) and desired_prefix in file:
                    image_paths.append(full_path)
        logging.info("Successfully found %d images in %s", len(image_paths), abs_path)
    except Exception as e:
        logging.error("Error finding images in %s: %s", abs_path, str(e))
    
    return image_paths
# return example
'''
"\n\n['C:\\Users\\zxx91\\OBJ.0_10762.jp2',
\n'C:\\Users\\zxx91\\OBJ.0_10763.jp2', 
\n'C:\\Users\\zxx91\\OBJ.0_10764.jp2', 
\n'C:\\Users\\zxx91\\OBJ.0_10765.jp2', 
\n'C:\\Users\\zxx91\\OBJ.0_10766.jp2', 
\n'C:\\Users\\zxx91\\OBJ.0_10767.jp2']\n"
'''

# read all the images from directory or local path
def find_all_json_path(image_directory_path):
    abs_path = os.path.join(image_directory_path, 'pdf')
    json_extensions = ['.json']
    json_paths = []
    desired_prefix = 'OBJ'
    # Walk through the directory
    try:
        for root, dirs, files in os.walk(abs_path):
            for file in files:
                full_path = os.path.join(root, file)
                if any(file.endswith(ext) for ext in json_extensions) and desired_prefix in file:
                    json_paths.append(full_path)
        logging.info("Successfully found %d images in %s", len(json_paths), abs_path)
    except Exception as e:
        logging.error("Error finding images in %s: %s", abs_path, str(e))
    
    return json_paths

# Initialize the client for the Vision API
client = vision.ImageAnnotatorClient()
def detectText(img):
    try:
        # Check if the file is a JP2 file
        with Image.open(img) as opened_image:
            # Convert to RGB if not already in JPEG format (necessary for non-JPEG formats)
            if opened_image.format != 'JPEG':
                with io.BytesIO() as output:
                    opened_image.convert('RGB').save(output, format="JPEG")
                    content = output.getvalue()
            else:
                # For JPEG (including JP2 handled by Pillow), read directly
                with io.open(img, 'rb') as image_file:
                    content = image_file.read()
        # Prepare the image for the Vision API
        image = types.Image(content=content)
        
        # Perform text detection
        response = client.text_detection(image=image)
        logging.info("Text detection successful for image: %s", img)
        return response
    except IOError as e:
        logging.error("IOError in detecting text for image %s: %s", img, e)
    except Exception as e:
        logging.error("Unexpected error in detecting text for image %s: %s", img, str(e))
        # Consider what to return or how to handle errors in your application context
        # Could return None, or raise the exception further after logging
        return None

    
# save google vision api result into json
def save_API_json(image_directory_path):
    '''
    img = '/home/dsu/notebooks/collection_utilities/ocr_processing/pdf/518/519/518_519_MapleGardenPage2_OBJ.0.tif'
    response = detectText(img)
    response_json = MessageToJson(response._pb)
    if '.tif' in img:
        json_file_name = img.replace(".tif", ".json")
    with open(json_file_name, "w") as json_file:
        json_file.write(response_json)
    '''
    base_dir = os.path.expanduser(image_directory_path + 'pdf')
    try:
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        all_img_path = find_all_img_path(image_directory_path)
        json_file_path = []
        for img in all_img_path:
            try:
                image_path = img.split('/')[-1]
                node_id, media_id = image_path.split('_')[:2]
                node_dir = os.path.expanduser(f"{base_dir}/{node_id}")
                media_dir = os.path.expanduser(f"{node_dir}/{media_id}")
                if not os.path.exists(media_dir):
                    os.makedirs(media_dir)
                response = detectText(img)
                response_json = MessageToJson(response._pb)
                if '.jpg' in image_path:
                    json_file_name = image_path.replace(".jpg", ".json")
                elif '.png' in image_path:
                    json_file_name = image_path.replace('.png', ".json")
                elif '.jp2' in image_path:
                    json_file_name = image_path.replace('.jp2', ".json")
                elif image_path.endswith('.tiff'):
                    json_file_name = image_path.replace('.tiff', ".json")
                elif image_path.endswith('.tif'):
                    json_file_name = image_path.replace('.tif', ".json")
                # json_file_name = image_path.replace('.jp2', '.json')
                json_file_path = json_file_path + [media_dir+'/'+json_file_name]
                with open(media_dir+'/'+json_file_name, "w") as json_file:
                    json_file.write(response_json)
            except Exception as e:
                logging.error("Error processing image %s: %s", img, str(e))
        return json_file_path
    except Exception as e:
        logging.error("Error setting up directories or processing images: %s", str(e))
        return []
    
# in this part, we will write the csv for header 
# "Node_id", "Title", "Media_id", "Local_File_Path", "OCR_File_Path"
# The PDF/A will use OCR json

# write csv file
def write_csv(csv_output_file, transformed_data, headers):
    try:
        with open(csv_output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            for row in transformed_data:
                # Optionally, handle specific keys more dynamically if needed
                row.pop('local_path', None)
                writer.writerow(row)
        logging.info(f"CSV file successfully written to {csv_output_file}")
    except IOError as e:
        logging.error(f"IOError occurred while writing CSV to {csv_output_file}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error occurred while writing CSV to {csv_output_file}: {e}")
        
# output csv with json
def output_csv_json(csv_input_file, csv_output_file, image_directory_path):
    mid_data = get_mid_data(csv_input_file)
    all_img_path = find_all_img_path(image_directory_path)
    save_API_json(image_directory_path)
    json_file_path = find_all_json_path(image_directory_path)
    transformed_data = []
    headers = ["Node_id", "Title", "field_weight","Media_id", "Model", "Local_File_Path", "OCR_File_Path"]
    # img_json_pairs = zip(all_img_path, json_file_path)
    csv_node = read_csv_from_node(csv_input_file)
    node_title = csv_node['title']
    node_csv_id = csv_node['Node_id']
    for main_id, nodes in mid_data.items():
        if main_id in node_csv_id.values:
            title_index = node_csv_id[node_csv_id == main_id].idxmax()
            row = {
                "Node_id": main_id,
                "Title": node_title[title_index],
                "field_weight": None,
                "field_weight": None,
                "Media_id": None,
                "Model": "Combined",
                "Local_File_Path": None,
                "OCR_File_Path": None 
            }
            transformed_data.append(row)
            
        for node_id, details in nodes.items():
            # this should be optimize
            search_term = details['Title'].replace(" ", "").replace("-", "")
            index = next((i for i, path in enumerate(all_img_path) if ('/' + node_id + '/' in path)), None)
            row = {
                "Node_id": node_id,
                "Title": details['Title'],
                "field_weight": details['field_weight'],
                "Media_id": details['Media_id'],
                "Model": "Individual",
                "Local_File_Path": all_img_path[index],
                "OCR_File_Path": json_file_path[index] 
            }
            row.pop('target_id', None)
            transformed_data.append(row)
    write_csv(csv_output_file, transformed_data, headers)

    

# generate pdf/A with selectable text and return file name
def create_pdf_with_selectable_text(media_dir, image_directory_path, json_data):
    # Open the image to get its dimensions
    pdfmetrics.registerFont(TTFont('NotoSansCJK', font_path)) 
    with Image.open(image_directory_path) as img:
        img_width, img_height = img.size
        # Save the image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_img_file:
            img.save(temp_img_file, format='JPEG', quality=img_quality)
            temp_img_path = temp_img_file.name
        # Create a PDF with the same size as the image
        if '.jpg' in os.path.basename(image_directory_path):
            temp_name = os.path.basename(image_directory_path).replace(".jpg", ".pdf")
        elif '.png' in os.path.basename(image_directory_path):
            temp_name = os.path.basename(image_directory_path).replace('.png', ".pdf")
        elif '.jp2' in os.path.basename(image_directory_path):
            temp_name = os.path.basename(image_directory_path).replace('.jp2', '.pdf')
        elif os.path.basename(image_directory_path).endswith('.tiff'):
            temp_name = os.path.basename(image_directory_path).replace('.tiff', ".pdf")
        elif os.path.basename(image_directory_path).endswith('.tif'):
            temp_name = os.path.basename(image_directory_path).replace('.tif', ".pdf")
        
        pdf_path = os.path.join(media_dir, temp_name)
        c = canvas.Canvas(pdf_path, pagesize=(img_width, img_height))
        c.setFont('NotoSansCJK', 12)
        # Add the image to the PDF at its original size
        c.drawImage(temp_img_path, 0, 0, width=img_width, height=img_height)

        # If 'textAnnotations' is in json_data, add the text; otherwise, just save the image as is
        if 'textAnnotations' in json_data:
            texts = json_data['textAnnotations'][1:]  # Skip the first summary item
            for text in texts:
                vertices = text['boundingPoly']['vertices']
                if len(vertices) >= 4:  # Ensure there are enough points to define a rectangle
                    x0, y0 = vertices[0]['x'], img_height - vertices[0]['y']
                    text_height = vertices[3]['y'] - vertices[0]['y']
                    c.setFillColorRGB(0, 0, 0, 0)
                    c.drawString(x0, y0 - text_height, text['description'])
        c.save()
        os.remove(temp_img_path)
    return pdf_path

# read json file to get the google vision api result from json
def read_json_api_result(csv_output_file):
    base_dir = os.path.expanduser(image_directory_path+'pdf')
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    pdf_file_path = []

    data = read_csv_from_node(csv_output_file)
    vision_api_response_file = data['OCR_File_Path']
    image_csv_file = data['Local_File_Path']
    for vision_api_response in range(len(vision_api_response_file)):
        if not isinstance(vision_api_response_file[vision_api_response], float):
            print(vision_api_response_file[vision_api_response])
            response = extract_bounding_polys(vision_api_response_file[vision_api_response])
            img = image_csv_file[vision_api_response]
            image_path = img.split('/')[-1]
            node_id = image_path.split('_')[0]
            media_id = image_path.split('_')[1]
            node_dir = os.path.expanduser(base_dir+'/'+str(node_id))
            media_dir = os.path.expanduser(node_dir+'/'+str(media_id)+'/')
            if not os.path.exists(media_dir):
                os.makedirs(media_dir)
            pdf_file = create_pdf_with_selectable_text(media_dir, img, response)
    output_csv_pdf(csv_output_file)


def extract_bounding_polys(vision_api_response):
    with open(vision_api_response) as file:
        response = json.load(file)
    return response

# save pdf/a file into the csv_output_file
def output_csv_pdf(csv_output_file):
    data = read_csv_from_node(csv_output_file)
    vision_api_response_file = data['OCR_File_Path']
    data['PDF_File_Path'] = ''
    
    for i in range(len(vision_api_response_file)):
        if not isinstance(vision_api_response_file[i], float):
            data.loc[i, 'PDF_File_Path'] = vision_api_response_file[i].replace('.json', '.pdf')
    data.to_csv(csv_output_file, index=False)

#Combining multiple PDF files into a single PDF
'''
def combine_pdf(target_paths, output_filename):
    pdf_writer = PyPDF2.PdfWriter()
    print(target_paths, output_filename)
    for path in target_paths:
        pdf_reader = PyPDF2.PdfReader(path)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

    with open(output_filename, 'wb') as out:
        pdf_writer.write(out)
'''
def combine_pdf(target_paths, output_filename):
    # if target_paths do have file, remove it before create new combine pdf 
    pdf_writer = PyPDF2.PdfWriter()
    for path in target_paths:
        try:
            pdf_reader = PyPDF2.PdfReader(path)
            if not pdf_reader.pages:
                logging.info(f"Warning: '{path}' contains no pages. Skipping.")
                continue
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        except Exception as e:
            logging.error(f"Error reading '{path}': {e}")
            continue

    if pdf_writer.pages:
        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)
        logging.info(f"PDF successfully created: {output_filename}")
    else:
        logging.info("No pages were added to the PDF writer. Output PDF not created.")

def save_csv_combine(csv_output_file):
    data = read_csv_from_node(csv_output_file)
    node_data = read_csv_from_node(csv_input_file)
    #vision_api_pdf_file = data['PDF_File_Path']
    vision_api_pdf_file = data[data['PDF_File_Path'].fillna('').astype(str) != ""]
    vision_api_pdf_file = vision_api_pdf_file['PDF_File_Path']
    abs_path = os.path.join(image_directory_path, 'pdf')
    for i in range(len(node_data)):
        matching_paths = [path for path in vision_api_pdf_file if 'pdf/' + str(node_data['Node_id'][i]) + '_' in path or 'pdf/' + str(node_data['Node_id'][i]) + '/' in path]
        if len(matching_paths) >= 1:
            combine_pdf(matching_paths, abs_path +'/'+ str(node_data['Node_id'][i]) + '/' + str(node_data['Node_id'][i]) +'.pdf')
            #data['PDF_File_Path'][i] = abs_path+'/'+ str(node_data['Node_id'][i]) + '/' + str(node_data['Node_id'][i]) +'.pdf'
            node_id = node_data.loc[i, 'Node_id']
            temp_pdf_file_path = abs_path + '/' + str(node_id) + '/' + str(node_id) + '.pdf'
            data.loc[data['Node_id'] == node_id, 'PDF_File_Path'] = temp_pdf_file_path
    data.to_csv(csv_output_file, index=False)
    
    '''
    for vision_api_response in range(len(vision_api_pdf_file)):
        if isinstance(vision_api_pdf_file[vision_api_response], float):
            print(11111)
            target_node = str(data['Node_id'][vision_api_response])  # Convert to string here
            # Use target_node to find all the pdfs in PDF_File_Path
            target_paths = data[data['PDF_File_Path'].astype(str).str.contains(target_node, na=False)]
            target_paths = target_paths['PDF_File_Path'].tolist()
            
            combine_pdf(target_paths, abs_path +'/'+ str(target_node)+ '/' +str(target_node)+'.pdf')
            data['PDF_File_Path'][vision_api_response] = abs_path+'/'+str(target_node)+'/'+str(target_node)+'.pdf'
    data.to_csv(csv_output_file, index=False)
    '''
    
def google_vision_api_run(HAVE_OCR):
    if HAVE_OCR == False:
        download_file(csv_input_file)
        output_csv_json(csv_input_file, csv_output_file, image_directory_path)
        read_json_api_result(csv_output_file)
        save_csv_combine(csv_output_file)
        print("Done")
    else:
        read_json_api_result(csv_output_file)
        save_csv_combine(csv_output_file)
        print("Done")

google_vision_api_run(HAVE_OCR)