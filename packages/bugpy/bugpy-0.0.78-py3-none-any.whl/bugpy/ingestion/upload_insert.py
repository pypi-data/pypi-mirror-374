from bugpy.ingestion import collect_metadata
from bugpy.data import upload_filelist
import pandas as pd


def upload_recordings(db, partial_upload=True, prompt_disconnect=False, parallel=False, s3_loc='s3_web'):
    """ Uploads a list of recordings from local storage

        :param db: bugpy.Connection object
        :param partial_upload: Whether to tolerate a partial upload
        :param prompt_disconnect: Whether to prompt the user to disconnect from the VPN to speed up upload
        :param parallel: Whether to upload in parallel, defaults to False
        :param s3_loc: Where to upload files, defaults to prod (s3_web)
        :return: list of files which failed to upload
    """

    df, notes = collect_metadata(db)

    df['file_path'] = 'raw_data/project_' + df['project_id'].astype(str) + '/experiment_' + df['experiment_id'].astype(
        str) + '/' + df['file_loc']

    experiment_ids = ','.join(df['experiment_id'].astype(str).unique())
    existing = db.query(f"select file_path from recordings where experiment_id in ({experiment_ids})")
    df = df[~df['file_path'].isin(existing)]

    if prompt_disconnect:
        print("Uploading data now, for faster upload, disconnect from the VPN now.")
        input("Press enter when you are ready")

    fails = upload_filelist(df['local_loc'], s3_label=s3_loc, uploadnames=df['file_path'], parallel=parallel)

    if len(fails) > 0 and not partial_upload:
        print(f"{len(fails)} files failed to upload - check and retry")
        return fails

    lost_files = {t[0] for t in fails}

    df = df[~df['local_loc'].isin(lost_files)]

    if prompt_disconnect:
        print("Upload complete, reconnect to the VPN")
        input("Press enter when you are ready")

    df['file_path'] = df['file_path'].str.replace('\\', '/')

    recording_ids = db.insert(df, 'recordings')

    if notes:
        print("Inserting notes")
        input_notes = pd.DataFrame(recording_ids, columns=['recording_id'])
        input_notes['notes'] = notes
        db.insert(input_notes, 'recording_notes')
    else:
        print("No notes to add")

    return fails
