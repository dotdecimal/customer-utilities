# Copyright (c) 2022 .decimal, LLC. All rights reserved.
# Author:   Kevin Erhart
# Desc:     Takes in a DICOM plan with a photon block and strips out the existing block data and replaces with a grid block
# 
# This file is provided as-is and users assume all responsibility for verifying the appropriateness of its content and output
#   before using for treatment of any living creature
#

import sys
import pydicom as dicom
import math
import copy
from datetime import datetime


input_file = 'RT_Plan.dcm'
output_file_base = 'output/RT_Plan_Grid_'
file_count = 100 # Number of files to write (each will have a unique UID and ref UIDs)
file_start_counter = 200 # must be > 100 and < (1000 - file_count)


# ----------------------------------------------------------------------
# -- Standard .decimal GRID Block parameters are set below -------------
# -- Only edit the section below if you have a custom GRID block -------
# ----------------------------------------------------------------------

hole_spacing = 21.1 # Center-to-Center spacing (mm) at isocenter
hole_diameter = 14.3 # Diameter of holes (mm) at isocenter
hole_count_x = 12
hole_count_y = 13
SAD = 1000.0 # Machine SAD (mm)

# ----------------------------------------------------------------------
# -- Users should not need to edit below this line ---------------------
# ----------------------------------------------------------------------

def replace_right(source, target, replacement):
    k = source.rfind(target)
    return source[:k] + replacement

ds = dicom.read_file(input_file)
modality = ds.Modality
if modality == 'RTPLAN':
    
    # Set some .decimal Info
    ds.Manufacturer = ".decimal"
    ds.ManufacturerModelName = "Grid Writer"
    ds.SoftwareVersions = "0.0.1"

    # Remove all but the first beam
    beams = ds.BeamSequence
    if len(beams) < 1:
            print("Plan must contain at least one beam")
            exit()
    
    beam = beams[0]

    if len(beam.BlockSequence) < 1:
        print("Plan must contain at least one aperture on beam #" + str(beam.BeamNumber))
        exit()

    block = beam.BlockSequence[0]
    try:
    	del block.BlockTransmission
    except:
        # Do nothing
        print("No BlockTransmission [OK]")
    
    block.BlockThickness = 76.2
    block.BlockMountingPosition = "SOURCE_SIDE"
    block.MaterialID = "Brass"
    
    circleCount = 60
    invAngle = 2.0 * math.pi / circleCount

    SADsq = SAD * SAD
    ydelta = 0.5 * math.sqrt(3.0) * hole_spacing
    startX = -0.5 * (hole_count_x - 1) * hole_spacing
    startY = -0.5 * (hole_count_y - 1) * ydelta

    # Loop to create a "block" for each aperture hole
    bn = 1;
    new_blocks = []
    for j in range(0, hole_count_y):
        
        offset = 0.0
        if (j % 2) != 1:
            offset = 0.5

        cy = startY + j * ydelta
        rB = 0.5 * hole_diameter * math.sqrt(cy * cy + SADsq) / SAD

        for i in range(0, hole_count_x - int(2 * offset)):
            cx = startX + (i + offset) * hole_spacing
            rA = 0.5 * hole_diameter * math.sqrt(cx * cx + SADsq) / SAD

            # Create "cirlce" as a point list
            poly = []
            for k in range(0, circleCount):
                x = cx + rA * math.cos(k * invAngle)
                y = cy + rB * math.sin(k * invAngle)
                poly.append(round(x, 4)) 
                poly.append(round(y, 4))

            # Add to dicom block
            block.BlockNumber = bn
            block.BlockNumberOfPoints = circleCount
            block.BlockData = poly
            new_blocks.append(copy.deepcopy(block))
            bn += 1

    beam.BlockSequence = new_blocks
    beam.NumberOfBlocks = len(new_blocks)

    # Edit the SOP UIDs to be unique
    now = datetime.now()
    uid = now.strftime(".45%y%m%d")
    uid1 = uid + "1"
    uid2 = uid + "2"
    uid3 = uid + "3"
    uids = []
    N = 3
    try:
        for i in range(0, len(ds.DoseReferenceSequence)):
            N += 1
            uids.append(uid + str(N))
    except:
        # Do nothing
        print("No Dose UIDs to replace [OK]")
    
    try:
        for i in range(0, len(ds.ReferencedStructureSetSequence)):
            N += 1
            uids.append(uid + str(N))
    except:
        # Do nothing
        print("No SS UIDs to replace [OK]")

    # Write desired number of files
    for i in range(file_start_counter, file_start_counter + file_count):
        i_str = str(i).rjust(3, '0')
        ds.SOPInstanceUID = replace_right(ds.SOPInstanceUID, ".", uid1 + i_str)
        ds.StudyInstanceUID = replace_right(ds.StudyInstanceUID, ".", uid2 + i_str)
        ds.SeriesInstanceUID = replace_right(ds.SeriesInstanceUID, ".", uid3 + i_str)
        N = 0
        # Look for Dose References
        try:
            for i in range(0, len(ds.DoseReferenceSequence)):
                ds.DoseReferenceSequence[i].DoseReferenceUID = replace_right(ds.DoseReferenceSequence[i].DoseReferenceUID, ".", uids[N] + i_str)
                N += 1
        except:
            # Do nothing
            N = N

        # Look for Structure Set References
        try:
            for i in range(0, len(ds.ReferencedStructureSetSequence)):
                ds.ReferencedStructureSetSequence[i].ReferencedSOPInstanceUID = replace_right(ds.ReferencedStructureSetSequence[i].ReferencedSOPInstanceUID, ".", uids[N] + i_str)
                N += 1
        except:
            # Do nothing
            N = N

        out_name = output_file_base + i_str + ".dcm"
        print("Saving Plan: " + out_name)
        ds.save_as(out_name)
