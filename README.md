# DSU_googleAPI
### In order to have google vision api key
#### Watch this tutorial (1:04 - 4:50) https://www.youtube.com/watch?v=wfyDiLMGqDM&list=PL3JVwFmb_BnSLFyVThMfEavAEZYHBpWEd&index=2
#### After this tutorial, you should have a JSON API key, which you need to place in your workspace path
#### In ~/DSU_googleAPI/config.yml edit ‘GOOGLE_APPLICATION_CREDENTIALS’ replace '<Your API KEY>' to your API key path

# Usage
## First edit config.yml
#### Change csv_input_file to your input CSV file path
#### Change csv_output_file to your output CSV file path
#### Change image_directory_path to your image save path
## Second install requirement.txt
#### pip install -r requirements.txt
## Third run code
#### python ./google_vision_api
