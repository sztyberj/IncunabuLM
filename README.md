# IncunabuLM 📜

![GitHub last commit](https://img.shields.io/github/last-commit/sztyberj/IncunabuLM?style=for-the-badge&color=blue)
![GitHub repo size](https://img.shields.io/github/repo-size/sztyberj/IncunabuLM?style=for-the-badge&color=green)
![GitHub stars](https://img.shields.io/github/stars/sztyberj/IncunabuLM?style=for-the-badge&color=yellow)
![GitHub forks](https://img.shields.io/github/forks/sztyberj/IncunabuLM?style=for-the-badge&color=orange)

> IncunabuLM: A small, decoder-only language model trained on Polish lectures and fine-tuned for generating poetry in the style of Old Polish. This project encapsulates the entire workflow from model training to deployment via a RESTful API and an interactive web application.

---

## 🚀 Overview

This project presents **IncunabuLM**, a bespoke language model designed with a specific artistic purpose: to generate poetry that mimics the style and vocabulary of Old Polish. The model was initially pre-trained on a corpus of Polish academic lectures to build a solid linguistic foundation and subsequently fine-tuned on historical Polish texts to master the art of poetry.

The project provides a complete ecosystem for interacting with the model, including:
* A RESTful API built with **FastAPI** to serve generation requests.
* An intuitive web interface created with **Streamlit** for easy experimentation.
* A **Docker** container for the Streamlit application, ensuring portability and simple deployment.
* Dependency management for the core project handled by **Poetry**.

---

## ✨ Features

* **Custom Language Model**: A from-scratch implementation of a decoder-only Transformer model.
* **Specialized Generation**: Fine-tuned specifically for generating Old Polish poetry.
* **RESTful API**: Exposes the model's generation capabilities through a clean `FastAPI` endpoint.
* **Interactive UI**: A `Streamlit` web application allows users to generate poems with custom prompts and parameters.
* **Containerized Web App**: The `Streamlit` interface is containerized with `Docker` for seamless deployment.
* **Modern Dependency Management**: Project dependencies are managed using `Poetry`.

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| **Language Model** | `PyTorch`, `NumPy` |
| **NLP / Tokenization** | `tokenizers` (Custom BPE) |
| **API & Web** | `FastAPI`, `Uvicorn`, `Streamlit`, `Pydantic` |
| **Deployment** | `Docker`, `Poetry` |
| **Language** | `Python` |
| **Tools** | `Git & GitHub` |

---

## 🏗️ Model Architecture

IncunabuLM is a decoder-only Transformer model with the following architecture:

| Parameter | Value | Description |
|---|---|---|
| `VOCAB_SIZE` | 16384 | The size of the vocabulary used by the tokenizer. |
| `N_EMBD` | 768 | The dimensionality of the token embeddings. |
| `N_LAYER` | 12 | The number of Transformer blocks in the model. |
| `N_HEAD` | 12 | The number of attention heads in each Transformer block. |
| `DROPOUT` | 0.2 | The dropout rate used for regularization. |
| **Total Parameters** | **~111.7M** | The total number of trainable parameters. |

<img width="559" height="1024" alt="Image" src="https://github.com/user-attachments/assets/87907aa3-fba0-46cc-b1d3-f75ade7b86e8" />

---

## 🔡 Tokenizer

The model uses a custom Byte-Pair Encoding (BPE) tokenizer built with the `tokenizers` library. Key characteristics include:

* **Model**: Byte-Pair Encoding (`BPE`) with a `[UNK]` token for unknown words.
* **Pre-tokenizer**: `ByteLevel` pre-tokenization is used to handle all possible byte sequences.
* **Vocabulary Size**: `16384` tokens.
* **Special Tokens**: The tokenizer is trained with the following special tokens: `[UNK]`, `[PAD]`, `[BOS]`, `[EOS]`, and `<|endoftext|>`.
* **Decoder**: A `ByteLevel` decoder is used to correctly reconstruct the text from tokens.

---

## 💾 Data Source

The pre-training and fine-tuning datasets were constructed using texts sourced from the [Wolne Lektury API](https://wolnelektury.pl/api). Wolne Lektury is a digital library project that provides open access to a vast collection of Polish literature, which was essential for building the model's corpus.

---

## 📸 Application Preview

### Streamlit Interface
The interactive web application where you can generate your own Old Polish poetry. The interface allows you to control the generation process through several parameters:

* **Temperature**: Adjusts the creativity of the model. Lower values produce more predictable text, while higher values generate more surprising results.
* **Top K**: Narrows the model's choices to the top K most likely tokens at each step, improving coherence.
* **Repetition Penalty (Kara za powtórzenie)**: Discourages the model from repeating the same words or phrases, leading to more varied output.
* **Text Length (Długość pisma)**: Defines the maximum length of the generated poem in tokens.

<img width="1876" height="920" alt="Image" src="https://github.com/user-attachments/assets/ae2f11d4-b783-4eb7-8715-a71f5ed7bdd5" />

### API Documentation (FastAPI)
The API is automatically documented using Swagger UI, providing a clear way to test the endpoints.

<img width="1860" height="920" alt="Image" src="https://github.com/user-attachments/assets/8cc073b9-2258-4537-883c-025f1a5e99e2" />

---

## 🏁 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

* Python 3.10+ and Poetry
* Docker

### Installation & Launch

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/sztyberj/IncunabuLM.git](https://github.com/your-username/IncunabuLM.git)
    cd IncunabuLM
    ```

2.  **Install dependencies with Poetry:**
    This will create a virtual environment and install the required packages for the model and API.
    ```sh
    poetry install
    ```

3.  **Download model from huggingface and edit model name in config.py:**
    ```sh
    https://huggingface.co/sztyberj/IncunabuLM-111M/tree/main
    ```
4.  **Run the FastAPI Server:**
    From the project root, run the following command. The API will be accessible at `http://localhost:8000`.
    ```sh
    poetry run uvicorn api.main:app --reload
    ```

5.  **Build and run the Streamlit Docker container:**
    Navigate to the `app` directory and build the Docker image. Then, run the container.
    ```sh
    docker-compose build -up
    ```

6.  **Access the applications:**
    * **FastAPI (API Docs)**: `http://localhost:8000/docs`
    * **Streamlit (Web App)**: `http://localhost:8501`

---

## 📜 Generated Example


_Bóg Już czas, że nie mógł do brzegu, Tak się prędko z nią zdarte wały.
Co na to, co tam i gdzie ludzie siedzą?
Ja też tu przy nich żyję jak trzeba, Przywionie mię mieć będę, a sam mistrzu!
Takem czasem: Pomóż o tem wiedzieć, bo ja dobrze wiem, Mistrz mój, jakom się boję nad tobą z tobą zgodzić;
ale za tem będzie lepiej, Ja chcę się baczny uciąć w te strony.” I na cóż mam powiedzieć?
A ten list to jest wasz domowy Zwyczaj sobie po głowie, Któregoż odeśleciał z nami?_

