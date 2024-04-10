# DSU_googleAPI
 <!-- ### In order to have google vision api key
#### Watch this tutorial (1:04 - 4:50) https://www.youtube.com/watch?v=wfyDiLMGqDM&list=PL3JVwFmb_BnSLFyVThMfEavAEZYHBpWEd&index=2
#### After this tutorial, you should have a JSON API key, which you need to place in your workspace path
#### In ~/DSU_googleAPI/config.yml edit ‘GOOGLE_APPLICATION_CREDENTIALS’ replace '<Your API KEY>' to your API key path
 -->

<!-- BEGIN-MARKDOWN-TOC -->
* [Installation](#installation)
* [Usage](#usage)
* [Functions](#functions)
<!-- END-MARKDOWN-TOC -->

## Installation

Create new env using conda:
```
conda create -n <env -name>
```

Activate conda env:
```
conda activate <env -name>
```

Install requirements:

```
pip install -r requirements.txt
```

## Usage
Edit config.yml:
```
csv_input_file <input CSV file path ex: repo_info.csv>
csv_split_output_file: <output CSV file name and path ex: csv_output.csv>
font_path: <Font path (support multi-language required)>
image_directory_path: <PDF, OCR JSON, Image save path>
GOOGLE_APPLICATION_CREDENTIALS: <Your Google application key path>
img_quality: <1 - 95>
HAVE_OCR: <False/True>
```

In terminal:
First, direct to the working path:
```
cd ~/DSU_googleAPI
```
Second, activate env:
```
conda activate <env -name>
```
Third, run the Python code:
```
python google_vision_api
```

## Functions
```
read_csv_from_node(csv_input_file)
```
- usage: read CSV file as pandas data frame
- input: CSV file path ('\csv_input_file.csv') 
- return: pandas data frame

| Node_id | Title                 | Language          |
|---------|-----------------------|-------------------|
| 16264   | Sushi One             | English,Japanese |
| 16267   | Harden & L. C. Corp. | English,Chinese  |
| 16270   | Sung Lin              | English,Chinese  |

```
access_node(node_data)
```
- usage: access each page from Node_id get media ID, title
- input: pandas data frame from read_csv_from_node output
- return:
```
{'16266': {'Media_id': '36086', 'Title': 'Sushi One - Page 1'}, 
'16265': {'Media_id': '36085', 'Title': 'Sushi One - Page 2'}, 
'16268': {'Media_id': '36087', 'Title': 'Harden &amp; L. C. Corp. - Page 1'}, 
'16269': {'Media_id': '36088', 'Title': 'Harden &amp; L. C. Corp. - Page 2'}, 
'16272': {'Media_id': '36090', 'Title': 'Sung Lin - Page 1'}, 
'16271': {'Media_id': '36089', 'Title': 'Sung Lin - Page 2'}}
```
 
```
process_media(nid_title_media_id)
```
- usage: get target ID from access_node output
- input: dictionary with structure {node_id:{'Media_id': '36089', 'Title': 'Sung Lin - Page 2'}} 
- return: 
```
{'16266': {'Media_id': '36086', 'Title': 'Sushi One - Page 1', 'target_id': 59809}, 
'16265': {'Media_id': '36085', 'Title': 'Sushi One - Page 2', 'target_id': 59806}, 
'16268': {'Media_id': '36087', 'Title': 'Harden &amp; L. C. Corp. - Page 1', 'target_id': 59812}, 
'16269': {'Media_id': '36088', 'Title': 'Harden &amp; L. C. Corp. - Page 2', 'target_id': 59815}, 
'16272': {'Media_id': '36090', 'Title': 'Sung Lin - Page 1', 'target_id': 59821},
'16271': {'Media_id': '36089', 'Title': 'Sung Lin - Page 2', 'target_id': 59818}}
```

```
process_file(mid_data)
```
- usage: download image from target ID
- input: dictionary with structure {'16271': {'Media_id': '36089', 'Title': 'Sung Lin - Page 2', 'target_id': 59818}} 
- return: None

```
download_file(csv_input_file)
```
- usage: download image helper
- input: csv_input_file path
- return: None

```
find_all_img_path(image_directory_path)
 ```
- usage: read all the images from directory or local path
- input: image_directory_path (setup in config)
- return: list of images path
```
"\n\n['C:\\Users\\zxx91\\OBJ.0_10762.jp2',
\n'C:\\Users\\zxx91\\OBJ.0_10763.jp2', 
\n'C:\\Users\\zxx91\\OBJ.0_10764.jp2', 
\n'C:\\Users\\zxx91\\OBJ.0_10765.jp2', 
\n'C:\\Users\\zxx91\\OBJ.0_10766.jp2', 
\n'C:\\Users\\zxx91\\OBJ.0_10767.jp2']\n"
```

```
detectText(img)
```
- usage: read all the images from the directory or local path
- input: image path from find_all_img_path 'C:\\Users\\zxx91\\OBJ.0_10767.jp2'
- return: response in JSON form from Google Vision API
- ![image](https://github.com/zhoux121/DSU_googleAPI/assets/21269237/d163779c-6b86-4726-a6bd-9363595b9027)

```
save_API_json(image_directory_path)
```
- usage: save Google Vision results into JSON file
- input: image_directory_path (setup in config)
- return: list of JSON path
['C:\\Users\\zxx91\\OBJ.0_10762.json', 'C:\\Users\\zxx91\\OBJ.0_10767.json']

```
write_csv(csv_output_file, transformed_data, headers)
```
- usage: helper function for saving data into CSV
- input: csv_output_file: CSV save path, transformed_data: data, headers: data frame: headers
- return: None
  
```
output_csv_json(csv_input_file, csv_output_file, image_directory_path)
```
- usage: save image path, node, title into csv
- input: csv_output_file: CSV input path, csv_output_file: CSV save path, image_directory_path: image path 'C:\\Users\\zxx91\\OBJ.0_10762.jp2'
- return: None

```
create_pdf_with_selectable_text(media_dir, image_directory_path, json_data, font_path)
```
- usage: create selectable/searchable text for pdf
- input: csv_output_file: media_dir, image_directory_path, json_data, font_path
- return: pdf path ['C:\\Users\\zxx91\\OBJ.0_10762.pdf']

```
read_json_api_result(csv_output_file)
```
- usage: read the JSON file to get the Google Vision API result from JSON file
- input: csv_output_file
- return: None

```
 extract_bounding_polys(vision_api_response)
```
- usage: Helper function for reading Google Vision API results from JSON file
- input: csv_output_file[OCR_File_Path] it is the JSON file location
- return:  ![image](https://github.com/zhoux121/DSU_googleAPI/assets/21269237/d163779c-6b86-4726-a6bd-9363595b9027)

```
output_csv_pdf(csv_output_file,pdf_file_path)
```
- usage: Helper function for saving pdf/a file into the csv_output_file
- input: csv_output_file,pdf_file_path
- return: None

```
combine_pdf(target_paths, output_filename)
```
- usage: helper function Combining multiple PDF files into a single PDF
- input: target_paths: pdf that has same title name, in list format, output_filename: combined pdf saving path
- return: None

```
save_csv_combine(csv_output_file)
```
- usage: Combining multiple PDF files into a single PDF
- input: csv_output_file CSV file
- return: None

```
google_vision_api_run(HAVE_OCR):
```
- usage: the main function that sets False for the first time run, True for editing the image quality without request API and download image again
- input: HAVE_OCR: TRUE/False
- return: None
