## Setup Environment - Anaconda

    conda create --name ds-project python=3.9
    conda activate ds-project
    pip install -r requirements.txt

## Setup Environment - Shell/Terminal

    mkdir data_analysis_project
    cd data_analysis_project
    pipenv install
    pipenv shell
    pip install -r requirements.txt

## Run Streamlit App

    streamlit run dashboard.py
