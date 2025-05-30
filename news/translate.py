# ruff: noqa: S314, E501, UP031
import json
from pathlib import Path

import requests

base_language = "it"
SEPARATOR = "|||SEPARATOR|||"


def secret(path):
    if secret.cached.get(path, "") == "":
        with Path(path).open() as secret_file:
            encoded_secret = secret_file.read()
        secret.cached[path] = encoded_secret.strip()  # Ensure no leading/trailing whitespace
    return secret.cached[path]


secret.cached = {}


class TranslationError(Exception):
    """Custom exception for translation errors."""


def translate(from_lang_code, title, content):
    api_key = secret("secrets/key")
    url = f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to={base_language}&from={from_lang_code}"

    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/json",
    }

    combined_text = f"{title}{SEPARATOR}{content}"
    body = [{"Text": combined_text}]

    translation_data = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=30,
    )

    if translation_data.status_code == 200:  # noqa: PLR2004
        try:
            response_json = translation_data.json()
            if not response_json or "translations" not in response_json[0]:
                raise TranslationError("Invalid response format from translation API.")

            translated_text_combined = response_json[0]["translations"][0]["text"]
            
            if SEPARATOR not in translated_text_combined:
                # Handle cases where separator might be missing or altered by translation
                # For now, we'll assume title is short and content is the rest
                # This might need more robust handling depending on typical title/content lengths
                # or if the separator itself can be part of the translatable text.
                # A simple heuristic: if there's a period, split there, else assign all to content.
                # This is a fallback and might not be perfect.
                parts = translated_text_combined.split('.', 1)
                if len(parts) > 1:
                    title_translated = parts[0] + '.'
                    content_translated = parts[1].strip()
                else: # No period, or separator issue, assign all to content, title becomes empty or a fixed string
                    title_translated = "" # Or some default, or log a warning
                    content_translated = translated_text_combined
            else:
                title_translated, content_translated = translated_text_combined.split(SEPARATOR, 1)

        except (json.JSONDecodeError, IndexError, KeyError) as e:
            message = f"Error parsing translation response: {e}, Response: {translation_data.text}"
            raise TranslationError(message)
    else:
        message = f"Error ! status code = {translation_data.status_code}, status message = {translation_data.text}"
        raise TranslationError(message)

    return (title_translated, content_translated)
