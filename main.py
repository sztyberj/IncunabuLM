from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import config
import torch
from tokenizers import Tokenizer
from src.model import TransformerDecoder
import logging
import uvicorn
import sys

DEVICE = torch.device('cuda' if torch.cuda.is_available() else torch.float16)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("IncunabuLM")

class ModelInput(BaseModel):
    context: str = Field(..., min_length=1, description="Tekst wejściowy dla modelu językowego.")
    max_tokens: int = Field(default=150, gt=0, le=1024, description="Maksymalna liczba tokenów do wygenerowania.")
    temperature: float = Field(default=1.0, gt=0.0, le=2.0)
    top_k: int = Field(default=50, gt=0)
    repetition_penalty: float = Field(default=1.0, gt=0.0)

class ModelOutput(BaseModel):
    response: str

def load_model_components():
    try:
        logger.info("Loading tokenizer...")
        tokenizer = Tokenizer.from_file(config.TOKENIZER_PATH)
        
        logger.info("Initializing model...")
        model = TransformerDecoder(
            config.VOCAB_SIZE, 
            config.N_EMBD, 
            config.BLOCK_SIZE, 
            config.N_HEAD, 
            config.N_LAYER, 
            config.DROPOUT
        )
        
        logger.info("Loading model weights...")
        model.load_state_dict(torch.load(config.MODEL_PATH, map_location=DEVICE, weights_only=True))
        model.to(DEVICE)
        model.eval()
        
        total_params = sum(p.numel() for p in model.parameters())
        logger.info(f"Model {config.MODEL_PATH.split('/')[-1]} loaded successfully.  Parameters: {total_params:,}")
        
        return tokenizer, model, total_params
        
    except Exception as e:
        logger.error(f"Failed to load model components: {e}")
        raise RuntimeError(f"Model initialization failed: {e}")

tokenizer, model, total_params = load_model_components()

app = FastAPI(title=getattr(config, 'title', 'IncunabuLM API'))

@app.post("/generate", response_model=ModelOutput)
async def generate_text(data: ModelInput):
    try:
        bos_token_id = tokenizer.token_to_id('[BOS]')
        if bos_token_id is None:
            raise ValueError("BOS token not found in tokenizer vocabulary")
            
        prompt_ids = tokenizer.encode(data.context).ids
        context = torch.tensor([[bos_token_id] + prompt_ids], dtype=torch.long, device=DEVICE)

        with torch.no_grad():
            generated_ids = model.generate(
                context, 
                max_new_tokens=data.max_tokens,
                temperature=data.temperature,
                top_k=data.top_k,
                repetition_penalty=data.repetition_penalty
            )
        
        decoded_text = tokenizer.decode(generated_ids[0].tolist())
        
        punctuation_marks = ['.', '?', '!']
        last_punc_indices = [decoded_text.rfind(p) for p in punctuation_marks]
        last_punc_idx = max(idx for idx in last_punc_indices if idx != -1) if any(idx != -1 for idx in last_punc_indices) else -1
        
        if last_punc_idx != -1 and last_punc_idx >= len(data.context):
            output = decoded_text[:last_punc_idx + 1]
        else:
            output = decoded_text

        return ModelOutput(response=output)
        
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

@app.get("/")
def root():
    return {
        "service": "IncunabuLM API",
        "status": "running",
        "model_name": f"{config.MODEL_PATH.split('/')[-1]}",
        "model_parameters": f"{total_params:,}",
        "endpoints": {
            "generate": "/generate",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": True}

if __name__ == "__main__":
    logger.info("Starting FastAPI server at http://0.0.0.0:8000")
    uvicorn.run(app, host='0.0.0.0', port='8000')