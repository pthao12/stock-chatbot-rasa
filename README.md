# QiBot Rasa

A Rasa-based stock chatbot providing convenient access to financial information, stock price queries, market data lookup, and transaction history tracking.

## System Requirements

- Python = 3.10

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/pthao12/stock-chatbot-rasa
cd stock-chatbot-rasa
```

### 2. Create and Activate a Virtual Environment

Create a virtual environment:

```bash
python -m venv venv
```

On macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install the Custom Vietnamese Tokenizer

The project uses a custom `VietnameseTokenizer` registered under:

```text
rasa.nlu.tokenizers.vi_tokenizer.VietnameseTokenizer
```

Copy vi_tokenizer.py into the tokenizers directory of the installed Rasa package.

**On Windows:**

```text
venv\Lib\site-packages\rasa\nlu\tokenizers\vi_tokenizer.py
```

**On macOS/Linux:**

```text
venv/lib/python3.10/site-packages/rasa/nlu/tokenizers/vi_tokenizer.py
```

Make sure that the file is located at the correct path before training the model.

## Train the Rasa Model

Run the following command from the `rasa` directory:

```bash
rasa train
```

If the training process completes successfully, a `.tar.gz` model file will be generated in the `models/` directory.

## Run the Rasa Server

Start the Rasa server with API and CORS support:

```bash
rasa run --enable-api --cors "*"
```

If the server starts successfully, the following message will be displayed:

```text
Rasa server is up and running
```

## Run the Action Server

Open a separate terminal, activate the virtual environment, and run:

```bash
rasa run actions
```

If the action server starts successfully, the following message will be displayed:

```text
Starting action endpoint server
```
