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
