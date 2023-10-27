import os
import time
import schedule
import shutil
from datetime import datetime
import pytz

import drive



tz_est = pytz.timezone('US/Eastern')



def create_world_export(world_name):
    input_directory = os.path.join('worlds', world_name)
    output_filename = os.path.join('worlds', f"[{datetime.now(tz_est).strftime('%Y-%m-%d %H;%M')}]__{world_name}")
    shutil.make_archive(output_filename, 'zip', input_directory)
    os.rename(f"{output_filename}.zip", f"{output_filename}.mcworld")
    return f"{output_filename}.mcworld"



def backup(drive_service, backup_types):
    upload_file = create_world_export('My Server World')

    # check the condition of each backup_type to see if we should upload the file there
    for backup_type_name, backup_type_options in backup_types.items():
        if backup_type_options['condition']():

            # Remove the oldest file if at maximum
            files = drive.get_files_in_folder(drive_service, backup_type_options['folder_id'])
            if backup_type_options['max_files'] is not None and files is not None:
                if len(files) >= backup_type_options['max_files']:
                    oldest_file = files[0]
                    drive.delete_file_by_id(drive_service, oldest_file['id'])

            # Upload the backup to its designated folder
            drive.upload_file_to_folder(drive_service, upload_file, backup_type_options['folder_id'])
    
    # Delete the export file
    os.remove(upload_file)



if __name__ == '__main__':
    # Authenticate and setup google drive connection
    credentials = drive.authenticate_gdrive()
    drive_service = drive.build('drive', 'v3', credentials=credentials)

    # define the different backup operations that will be performed
    backup_types = {
        'hourly': {     # hourly backups are done everytime the job is run
            'folder_id': '1aLT3DAL-lq6rRaUJjYw7E_O_JyYfzpYs',
            'max_files': 12,
            'condition': lambda: True   
        },

        'daily': {      # daily backups are done every day at 12am
            'folder_id': '10yI82oHltCQEPl0p6aKAuF2jluK6wDCa',
            'max_files': 7,
            'condition': lambda: datetime.now(tz_est).hour == 0 
        },

        'weekly': {     # weekly backups are done on sundays at 12am
            'folder_id': '1u7KzYrz_1PhAv7OUZhe8qD6FKNUZO3gZ',
            'max_files': 4,
            'condition': lambda: datetime.now(tz_est).weekday() == 6 and datetime.now(tz_est).hour == 0 
        },

        'monthly': {    # monthly backups are done on the first day of the month at 12am
            'folder_id': '1XfBs2MZf6qmdhbfE8EJlfrJMQlvmCeik',
            'max_files': 6,
            'condition': lambda: datetime.now(tz_est).day == 1 and datetime.now(tz_est).hour == 0 
        },

        'yearly': {     # yearly backups are done on the first day of the year at 12am
            'folder_id': '1dMWTN9d2NrAU1v6WHB5RiQhOm8NQD5Gm',
            'max_files': None,
            'condition': lambda: datetime.now(tz_est).month == 1 and datetime.now(tz_est).day == 1 and datetime.now(tz_est).hour == 0 
        }
    }

    # schedule the backup job to run every hour
    schedule.every().hour.at(":00").do(backup, drive_service, backup_types)
    while True:
        time_to_next_job = schedule.idle_seconds()
        if time_to_next_job is None:
            # no more jobs
            break
        elif time_to_next_job > 0:
            # sleep exactly the right amount of time
            time.sleep(time_to_next_job)
        schedule.run_pending()
