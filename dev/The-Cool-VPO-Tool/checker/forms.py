from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class TPEntry(forms.Form):
    tp = forms.CharField()
    xccsph0 = forms.BooleanField()
    xccdfh0 = forms.BooleanField()
    hccspm0 = forms.BooleanField()
    hccsrm0 = forms.BooleanField()
    hccdem2 = forms.BooleanField()
    lccspu0 = forms.BooleanField()
    lccsru0 = forms.BooleanField()
    xccsph1 = forms.BooleanField()
    xccdfh1 = forms.BooleanField()
    hccspm1 = forms.BooleanField()
    hccsrm1 = forms.BooleanField()
    hccdem1 = forms.BooleanField()
    lccspu1 = forms.BooleanField()
    lccsru1 = forms.BooleanField()
    xccdph1 = forms.BooleanField()
    xccspj0 = forms.BooleanField()
    xccspk0 = forms.BooleanField()
    xccdmh1 = forms.BooleanField()
    hccspn0 = forms.BooleanField()
    hccsrn0 = forms.BooleanField()
    lccspv0 = forms.BooleanField()
    lccsrv0 = forms.BooleanField()
    xccsp_jtdh1 = forms.BooleanField()
    ##################################
    hccsr_stim = forms.BooleanField()
    xcc64lk0 = forms.BooleanField()
    xcc64lk1 = forms.BooleanField()
    xccspk1 = forms.BooleanField()
    xccapk0 = forms.BooleanField()
    hccsrn1 = forms.BooleanField()
    ##################################
    xccspa0 = forms.BooleanField()
    xccspa1 = forms.BooleanField()
    xccspa2 = forms.BooleanField()
    xccspb0 = forms.BooleanField()
    xccspc0 = forms.BooleanField()
    xccspc1 = forms.BooleanField()
    xcc112La0 = forms.BooleanField()
    xccspd0 = forms.BooleanField()
    xccspsrha0 = forms.BooleanField()
    ##################################

    ww = forms.IntegerField()
    tp_select = forms.CharField()


class VPOEntry(forms.Form):
    vpo = forms.CharField()
    bom = forms.CharField()
    locs = forms.CharField()
    date = forms.CharField()

