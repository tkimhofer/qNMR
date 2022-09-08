import pandas as pd
import matplotlib.pyplot as plt

s=sample('/Users/TKimhofer/pyt/qNMR/dat/f1/90')


path = '/Users/TKimhofer/pyt/qNMR/dat/covid19_biogune_IVDR02_COVp21_120221/130'
s=sample(path)

# superclass is sample with methods for extracting full res and quant data
class sample:
    def __init__(self, path):
        import os
        import re
        self.exists = False
        self.path_exp = path
        self.idInt = None
        self.path_xml = None
        self._getID()
        self.list_xml()
        if len(self.path_xml) > 0 :
            self.path_quantXml = [(x, os.path.basename(x).split('.xml')[0]) for x in self.path_xml if bool(re.search('.*quant.*|lipo|qc', x))]
            if len(self.path_quantXml) > 0:
                self.exists = True
                self.quant = {}
                for i in range(len(self.path_quantXml)):
                    self._extract_quant(self.path_quantXml[i])

    def _getID(self):
        import os
        import subprocess as sp
        pacqu = os.path.join(self.path_exp, 'acqus')
        out=sp.Popen('grep USERA2 '+ pacqu, stdout=sp.PIPE, stderr=sp.PIPE,  shell=True)
        try:
            iid = str(out.communicate()[0]).split('<')[1].split('>')[0]
            if iid != '':
                self.idInt=str(out.communicate()[0]).split('<')[1].split('>')[0]
            else:
                self.idInt = 'not ID in USERA2'
        except:
            self.idInt = 'not ID in USERA2'



    def list_xml(self):
        import glob, os
        # ['lipo_results', 'plasma_quant_report_ver_1_0', 'PROF_PLASMA_NOESY', 'plasma_qc_report']

        pp=os.path.join(self.path_exp, 'pdata', '1', '*') + '.xml'

        self.path_xml = glob.glob(pp, recursive=True)

    # @staticmethod
    # def _charToFloat(v):
    #     try:
    #         s = float(v)
    #     except:
    #         s = v
    #     return s

    # @staticmethod
    def _metRecurse(self, met, res ={}):
        if len(met) > 1:
            res.update(met[0].attrib)
            self._metRecurse(met[1:], res)
        if len(met) == 1:
            res.update(met[0].attrib)
            return res
        return res

    def _extract_quant(self, fpath):
        import xml.etree.ElementTree as et
        ftree = et.parse(fpath[0])
        results = ftree.getroot().find('QUANTIFICATION')

        feats = {}
        for met in results:
            met_out = {}
            met_out.update(met.attrib)
            met_out = self._metRecurse(met, met_out)

            feats.update({met_out['name']: met_out})
        self.quant.update({fpath[1]: feats})
# cbn sample exp  tenner system
class cohort(sample):
    def __init__(self, root):
        self.root = root
        self.epath = []
        self.nExp = []
        self._idFolder()
        self._map_expSampleFolder()
        self.qCohort = {}
        self.quant = None
        self._get_quant(type='plasma_quant_report')

    def _idFolder(self):
        # find acqus files

        import os
        for root, dirs, files in os.walk(self.root):
            for f in files:
                if f == 'acqus':
                    self.epath.append(root)

    def _map_expSampleFolder(self):
        import  numpy as np
        A = set()
        smap = {}
        dd =  self.epath
        for i in dd:
            s = i[0:-1]
            if s in A:
                smap.update({s: smap[s] + [i]})
            else:
                smap.update({s: [i]})
                A.add(s)
        self.smap = smap

        # remove calibration experiments
        keep = {}
        for i in self.smap:
            ele = self.smap[i]
            if type(ele) is list:
               if any([j[-1]=='0' for j in ele]):
                   keep.update({i: self.smap[i]})
                   self.nExp.append(len( self.smap[i]))

        self.smap  = keep
        print(f'Number of samples {len( self.smap)}')
        print(f'Number of experiments per sample {np.median(self.nExp)} ({np.min(self.nExp)}-{np.max(self.nExp)})')


    # extract quant from experiments and check if more than one exists for a single sample
    def _get_quant(self, type='plasma_quant_report'):
        import numpy as np
        import pandas as pd
        sc = []
        res = {}
        conc = {}
        iids = []
        quant_type = []
        for i in  self.smap: # for each sample
            # single sample, multiple experiments
            sample_count = 0
            for fi in  self.smap[i]: # for each experiment
                tt = sample(fi)
                if tt.exists: # quant data available
                    # include summary how many quant data sets for the cohort (e.g., 80% small molecule v1, ...)
                    if 'plasma_quant_report' in tt.quant.keys():
                        iids.append(tt.idInt)
                        try:
                            quant_type = quant_type + [x[1] for x in s.path_quantXml]
                        except:
                            raise(ValueError('quantXML not there'))
                       # if 'plasma_quant_report' not in list(res):
                        #print(i)
                        #res.update({i: {}})
                        df = pd.DataFrame(tt.quant['plasma_quant_report']).T
                        df['id'] = fi
                        df = df.T
                        #res[i].update({fi: df})
                        conc.update({fi: df.T.conc})
                        sample_count += 1
            sc.append(sample_count)

        print(f'Quant experiment type distribution: {np.unique(quant_type, return_counts=True)[0]}')
        # print(f'Samples with multiple quant results {len(np.where(np.array(sc) ==0)[0])}')
        # print(f'Samples without quant results {len(np.where(np.array(sc) >1)[0])}')

        #print(np.array(list(self.smap.keys()))[np.where(np.array(sc) > 1)[0]])
        #print(np.array(list(self.smap.keys()))[np.where(np.array(sc) ==0)[0]])

        inter = pd.DataFrame(conc).T
        self.quant = inter.apply(pd.to_numeric)
        self.quant['iid'] = iids

    #
    #
    # @staticmethod
    # def extractValRecurse(ele):
    #     if len(ele) > 1:
    #         pass
    #     else:
    #         conc = {}
    #         for i in ele:
    #             conc.update({i: ele[i]['conc']})
    #
    #
    # def tableQuant(self, type):
    #     import pandas as pd
    #     type = 'plasma_quant_report_ver_1_0'
    #
    #     pd.DataFrame(qCohort['/Users/TKimhofer/pyt/qNMR/dat/f2/6'][])
    #
    #     for i in self.qCohort

c = cohort('/Users/TKimhofer/pyt/qNMR/dat/')
c.quant.to_excel('/Users/TKimhofer/pyt/qNMR/dat/quant.xlsx')

import numpy as np
plt.scatter(c.quant.Glucose, c.quant['Lactic acid'])
np.where(c.quant.iid.str.contains('HC-COVID0437').values)

import pickle

pickle.dump(c.quant, open('nmr_quant_aliquot1.pkl', 'bw'))









