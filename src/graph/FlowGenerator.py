import random
import numpy as np
import json
from typing import List, Dict
from math import floor

from src.graph.Flow import Flow


class FlowGenerator:
    flows: List[Flow]

    def __init__(self):
        pass

    @classmethod
    def compute_hyper_period(cls, flows: List[Flow]):
        # TODO compute hyper period of flows
        # fake method here
        _F: List[Flow] = sorted(flows, key=lambda f: f.period)
        return _F[-1].period

    @staticmethod
    def smooth_period(hp: int, p: int) -> int:
        # TODO smooth period of all flows
        _n: int = floor(hp / p)
        return int(hp / _n)

    @classmethod
    def generate_r(cls, n: int = 0, hn: List[int] = 0, s: List[int] = [], p: List[int] = [], dn: List[int] = [],
                   rl: List[float] = [], dl: List[int] = []) -> List[Flow]:
        _F: List[Flow] = []
        _P: List[int] = [100000, 150000, 300000, 600000]  # TODO fake period here
        for _i in range(n):
            _fid = _i + 1
            _s: int = random.randint(s[0], s[1])
            # _p: int = random.randint(p[0], p[1])
            _p: int = _P[random.randint(0, len(_P)) - 1]  # TODO fake method here
            _dn: int = random.randint(dn[0], dn[1])
            _rl: int = random.randint(rl[0], rl[1])
            _dl: int = random.randint(dl[0], dl[1])
            _src: int = hn[random.randint(0, len(hn)) - 1]
            while True:
                _D: List[int] = random.sample(hn, _dn)
                _D = list(filter(lambda d: d != _src, set(_D)))
                if len(_D) != 0:
                    break
            _p = cls.smooth_period(p[1], _p)
            _f: Flow = Flow(_fid, _s, _p, _src, _D, _rl, _dl)
            _F.append(_f)
        return _F

    @classmethod
    def generate_s(cls):
        '''
        generate the set of flows specifically
        :return:
        '''
        pass

    @staticmethod
    def _obj2json_helper(obj):
        if type(obj).__name__ == 'set':
            return list(obj)
        else:
            return obj

    @staticmethod
    def _json2obj_helper(d):
        obj = object.__new__(Flow)  # Make instance without calling __init__
        for key, value in d.items():
            if key == 'walked_edges' or key == 'negative_walked_edges':
                value = set(value)
            setattr(obj, key, value)
        return obj

    @classmethod
    def flow2json(cls, flow: Flow):
        json.dumps(flow.__dict__, default=cls._obj2json_helper)

    @classmethod
    def flows2json(cls, flows: List[Flow]) -> str:
        _F: str = dict()
        for _i, flow in enumerate(flows):
            _F['f' + str(_i)] = json.dumps(flow.__dict__, default=cls._obj2json_helper)
        return json.dumps(_F)

    @classmethod
    def json2flows(cls, json_str) -> List[Flow]:
        _flows_str: Dict[str] = json.loads(json_str)
        _F: List[Flow] = []
        for _flow_str in _flows_str.values():
            _f: Flow = json.loads(_flow_str, object_hook=cls._json2obj_helper)
            _F.append(_f)
        return _F
