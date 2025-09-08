"""
Author: Tran Quoc Dat <dat.tq6141@gmail.com>
Created: 02 Sep, 2025 21:54
File: main.py
"""

import numpy as np
import talib, os

from dotenv import load_dotenv

from loguru import logger
from pathlib import Path
from metastock2pd import *

from utils.indicators import (
    Chart,
)

load_dotenv()

valid_prj = True
for _, v in enumerate(('BOT_TOKEN', 'CHAT_ID', 'METASTOCK_DIR')):
    if not os.getenv(v):
        valid_prj = False
        logger.error(f'Please configure variable ${v}')

if not valid_prj:
    raise Exception('Please configure variables: $BOT_TOKEN, $CHAT_ID, $METASTOCK_DIR')


def _get_symbol_data(symbol: str, masterdf):
    filenames = masterdf[masterdf['symbol'].str.upper() == symbol]['filename'].values
    filename = filenames[0] if len(filenames) else None
    if filename:
        pricedf = metastock_read(filename)
        columns = ['open', 'close', 'low', 'high', 'volume']
        return pricedf.sort_index()[columns]

def get_daily_chart(ticker: str, window_size: int = 180):
    masterdf = metastock_read_master(Path(os.getenv('METASTOCK_DIR')).joinpath('Daily'))     
    pricedf = _get_symbol_data(ticker, masterdf)
    
    if pricedf is not None:
        pricedf = pricedf.tail(400)
            
        chart = Chart(
            title= ticker.upper(),
            pricedf= pricedf,
            max_ticks= window_size,
            base_style = 'starsandstripes'
        )
        
        # MAs
        ma_panel = 0        
        ma_periods = (10, 30, 50, 110, 200)
        ma_colors = {
            10: '#070706',
            30: '#1963d3',
            50: '#db0f2e',
            110: '#ff66cc',
            200: '#39C0D2',
        }
        
        for p in ma_periods:
            new_field = f'MA({p})'
            pricedf.loc[:, new_field] = talib.MA(real= pricedf['close'], timeperiod= p)
            
            chart.addplots(
                field_name= new_field,
                panel= ma_panel,
                type= 'line',
                hex_color= ma_colors[p],
            )
            
        # RSI
        rsi_pannel = 1
        rsi_period = 14
        rsi_colors = [
            '#1c3d99',
            '#991c26'
        ]
        
        pricedf.loc[:, f'RSI({rsi_period})'] = talib.RSI(real= pricedf['close'], timeperiod= 14)
        pricedf.loc[:, 'MA-RSI'] = talib.MA(real= pricedf[f'RSI({rsi_period})'], timeperiod= 14)
        
        for i, field_name in enumerate([f'RSI({rsi_period})', 'MA-RSI']):    
            chart.addplots(
                field_name= field_name,
                panel= rsi_pannel,
                type= 'line',
                hex_color= rsi_colors[i],
                label= 'RSI'
            )
            
        # Volume
        vol_pannel = 2
        vol_period = 50
        pricedf[f'Vol({vol_period})'] = talib.MA(pricedf['volume'], timeperiod= 50)
        
        vol_colors = {
            'up': '#00aa00',
            'down': '#d90000',
        }
        volume_colors = np.where(
            pricedf['close'].values >= pricedf['open'].values,
            vol_colors['up'], vol_colors['down']
        )
        
        for i, field_name  in enumerate(['volume', f'Vol({vol_period})']):
            chart.addplots(
                field_name= field_name,
                panel= vol_pannel,
                type= 'bar' if field_name == 'volume' else 'line',
                hex_color= volume_colors if field_name == 'volume' else 'r',
                label= 'Volume'
            )  
        
        chart.plot(show= False)
        return chart.fig
    


if __name__ == '__main__':
    ticker = 'MBB'
    get_daily_chart(
        ticker= ticker
    )