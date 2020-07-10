# -*- coding: utf-8 -*-
import concurrent.futures
import functools
import logging
import os
import multiprocessing as mp
import time

import numpy as np
import matplotlib.pyplot as plt

import settings

try:
    import colorlog
except ImportError:
    colorlog = None

logger = logging.getLogger(__file__)


def plot_image(image, factor=1):
    """
    Utility function for plotting RGB images.
    """
    # fig = plt.subplots(nrows=1, ncols=1, figsize=(15, 7))

    if np.issubdtype(image.dtype, np.floating):
        plt.imshow(np.minimum(image * factor, 1))
    else:
        plt.imshow(image)


def init_logger(logger, log_file=None,):
    if log_file:
        log_file_dir_name = os.path.dirname(log_file)
        if not os.path.exists(log_file_dir_name):
            os.makedirs(log_file_dir_name)
        lo_to_file_handler = logging.FileHandler(log_file)
        # logging.basicConfig(filename=log_file)
    else:
        lo_to_file_handler = None

    level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
    logger.setLevel(level)
    log_str_color_format = (
        '%(log_color)s[%(asctime)s] %(name)s '
        '%(lineno)d %(levelname)s--> %(message)s'
    )

    log_str_format = (
        '[%(asctime)s] %(name)s '
        '%(lineno)d %(levelname)s--> %(message)s'
    )
    if colorlog:
        formatter = colorlog.ColoredFormatter(log_str_color_format)
    else:
        formatter = logging.Formatter(
            log_str_format,
            # datefmt='%Y-%m-%d %H:%M:%S'
        )

    if lo_to_file_handler:
        lo_to_file_handler.setLevel(logging.INFO)
        lo_to_file_handler.setFormatter(formatter)
        logger.addHandler(lo_to_file_handler)
    else:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)


def init_mp_pool():
    num_procs = mp.cpu_count()
    if num_procs > 6:
        num_procs = num_procs - 2
    else:
        num_procs = 1

    print(f"Starting multiprocessing.Pool({num_procs})")
    return mp.Pool(num_procs)


def init_thread_pool_executor():
    return concurrent.futures.ThreadPoolExecutor(max_workers=6)


def timeit(func):
    """Simple decorator to measure wall-clock time of a function."""
    @functools.wraps(func)
    def timed(*args, **kwargs):
        tstart = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            duration_ms = (time.time() - tstart) * 1000
            print(f"{func.__name__} {duration_ms:2.2f} ms")

    return timed