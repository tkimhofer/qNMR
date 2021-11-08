m#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:32:08 2020

@author: TKimhofer
"""

import glob
import xml.etree.ElementTree as et
import pandas as pd
import os



def list_files(path, ft='urine_quant_report_e_ver_1_0'):
#     path - list all xml files in dir and subdirs
#     type - stringmatch with file name
    
    files=glob.glob(path+'/**/*'+ft+'.xml', recursive=True)
    return(files)


def extract_plasmaQC(files):
    fil_out=list()

    for f in files:
        ftree = et.parse(f)
        res = ftree.getroot()

        tst=res.find('SAMPLE')

        
        sample_out=[]
        for met in tst.iter('INFO'):
            # this is creatinine
            out = {
                    'param': met.attrib.get('name'),
                    f: met.attrib.get('value')
                    }
            sample_out.append(out)
            
            
            
        
        #pd.DataFrame.from_dict(sample_out)
        
        
        tst=res.find('QUANTIFICATION')
        
        specQC_out=[]
        prepQC_out=[]
        matInteg_out=[]
        contam_out=[]
        for met in tst.iter('PARAMETER'):
            print(met.attrib.get('type'))
            if(met.attrib.get('type') == 'NMR Spectral Quality'):
                out = {
                    'param': met.attrib.get('name'),
                    'value': met.attrib.get('comment')
                    }
                specQC_out.append(out)
            if(met.attrib.get('type') == 'NMR Preparation Quality'):
                out = {
                    'param': met.attrib.get('name'),
                    'value': met.attrib.get('comment')
                    }
                prepQC_out.append(out)
            if(met.attrib.get('type') == 'Matrix Integrity Test : Conc.'):
                out = {
                    'param': met.attrib.get('name')+' Conc',
                    'value': met.attrib.get('comment')
                    }
                matInteg_out.append(out)
            if(met.attrib.get('type') == 'Matrix Integrity Test : Shift'):
                out = {
                    'param': met.attrib.get('name')+' Shift',
                    'value': met.attrib.get('comment')
                    }
                matInteg_out.append(out)
            if(met.attrib.get('type') == 'Contamination Test'):
                out = {
                    'param': met.attrib.get('name'),
                    'value': met.attrib.get('comment')
                    }
                contam_out.append(out)    
           
 
        fil_out.append(list([pd.DataFrame.from_dict(sample_out), 
                             pd.DataFrame.from_dict(specQC_out),
                             pd.DataFrame.from_dict(prepQC_out),
                             pd.DataFrame.from_dict(matInteg_out),
                             pd.DataFrame.from_dict(contam_out)
                             ]))
    return(fil_out)
    

def extract_lipo(files):
    fil_out=list()

    for f in files:
        ftree = et.parse(f)
        results = ftree.getroot().find('QUANTIFICATION')

        met_out=[]
        for met in results:
            # this is creatinine
            met_name_out=met.attrib.get('name')
            out = {
                    'param': met.attrib.get('comment'),
                    'unit': met.find('VALUE').attrib.get('unit'),
                    'value': convertChartoFloat(met.find('VALUE').attrib.get('value')),
                    'lod': convertChartoFloat(met.find('VALUE').attrib.get('lod')),
                    'loq': convertChartoFloat(met.find('VALUE').attrib.get('loq'))
                    }
            met_out.append([met_name_out, f,  out])
        fil_out.append(met_out)
    return(fil_out)





def extract_uquant_b(files):
    fil_out=list()

    for f in files:
        ftree = et.parse(f)
        results = ftree.getroot().find('QUANTIFICATION')

        met_out=[]
        for met in results:
            # this is creatinine
            met_name_out=met.attrib.get('name')
            out = {
                    'unit': met.find('VALUE').attrib.get('concUnit'),
                    'value': convertChartoFloat(met.find('VALUE').attrib.get('conc')),
                    #'valueext': convertChartoFloat(met.find('VALUE').attrib.get('valueext')),
                    'lod': convertChartoFloat(met.find('VALUE').attrib.get('lod')),
                    'loq': convertChartoFloat(met.find('VALUE').attrib.get('loq'))
                  
                    }
            
            if(len(list(met))>3):
                out1 = {
                    'unit': met.find('VALUERELATIVE').attrib.get('concUnit'),
                    'value': convertChartoFloat(met.find('VALUERELATIVE').attrib.get('conc')),
                    'lod': convertChartoFloat(met.find('VALUERELATIVE').attrib.get('lod')),
                    'loq': convertChartoFloat(met.find('VALUERELATIVE').attrib.get('loq'))
                    }
                met_out.append([met_name_out,  f, out, out1])                
            else:
                met_out.append([met_name_out, f,  out])
        fil_out.append(met_out)
    return(fil_out)




def extract_uquant_e(files):
    fil_out=list()

    for f in files:
        ftree = et.parse(f)
        results = ftree.getroot().find('QUANTIFICATION')

        met_out=[]
        for met in results:
            met_name_out=met.attrib.get('name')
            out = {
                    'unit': met.find('VALUE').attrib.get('unit'),
                    'value': convertChartoFloat(met.find('VALUE').attrib.get('value')),
                    'valueext': convertChartoFloat(met.find('VALUE').attrib.get('valueext')),
                    'lod': convertChartoFloat(met.find('VALUE').attrib.get('lod')),
                    'loq': convertChartoFloat(met.find('VALUE').attrib.get('loq'))
                    }
            
            if out.get('value') != out.get('valueext'):
                print('Parameter values in attribute value and valueext are not identical')
                return
            
            if len(met.findall('VALUE')) >1 :
                met1=met.findall('VALUE')[1]
                out1 = {
                    'unit': met1.attrib.get('unit'),
                    'value': convertChartoFloat(met1.attrib.get('value')),
                    'valueext': convertChartoFloat(met1.attrib.get('valueext')),
                    'lod': convertChartoFloat(met1.attrib.get('lod')),
                    'loq': convertChartoFloat(met1.attrib.get('loq'))
                    }
                met_out.append([met_name_out,  f, out, out1])                
            else:
                met_out.append([met_name_out, f,  out])
        fil_out.append(met_out)
    return(fil_out)



def create_tbl(extr, unit='mmol/L'):
    

    #unit present?
    id=-1
    for un in range(2,len(extr[0][1])):
        if(extr[0][1][un].get('unit')==unit):
            id=un
    
    if id == (-1):
        print('Unit '+unit+' not found')
        return
    #mout=pd.DataFrame(columns=['ID', 'Unit', 'LOD', 'LOQ'])
    
    metIds=[]
    add=[]
    for me in extr[0]:
        metIds.append(me[0])
        if(len(me)>id):
            add.append([me[0], me[id].get('unit'), me[id].get('lod'), me[id].get('loq')])
        else:
            add.append([me[0], '-', '-', '-', ])
        
    mout=pd.DataFrame(add, columns=['ID', 'Unit', 'LOD', 'LOQ'])
    
    
    files=[]
    for me in extr:
        files.append(me[0][1])
        
    dout=pd.DataFrame(index=files, columns=metIds)
    
    for i_file in range(len(extr)): # for evert file
        mets=[]
        for i_met in range(len(extr[i_file])): # for every metabolite
            if(len(extr[i_file][i_met])>id):
                mets.append(extr[i_file][i_met][id].get('value')) 
            else: 
                mets.append('-')
        dout.iloc[i_file]=mets
    
    return([dout, mout])
    

        
def convertChartoFloat(instr):
    if instr.isdigit() == True:
        return float(instr)
    else: 
        return(instr)


def collate_Bruker_MetaboliteFits(path, ftype='e'):
    
    if not path.endswith(os.path.sep):
        path += os.path.sep
    
    if(ftype=='e'):
        rawData_ur=list_files(path, ft='urine_quant_report_e_ver_1_0')
    if(ftype=='b'):
        rawData_ur=list_files(path, ft='urine_quant_report_b')
       
    
    if(len(rawData_ur)>0):
        if(ftype=='e'):
            extrData=extract_uquant_e(rawData_ur)
        if(ftype=='b'):
            extrData=extract_uquant_b(rawData_ur)
    
        tbls_mmolL=create_tbl(extrData, unit='mmol/L')
    
        # generate excel files
        writer = pd.ExcelWriter(path+ftype+'Met_fits.xlsx', engine='xlsxwriter')
        tbls_mmolL[0].to_excel(writer, sheet_name='Quant Table')    
        tbls_mmolL[1].to_excel(writer, sheet_name='Quant Details', index=False)    
        writer.save()
        print('Saving file '+path+ftype+'Met_fits_Urine.xlsx')
        
        tbls_creaNorm=create_tbl(extrData, unit='mmol/mol Crea')
    
        # generate excel files
        writer = pd.ExcelWriter(path+ftype+'Met_fits_CreaNorm.xlsx', engine='xlsxwriter')
        tbls_creaNorm[0].to_excel(writer, sheet_name='Quant Table')    
        tbls_creaNorm[1].to_excel(writer, sheet_name='Quant Details', index=False)    
        writer.save()
        print('Saving file '+path+ftype+'Met_fits_Urine_CreaNorm.xlsx')


    if(ftype=='e'):
        rawData_pl=list_files(path, ft='plasma_quant_report_e_ver_1_0')
    if(ftype=='b'):
        rawData_pl=list_files(path, ft='plasma_quant_report')
    
    if(len(rawData_pl)>0):
        if(ftype=='e'):
            extrData=extract_uquant_e(rawData_pl)
        if(ftype=='b'):
            extrData=extract_uquant_b(rawData_pl)
    
        tbls_mmolL=create_tbl(extrData, unit='mmol/L')
        # generate excel files
        writer = pd.ExcelWriter(path+ftype+'Met_fits_Plasma.xlsx', engine='xlsxwriter')
        tbls_mmolL[0].to_excel(writer, sheet_name='Quant Table')    
        tbls_mmolL[1].to_excel(writer, sheet_name='Quant Details', index=False)    
        writer.save()
        print('Saving file '+path+ftype+'Met_fits_Plasma.xlsx')
    
        tbls_creaNorm=create_tbl(extrData, unit='mmol/mol Crea')
    
        # generate excel files
        writer = pd.ExcelWriter(path+ftype+'Met_fits_Plasma_CreaNorm.xlsx', engine='xlsxwriter')
        tbls_creaNorm[0].to_excel(writer, sheet_name='Quant Table')    
        tbls_creaNorm[1].to_excel(writer, sheet_name='Quant Details', index=False)    
        writer.save()
        print('Saving file '+path+ftype+'Met_fits_Plasma_CreaNorm.xlsx')
   
    
        
def collate_Bruker_lipo(path):
    
    if not path.endswith(os.path.sep):
        path += os.path.sep
    
    rawDat=list_files(path, ft='lipo_results')
       
    
    if(len(rawDat)>0):
        extrData=extract_lipo(rawDat)
        
        
        metIds=[]
        add=[]
        for me in extrData[0]:
            metIds.append(me[0])
            add.append([me[0], me[2].get('param'), me[2].get('unit'), me[2].get('lod'), me[2].get('loq')])
           
                
        mout=pd.DataFrame(add, columns=['Parameter', 'Info', 'Unit', 'LOD', 'LOQ'])
         
        
        # generate table output of parameter quantities
        files=[]
        for me in extrData:
            files.append(me[0][1])
            
        dout=pd.DataFrame(index=files, columns=metIds)
        
        for i_file in range(len(extrData)): # for every file
            mets=[]
            for i_met in range(len(extrData[i_file])): # for every metabolite
                mets.append(extrData[i_file][i_met][2].get('value')) 
            dout.iloc[i_file]=mets
        
        # generate table output of parameter quantities
        
    
        # generate excel files
        writer = pd.ExcelWriter(path+'Lipo_fits.xlsx', engine='xlsxwriter')
        dout.to_excel(writer, sheet_name='Quant Table')    
        mout.to_excel(writer, sheet_name='Quant Details', index=False)    
        writer.save()
        print('Saving file '+path+'Lipo_fits.xlsx')
        
        
        
def collate_Bruker_plasmaQC(path):
    
    if not path.endswith(os.path.sep):
        path += os.path.sep
    
    rawDat=list_files(path, ft='plasma_qc_report')
       
    
    if(len(rawDat)>0):
        extrData=extract_plasmaQC(rawDat)
        
        
        for i in range(len(extrData)):
            if( i == 0 ):
                sample_out=extrData[i][0]
                specQC_out=extrData[i][1]
                prepQC_out=extrData[i][2]
                matInteg_out=extrData[i][3]
                contam_out=extrData[i][4]
            else:
                sample_out = pd.concat([sample_out, extrData[i][0].iloc[:,1]], axis=1, join='inner')
                specQC_out = pd.concat([specQC_out, extrData[i][1].iloc[:,1]], axis=1, join='inner')
                prepQC_out = pd.concat([prepQC_out, extrData[i][2].iloc[:,1]], axis=1, join='inner')
                matInteg_out = pd.concat([matInteg_out, extrData[i][3].iloc[:,1]], axis=1, join='inner')
                contam_out = pd.concat([contam_out, extrData[i][4].iloc[:,1]], axis=1, join='inner')
    
        sample_out.columns = sample_out.columns.str.replace(path, '', regex=False).str.replace('/pdata/1/plasma_qc_report.xml', '', regex=False)
        sample_out.iloc[:,0]=sample_out.iloc[:,0].str.replace('\(.*', '', regex=True)
        
        specQC_out.columns = sample_out.columns
        prepQC_out.columns = sample_out.columns
        matInteg_out.columns = sample_out.columns
        contam_out.columns = sample_out.columns
        
        
        info=pd.DataFrame( [['# Experiment Folder: '+path], ['# Toobox version: '+'V1']])
    
        # generate excel files
        writer = pd.ExcelWriter(path+'PlasmaQC.xlsx', engine='xlsxwriter')
        info.to_excel(writer, sheet_name='Summary', index=False, startrow=0, startcol=0, header=False)
        info.to_excel(writer, sheet_name='NMR Spectral Quality', index=False, startrow=0, startcol=0, header=False)
        info.to_excel(writer, sheet_name='NMR Preparation Quality', index=False, startrow=0, startcol=0, header=False)
        info.to_excel(writer, sheet_name='Matrix Integrity Test', index=False, startrow=0, startcol=0, header=False)
        info.to_excel(writer, sheet_name='Matrix Contamination Test', index=False, startrow=0, startcol=0, header=False)
        
        sample_out.to_excel(writer, sheet_name='Summary', index=False, startrow=3, startcol=0)   
        specQC_out.to_excel(writer, sheet_name='NMR Spectral Quality', index=False, startrow=3, startcol=0)   
        prepQC_out.to_excel(writer, sheet_name='NMR Preparation Quality', index=False, startrow=3, startcol=0)   
        matInteg_out.to_excel(writer, sheet_name='Matrix Integrity Test', index=False, startrow=3, startcol=0)   
        contam_out.to_excel(writer, sheet_name='Matrix Contamination Test', index=False, startrow=3, startcol=0)   
        #mout.to_excel(writer, sheet_name='Quant Details', index=False)    
        writer.save()
        print('Saving file '+path+'PlasmaQC.xlsx')    
    
 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    