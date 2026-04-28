"""
OpenAI Client for the Personal Assistant Bot.
Provides methods for text generation, vision, STT, and TTS.
"""

from typing import List, Dict, Optional
import httpx
from openai import AsyncOpenAI
from pathlib import Path
import time

from config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_PROXY_URL,
    GPT_MODEL,
    WHISPER_MODEL,
    TTS_MODEL,
    VISION_MODEL,
    TEMPERATURE,
    MAX_TOKENS
)
from utils.logging import logger


class OpenAIClient:
    """Async client for OpenAI API operations."""
    
    def __init__(self):
        """Initialize the OpenAI client."""
        client_kwargs = {
            "api_key": OPENAI_API_KEY,
            "base_url": OPENAI_BASE_URL,
        }
        if OPENAI_PROXY_URL:
            client_kwargs["http_client"] = httpx.AsyncClient(proxy=OPENAI_PROXY_URL)

        self.client = AsyncOpenAI(**client_kwargs)
        
        logger.info("OpenAI client initialized with base URL: %s", OPENAI_BASE_URL)
        if OPENAI_PROXY_URL:
            logger.info("OpenAI proxy enabled")
        
        self.proxy_url = OPENAI_PROXY_URL
    
    async def generate_text_response(
        self,
        messages: List[Dict[str, str]],
        model: str = GPT_MODEL,
        temperature: float = TEMPERATURE,
        max_tokens: int = MAX_TOKENS,
        request_id: Optional[str] = None
    ) -> str:
        """
        Generate text response using GPT model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use
            temperature: Response randomness (0-2)
            max_tokens: Maximum tokens in response
        
        Returns:
            Generated text response
        """
        started = time.perf_counter()
        try:
            total_chars = sum(len(msg.get("content", "")) for msg in messages if isinstance(msg.get("content"), str))
            logger.info(
                "[req:%s] OpenAI[text]: request start model=%s messages=%s total_chars=%s temperature=%s max_tokens=%s",
                request_id or "n/a",
                model,
                len(messages),
                total_chars,
                temperature,
                max_tokens
            )
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            result = response.choices[0].message.content
            logger.info(
                "[req:%s] OpenAI[text]: response received in %sms, chars=%s",
                request_id or "n/a",
                round((time.perf_counter() - started) * 1000),
                len(result) if result else 0
            )
            return result
            
        except Exception as e:
            logger.error(
                "[req:%s] OpenAI[text]: error after %sms: %s",
                request_id or "n/a",
                round((time.perf_counter() - started) * 1000),
                e
            )
            raise
    
    async def analyze_image(
        self,
        image_url: str,
        prompt: str = "Опиши это изображение подробно. Что ты видишь?",
        model: str = VISION_MODEL
    ) -> str:
        """
        Analyze an image using GPT-4 Vision.
        
        Args:
            image_url: URL or base64 encoded image
            prompt: Analysis prompt
            model: Vision model to use
        
        Returns:
            Image analysis result
        """
        started = time.perf_counter()
        try:
            logger.info(
                "OpenAI[vision]: request start model=%s image_url_len=%s prompt_len=%s",
                model,
                len(image_url) if image_url else 0,
                len(prompt) if prompt else 0
            )
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            }
                        ]
                    }
                ],
                max_tokens=MAX_TOKENS
            )
            
            result = response.choices[0].message.content
            logger.info(
                "OpenAI[vision]: response received in %sms, chars=%s",
                round((time.perf_counter() - started) * 1000),
                len(result) if result else 0
            )
            return result
            
        except Exception as e:
            logger.error(
                "OpenAI[vision]: error after %sms: %s",
                round((time.perf_counter() - started) * 1000),
                e
            )
            raise
    
    async def transcribe_audio(
        self,
        audio_file_path: Path,
        model: str = WHISPER_MODEL
    ) -> str:
        """
        Transcribe audio file to text using Whisper.
        
        Args:
            audio_file_path: Path to audio file
            model: Whisper model to use
        
        Returns:
            Transcribed text
        """
        started = time.perf_counter()
        try:
            logger.info("OpenAI[stt]: request start model=%s file=%s", model, audio_file_path)
            
            with open(audio_file_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    response_format="text"
                )
            
            logger.info(
                "OpenAI[stt]: response received in %sms, chars=%s",
                round((time.perf_counter() - started) * 1000),
                len(response) if response else 0
            )
            return response
            
        except Exception as e:
            logger.error(
                "OpenAI[stt]: error after %sms: %s",
                round((time.perf_counter() - started) * 1000),
                e
            )
            raise
    
    async def generate_speech(
        self,
        text: str,
        voice: str = "alloy",
        model: str = TTS_MODEL,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate speech from text using TTS.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, nova, fable, onyx, shimmer)
            model: TTS model to use
            output_path: Path to save audio file
        
        Returns:
            Path to generated audio file
        """
        started = time.perf_counter()
        try:
            logger.info(
                "OpenAI[tts]: request start model=%s voice=%s text_len=%s",
                model,
                voice,
                len(text) if text else 0
            )
            
            response = await self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text
            )
            
            # Default output path
            if output_path is None:
                from config import DATA_DIR
                import uuid
                output_path = DATA_DIR / f"tts_{uuid.uuid4()}.mp3"
            
            # Save audio to file
            response.stream_to_file(str(output_path))
            
            logger.info(
                "OpenAI[tts]: response received in %sms output=%s",
                round((time.perf_counter() - started) * 1000),
                output_path
            )
            return output_path
            
        except Exception as e:
            logger.error(
                "OpenAI[tts]: error after %sms: %s",
                round((time.perf_counter() - started) * 1000),
                e
            )
            raise


# Global client instance
openai_client = OpenAIClient()

