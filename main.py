from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from typing import Optional
from core import * 
from typing import List
from pydantic import BaseModel, Field
import json

app = FastAPI()

_process = ProcessApi()
llm = None


def load_json(path: str) -> dict:
    """
    Load a JSON file and return it as a Python dictionary.
    
    Args:
        path (str): Path to the JSON file.
    
    Returns:
        dict: Parsed JSON data as a Python dictionary.
    """
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


class ConversationData(BaseModel):
    folder_name: str = Field(..., description="The slug or unique name of the bot folder")
    user_text: str = Field(..., description="The text content to process or send")
    last_3_conversations: List[str] = Field(
        ..., description="List containing the last three conversation messages"
    )

class StartLine(BaseModel):
    folder_name: str = Field(..., description="The slug or unique name of the bot folder")

@app.get("/")
def index():
    return {"message": "Hare Krishna"}

@app.get("/model_list")
def index():
    res = ["openai/gpt-oss-20b" , "deepseek-r1-distill-llama-70b" ,
            "gemma2-9b-it" , "llama-3.3-70b-versatile" , "openai/gpt-oss-120b" ,"meta-llama/llama-4-maverick-17b-128e-instruct"]
    return {"models": res}

@app.post("/get_first_line")
def start(payload:StartLine):
    try:
        global llm
        folder_name = payload.folder_name
        config_path = os.path.join("bots_data", "pdf_bots", folder_name, "config.json")
        config_data = load_json(config_path)
        start_line = config_data.get('initial_line')
        api = config_data.get('groq_api_key')
        llm  = GroqAIProcessor(api)

        return {"initial_line": start_line}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bot: {e}")

@app.post("/create_bot")
async def create_bot(
    name: str = Form(..., description="Bot name"),
    model: str = Form(..., description="LLM model id"),
    groq_api_key: str = Form(..., description="groq api key"),
    system_prompt: str = Form(..., description="System prompt for the bot"),
    initial_line: Optional[str] = Form("", description="Initial greeting line"),
    pdf: UploadFile = File(..., description="PDF file to upload"),
):
    try:
        if not pdf.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        pdf_bytes = await pdf.read()

        result = _process.create_bot(
            name=name,
            model=model,
            system_prompt=system_prompt,
            initial_line=initial_line,
            pdf_filename=pdf.filename,
            pdf_bytes=pdf_bytes,   
            split=True,
            groq_api_key = groq_api_key
        )

        return {
            "folder_name": result["folder_name"],
            "index_dir": result["index_dir"],
            "message": "Bot created and embeddings built successfully."
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bot: {e}")


@app.post("/talk_to_bot")
async def talk_bot(payload : ConversationData):
    try:
        global load_json , llm
        folder_name = payload.folder_name
        user_text = payload.user_text
        last_conversation = payload.last_3_conversations
        config_path = os.path.join("bots_data", "pdf_bots", folder_name, "config.json")
        index_dir = os.path.join("vector_store", folder_name)

        context = _process._create_index.get_top_k_results(index_dir , user_text , 5)

        config_data = load_json(config_path)
        prompt = config_data.get('system_prompt')
        model = config_data.get('model')
        print('#'*10)
        context
        ## pass context , question  , model and system prompt to llm 
        response = llm.run_completion(user_text , context , last_conversation , prompt , model)
        print('#'*10)
        print(response)
        return  {"answer" : response}
    
    except Exception as e:
        return {"error": f"Internal error: {e}"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", port=5000, reload=True)
