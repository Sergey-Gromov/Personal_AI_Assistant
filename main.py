"""
Main Entry Point.
Starts the Telegram bot using pyTelegramBotAPI.
"""

import asyncio

from bot import bot
from utils.logging import logger


async def setup_bot():
    """Setup bot with handlers and initialize RAG if needed."""
    logger.info("Bot starting up...")
    
    # Import handlers (they will register themselves via decorators)
    try:
        from handlers import start, text, voice, image, document_upload
        logger.info("Handlers imported successfully")
    except Exception as e:
        logger.error(f"Error importing handlers: {e}", exc_info=True)
        raise
    
    # Initialize RAG index if documents exist
    try:
        from rag.index import vector_index
        from config import DOCUMENTS_DIR
        
        # Check if documents directory has supported files
        supported_extensions = {'.pdf', '.txt', '.md'}
        docs = [
            d for d in DOCUMENTS_DIR.rglob('*')
            if d.is_file() and d.suffix.lower() in supported_extensions
        ]
        
        if docs:
            # Reindex only when the persisted Chroma index does not match the files on disk.
            stats = vector_index.get_stats()
            indexed_chunks = stats.get("total_documents", 0) if isinstance(stats, dict) else 0
            indexed_sources = set(stats.get("indexed_sources", [])) if isinstance(stats, dict) else set()
            document_sources = {doc.name for doc in docs}
            
            if (
                isinstance(indexed_chunks, int)
                and indexed_chunks > 0
                and indexed_sources == document_sources
            ):
                logger.info(
                    f"Found {len(docs)} documents, existing index has {indexed_chunks} chunks. "
                    "Index sources match documents, skipping startup reindex."
                )
            else:
                missing_sources = sorted(document_sources - indexed_sources)
                stale_sources = sorted(indexed_sources - document_sources)
                if missing_sources:
                    logger.info("Documents missing from index: %s", ", ".join(missing_sources))
                if stale_sources:
                    logger.info("Stale index sources not found on disk: %s", ", ".join(stale_sources))

                logger.info(f"Found {len(docs)} documents, rebuilding RAG index...")
                count = vector_index.index_documents_directory(force_reindex=True)
                logger.info(f"Indexed {count} document chunks")
        else:
            logger.info("No documents found in data/documents/")
    
    except Exception as e:
        logger.warning(f"Could not initialize RAG index: {e}")
    
    try:
        # Network hiccups should not block bot startup completely.
        bot_info = await asyncio.wait_for(bot.get_me(), timeout=15)
        logger.info(f"Bot started: @{bot_info.username}")
    except asyncio.TimeoutError:
        logger.warning("Could not get bot info (timeout), continuing startup")
    except Exception as e:
        logger.warning(f"Could not get bot info: {e}")


async def shutdown_bot():
    """Actions to perform on bot shutdown."""
    logger.info("Bot shutting down...")
    try:
        await bot.close_session()
    except:
        pass
    logger.info("Bot shutdown complete")


async def main():
    """Main function to run the bot."""
    reconnect_delay = 5
    max_reconnect_delay = 60
    reconnect_attempt = 0

    try:
        # Setup bot
        await setup_bot()

        # Keep polling alive across transient Telegram network failures
        while True:
            reconnect_attempt += 1
            try:
                if reconnect_attempt == 1:
                    logger.info("Starting bot polling...")
                else:
                    logger.warning(
                        f"Reconnecting to Telegram polling (attempt #{reconnect_attempt}, "
                        f"delay={reconnect_delay}s)..."
                    )

                await bot.infinity_polling(
                    timeout=10,
                    skip_pending=True
                )
                logger.warning("Polling stopped unexpectedly, restarting...")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.warning(
                    f"Polling error: {e}. Reconnecting in {reconnect_delay} seconds..."
                )

            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    finally:
        await shutdown_bot()


if __name__ == "__main__":
    try:
        logger.info("="*60)
        logger.info("Personal Assistant Bot - Starting")
        logger.info("="*60)
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
