from .util import *
import time

# ======================================================================================================================
# County Comparison
# ======================================================================================================================
def export_target_fips(cursor, fips_code=None, state_prefix=None):
    """Export a dictionary of all fips codes in the same state: {FIPS: [County Name, State Code]}"""
    try:
        if fips_code is not None and is_valid_fips(fips_code):
            prefix = str(fips_code)[:2]
        elif fips_code is not None:
            raise ValueError
        elif state_prefix is not None and len(str(state_prefix)) == 2 and is_number(state_prefix):
            prefix = state_prefix
        elif state_prefix is not None:
            raise ValueError
        else:
            raise ValueError
        sql_query = "select * from ZDomainData.xref.utMasterFIPS where StndCode like '{0}%'".format(prefix)
        cursor.execute(sql_query)
        export = cursor.fetchall()
        if len(export) == 0:
            raise ValueError
        else:
            export = {fips: [county, state] for fips, county, state in export}
            return export
    except ValueError:
        print("Invalid FIPS: {0}".format(fips_code))

def get_county_name(cursor, fips):
    sql_query = "select CountyName, StateCode from ZDomainData.xref.utMasterFIPS where StndCode = '{0}'".format(fips)
    cursor.execute(sql_query)
    export = cursor.fetchall()
    return export[0]

def get_statewide_fips(cursor, fips_code):
    """Get statewide fips that assigned previously"""
    query = "select statewide_fips, group_type from tools.onestopshop.county_grouping " \
            "where fips = '{0}'".format(fips_code)
    cursor.execute(query)
    result = cursor.fetchall()
    if len(result) > 0:
        return result[0]

def list_all_groups(cursor, state_prefix, target_fips):
    """list all existing fips codes that will be used for comparison"""
    query = extract_query(r"resources\Sample Counties for Comparison.txt").format(state_prefix, target_fips)
    cursor.execute(query)
    result = cursor.fetchall()
    result_dict = {f: (s, t) for s, t, m, f in result}
    return result_dict

def get_next_statewide_code(cursor, statewide_prefix):
    """export next available statewide fips in the state"""
    query = "select max(statewide_fips) from tools.onestopshop.county_grouping " \
            "where group_type = 'Statewide' and statewide_fips like '{0}%'".format(statewide_prefix)
    cursor.execute(query)
    result = cursor.fetchall()
    if result[0][0] is not None:
        new_statewide_code = str(int(result[0][0]) + 2)
    else:
        new_statewide_code = str(int(statewide_prefix[:2]) * 1000 + 2)
    if len(new_statewide_code) < 5:
        new_statewide_code = "0" + new_statewide_code
    while is_valid_fips(new_statewide_code):
        new_statewide_code = str(int(new_statewide_code) + 2)
        if len(new_statewide_code) < 5:
            new_statewide_code = "0" + new_statewide_code
    return new_statewide_code

def source_file_layout(cursor, fips_codes_list):
    """Output source file layouts for input FIPS code(s)"""
    fips_code_str = ",".join(["'{0}'".format(code) for code in fips_codes_list])
    sql_query = extract_query(r"resources\Source Table Columns.txt").format(fips_code_str)
    cursor.execute(sql_query)
    data = cursor.fetchall()
    output = {}
    for FIPS, filename, _, colname in data:
        try:
            output[(FIPS, filename)].append(colname)
        except KeyError:
            output[(FIPS, filename)] = [colname]
    return output

def compare_two_sets(set1, set2):
    """Compare two sets of values and return the ratio between intersection and union"""
    intersect_set = len(set1.intersection(set2))
    union_set = len(set1.union(set2))
    r = intersect_set/union_set
    return r

def compare_two_lists_of_sets(list1, list2):
    """Compare two lists of sets of values and return a similarity score"""
    if len(list1) == 0 or len(list2) == 0:
        similarity = 0
    else:
        matched_rates = []
        for set1 in list1:
            rates = []
            for set2 in list2:
                r = compare_two_sets(set1, set2)
                rates.append(r)
            matched_rates.append(max(rates))
        similarity = sum(matched_rates)/max([len(list1), len(list2)])
    return similarity

def county_layout_summary(layouts):
    """Construct summary table: FIPS, File Name, Number of fields, and concatenation of all fields"""
    file_summary = []
    for k, v in layouts.items():
        file_summary.append((k[0], k[1], str(len(v)), ",".join(v)))
    return file_summary

def assign_statewide_codes(county_groups, statewide_prefix):
    """Assign statewide FIPS codes to grouped counties"""
    statewide_index = 1
    statewide_prefix = int(statewide_prefix)
    new_output = {}
    for group_num, counties in county_groups.items():
        if len(counties) > 1:
            valid_statewide_code = False
            while not valid_statewide_code:
                statewide_fips = str(statewide_prefix * 1000 + statewide_index * 2)
                statewide_index = statewide_index + 1
                if len(statewide_fips) < 5:
                    statewide_fips = '0' + statewide_fips
                if not is_valid_fips(statewide_fips):
                    valid_statewide_code = True
                    new_output[(statewide_fips, 'Statewide')] = counties
        else:
            statewide_fips = str(counties[0][0])
            new_output[(statewide_fips, 'Individual')] = counties
    return new_output

def group_counties(cursor, fips_codes_list, threshold=0.8):
    """Main function for grouping counties: find grouping inside given fips list"""
    layouts = source_file_layout(cursor, fips_codes_list)
    county_field_sets = {}
    for k, v in layouts.items():
        fips_code = k[0]
        column_headers = set(v)
        try:
            county_field_sets[fips_code].append(column_headers)
        except KeyError:
            county_field_sets[fips_code] = [column_headers]
    county_groups = {}
    county_field_sets_copy2 = county_field_sets.copy()
    county_field_sets_copy = county_field_sets.copy()
    # Step 1: Exact Match
    while county_field_sets_copy:
        fips, field_set = county_field_sets_copy.popitem()
        exact_match_list = []
        for k, v in county_field_sets_copy.items():
            r = compare_two_lists_of_sets(field_set, v)
            if r == 1:
                exact_match_list.append((k, 'Exact'))
        if len(exact_match_list) > 0:
            exact_match_list.append((fips, 'Exact'))
            for i, _ in exact_match_list:
                county_field_sets.pop(i)
                if i != fips:
                    county_field_sets_copy.pop(i)
            if len(county_groups) == 0:
                new_group_index = 0
            else:
                new_group_index = max(county_groups) + 1
            county_groups[new_group_index] = exact_match_list
    # Step 2: Approximate Match
    exact_format_captured = {k: [(v[0][0], county_field_sets_copy2[v[0][0]])]
                             for k, v in county_groups.items() if v[0][1] == 'Exact'}
    while county_field_sets:
        approx_format_captured = {k: [(fips, county_field_sets_copy2[fips]) for fips, match_type in v]
                                  for k, v in county_groups.items() if v[0][1] == 'Approx'}
        format_captured = {**exact_format_captured, **approx_format_captured}
        fips, field_set = county_field_sets.popitem()
        scores = {group: max([0]+[compare_two_lists_of_sets(field_set, layout) for _, layout in layouts])
                  for group, layouts in format_captured.items()}
        if len(scores) == 0:
            matched_group = None
            max_score = 0
        else:
            matched_group = sorted(scores, key=lambda key: scores[key], reverse=True)[0]
            max_score = scores[matched_group]
        if max_score >= threshold:
            county_groups[matched_group].append((fips, 'Approx'))
        else:
            if len(county_groups) == 0:
                new_group_index = 0
            else:
                new_group_index = max(county_groups) + 1
            county_groups[new_group_index] = [(fips, 'Approx')]
    return county_groups

def group_finder(cursor, fips_codes):
    """Group the entire state and assign statewide fips"""
    fips_state_group = {}
    for fips in fips_codes:
        if is_valid_fips(fips):
            key = str(fips)[:2]
            try:
                fips_state_group[key].append(fips)
            except KeyError:
                fips_state_group[key] = [fips]
    if len(fips_state_group) > 0:
        target_counties = [export_target_fips(cursor, state_prefix=prefix) for prefix in list(fips_state_group.keys())]
        county_name_dict = {}
        for i in target_counties:
            county_name_dict = {**county_name_dict, **i}
        target_fips_list = [list(county_set.keys()) for county_set in target_counties]
        final_county_groups = {}
        for fips_codes_list in target_fips_list:
            statewide_prefix = fips_codes_list[0][:2]
            print(statewide_prefix)
            county_groups = group_counties(cursor, fips_codes_list, threshold=0.8)
            county_groups = assign_statewide_codes(county_groups, statewide_prefix)
            final_county_groups = {**final_county_groups, **county_groups}
        return final_county_groups, county_name_dict

def find_match_county(cursor, fips_codes_list, target_fips, threshold=0.8):
    """find a match in the given fips codes list"""
    layouts = source_file_layout(cursor, fips_codes_list + [target_fips])
    county_field_sets = {}
    for k, v in layouts.items():
        fips_code = k[0]
        column_headers = set(v)
        try:
            county_field_sets[fips_code].append(column_headers)
        except KeyError:
            county_field_sets[fips_code] = [column_headers]
    # Step 1: Exact Match
    target_field_set = county_field_sets.pop(target_fips)
    for k, v in county_field_sets.items():
        r = compare_two_lists_of_sets(target_field_set, v)
        if r == 1:
            return [k, 'Exact']
    # Step 2: Approximate Match
    scores = {k: compare_two_lists_of_sets(target_field_set, v) for k, v in county_field_sets.items()}
    if len(scores) == 0:
        matched_fips = None
        max_score = 0
    else:
        matched_fips = sorted(scores, key=lambda key: scores[key], reverse=True)[0]
        max_score = scores[matched_fips]
    if max_score >= threshold:
        return [matched_fips, 'Approx']
    return [None, None]

def classify(cursor, target_fips):
    """Main function for classifying one county"""
    try:
        county_name, state_code = get_county_name(cursor, target_fips)
        state_prefix = target_fips[:2]
        sample_counties = list_all_groups(cursor, state_prefix, target_fips)
        sample_fips = list(sample_counties.keys())
        matched_fips, matched_type = find_match_county(cursor, sample_fips, target_fips)
        if matched_fips is None and matched_type is None:
            new_records = [[target_fips, 'Individual', target_fips, county_name, state_code, 'Approx']]
            return new_records
        else:
            statewide_fips, group_type = sample_counties[matched_fips]
            if group_type == 'Statewide':
                new_records = [[statewide_fips, group_type, target_fips, county_name, state_code, matched_type]]
                return new_records
            else:
                matched_county_name, matched_state_code = get_county_name(cursor, matched_fips)
                new_statewide_fips = get_next_statewide_code(cursor, state_prefix)
                new_records = [[new_statewide_fips, 'Statewide', matched_fips, matched_county_name, matched_state_code, matched_type],
                               [new_statewide_fips, 'Statewide', target_fips, county_name, state_code, matched_type]]
                return new_records
    except IndexError:
        print("Invalid FIPS")
        return []
    except KeyError:
        print("No Source Files Found for {0}! Please Upload source files first!".format(target_fips))
        return []

def move_single_statewide_to_individual(cursor):
    """Move any county are individual but labeled as statewide"""
    query = "select min(fips), min(county), min(state) from tools.onestopshop.county_grouping " \
            "where group_type = 'Statewide' group by statewide_fips having count(*) = 1"
    cursor.execute(query)
    fips = cursor.fetchall()
    if len(fips) > 0:
        result = [[code[0], 'Individual', code[0], code[1], code[2], 'Approx'] for code in fips]
        return result
    else:
        return fips

def create_county_grouping_table(cursor, dbname, schema, table_name, groups, county_info):
    """Create county_grouping table to display final county grouping"""
    result = []
    for group_num, county_set in groups.items():
        for county, match_type in county_set:
            result.append([str(group_num[0]), str(group_num[1]), str(county),
                           county_info[str(county)][0], county_info[str(county)][1],
                           str(match_type)])
    drop_sql_table(cursor, dbname, schema, table_name)
    create_sql_table(cursor, dbname, schema, table_name, columns=['Statewide_FIPS', 'Group_Type', 'FIPS',
                                                                  'County', 'State', 'Match_Type'])
    insert_to_sql_table(cursor, dbname, schema, table_name, records=result)
    print("... {2} table is created in {0}.{1}!".format(dbname, schema, table_name))

def update_county_grouping_table(cursor, dbname, schema, table_name, new_records):
    """Update county_grouping table with new records"""
    if len(new_records) > 0:
        fips_codes = ",".join(["'{0}'".format(row[2]) for row in new_records])
        query = "delete from {0}.{1}.{2} where fips in ({3})".format(dbname, schema, table_name, fips_codes)
        cursor.execute(query)
        insert_to_sql_table(cursor, dbname, schema, table_name, records=new_records)

def generate_county_grouping_table():
    """Generate/re-generate county_grouping table in tools.onestopshop"""
    start_time = time.time()
    rds_server, login_name, login_pwd = get_rds_credential()
    db_login = {'server': rds_server, 'dbname': 'src', 'username': login_name, 'password': login_pwd}
    conn_rds = connect_to_sql_server(**db_login, quiet_mode=True)
    cursor_rds = conn_rds.cursor()
    sample_counties = ['02013', '01001', '05001', '04001', '06001', '08001', '09001', '11001', '10001', '12001',
                       '13001', '66010', '15001', '19001', '16001', '17001', '18001', '20001', '21001', '22001',
                       '25001', '24001', '23001', '26001', '27001', '29001', '28001', '30001', '37001', '38001',
                       '31001', '33001', '34001', '35001', '32001', '36001', '39001', '40001', '41001', '42001',
                       '72001', '44001', '45001', '46003', '47001', '48001', '49001', '51001', '78010', '50001',
                       '53001', '55001', '54001', '56001']
    sample_counties = sorted(sample_counties)
    g, d = group_finder(cursor_rds, sample_counties)
    dbname = 'tools'
    schema_name = 'onestopshop'
    create_county_grouping_table(cursor_rds, dbname, schema_name, 'county_grouping', g, d)
    conn_rds.commit()
    conn_rds.close()
    print("--- %s seconds ---" % (round(time.time() - start_time, 2)))

def statewide_classifier(target_fips, cursor=None, update_database=False):
    """classify a county to be statewide or not and update county_grouping table with new grouping"""
    if cursor is None:
        rds_server, login_name, login_pwd = get_rds_credential()
        db_login = {'server': rds_server, 'dbname': 'src', 'username': login_name, 'password': login_pwd}
        conn_rds = connect_to_sql_server(**db_login, quiet_mode=True)
        cursor_rds = conn_rds.cursor()
    else:
        cursor_rds = cursor
    dbname = 'tools'
    schema_name = 'onestopshop'
    new_records = classify(cursor_rds, target_fips)
    new_records = new_records + move_single_statewide_to_individual(cursor_rds)
    if update_database:
        update_county_grouping_table(cursor_rds, dbname, schema_name, 'county_grouping', new_records)
    else:
        return new_records
    if cursor is None:
        conn_rds.commit()
        conn_rds.close()

if __name__ == '__main__':
    statewide_classifier(target_fips='48231', update_database=True)