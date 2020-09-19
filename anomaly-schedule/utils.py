import os
import time
import logging
from typing import List
import sys

def get_now(format: str='%Y-%m-%d-%H.%M.%S') -> str:
    """
    获得当前的时间
    
    Returns
    -------
    str: 当前时间的format格式
    """    
    return time.strftime(format, time.localtime(time.time()))


def get_log(name: str, log_name: str, format_p :str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', log_dir:str='./log'):
    """
    获得logger的对象

    Parameters
    ----------
    name : str
        logger的名称
    log_name : str
        log_file的名称，如果log_name == None， 则不会存在log file
    format_p : str, optional
        log的format格式, by default '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_dir : str, optional
        log文件的目录, by default './log'

    Returns
    -------
    [type]
        [description]
    """    
    logger = logging.getLogger(name)
    formatter = logging.Formatter(format_p)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    
    logger.addHandler(ch)
    
    if len(log_name):
        file_name = log_name + get_now() + '.log'
        
        fh = logging.FileHandler(os.path.join(log_dir, file_name))
        
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    logger.setLevel(logging.INFO)
    return logger

# def get_error_yaml(kinds: List[str], duration: int, rand_gas: int) -> str:
#     pass