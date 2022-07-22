from collections import Counter
from elixhauser_comorbidity_index.eci_icd10_map import dx2elix

class ElixhauserEngine:
    def __init__(self):
        self.dx2elix = dx2elix

        # NOTE: weights are adopted from the following link
        # https://www.hcup-us.ahrq.gov/toolssoftware/comorbidity/comindex2012-2015.txt
        self.weights = {
            "readmission": {
                "AIDS": 19, "ALCOHOL": 6, "ANEMDEF": 9, "ARTH": 4,
                "BLDLOSS": 3, "CHF": 13, "CHRNLUNG": 8, "COAG": 7,
                "DEPRESS": 4, "DM": 6, "DMCX": 9, "DRUG": 14,
                "HTN_C": -1, "HYPOTHY": 0, "LIVER": 10, "LYMPH": 16,
                "LYTES": 8, "METS": 21, "NEURO": 7, "OBESE": -3,
                "PARA": 6, "PERIVASC": 4, "PSYCH": 10, "PULMCIRC": 5,
                "RENLFAIL": 15, "TUMOR": 15, "ULCER": 0, "VALVE": 0,
                "WGHTLOSS": 10
                },
            "mortality": {
                "AIDS": 0, "ALCOHOL": -1, "ANEMDEF": -2, "ARTH": 0,
                "BLDLOSS": -3, "CHF": 9, "CHRNLUNG": 3, "COAG": 11,
                "DEPRESS": -5, "DM": 0, "DMCX": -3, "DRUG": -7,
                "HTN_C": -1, "HYPOTHY": 0, "LIVER": 4, "LYMPH": 6,
                "LYTES": 11, "METS": 14, "NEURO": 5, "OBESE": -5,
                "PARA": 5, "PERIVASC": 3, "PSYCH": -5, "PULMCIRC": 6,
                "RENLFAIL": 6, "TUMOR": 7, "ULCER": 0, "VALVE": 0,
                "WGHTLOSS": 9
                }
            }

    def get_elixhauser(self, dx_lst):
        """
        Returns the Elixhauser Comorbidity Index for the given list of 
        diagnosis codes.
        The original software can be found at
        https://www.hcup-us.ahrq.gov/toolssoftware/comorbidityicd10/
            comorbidity_icd10.jsp

        Parameters
        __________
        icd_lst: list of str
                A list of ICD10 diagnosis codes.
        """

        def search(dx):
            cmrbdt = ""
            for i in range(4, 8):
                dx_shrt = dx[:i]
                if dx_shrt in self.dx2elix:
                    cmrbdt = self.dx2elix[dx_shrt]      
                    break
            return cmrbdt

        def apply_hierarchy(rawgrp_lst):
            cmrbdt_cnt = Counter()
            hpn_set = {"HTNPREG", "HTNWOCHF", "HTNWCHF",
                        "HRENWORF", "HRENWRF",
                        "HHRWOHRF", "HHRWCHF", "HHRWRF", "HHRWHRF",
                        "OHTNPREG"}
            for rawgrp in rawgrp_lst:
                if rawgrp in hpn_set:
                    cmrbdt_cnt["HTNCX"] = 1
                    if rawgrp in {"HTNWCHF", "HHRWCHF", "HHRWHRF"}:
                        cmrbdt_cnt["CHF"] = 1
                    if rawgrp in {"HRENWRF", "HHRWRF", "HHRWHRF"}:
                        cmrbdt_cnt["RENLFAIL"] = 1
                else:
                    cmrbdt_cnt[rawgrp] = 1
            if cmrbdt_cnt["HTNCX"] > 0:
                cmrbdt_cnt["HTN"] = 0
            if cmrbdt_cnt["METS"] > 0:
                cmrbdt_cnt["TUMOR"] = 0
            if cmrbdt_cnt["DMCX"] > 0:
                cmrbdt_cnt["DM"] = 0
            cmrbdt_lst = [cmrbdt for cmrbdt, cnt in cmrbdt_cnt.items() 
                        if cnt > 0]
            return cmrbdt_lst

        def apply_score(cmrbdt_lst, model="readmission"):
            score = 0
            for cmrbdt in cmrbdt_lst:
                if cmrbdt in {"HTNCX", "HTN"}:
                    score += self.weights[model]["HTN_C"]
                else:
                    score += self.weights[model][cmrbdt]
            return score

        if not isinstance(dx_lst, list):
            dx_lst = [dx_lst]
 
        dx_set = {dx.strip().upper().replace(".","") for dx in dx_lst} 
        rawgrp_lst = [grp for grp in {search(dx) for dx in dx_set}
                        if grp not in {"", "NONE"}]
        cmrbdt_lst = apply_hierarchy(rawgrp_lst) 

        readmission_scr = apply_score(cmrbdt_lst, "readmission")
        mortality_scr = apply_score(cmrbdt_lst, "mortality")

        out = {"cmrbdt_lst": cmrbdt_lst,
                "readmission_scr": readmission_scr,
                "mortality_scr": mortality_scr}

        return out

# import re
# def read_elixhauser():
#     dx2elix = {}
#     with open("D:\\Users\\snagapuri\\Elixhauser_comorbidity_index\\elix_comformat_icd10cm_2019_1.txt", "r") as fp:
#         start = False
#         end = False
#         dxlst = []
#         for line in fp.readlines():
#             if line.strip() == "Value $RCOMFMT":
#                 start = True
#             if start and line.strip()==";":
#                 end = True
#                 break
#             if start and not end:
#                 if "=" in line:
#                     pttr = r"\"(.*)\"=\"(.*)\""
#                     matches = re.findall(pttr, line)
#                     if len(matches) > 0 and len(matches[0]) == 2:
#                         dx, elix = matches[0][0], matches[0][1]
#                         dxlst.append(dx)
#                         for dx in dxlst:
#                             dx2elix[dx] = elix
#                         dxlst = []
#                 elif "," in line:
#                     pttr = r"\"(.*)\","
#                     matches = re.findall(pttr, line)
#                     if len(matches) > 0:
#                         dx = matches[0]
#                         dxlst.append(dx)
#     return dx2elix


# with open("D:\\Users\\snagapuri\\Elixhauser_comorbidity_index\\eci_icd10_map", "w") as fp:
#     w = read_elixhauser()
#     fp.write("dx2elix = " + str(w))
