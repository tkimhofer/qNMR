#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:32:08 2020

@author: TKimhofer
"""

import glob
import xml.etree.ElementTree as et
import pandas as pd



def list_files(path, type='urine_quant_report_e_ver_1_0'):
#     path - list all xml files in dir and subdirs
#     type - stringmatch with file name
    
    files=glob.glob(path+'/**/*'+type+'.xml', recursive=True)
    return(files)




def extract_uquant(files):
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
        print('Unit '+unit+'not found')
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
    
    for i_file in range(len(extr)):
        mets=[]
        for i_met in range(len(extr[i_file])):
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


def collate_Bruker_MetaboliteFits(path):
    
    rawData_ur=list_files(path, type='urine_quant_report_e_ver_1_0')
    if(len(rawData_ur)>0):
    
        extrData=extract_uquant(rawData_ur)
    
        tbls_mmolL=create_tbl(extrData, unit='mmol/L')
    
        # generate excel files
        writer = pd.ExcelWriter(path+'Met_fits.xlsx', engine='xlsxwriter')
        tbls_mmolL[0].to_excel(writer, sheet_name='Quant Table')    
        tbls_mmolL[1].to_excel(writer, sheet_name='Quant Details', index=False)    
        writer.save()
        print('Saving file '+path+'Met_fits_Urine.xlsx')
        
        tbls_creaNorm=create_tbl(extrData, unit='mmol/mol Crea')
    
        # generate excel files
        writer = pd.ExcelWriter(path+'Met_fits_CreaNorm.xlsx', engine='xlsxwriter')
        tbls_creaNorm[0].to_excel(writer, sheet_name='Quant Table')    
        tbls_creaNorm[1].to_excel(writer, sheet_name='Quant Details', index=False)    
        writer.save()
        print('Saving file '+path+'Met_fits_Urine_CreaNorm.xlsx')
    
    
    rawData_pl=list_files(path, type='plasma_quant_report_e_ver_1_0')
    
    if(len(rawData_pl)>0):
        extrData=extract_uquant(rawData_pl)
    
        tbls_mmolL=create_tbl(extrData, unit='mmol/L')
    
        # generate excel files
        writer = pd.ExcelWriter(path+'Met_fits.xlsx', engine='xlsxwriter')
        tbls_mmolL[0].to_excel(writer, sheet_name='Quant Table')    
        tbls_mmolL[1].to_excel(writer, sheet_name='Quant Details', index=False)    
        writer.save()
        print('Saving file '+path+'Met_fits_Plasma.xlsx')
    
        tbls_creaNorm=create_tbl(extrData, unit='mmol/mol Crea')
    
        # generate excel files
        writer = pd.ExcelWriter(path+'Met_fits_CreaNorm.xlsx', engine='xlsxwriter')
        tbls_creaNorm[0].to_excel(writer, sheet_name='Quant Table')    
        tbls_creaNorm[1].to_excel(writer, sheet_name='Quant Details', index=False)    
        writer.save()
        print('Saving file '+path+'Met_fits_Plasma_CreaNorm.xlsx')
    
    
    
    
    
    
    