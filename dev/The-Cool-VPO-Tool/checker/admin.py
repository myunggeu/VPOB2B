from django.contrib import admin
from checker.models import VPO_DESC, VPO_LOC, Plan, PLAN_STATUS

admin.site.register(PLAN_STATUS)
admin.site.register(VPO_DESC)
admin.site.register(VPO_LOC)
admin.site.register(Plan)

# Register your models here.
