import os
import re
import json
import base64
from datetime import datetime
from typing import Dict, Optional


class BotSaver:
    """
    Saves bot data in a folder named after the user-given bot name.
    Creates config.json with metadata and stores the uploaded PDF.
    Supports both raw bytes (best for multipart/form-data) and base64 via a helper.
    """

    def __init__(self, root_dir: str = "bots_data/pdf_bots"):
        self.root_dir = root_dir
        os.makedirs(self.root_dir, exist_ok=True)

    def save_bot(
        self,
        name: str,
        model: str,
        system_prompt: str,
        pdf_bytes: bytes,
        pdf_filename: str,
        groq_api_key : str ,
        split: Optional[bool] = True,
        initial_line: Optional[str] = ""
    ) -> Dict:
        """
        Save bot metadata and PDF in a folder named by slugified bot name.
        Returns metadata with only the folder_name for the bot.
        Use this with multipart/form-data (UploadFile -> bytes).
        """
        if not name or not name.strip():
            raise ValueError("Bot name cannot be empty.")
        if not pdf_filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are allowed (got: %s)" % pdf_filename)

        slug = self._slugify(name)
        folder_name = self._ensure_unique_dir(slug)
        bot_dir = os.path.join(self.root_dir, folder_name)
        os.makedirs(bot_dir, exist_ok=True)

        # Save PDF
        pdf_path = os.path.join(bot_dir, "document.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        # Save config metadata
        meta = {
            "folder_name": folder_name,
            "name": name.strip(),
            "model": model,
            "system_prompt": system_prompt.strip(),
            "initial_line": (initial_line or "").strip(),  # <-- NEW
            "pdf_filename": pdf_filename,
            "split": bool(split),
            "created_at": datetime.now().isoformat() ,
            "groq_api_key" : groq_api_key
        }

        config_path = os.path.join(bot_dir, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return meta

    def save_bot_from_base64(
        self,
        name: str,
        model: str,
        system_prompt: str,
        pdf_base64: str,
        pdf_filename: str,
        split: Optional[bool] = True,
        initial_line: Optional[str] = ""   # <-- NEW
    ) -> Dict:
        """
        Convenience wrapper if the PDF arrives as base64 (e.g., JSON payloads).
        Decodes and delegates to save_bot().
        """
        try:
            pdf_bytes = base64.b64decode(pdf_base64)
        except Exception as e:
            raise ValueError(f"Invalid base64 PDF data: {e}")

        return self.save_bot(
            name=name,
            model=model,
            system_prompt=system_prompt,
            pdf_bytes=pdf_bytes,
            pdf_filename=pdf_filename,
            split=split,
            initial_line=initial_line,
        )

    # ---------- helpers ----------

    @staticmethod
    def _slugify(name: str) -> str:
        """
        Convert a string to a safe slug for folder names.
        """
        s = name.strip().lower()
        s = re.sub(r"[\s_]+", "-", s)
        s = re.sub(r"[^a-z0-9\-]+", "", s)
        s = re.sub(r"-{2,}", "-", s).strip("-")
        return s or "bot"

    def _ensure_unique_dir(self, slug: str) -> str:
        """
        Ensure the folder name is unique by appending -001, -002, etc. if needed.
        """
        candidate = slug
        counter = 1
        while os.path.exists(os.path.join(self.root_dir, candidate)):
            candidate = f"{slug}-{counter:03d}"
            counter += 1
        return candidate


if __name__ == '__main__':
    print('done')