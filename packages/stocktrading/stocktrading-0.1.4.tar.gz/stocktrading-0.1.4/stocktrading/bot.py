"""
Author: Tran Quoc Dat <dat.tq6141@gmail.com>
Created: 07 Sep, 2025 19:44
File: bot.py
"""

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from io import BytesIO
from loguru import logger

import os
from dotenv import load_dotenv

load_dotenv()

try:
    from main import get_daily_chart
except Exception as e:
    import sys
    logger.info(str(e))    
    sys.exit()
    
    
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')
    
    
async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if not context.args:
        await update.message.reply_text("Usage: /stock <SYMBOL> (for example: /stock hpg)")
        return
    
    try:
        
        ticker = context.args[0].upper()
        fig = get_daily_chart(ticker= ticker)
        if fig:
            buffer = BytesIO()
            fig.savefig(buffer, format="png", bbox_inches="tight")
            buffer.seek(0)

            try:
                import matplotlib.pyplot as plt
                plt.close(fig)
            except Exception as e:
                logger.error(str(e))
            
            await update.message.reply_photo(
                photo = buffer, 
                pool_timeout= 10,
                read_timeout= 10,
                write_timeout= 10,
            )
            
            buffer.close()
        
        else:
            await update.message.reply_text(text= f'Invalid stock `{ticker}`')

    except Exception as e:
        logger.info(str(e))

def run():
    app = ApplicationBuilder().token(os.getenv('BOT_TOKEN')).build()
    app.add_handler(CommandHandler("stock", stock))
    logger.info('Bot is running...')
    app.run_polling()
    
    
if __name__ == "__main__":
    run()