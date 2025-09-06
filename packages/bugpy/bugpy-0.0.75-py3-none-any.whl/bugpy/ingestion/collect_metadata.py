import pandas as pd
import os
from bugpy.utils import ossafe_join


def get_id(table, db, target):
    reftable = db.query(f"select {table}_id as id, {target} as target from {table}s order by {table}_id")
    reftable['id'] = reftable['id'].astype(str)

    print(f"Select the correct ID for {table} from:\n")
    for i, row in reftable.iterrows():
        print(f'{row["id"]}:\t {row["target"]}')

    select_id = None
    while select_id not in reftable['id'].values:
        select_id = input("Select correct ID\n> ")
    selection = reftable[reftable['id'] == select_id]['target'].iloc[0]
    select_id = int(select_id)
    print(f"You selected {select_id}: {selection}")

    return select_id, selection


def get_limited(item, limit_list):
    print(f"Select the correct ID for {item} from:\n")
    items = {}
    for i, item in enumerate(limit_list):
        print(f'{i}:\t {item}')
        items[str(i)] = item

    select_id = None
    while select_id not in items:
        select_id = input("Select a valid ID\n> ")

        if select_id == '':
            print("No id selected, skipping")
            return None, None
    selection = items[select_id]
    print(f"You selected {select_id}: {selection}")

    return select_id, selection


def get_date(text):
    date_selected = False
    output_date = ''
    while not date_selected:
        date = input(text + '\n> ')
        try:
            date = pd.to_datetime(date)
        except Exception:
            print(f'{date} is not a valid date. Try again.')
            continue

        correct = None
        while correct not in ['y', 'n']:
            if pd.isna(date):
                correct = input(f"Date is unknown - is this correct? [y/n]\n> ")
                output_date = None
            else:
                correct = input(f"Date selected is {date.strftime('%d %B %Y %H:%M')} - is this correct? [y/n]\n> ")
                output_date = date.strftime('%Y-%m-%d %H:%M:%S')
            correct = correct.strip()

        if correct == 'y':
            date_selected = True
    return output_date


def get_latitude():
    correct = False
    while not correct:
        latitude = input("Please enter a latitude (degrees)\n> ")
        if latitude == '':
            print("No latitude entered")
            return None
        try:
            latitude = float(latitude)
        except ValueError:
            print("Latitude should be a number")
            continue
        if latitude < -90 or latitude > 90:
            print("Latitude should be between -90 and +90")
            continue
        correct = True
    return latitude


def get_longitude():
    correct = False
    while not correct:
        longitude = input("Please enter a longitude (degrees)\n> ")
        if longitude == '':
            print("No longitude entered")
            return None
        try:
            longitude = float(longitude)
        except ValueError:
            print("Longitude should be a number")
            continue
        if longitude < -180 or longitude > 180:
            print("Longitude should be between -180 and +180")
            continue
        correct = True
    return longitude


def get_number(question):
    correct = False
    while not correct:
        number = input(question + '\n> ')
        if number == '':
            print("No number selected")
            return None
        try:
            number = float(number)
        except ValueError:
            print("Entry should be a number, or empty")
            continue
        correct = True
    return number


def get_project_and_experiment(db):
    project_id, _ = get_id('project', db, 'project_name')

    reftable = db.query(f"select experiment_id as id, experiment_name as target from experiments "
                        f"where project_id = {project_id} "
                        f"order by experiment_id")
    reftable['id'] = reftable['id'].astype(str)

    print(f"Select the correct ID for experiment from:\n")
    for i, row in reftable.iterrows():
        print(f'{row["id"]}:\t {row["target"]}')
    print(
        f"If your experiment isn't here, please register it in the database at https://connect.doit.wisc.edu/bickportal/new-experiment")

    experiment_id = None
    while experiment_id not in reftable['id'].values:
        experiment_id = input("Select correct ID\n> ")
    selection = reftable[reftable['id'] == experiment_id]['target'].iloc[0]
    print(f"You selected {experiment_id}: {selection}")

    return project_id, experiment_id


def recording_metadata_collector(db, df=pd.DataFrame()):
    ids = {'locationtype': 'name',
           'substrate': "concat(common_name, case when variety is not null then concat(' (', variety, ')') else '' end)",
           'targetorgan': 'name',
           'noisedampener': 'name',
           'timezone': 'timezone',
           'sensortype': 'sensor_type'}
    freeform = {'location': 'Please type the address where the experiment took place'}
    dates = {'recording_start': 'Please enter the start datetime of the recording, in format YYYY-MM-DD HH:MM:SS'}
    numbers = {'replication': 'What replication number is this'}

    if type(df) != pd.DataFrame:
        print("Provided df is not a pandas dataframe! Starting from scratch\n")

    happy = 'n'

    while happy != 'y':
        output = {}

        summary = {}

        for item in dates:
            if item not in df.columns:
                chosen_date = get_date(dates[item])
                output[item] = chosen_date
                summary[item] = chosen_date
            else:
                summary[item] = df[item].unique()[0]
            print('')

        for item in freeform:
            if item not in df.columns:
                chosen_value = input(freeform[item] + '\n>')
                output[item] = chosen_value
                summary[item] = chosen_value
            else:
                summary[item] = df[item].unique()[0]
            print('')

        for item in numbers:
            if item not in df.columns:
                number = get_number(numbers[item])
                output[item] = number
                summary[item] = number
            else:
                summary[item] = df[item].unique()[0]
            print('')

        for item in ids:
            if item not in df.columns:
                id_number, id_name = get_id(item, db, ids[item])
                output[item + '_id'] = id_number
                summary[item] = id_name
            else:
                summary[item] = df[item].unique()[0]
            print('')

        latitude = get_latitude()
        print('')
        longitude = get_longitude()
        output['latitude'] = latitude
        output['longitude'] = longitude
        summary['latitude'] = latitude
        summary['longitude'] = longitude

        print("\n\n---------------------------")
        print("Does this look right?\n")
        for column in summary:
            print(f'{column}:\t {summary[column]}')
        happy = input('\ny/n?\n> ').strip().lower()

    return pd.DataFrame([output])


def mic_metadata_collector(db, df=pd.DataFrame()):
    ids = {'insect': "concat(common_name,' (',genus,' ',species,')')",
           'lifestage': "lifestage"}
    freeform = {'chemical': 'What chemical was used? Leave blank if n/a',
                'application_rate': 'What was the application rate (e.g. 8.5 fl oz/ac)? Leave blank if n/a',
                'genotype': 'What was the genotype code? Leave blank if n/a',
                'phenotype': 'What was the phenotype code? Leave blank if n/a/'}
    numbers = {'insect_count': 'How many insects were used? Leave blank if n/a'}
    limited = {'insect_density': ['none', 'low', 'medium', 'high'],
               'application_process': ['manual placement', 'soil injection', 'in-furrow', 'genotype', 'sprayed',
                                       'natural origin']}

    existing_treatments = db.query("select * from treatments;").fillna(-1)

    if type(df) != pd.DataFrame:
        print("Provided df is not a pandas dataframe! Starting from scratch")

    mic_list = [str(m) for m in df['sensor_number'].unique()]

    print("You will now be asked to enter which treatment was present for each sensor (e.g. contact mic). If more than "
          "one sensor recorded the same treatment (e.g. 1 corn root worm on corn plant with no special conditions) "
          "then these can be grouped.")
    print(f"In the provided dataset, there are {len(mic_list)} sensors identified: {','.join(mic_list)}")
    handled = {}
    group_number = 1
    while any(mic not in handled for mic in mic_list):
        remaining = [str(mic) for mic in mic_list if mic not in handled]
        group = input(
            f"List sensor numbers that share treatment {group_number} - separate with commas (e.g. {','.join(remaining)})\n> ")
        try:
            group = group.strip().split(',')
        except Exception as e:
            print(f'{group} is not a valid input. Please enter sensor numbers separated with a comma')
        if any(g not in mic_list for g in group):
            print(f'One or more of {group} is not in {mic_list}!')
            continue
        if any(g in handled for g in group):
            print(f'One or more of {group} is already in {handled.keys()}!')
            continue
        for g in group:
            handled[g] = group_number
        group_number += 1

    inverted = {v: [k for k in handled if handled[k] == v] for v in set(handled.values())}

    happy = 'n'

    while happy != 'y':

        outputs = []
        summaries = []

        for tret in inverted:
            mics = inverted[tret]
            subdf = df[df['sensor_number'].isin(mics)]
            print(f"\n----------------------------\n"
                  f"For sensor numbers {' and '.join(mics)}"
                  f"\n----------------------------\n")

            output = {}
            summary = {}

            for item in limited:
                if item not in subdf.columns:
                    item_id, value = get_limited(item, limited[item])
                    output[item] = value
                    summary[item] = value
                else:
                    summary[item] = df[item].unique()[0]
                print('')

            for item in freeform:
                if item not in subdf.columns:
                    value = input(freeform[item] + '\n> ')
                    if value == '':
                        value = None
                    output[item] = value
                    summary[item] = value
                else:
                    summary[item] = df[item].unique()[0]
                print('')

            for item in numbers:
                if item not in subdf.columns:
                    value = get_number(numbers[item])
                    output[item] = value
                    summary[item] = value
                else:
                    summary[item] = df[item].unique()[0]
                print('')

            for item in ids:
                if item not in subdf.columns:
                    id_number, id_name = get_id(item, db, ids[item])
                    output[item + '_id'] = id_number
                    summary[item] = id_name
                else:
                    summary[item] = df[item].unique()[0]
                print('')

            treatment_params = ['insect_id', 'lifestage_id', 'insect_count', 'application_process', 'chemical',
                                'application_rate', 'genotype', 'phenotype', 'insect_density']
            output_df = pd.DataFrame([output])
            matches = pd.merge(output_df.fillna(-1), existing_treatments, on=treatment_params)
            if len(matches) == 0:
                name = input("Input a short name for this treatment (e.g. 'Low CRW')\n> ")
                output['treatment_name'] = name
                summary['treatment_name'] = name
            else:
                output['existing_treatment_id'] = matches['treatment_id'].iloc[0]
                output['treatment_name'] = matches['name'].iloc[0]
                summary['treatment_name'] = matches['name'].iloc[0]

            for mic in mics:
                print(mic)
                output['sensor_number'] = int(mic)
                outputs.append(output.copy())
                summary['sensor_number'] = int(mic)
                summaries.append(summary.copy())

        print("\n\n---------------------------")
        print("Does this look right?\n")
        for summary in summaries:
            print(f"For sensor number {summary['sensor_number']}")
            for column in summary:
                if column == 'sensor_number':
                    continue
                print(f'{column}:\t {summary[column]}')
        happy = input('\ny/n?\n> ').strip().lower()

    outputs = pd.DataFrame(outputs)

    return outputs


def load_data(folder, base_loc='', allowed_extensions=['.wav']):
    df = []
    allowed_extensions = tuple(allowed_extensions)
    for root, _, files in os.walk(ossafe_join([base_loc, folder]).rstrip('/')):
        for file in files:
            if file.endswith(allowed_extensions):
                full_path = ossafe_join([root, file])
                if base_loc is not None:
                    rel_path = os.path.relpath(full_path, base_loc)
                else:
                    rel_path = full_path
                df.append(rel_path)
    df = pd.DataFrame(df, columns=['file_loc'])
    return df


def get_filelist():
    data_loaded = False
    print('All folder details will be preserved in s3 as provided, please provide the absolute file loc if '
          'running this script away from the target folder.\n'
          'e.g. if the data folder to be uploaded is /home/data/raw_data/2025_data/Collaborator2/TargetExperiment, '
          'then labels in CSV or folder should be provided from the root directory TargetExperiment and you '
          'need to provide the absolute path /home/data/raw_data/2025_data/Collaborator2. If you are already in the '
          'folder containing your target folder, skip this.')
    root = input('What is your filepath prefix?\n')
    root = root.replace('\\', '/').rstrip('/')
    while not data_loaded:
        data_choice = input(
            "How do you have your file list?\n1. In a csv with column heading 'file_loc'\n2.In a folder (subfolders is fine)\n> ")
        if data_choice == '1':
            data_csv = input("Please enter csv location (absolute is best)\n> ")
            try:
                df = pd.read_csv(data_csv)
                assert 'file_loc' in df.columns
                data_loaded = True
            except AssertionError:
                print("CSV does not contain header 'file_loc'")
            except Exception as e:
                print(f"CSV could not be loaded because {e}, try again")
            for file in df['file_loc']:
                target_loc = ossafe_join([root, file]).rstrip('/')
                if not os.path.exists(target_loc):
                    raise Exception(f"Could not find {target_loc} in csv! Please check")

        elif data_choice == '2':
            data_folder = input("Input folder containing data (all subfolders will be scanned)\n> ")
            df = load_data(data_folder, root)
            data_loaded = True

    print(f"Found {len(df)} wav files!")

    df['local_loc'] = root + '/' + df['file_loc'].str.strip('/')

    if 'filesize_mb' not in df:
        df['filesize_mb'] = df['local_loc'].apply(os.path.getsize) / (1024 * 1024)

    return df


def fill_sensor_number(df):
    if 'sensor_number' not in df or any(df['sensor_number'].isna()):
        automic = None
        while automic not in ['y', 'n']:
            example_file = df['file_loc'].iloc[0].split('/')[-1]
            print(f"One example file:\n{example_file}")
            automic = input(
                "Do audio files contain mic info (e.g. in the form Pi1_Date_mic0hour1_0.wav)? [y/n]\n> ").lower().strip()
        if automic == 'y':
            try:
                df['sensor_number'] = df['file_loc'].str.split('mic').str[1].str[:1].astype(int)
                print(f"Found mics numbered from {df['sensor_number'].min()} to {df['sensor_number'].max()}")
            except Exception:
                print("Mic numbers could not be successfully inferred! Upload one set of mics at a time")
        else:
            getting_micnum = True
            while getting_micnum:
                micnum = input(
                    "Please enter mic number for files (if multiple mics, upload separately or provide data in csv)\n> ")
                try:
                    micnum = int(micnum)
                    getting_micnum = False
                except Exception:
                    print("Enter a valid integer mic number")
            df['sensor_number'] = micnum
    return df['sensor_number']


def fill_hour_offset(df):
    if 'hour_offset' not in df or any(df['hour_offset'].isna()):
        automic = None
        while automic not in ['y', 'n']:
            example_file = df['file_loc'].iloc[0].split('/')[-1]
            print(f"One example file:\n{example_file}")
            automic = input(
                "Do audio files contain hour info (e.g. in the form Pi1_Date_mic0hour1_0.wav)? [y/n]\n> ").lower().strip()
        if automic == 'y':
            try:
                df['hour_offset'] = df['file_loc'].str.split('hour').str[1].str.split('_').str[0].str.split('.').str[0].astype(int)
                print(f"Found hours numbered from {df['hour_offset'].min()} to {df['hour_offset'].max()}")
            except Exception:
                print("Hours could not be successfully inferred! Will be left blank - please fix manually if needed")
                df['hour_offset'] = None
        else:
            print("Hours will be left blank - please fix manually if needed")
            df['hour_offset'] = None
    return df['hour_offset']


def fill_and_add_treatment(df, db):
    treatment_list = ['treatment_name', 'insect_id', 'lifestage_id', 'insect_count', 'application_process', 'chemical',
                      'application_rate', 'genotype', 'phenotype', 'insect_density']
    if 'existing_treatment_id' not in df.columns:
        df['existing_treatment_id'] = None
    treatments = df[df['existing_treatment_id'].isna()][treatment_list].drop_duplicates()
    treatments['name'] = treatments['treatment_name']
    if len(treatments) > 0:
        db.insert(treatments, 'treatments')
        treatments = treatments.fillna(-1)
        treatment_ids = db.query("select *, name as treatment_name from treatments;").fillna(-1)
        treatment_ids = pd.merge(treatments, treatment_ids, on=treatment_list)

        df = pd.merge(df, treatment_ids[['treatment_name', 'treatment_id']], on='treatment_name', how='left')
        df['treatment_id'] = df['treatment_id'].fillna(df['existing_treatment_id'])
        return df['treatment_id']
    else:
        return df['existing_treatment_id']


def collect_metadata(db):
    df = get_filelist()
    df['sensor_number'] = fill_sensor_number(df)
    df['hour_offset'] = fill_hour_offset(df)

    if 'experiment_id' not in df or 'project_id' not in df:
        project_id, experiment_id = get_project_and_experiment(db)
        df['experiment_id'] = experiment_id
        df['project_id'] = project_id
    elif any(df['experiment_id'].isna()) or any(df['project_id'].isna()):
        print(f"One or more of your 'experiment_id' column is null, disregarding.")
        project_id, experiment_id = get_project_and_experiment(db)
        df['project_id'] = project_id
        df['experiment_id'] = experiment_id

    output = recording_metadata_collector(db, df)

    df = pd.merge(df, output, how='cross')

    micdetails = mic_metadata_collector(db, df)

    df = pd.merge(df, micdetails, on='sensor_number')

    df['treatment_id'] = fill_and_add_treatment(df, db)

    notes = input("Do you have any notes to add to these recordings? y/n?\n> ").strip().lower()
    if notes == 'y':
        notes = input("Enter notes").replace(';',',')
    else:
        notes = False

    return df, notes
