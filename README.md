# qNMR
Read NMR quantification data (metabolites/plasmaptrotein classes/subclasses) from research study into 2D matrix for statistical analysis

### Usage: 
```python
collate_Bruker_MetaboliteFits(path)
```


#### Input: 

  **path** (str) - path to directory of NMR experiments / xml quantification files ('urine_quant_report_e_ver_1_0', 'plasma_quant_report_e_ver_1_0')



#### Output: 

  Excel file with two sheets:

 **Sheet 1:** Quatification data, 2D matrix with rows and columns representing samples and variabels, resp.
 
 **Sheet 2:** Dictionary fro variable/analyte mapping & technical details (measurement unit, quantification limits)


