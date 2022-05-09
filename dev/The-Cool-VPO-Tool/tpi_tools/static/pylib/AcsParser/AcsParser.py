import re

class ParseCbAcsFile:

    def __init__(self, acs_file):
        self.acs_file = acs_file
        self.cb_params = {}

    def parse_params(self):
        #  open the acs file and parse the <params /> for tokens DOMAIN, TESTNAME, OPERATION, DATATYPE, AKA
        acs_file_obj = open(self.acs_file, 'r')
        print "Opening {}".format(self.acs_file)
        #  define the params to search
        params_to_search = ['DOMAIN', 'TESTNAME', 'OPERATION', 'DATATYPE', 'AKA']

        param_number = 0
        # search through each param for token in params to search
        for line in acs_file_obj:
            if re.search('\s*<param ', line) > 0:
                params = line.split(" ")
                self.cb_params[param_number] = {}
                for param in params:
                    for token in params_to_search:
                        token_value = re.search("{}=(\S+)".format(token), param)
                        if token_value > 0:
                            self.cb_params[param_number][token] = token_value.group(1).replace("/>", "")
                param_number += 1

        acs_file_obj.close()

