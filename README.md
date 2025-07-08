# FlipTop Analysis

This project explores rap battles in the [FlipTop Battle League](https://www.fliptop.com.ph/about), modeling emcee career histories and rap battle networks.

## 📝 Plan




## 📁 Project Structure

```
fliptop-analysis/
│
├── data/                            # Sample and intermediate data
│   ├── emcees.csv                   # Emcee profiles and metadata
│   ├── README.md                    # Notes about data files
│   ├── sample.json                  # Sample video data
│   ├── sample_descriptions.json     # Text descriptions of sample videos
│   ├── secret.json                  # API credentials (ignored via .gitignore)
│   └── videos.json                  # Full scraped video metadata
│
├── notebooks/                       # Jupyter notebooks for EDA and analysis
│   └── eda.ipynb                    # Exploratory Data Analysis
│
├── scripts/                         # Python scripts for scraping/preprocessing
│   ├── __pycache__/                 # Compiled bytecode (auto-generated)
│   ├── api_scrape_channel.py       # Scrapes channel data using API
│   ├── emcee_scraper.py            # Extracts emcee names and matchups
│   └── sample_videos.py            # Loads and filters sample video data
│
├── .gitattributes                   # Git attributes (e.g. text normalization)
├── .gitignore                       # Ignore raw data, secrets, and cache files
├── environment.yml                  # Conda/Mamba environment configuration
├── LICENSE                          # Project license
└── README.md                        # Project overview and instructions (YOU'RE HERE)

```

## 🪪 License

This code is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

Please note: This project scrapes metadata from YouTube for educational purposes only. Be mindful of YouTube's [Terms of Service](https://www.youtube.com/t/terms).
