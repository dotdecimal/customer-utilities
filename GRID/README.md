# GRID Therapy Support Files

This folder contains various files and scripts that may be helpful for users of .decimal GRID Blocks.

The main file of interest is Add-Grid-to-RTPlan.py
This file allows you to create a batch of DICOM RT Plan files with a beam that contains the blocks necessary to compute dose through a GRID Block using your Treatment Planning System (TPS).

Before explaining how to use this script, it's worth first describing why this script is necessary. DICOM files have the requirement that each file ever created is supposed to have a unique SOP Instance UID tag. Because of this requirement, most TPS software will restrict you from importing files with the same UIDs into different patients. This means that generating a single DICOM file with the GRID Block information is not sufficient, since it will only work for one patient in your TPS. So the purpose of this script is to first generate a DICOM Plan file with the GRID Block information, then to create a significant number of copies of this file, each having a unique SOP Instance UID as required by DICOM, and also having any references to other files (e.g. dose or structure set) altered, as many TPSs also check reference UIDs for unqiueness against existing patients before allowing import. 

With the "why" in mind, let's now cover the "how" of using this script.

Since many TPSs have specific import requirements for DICOM Plans, you should follow the steps below to use this script:
1. Use your TPS to create a treatment plan for any patient (or phantom) with a single beam containing a standard (non-MLC) photon block (any block shape will do). This ensures all machine information, tray positions, accessory codes, etc will be correct during the later import steps.
2. Export this plan to disc (it is recommended that you anonymize this plan when exporting to ensure your TPS does not try to link it back to the original patient, via the MRN or name, when importing the files generated later in this process).
3. Open the Add-Grid-to-RTPlan.py file and edit the "input_file" variable to match the name of your exported DICOM RT Plan file from above.
4. Edit the "output_file_base" variable to the location and file name you would like to use for the output files.
5. Edit the "file_count" variable to set the number of files you'd like to create.
6. Edit the "file_start_counter" variable (note: this only needs to be changed if you're exporting multiple batches of files on the same day).
7. Run the script using your python IDE or from command line. Your new files will be generated and saved to the location you set above.
  - This script reads your input RT Plan file and replaces the original photon block with the appropriate block data to describe a .decimal GRID Block.
  - Then it generates the specified number of files, each containing the same GRID Block data but having unique DICOM SOP Instance UID tags (including tags for any referenced dose or structure set files).
8. You can now import one of the above files into a patient within your TPS and you'll have a beam with a GRID Block present. Use care when importing and be sure to select a single file and not an entire directory or you may inadvertidely import your entire batch of plans into a single patient.
9. You should be able to alter the beam direction and position, as weill as collimate the beam using the jaws or MLC leaves if desired within your TPS.
10. Once the beam is adjusted as desired, you can compute dose as usual in your TPS and the GRID Block hole pattern should be applied. Note: Transmission values and other data may be required to be set in your TPS in order to obtain accurate dose calculations, which can be both machine and energy dependent; please consult published literature or measured data to ensure accurate dose calculations are achieved.
  
Python Information:
 - This script was developed and tested using python 3.4.3, but likely works on newer versions.
 - The following python packages are required:
   - pydicom
   
