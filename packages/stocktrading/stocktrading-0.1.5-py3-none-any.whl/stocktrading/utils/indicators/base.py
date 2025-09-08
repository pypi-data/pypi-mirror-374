
"""
Author: Tran Quoc Dat <dat.tq6141@gmail.com>
Created: 07 Sep, 2025 09:41
File: base.py
"""


import mplfinance as mpf
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

from pandas import DataFrame
from datetime import datetime, timedelta
from pytz import timezone

from typing import Any
from matplotlib.transforms import blended_transform_factory

def text_color_for_background(hexcolor: str) -> str:
    # hex to RGB 0..255
    hexcolor = hexcolor.lstrip('#')
    r = int(hexcolor[0:2], 16)
    g = int(hexcolor[2:4], 16)
    b = int(hexcolor[4:6], 16)
    # tính brightness theo công thức thường dùng
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    return 'black' if brightness > 186 else 'white'


def add_label_text(
    axe: Axes,
    df: DataFrame,
    field_name: Any,
    fontsize: int,
    bg_color: Any = '#ffffff',
):
    trans = blended_transform_factory(axe.transAxes, axe.transData)
    
    last_value = float(df[field_name].values[-1])
    
    axe.text(
        1.01, 
        last_value,
        f"{last_value:.2f}",
        transform=trans,
        ha='left', va='center',
        fontsize=fontsize,
        bbox=dict(boxstyle='round,pad=0.3', fc= bg_color, ec= None, alpha=0.95),
        color= text_color_for_background(bg_color)
    )
    
    return last_value

class Chart:
    
    def __init__(
        self,
        title: str,
        pricedf: DataFrame,
        max_ticks = 180,
        base_style: str = 'starsandstripes',
    ):
        now = datetime.now()
        xlim = (now - timedelta(days= max_ticks), now + timedelta(days= 20))
        
        y_min = float(pricedf['low'].min())*0.9
        y_max = float(pricedf['high'].max())*1.25
        ylim = (y_min, y_max)
        
        self.pricedf = pricedf
        self.kwargs = dict(
            title= title,
            type= "candle",
            figsize= (14, 8),
            xrotation= 0,
            xlim= xlim,
            ylim= ylim,
            addplot= [],
            returnfig= True
        )
        
        self.style = mpf.make_mpf_style(
            base_mpf_style= base_style,
            marketcolors = mpf.make_marketcolors(up= '#00aa00', down= '#d90000'),
        )
        
        self.fig: Figure
        self.axes: Axes
        self.label_conf: dict[str[Any]] = {}

    def addplots(
        self,
        field_name: str,
        panel: int,
        type: str = 'line',
        hex_color: str = None,
        label: str = '',
    ):
        series = self.pricedf[field_name]
        plot = mpf.make_addplot(
            data = series,
            panel = panel,
            type = type,
            color = hex_color,
            ylabel = label
        )
        
        self.kwargs['addplot'].append(plot)
        
        self.label_conf[field_name] = {}
        self.label_conf[field_name]['axe'] = panel*2
        self.label_conf[field_name]['bg_color'] = hex_color
        
    def plot(self, show= True):
        self.fig, self.axes = mpf.plot(self.pricedf, **self.kwargs, style= self.style)
        
        self.label_conf['close'] = {}
        self.label_conf['close']['axe'] = 0
        self.label_conf['close']['bg_color'] = '#ffffff'        
        
        ma_colors = {}
        for field_name in self.label_conf:
            if 'vol' not in field_name.lower() :
                label_conf = self.label_conf[field_name]            
                last_value = add_label_text(
                    axe = self.axes[label_conf['axe']],
                    df = self.pricedf,
                    field_name = field_name,
                    fontsize = 8,
                    bg_color = label_conf['bg_color']
                )
                self.label_conf[field_name]['last_value'] = last_value
                
            if 'ma(' in field_name.lower():
                ma_colors[field_name] = label_conf['bg_color']
        
        # Legend
        handles_ma = []
        for w, col in ma_colors.items():
            handles_ma.append(Line2D([0], [0], color=col, lw=1.5, label= f'{w}: {self.label_conf[w]['last_value']:.2f}'))

        self.axes[0].legend(handles=handles_ma, loc='upper left', fontsize=9, frameon=True)
        
        if show:
            plt.tight_layout()
            plt.show()
