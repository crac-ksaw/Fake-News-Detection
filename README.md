# Fake News Detector 🧠

A Streamlit-powered web application designed to detect fake news using advanced natural language processing techniques. It leverages a custom-trained deep learning model (`heights.h5`) and the Groq API as an enhancement engine for sophisticated news verification.

## Features

- **User-Friendly Interface:** Clean and intuitive web UI built with Streamlit.
- **Model Integration:** Utilizes the `heights.h5` data model, expertly trained on news datasets to distinguish between genuine and fake news.
- **Groq API Enhancement:** Connects to the Groq API to improve detection accuracy and add advanced inference capabilities, offering more reliable news classification.
- **Environment Variable Support:** Leverages `.env` file for API keys and secure configuration.
- **Modern Python Stack:** Powered by `streamlit`, `requests`, and `python-dotenv`.


## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/fake-news-detector.git
cd fake-news-detector
```


### 2. Install Requirements

```bash
pip install -r requirements.txt
```


### 3. Add Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key
GROQ_API_URL=https://api.groq.com/v1/endpoint
GROQ_MODEL=your_groq_model_name
```


## Usage

Launch the Streamlit application:

```bash
streamlit run bert_app.py
```

Visit the displayed local URL to interact with the Fake News Detector.

## How It Works

1. **User Input:** Enter a piece of news or text into the web interface.
2. **Local Prediction:** The app loads and queries the `heights.h5` trained model to predict if the news is fake.
3. **Enhanced Verification:** For advanced or ambiguous entries, the text is sent to the Groq API for a second opinion leveraging Groq’s powerful AI infrastructure.
4. **Results:** The interface displays a clear verdict – real or fake – with potential confidence scores or insightful feedback.

## Project Structure

| File | Description |
| :-- | :-- |
| `bert_app.py` | Main Streamlit application code. |
| `requirements.txt` | Python dependencies. |
| `.env` | Environment variables (not included). |
| `heights.h5` | Trained deep learning data model (see notes). |

## Limitations

- **Not Updated to Latest News:** The underlying `heights.h5` model and the system’s predictions are based on news data available at the time of training. As a result, events and content from after the latest training set are not considered, limiting the tool's ability to verify or analyze emerging news topics.
- **Model Generalization:** Predictions may not reflect context changes or new forms of misinformation that have emerged since the latest training.
- **Dependence on Groq API:** Advanced detection features require internet connectivity and valid API credentials.
- **No Real-Time Fact-Checking:** The system does not perform live cross-referencing with ongoing news sources or databases.
- **Potential for False Positives/Negatives:** As with any automated model, errors in classification can occur, especially with nuanced or ambiguous news content.


## Notes

- **Model File:** Ensure you have `heights.h5` in the project directory for the app to function.
- **API Key:** Sign up at Groq and obtain API credentials for enhanced analysis.
- **Security:** Never commit your `.env` file or API keys to public repositories.


## License

This project is for educational and research purposes. Please check individual files for their respective licenses if using or modifying them.

## Acknowledgements

- Streamlit team for an exceptional open-source web app framework.
- The creators of Groq for enabling advanced NLP capabilities via API.
- Open-source contributors to Python NLP toolkits.

Feel free to submit issues or requests for additional features!
