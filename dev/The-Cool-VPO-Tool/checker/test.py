import os
current_dir = os.getcwd()
vpo = 'I809002CR'



def update_test_time(vpo):
    print("Updating test time")
    #edit_and_run_cb_script(cb_template, vpo)
    tp_data = parse_itime_file(itime_file)
    #total_time = calculate_total_itime_permodule(tp_data)
    print("Saved")

####Methods for test time tool####
itime_file = r"{}\static\checker\temp_files\itime.csv".format(current_dir)
cb_template = r"{}\static\checker\temp_files\clx_itime_summary_template.acs".format(current_dir)


# total_time[team][module] = total time per module
# total_time[team][team_total] = total time per team
# example:
# total_time[CACHE][ARR_CACHE] = 112817.0527
# total_time[CACHE][CACHE_total] = 113194.302


def edit_and_run_cb_script(template, lot_name):
    '''edit cb script to generate itime csv file'''
    with open(r"{}\static\checker\temp_files\tempcb.acs".format(current_dir), 'w') as tempcb:
        with open(template, 'r') as tempf:
            for line in tempf:
                if 'CHANGE_ME' in line:
                    tempcb.write('  TS.lot in (\'{}\')\n'.format(lot_name))
                else:
                    tempcb.write(line)


def parse_itime_file(file):
    tp_data = {}
    with open(file, 'r') as itime:
        for line in itime:
            current_line = line.split(',')
            team = current_line[0]
            module = current_line[1]
            instance = current_line[2]
            itime_w = current_line[3]
            vpo = current_line[8]
            location = current_line[9]
            bom = current_line[10]
            tp = current_line[13].replace("\n", "")
            if tp != "PROGRAM_NAME":
                if tp not in tp_data.keys():
                    tp_data[tp] = {}
                if team not in tp_data[tp].keys():
                    tp_data[tp][team] = {}
                if module not in tp_data[tp][team].keys():
                    tp_data[tp][team][module] = {}
                tp_data[tp][team][module][instance] = float(itime_w)
    return tp_data


def calculate_total_itime_permodule(data):
    total_time = {}
    for tp in data.keys():
        for team in data[tp].keys():
            total_time[team] = {}
            total_time[team][team + '_total'] = 0
            for module in data[tp][team].keys():
                total_time[team][module] = 0
                for instance in data[tp][team][module].keys():
                    total_time[team][module] += data[tp][team][module][instance]
                    total_time[team][team + '_total'] += data[tp][team][module][instance]
    return total_time

update_test_time(vpo)