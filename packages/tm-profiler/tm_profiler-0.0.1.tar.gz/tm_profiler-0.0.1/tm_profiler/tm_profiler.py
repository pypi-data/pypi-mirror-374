import time
import os
import types
from enum import Enum
from functools import wraps

# NOTE: This needs to be in sync with __init__.py
__version__ = '0.0.1'


class LibConf:
    _instance = None

    __log_tile_enabled = True

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def log_time_enabled(self, enabled=True):
        self.__log_tile_enabled = enabled

    def is_enabled(self):
        return self.__log_tile_enabled


def log_time_enabled(enabled=True):
    return LibConf().log_time_enabled(enabled)


class FuncNameFormat(Enum):
    NAME = "name"
    ABS = "abs"
    REL = "rel"


class NpTimer:
    _instance = None

    __time_counters: dict[str, float] = {}
    __call_counters: dict[str, int] = {}
    __last_name: str = "none"
    __last_time: float = .0
    __last_call: int = 0

    function_name_format = FuncNameFormat.REL
    round_dec = 3

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def count(self, sec: float, func, print_inline: bool = False):
        if isinstance(func, types.FunctionType):
            func_name = func.__name__
            if self.function_name_format == FuncNameFormat.ABS:
                func_name = f"{os.path.abspath(func.__code__.co_filename)}[{func_name}]"
            elif self.function_name_format == FuncNameFormat.REL:
                func_name = f"{os.path.basename(func.__code__.co_filename)}[{func_name}]"

        elif isinstance(func, str):
            func_name = func
        else:
            func_name = "xxx"

        if func_name not in self.__time_counters:
            self.__time_counters[func_name] = 0
            self.__call_counters[func_name] = 0
        self.__time_counters[func_name] += sec
        self.__call_counters[func_name] += 1
        self.__last_name = func_name
        self.__last_time = sec
        self.__last_call = self.__call_counters[func_name]

        if print_inline:
            print(f"Function ({func_name}:{self.__last_call}) - took: {sec:.{self.round_dec}f}s")

    def print_last(self):
        print(f"Function ({self.__last_name}:{self.__last_call}) - took: {self.__last_time:.{self.round_dec}f}s")

    def _sorted_stat(self, sort_by: str = "name"):
        stat = [(k, self.__call_counters[k], v, v / self.__call_counters[k]) for k, v in self.__time_counters.items()]
        if sort_by == "name":
            return sorted(stat, key=lambda item: item[0])
        if sort_by == "calls":
            return sorted(stat, key=lambda item: item[1])
        if sort_by == "total":
            return sorted(stat, key=lambda item: item[2])
        if sort_by == "avg":
            return sorted(stat, key=lambda item: item[3])
        else:
            return sorted(stat, key=lambda item: item[0])

    def print_table(self, sort_by: str = "name"):
        headers = [("Name", "Time total(s)", "Calls", "Time average(s)")]
        calls_list = headers + [(n, f"{t:.{self.round_dec}f}", str(c), f"{a:.{self.round_dec}f}") for n, c, t, a in self._sorted_stat(sort_by)]

        c_lens = [0, 0, 0, 0]
        for x in calls_list:
            for i, y in enumerate(x):
                c_lens[i] = max(len(y), c_lens[i])

        ret = []
        sp = ""
        for i, c in enumerate(calls_list):
            if i == 0:
                h_str = f"| {c[0]:<{c_lens[0]}} | {c[1]:<{c_lens[1]}} | {c[2]:<{c_lens[2]}} | {c[3]:<{c_lens[3]}} |"
                sp = "-" * len(h_str)
                ret.append("_" * len(h_str))
                ret.append(h_str)
                ret.append(sp)
                continue
            ret.append(f"| {c[0]:<{c_lens[0]}} | {c[1]:>{c_lens[1]}} | {c[2]:>{c_lens[2]}} | {c[3]:>{c_lens[3]}} |")
        ret.append(sp)

        return "\n".join(ret)

    def __repr__(self):
        return self.print_table()


def set_output_dec(dec: int):
    NpTimer().round_dec = dec


def set_output_name_format(onf: FuncNameFormat):
    NpTimer().function_name_format = onf


def print_stat():
    print(NpTimer())


def print_table(sort_by: str = "name"):
    print(NpTimer().print_table(sort_by))


def print_last():
    print(NpTimer().print_last())


# Decorators
def profile(print_inline=False):
    def decorator(func):
        if LibConf().is_enabled():
            @wraps(func)
            def wrapper(*args, **kwargs):
                s_time = time.time()
                # Call wrapped function
                res = func(*args, **kwargs)

                e_time = time.time()
                NpTimer().count(e_time - s_time, func, print_inline)
                return res
        else:
            return func

        return wrapper

    return decorator
