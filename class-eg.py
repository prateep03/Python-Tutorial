# sourceManager
# Documentation at https://bitbucket.zgtools.net/projects/CDA/repos/sourcemanager/browse
# Created by Anna Liu (annali@zillowgroup.com)
import multiprocessing
import threading
import datetime
import webbrowser
from appJar import *
from zanalyzer import *

# ======================================================================================================================
# Source Upload
# ======================================================================================================================
def upload_source_files_parallel(dbname, schema, source_folder, mode='drop', trigger=0):
    """
    Upload source files (parallel - multiple processes)
    :param dbname: database name
    :param schema: schema name
    :param source_folder: the source folder path
    :param trigger: int
                    tell which tab triggers this function
                    0: Upload
                    1: Customize
                    2: Batch upload
    :param mode: how to handle existing tables: 'drop' or 'keep'.
    :return: None
    """
    # Reset status bar to 0
    global percentComplete, current_batch, failed_files
    print("Upload files in parallel...")
    fips_key = schema.replace("_", "")
    if trigger == 0:
        percentComplete = 0
    elif trigger == 2:
        current_batch[fips_key]['percentComplete'] = 0
    # create a list of source files to upload
    target_files = [(os.stat(os.path.join(source_folder, file)).st_size, {'file': file, 'source_folder': source_folder,
                                                                          'dbname': dbname, 'schema': schema,
                                                                          'mode': mode, 'login': db_login})
                    for file in os.listdir(source_folder) if is_standardized(os.path.join(source_folder, file))]
    target_files = sorted(target_files, key=lambda x: x[0])
    # Record failed files (csv files that are not standardized
    non_standardized_files = [file for file in os.listdir(source_folder)
                              if not is_standardized(os.path.join(source_folder, file))
                              and file.endswith('.csv')]
    if len(non_standardized_files) > 0:
        failed_files[fips_key] = non_standardized_files
    if len(target_files) == 0:
        return True
    # upload files in parallel
    allUploadProcesses = []
    index = 0
    upload_manager = multiprocessing.Manager()
    upload_failed_flles = upload_manager.list()
    for file in target_files:
        size, params = file
        process = multiprocessing.Process(target=file_upload_worker, args=(params, upload_failed_flles))
        process.start()
        allUploadProcesses.append(process)
    for process in allUploadProcesses:
        process.join()
        index = index + 1
        if trigger == 1:
            app.showMessage('mess_dev2')
            if index == len(target_files):
                if len(upload_failed_flles) > 0:
                    try:
                        failed_files[fips_key] += upload_failed_flles
                    except KeyError:
                        failed_files[fips_key] = upload_failed_flles
                if len(failed_files) > 0:
                    file_str = [", ".join(v)for k, v in failed_files.items()][0]
                    file_count = len(upload_failed_flles)
                    app.hideMessage('mess_dev2')
                    message = "Uploaded total {0} files to dev.{1}. \n" \
                              "The following files have been excluded: \n\n {2}\n\n" \
                              "Please make sure that all uploaded files MUST be standardized correctly. " \
                              "Please review them!".format(index-file_count, os.environ['USERNAME'], file_str)
                    app.infoBox("Bad files detected!", message, parent=None)
                else:
                    app.setMessage("mess_dev2",
                                   "Finished! Uploaded total {0} files to dev.{1}!".format(index,
                                                                                           os.environ['USERNAME']))
            else:
                app.setMessage("mess_dev2",
                               "Uploading {0} of {1} files to dev.{2}...".format(index,
                                                                                 len(target_files),
                                                                                 os.environ['USERNAME']))
        elif trigger == 2:
            current_batch[fips_key]['percentComplete'] = round(100 * (index / len(allUploadProcesses)))
        else:
            percentComplete = round(100 * (index / len(allUploadProcesses)))
    if trigger != 1 and len(upload_failed_flles) > 0:
        try:
            failed_files[fips_key] += upload_failed_flles
        except KeyError:
            failed_files[fips_key] = upload_failed_flles

def upload_source(FIPS=None, source_path=None, trigger=0):
    """Start point for uploading source"""
    if FIPS is None or source_path is None:
        FIPS = app.getEntry('fipsEnt')
        source_path = app.getEntry('sourcePathEnt')
    if isinstance(source_path, str):
        source_path = source_path.replace('\\', '/')
    if is_valid_fips(FIPS) and os.path.exists(source_path) and os.path.isdir(source_path):
        print("-----------------------------------------------------------------------------------")
        print("FIPS: {0}".format(FIPS))
        print("Source Folder Path: {0}".format(source_path))
        print("-----------------------------------------------------------------------------------")
        print("Uploading Source Files to RDS Server")
        start_time = time.time()
        conn_rds = connect_to_sql_server(**db_login)
        cursor_rds = conn_rds.cursor()
        src_dbname = 'src'
        src_schema_name = '_{0}'.format(FIPS)
        create_sql_schema(cursor_rds, src_dbname, src_schema_name)
        if app.getCheckBox("Empty Schema?"):
            clean_sql_schema(cursor_rds, src_dbname, src_schema_name)
        conn_rds.commit()
        bad_county = upload_source_files_parallel(src_dbname, src_schema_name, source_path, trigger=trigger)
        # Update county_grouping table
        print("Updating county_grouping for FIPS {0}...".format(FIPS))
        statewide_classifier(target_fips=FIPS, cursor=cursor_rds, update_database=True)
        conn_rds.commit()
        conn_rds.close()
        print("--- %s seconds ---" % (round(time.time() - start_time, 2)))
        if trigger == 0:
            if bad_county:
                message = "Source files are failed to upload for FIPS {0}.\n" \
                          "Please make sure that all source files MUST be standardized correctly. " \
                          "Please review them".format(FIPS)
                app.infoBox("File upload failed!", message, parent=None)
            elif len(failed_files) > 0:
                file_str = [", ".join(v) for k, v in failed_files.items()][0]
                message = "Source files have been uploaded for FIPS {0} except the following files: \n{1}\n\n " \
                          "Please make sure that all source files MUST be standardized correctly. " \
                          "Please review them!".format(FIPS, file_str)
                app.infoBox("File upload finished!", message, parent=None)
            else:
                message = "All source files have been uploaded for FIPS {0}!".format(FIPS)
                app.infoBox("File upload finished!", message, parent=None)
            reset_upload_screen()
    else:
        app.errorBox("Invalid Entry", "Invalid FIPS or source folder path!")

def upload_source_dev():
    """For Mapping Specs: upload files and lookup tables to dev"""
    # get all checkboxes
    copy_tables_checked = app.getCheckBox("Copy ALL source file table(s) from src")
    lookup_checked = app.getCheckBox("Create Lookup Tables")
    statewide_checked = app.getCheckBox("Statewide")
    upload_checked = app.getCheckBox("Supplemental file(s) from local")
    database_cleaned = False
    start_time = time.time()
    if copy_tables_checked or lookup_checked:
        FIPS = app.getEntry('fipsEnt_dev')
        fips_entered = FIPS.replace(' ', '').split(',')
        schemas_entered = ['\'_{0}\''.format(code) for code in fips_entered if is_valid_fips(code)]
        schemas_entered_str = ",".join(schemas_entered)
        if FIPS != '' and len(fips_entered) > 0 and len(fips_entered) == len(schemas_entered):
            print("-----------------------------------------------------------------------------------")
            print("FIPS: {0}".format(FIPS))
            print("Uploading Source Files to RDS Server")
            conn_rds = connect_to_sql_server(**db_login)
            cursor_rds = conn_rds.cursor()
            dev_dbname = 'dev'
            dev_schema_name = os.environ['USERNAME']
            if not database_cleaned:
                app.showMessage('mess_dev')
                create_sql_schema(cursor_rds, dev_dbname, dev_schema_name)  # create the schema for user if not existed
                clean_sql_schema(cursor_rds, dev_dbname, dev_schema_name)
                database_cleaned = True
                app.hideMessage('mess_dev')
            if copy_tables_checked:
                src_tables = get_table_names(cursor_rds, 'src', schemas_entered_str)
                print("Total {0} tables found in src ...".format(len(src_tables)))
                app.setMessage("mess_dev1", "Total {0} tables found in src ...".format(len(src_tables)))
                app.showMessage('mess_dev1')
                counter = 0
                for schema_from, table_name in src_tables:
                    new_table_name = schema_from + "_" + table_name
                    # SQL table name length limit is 128 characters
                    new_table_name = new_table_name[:128]
                    print("... Copying table {0} from {1}.{2} to {3}.{4}".format(table_name, 'src', schema_from,
                                                                                 dev_dbname, dev_schema_name))
                    copy_sql_table(cursor_rds, 'src', schema_from, table_name, dev_dbname, dev_schema_name, new_table_name)
                    counter += 1
                    app.setMessage("mess_dev1",
                                   "{0} of {1} table(s) successfully copied from src to dev.{2}!".format(counter, len(src_tables), os.environ['USERNAME']))
                conn_rds.commit()
                app.setMessage("mess_dev1",
                               "Total {0} table(s) successfully copied from src to dev.{1}!".format(len(src_tables),
                                                                                                    os.environ['USERNAME']))
            if lookup_checked:
                create_all_lookups(cursor_rds, dev_dbname, dev_schema_name, fips_entered, statewide_checked)
                app.showMessage('mess_dev3')
            conn_rds.commit()
            conn_rds.close()
        elif FIPS != '':
            invalid_codes = ",".join([code for code in fips_entered if not is_valid_fips(code)])
            app.errorBox("Invalid FIPS Codes", "The following FIPS Code(s) are invalid: \n\n {0}".format(invalid_codes))
            return
    if upload_checked:
        source_path = app.getEntry('sourcePathEnt_dev')
        source_path = source_path.replace('\\', '/')
        if os.path.exists(source_path) and os.path.isdir(source_path):
            print("-----------------------------------------------------------------------------------")
            print("Source File Path: {0}".format(source_path))
            print("Uploading Source Files to RDS Server")
            dev_dbname = 'dev'
            dev_schema_name = os.environ['USERNAME']
            if not database_cleaned:
                app.showMessage('mess_dev')
                conn_rds = connect_to_sql_server(**db_login)
                cursor_rds = conn_rds.cursor()
                create_sql_schema(cursor_rds, dev_dbname, dev_schema_name)  # create the schema for user if not existed
                clean_sql_schema(cursor_rds, dev_dbname, dev_schema_name)
                database_cleaned = True
                conn_rds.commit()
                conn_rds.close()
                app.hideMessage('mess_dev')
            bad_county = upload_source_files_parallel(dev_dbname, dev_schema_name, source_path, trigger=1)
            if bad_county:
                message = "Supplemental files are failed to upload.\n" \
                          "Please make sure that all source files MUST be standardized correctly. Please review them!"
                app.infoBox("Upload Failure!", message, parent=None)
        elif upload_checked and source_path != '':
            app.errorBox("Invalid Path", "Invalid path: {0}".format(source_path))
    print("--- %s seconds ---" % (round(time.time() - start_time, 2)))

# ======================================================================================================================
# Sub Windows - Utility Functions
# ======================================================================================================================
def create_status_window(max_num_files):
    app.startSubWindow("Uploading...", modal=True)
    app.setSize(400, 300)
    app.setSticky("news")
    app.setStretch("both")
    for index in range(max_num_files):
        app.addLabel("current_file{0}".format(index), "", row=index, column=0)
        # app.setLabelAlign("current_file{0}".format(index), 'left')
        app.addMeter("progress{0}".format(index), row=index, column=1)
        app.setMeterFill("progress{0}".format(index), "green")
    app.stopSubWindow()
    app.hideSubWindow("Uploading...")

def update_status_window(max_num_files):
    index = 0
    for fips_code, info in current_batch.items():
        app.setLabel("current_file{0}".format(index), fips_code)
        app.showLabel("current_file{0}".format(index))
        app.showMeter("progress{0}".format(index))
        index = index + 1
    while index < max_num_files:
        app.hideLabel("current_file{0}".format(index))
        app.hideMeter("progress{0}".format(index))
        index = index + 1

def create_layout_file_input_box(layout_file_lookup_table_colnames):
    """Sub-window for adding/editing a record to Layout File Registration table"""
    app.startSubWindow("View/Add/Edit Record", modal=True)
    app.setSize(1100, 450)
    app.setSticky("news")
    app.startLabelFrame("Add/Edit fields and press OK to save")
    app.setFont(11)
    app.setStretch("both")
    app.setSticky("")
    app.addLabel("RowIDLabel", "Row ID", row=0, column=0)
    app.setLabelAlign("RowIDLabel", 'left')
    app.setLabelWidth("RowIDLabel", 20)
    app.addLabel("RecordTypeLabel", "Record Type", row=1, column=0)
    app.setLabelAlign("RecordTypeLabel", 'left')
    app.setLabelWidth("RecordTypeLabel", 20)
    app.addEntry("RowIDEntry", row=0, column=1, colspan=3)
    app.setEntryWidth("RowIDEntry", 80)
    app.addEntry("RecordTypeEntry", row=1, column=1, colspan=3)
    app.setEntryWidth("RecordTypeEntry", 80)
    for field_order, field_name in layout_file_lookup_table_colnames:
        label_title = field_name.replace("_", "") + "Label"
        entry_title = field_name.replace("_", "") + "Entry"
        app.addLabel(label_title, field_name.replace("_", " "), row=field_order + 2, column=0, colspan=1)
        app.setLabelAlign(label_title, 'left')
        app.setLabelWidth(label_title, 20)
        if field_name == 'Tag':
            values = ['Main', 'Tax', 'PCR', 'Land', 'Building', 'Value',
                      'Residential', 'Commercial', 'Other']
            app.addTickOptionBox(entry_title, values, row=field_order + 2, column=1, colspan=3)
            app.setOptionBoxWidth(entry_title, 80)
        else:
            app.addEntry(entry_title, row=field_order + 2, column=1, colspan=3)
            app.setEntryWidth(entry_title, 80)
        if field_name.lower().startswith("config"):
            app.addButton("Browse config file", update_layout_file_lookup_fields, row=field_order + 2, column=4)
            app.addButton("Open config file", update_layout_file_lookup_fields, row=field_order + 2, column=5)
        elif field_name.lower().startswith("original"):
            app.addButton("Browse layout file", update_layout_file_lookup_fields, row=field_order + 2, column=4)
            app.addButton("Open layout file", update_layout_file_lookup_fields, row=field_order + 2, column=5)
    app.disableEntry("RowIDEntry")
    app.disableEntry("RecordTypeEntry")
    app.disableEntry("FileIDEntry")
    app.disableEntry("ByteLengthEntry")
    app.disableEntry("NumberOfFieldsEntry")
    app.setSticky("ew")
    app.addButtons(["OK", "Cancel"], update_layout_file_lookup_fields, colspan=5)
    app.setButtonWidth("OK", 20)
    app.setButtonFg("OK", "white")
    app.setButtonBg("OK", "green")
    app.setButtonFg("Cancel", "white")
    app.setButtonBg("Cancel", "black")
    app.stopLabelFrame()
    app.stopSubWindow()
    app.hideSubWindow('View/Add/Edit Record')

def reset_subwindow_input_fields():
    """Reset the subwindow for layout file registration input"""
    layout_file_lookup_table_colnames = list_all_columns(cursor=None, dbname='tools',
                                                         schema='onestopshop', table='layout_file_lookup',
                                                         db_login=db_login)
    for field_order, field_name in layout_file_lookup_table_colnames:
        if field_name == 'Tag':
            optionboxname = field_name.replace('_', '') + "Entry"
            values = app.getOptionBox(optionboxname)
            for k, v in values.items():
                app.setOptionBox(optionboxname, k, value=False)
        else:
            app.setEntry(field_name.replace("_", "") + "Entry", "")

# ======================================================================================================================
# Utility/helper functions
# ======================================================================================================================
def update_meter():
    """update status bar using the global variable"""
    global all_sources, current_batch, batch_size, currentBatchComplete, failed_files, click_move_to_county_binder
    app.setMeter("progress", percentComplete)
    index = 0
    for FIPS, info in current_batch.items():
        try:
            app.setMeter("progress{0}".format(index), info['percentComplete'])
        except appjar.ItemLookupError:
            pass
        index = index + 1
    currentBatchComplete = (len(current_batch) > 0) & (len([FIPS for FIPS, info in current_batch.items()
                                                            if info['percentComplete'] < 100]) == 0)
    if currentBatchComplete and len(all_sources) > 0:
        current_batch = {}
        for i in range(batch_size):
            try:
                temp = all_sources.popitem()
                current_batch[temp[0]] = temp[1]
            except KeyError:
                break
        update_status_window(batch_size)
        simultaneous_batch_upload(current_batch)
    elif len(all_sources) == 0 and len(current_batch) > 0 and currentBatchComplete:
        current_batch = {}
        if len(failed_files) > 0:
            file_str = "\n".join([k + ": " + ", ".join(v) for k, v in failed_files.items()])
            message = "Upload Finished! The following file(s) are excluded: \n{0}\n\n " \
                      "Please make sure that all source files MUST be standardized correctly. Please review them!".format(file_str)
            app.infoBox("Bad Files Detected!", message, parent=None)
        else:
            app.infoBox("Files Uploaded Successfully!", "Files Uploaded Successfully!")
        app.hideSubWindow("Uploading...")
        reset_upload_screen()

def reset_upload_screen():
    """Reset Upload Screen to empty entries"""
    app.setCheckBox("Empty Schema?", ticked=False)
    app.setCheckBox("Easy Upload", ticked=False)
    app.setCheckBox("Statewide Counties", ticked=False)
    app.setEntry("fipsEnt", "")
    app.setEntry("sourcePathEnt", "")
    app.hideLabel("current_file")
    app.hideMeter("progress")

def simultaneous_batch_upload(batch):
    """simultaneously upload from multiple source folders"""
    for fips, info in batch.items():
        source_path = info['upload_path']
        if is_valid_fips(fips) and os.path.exists(source_path) and os.path.isdir(source_path):
            threadObj = threading.Thread(target=upload_source, args=(fips, source_path, 2))
            threadObj.start()

def preload_source_file_path():
    """construct all source file paths and return number of batches"""
    global all_sources, current_batch, batch_size
    all_sources = {}
    user = os.environ["USERNAME"]
    local_folder = r'C:\Users\{0}\Desktop\ICR - Move to Network'.format(user)
    county_folders = [folder_name for folder_name in os.listdir(local_folder)
                      if os.path.isdir(os.path.join(local_folder, folder_name))]
    for county_folder in county_folders:
        try:
            county_fips, county_name, county_state, _ = county_folder.split("_")
            source_path = os.path.join(local_folder, county_folder, 'Converted')
            all_sources[county_fips] = {'upload_path': source_path, 'percentComplete': 0}
        except ValueError:
            print("Invalid County Folder: {0}".format(county_folder))
    all_sources = {fips: all_sources[fips] for fips in sorted(all_sources, reverse=True)}
    num_batches = int(math.ceil(len(all_sources) / batch_size))
    current_batch = {}
    for i in range(batch_size):
        try:
            temp = all_sources.popitem()
            current_batch[temp[0]] = temp[1]
        except KeyError:
            break
    return num_batches

def fetch_source_path():
    """construct all source file paths and return number of batches and files causing problems"""
    global all_sources, current_batch, batch_size
    FIPS = app.getEntry('fipsEnt')
    fips_codes = FIPS.replace(' ', '').split(',')
    all_sources = {}
    counties_upload, invalid_fips = search_county_names(fips_codes)
    irregular_county_folders = []
    unstandardized_counties = []
    for county in counties_upload:
        county_path = os.path.join(county_binder_path, county['State'], county['County'])
        if os.path.exists(county_path) and os.path.isdir(county_path):
            all_editions = [int(edition) for edition in os.listdir(county_path) if is_number(edition)]
            if len(all_editions) > 0:
                latest_edition = str(max(all_editions))
                county_subfolder_name = "_".join([county['FIPS'], county['County'], county['State'], latest_edition])
                source_folder_path = os.path.join(county_binder_path, county['State'], county['County'], latest_edition,
                                                  county_subfolder_name, 'Source Files')
                if os.path.exists(source_folder_path) and os.path.isdir(source_folder_path):
                    standardized_files = [file for file in os.listdir(source_folder_path)
                                          if is_standardized(os.path.join(source_folder_path, file))
                                          and file.endswith('.csv')]
                    if len(standardized_files) > 0:
                        all_sources[county['FIPS']] = {'upload_path': source_folder_path, 'percentComplete': 0}
                    else:
                        unstandardized_counties.append(county['FIPS'])
                else:
                    irregular_county_folders.append(county['FIPS'])
            else:
                irregular_county_folders.append(county['FIPS'])
        else:
            irregular_county_folders.append(county['FIPS'])
    all_sources = {fips: all_sources[fips] for fips in sorted(all_sources, reverse=True)}
    num_batches = int(math.ceil(len(all_sources) / batch_size))
    current_batch = {}
    for i in range(batch_size):
        try:
            temp = all_sources.popitem()
            current_batch[temp[0]] = temp[1]
        except KeyError:
            break
    return num_batches, irregular_county_folders, invalid_fips, unstandardized_counties

def fetch_statewide_source_path():
    """construct all source file paths and return number of batches and files causing problems"""
    global all_sources, current_batch, batch_size
    FIPS = app.getEntry('fipsEnt')
    fips_codes = FIPS.replace(' ', '').split(',')
    statewide_folder = app.getEntry('sourcePathEnt')
    if isinstance(statewide_folder, str):
        statewide_folder = statewide_folder.replace('\\', '/')
        if not statewide_folder.endswith("Source Files"):
            statewide_folder = os.path.join(statewide_folder, 'Source Files')
    if os.path.exists(statewide_folder) and os.path.isdir(statewide_folder):
        all_sources = {}
        counties_upload, invalid_fips = search_county_names(fips_codes)
        irregular_county_folders = []
        unstandardized_counties = []
        statewide_counties = [county.upper() for county in os.listdir(statewide_folder)
                              if os.path.exists(os.path.join(statewide_folder, county)) and
                              os.path.isdir(os.path.join(statewide_folder, county))]
        for county in counties_upload:
            if county['County'].upper() in statewide_counties:
                source_folder_path = os.path.join(statewide_folder, county['County'].upper())
                standardized_files = [file for file in os.listdir(source_folder_path)
                                      if is_standardized(os.path.join(source_folder_path, file))
                                      and file.endswith('.csv')]
                if len(standardized_files) > 0:
                    all_sources[county['FIPS']] = {'upload_path': source_folder_path, 'percentComplete': 0}
                else:
                    unstandardized_counties.append(county['FIPS'])
            else:
                irregular_county_folders.append(county['FIPS'])
        all_sources = {fips: all_sources[fips] for fips in sorted(all_sources, reverse=True)}
        num_batches = int(math.ceil(len(all_sources) / batch_size))
        current_batch = {}
        for i in range(batch_size):
            try:
                temp = all_sources.popitem()
                current_batch[temp[0]] = temp[1]
            except KeyError:
                break
        return num_batches, irregular_county_folders, invalid_fips, unstandardized_counties
    else:
        raise Exception('Invalid statewide folder path!')

# ======================================================================================================================
# Major Callback functions
# ======================================================================================================================
def click(button):
    """callback function when clicking the button on the main page"""
    global percentComplete, current_batch, batch_size, currentBatchCompletem, failed_files, click_move_to_county_binder
    percentComplete = 0
    if button == "Upload":
        failed_files = {}
        if app.getCheckBox("Easy Upload"):
            if app.getCheckBox("Statewide Counties"):
                try:
                    num_batches, irregular_county_folders, invalid_fips, unstandardized_counties = fetch_statewide_source_path()
                except Exception as e:
                    print(e.args[0])
                    app.errorBox("Error!", e.args[0])
                    return
            else:
                num_batches, irregular_county_folders, invalid_fips, unstandardized_counties = fetch_source_path()
            if num_batches > 0:
                if len(irregular_county_folders) > 0:
                    mess1 = "The following counties have irregular folder structures: \n{0}\n\n".format(
                        ",".join(irregular_county_folders), ",".join(invalid_fips))
                else:
                    mess1 = ""
                if len(invalid_fips) > 0:
                    mess2 = "The following FIPS code(s) are invalid: \n{0}\n\n".format(",".join(invalid_fips))
                else:
                    mess2 = ""
                if len(unstandardized_counties) > 0:
                    mess3 = "The following counties are not standardized: \n{0}\n\n".format(
                        ",".join(unstandardized_counties))
                else:
                    mess3 = ""
                message = mess1 + mess2 + mess3
                if message == "":
                    update_status_window(batch_size)
                    app.showSubWindow("Uploading...")
                    simultaneous_batch_upload(current_batch)
                else:
                    message = message + "Press YES to continue uploading other valid counties;\nPress NO to quit."
                    res = app.yesNoBox("Warning!", message, parent=None)
                    if res:
                        update_status_window(batch_size)
                        app.showSubWindow("Uploading...")
                        simultaneous_batch_upload(current_batch)
            else:
                app.errorBox("Error!", "All counties you entered either have invalid FIPS codes or "
                                       "have irregular folder structures. Please double check or uncheck 'Easy Upload' "
                                       "to upload regularly!")
        else:
            app.showLabel("current_file")
            app.showMeter("progress")
            app.setMeter("progress", 0)
            threadObj = threading.Thread(target=upload_source)
            threadObj.start()
    elif button == "Submit":
        failed_files = {}
        app.hideMessage('mess_dev1')
        app.hideMessage('mess_dev2')
        app.hideMessage('mess_dev3')
        app.hideMessage('mess_dev4')
        thread1 = threading.Thread(target=upload_source_dev)
        thread1.start()
    elif button == "Browse":
        selected_source = app.directoryBox(title="Choose A Source Folder",
                                           dirName=county_binder_path, parent=None)
        if selected_source is not None:
            app.setEntry("sourcePathEnt", selected_source)

def press(btn):
    """Callback function in Layout File Lookup"""
    global table_filters
    if btn == "Apply filters" or btn == "Reset":
        conn = connect_to_sql_server(**db_login, quiet_mode=True)
        cursor = conn.cursor()
        if len(table_filters) > 0:
            conditions = "where {0}".format(" AND ".join(table_filters))
        else:
            conditions = ""
        cursor.execute("select * from tools.onestopshop.layout_file_lookup {0}".format(conditions))
        data = cursor.fetchall()
        data = [["Saved"]+list(line) for line in data]
        app.replaceAllTableRows("layoutfilelist", data=data)
    elif btn == "Add to filter":
        search_type = app.getOptionBox("Search").replace(" ", "_")
        search_key = app.getEntry("SearchKey")
        if search_key != "" and ("length" in search_type.lower() or "number" in search_type.lower()):
            table_filters.append("{0} = '{1}'".format(search_type, search_key))
            app.setMessage("filter_summary", "Filter(s): " + " | ".join(table_filters))
        elif search_key != "":
            table_filters.append("{0} like '%{1}%'".format(search_type, search_key))
            app.setMessage("filter_summary", "Filter(s): " + " | ".join(table_filters))
    elif btn == "Clear all filters":
        table_filters = []
        app.setMessage("filter_summary", "Filter(s): ")
    elif btn == "Save All Changes":
        conn = connect_to_sql_server(**db_login, quiet_mode=True)
        cursor = conn.cursor()
        rowcounts = app.getTableRowCount("layoutfilelist")
        for i in range(rowcounts):
            row_data = app.getTableRow("layoutfilelist", i)
            if row_data[0] == "New":
                insert_to_sql_table(cursor=cursor, dbname='tools', schema='onestopshop',
                                    table='layout_file_lookup', records=row_data[1:])
            elif row_data[0] == "Modified":
                colnames = list_all_columns(cursor=cursor, dbname='tools', schema='onestopshop', table='layout_file_lookup')
                query = "UPDATE tools.onestopshop.layout_file_lookup SET {0} WHERE File_ID = '{1}'".format(
                    ",".join(["{0}='{1}'".format(pair[0][1], pair[1]) for pair in zip(colnames[1:], row_data[2:])]),
                    row_data[1]
                )
                cursor.execute(query)
        conn.commit()
        conn.close()
        press("Apply filters")
    elif is_number(btn):
        reset_subwindow_input_fields()
        selected_row = [btn] + app.getTableRow("layoutfilelist", int(btn))
        field_names = list_all_columns(cursor=None, dbname='tools', schema='onestopshop', table='layout_file_lookup',
                                       db_login=db_login)
        field_names = ["Row_ID", "Record_Type"] + [field[1] for field in sorted(field_names, key=lambda x: x[0])]
        for field_name, field_content in zip(field_names, selected_row):
            if field_name == 'Tag':
                if field_content != '':
                    selected_tag = field_content.replace(" ", "").split(",")
                    for tag in selected_tag:
                        app.setOptionBox(field_name.replace('_', '') + "Entry", tag, value=True)
            else:
                app.setEntry(field_name.replace('_', '') + "Entry", field_content)
        if app.getEntry("RecordTypeEntry") == 'Saved':
            app.setEntry("RecordTypeEntry", 'Modified')
        app.showSubWindow('View/Add/Edit Record')
    elif btn == "Add New Row":
        reset_subwindow_input_fields()
        row_count = app.getTableRowCount("layoutfilelist")
        app.setEntry("RowIDEntry", row_count)
        app.setEntry("RecordTypeEntry", 'New')
        app.setEntry("FileIDEntry", datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))
        app.showSubWindow('View/Add/Edit Record')

def menu_press(btn):
    """Callback funtion when clicking on menu bar"""
    if btn == "About sourceManager...":
        bitbucket_url = "https://bitbucket.zgtools.net/projects/CDA/repos/sourcemanager/browse"
        webbrowser.open(bitbucket_url)
    elif btn == "Close":
        app.stop()

def update_layout_file_lookup_fields(btn):
    """Callback function for sub-window for editing record in Layout File Lookup"""
    if btn == "Cancel":
        app.hideSubWindow('View/Add/Edit Record')
    elif btn == "Browse config file":
        selected_file = app.openBox(title="Choose a file", dirName=county_binder_path,
                                    fileTypes=[('config', '*.cfg'), ('text', '*.txt')], asFile=False, parent=None)
        app.setEntry("ConfigurationLocationEntry", selected_file.replace("/","\\"))
    elif btn == "Open config file":
        selected_file = app.getEntry("ConfigurationLocationEntry")
        if os.path.exists(selected_file):
            os.startfile(selected_file)
    elif btn == "Browse layout file":
        selected_file = app.openBox(title="Choose a file", dirName=county_binder_path,
                                    fileTypes=None, asFile=False, parent=None)
        app.setEntry("OriginalLayoutLocationEntry", selected_file.replace("/","\\"))
    elif btn == "Open layout file":
        selected_file = app.getEntry("OriginalLayoutLocationEntry")
        if os.path.exists(selected_file):
            os.startfile(selected_file)
    elif btn == "OK":
        field_names = list_all_columns(cursor=None, dbname='tools', schema='onestopshop', table='layout_file_lookup',
                                       db_login=db_login)
        field_names = ["Row_ID", "Record_Type"] + [field[1] for field in sorted(field_names, key=lambda x: x[0])]
        new_data = []
        for field_name in field_names:
            if field_name == "Tag":
                allOptions = app.getOptionBox(field_name.replace('_', '') + "Entry")
                tags = ",".join([option for option, checked in allOptions.items() if checked])
                new_data.append(tags)
            else:
                new_data.append(app.getEntry(field_name.replace('_', '') + "Entry"))
        config_file_location = new_data[11]
        if os.path.exists(config_file_location) and os.path.isfile(config_file_location):
            try:
                with open(config_file_location, 'r') as f:
                    config_info = f.readlines()
                extracted_config = [field.strip().split(', ') for field in config_info]
                char_bytes = sum([int(x[0]) for x in extracted_config])
                field_count = len(extracted_config)
                new_data[8] = char_bytes
                new_data[9] = field_count
                app.hideSubWindow('View/Add/Edit Record')
                row_count = app.getTableRowCount("layoutfilelist")
                if int(new_data[0]) < row_count:
                    app.replaceTableRow("layoutfilelist", int(new_data[0]), new_data[1:])
                else:
                    app.addTableRow("layoutfilelist", new_data[1:])
            except:
                pass

def show_folder_path_entries():
    copy_tables_checkbox = app.getCheckBox("Copy ALL source file table(s) from src")
    lookup_checkbox = app.getCheckBox("Create Lookup Tables")
    upload_checkbox = app.getCheckBox("Supplemental file(s) from local")
    if upload_checkbox:
        app.showLabel("sourcePathLab_dev")
        app.showEntry("sourcePathEnt_dev")
        app.showButton("Submit")
    else:
        app.hideLabel("sourcePathLab_dev")
        app.hideEntry("sourcePathEnt_dev")
        app.clearEntry("sourcePathEnt_dev")
        app.hideMessage("mess_dev2")
        if not copy_tables_checkbox and not lookup_checkbox:
            app.hideButton("Submit")

def show_fips_entries():
    copy_tables_checkbox = app.getCheckBox("Copy ALL source file table(s) from src")
    lookup_checkbox = app.getCheckBox("Create Lookup Tables")
    upload_checkbox = app.getCheckBox("Supplemental file(s) from local")
    if copy_tables_checkbox or lookup_checkbox:
        app.showLabel("fipsLab_dev")
        app.showEntry("fipsEnt_dev")
        app.showButton("Submit")
        if lookup_checkbox:
            app.showCheckBox("Statewide")
        else:
            app.hideCheckBox("Statewide")
            app.hideMessage("mess_dev3")
            app.setCheckBox("Statewide", ticked=False)
    else:
        app.hideLabel("fipsLab_dev")
        app.hideEntry("fipsEnt_dev")
        app.clearEntry("fipsEnt_dev")
        app.hideCheckBox("Statewide")
        app.hideMessage("mess_dev1")
        app.hideMessage("mess_dev3")
        app.hideMessage('mess_dev4')
        app.setCheckBox("Statewide", ticked=False)
        if not upload_checkbox:
            app.hideButton("Submit")

def hide_path_entries():
    if app.getCheckBox("Easy Upload") and app.getCheckBox("Statewide Counties"):
        app.clearEntry("fipsEnt")
        app.setEntryMaxLength("fipsEnt", 600)
        app.showLabel("sourcePathLab")
        app.setLabel("sourcePathLab", "Statewide Folder Path: ")
        app.showEntry("sourcePathEnt")
        app.showButton("Browse")
        app.hideLabel("current_file")
        app.hideMeter("progress")
    elif app.getCheckBox("Easy Upload"):
        app.clearEntry("fipsEnt")
        app.clearEntry("sourcePathEnt")
        app.setEntryMaxLength("fipsEnt", 600)
        app.showCheckBox("Statewide Counties")
        app.hideLabel("sourcePathLab")
        app.hideEntry("sourcePathEnt")
        app.hideButton("Browse")
        app.hideLabel("current_file")
        app.hideMeter("progress")
    else:
        app.clearEntry("fipsEnt")
        app.clearEntry("sourcePathEnt")
        app.setEntryMaxLength("fipsEnt", 5)
        app.setCheckBox("Statewide Counties", ticked=False, callFunction=False)
        app.hideCheckBox("Statewide Counties")
        app.setLabel("sourcePathLab", "Source File Folder Path: ")
        app.showLabel("sourcePathLab")
        app.showEntry("sourcePathEnt")
        app.showButton("Browse")

# ======================================================================================================================
# Main Function
# ======================================================================================================================
def sourceManager():
    """Build GUI for sourceManager"""
    global app
    bgColor = "#EBF5FB"
    app = gui("sourceManager", "800x500")
    app.winIcon = None
    app.setBg(bgColor)
    app.setButtonFont(size=14, family="Segoe UI", weight="bold")
    app.setLabelFont(size=12, family="Segoe UI")
    # Menu bar
    fileMenus = ["About sourceManager...", "-",
                 "Close"]
    app.addMenuList("Mode", fileMenus, menu_press)
    app.startTabbedFrame("sourceManager")
    # =====================================================================================================
    # File Upload
    app.startTab("Upload")
    app.setTabBg("sourceManager", "Upload", bgColor)
    app.startLabelFrame("Source Details", colspan=3)
    app.setSticky("ew")
    app.addCheckBox("Empty Schema?", 0, 0)
    app.addCheckBox("Easy Upload", 1, 0)
    app.setCheckBoxChangeFunction("Easy Upload", hide_path_entries)
    app.addCheckBox("Statewide Counties", 1, 1)
    app.setCheckBoxChangeFunction("Statewide Counties", hide_path_entries)
    app.hideCheckBox("Statewide Counties")
    app.addLabel("fipsLab", "FIPS: ", 2, 0)
    app.addEntry("fipsEnt", 2, 1)
    app.setEntryMaxLength("fipsEnt", 5)
    app.addLabel("sourcePathLab", "Source File Folder Path: ", 3, 0)
    app.addEntry("sourcePathEnt", 3, 1)
    app.setLabelWidth("fipsLab", 20)
    app.setLabelWidth("sourcePathLab", 20)
    app.setEntryWidth("fipsEnt", 50)
    app.setEntryWidth("sourcePathEnt", 50)
    app.addButtons(["Browse"], click, 3, 2)
    app.addButtons(["Upload"], click, 4, 0, colspan=3)
    app.setButtonFg("Upload", "white")
    app.setButtonBg("Upload", "green")
    app.stopLabelFrame()
    # Upload status bar
    app.addLabel("current_file", "File Upload Status: ", 3, 0)
    app.setLabelAlign('current_file', 'left')
    app.addMeter("progress", 3, 1)
    app.setMeterFill("progress", "green")
    app.hideLabel("current_file")
    app.hideMeter("progress")
    app.registerEvent(update_meter)
    app.stopTab()
    # Customize Tab
    app.startTab("Customize")
    app.setTabBg("sourceManager", "Customize", bgColor)
    app.startLabelFrame("Customize your schema", colspan=2)
    app.setSticky("ew")
    app.setFont(11)
    message_customize = "*Notes: Multiple FIPS codes need to be separated by comma."
    app.addLabel("fipsLab_notes", message_customize, 0, 0, colspan=2)
    app.getLabelWidget('fipsLab_notes').config(font="Calibri 11")
    app.setLabelFg('fipsLab_notes', 'red')
    app.addCheckBox("Copy ALL source file table(s) from src", 1, 0, colspan=2)
    app.addCheckBox("Create Lookup Tables", 2, 0)
    app.addCheckBox("Statewide", 2, 1)
    app.addCheckBox("Supplemental file(s) from local", 3, 0, colspan=2)
    app.setCheckBoxChangeFunction("Supplemental file(s) from local", show_folder_path_entries)
    app.setCheckBoxChangeFunction("Copy ALL source file table(s) from src", show_fips_entries)
    app.setCheckBoxChangeFunction("Create Lookup Tables", show_fips_entries)
    app.addLabel("fipsLab_dev", "FIPS: ", 5, 0)
    app.addEntry("fipsEnt_dev", 5, 1)
    app.addLabel("sourcePathLab_dev", "Source File Folder Path: ", 6, 0)
    app.addEntry("sourcePathEnt_dev", 6, 1)
    app.addButtons(["Submit"], click, 7, 0, colspan=3)
    # Label Alignment
    app.setLabelAlign('fipsLab_notes', 'left')
    app.setLabelAlign('fipsLab_dev', 'left')
    app.setLabelAlign('sourcePathLab_dev', 'left')
    app.setLabelWidth("fipsLab_dev", 20)
    app.setLabelWidth("sourcePathLab_dev", 20)
    app.setEntryWidth("fipsEnt_dev", 70)
    app.setEntryWidth("sourcePathEnt_dev", 70)
    # Hide label and entries
    app.hideLabel("fipsLab_dev")
    app.hideEntry("fipsEnt_dev")
    app.hideLabel("sourcePathLab_dev")
    app.hideEntry("sourcePathEnt_dev")
    app.hideCheckBox("Statewide")
    app.hideButton("Submit")
    # Message
    app.addMessage('mess_dev', "Database Cleaning...", colspan=3)
    app.setMessageAlign('mess_dev', 'left')
    app.setMessageWidth("mess_dev", 600)
    app.setMessageFg('mess_dev', 'black')
    app.hideMessage('mess_dev')
    app.addEmptyMessage('mess_dev1', colspan=3)
    app.setMessageAlign('mess_dev1', 'left')
    app.setMessageWidth("mess_dev1", 600)
    app.setMessageFg('mess_dev1', 'green')
    app.addEmptyMessage('mess_dev2', colspan=3)
    app.setMessageAlign('mess_dev2', 'left')
    app.setMessageWidth("mess_dev2", 600)
    app.setMessageFg('mess_dev2', 'blue')
    app.addMessage('mess_dev3', "Created 3 lookup tables!", colspan=3)
    app.setMessageAlign('mess_dev3', 'left')
    app.setMessageWidth("mess_dev3", 600)
    app.setMessageFg('mess_dev3', 'black')
    app.hideMessage('mess_dev3')
    app.addMessage('mess_dev4', "Created County Groups and File Summary tables", colspan=3)
    app.setMessageAlign('mess_dev4', 'left')
    app.setMessageWidth("mess_dev4", 600)
    app.setMessageFg('mess_dev4', 'black')
    app.hideMessage('mess_dev4')
    app.stopLabelFrame()
    app.stopTab()
    # =====================================================================================================
    # Layout File Registration
    app.startTab("Layout File Search")
    app.setTabBg("sourceManager", "Layout File Search", bgColor)
    layout_file_lookup_table_colnames = list_all_columns(cursor=None, dbname='tools',
                                                         schema='onestopshop', table='layout_file_lookup',
                                                         db_login=db_login)
    layout_file_lookup_table_colnames = sorted(layout_file_lookup_table_colnames, key=lambda x: x[0])
    layout_file_lookup_table_colnames_display = [colname[1].replace("_", " ")
                                                 for colname in layout_file_lookup_table_colnames]
    app.startLabelFrame("Layout File Search")
    app.addMessage("filter_summary", "Filter(s): ", row=0, column=0, colspan=4)
    app.setMessageAlign('filter_summary', 'left')
    app.setMessageWidth("filter_summary", 750)
    app.setMessageFg('filter_summary', 'green')
    app.addLabelOptionBox("Search", layout_file_lookup_table_colnames_display, row=1, column=0)
    app.addEntry("SearchKey", row=1, column=1)
    app.addButtons(["Add to filter", "Clear all filters", "Apply filters"], press, 1, 2, colspan=2)
    app.stopLabelFrame()
    app.addTable("layoutfilelist", data=[["Record Type"] + layout_file_lookup_table_colnames_display],
                 addRow=None,
                 disabledEntries=[0, 1, 6, 7],
                 showMenu=False,
                 action=press,
                 actionButton="View/Edit")
    app.addButtons(["Add New Row", "Save All Changes", "Reset"], press)
    app.stopTab()
    app.stopTabbedFrame()
    # =====================================================================================================
    # sub windows
    create_layout_file_input_box(layout_file_lookup_table_colnames)
    create_status_window(batch_size)
    app.go()

# ======================================================================================================================
# Main Script
# ======================================================================================================================
if __name__ == '__main__':
    multiprocessing.freeze_support()
    # Global variables
    rds_server, login_name, login_pwd = get_rds_credential()
    db_login = {'server': rds_server, 'dbname': 'src', 'username': login_name, 'password': login_pwd}
    county_binder_path = r"\\IRV-WIN-FIL-001\Data Services Assessment Team\County Binders"
    table_filters = []
    percentComplete = 0
    batch_size = 5
    all_sources = {}
    current_batch = {}
    failed_files = {}
    currentBatchComplete = False
    app = None
    # main function
    sourceManager()