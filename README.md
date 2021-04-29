# qNMR
XL parser to import Bruker IVDr absolute quantification data (metabolites/plasmaptrotein classes/subclasses) into 2D matrix for statistical evaluation.

### Usage: 
```python
collate_Bruker_MetaboliteFits(path)
```


#### Input: 

  **path** (str) - path to directory of NMR experiments / xml quantification files ('urine_quant_report_e_ver_1_0', 'plasma_quant_report_e_ver_1_0')



#### Output: 

  Excel file in *path* containing two sheets:

 **Sheet 1:** Quatification data, 2D matrix with rows and columns representing samples and variables, resp.
 
 **Sheet 2:** Dictionary fro variable/analyte mapping & technical details (measurement unit, quantification limits)


