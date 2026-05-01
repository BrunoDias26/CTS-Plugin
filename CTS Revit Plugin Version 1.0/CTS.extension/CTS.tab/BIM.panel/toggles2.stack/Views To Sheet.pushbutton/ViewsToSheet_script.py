# -*- coding: utf-8 -*-
__title__ = "Views To Sheet"
__doc__ = """Version 1.0

How to use:

- Run this tool. 
- Select the views you want to place.
- select the Title Block to use.

Author: Bruno Dias"""

__author__ = "Bruno Dias"     #Description of the button displayed in Revit UI
__min_revit_ver__= 2024
__max_revit_ver__ = 2025

import random
import string

import os
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import forms, revit, script

import clr
clr.AddReference('System')
from System.Collections.Generic import List


###### Variables ########

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
active_view = doc.ActiveView


###### Functions ########

def title_block_middle(tb):
    
    # definindo o ponto central dá área útil do TitleBlock
    if  isinstance(tb,FamilyInstance):
        tb_point = tb.Location.Point
        tb_width = tb.get_Parameter(BuiltInParameter.SHEET_WIDTH).AsDouble() - 0.44
        tb_height = tb.get_Parameter(BuiltInParameter.SHEET_HEIGHT).AsDouble() 

        tb_center = tb_point + XYZ(tb_width / 2, tb_height / 2, 0) 

        return tb_center
    
    else:
        return XYZ(0,0,0)


def sheetnumber(view, list):

    # definindo a padronização do SheetNumber
    try:
        view_name = view.Name
        view_lvl = view_name.split("-")[0].strip()

        view_discipline = view.get_Parameter(BuiltInParameter.VIEW_DISCIPLINE).AsValueString()[0]
        view_scope_box = view.get_Parameter(BuiltInParameter.VIEWER_VOLUME_OF_INTEREST_CROP).AsValueString()

        sheet_number = view_discipline + " - " + view_lvl + " - " + view_scope_box

    
    except:
        prefix = "A-"
        carac = string.digits
        comp = 3

        sufix = ''.join(random.choice(carac) for _ in range(comp))
        sheet_number = prefix + sufix


    # evitando duplicidade no SheetNumber
    final_sheet_number = sheet_number
    count = 1

    while final_sheet_number in list:
        final_sheet_number = sheet_number + "_" + str(count)
        count += 1

    list.append(final_sheet_number)

    return final_sheet_number


###### Main Execution ########

views = forms.select_views(title='Select Views (Unplaced Plans and Sections)', filterfunc=lambda v: (v.ViewType in [ViewType.FloorPlan, ViewType.CeilingPlan, ViewType.Section]
        and not v.IsTemplate and (v.get_Parameter(BuiltInParameter.VIEWER_SHEET_NAME) and v.get_Parameter(BuiltInParameter.VIEWER_SHEET_NAME).AsString() == "---")))

if views:
    titleblock = forms.select_titleblocks()
    if titleblock and titleblock != ElementId.InvalidElementId:

        get_all_sheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
        existing_sheets = [sheet.SheetNumber for sheet in get_all_sheets]


        ##### Transaction ########

        t = Transaction(doc, "Create Sheets")
        t.Start()

        for view in views:
            view_name = view.Name

            # criando a folha e setando SheetName e SheetNumber
            new_sheet = ViewSheet.Create(doc,titleblock)
            new_sheet.Name = view_name
            new_sheet.SheetNumber = sheetnumber(view,existing_sheets)
            
            tb_instance = list(FilteredElementCollector(doc,new_sheet.Id).OfCategory(BuiltInCategory.OST_TitleBlocks).ToElements())[0]

            tb_center = title_block_middle(tb_instance)
            Viewport.Create(doc, new_sheet.Id, view.Id,tb_center)

        t.Commit()


    else:
        forms.alert("User must select a Title Block.")
