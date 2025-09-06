from bugpy.data import upload_filelist
from bugpy.utils import get_credentials, multiprocess, multithread
import pandas as pd
import shutil
import bugpy
import os
import re
from tqdm import tqdm

def filesize(filepath):
    bytes = os.path.getsize(filepath)
    return bytes / (1024 * 1024)

def format_for_s3(row, filetype):
    if filetype not in ['audio','img']:
        raise Exception('filetype must be one of: audio, img')
    if 'processeddata' in row[f'{filetype}_filepath']:
        return row[f'{filetype}_filepath']
    output = row[f'{filetype}_filepath'].replace('temp/Snippets', '')
    if filetype =='audio':
        output = re.sub(r'(?<!\.wav)$', '.wav', output)
    elif filetype=='img':
        output = re.sub(r'(?<!\.png)$', '.png', output)
    output = 'processeddata/' + row['section'] + output
    return output


def process_data(func, extractionmethod_id, experiment_id, delete_existing=False, output_loc='temp', multiprocessing=True, cpu_cores=None):
    """ Finds data that hasn't been processed with a given process, processes it and uploads. If existing processed
    files are found in the output_loc, these are read and used instead of re-processed. Set delete_existing='y' to
    avoid this behaviour.

        :param func: The processing function, takes one argument (use partial if config required)
        :param extractionmethod_id: The id of the processing function
        :param experiment_id: The id of the experiment to process
        :param delete_existing: Whether to delete files currently in the output_loc
        :param output_loc: The temporary location of processed files
        :param multiprocessing: If True then multiprocessing is used
        :param cpu_cores: The number of CPUs to use, if None then uses all
        :return: list of files which failed to upload
    """
    db = bugpy.Connection()

    if delete_existing not in [True, False]:
        raise Exception('delete_existing must be either True or False')

    if delete_existing:
        try:
            shutil.rmtree(output_loc)
        except:
            pass
        os.mkdir(output_loc)
    else:
        try:
            os.mkdir(output_loc)
        except:
            pass


    to_process = db.query(f"select r.recording_id, file_path, recording_start, hour_offset from recordings r "
                          f"left join recording_snippets s on s.recording_id = r.recording_id "
                          f"where s.n_snippets is NULL and r.experiment_id = {experiment_id} and r.valid=1")

    if len(to_process)==0:
        print("All files already processed")
        return

    to_process['local_time'] = pd.to_datetime(to_process['recording_start']) + pd.to_timedelta(to_process['hour_offset'],
                                                                                               unit='h')
    to_process['section'] = to_process['file_path'].str.split('/').str[1:3].str.join('/')

    if multiprocessing:
        print(f"Processing {len(to_process)} streamed files using multiprocessing")
        op, fails = process_folder_multiprocess_streamed(to_process['file_path'], func, n_cores=cpu_cores)
    else:
        print(f"Processing {len(to_process)} streamed files sequentially")
        op, fails = process_folder_streamed(to_process['file_path'], func)


    to_process = to_process[~to_process['file_path'].isin(fails)]

    if len(op)==0:
        insert_summary = to_process[['recording_id']]
        insert_summary['extractionmethod_id'] = extractionmethod_id
        insert_summary['n_snippets']= 0
        db.insert(insert_summary, 'recording_snippets')
        return

    to_insert = pd.merge(op, to_process, left_on='orig_audio', right_on='file_path')

    assert len(op) == len(to_insert)

    try:

        to_insert['local_audio_filepath'] = to_insert['audio_filepath'].str.replace(r'(\d+)/audio', r'\1_complete/audio',
                                                                                    regex=True).str.replace(r'(?<!\.wav)$',
                                                                                                            '.wav', regex=True)

        to_insert['local_img_filepath'] = to_insert['img_filepath'].str.replace(r'(\d+)/imgs', r'\1_complete/imgs',
                                                                                    regex=True).str.replace(r'(?<!\.png)$',
                                                                                                            '.png', regex=True)
        to_insert['recording_time_start'] = pd.to_timedelta(to_insert['start_sample'] / (22050), unit='s')
        to_insert['local_time_start'] = to_insert['local_time'] + to_insert['recording_time_start']
        to_insert['recording_time_start'] = to_insert['recording_time_start'].apply(lambda x: str(x).split(' ')[-1])

        to_insert['sample_length'] = to_insert['stop_sample'] - to_insert['start_sample']

        to_insert['extractionmethod_id'] = extractionmethod_id

        to_insert['audio_filesize_mb'] = to_insert['local_audio_filepath'].apply(filesize)
        to_insert['img_filesize_mb'] = to_insert['local_img_filepath'].apply(filesize)

        to_insert['audio_filepath'] = to_insert.apply(format_for_s3, filetype='audio', axis=1)
        to_insert['img_filepath'] = to_insert.apply(format_for_s3, filetype='img', axis=1)
    except Exception as e:
        to_insert.to_csv('processing_error.csv', index=False)
        raise e

    to_insert = to_insert[['recording_id',
                           'audio_filepath',
                           'img_filepath',
                           'local_audio_filepath',
                           'local_img_filepath',
                           'local_time_start',
                           'recording_time_start',
                           'start_sample',
                           'sample_length',
                           'audio_filesize_mb',
                           'img_filesize_mb',
                           'max_amplitude',
                           'major_freq',
                           'extractionmethod_id']]

    bucket = get_credentials('s3_web', 'BUCKET')
    fails_audio = upload_filelist(to_insert['local_audio_filepath'], bucket, uploadnames=to_insert['audio_filepath'])
    fails_img = upload_filelist(to_insert['local_img_filepath'], bucket, uploadnames=to_insert['img_filepath'])
    #

    failed_records = to_insert[(to_insert['local_audio_filepath'].isin(fails_audio)) | (to_insert['local_img_filepath'].isin(fails_img))]['recording_id'].unique()
    to_process = to_process[~to_process['recording_id'].isin(failed_records)]

    to_insert = to_insert[
        (~to_insert['local_audio_filepath'].isin(fails_audio)) & (~to_insert['local_img_filepath'].isin(fails_img))]


    insert_summary = to_insert[['recording_id']]
    insert_summary['n_snippets'] = 1
    insert_summary = insert_summary[['recording_id', 'n_snippets']].groupby('recording_id').count()

    insert_summary = pd.merge(to_process[['recording_id']].drop_duplicates(), insert_summary,
                              on='recording_id', how='left').fillna(0)
    insert_summary['extractionmethod_id'] = extractionmethod_id

    db.insert(insert_summary, 'recording_snippets')
    db.insert(to_insert, 'snippets')

    shutil.rmtree(output_loc)


def process_folder_multiprocess_streamed(file_locs, func, n_cores=None, raise_errors=True):
    if n_cores is None:
        n_cores = os.cpu_count()
    if os.name == 'nt' or True:
        fails, output = multithread(file_locs, func, max_workers=n_cores, raise_errors=raise_errors)
    else:
        fails, output = multiprocess(file_locs, func, max_workers=n_cores, raise_errors=raise_errors)

    return pd.concat(output), fails


def process_folder_streamed(file_locs, func):
    try_again = []
    output = []
    failures = []
    for file_path in tqdm(file_locs):
        try:
            output.append(func(file_path))
        except Exception as e:
            print(e)
            try_again.append(file_path)
    if len(try_again) > 0:
        print(f'{len(try_again)} failed, retrying')
        for file_path in tqdm(try_again):
            try:
                output.append(func(file_path))
            except Exception as e:
                failures.append(file_path)
                print(f'{file_path} failed again')
                print(e)
    return pd.concat(output), failures