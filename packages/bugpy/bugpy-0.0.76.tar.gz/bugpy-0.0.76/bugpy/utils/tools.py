import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import os
import keyring
import platform

if platform.system() == 'Linux' and os.environ.get("DISPLAY") is None:
    from keyrings.alt.file import PlaintextKeyring
    keyring.set_keyring(PlaintextKeyring())

def ossafe_join(stringlist):
    leading = stringlist[0][0] in ['/','\\']
    stringlist = [s.strip('/').strip('\\') for s in stringlist]
    if leading:
        stringlist[0] = '/'+stringlist[0]
    return '/'.join(stringlist)

def get_credentials(credential_type,credential_value):
    """ Retrieves a credential from local credential manager """
    return keyring.get_password(credential_type, credential_value)


def convert_json(val):
    """ Converts a json column into a database-palatable json column """
    if type(val) == str:
        mdict = json.loads(val)
    else:
        mdict = val
    output = json.dumps(mdict)
    return output


def _multithread_func(inputs, func, max_workers, raise_errors, description=None):
    """ Passes a list of inputs to a function

        :param inputs: list of input values to function
        :param func: prepared function
        :param description: description of process (for printing purposes), defaults to None
        :return: list of inputs causing function failures
    """
    failures = []
    outputs = []

    with tqdm(desc=description, total=len(inputs)) as pbar:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(func, i): i for i in inputs
            }
            for future in as_completed(futures):
                if future.exception():
                    if type(future.exception()) != UserWarning and raise_errors:
                        raise future.exception()
                    failures.append(futures[future])
                elif future.result() is not None:
                    outputs.append(future.result())
                pbar.update(1)

    return failures, outputs


def multithread(inputs, func, description=None, retry=True, max_workers=None, raise_errors=False):
    """ Passes a list of inputs to a function

        :param inputs: list of input values to function
        :param func: prepared function
        :param description: description of process (for printing purposes), defaults to None
        :param retry: flag to attempt single retry per input in case of failures
        :param max_workers: maximum number of threads, if <0 uses number of cpu cores, if None uses number of cpu cores
        + 4, defaults to None
        :return: list of inputs causing function failures, list of successful uploads
    """

    if max_workers is None or max_workers < 0:
        max_workers = os.cpu_count()

    failures, outputs = _multithread_func(inputs, func, max_workers, raise_errors, description)

    if len(failures) > 0 and retry:
        failures, outputs_retry = _multithread_func(failures, func, max_workers, raise_errors, description)

        outputs = outputs + outputs_retry

    return failures, outputs


def _multiprocess_func(inputs, func, max_workers, raise_errors, description=None):
    """ Passes a list of inputs to a function

        :param inputs: list of input values to function
        :param func: prepared function
        :param description: description of process (for printing purposes), defaults to None
        :return: list of inputs causing function failures
    """
    failures = []
    outputs = []

    with tqdm(desc=description, total=len(inputs)) as pbar:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(func, i): i for i in inputs
            }
            for future in as_completed(futures):
                if future.exception():
                    if type(future.exception()) != UserWarning and raise_errors:
                        raise future.exception()
                    failures.append(futures[future])
                elif future.result() is not None:
                    outputs.append(future.result())
                pbar.update(1)

    return failures, outputs


def multiprocess(inputs, func, description=None, retry=True, max_workers=None, raise_errors=False):
    """ Passes a list of inputs to a function

        :param inputs: list of input values to function
        :param func: prepared function
        :param description: description of process (for printing purposes), defaults to None
        :param retry: flag to attempt single retry per input in case of failures
        :param max_workers: maximum number of threads, if <0 uses number of cpu cores, if None uses number of cpu cores
        + 4, defaults to None
        :return: list of inputs causing function failures
    """

    if max_workers is None or max_workers < 0:
        max_workers = os.cpu_count()

    failures, outputs = _multiprocess_func(inputs, func, max_workers, raise_errors, description)

    if len(failures) > 0 and retry:
        failures, outputs_retry = _multiprocess_func(failures, func, max_workers, raise_errors, description)

        outputs = outputs + outputs_retry

    return failures, outputs


def add_directory_to_fileseries(directory, filename_series):
    """ Adds a directory to the front of a series

        :param directory: directory string
        :param filename_series: pandas series of filenames to be prefixed
        :return: pandas series of directory + filenames
    """

    filename_series = filename_series.astype(str)
    output_series = filename_series.apply(lambda col: os.path.join(directory, col))

    return output_series