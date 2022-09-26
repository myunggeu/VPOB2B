from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

class PostExplanation(forms.Form):
    explanation = forms.CharField()

class TPIEntry(forms.Form):
    old_VPOs = forms.CharField()
    new_VPOs = forms.CharField()
    old_TP_Name = forms.CharField()
    new_TP_Name = forms.CharField()
    old_TP_Path = forms.CharField()
    new_TP_Path = forms.CharField()
    # locations = forms.CharField()
    # loc_6264 = forms.CharField()
    # loc_6215 = forms.CharField()
    # HOT
    loc_6092 = forms.CharField()
    loc_6163 = forms.CharField()
    loc_6167 = forms.CharField()
    loc_6193 = forms.CharField()
    loc_6208 = forms.CharField()
    loc_6242 = forms.CharField()
    loc_6245 = forms.CharField()
    loc_6260 = forms.CharField()
    loc_6261 = forms.CharField()
    loc_6262 = forms.CharField()
    loc_6263 = forms.CharField()
    loc_6265 = forms.CharField()
    loc_6266 = forms.CharField()
    loc_6268 = forms.CharField()
    loc_6269 = forms.CharField()
    loc_6270 = forms.CharField()
    loc_5193 = forms.CharField()
    loc_5242 = forms.CharField()
    loc_5260 = forms.CharField()
    loc_5261 = forms.CharField()
    loc_5263 = forms.CharField()
    loc_5265 = forms.CharField()
    loc_5266 = forms.CharField()
    loc_5268 = forms.CharField()
    loc_5269 = forms.CharField()
    loc_5270 = forms.CharField()
    # COLD
    loc_6212 = forms.CharField()
    loc_6213 = forms.CharField()
    loc_6216 = forms.CharField()
    loc_6218 = forms.CharField()
    loc_6219 = forms.CharField()
    loc_6220 = forms.CharField()
    loc_6243 = forms.CharField()
    loc_6254 = forms.CharField()
    loc_5212 = forms.CharField()
    loc_5213 = forms.CharField()
    loc_5216 = forms.CharField()
    loc_5218 = forms.CharField()
    loc_5219 = forms.CharField()
    loc_5220 = forms.CharField()
    Sites = forms.CharField()

    def __str__(self):
        return self.new_TP_Name + "_" + self.old_TP_Name + "_" + self.Sites # + "_" + self.timestamp

    # old_vpo = forms.CharField()
    # new_vpo = forms.CharField()
    # old_tp = forms.CharField()
    # new_tp = forms.CharField()
    # location = forms.CharField()
    # reparse_csv = forms.BooleanField(required=False)

    # def __str__(self):
        # return self.new_tp + '-' + self.location





