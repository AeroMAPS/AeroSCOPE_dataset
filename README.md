<p align="center">
  <img src=https://github.com/AeroMAPS/AeroSCOPE/assets/97613437/1824dcdd-1c25-489c-96e0-4897a0773b7c />
</p>


# Welcome 
AeroSCOPE is a project that aims to bring together various open data sources on air transport in order to better understand the geographical distribution of air transport.
More details on data collection and compilation can be found in the article accompanying this work: XXXX (TODO)


## Setup

It is suggested to use a new [conda](https://docs.conda.io/en/latest/miniconda.html) virtual environment to install the required packages.
Pyhton 3.10 is suggested, altough older versions might work.

In the new virtual environment, navigate to the project folder. Most installs are made using poetry, except for poetry itself whic can be nstalled using pip or conda.

```bash
pip install poetry 
poetry install 
```

## Usage
There are two distinct ways to use AeroSCOPE.

* Simple usage: only to use the graphical interface or to download the final database, no external inputs are required.
* Advanced usage: run all the data collection and processing notebooks. External data inputs, too large to be stored on git or whose diffusion is restricted are needed.

### Simple usage

__Raw database csv file:__ 
The last version of the processed database is stored at [Final Dataset](https://github.com/AeroMAPS/AeroSCOPE/blob/main/TrafficEstimator/03_routes_schedule/data/final_26_09.csv). 
Be sure to replace default NaN (such as NA) when reading the csv, to avoid mistakingly consider North America and Namibia codes as NaN.

__AeroSCOPE app:__
To run the simple web app designed to explore the data, one can either visit www.aeroscope.isae-supaero.fr or navigate to the 04_app folder using a terminal and run the app using voila.

```bash
cd (path to 04_app) 
voila front-dev.ipynb
```

### Adavanced usage

The process data collection is widely described in each notebook. Here, the articulation of the different notebooks and folders is described.  

TODO few words on teh overall process.

The first folder ([01_wikipedia_parser](https://github.com/AeroMAPS/AeroSCOPE/tree/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/01_wikipedia_parser)) stores the data and notebooks used to parse Wikipedia for airport information and flight routes. **In case the user wants to re-run the notebooks, please be aware that without precautions, the most recent version of wikipedia will be parsed, thus erasing the data collected for this work.**   
- [01-airport_parsing.ipynb](https://github.com/AeroMAPS/AeroSCOPE/blob/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/01_wikipedia_parser/01-airport_parsing.ipynb) is used to retreive all airports pages urls and then to parse their wikipedia and wikidata informations.
- [02-routes_parsing.ipynb](https://github.com/AeroMAPS/AeroSCOPE/blob/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/01_wikipedia_parser/02-routes_parsing.ipynb) is used to retreive all routes starting from each of the previously found airport. Note that this notebook would be particularly sensitive to a new run, as routes are constantly updated.
- [03-routes_processing.ipynb](https://github.com/AeroMAPS/AeroSCOPE/blob/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/01_wikipedia_parser/03-routes_processing.ipynb) is essentially a processing notebook, building on the results from teh two previous notebooks.

The second folder ([02_airport_features](https://github.com/AeroMAPS/AeroSCOPE/tree/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/02_airport_features)) is used to add external features to each airport found previously such as population data, economical or geographical data.
- [00_kontur_loading](https://github.com/AeroMAPS/AeroSCOPE/blob/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/02_airport_features/00_kontur_loading.ipynb) is a side-notebook, to load and process a very large, density base population dataset. Since the input dataset weighs 6 Gb (compressed in .gpkg), it isn not worth it to store an version it => download it at [Kontur 400m Data](https://geodata-eu-central-1-kontur-public.s3.amazonaws.com/kontur_datasets/kontur_population_20220630.gpkg.gz) and put it in the data folder. Similarly, the output csv file weighs 916 Mo, so it is not stored either. **Therefore this notebook should be run before 01_airport_features_construction**.  
- [01_airport_features_construction.ipynb](https://github.com/AeroMAPS/AeroSCOPE/blob/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/02_airport_features/01_airport_features_construction.ipynb) effectively adds the informations described before to the wikipedia-parsed airport database.

The third folder ([03_routes_schedule](https://github.com/AeroMAPS/AeroSCOPE/tree/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/03_routes_schedule)) is used to store the notebooks compiling the various datasets, to perform the learning and estimation on routes where the traffic is unknown and finally also the notebooks testing the final dataset.
- [00_oag_preprocessing.ipynb](https://github.com/AeroMAPS/AeroSCOPE/blob/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/03_routes_schedule/00_oag_preprocessing.ipynb) is a side-notebook used to load and preprocess OAG dataset, that is used in the test notebook as a comparison source. Unfortunately, this data being proprietary, it is impossible to disclode neither the source file nor the process oag file.
- [01_routes_preparation.ipynb](https://github.com/AeroMAPS/AeroSCOPE/blob/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/03_routes_schedule/01_routes_preparation.ipynb) is used to merge the route database with the completed airport informations. Traffic information (number of seats availabe) is added to each route existing open source databases onto the route database. 
Most input files are includede in the repository, excepted:
  - BTS/T_T100_SEGMENT_ALL_CARRIER_2019.csv -> dowloadable on [US BTS](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FMG)
  - Eurocontrol -> four month of 2019 data, downloadable for the reasearch community [Eurocontrol](https://ext.eurocontrol.int/prisme_data_provision_hmi/) (requires account creation)
  - OpenSky -> 12 months of 2019 data, processed in [osky_data_extraction.ipynb](https://github.com/AeroMAPS/AeroSCOPE/blob/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/Utilities/osky_data_extraction.ipynb) and downloadable at [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7923702.svg)](https://doi.org/10.5281/zenodo.7923702). The notebbok gather the months together and filter the data to flight were the final data point is below 1000ft.
- [02_routes_estimation.ipynb](https://github.com/AeroMAPS/AeroSCOPE/blob/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/03_routes_schedule/02_routes_estimation.ipynb) is used to test several estimation technique and finally estimates the traffic using XGBoost regressor.
- [03_routes_product.ipynb](https://github.com/AeroMAPS/AeroSCOPE/blob/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/03_routes_schedule/03_routes_product.ipynb) is the 'production' dataset creation notebook. It is similar in many ways to the first notebook of the folder but follows a different aggregation logic (not built on wikipedia database anymore). Airport passenger traffic information is used to scaele estimated routes to minimize airport-level error.
- [04_final_testing.ipynb](https://github.com/AeroMAPS/AeroSCOPE/blob/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/03_routes_schedule/04_final_testing.ipynb) is used to perform tests at different levels (airport, route, country, flows), using various comparison sources detailled in the notebook.

The fourth folder ([04_app](https://github.com/AeroMAPS/AeroSCOPE/tree/12249404672c03aca98608c6e85cdd7e82fa59ea/TrafficEstimator/04_app)) contains the app notebook, that **is designed to run with *voila*, not as a standard notebook**. Several .py files used for plots. The preprocess.py file should be run if the source file is modified to adequately modify the processd data storage file , used for a faster *voila* execution.
  
## Authors

Antoine Salgas <br>
Contact: [antoine.salgas@isae-supaero.fr]

## License

TODO
