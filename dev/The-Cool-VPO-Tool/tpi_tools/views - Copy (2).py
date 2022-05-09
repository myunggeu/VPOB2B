from typing import List

from django.shortcuts import render
from .models import Bin2Bin, TP
from .forms import PostExplanation, TPIEntry
from django.http import HttpResponse
from django.utils.http import urlencode
# from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import RequestContext
from django.template import loader
import socket
import urllib
import os
import re
import time
import csv
from datetime import datetime
import uuid

import string
import subprocess
import codecs


# Bom = ''
#stamp = ''

current_dir = os.getcwd()
out_file = "file.csv"
bom_decoder = {"SPH0": "XCCSP", # THIS IS A BACKUP
               "SPH1": "XCCSP",
               "JDH1": "XCCSP",
               "STM1": "HCCSR", #added
               "JTH1": "XCCSP",
               "DFH0": "XCCDF",
               "DPH0": "XCCDP",
               "DMH0": "XCCDM",
               "DFH1": "XCCDF",
               "DPH1": "XCCDP",
               "DMH1": "XCCDM",
               "DMH2": "XCCDM",
               "DEM1": "XCCDE",
               "DEM2": "XCCDE",
               "SPM0": "HCCSP",
               "SRM0": "HCCSR",
               "SPM1": "HCCSP",
               "SRM1": "HCCSR",
               "SPU0": "LCCSP",
               "SRU0": "LCCSR",
               "SPU1": "LCCSP",
               "SRU1": "LCCSR",
               "SCH0": "SORT_XCC",
               "SCM0": "SORT_HCC",
               "SCU0": "SORT_LCC",
               }

bom_decoder_SKX = {"SPH0": "SKX XCCSP",
                   "SPH1": "SKX XCCSP",
                   "JDH1": "SKX XCCSP",
                   "STM1": "SKX HCCSR",
                   "JTH1": "SKX XCCSP",
                   "DFH0": "SKX XCCDF",
                   "DPH0": "SKX XCCDP",
                   "DMH0": "SKX XCCDM",
                   "DFH1": "SKX XCCDF",
                   "DPH1": "SKX XCCDP",
                   "DMH1": "SKX XCCDM",
                   "DMH2": "SKX XCCDM",
                   "DEM1": "SKX XCCDE",
                   "DEM2": "SKX XCCDE",
                   "SPM0": "SKX HCCSP",
                   "SRM0": "SKX HCCSR",
                   "SPM1": "SKX HCCSP",
                   "SRM1": "SKX HCCSR",
                   "SPU0": "SKX LCCSP",
                   "SRU0": "SKX LCCSR",
                   "SPU1": "SKX LCCSP",
                   "SRU1": "SKX LCCSR",
                   "SCH0": "SORT_XCC",
                   "SCM0": "SORT_HCC",
                   "SCU0": "SORT_LCC",
                   "DMHX": "SKX SKM",
                   }


bom_decoder_CLX = {"SPK1": "CLX XCCSP",
                   "SPN1": "CLX HCCSP",
                   "SPV1": "CLX LCCSP",
                   "SRN1": "CLX HCCSR",
                   "SRV1": "CLX LCCSR",
                   "64K0": "CLX XCC64L",
                   "64K1": "CLX XCC64L",
                   "SPN0": "CLX HCCSP",
                   "SPK0": "CLX XCCSP",
                   "XXK0": "CLX AP",
                   "XXK1": "CLX AP"
                   }


bom_decoder_SPR = {"SPA2": "SPR XCCSP",
                   "SPB0": "SPR XCCSP"
                   }


bom_to_template_cb_file = {"H0": "template_xcc.acs",
                           "H1": "template_xcc.acs",
                           "M0": "template_hcc.acs",
                           "M1": "template_hcc_cmt.acs",
                           "M2": "template_hcc_cmt.acs",
                           "U0": "template_lcc.acs",
                           "U1": "template_lcc.acs",
                           "SC": "template_sort.acs"
                           }

# hot_locations = ['6262', '6270', '6264', '6261', '6248']
# hot_cmt_locations = ['7711']
# cold_locations = ['6212', '6215', '6248']
# cold_cmt_locations = ['7712']

#headers = ""

# variables for possible queue
class Queue:
    def __init__(self):
        # Initialize queue class
        self.items = []

    def isEmpty(self):
        # Determines if queue is empty
        return self.items == []

    def add(self, item):
        # Adds element to the beginning of the queue
        self.items.insert(0, item)

    def pop(self):
        # Takes element out from the beginning of the queue
        return self.items.pop()

    def size(self):
        # Returns size of the queue
        return len(self.items)

    def front(self):
        # Returns item in front of the list
        return self.items[self.size() - 1]


queue_old_vpo = Queue()
queue_old_tp = Queue()
queue_new_vpo = Queue()
queue_new_tp = Queue()
queue_location = Queue()
queue_reparse_csv = Queue()

# variables for possible queue
queue_old_VPOs_list = []
queue_old_tpPaths_list = []
queue_old_tpNames_list = []
queue_new_VPOs_list = []
queue_new_tpPaths_list = []
queue_new_tpNames_list = []
queue_locations_list = []
queue_BinDefs_list = []
queue_timestamp_list = []
queue_username_list = []
queue_identifier_list = []
queue_Sites_list = []

users_identifiers = []
entry_length = []


def parse_cb_csv_file(lot_file_name, old_tp, new_tp, location, lots_old_new):
    Bom = ' '
    print("INSIDE parse_cb_csv_file FUNCTION")
    print("5-7 section of new tp: ", new_tp[5:7])
    if new_tp[5:7] == "SC":
        unit_header = "DFF_ULT"
    else:
        unit_header = "VIS_ID"
    print("Parsing CSV File")
    print("Location: ", location)
    if location == "6262" or location == "6270" or location == "6264" or location == "6261" or location == "6248":
        # add back [CLASSHOT] when putting back MIDAS
        group = "[CLASSHOT]"
    elif location == "6215" or location == "6212":
        # add back [CLASSCOLD] when putting back MIDAS
        group = "[CLASSCOLD]"
    elif location == "132310" or location == "6051":
        group = ""

    print("")
    print("{},{}".format(old_tp, new_tp))
    all_bins = {}
    all_bins["{}@{}".format(location, old_tp)] = []
    all_bins["{}@{}".format(location, new_tp)] = []
    bin_to_bin_count = {}
    unit_data = {}

    #########################################################
    if new_tp[0:3] == 'CLX':
        print("working with CLX Test Program")
        Bom = bom_decoder_CLX[new_tp[5:9]]

    elif new_tp[0:3] == 'SKX':
        print("working with SKX Test Program")
        Bom = bom_decoder_SKX[new_tp[5:9]]

    elif new_tp[0:3] == 'SPR':
        print("working with SPR Test Program")
        Bom = bom_decoder_SPR[new_tp[5:9]]
    #########################################################

    mainTP = new_tp[-4:]
    vpos = "New: "
    vpos += ",".join(lots_old_new["new"])
    vpos += "; Old: "
    vpos += ",".join(lots_old_new["old"])
    print("")
    print("vpos: ", vpos)
    print("")

    # creating a timestamp
    ts = int(time.time())
    st = datetime.fromtimestamp(ts)

    st = str(st)
    part1, part2 = st.split(' ')
    part1 = part1.replace("-", "_")
    part2 = part2.replace(":", "_")
    stamp = '(' + part1 + '_' + part2 + ')'
    print('STAMP:', stamp)

    tp_info = TP(tp_bom="{0}@{1}_{2}".format(location, new_tp, stamp), Bom=Bom, mainTP=mainTP, vpos=vpos)
    tp_info.save()
    all_tps_old = []
    all_tps_new = []
    with open(r"{}\tpi_tools\static\tpi_tools\input_files\rawdata_{}_{}.csv".format(current_dir, location, lot_file_name), 'r') as data:
        for index, line in enumerate(data):
            # print("THIS IS THE INDEX NUMBER --->", index)
            skip_unit = False
            split_line = line.replace("\n", "").split(",")
            print("SPLIT LINE: ", split_line)
            edited_split_line = []
            # headers = ""
            # print("split_line[0]: ", split_line[0])
            if "LOT" in split_line[0]: # --> or "LOT" in split[4]: CAN TRY THIS TO SEE WHAT HAPPENS AFTER
                print("INSIDE FIRST IF STATEMENT")
                for line_item in split_line:
                    print("LINE ITEM:", line_item)
                    #line_item_no_pkg = line_item.replace(r"VIS_ID@7711@[NA]@", r"VIS_ID@GARBAGE@")\
                    #    .replace(r"VIS_ID@7712@[NA]@", r"VIS_ID@GARBAGE@").replace(r"_PKG", "")\
                    #    .replace(r"_[PKG]", "").replace(r"@_7711", "@7711").replace(r"@_7712", "@7712")
                    #line_item_no_pkg = line_item.replace("VIS_ID@7711[NA]@", "VIS_ID@GARBAGE@")\
                    #    .replace("VIS_ID@7712[NA]@", "VIS_ID@GARBAGE@").replace("_PKG", "")\
                    #    .replace("VIS_ID@_7711_[PKG]", "VIS_ID@7711").replace("VIS_ID@_7712_[PKG]", "VIS_ID@7712")
                    #if "6262" in line_item:
                    #    edited_split_line.append(line_item.replace("6262", "6270"))
                    #else:
                    edited_split_line.append(line_item)

                headers = edited_split_line

                # get rv_tps for new and old tp
                # if new_tp[0:3] == 'SPR':
                    # re_old_tp = r'({}\[PKG]\S+{})'.format(unit_header, old_tp[-6:])
                    # re_new_tp = r'({}\[PKG]\S+{})'.format(unit_header, new_tp[-6:])
                # else:
                    # re_old_tp = r'({}\S+{})'.format(unit_header, old_tp[-6:])
                    # re_new_tp = r'({}\S+{})'.format(unit_header, new_tp[-6:])

                re_old_tp = r'({}\S+{})'.format(unit_header, old_tp[-6:])
                re_new_tp = r'({}\S+{})'.format(unit_header, new_tp[-6:])

                # print("RE_OLD_TP: ", re_old_tp)
                # print("RE_NEW_TP: ", re_new_tp)

                for header in headers:
                    # if "PKG" in header:
                    match_old = re.match(re_old_tp, header)
                    match_new = re.match(re_new_tp, header)

                    print("match_old: ", match_old)
                    print("match_new: ", match_new)
                    if match_old:
                        all_tps_old.append(match_old.group(1))
                    if match_new:
                        all_tps_new.append(match_new.group(1))

                    # if match_old and ("PKG" in header):
                        # all_tps_old.append(match_old.group(1))
                    # if match_new and ("PKG" in header):
                        # all_tps_new.append(match_new.group(1))

                    print("all_tps_old: ", all_tps_old)
                    print("all_tps_new: ", all_tps_new)

                print("FOLLOWING IS A LIST OF ALL TPS OLD AND NEW")
                print("{},{}".format(all_tps_old, all_tps_new))
            else:
                print("INSIDE ELSE STATEMENT")
                #headers = ""
                if len(split_line) <= 2:
                    print("ELSE STATEMENT....FIRST IF")
                    continue
                skip_unit = True
                # print("all_tps_old: ", all_tps_old)
                for tpo in all_tps_old:
                    if split_line[headers.index(tpo)] != "":
                        skip_unit = False
                if not skip_unit:
                    print("INSIDE IF NOT STATEMENT")
                    for tpn in all_tps_new:
                        if split_line[headers.index(tpn)] != "":
                            skip_unit = False
                if not skip_unit:
                    skip_unit = True
                    for tpn in all_tps_new:
                        if split_line[headers.index(tpn)] != "":
                            skip_unit = False
                if split_line[headers.index("WAFER")] == "1A" or split_line[headers.index("WAFER")] == "1B" or split_line[headers.index("WAFER")] == "1C":
                    print("SKIPPING UNIT, Not Unit data")
                    continue
                if skip_unit:
                    print("SKIPPING UNIT, missing old or new data")
                    continue
                unit_data[index] = {}
                for header_index, header in enumerate(headers):
                    if header != "GROUP":
                        # print("split_line ------------------> ", split_line[header_index])
                        unit_data[index][header] = split_line[header_index]
        all_tps_old = sorted(all_tps_old, reverse=True)
        all_tps_new = sorted(all_tps_new, reverse=True)
        for unit in unit_data.keys():
            for oldtp in all_tps_old:
                if old_tp[0:3] == 'SPR':
                    if unit_header == "DFF_ULT":
                        oldtp = oldtp[-21:]
                    else:
                        oldtp = oldtp[-19:]
                else:
                    if unit_header == "DFF_ULT":
                        oldtp = oldtp[-21:]
                    else:
                        oldtp = oldtp[-19:]
                        # print("THIS IS THE OLDTP ----------------------> ", oldtp)
                if unit_data[unit]["FB@{}{}@{}_PKG".format(location, group, oldtp)] != "":
                    old_bin = unit_data[unit]["FB@{}{}@{}_PKG".format(location, group, oldtp)] # this is where old_bin is set


                    print("old tp used: {}".format(oldtp))
                    break
            for newtp in all_tps_new:
                if new_tp[0:3] == 'SPR':
                    if unit_header == "DFF_ULT":
                        newtp = newtp[-21:]
                    else:
                        newtp = newtp[-19:]
                else:
                    if unit_header == "DFF_ULT":
                        newtp = newtp[-21:]
                    else:
                        newtp = newtp[-19:]
                        # print("THIS IS THE NEWTP ----------------------> ", newtp)
                if unit_data[unit]["FB@{}{}@{}_PKG".format(location, group, newtp)] != "":
                    new_bin = unit_data[unit]["FB@{}{}@{}_PKG".format(location, group, newtp)] # this is where new_bin is set


                    print("new tp used: {}".format(newtp))
                    break
            if "{}_{}".format(new_bin, old_bin) not in bin_to_bin_count.keys():
                bin_to_bin_count["{}_{}".format(new_bin, old_bin)] = 1
            else:
                bin_to_bin_count["{}_{}".format(new_bin, old_bin)] += 1
            if int(old_bin) not in all_bins["{}@{}".format(location, old_tp)]:
                all_bins["{}@{}".format(location, old_tp)].append(int(old_bin))
            if int(new_bin) not in all_bins["{}@{}".format(location, new_tp)]:
                all_bins["{}@{}".format(location, new_tp)].append(int(new_bin))
            unit_data[unit]["bin_new_old"] = "{}_{}".format(new_bin, old_bin)
            if old_bin != new_bin:
                matching = "No"
                unit_data[unit]["matching"] = matching
            else:
                matching = "Yes"
                unit_data[unit]["matching"] = matching
            all_vmin_data = ""
            all_tester_data = ""
            for data_key in unit_data[unit].keys():
                # print("data_key: ", data_key)
                if "_SRH" in data_key or "_CHK" in data_key:
                    all_vmin_data += "{}~{}`".format(data_key, unit_data[unit][data_key])
                if "TIUID" in data_key:
                    all_tester_data += "{}: {}__".format(data_key, unit_data[unit][data_key])
                if "TIU_PERSONALITY_CARD_ID" in data_key:
                    all_tester_data += "{}: {}__".format(data_key, unit_data[unit][data_key])
                if "SITEID" in data_key:
                    all_tester_data += "{}: {}__".format(data_key, unit_data[unit][data_key])
                if "THERMAL_HEAD" in data_key:
                    all_tester_data += "{}: {}__".format(data_key, unit_data[unit][data_key])
                if "TESTER_ID" in data_key:
                    all_tester_data += "{}: {}__".format(data_key, unit_data[unit][data_key])
            print("SAVING ENTRY TO DB\n\n{}, {}, {}".format(tp_info, unit, newtp))
            new_entry, created = Bin2Bin.objects.get_or_create(tp_name=tp_info, unit=unit_data[unit]["{}@_{}_[PKG]{}@{}".format(unit_header, location, group, newtp)])
            new_entry.old_tp_bom = "{}@{}".format(location, old_tp)
            new_entry.unit = unit_data[unit]["{}@_{}_[PKG]{}@{}".format(unit_header, location, group, newtp)]
            new_entry.tp_name = tp_info
            # new_entry.new_bin = new_bin
            # new_entry.old_bin = old_bin

            print("OLD_BIN BEFORE CALLING BIN MOD FUNCTION: ", old_bin)

            #########################################################
            if new_tp[0:3] == 'CLX':
                print("working with CLX TPs")
                new_entry.new_bin = BinMod(new_bin, r"C:\Users\vabarca\VPO_TEMPLATES\BinDef\Bin_Ref_CLX.txt")
                new_entry.old_bin = BinMod(old_bin, r"C:\Users\vabarca\VPO_TEMPLATES\BinDef\Bin_Ref_CLX.txt")
            elif new_tp[0:3] == 'SKX':
                print("working with SKX TPs")
                new_entry.new_bin = BinMod(new_bin, r"C:\Users\vabarca\VPO_TEMPLATES\BinDef\Bin_Ref_SKX.txt")
                new_entry.old_bin = BinMod(old_bin, r"C:\Users\vabarca\VPO_TEMPLATES\BinDef\Bin_Ref_SKX.txt")
            elif new_tp[0:3] == 'SPR':
                print("working with SPR TPs")
                new_entry.new_bin = BinMod(new_bin, r"C:\Users\vabarca\VPO_TEMPLATES\BinDef\Bin_Ref_SPR.txt")
                new_entry.old_bin = BinMod(old_bin, r"C:\Users\vabarca\VPO_TEMPLATES\BinDef\Bin_Ref_SPR.txt")
            #########################################################
            # new_entry.new_bin = BinMod(new_bin, r"C:\Users\vabarca\VPO_TEMPLATES\BinDef\Bin_Ref.txt")
            # new_entry.old_bin = BinMod(old_bin, r"C:\Users\vabarca\VPO_TEMPLATES\BinDef\Bin_Ref.txt")
            new_entry.explanation = ""
            new_entry.vmin = all_vmin_data
            new_entry.tester_info = all_tester_data
            new_entry.save()
            print("VID: {}, new:{}, old:{}, Matching?:{}".format(unit_data[unit]["{}@_{}_[PKG]{}@{}".format(unit_header, location, group, newtp)],
                                                                 new_bin, old_bin, matching))

            #queue_old_vpo[len(queue_old_vpo) - 1] = 'DONE'


def BinMod_BACKUP(current_bin, BinRef_file):
    candidate = ''
    binLength = len(current_bin)


    hard_bin = int(current_bin) // (10 ** (len(current_bin) - 2))
    # print('CURRENT_BIN: ', current_bin)
    # print('SOFT_BIN: ', soft_bin)

    if (hard_bin == 96 or hard_bin == 98 or hard_bin == 99) and len(current_bin) == 4:
        candidate = current_bin
        return candidate #keeping it blank

    elif int(current_bin) < 800:
        candidate = current_bin + ' (PASS)'
        return candidate # setting it as 'pass'

    else: # looking up failure
        with open(BinRef_file, 'r') as f:
            for line in f:
                part1, part2 = line.split(' ')
                # print('PART1: ', part1)
                # print('CURRENT_BIN: ', current_bin)
                # print('LINE: ', line)

                if part1 == str(current_bin):
                    print('FOUND THE RIGHT STRING')
                    # BinRef_file.close()
                    candidate = line
                    return candidate


def BinMod_BACKUP2(current_bin, BinRef_file):
    binLength = len(current_bin)
    hard_bin = 0

    if binLength == 4: # only done if softbin is 4 digits long,
        hard_bin = int(current_bin) // (10 ** (binLength - 2))

    if hard_bin == 96 or hard_bin == 98 or hard_bin == 99:
        candidate = current_bin
        return candidate  # keeping it blank
    elif int(current_bin) < 800:
        candidate = current_bin + ' (PASS)'
        return candidate  # setting it as 'pass'
    else:  # looking up failure
        with open(BinRef_file, 'r') as f:
            for line in f:
                part1, part2 = line.split(' ')
                # print('PART1: ', part1)
                # print('CURRENT_BIN: ', current_bin)
                # print('LINE: ', line)

                if part1 == str(current_bin):
                    print('FOUND THE RIGHT STRING')
                    candidate = line
                    f.close()
                    return candidate


def BinMod(current_bin, BinRef_file):
    binLength = len(current_bin)
    hard_bin = 0
    print("CURRENT BIN: ", current_bin)

    if binLength == 4: # only done if softbin is 4 digits long,
        hard_bin = int(current_bin) // (10 ** (binLength - 2))
        print("HARD_BIN MODIFIED: ", hard_bin)

    if hard_bin == 96 or hard_bin == 98 or hard_bin == 99:
        candidate = current_bin
        print("FIRST IF STATEMENT")
        return candidate  # keeping it blank
    elif int(current_bin) < 800:
        candidate = current_bin #str(current_bin) + ' (PASS)'
        print("SECOND IF STATEMENT")
        print("CURRENT BIN IS:", current_bin)
        return candidate  # setting it as 'pass'
    else:  # looking up failure
        print("THIRD IF STATEMENT")
        with open(BinRef_file, 'r') as f:
            for line in f:
                part1, part2 = line.split(' ')
                # print('PART1: ', part1)
                # print('CURRENT_BIN: ', current_bin)
                # print('LINE: ', line)

                if part1 == str(current_bin):
                    print('FOUND THE RIGHT STRING')
                    candidate = line
                    f.close()
                    print("CANDIDATE: ", candidate)
                    return candidate


def index(request):
    host_name = "Blank"
    try:
        cookies = request.META['HTTP_COOKIE']
    except:
        return HttpResponse("Error! Please log into Circuit page and try again!")
    split_cookies = cookies.split("; ")
    for cookie in split_cookies:
        if "IDSID" in cookie:
            host_name = cookie[6:]
    return host_name
    # return render(request, 'tpi_tools/home.html', {'user': host_name})


def index_BACKUP(request):
    host_name = "Blank"
    try:
        cookies = request.META['HTTP_COOKIE']
    except:
        return HttpResponse("Error! Please log into Circuit page and try again!")
    split_cookies = cookies.split("; ")
    for cookie in split_cookies:
        if "IDSID" in cookie:
            host_name = cookie[6:]
    return render(request, 'tpi_tools/home.html', {'user': host_name})

def tpi_page(request):
    print("[1] INSIDE tpi_page FUNCTION")
    if request.method == "POST":
        print("TPI_Page")
        form_value = TPIEntry(request.POST)
        # print("form_value:", form_value)

        old_VPOs = form_value['old_VPOs'].value()
        print("old VPOs:", old_VPOs)
        old_TP_Path = form_value['old_TP_Path'].value()
        print("old_TP_Path:", old_TP_Path)
        old_TP_Name = form_value['old_TP_Name'].value()
        print("old_TP_Name:", old_TP_Name)
        new_VPOs = form_value['new_VPOs'].value()
        print("new VPOs:", new_VPOs)
        new_TP_Path = form_value['new_TP_Path'].value()
        print("new_TP_Path:", new_TP_Path)
        new_TP_Name = form_value['new_TP_Name'].value()
        print("new_TP_Name:", new_TP_Name)
        # HOT
        loc_6167 = form_value['loc_6167'].value()
        print("locations:", loc_6167)
        loc_6261 = form_value['loc_6261'].value()
        print("locations:", loc_6261)
        loc_6262 = form_value['loc_6262'].value()
        print("locations:", loc_6262)
        loc_6265 = form_value['loc_6265'].value()
        print("locations:", loc_6265)
        loc_6266 = form_value['loc_6266'].value()
        print("locations:", loc_6266)
        loc_6268 = form_value['loc_6268'].value()
        print("locations:", loc_6268)
        loc_6269 = form_value['loc_6269'].value()
        print("locations:", loc_6269)
        loc_6270 = form_value['loc_6270'].value()
        print("locations:", loc_6270)
        loc_5261 = form_value['loc_5261'].value()
        print("locations:", loc_5261)
        loc_5265 = form_value['loc_5265'].value()
        print("locations:", loc_5265)
        loc_5266 = form_value['loc_5266'].value()
        print("locations:", loc_5266)
        loc_5268 = form_value['loc_5268'].value()
        print("locations:", loc_5268)
        loc_5269 = form_value['loc_5269'].value()
        print("locations:", loc_5269)
        loc_5270 = form_value['loc_5270'].value()
        print("locations:", loc_5270)
        # COLD
        loc_6212 = form_value['loc_6212'].value()
        print("locations:", loc_6212)
        loc_6216 = form_value['loc_6216'].value()
        print("locations:", loc_6216)
        loc_6218 = form_value['loc_6218'].value()
        print("locations:", loc_6218)
        loc_6219 = form_value['loc_6219'].value()
        print("locations:", loc_6219)
        loc_6220 = form_value['loc_6220'].value()
        print("locations:", loc_6220)
        loc_5212 = form_value['loc_5212'].value()
        print("locations:", loc_5212)
        loc_5216 = form_value['loc_5216'].value()
        print("locations:", loc_5216)
        loc_5218 = form_value['loc_5218'].value()
        print("locations:", loc_5218)
        loc_5219 = form_value['loc_5219'].value()
        print("locations:", loc_5219)
        loc_5220 = form_value['loc_5220'].value()
        print("locations:", loc_5220)
        Sites = form_value['Sites'].value()
        print("Site:", Sites)
        print("\n")

        # locations = str(loc_6167) + str(loc_6261) + "," + str(loc_6262) + "," + str(loc_6270) + "," + str(loc_6264) + "," + str(loc_6212) + "," + str(loc_6215)
        hot_locations = [loc_6167, loc_6261, loc_6262, loc_6265, loc_6266, loc_6268, loc_6269, loc_6270, loc_5261, loc_5265, loc_5266, loc_5268, loc_5269, loc_5270]
        cold_locations = [loc_6212, loc_6216, loc_6218, loc_6219, loc_6220, loc_5212, loc_5216, loc_5218, loc_5219, loc_5220]
        locations = hot_locations + cold_locations

        wait_time = 0
        if len(queue_old_VPOs_list) != 0:
            wait_time = ((len(queue_old_VPOs_list) + 1) * 60) # trying a 1 minute wait time

        populateQueues(old_VPOs, new_VPOs, old_TP_Name, new_TP_Name, old_TP_Path, new_TP_Path, locations, Sites)

        if wait_time != 0:
            print("THERE IS A SUBMISSION IN PROGRESS - NEED TO WAIT  ---> ", wait_time, "seconds")
            print("WAITING.....")
            time.sleep(wait_time)
            print("PROCEEDING TO NEXT JOB")

        tracker = 0
        print("THIS IS THE ENTRY LENGTH: ", entry_length)
        if len(entry_length) > 0:
            while tracker < entry_length[0]:
                tracker += 1
                print("INSIDE THE MAIN WHILE LOOP")
                print("WORKING IN THIS LOCATION: ", queue_locations_list[0])

                tpi_tools(queue_old_VPOs_list[0], queue_old_tpNames_list[0], queue_Sites_list[0], queue_timestamp_list[0],
                         queue_new_VPOs_list[0], queue_new_tpNames_list[0], queue_locations_list[0])

                print("RETURNED FROM NEXT FUNCTION")
                print("WILL WAIT FOR 10 SECONDS AS A BUFFER......")

                queue_old_VPOs_list.pop(0)
                queue_old_tpPaths_list.pop(0)
                queue_old_tpNames_list.pop(0)
                queue_new_VPOs_list.pop(0)
                queue_new_tpPaths_list.pop(0)
                queue_new_tpNames_list.pop(0)
                queue_locations_list.pop(0)
                queue_BinDefs_list.pop(0)
                queue_timestamp_list.pop(0)
                queue_username_list.pop(0)
                queue_identifier_list.pop(0)
                queue_Sites_list.pop(0)
                users_identifiers.pop(0)

                time.sleep(10)
                print("DONE WAITING, MOVING ON TO NEXT LOCATION")

            entry_length.pop(0)
        print("DONE WITH CURRENT JOB")
        print("THIS IS THE STATUS OF THE USERS_IDENTIFIERS LIST: ", users_identifiers)

    hostName = index(request)
    template = loader.get_template('tpi_tools/tpi_page.html')
    context = {
        'hostName': hostName,
    }
    return HttpResponse(template.render(context, request))


def populateQueues(old_VPOs, new_VPOs, old_TP_Name, new_TP_Name, old_TP_Path, new_TP_Path, locations, Sites):
    try:
        print("SAVING DATA IN QUEUE\n")

        oldTP_Path = completePath(old_TP_Path, Sites)
        newTP_Path = completePath(new_TP_Path, Sites)
        binDef_Path, current_time = binDefPath(newTP_Path)

        username = 'vabarca' + '_' + str(len(queue_old_VPOs_list))

        entry_length_num = 0
        # steps = locations.split(",")
        # for step in steps:
        for step in locations:
            if step != "None":
                entry_length_num += 1
                queue_old_VPOs_list.append(old_VPOs)
                queue_old_tpPaths_list.append(oldTP_Path)
                queue_old_tpNames_list.append(old_TP_Name)
                queue_new_VPOs_list.append(new_VPOs)
                queue_new_tpPaths_list.append(newTP_Path)
                queue_new_tpNames_list.append(new_TP_Name)
                queue_locations_list.append(step)
                queue_BinDefs_list.append(binDef_Path)
                queue_timestamp_list.append(current_time)
                queue_username_list.append(username)
                queue_identifier_list.append(username + current_time)
                queue_Sites_list.append(Sites)
                users_identifiers.append(username + current_time)
        entry_length.append(entry_length_num)
        print("THIS IS THE LENGTH OF THE QUEUE: ", len(queue_old_VPOs_list))
    except:
        print("NOTHING")


def completePath(TP, Sites):
    # TP_Path = str(TP)
    TP_Path = TP.replace(" ", "")

    sc_drive_full1 = '\\\\amr.corp.intel.com\ec\proj\mdl\sc\intel'
    print("sc_drive_full1 ---> ", sc_drive_full1)
    sc_drive_full2 = '\\\\amr\ec\proj\mdl\sc\intel'

    cr_drive_full1 = '\\\\amr.corp.intel.com\ec\proj\mdl\cr\intel'
    print("cr_drive_full1 ---> ", cr_drive_full1)
    cr_drive_full2 = '\\\\amr\ec\proj\mdl\cr\intel'

    if sc_drive_full1 in TP_Path:
        print("FIRST IF STATEMENT")
        return TP_Path.replace(sc_drive_full1, "I:")
    # return TP
    elif sc_drive_full2 in TP_Path:
        return TP_Path.replace(sc_drive_full2, "I:")
    # return TP
    elif cr_drive_full1 in TP_Path:
        print("THIRD IF STATEMENT")
        return TP_Path.replace(cr_drive_full1, "R:")
    # return TP
    elif cr_drive_full2 in TP_Path:
        return TP_Path.replace(cr_drive_full2, "R:")
    elif (Sites == "SC") or (Sites == "AN"):
        return "I:" + str(TP_Path[2:])
    elif Sites == "CR":
        return "R:" + str(TP_Path[2:])

def completePath_BACKUP(TP, Sites):
    rootPath = ""
    if (Sites == "SC") or (Sites == "AN"):
        rootPath = "I:"
    elif Sites == "CR":
        rootPath = "R:"
    # elif Sites == "AN":
        # rootPath = ""

    # print("THIS IS THE TP PATH --->", TP)
    # print("THIS IS THE TP PATH --->", TP[2:])
    # return rootPath + TP[2:]
    return rootPath + str(TP[2:])



def binDefPath(TP):
    now = datetime.now()
    current_time = now.strftime("%H_%M_%S_%d_%m_%y")

    binDefPath_TP = TP + "\BinDefinitions.bdefs"

    # print("THIS IS THE binDefPath_TP: ", binDefPath_TP)

    binDefFile = "BinDef_file_" + str(current_time) + ".txt"
    binDefPath = "C:/Users/vabarca/VPO_TEMPLATES/BinDef/" + binDefFile

    softBins = "BinGroup SoftBins"
    leafBin = "\t\tLeafBin b"

    softBins_flag = 0
    buffer = ""
    f = open(binDefPath_TP, "r")

    for line in f:
        if softBins in line:
            softBins_flag = 1
        # print("FOUND RIGHT GROUP")
        elif softBins_flag == 1:
            if leafBin in line:
                parsedLine = line.replace(leafBin, "")
                parsedLine = parsedLine.split("_")
                # print("THIS IS THE PARSED LINE --->", parsedLine)
                # print("")
                if len(parsedLine[0]) <= 4:
                    # print("FOUND CORRECT BIN")
                    if "pass" in parsedLine[1]:
                        buffer += str(parsedLine[0]) + "\n"
                    elif "fail" in parsedLine[1]:
                        buffer += str(parsedLine[0]) + "(" + str(parsedLine[2]) + "_" + str(
                            parsedLine[3].split(" ")[0]) + ")" + "\n"

    f.close()

    g = open(binDefPath, "w")
    g.write(buffer)
    g.close()

    return binDefPath, current_time

def tpi_page_BACKUP(request):
    print("[1] INSIDE tpi_page FUNCTION")
    if request.method == "POST":
        print("TPI_Page")
        form_value = TPIEntry(request.POST)
        # print("form_value:", form_value)
        reparse_csv = form_value['reparse_csv'].value()
        print("reparse_csv: ", reparse_csv)
        old_vpo = form_value['old_vpo'].value()
        print("old_vpo:", old_vpo)
        new_vpo = form_value['new_vpo'].value()
        print("new_vpo: ", new_vpo)
        old_tp = form_value['old_tp'].value()
        print("old_tp: ", old_tp)
        new_tp = form_value['new_tp'].value()
        print("new_tp: ", new_tp)
        location = form_value['location'].value()
        print("location: ", location)
        if old_vpo == "" or new_vpo == "" or old_tp == "" or new_tp == "" or location == "":
            return HttpResponse(status=500)
        #############################################################
        # QUEUE
        print("SAVING DATA IN QUEUE\n")
        # ADD DATA TO QUEUE
        queue_old_vpo.add(old_vpo)
        queue_old_tp.add(old_tp)
        queue_new_vpo.add(new_vpo)
        queue_new_tp.add(new_tp)
        queue_location.add(location)
        queue_reparse_csv.add(reparse_csv)

        # Printing length of queue
        print("B2Bs IN THE QUEUE - OLD: ", queue_old_vpo.size())
        print("B2Bs IN THE QUEUE - NEW: ", queue_new_vpo.size())
        #print(queue_old_vpo)
        #print(queue_new_vpo)

        # DETERMINE AND EXECUTE WAIT TIME
        wait_time = (3 * 60) * (queue_old_vpo.size() - 1)
        print("WAIT TIME: ", wait_time, "seconds")
        print("WAITING.....")
        time.sleep(wait_time)
        print("DONE WAITING")

        print("PROCESSING DATA................")
        pos = queue_old_vpo.size() - 1
        print("POS VALUE: ", pos)
        tpi_tools(queue_old_vpo.front(), queue_old_tp.front(), queue_new_vpo.front(), queue_new_tp.front(), queue_location.front(),
                  queue_reparse_csv.front())
        #tpi_tools(queue_old_vpo[pos], queue_old_tp[pos], queue_new_vpo[pos], queue_new_tp[pos], queue_location[pos],
        #         queue_reparse_csv[pos])
        # tpi_tools(queue_old_vpo[pos], queue_old_tp[pos], queue_new_vpo[pos], queue_new_tp[pos], queue_location[pos], queue_reparse_csv[pos])
        print("DONE PROCESSING DATA")

        ###############################################################################
        # MOST RECENT ENTRY HAS BEEN USED, IT NEEDS TO BE DELETED FOR "pos" VARIABLE TO FUNCTION AS INTENDED
        queue_old_vpo.pop()
        queue_old_tp.pop()
        queue_new_vpo.pop()
        queue_new_tp.pop()
        queue_location.pop()
        queue_reparse_csv.pop()
        ###############################################################################

        if queue_old_vpo.size() == 0:
            print("DONE FOR NOW")
        else:
            print("MOVING ON TO NEXT ITEM IN QUEUE")
        ###############################################################
        status = "Finished saving B2B for {}".format(new_tp)
    else:
        status = "Pending, Items currently on the queue: " + str(queue_old_vpo.size())
    return render(request, 'tpi_tools/tpi_page.html', {'status': status})

######################################################################################################################

def tpi_tools(old_vpo, old_tp, site, timestamp, new_vpo, new_tp, location):
    print("[2] INSIDE tpi_tools FUNCTION")
    lots = []
    lots_old_new = {}
    lots_old_new["old"] = []
    lots_old_new["new"] = []
    print('LOTS OLD NEW: ', lots_old_new)
    for ovpo in reversed(old_vpo.replace(" ", "").split(",")):
        lots.append(ovpo)
        lots_old_new["old"].append(ovpo)
    for nvpo in reversed(new_vpo.replace(" ", "").split(",")):
        lots.append(nvpo)
        lots_old_new["new"].append(nvpo)

    if len(lots) > 5:
        lot_file_name = '_'.join(lots[:5])
    else:
        lot_file_name = '_'.join(lots)

    if new_tp[5:7] == "SC":
        template_file = 'template.acs' # bom_to_template_cb_file["SC"]
    else:
        template_file = 'template.acs' # bom_to_template_cb_file[new_tp[7:9]]

    # if not reparse_csv:
    create_cb_script(lots, r'{}\tpi_tools\static\tpi_tools\input_files\{}'.format(current_dir, template_file), location, lot_file_name, site, timestamp)
    execute_cb_script(lot_file_name, location)
    parse_cb_csv_file(lot_file_name, old_tp, new_tp, location, lots_old_new)
    ###############################################################################
    # DATA IN QUEUE GETS CHANGED TO DONE AFTER THE DATA HAS ALREADY BEEN USED
    # queue_old_vpo[pos] = "DONE"
    # queue_old_tp[pos] = "DONE"
    # queue_new_vpo[pos] = "DONE"
    # queue_new_tp[pos] = "DONE"
    # queue_location[pos] = "DONE"
    # queue_reparse_csv[pos] = "DONE"
    ###############################################################################


def tpi_tools_BACKUP(old_vpo, old_tp, new_vpo, new_tp, location, reparse_csv):
    print("[2] INSIDE tpi_tools FUNCTION")
    lots = []
    lots_old_new = {}
    lots_old_new["old"] = []
    lots_old_new["new"] = []
    print('LOTS OLD NEW: ', lots_old_new)
    for ovpo in reversed(old_vpo.replace(" ", "").split(",")):
        lots.append(ovpo)
        lots_old_new["old"].append(ovpo)
    for nvpo in reversed(new_vpo.replace(" ", "").split(",")):
        lots.append(nvpo)
        lots_old_new["new"].append(nvpo)

    if len(lots) > 5:
        lot_file_name = '_'.join(lots[:5])
    else:
        lot_file_name = '_'.join(lots)

    if new_tp[5:7] == "SC":
        template_file = 'template.acs' # bom_to_template_cb_file["SC"]
    else:
        template_file = 'template.acs' # bom_to_template_cb_file[new_tp[7:9]]

    if not reparse_csv:
        create_cb_script(lots, r'{}\tpi_tools\static\tpi_tools\input_files\{}'.format(current_dir, template_file), location, lot_file_name)
        execute_cb_script(lot_file_name, location)
    parse_cb_csv_file(lot_file_name, old_tp, new_tp, location, lots_old_new)
    ###############################################################################
    # DATA IN QUEUE GETS CHANGED TO DONE AFTER THE DATA HAS ALREADY BEEN USED
    # queue_old_vpo[pos] = "DONE"
    # queue_old_tp[pos] = "DONE"
    # queue_new_vpo[pos] = "DONE"
    # queue_new_tp[pos] = "DONE"
    # queue_location[pos] = "DONE"
    # queue_reparse_csv[pos] = "DONE"
    ###############################################################################

###############################################################################################################

import collections

def tps_in_db(request):
    print("Show tps in db")
    hostName = index(request)

    print("\n\nUser: {}".format(hostName))
    tps = {}
    # get list of TPs in database and send to home.html
    mainTPs_in_db = TP.objects.values('mainTP').distinct() # S823, S817,.....
    # print() # debug
    # print("mainTPs_in_db: ", mainTPs_in_db)
    maintp_boms_tps = {}
    ordered_main_tp_boms_tps = {}


    for mainTP in mainTPs_in_db:
        # print("INSIDE FIRST FOR LOOP")
        current_tp = mainTP['mainTP'] # addresses each tp individually
        # print("DEBUGGING")  # debug
        # print("current_tp: ", current_tp)
        # print()
        maintp_boms_tps[current_tp] = {}
        # print("DEBUGGING")  # debug
        # print("maintp_boms_tps: ", maintp_boms_tps)
        # print()
        entries_matching_current_tp = TP.objects.values().filter(mainTP__icontains=current_tp)
        # print("DEBUGGING")  # debug
        # print("entries_matching_current_tp: ", entries_matching_current_tp)
        # print()
        for matching_tp_entry in entries_matching_current_tp:
            # print("INSIDE SECOND FOR LOOP")
            current_bom = matching_tp_entry['Bom']
            maintp_boms_tps[current_tp][current_bom] = []
            entries_matching_current_tp_and_bom = TP.objects.values().filter(mainTP__icontains=current_tp,
                                                                             Bom__icontains=current_bom)
            for matching_tp_and_bom in entries_matching_current_tp_and_bom:
                # print("INSIDE THIRD FOR LOOP")
                current_tp_bom = matching_tp_and_bom['tp_bom']
                maintp_boms_tps[current_tp][current_bom].append(current_tp_bom)
        ordered_main_tp_boms_tps = collections.OrderedDict(sorted(maintp_boms_tps.items(), reverse=True))

        # print(ordered_main_tp_boms_tps)

    hostName = index(request)
    template = loader.get_template('tpi_tools/tps_in_db.html')
    context = {
        'hostName': hostName,
        'maintp_boms_tps': ordered_main_tp_boms_tps
    }
    return HttpResponse(template.render(context, request))


        
        

    # return render(request, 'tpi_tools/tps_in_db.html', {'maintp_boms_tps': ordered_main_tp_boms_tps, 'user': host_name})

# method to direct to VID page
def vid(request, new_tp, unit):
    host_name = "Blank"
    try:
        cookies = request.META['HTTP_COOKIE']
    except:
        return HttpResponse("Error! Please log into Circuit page and try again!")
    split_cookies = cookies.split("; ")
    for cookie in split_cookies:
        if "IDSID" in cookie:
            host_name = cookie[6:]
    sbft_vmins = {}
    cache_vmins = {}
    scan_vmins = {}
    core_disable_instances = []
    entry = Bin2Bin.objects.get(unit=unit, tp_name=new_tp)
    all_vmin_data = entry.vmin
    tester_info = entry.tester_info
    split_tester_info = tester_info.split("__")
    all_content_and_vmin = all_vmin_data.split("`")
    for content_and_vmin in all_content_and_vmin:
        dataset = content_and_vmin.split("~")
        if len(dataset) > 1:
            instance = dataset[0]
            vmin = dataset[1].split("|")[0]
            vmin_split = vmin.split("V")
            if len(vmin_split) < 4:
                vmin_split = []
                vmin_split.append(vmin)

            if "-999V" in vmin:
                core_disable_instances.append(instance)
            if "SBFT" in instance:
                sbft_vmins[instance] = vmin_split
            if "CACHE" in instance:
                cache_vmins[instance] = vmin_split
            if "SCAN" in instance:
                scan_vmins[instance] = vmin_split
    return render(request, 'tpi_tools/vid.html', {'unit': unit, 'new_tp': new_tp, 'sbft_vmins': sbft_vmins,
                                                  'cache_vmins': cache_vmins, 'scan_vmins': scan_vmins,
                                                  'core_disable_instances': core_disable_instances,
                                                  'tester_info': split_tester_info, 'user': host_name})


def create_cb_script(lots, sample_cb_script, location, lot_file_name, site, timestamp):
    print("INSIDE create_cb_script FUNCTION")
    #bom_to_file = {}
    bin2bin_parse = ParseCbAcsFile(sample_cb_script)
    # print("bin2bin_parse: ", bin2bin_parse)
    bin2bin_parse.parse_params()
    params = bin2bin_parse.cb_params
    # global sites
    all_class_locations = ['6262', '6264', '6212', '6270', '6215', '7711', '7712', '6261', '6248']
    if location in all_class_locations:
        sites = ['MIDAS']
        domain = "CLASS"
    elif location == "132310":
        sites = ['D1D']
        domain = "SORT"
    elif location == "6051":
        sites = ['f24']
        domain = "SORT"
    file_name = lot_file_name
    cb_file = open(r'{}\tpi_tools\static\tpi_tools\input_files\raw_data_extract_{}_{}_{}.acs'.format(current_dir, site, location, timestamp), 'w')

    cb_file.write("<!--\n\n")
    cb_file.write(" User: vabarca\n")
    cb_file.write(" Date: Tue Dec 01 12:45:57 2015\n")
    cb_file.write(" CB: CrystalBall_Proto\n")
    cb_file.write("-->\n")
    cb_file.write("\n\n")
    cb_file.write("<!-- %%%%%%%%%%%%%%%%%%%%%%%s Collection %%%%%%%%%%%%%%%%%%%%%%% #TAG -->\n")
    cb_file.write("\n\n")
    # if self.tp_name != "":
    #    cb_file.write("<!--\n")
    cb_file.write("<collection type=material >\n")
    cb_file.write("<group >\n")
    for lotname in lots:
        for site in sites:
            cb_file.write("    {} SITE={} DOMAIN={}\n".format(lotname, site, domain))
    cb_file.write("</group >\n")
    cb_file.write("</collection >\n")
    # if self.tp_name != "":
    #    cb_file.write(" -->\n")
    cb_file.write("\n\n")
    cb_file.write("<!-- %%%%%%%%%%%%%%%%%%%%%%% Parameters %%%%%%%%%%%%%%%%%%%%%%% #TAG -->\n")
    cb_file.write("\n\n")
    cb_file.write("<parameters >\n")
    for site in sites:
        for key in params.keys():
            #<param DATATYPE=FIELD DOMAIN=CLASS FIELD=TESTER_ID OPERATION=6262 SITE=SVC TABLE=SCWAFSUMS />
            print(params[key])
            if 'FIELD' in params[key].keys():
                cb_file.write(" <param DOMAIN={} SITE={} OPERATION={} DATATYPE={} FIELD={} TABLE={} />\n"
                              .format(params[key]['DOMAIN'],
                                      site,
                                      location,
                                      params[key]['DATATYPE'],
                                      params[key]['FIELD'],
                                      params[key]['TABLE']))
                if location == "6270":
                    cb_file.write(" <param DOMAIN={} SITE={} OPERATION={} DATATYPE={} FIELD={} TABLE={} />\n"
                                  .format(params[key]['DOMAIN'],
                                          site,
                                          "6262",
                                          params[key]['DATATYPE'],
                                          params[key]['FIELD'],
                                          params[key]['TABLE']))
            else:
                cb_file.write(" <param DOMAIN={} SITE={} OPERATION={} DATATYPE={} TESTNAME={} />\n"
                              .format(params[key]['DOMAIN'],
                                      site,
                                      location,
                                      params[key]['DATATYPE'],
                                      params[key]['TESTNAME'], ))
                if location == "6270":
                    cb_file.write(" <param DOMAIN={} SITE={} OPERATION={} DATATYPE={} TESTNAME={} />\n"
                              .format(params[key]['DOMAIN'],
                                      site,
                                      "6262",
                                      params[key]['DATATYPE'],
                                      params[key]['TESTNAME'], ))
    cb_file.write("</parameters>\n")
    cb_file.write("\n\n")
    cb_file.write("<!-- %%%%%%%%%%%%%%%%%%%%%%% Analysis %%%%%%%%%%%%%%%%%%%%%%% #TAG -->\n")
    cb_file.write("\n\n")
    cb_file.write("<analysis app=cb  >\n")
    cb_file.write("  TOOL=GIVEMEDATA\n")
    cb_file.write(
        "  /OUTPUT='{}\\tpi_tools\\static\\tpi_tools\\input_files\\rawdata_{}_{}.csv'\n".format(current_dir, location, file_name))
    cb_file.write("  /FORMAT=CSV\n")
    cb_file.write("  /HASCLASS=T\n")
    cb_file.write("  /IGNORE_VHL\n")
    cb_file.write("  /AUTOAKA\n")
    cb_file.write("  /AUTOCONTEXT\n")
    cb_file.write("  /NOMERGESCPROG\n")
    cb_file.write("  /ASMERLIN\n")
    cb_file.write("\n\n")
    cb_file.write("</analysis>\n")
    cb_file.write("\n\n")
    cb_file.close()


def create_cb_script_BACKUP(lots, sample_cb_script, location, lot_file_name):
    print("INSIDE create_cb_script FUNCTION")
    #bom_to_file = {}
    bin2bin_parse = ParseCbAcsFile(sample_cb_script)
    # print("bin2bin_parse: ", bin2bin_parse)
    bin2bin_parse.parse_params()
    params = bin2bin_parse.cb_params
    # global sites
    all_class_locations = ['6262', '6264', '6212', '6270', '6215', '7711', '7712', '6261', '6248']
    if location in all_class_locations:
        sites = ['MIDAS']
        domain = "CLASS"
    elif location == "132310":
        sites = ['D1D']
        domain = "SORT"
    elif location == "6051":
        sites = ['f24']
        domain = "SORT"
    file_name = lot_file_name
    cb_file = open(r'{}\tpi_tools\static\tpi_tools\input_files\raw_data_extract_{}_{}.acs'.format(current_dir, location, file_name), 'w')

    cb_file.write("<!--\n\n")
    cb_file.write(" User: vabarca\n")
    cb_file.write(" Date: Tue Dec 01 12:45:57 2015\n")
    cb_file.write(" CB: CrystalBall_Proto\n")
    cb_file.write("-->\n")
    cb_file.write("\n\n")
    cb_file.write("<!-- %%%%%%%%%%%%%%%%%%%%%%%s Collection %%%%%%%%%%%%%%%%%%%%%%% #TAG -->\n")
    cb_file.write("\n\n")
    # if self.tp_name != "":
    #    cb_file.write("<!--\n")
    cb_file.write("<collection type=material >\n")
    cb_file.write("<group >\n")
    for lotname in lots:
        for site in sites:
            cb_file.write("    {} SITE={} DOMAIN={}\n".format(lotname, site, domain))
    cb_file.write("</group >\n")
    cb_file.write("</collection >\n")
    # if self.tp_name != "":
    #    cb_file.write(" -->\n")
    cb_file.write("\n\n")
    cb_file.write("<!-- %%%%%%%%%%%%%%%%%%%%%%% Parameters %%%%%%%%%%%%%%%%%%%%%%% #TAG -->\n")
    cb_file.write("\n\n")
    cb_file.write("<parameters >\n")
    for site in sites:
        for key in params.keys():
            #<param DATATYPE=FIELD DOMAIN=CLASS FIELD=TESTER_ID OPERATION=6262 SITE=SVC TABLE=SCWAFSUMS />
            print(params[key])
            if 'FIELD' in params[key].keys():
                cb_file.write(" <param DOMAIN={} SITE={} OPERATION={} DATATYPE={} FIELD={} TABLE={} />\n"
                              .format(params[key]['DOMAIN'],
                                      site,
                                      location,
                                      params[key]['DATATYPE'],
                                      params[key]['FIELD'],
                                      params[key]['TABLE']))
                if location == "6270":
                    cb_file.write(" <param DOMAIN={} SITE={} OPERATION={} DATATYPE={} FIELD={} TABLE={} />\n"
                                  .format(params[key]['DOMAIN'],
                                          site,
                                          "6262",
                                          params[key]['DATATYPE'],
                                          params[key]['FIELD'],
                                          params[key]['TABLE']))
            else:
                cb_file.write(" <param DOMAIN={} SITE={} OPERATION={} DATATYPE={} TESTNAME={} />\n"
                              .format(params[key]['DOMAIN'],
                                      site,
                                      location,
                                      params[key]['DATATYPE'],
                                      params[key]['TESTNAME'], ))
                if location == "6270":
                    cb_file.write(" <param DOMAIN={} SITE={} OPERATION={} DATATYPE={} TESTNAME={} />\n"
                              .format(params[key]['DOMAIN'],
                                      site,
                                      "6262",
                                      params[key]['DATATYPE'],
                                      params[key]['TESTNAME'], ))
    cb_file.write("</parameters>\n")
    cb_file.write("\n\n")
    cb_file.write("<!-- %%%%%%%%%%%%%%%%%%%%%%% Analysis %%%%%%%%%%%%%%%%%%%%%%% #TAG -->\n")
    cb_file.write("\n\n")
    cb_file.write("<analysis app=cb  >\n")
    cb_file.write("  TOOL=GIVEMEDATA\n")
    cb_file.write(
        "  /OUTPUT='{}\\tpi_tools\\static\\tpi_tools\\input_files\\rawdata_{}_{}.csv'\n".format(current_dir, location, file_name))
    cb_file.write("  /FORMAT=CSV\n")
    cb_file.write("  /HASCLASS=T\n")
    cb_file.write("  /IGNORE_VHL\n")
    cb_file.write("  /AUTOAKA\n")
    cb_file.write("  /AUTOCONTEXT\n")
    cb_file.write("  /NOMERGESCPROG\n")
    cb_file.write("  /ASMERLIN\n")
    cb_file.write("\n\n")
    cb_file.write("</analysis>\n")
    cb_file.write("\n\n")
    cb_file.close()





def execute_cb_script(file_name, location):
    print("INSIDE execute_cb_script FUNCTION")
    if os.path.isfile(r"{}\tpi_tools\static\tpi_tools\input_files\raw_data_extract_{}_{}.csv".format(current_dir, location, file_name)):
        os.remove(r"{}\tpi_tools\static\tpi_tools\input_files\raw_data_extract_{}_{}.acs".format(current_dir, location, file_name))
    if os.path.isfile(r"{}\tpi_tools\static\tpi_tools\input_files\rawdata_{}_{}.csv".format(current_dir, location, file_name)):
        os.remove(r"{}\tpi_tools\static\tpi_tools\input_files\rawdata_{}_{}.csv".format(current_dir, location, file_name))
    os.system(r"{}\tpi_tools\static\tpi_tools\input_files\raw_data_extract_{}_{}.acs".format(current_dir, location, file_name))
    while os.path.isfile(r"{}\tpi_tools\static\tpi_tools\input_files\rawdata_{}_{}.csv".format(current_dir, location, file_name)) == False:
        time.sleep(2)
    time.sleep(35)

def getProgress(tp_name):
    print("Getting Progress for : {}".format(tp_name))
    #gets the number of explanations left in order to update the progress bar
    entries = Bin2Bin.objects.filter(tp_name=tp_name)
    total = len(entries)
    done = 0
    for entry in entries:
        if entry.explanation != '':
            done = done + 1
    return done

def show_b2b(request, tp_name, no_render=False):
    print("Show B2B")
    host_name = "Blank"
    try:
        cookies = request.META['HTTP_COOKIE']
    except:
        return HttpResponse("Error! Please log into Circuit page and try again!")
    split_cookies = cookies.split("; ")
    for cookie in split_cookies:
        if "IDSID" in cookie:
            host_name = cookie[6:]
    print("\n\nUser: {}".format(host_name))
    # read database entry for current tp_name
    # collect all bins in old and new
    all_bins_old = []
    all_bins_new = []
    bin2bin_count = {}
    old_tp = ""
    tp_entries = Bin2Bin.objects.filter(tp_name=tp_name)
    tp_info = TP.objects.get(tp_bom=tp_name)
    curr_location = tp_name[:4]
    #print(tp_info.vpos)
    vpos_old_new = tp_info.vpos.replace(" ", "").split(";")
    for vpos in vpos_old_new:
        if "New" in vpos:
            new_vpos = vpos.replace("New: ", "").split(",")
        elif "Old" in vpos:
            old_vpos = vpos.replace("Old: ", "").split(",")
    # create the trace mailto link URL
    # trace://site=SC&source=CLASSHDMT&new=IA738008FM_6264&viewMode=Bins/
    email_body = r'Trace B2b: trace%3A%2F%2Fsite%3DCR%26source%3DCLASSHDMT%26new%3D'
    for item in new_vpos:
        email_body += r'{}_{}%252c'.format(item, curr_location)
    email_body += r'ref%3D'
    for item in old_vpos:
        email_body += r'{}_{}%252c'.format(item, curr_location)
    email_body += r'%26viewMode%3DBins'
    # end create trace mailto link URL

    # collect all bins in old and new
    unit_and_explanation = {}
    for tp_entry in tp_entries:
        old_bin = tp_entry.old_bin
        new_bin = tp_entry.new_bin
        old_tp = tp_entry.old_tp_bom
        explanation = tp_entry.explanation
        unit = tp_entry.unit
        unit_and_explanation[unit] = explanation
        if old_bin not in all_bins_old:
            all_bins_old.append(old_bin)
        if new_bin not in all_bins_new:
            all_bins_new.append(new_bin)
        oldbin_newbin = "{}_{}".format(old_bin, new_bin)
        if oldbin_newbin not in bin2bin_count.keys():
            bin2bin_count[oldbin_newbin] = 1
        else:
            bin2bin_count[oldbin_newbin] += 1

    # create b2b_table array to be displayed
    b2b_table_array = []
    header_list = [""]
    for IB in sorted(all_bins_new): # COULD ADD CODE HERE TO MAKE THE B2B TABLE LOOK BETTER --> LOOK AT all_bins_new and all_bins_old
        print("IB: ", IB)
        header_list.append(IB)
    print('HEADER LIST: ', header_list)
    b2b_table_array.append(header_list)
    for index, current_old_bin in enumerate(sorted(all_bins_old)):
        print('INDEX: ', index)
        print('CURRENT_BIN_OLD: ', current_old_bin)
        current_line = [current_old_bin]
        for current_new_bin in sorted(all_bins_new):
            if "{}_{}".format(current_old_bin, current_new_bin) in bin2bin_count:
                current_line.append("{}".format(bin2bin_count["{}_{}".format(current_old_bin, current_new_bin)]))
            else:
                current_line.append("")
        b2b_table_array.append(current_line)
    complete = 0
    progress = 1
    if no_render:
        return {'b2b_table_array': b2b_table_array,
                'tp_entries': tp_entries, 'old_tp': old_tp,
                'new_tp': tp_name, 'new_bins_sorted': sorted(all_bins_new),
                'old_bins_sorted': sorted(all_bins_old),
                'percent_complete': progress, 'vpos_old_new': vpos_old_new,
                'email_body': email_body}
    else:
        curr_uuid = uuid.uuid4()
        request.session['tp_entries_{}'.format(curr_uuid)] = unit_and_explanation
        print("[System] Unit explanation session saved in browser cache!")
        print('tp_entries_{}'.format(curr_uuid))
        return render(request, 'tpi_tools/show_b2b.html', {'b2b_table_array': b2b_table_array,
                                                           'tp_entries': tp_entries, 'old_tp': old_tp,
                                                           'new_tp': tp_name, 'new_bins_sorted': sorted(all_bins_new),
                                                           'old_bins_sorted': sorted(all_bins_old),
                                                           'percent_complete': progress, 'vpos_old_new': vpos_old_new,
                                                           'email_body': email_body, 'user': host_name,
                                                           'session_name': 'tp_entries_{}'.format(curr_uuid)})


def submit_explanations(request):
    print("entering submit explanations")
    og_timestamp = 'empty'
    if request.method == "POST":
        form_value = request.POST
        # print('FORM_VALUE:', form_value)
        session_name = form_value['session_name']
        # print('SESSION NAME: ', session_name)
        host_name = "Blank"
        try:
            tp_entries = request.session[session_name]
            no_tp_entries = False
        except:
            no_tp_entries = True
            print("[System] No explanation table cookie found!")
        try:
            cookies = request.META['HTTP_COOKIE']
        except:
            return HttpResponse("Error! Please log into Circuit page and try again!")
        split_cookies = cookies.split("; ")
        for cookie in split_cookies:
            if "IDSID" in cookie:
                host_name = cookie[6:]
        print("\n\nUser: {}".format(host_name))

        explanations = form_value['explanations'].split("&")



        new_tp = form_value['tp_name']
        #timestamp = new_tp[-22:]
        #og_timestamp = timestamp
        #print('Initial time stamp: ', timestamp)
        #timestamp = timestamp.replace(":", "_")
        #timestamp = timestamp.replace("-", "_")
        #timestamp = timestamp[2:-1]
        #print('TIMESTAMP: ', timestamp)


        #full_tp = new_tp
        #new_tp = new_tp[:-22]
        print('NEW_TP: ', new_tp)
    #with open(r"{}\tpi_tools\static\tpi_tools\input_files\Backup\{}_{}_{}.txt"
                      #.format(current_dir, host_name, time.strftime("%Y_%m_%d__%H_%M_%S"), new_tp), "w") as bf:
    with open(r"{}\tpi_tools\static\tpi_tools\input_files\Backup\{}_{}.txt".format(current_dir, host_name, new_tp), "w") as bf:
        print('INSIDE WITH STATEMENT')
        for explanation in explanations:
            print('INSIDE FOR LOOP')
            print(og_timestamp)
            #explanation = explanation.replace(og_timestamp, "")
            print('EXPLANATION: ', explanation)
            visidtp_and_explanation = explanation.split("=")
            print('visidtp_and_explanation: ', visidtp_and_explanation)


            #visid = visidtp_and_explanation[0].replace("explanation_", "").split("_")[1]
            visid = visidtp_and_explanation[0]
            visid = visid[-13:]

            print('VISID:', visid)
            explain = urllib.parse.unquote(visidtp_and_explanation[1])
            print('EXPLAIN: ', explain)

            #tp_name = urllib.parse.unquote(visidtp_and_explanation[0].replace("explanation_", "").split("_")[0])

            tp_name = urllib.parse.unquote(visidtp_and_explanation[0].replace("explanation_", "").split(")_")[0])
            tp_name = tp_name + ")"  #IT SEEMS LIKE THIS TP HAS TO BE THE SAME AS THE LINK IN THE B2B Page

            print('TP Name: ', tp_name)
            tp_bom_vid_entry = Bin2Bin.objects.get(tp_name=tp_name, unit=visid)
            if not no_tp_entries:
                if visid in tp_entries.keys():
                    if tp_entries[visid] != explain:
                        if explain != "":
                            print("Updating Entry for {}, {}".format(visid, explain))
                            bf.write("visid: {}, Explanation: {}\n".format(visid, explain))
                            tp_bom_vid_entry.explanation = explain
                            tp_bom_vid_entry.save()
                        else:
                            bf.write("Blank Entry: {}\n".format(visid))
                else:
                    if explain != "":
                        print("Updating Entry for {}, {}".format(visid, explain))
                        bf.write("visid: {}, Explanation: {}, HAD COOKIE BUT NO UNIT\n".format(visid, explain))
                        tp_bom_vid_entry.explanation = explain
                        tp_bom_vid_entry.save()
                    else:
                        bf.write("Blank Entry: {},HAD COOKIE BUT NO UNIT\n".format(visid))
            else:
                if explain != "":
                    print("Updating Entry for {}, {}".format(visid, explain))
                    bf.write("visid: {}, Explanation: {}, NO COOKIES for unit!\n".format(visid, explain))
                    tp_bom_vid_entry.explanation = explain
                    tp_bom_vid_entry.save()
                else:
                    bf.write("Blank Entry: {}\n".format(visid))
    bin2bin_dict = show_b2b(request, new_tp, no_render=True)
    return render(request, 'tpi_tools/show_b2b.html', bin2bin_dict)




def submit_explanations_BACKUP(request):
    print("entering submit explanations")
    og_timestamp = 'empty'
    if request.method == "POST":
        form_value = request.POST
        print('FORM_VALUE:', form_value)
        session_name = form_value['session_name']
        print('SESSION NAME: ', session_name)
        host_name = "Blank"
        try:
            tp_entries = request.session[session_name]
            no_tp_entries = False
        except:
            no_tp_entries = True
            print("[System] No explanation table cookie found!")
        try:
            cookies = request.META['HTTP_COOKIE']
        except:
            return HttpResponse("Error! Please log into Circuit page and try again!")
        split_cookies = cookies.split("; ")
        for cookie in split_cookies:
            if "IDSID" in cookie:
                host_name = cookie[6:]
        print("\n\nUser: {}".format(host_name))

        explanations = form_value['explanations'].split("&")



        new_tp = form_value['tp_name']
        timestamp = new_tp[-22:]
        og_timestamp = timestamp
        print('Initial time stamp: ', timestamp)
        timestamp = timestamp.replace(":", "_")
        timestamp = timestamp.replace("-", "_")
        timestamp = timestamp[2:-1]
        print('TIMESTAMP: ', timestamp)


        full_tp = new_tp
        new_tp = new_tp[:-22]
        print('NEW_TP: ', new_tp)
    #with open(r"{}\tpi_tools\static\tpi_tools\input_files\Backup\{}_{}_{}.txt"
                      #.format(current_dir, host_name, time.strftime("%Y_%m_%d__%H_%M_%S"), new_tp), "w") as bf:
    with open(r"{}\tpi_tools\static\tpi_tools\input_files\Backup\{}_{}_{}.txt".format(current_dir, host_name, timestamp, new_tp), "w") as bf:
        print('INSIDE WITH STATEMENT')
        for explanation in explanations:
            print('INSIDE FOR LOOP')
            print(og_timestamp)
            #explanation = explanation.replace(og_timestamp, "")
            print('EXPLANATION: ', explanation)
            visidtp_and_explanation = explanation.split("=")
            print('visidtp_and_explanation: ', visidtp_and_explanation)


            visid = visidtp_and_explanation[0].replace("explanation_", "").split("_")[1]
            print('VISID:', visid)
            explain = urllib.parse.unquote(visidtp_and_explanation[1])
            print('EXPLAIN: ', explain)

            tp_name = urllib.parse.unquote(visidtp_and_explanation[0].replace("explanation_", "").split("_")[0])
            print('TP Name: ', tp_name)
            tp_bom_vid_entry = Bin2Bin.objects.get(tp_name=tp_name, unit=visid)
            if not no_tp_entries:
                if visid in tp_entries.keys():
                    if tp_entries[visid] != explain:
                        if explain != "":
                            print("Updating Entry for {}, {}".format(visid, explain))
                            bf.write("visid: {}, Explanation: {}\n".format(visid, explain))
                            tp_bom_vid_entry.explanation = explain
                            tp_bom_vid_entry.save()
                        else:
                            bf.write("Blank Entry: {}\n".format(visid))
                else:
                    if explain != "":
                        print("Updating Entry for {}, {}".format(visid, explain))
                        bf.write("visid: {}, Explanation: {}, HAD COOKIE BUT NO UNIT\n".format(visid, explain))
                        tp_bom_vid_entry.explanation = explain
                        tp_bom_vid_entry.save()
                    else:
                        bf.write("Blank Entry: {},HAD COOKIE BUT NO UNIT\n".format(visid))
            else:
                if explain != "":
                    print("Updating Entry for {}, {}".format(visid, explain))
                    bf.write("visid: {}, Explanation: {}, NO COOKIES for unit!\n".format(visid, explain))
                    tp_bom_vid_entry.explanation = explain
                    tp_bom_vid_entry.save()
                else:
                    bf.write("Blank Entry: {}\n".format(visid))
    bin2bin_dict = show_b2b(request, new_tp, no_render=True)
    return render(request, 'tpi_tools/show_b2b.html', bin2bin_dict)


def contact(request):
    host_name = "Blank"
    try:
        cookies = request.META['HTTP_COOKIE']
    except:
        return HttpResponse("Error! Please log into Circuit page and try again!")
    split_cookies = cookies.split("; ")
    for cookie in split_cookies:
        if "IDSID" in cookie:
            host_name = cookie[6:]
    return render(request, 'tpi_tools/contact.html', {'user': host_name})

def about(request):
    host_name = "Blank"
    try:
        cookies = request.META['HTTP_COOKIE']
    except:
        return HttpResponse("Error! Please log into Circuit page and try again!")
    split_cookies = cookies.split("; ")
    for cookie in split_cookies:
        if "IDSID" in cookie:
            host_name = cookie[6:]
    return render(request, 'tpi_tools/about.html', {'user': host_name})

def save_b2b(request, tp_name):

    all_bins_old = []
    all_bins_new = []
    bin2bin_count = {}
    old_tp = "EMPTY"
    tp_entries = Bin2Bin.objects.filter(tp_name=tp_name)
    tp_info = TP.objects.get(tp_bom=tp_name)
    for tp_entry in tp_entries:
        old_bin = tp_entry.old_bin[:-2]
        new_bin = tp_entry.new_bin[:-2]
        old_tp = tp_entry.old_tp_bom
        if old_bin not in all_bins_old:
            all_bins_old.append(old_bin)
        if new_bin not in all_bins_new:
            all_bins_new.append(new_bin)
        oldbin_newbin = "{}_{}".format(old_bin, new_bin)
        if oldbin_newbin not in bin2bin_count.keys():
            bin2bin_count[oldbin_newbin] = 1
        else:
            bin2bin_count[oldbin_newbin] += 1
    # create b2b_table array to be displayed
    save_file = "{}_{}_{}.csv".format(old_tp.replace("@", "_"), tp_name.replace("@", "_"),
                                      str(datetime.now().isoformat()).replace(":", "_").replace(".", "__"))
    b2b_table_array = []
    header_list = [""]
    for IB in sorted(all_bins_new):
        header_list.append(IB)
    b2b_table_array.append(header_list)
    for index, current_old_bin in enumerate(sorted(all_bins_old)):
        current_line = [current_old_bin]
        for current_new_bin in sorted(all_bins_new):
            if "{}_{}".format(current_old_bin, current_new_bin) in bin2bin_count:
                current_line.append("{}".format(bin2bin_count["{}_{}".format(current_old_bin, current_new_bin)]))
            else:
                current_line.append("")
        b2b_table_array.append(current_line)
    all_bins_old_full = []
    for entry in tp_entries:
        if entry.old_bin not in all_bins_old_full:
            all_bins_old_full.append(entry.old_bin)
    #create csv file to save
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}_b2b.csv'.format(tp_name)
    writer = csv.writer(response)
    writer.writerow([str(datetime.now().isoformat())])
    writer.writerow([tp_info.vpos])
    writer.writerow(["Old TP(Left->Down): {}".format(old_tp)])
    writer.writerow(["New TP(Top->Right): {}".format(tp_name)])

    for line in b2b_table_array:
        current_line = []
        for cell_value in line:
            current_line.append(cell_value)
        writer.writerow(current_line)
    writer.writerow([])
    writer.writerow(['Visualid', 'Old Bin', 'New Bin', 'Explanation'])
    for bin in sorted(all_bins_old_full):
        for entry in tp_entries:
            if bin in entry.old_bin:
                if entry.old_bin[:-2] != entry.new_bin[:-2]:
                    writer.writerow([entry.unit, entry.old_bin, entry.new_bin, entry.explanation])
    #return render(request, 'tpi_tools/save_b2b.html', {'old_tp': old_tp, 'new_tp': tp_name, })
    return response

def save_b2b_only_explanations(request, tp_name):

    all_bins_old = []
    all_bins_new = []
    bin2bin_count = {}
    old_tp = "EMPTY"
    tp_entries = Bin2Bin.objects.filter(tp_name=tp_name)
    tp_info = TP.objects.get(tp_bom=tp_name)
    for tp_entry in tp_entries:
        old_bin = tp_entry.old_bin[:-2]
        new_bin = tp_entry.new_bin[:-2]
        old_tp = tp_entry.old_tp_bom
        if old_bin not in all_bins_old:
            all_bins_old.append(old_bin)
        if new_bin not in all_bins_new:
            all_bins_new.append(new_bin)
        oldbin_newbin = "{}_{}".format(old_bin, new_bin)
        if oldbin_newbin not in bin2bin_count.keys():
            bin2bin_count[oldbin_newbin] = 1
        else:
            bin2bin_count[oldbin_newbin] += 1
    # create b2b_table array to be displayed
    save_file = "{}_{}_{}.csv".format(old_tp.replace("@", "_"), tp_name.replace("@", "_"),
                                      str(datetime.now().isoformat()).replace(":", "_").replace(".", "__"))
    b2b_table_array = []
    header_list = [""]
    for IB in sorted(all_bins_new):
        header_list.append(IB)
    b2b_table_array.append(header_list)

    all_bins_old_full = []
    for entry in tp_entries:
        if entry.old_bin not in all_bins_old_full:
            all_bins_old_full.append(entry.old_bin)
    #create csv file to save
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}_b2b.csv'.format(tp_name)
    writer = csv.writer(response)

    writer.writerow(['Visualid', 'Old Bin', 'New Bin', 'Explanation'])
    for bin in sorted(all_bins_old_full):
        for entry in tp_entries:
            if bin in entry.old_bin:
                if entry.old_bin[:-2] != entry.new_bin[:-2]:
                    writer.writerow([entry.unit, entry.old_bin, entry.new_bin, entry.explanation])
    #return render(request, 'tpi_tools/save_b2b.html', {'old_tp': old_tp, 'new_tp': tp_name, })
    return response

class ParseCbAcsFile:
    def __init__(self, acs_file):
        self.acs_file = acs_file
        self.cb_params = {}

    def parse_params(self):
        #  open the acs file and parse the <params /> for tokens DOMAIN, TESTNAME, OPERATION, DATATYPE, AKA
        acs_file_obj = open(self.acs_file, 'r')
        print(acs_file_obj)
        #  define the params to search
        params_to_search = ['DOMAIN', 'TESTNAME', 'OPERATION', 'DATATYPE', 'AKA', 'TABLE', 'FIELD']
        param_number = 0
        # search through each param for token in params to search
        for current_line in acs_file_obj:
            if re.search('\s*<param ', current_line) != None:
                params = current_line.split(" ")
                self.cb_params[param_number] = {}
                for param in params:
                    for token in params_to_search:
                        token_value = re.search("{}=(\S+)".format(token), param)
                        if token_value != None:
                            self.cb_params[param_number][token] = token_value.group(1).replace("/>", "")
                param_number += 1

        acs_file_obj.close()

def down(request, hello, down):
    return HttpResponse("Page is currently down :")




