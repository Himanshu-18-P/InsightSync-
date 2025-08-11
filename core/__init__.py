import os
import base64
from typing import Dict, Optional

from core.process_data.savedata import BotSaver  
from core.process_data.vectordb import PDFIndexer 
from core.oai.answer import *

BOT_ROOT = "bots_data/pdf_bots" 
VECTOR_ROOT = "vector_store"      

class ProcessApi:
    def __init__(self, bot_root: str = BOT_ROOT, vector_root: str = VECTOR_ROOT):
        self.bot_root = bot_root
        self.vector_root = vector_root
        os.makedirs(self.bot_root, exist_ok=True)
        os.makedirs(self.vector_root, exist_ok=True)

        self._save_config = BotSaver(root_dir=self.bot_root)
        self._create_index = PDFIndexer()

    def create_bot(
        self,
        *,
        name: str,
        model: str,
        system_prompt: str,
        pdf_filename: str,
        initial_line: str = "",         
        split: bool = True,
        pdf_base64: Optional[str] = None,  
        pdf_bytes: Optional[bytes] = None,
        groq_api_key:str
    ) -> Dict:
        """
        1) Get PDF bytes (from base64 or bytes)
        2) Save bot (BotSaver) -> returns folder_name in meta
        3) Build FAISS + BM25 under vector_store/<folder_name> (PDFIndexer)
        4) Return identifiers/paths for next steps
        """
        # ---- 1) Resolve PDF bytes ----
        if pdf_bytes is None:
            if not pdf_base64:
                raise ValueError("Provide either pdf_bytes or pdf_base64.")
            try:
                pdf_bytes = base64.b64decode(pdf_base64)
            except Exception as e:
                raise ValueError(f"Invalid base64 PDF: {e}")

        # ---- 2) Save bot ----
        meta = self._save_config.save_bot(
            name=name,
            model=model,
            system_prompt=system_prompt,
            pdf_bytes=pdf_bytes,
            pdf_filename=pdf_filename,
            groq_api_key = groq_api_key,
            split=split,
            initial_line=initial_line
        )
        folder_name = meta["folder_name"]  


        pdf_path = os.path.join(self.bot_root, folder_name, "document.pdf")
        index_dir = os.path.join(self.vector_root, folder_name)  

        self._create_index.set_path(pdf_path=pdf_path, index_dir=index_dir)
        self._create_index.build_and_save_indexes(split=split)

        
        return {
            "folder_name": folder_name,
            "index_dir": index_dir,
        }


if __name__ == '__main__':
    print('done')