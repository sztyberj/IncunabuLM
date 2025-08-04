# config.py

# --- App
TITLE = "IncunabuLM"
API_URL = "http://host.docker.internal:8000/generate"
CSS = "utilis/style.css"
IMAGE_PATH = 'utilis/scribe.png'

TOKENIZER_PATH = "tokenizer/bpe_tokenizer.json"
MODEL_PATH = "models/incunabulm_111m_poems_v2.pth"

# --- Training params
BATCH_SIZE = 8
BLOCK_SIZE = 2048
EVAL_INTERVAL = 250
EVAL_ITERS = 200
WEIGHT_DECAY = 0.1
CLIP_GRAD_NORM = 1.0
ACCUMULATION_STEPS = 8

# --- Learning rate scheduler
MIN_LEARNING_RATE = 3e-5
LEARNING_RATE = 3e-4
WARMUP_ITERS = 2000
MAX_ITERS = 50000

# --- Model params
N_EMBD = 768
N_HEAD = 12
N_LAYER = 12
DROPOUT = 0.2

# --- Tokenizer params
VOCAB_SIZE = 16384

