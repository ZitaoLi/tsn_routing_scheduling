from typing import List, Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import random


class GanttBlock:
    begin: int
    end: int
    caption: str
    color: str

    def __init__(self, begin, end, caption, color='#000000'):
        self.begin = begin
        self.end = end
        self.caption = caption
        self.color = color


class GanttEntry:
    y_tick: int
    y_tick_label: str
    high: int
    blocks: List[GanttBlock]

    def __init__(self, y_tick, y_tick_label, high, blocks):
        self.y_tick = y_tick
        self.y_tick_label = y_tick_label
        self.high = high
        self.blocks = blocks


class Visualizer:
    def __init__(self):
        self.ax = plt.gca()
        [self.ax.spines[i].set_visible(False) for i in ["top", "right"]]

    @staticmethod
    def random_color() -> str:
        color_arr: List[str] = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        color: str = ""
        for i in range(6):
            color += color_arr[random.randint(0, 14)]
        return "#" + color

    @classmethod
    def gatt(cls, m, t):
        for j in range(len(m)):  # 工序j
            i = m[j] - 1  # 机器编号i
            if j == 0:
                plt.barh(i, t[j])
                plt.text(np.sum(t[:j + 1]) / 8, i, 'J%s\nT%s' % ((j + 1), t[j]), color="white", size=8)
            else:
                plt.barh(i, t[j], left=(np.sum(t[:j])))
                plt.text(np.sum(t[:j]) + t[j] / 8, i, 'J%s\nT%s' % ((j + 1), t[j]), color="white", size=8)

    @classmethod
    def draw_gantt(cls, xlim: List[int], ylim: List[int], gantt_entries: List[GanttEntry]):
        plt.rcParams['savefig.dpi'] = 300  # 图片像素
        plt.rcParams['figure.dpi'] = 300  # 分辨率
        plt.rcParams.update({'font.size': 5})  # set font size
        # plt.xticks(np.arange(xlim[0], xlim[1], 2048))

        # Declaring a figure "gnt"
        fig, gnt = plt.subplots()

        # Setting Y-axis limits
        gnt.set_ylim(ylim[0], ylim[1])

        # Setting X-axis limits
        gnt.set_xlim(xlim[0], xlim[1])

        # Setting labels for x-axis and y-axis
        gnt.set_xlabel('seconds since start')
        gnt.set_ylabel('Processor')

        _yticks: List[int] = []
        _yticklabels: List[str] = []
        for _ge in gantt_entries:
            # set y-tick and y-label
            _yticks.append(_ge.y_tick)
            _yticklabels.append(_ge.y_tick_label)
            # create blocks
            _gbs: List[GanttBlock] = _ge.blocks
            _interval: List[Tuple[int]] = []
            for _i, _gb in enumerate(_gbs):
                _t: Tuple = (_gb.begin, _gb.end)
                _interval.append(_t)
                gnt.text(_gb.begin, _ge.y_tick, _gb.caption)
                gnt.broken_barh([_interval[_i]], (_ge.y_tick, _ge.high), facecolor=_gb.color)  # TODO facecolors
        gnt.set_yticks(_yticks)
        gnt.set_yticklabels(_yticklabels)

        # Setting graph attribute
        gnt.grid(b=True, which='major', color='#666666', linestyle='-')
        # gnt.minorticks_on()
        # gnt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

        # show gantt chart
        plt.show()

    @classmethod
    def test(cls):
        m = np.random.randint(1, 7, 10)
        t = np.random.randint(15, 25, 10)
        cls.gatt(m, t)
        plt.yticks(np.arange(max(m)), np.arange(1, max(m) + 1))
        plt.show()

    @classmethod
    def test_2(cls):
        # Declaring a figure "gnt"
        fig, gnt = plt.subplots()

        # Setting Y-axis limits
        gnt.set_ylim(0, 50)

        # Setting X-axis limits
        gnt.set_xlim(0, 160)

        # Setting labels for x-axis and y-axis
        gnt.set_xlabel('seconds since start')
        gnt.set_ylabel('Processor')

        # Setting ticks on y-axis
        gnt.set_yticks([15, 25, 35])
        # Labelling tickes of y-axis
        gnt.set_yticklabels(['1', '2', '3'])

        # Setting graph attribute
        gnt.grid(b=True, which='major')
        plt.minorticks_on()
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

        # Declaring a bar in schedule
        gnt.broken_barh([(40, 50), (45, 55)], (30, 5), facecolors=('tab:orange'))
        gnt.broken_barh([(20, 10)], (30, 5), facecolors=('tab:green'))
        gnt.text(40, 30, 'hello world')

        # Declaring multiple bars in at same level and same width
        gnt.broken_barh([(110, 10), (150, 10)], (10, 5), facecolors='tab:blue')
        gnt.text(110, 10, 'hello world')
        gnt.text(150, 10, 'hello world')

        gnt.broken_barh([(0, 40), (100, 20), (130, 40)], (20, 5), facecolors=('tab:red'))

        # show gantt chart
        plt.show()
