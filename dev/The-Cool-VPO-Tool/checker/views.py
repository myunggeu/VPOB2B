from django.http import HttpResponse
from django.shortcuts import render
from django.forms.models import model_to_dict
from checker.models import Plan, VPO_DESC, VPO_LOC, PLAN_STATUS, TEST_TIME_MODULE,TEST_TIME_TP
from .forms import TPEntry, VPOEntry
import os
import datetime
import time
import urllib
import csv
from django_mysql.models import JSONField
import json
accepted_users = ['rshibano', 'mbhutani', 'arunasun', 'svbasole', 'ravivisw', 'aguilara', 'hhbonill', 'lcferna1',
                  'gamendez', 'jdperezg', 'lmvasque', 'gvegalee', 'bvillalo', 'mtjimene', 'nmorar', 'sgorthi',
                  'kkottu', 'zheyin', 'casolano', 'vabarca', 'mharms', 'kdu3', 'vgudmund', 'samyukth', 'dmantena',
                  'arunasun', 'sicongyu', 'myunggeu']
current_dir = os.getcwd()


def index(request):
    print("INSIDE INDEX PAGE - HOMEPAGE?")
    if request.method == "POST": # I don't think this if statement ever gets called?
        print('INSIDE FIRST IF STATEMENT')
        form_value = TPEntry(request.POST)
        print('FORM VALUE: ', form_value)
        if form_value.is_valid():
            tp = form_value['tp'].value()
            ww = form_value['ww'].value()
            # check to see if the tp already exists
            if not Plan.objects.filter(tp=tp).exists():
                new_tpEntry = Plan(tp=tp, ww=ww)
                new_tpEntry.save()
    tp_entries = list(Plan.objects.all())
    print("ABOUT TO LOAD index.html")
    return render(request, 'index.html', {'entries': tp_entries})

def check_ituff_exists(vpo, location):
    ituff_path = ""
    if vpo[:1] == "J":
        ituff_path = r'\\amr\ec\proj\mdl\cr\intel\hdmxdata\prod'
    elif vpo[:1] == "I":
        ituff_path = r'\\amr\ec\proj\mdl\sc\intel\hdmxdata\prod'
    else:
        raise
    path = r"{}\{}_{}\1A".format(ituff_path, vpo, location)
    print(path)
    if os.path.isfile(path):
        print("ituff found!")
        return True
    else:
        print("ituff not found!")
        return False

def check_cb_results(vpos):
    print("[System] -- Running CB script and parsing output csv")
    # generate cb script
    with open(r"{}\checker\static\checker\temp_files\out_cb.acs".format(current_dir), "w") as acs:
        acs.write('<collection type=material>\n')
        acs.write('   <group>\n')
        for vpo in vpos:
            acs.write('      {} SITE=MIDAS,CR,SVC,ARIES DOMAIN=CLASS\n'.format(vpo))
        acs.write('   </group>\n')
        acs.write('</collection>\n')
        acs.write('\n<analysis app=cb >\n')
        acs.write('   TOOL=SCPREFETCH\n')
        acs.write('   /HASCLASS=T\n')
        acs.write('   /SEPARATEBY=NONE\n')
        acs.write('   CLASSDISPLAY=RAW\n')
        acs.write('   DISPLAYAS=TABLE\n')
        acs.write('   SORTDISPLAY=RAW\n')
        acs.write('   /COMBINEPARTFLOW\n')
        acs.write('   /FORMAT=CSV\n')
        acs.write('   /OUTPUT=\'{}\\checker\\static\\checker\\temp_files\\outputR.csv\'\n'.format(current_dir))
        acs.write('   /ASMERLIN\n')
        acs.write('</analysis>\n')
    # execute cb script
    os.system(r"{}\checker\static\checker\temp_files\out_cb.acs".format(current_dir))
    # parse csv
    while os.path.isfile(r"{}\checker\static\checker\temp_files\outputR.csv".format(current_dir)) == False:
        time.sleep(2)
    time.sleep(3)
    vpo_info = {}
    #vpo_info[vpo] = {}
    # SITE	LOT	OPERATION	SOURCE	FACILITY	PROGRAM	PART	PROCESS	FLOW	TEST_END_DATE	TEMPERATURE	WW_END_TEST	#TESTED	T_GOOD	SEPARATION	GROUP	IB1
    with open(r"{}\checker\static\checker\temp_files\outputR.csv".format(current_dir), 'r') as csvf:
        for line in csvf:
            split_line = line.replace("\n", "").split(",")
            if "SITE" in split_line[0]:
                headers = split_line
                IBs = []
                for header in headers:
                    if "IB" in header:
                        IBs.append(header)
            elif len(split_line) < 2:
                continue
            else:
                statistics = {}
                location = split_line[headers.index("OPERATION")]
                statistics['vpo_program'] = split_line[headers.index("PROGRAM")]
                statistics['vpo_part'] = split_line[headers.index("PART")]
                statistics["t_good"] = split_line[headers.index("T_GOOD")]
                statistics["total_tested"] = split_line[headers.index("#TESTED")]
                statistics["percent_good"] = '{0:.0%}'.format(int(statistics["t_good"])/int(statistics["total_tested"]))
                test_end_date = split_line[headers.index("TEST_END_DATE")]
                vpo = split_line[headers.index("LOT")]
                ib_all = {}
                if vpo not in vpo_info.keys():
                    vpo_info[vpo] = {}
                for ib in IBs:
                    ib_all[ib] = split_line[headers.index(ib)].replace("\n", "")
                vpo_info[vpo][location] = {}
                vpo_info[vpo][location]["statistics"] = statistics
                vpo_info[vpo][location]["test_end_date"] = test_end_date
                ib_display_string = ""
                for key, value in ib_all.items():
                    if value.replace(" ", "").replace("\n", "") != "0":
                        ib_display_string += "{}: {}<br>".format(key, value)
                vpo_info[vpo][location]["ib_all"] = ib_display_string
    os.remove(r"{}\checker\static\checker\temp_files\outputR.csv".format(current_dir))
    return vpo_info

def valid_plan(request, tp):
    print("[System] -- Rendering main validation plan page")
    print(tp)
    tpEntry = Plan.objects.get(tp=tp)
    vpo_loc = VPO_LOC.objects.all()
    vpo_loc_list = {}
    vpo_and_id = {}
    bom_and_statuses = {}
    ww = tpEntry.ww
    supported_boms = []
    vpo_desc = VPO_DESC.objects.filter(tp=tp)
    #plan_status = PLAN_STATUS.objects.filter(ptp=tp)
    #print(plan_status)
    for vpo in vpo_desc:
        vpo_and_id[vpo.id] = vpo.vpo
        if vpo.bom not in supported_boms:
            supported_boms.append(vpo.bom)
            bom_and_statuses[vpo.bom] = {}
    for bom in supported_boms:
        bom_statuses = PLAN_STATUS.objects.filter(ptp=tp, pbom=bom)
        for bom_status in bom_statuses:
            bom_and_statuses[bom] = {'ptp':bom_status.ptp, 'pbom':bom_status.pbom, 'ppilots': bom_status.ppilots,
                                     'pyield': bom_status.pyield, 'pbs': bom_status.pbs, 'ptherm': bom_status.ptherm,
                                     'pb2b': bom_status.pb2b, 'pqa': bom_status.pqa, 'pinitwtl': bom_status.pinitwtl,
                                     'pfinwtl': bom_status.pfinwtl, 'pfwp': bom_status.pfwp, 'pfuse': bom_status.pfuse}


    request.session['vpo_and_id'] = vpo_and_id
    return render(request, 'valplan.html', {'vpo_loc': vpo_loc, 'vpo_desc': vpo_desc, 'bom_and_statuses': bom_and_statuses,
                                            'tp': tp, 'ww':ww, 'supported_boms': supported_boms})

def refresh_plan(request):
    print("[System] -- Refreshing Plan Page")
    tp = request.POST["tp"]
    vpo_list = VPO_DESC.objects.filter(tp=tp)
    all_vpos = []
    entries = []
    for vpo_entry in vpo_list:
        if vpo_entry.vpo != "":
            all_vpos.append(vpo_entry.vpo)
    vpo_info = check_cb_results(all_vpos)
    for vpo in vpo_info.keys():
        if vpo != "":
            #vpo_info[vpo][location]["statistics"]["percent_good"]
            for location in vpo_info[vpo].keys():
                if location == 6129:
                    print("loc 6129: {}".format(vpo_info))
                try:
                    new_loc = VPO_LOC.objects.get(vpo=vpo, location=location)
                    new_loc.bin_desc = vpo_info[vpo][location]["ib_all"]
                    new_loc.yield_val = vpo_info[vpo][location]["statistics"]["percent_good"]
                    new_loc.vpo_program = vpo_info[vpo][location]["statistics"]["vpo_program"]
                    new_loc.vpo_part = vpo_info[vpo][location]["statistics"]["vpo_part"]
                    new_loc.status = True
                    new_loc.save()
                except:
                    print("failed")
                    continue
            vpo_dict = {"vpo": vpo, "bom": vpo, "locations": {}}
            vpo_locs = VPO_LOC.objects.filter(vpo=vpo)
            loc_set = {}
            if len(vpo_locs) > 0:
                for loc in vpo_locs:
                    loc_set[loc.location] = [loc.status,loc.bin_desc]
            vpo_dict["locations"] = loc_set

            entries.append(vpo_dict)
    return render(request,'valplan.html', {'entries': entries, 'tp': tp})


def delete_vpo(request):
    try:
        cookies = request.META['HTTP_COOKIE']
        split_cookies = cookies.split("; ")
        for cookie in split_cookies:
            if "IDSID" in cookie:
                host_name = cookie[6:]
        if host_name in accepted_users:
            print("\n\nAccepted, User: {}".format(host_name))
            vpo_del = request.POST["vpo"]
            vpo_id = request.POST["vpo_id"]
            tp = request.POST["tp"]
            print(tp)
            VPO_DESC.objects.filter(vpo=vpo_del, id=vpo_id).delete()
            if vpo_del != "":
                VPO_LOC.objects.filter(vpo=vpo_del).delete()
            vpo_list = VPO_DESC.objects.filter(tp=tp)
            entries = []
            for val in vpo_list:
                vpo_dict = {"vpo": val.vpo, "bom": val.bom, "locations": {}}
                vpo_locs = VPO_LOC.objects.filter(vpo=val.vpo)
                loc_set = {}
                if (len(vpo_locs) > 0):
                    for loc in vpo_locs:
                        loc_set[loc.location] = [loc.status, loc.bin_desc]
                vpo_dict["locations"] = loc_set
                # print(vpo_dict)
                entries.append(vpo_dict)
            return render(request, 'valplan.html', {'entries': entries, 'tp': tp})
        else:
            print("\n\nRejected, User: {}".format(host_name))
            return render(request, 'reject.html')
    except:
        print("\n\nRejected, User: Unknown")
        return render(request, 'reject.html')


def add_template(request):
    print("[System] Add Template function")
    # get user name from cookies to limit access to page
    try:
        cookies = request.META['HTTP_COOKIE']
        split_cookies = cookies.split("; ")
        for cookie in split_cookies:
            if "IDSID" in cookie:
                host_name = cookie[6:]
        if host_name in accepted_users:
            print("\n\nAccepted, User: {}".format(host_name))
            tp_entries = list(Plan.objects.all())
            template = parse_vpo_template_file(
                #r"I:\CMT_ENG\skx\tpi\user\rshibano\val_plan_template\vpo_template.csv".format(current_dir))
                #r"C:\Users\vabarca\Dev\val_plan_template\vpo_template.csv".format(current_dir))
                r"C:\Users\myunggeu\VPO_TEMPLATES\val_plan_template\vpo_template_6_16_2022.csv".format(current_dir))

            boms = template.keys()
            prod_and_boms = {}
            for curr_bom in boms:
                if template[curr_bom][-1][-1] not in prod_and_boms.keys():
                    prod_and_boms[template[curr_bom][-1][-1]] = []
                    prod_and_boms[template[curr_bom][-1][-1]].append(curr_bom)
                else:
                    prod_and_boms[template[curr_bom][-1][-1]].append(curr_bom)
            print("BELOW IS THE prod_and_boms variable")
            print(prod_and_boms)
            return render(request, 'vpo_entry.html', {'tp_entries': tp_entries, 'prod_and_boms': prod_and_boms})
        else:
            print("\n\nRejected, User: {}".format(host_name))
            return render(request, 'reject.html')
    except:
        print("\n\nError Parsing FILE!!, User: Unknown")
        return render(request, 'template_error.html')

def create_template(request):
    print("[System] -- Create Template")
    #template = parse_vpo_template_file(r"I:\CMT_ENG\skx\tpi\user\rshibano\val_plan_template\vpo_template.csv".format(current_dir))
    #template = parse_vpo_template_file(r"C:\Users\vabarca\Dev\val_plan_template\vpo_template.csv".format(current_dir))
    template = parse_vpo_template_file(r"C:\Users\myunggeu\VPO_TEMPLATES\val_plan_template\vpo_template_6_16_2022.csv".format(current_dir))
    boms = template.keys()
    form_value = TPEntry(request.POST)
    tp = form_value['tp'].value()
    ww = form_value['ww'].value()
    supported_boms = []
    supported_templates = []
    for bom in boms:
        print("{},{}".format(bom, form_value[bom].value()))
        if form_value[bom].value():
            supported_boms.append(bom)
            supported_templates.append(template[bom])
    if len(supported_boms) < 1:
        return HttpResponse("You did not select any boms, go back and try again!")
    if tp == "":
        return HttpResponse("No TP entered, go back and try again!")
    if ww == "":
        return HttpResponse("No WW entered, go back and try again!")
    return render(request, 'val_plan_admin.html', {'ww': ww, 'tp':tp, 'supported_templates': supported_templates, 'supported_boms': supported_boms})

def save_template(request):
    print("[System] -- Entered Save Template")
    tp = request.POST['tp']
    ww = request.POST['ww']
    if not Plan.objects.filter(tp=tp).exists():
        new_tp = Plan(tp=tp, ww=ww)
        new_tp.save()

    table_entries = request.POST['submit_table'].split("%2B%2B%2B")
    db_entries = []
    db_row = {}
    for entry in table_entries:
        entry_params = entry.split("&")
        for param in entry_params:
            values = param.split("=")
            if len(values) < 2:
                continue
            db_row[urllib.parse.unquote(values[0])] = urllib.parse.unquote(values[1])
        print(db_row)
        if len(db_row) != 0:
            db_entries.append(db_row.copy())
    print(db_entries)
    for db_entry in db_entries:
        new_row = VPO_DESC(tp=tp, bom=db_entry['bom'], ww=db_entry['ww'], site=db_entry['site'],
                           units=db_entry['units'], device=db_entry['device'], source_lot=db_entry['source'],
                           locations=db_entry['locations'], description=db_entry['description'])
        new_row.save()
        if not PLAN_STATUS.objects.filter(ptp=tp, pbom=db_entry['bom']).exists():
            new_plan_status = PLAN_STATUS(ptp=tp, pbom=db_entry['bom'])
            new_plan_status.save()
    return HttpResponse("Saved")

def add_to_template(request):
    print("[System] -- Add to Template")
    form_value = TPEntry(request.POST)
    print(form_value)
    tp = form_value['tp_select'].value()
    ww = Plan.objects.get(tp=tp).ww
    supported_boms = ['']
    supported_templates = [['']]
    if tp == "":
        return HttpResponse("No TP entered, go back and try again!")
    if ww == "":
        return HttpResponse("No WW entered, go back and try again!")
    return render(request, 'val_plan_admin.html',
                  {'ww': ww, 'tp': tp, 'supported_templates': supported_templates, 'supported_boms': supported_boms})

def update_vpo(request):
    print("[System] -- Updating VPO entry")
    vpo_and_id_before = request.session["vpo_and_id"]

    table_entries = request.POST['submit_table']
    entry = table_entries.split("&")
    print(entry)
    id_and_vpo = {}
    for vpo in entry:
        if "vpo_" in vpo:
            print("VPO: {}".format(vpo))
            vpo_id = vpo.replace("vpo_", "").split("=")[0]
            print(vpo_id)
            vpo_number = vpo.replace("vpo_", "").split("=")[1].replace("%20", "").replace(" ", "")
            # save to VPO_DESC db
            vpo_desc_obj = VPO_DESC.objects.get(id=int(vpo_id))
            vpo_desc_obj.vpo = vpo_number
            vpo_desc_obj.save()
            # save to VPO_LOC db
            locations = vpo_desc_obj.locations.replace(" ", "").split(",")
            if vpo_number != "":
                if vpo_id not in vpo_and_id_before.values():
                    for location in locations:
                        if not VPO_LOC.objects.filter(vpo=vpo_number, location=int(location)).exists():
                            print("Updated VPO for {}, {}".format(vpo_number, location))
                            vpo_loc_obj = VPO_LOC(vpo=vpo_number, location=int(location))
                            vpo_loc_obj.save()
                else:
                    print("vpo skipped")
    return HttpResponse("No WW entered, go back and try again!")

def update_vpo_info(request):
    print("[System] -- Updating VPO info")
    vpo_info = request.POST.getlist('vpo_info[]')
    print(vpo_info)
    vpo_desc_obj = VPO_DESC.objects.get(id=int(vpo_info[0]))
    print(vpo_info[7])
    vpo_desc_obj.ww = vpo_info[2]
    vpo_desc_obj.vpo = vpo_info[3]
    vpo_desc_obj.site = vpo_info[4]
    vpo_desc_obj.units = vpo_info[5]
    vpo_desc_obj.device = vpo_info[6]
    vpo_desc_obj.source_lot = vpo_info[7]
    vpo_desc_obj.locations = vpo_info[8]
    vpo_desc_obj.description = vpo_info[9]
    vpo_desc_obj.save()
    return HttpResponse("Complete!")

def update_valplan_status(request):
    print("[System] -- Updating val plan status")
    status_checked = request.POST.getlist('checked[]')
    tp = request.POST['tp']
    #initially clear all checkboxes
    status = PLAN_STATUS.objects.filter(ptp=tp)
    for bom in status:
        bom.ppilots = False
        bom.pyield = False
        bom.pbs = False
        bom.ptherm = False
        bom.pb2b = False
        bom.pqa = False
        bom.pinitwtl = False
        bom.pfinwtl = False
        bom.pfwp = False
        bom.pfuse = False
        bom.save()

    #update checkboxes with values from DB
    for status in status_checked:
        item_and_bom = status.split("_")
        print(item_and_bom)
        plan_status = PLAN_STATUS.objects.get(ptp=tp, pbom=item_and_bom[1])
        if item_and_bom[0] == "ppilots":
            plan_status.ppilots = True
        if item_and_bom[0] == "pyield":
            plan_status.pyield = True
        if item_and_bom[0] == "pbs":
            plan_status.pbs= True
        if item_and_bom[0] == "ptherm":
            plan_status.ptherm = True
        if item_and_bom[0] == "pb2b":
            plan_status.pb2b= True
        if item_and_bom[0] == "pqa":
            plan_status.pqa= True
        if item_and_bom[0] == "pinitwtl":
            plan_status.pinitwtl = True
        if item_and_bom[0] == "pfinwtl":
            plan_status.pfinwtl = True
        if item_and_bom[0] == "pfwp":
            plan_status.pfwp= True
        if item_and_bom[0] == "pfuse":
            plan_status.pfuse = True
        plan_status.save()
        print("Saved")
    return HttpResponse("ok")

def delete_all_entries(request):
    form_value = TPEntry(request.POST)
    print(form_value)
    tp = form_value['tp_select'].value()
    try:
        PLAN_STATUS.objects.filter(ptp=tp).delete()
        Plan.objects.filter(tp=tp).delete()
        VPO_DESC.objects.filter(tp=tp).delete()
    except:
        return HttpResponse("Error, failed to delete entries")
    return HttpResponse("Deleted all entries for {}!".format(tp))

def parse_vpo_template_file(template_file):
    print("[System] -- Parsing VPO template file")
    template = {}
    with open(template_file, 'r') as tf:
        tf_read = csv.reader(tf)
        for row in tf_read:
            print("Row: {}".format(row))
            if len(row) < 5:
                print("skip row")
                continue
            if row[0] not in template.keys():
                template[row[0]] = []
            template[row[0]].append([row[0],row[1],row[2],row[3],row[4],row[5],row[6].replace("\t", "")
                                    .replace(" ", ""),row[7],row[8].replace(" ", "")])
    print(template)
    return template

def save_csv(request, tp_name):
    print("[System] -- Saving VPO page to csv")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}_table.csv'.format(tp_name)
    writer = csv.writer(response)
    writer.writerow([tp_name])
    writer.writerow([str(datetime.datetime.now().isoformat())])
    writer.writerow(['BOM', 'WW', 'VPO', 'SITE', 'UNITS', 'DEVICE', 'SOURCE LOT', 'LOCATIONS', 'DESCRIPTION'])
    for entry in VPO_DESC.objects.filter(tp=tp_name):
        loc_underscore = entry.locations.replace(",", "_")
        vpos = entry.vpo.split(",")
        vpo_status = ""
        for vpo in vpos:
            for loc_entry in VPO_LOC.objects.filter(vpo=vpo):
                print(loc_entry)
                if loc_entry.status:
                    status = "done"
                else:
                    status = "pending"

                vpo_status += "{}-{}_".format(loc_entry.location, status)
        writer.writerow([entry.bom, entry.ww, entry.vpo, entry.site,entry.units, entry.device,
                         entry.source_lot, vpo_status, entry.description])
    return response

def update_test_time(request):
    print("[System] -- Updating test time")
    tp = request.POST['tp']
    vpo = request.POST['vpo']
    loc = request.POST['loc']
    bom = request.POST['bomstep']
    edit_and_run_cb_script(cb_template, vpo, loc)
    tp_data, prod = parse_itime_file(itime_file)
    total_time = calculate_total_itime_permodule(tp_data)
    save_to_db(tp_data, total_time, tp, loc, prod, bom)
    print("Saved")
    return HttpResponse("ok")

def test_time(request):
    print("[System] -- Main TT page")
    tp_level_tt = []
    modules = []
    modules_tt = []
    modules.append('TP')
    modules.append('TOTAL')
    modules.append('PHI')
    modules.append('PRODUCT')
    modules.append('LOCATION')
    modules.append('BOM')
    total_time_tp = float(0.0)

    tp_list = TEST_TIME_TP.objects.values_list('tp').distinct()
    tp_list_module = TEST_TIME_MODULE.objects.values_list('tp').distinct()
    func_inst_tt = get_all_module_tt(tp_list_module, 'FUNC')
    tpi_inst_tt = get_all_module_tt(tp_list_module, 'TPI')
    cache_inst_tt = get_all_module_tt(tp_list_module, 'CACHE')
    scan_inst_tt = get_all_module_tt(tp_list_module, 'SCAN')
    binning_inst_tt = get_all_module_tt(tp_list_module, 'BINNING')
    thermal_inst_tt = get_all_module_tt(tp_list_module, 'THERMAL')
    lttc_inst_tt = get_all_module_tt(tp_list_module, 'LTTC')
    chvqk_inst_tt = get_all_module_tt(tp_list_module, 'CHVQK')

    for tp in tp_list:
        if tp != '':
            #for TP level TT

            tp_objs = TEST_TIME_TP.objects.filter(tp=tp[0])
            for tp_obj in tp_objs:
                module_and_tts = json.loads(tp_obj.module_and_tt)
                modules_tt.append(tp[0])
                modules_tt.append(tp_obj.phi)
                modules_tt.append(tp_obj.product)
                modules_tt.append(tp_obj.location)
                modules_tt.append(tp_obj.bom)
                for module in module_and_tts.keys():
                    if module not in modules:
                        modules.append(module)
                    modules_tt.append(module_and_tts[module]["{}_total".format(module)]/1000)
                    total_time_tp += module_and_tts[module]["{}_total".format(module)]/1000

                modules_tt.insert(1, total_time_tp)
            tp_level_tt.append(modules_tt)

            modules_tt = []
            total_time_tp = float(0.0)
    tp_level_tt.insert(0,modules)
    return render(request, 'test_time.html', {'tp_level_tt': json.dumps(tp_level_tt),
                                              'func_tt': json.dumps(func_inst_tt),
                                              'tpi_tt': json.dumps(tpi_inst_tt),
                                              'cache_tt': json.dumps(cache_inst_tt),
                                              'scan_tt': json.dumps(scan_inst_tt),
                                              'binning_tt': json.dumps(binning_inst_tt),
                                              'thermal_tt': json.dumps(thermal_inst_tt),
                                              'chvqk_tt': json.dumps(chvqk_inst_tt),
                                              'lttc_tt': json.dumps(lttc_inst_tt),})

def get_all_module_tt(tp_list, team_name):
    all_tts_dict = {}
    module_inst_tt = []
    all_module_inst_names = []
    for tp in tp_list:
        if tp != '':
            #print(tp[0])
            #module_inst_tt_raw = []
            tp_now = tp[0]
            if tp_now not in all_tts_dict.keys():
                all_tts_dict[tp_now] = {}
            # looking up all FUNC tp test time entries in database (FUN_SBFT/FUN_DRNG) for current TP
            module_tp_objs = TEST_TIME_MODULE.objects.filter(tp=tp_now, team=team_name)
            for module_tp_obj in module_tp_objs:
                #print("TP: {}, Module: {}, Team: {}".format(module_tp_obj.tp, module_tp_obj.module, module_tp_obj.team))
                #if len(module_inst_tt_raw) == 0:
                #    module_inst_tt_raw = [tp_now]
                current_module = module_tp_obj.module
                instance_and_tts = json.loads(module_tp_obj.instance_and_tt)

                for instance in instance_and_tts.keys():
                    # Adding tt for current module_inst name for current TP
                    if "{}_{}".format(current_module, instance) not in all_tts_dict[tp_now].keys():
                        all_tts_dict[tp_now]["{}_{}".format(current_module, instance)] = instance_and_tts[instance] / 1000
                    # keeping track of all module_inst names for all TPs
                    if "{}_{}".format(current_module, instance) not in all_module_inst_names:
                        all_module_inst_names.append("{}_{}".format(current_module, instance))
    all_module_inst_names = sorted(all_module_inst_names)
    heading_list = ['Instance']

    for instance_name in all_module_inst_names:
        curr_inst_list = [instance_name]
        for curr_tp in all_tts_dict.keys():
            if curr_tp not in heading_list:
                heading_list.append(curr_tp)
            if instance_name in all_tts_dict[curr_tp].keys():
                curr_inst_list.append(all_tts_dict[curr_tp][instance_name])
            else:
                curr_inst_list.append(float(0.0))

        #print(all(i < 0.001 for i in module_inst_tt[1:]))
        delete_me = True
        for value in curr_inst_list[1:]:
            if value > 0.2:
                delete_me = False
            else:
                continue
        if not delete_me:
            module_inst_tt.append(curr_inst_list)

    module_inst_tt.insert(0, heading_list)

    return module_inst_tt

def tester_status(request):

    return render(request, 'tester_status.html')


#def bin2bin(request):
 #   return render(request, 'bin2bin.html')


####Methods for test time tool####
itime_file = r"{}\checker\static\checker\temp_files\itime.csv".format(current_dir)
cb_template = r"{}\checker\static\checker\temp_files\clx_itime_summary_template.acs".format(current_dir)
temp_cb_dir = r"{}\checker\static\checker\temp_files\temp_cb.acs".format(current_dir)


#total_time[team][module] = total time per module
#total_time[team][team_total] = total time per team
#example:
#total_time[CACHE][ARR_CACHE] = 112817.0527
#total_time[CACHE][CACHE_total] = 113194.302


def edit_and_run_cb_script(template, lot_name, loc):
    '''edit cb script to generate itime csv file'''
    if os.path.isfile(r"{}\checker\static\checker\temp_files\temp_cb.acs".format(current_dir)):
        os.remove(r"{}\checker\static\checker\temp_files\temp_cb.acs".format(current_dir))
    #if os.path.isfile(r"{}\checker\static\checker\temp_files\itime.csv".format(current_dir)):
    #    os.remove(r"{}\checker\static\checker\temp_files\itime.csv".format(current_dir))
    try:
        with open(temp_cb_dir, 'w') as tempcb:
            with open(template, 'r') as tempf:
                for line in tempf:
                    if 'CHANGE_ME' in line:
                        tempcb.write('  TS.lot in (\'{}\')\n'.format(lot_name))
                    elif 'CHANGE_LOC' in line:
                        tempcb.write('  and TS.OPERATION in (\'{}\')\n'.format(loc))
                    else:
                        tempcb.write(line)
    except:
        raise
    # execute cb script
    os.system(r"{}\checker\static\checker\temp_files\temp_cb.acs".format(current_dir))
    # parse csv
    while os.path.isfile(r"{}\checker\static\checker\temp_files\itime.csv".format(current_dir)) == False:
        time.sleep(2)
    time.sleep(3)


def parse_itime_file(file):
    print("Parsing itime file")
    tp_data = {}
    product = ""
    with open(file, 'r') as itime:
        for line in itime:
            current_line = line.split(',')
            team = current_line[0]
            module = current_line[1]
            instance = current_line[2]
            itime_w = current_line[3]
            vpo = current_line[8]
            location = current_line[10]
            product = current_line[13][:3]
            tp = current_line[13].replace("\n", "")
            if tp != "PROGRAM_NAME":
                if tp not in tp_data.keys():
                    tp_data[tp] = {}
                if team not in tp_data[tp].keys():
                    tp_data[tp][team] = {}
                if module not in tp_data[tp][team].keys():
                    tp_data[tp][team][module] = {}
                tp_data[tp][team][module][instance] = float(itime_w)
    return tp_data, product

def calculate_total_itime_permodule(data):
    print("Calculating total itime per module")
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

def save_to_db(tpdata, totaltime, tp, loc, product, bom):
    print("Save to DB\n")
    team_and_tt = ""
    instance_and_tt = ""
    tp = product + "_" + bom + "_" + tp + "_" + loc
    for team in totaltime.keys():
        team_and_tt += "{}-{},".format(team, totaltime[team]['{}_total'.format(team)])
    print(team_and_tt)
    prev_tp, new_tp = TEST_TIME_TP.objects.update_or_create(tp=tp, location=loc, product=product, bom=bom)
    if new_tp:
        prev_tp.tp = tp
        prev_tp.location = loc
        prev_tp.product = product
        prev_tp.bom = bom
        prev_tp.phi = "60"
        prev_tp.module_and_tt = json.dumps(totaltime)
        #new_tp = TEST_TIME_TP(tp=tp, bom="dummy", phi=160, module_and_tt=json.dumps(totaltime))
        prev_tp.save()
    else:
        prev_tp.module_and_tt = json.dumps(totaltime)
        # new_tp = TEST_TIME_TP(tp=tp, bom="dummy", phi=160, module_and_tt=json.dumps(totaltime))
        prev_tp.save()

    for temptp in tpdata.keys():
        tpshort = temptp
    for team in tpdata[tpshort].keys():
        for module in tpdata[tpshort][team].keys():
            instance_and_tt = {}
            for instance in tpdata[tpshort][team][module].keys():
                tt = tpdata[tpshort][team][module][instance]
                instance_and_tt[instance] = tt
            old_module_tp, new_module_tp = TEST_TIME_MODULE.objects.update_or_create(bom=bom, tp=tp,
                                                                                     module=module, team=team,
                                                                                     location=loc, product=product)
            if new_module_tp:
                old_module_tp.bom = bom
                old_module_tp.tp = tp
                old_module_tp.location = loc
                old_module_tp.module = module
                old_module_tp.team = team
                old_module_tp.product=product
                old_module_tp.instance_and_tt = json.dumps(instance_and_tt)
                old_module_tp.save()
            if old_module_tp:
                old_module_tp.instance_and_tt = json.dumps(instance_and_tt)
                old_module_tp.team = team
                old_module_tp.save()

