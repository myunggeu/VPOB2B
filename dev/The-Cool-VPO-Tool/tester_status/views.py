from django.shortcuts import render
from django.http import HttpResponse
from tester_status.models import TESTER, STATUS, RESERVATION
from datetime import datetime, timedelta
from django.utils import timezone
import json
from django.core.serializers.json import DjangoJSONEncoder
testers = {'CR':[1455, 1701, 1785],
           }
cells = ['A101', 'A102',
         'A201', 'A202',
         'A301', 'A302',
         'A401', 'A402',
         'A501', 'A502',
         ]

def add_testers(request):
    for site in testers.keys():
        for tester_name in testers[site]:
            for cell in cells:
                tester_entry, is_new_tester = TESTER.objects.update_or_create(site=site, tester_name=tester_name, cell=cell)
                tester_entry.save()
    return HttpResponse("ok")

# Create your views here.
def tester_status(request):
    print("[System] -- Main Tester Status page")
    '''Main tester status view'''
    tester_dict = {}

    # fetch entries in DB to send to main page
    #   All testers/cells available for all sites
    #   Cell level status entries for all testers/cells/sites fetched
    tester_objs = TESTER.objects.all()
    for tester_obj in tester_objs:

        #fill in dictionary with site/tester id/cell names available in DB
        if tester_obj.site not in tester_dict.keys():
            tester_dict[tester_obj.site] = {}
        if tester_obj.tester_name not in tester_dict[tester_obj.site].keys():
            tester_dict[tester_obj.site][tester_obj.tester_name] = []
        if tester_obj.cell not in tester_dict[tester_obj.site][tester_obj.tester_name]:
            tester_dict[tester_obj.site][tester_obj.tester_name].append(tester_obj.cell)

    #fill in list with status entries for all tester/cells in each site
    # site = [[status entry 1],[status entry 2],[status entry3]]
    status_objs = STATUS.objects.all()
    status_list = []
    for status_obj in status_objs:
        tester_obj = TESTER.objects.get(id=status_obj.tester_id)
        if not status_obj.status_up:
            status = "DOWN, {}".format(status_obj.details)
            style = "red"
        else:
            status = "UP"
            style = "green"
        details = ['{}-{}:{}'.format(tester_obj.site, tester_obj.tester_name,tester_obj.cell), status, style,
                       status_obj.start_time, status_obj.end_time]
        status_list.append(details)
    return render(request, 'tester_status.html', {'testers': tester_dict,
                                                  'status': json.dumps(status_list, cls=DjangoJSONEncoder)})

def tester_up_down(request):
    '''
    Details: Used to signal the tester as down.
    :param request:
    :param site: Site which tester is located
    :param tester_name: Tester ID
    :param cell: Cell name
    :param reason: Reason why tester is down
    :return:
    '''
    print("[System] -- Entering Tester Down/UP")

    site = request.POST['loc']
    tester_name = request.POST['tester_id']
    cell = request.POST['cell']
    reason = request.POST['reason']
    print("Site: {} Tester Name: {} Cell: {} Reason Down: {}\n".format(site, tester_name, cell, reason))
    tester_entry = TESTER.objects.get(site=site, tester_name=tester_name, cell=cell)
    ## update previous entry's end_time to current time
    previous_entries = STATUS.objects.filter(tester_id=tester_entry.id)
    if previous_entries:
        previous_entry = previous_entries.latest('end_time')
        previous_entry.end_time = timezone.now()
        previous_entry.save()
    ## add new entry
    end_time_pre = timezone.now()
    #set end time to now + 7 days until the status is updated
    end_time = end_time_pre + timezone.timedelta(hours=12)
    print(end_time)
    if reason == "":
        status_up = True
    else:
        status_up = False
    status_entry = STATUS.objects.create(tester_id=tester_entry.id, status_up=status_up, details=reason, start_time=timezone.now(), end_time=end_time)
    status_entry.save()
    return HttpResponse(site + tester_name + cell + reason)

def tester_up(request, site, tester_name, cell):


    return HttpResponse(site + tester_name + cell)