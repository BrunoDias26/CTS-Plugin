# -*- coding: utf-8 -*-
__title__ = "Top alignment"
__doc__ = """Version 1.0  

How to use:

- Select tags in the view
- Run the command to align all tags to the topmost one

Author: Bruno Dias"""

__author__ = "Bruno Dias"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2025


###### imports ########

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
rvt_year = int(app.VersionNumber)
Path_script = os.path.dirname(__file__)


###### Functions ########

def select_tags():
    
    allowed_cats = {
        BuiltInCategory.OST_FabricationPipeworkTags,
        BuiltInCategory.OST_WallTags,
        BuiltInCategory.OST_FabricationHangerTags,
        BuiltInCategory.OST_PipeAccessoryTags,
        BuiltInCategory.OST_PipeTags,
        BuiltInCategory.OST_DoorTags,
        BuiltInCategory.OST_FloorTags,
        BuiltInCategory.OST_WindowTags,
        BuiltInCategory.OST_AreaTags,
        BuiltInCategory.OST_FlexPipeTags,
        BuiltInCategory.OST_FurnitureTags,
        BuiltInCategory.OST_RoofTags,
        BuiltInCategory.OST_PipeFittingTags,
    }

    # Pega os elementos atualmente selecionados no Revit
    selected_ids = uidoc.Selection.GetElementIds()
    if not selected_ids:
        return None

    # Converte IDs em elementos e filtra direto pelas categorias
    filtered = []
    for eid in selected_ids:
        e = doc.GetElement(eid)
        if e and e.Category and e.Category.BuiltInCategory in allowed_cats:
            filtered.append(e)

    if not filtered:
        forms.alert("No element recognized in the selection.", title="Tag alignment")
        return None

    return filtered
    


def get_position(tag):
    return tag.TagHeadPosition


def get_topmost_tag(tags, view):
    """Retorna a tag mais alta na vista (maior projeção na direção UpDirection)."""
    topmost = None
    max_proj = float("-inf")
    up_dir = view.UpDirection

    for t in tags:
        try:
            pos = get_position(t)
            proj = pos.DotProduct(up_dir)
            if proj > max_proj:
                max_proj = proj
                topmost = t
        except:
            pass
    return topmost


def align_tags(reference_tag, tag_list, view, spacing=0.15):
    """Alinha tags horizontalmente mantendo o Y da referência e distribuindo por espaçamento fixo."""
    ref_pos = get_position(reference_tag)
    right, left = [], []

    right_dir = view.RightDirection
    up_dir = view.UpDirection

    # Divide em grupos à direita e à esquerda da referência
    for tag in tag_list:
        if tag.Id == reference_tag.Id:
            continue
        pos = get_position(tag)
        if pos.DotProduct(right_dir) > ref_pos.DotProduct(right_dir):
            right.append(tag)
        else:
            left.append(tag)

    # Ordena pela distância na direção direita/esquerda
    right.sort(key=lambda t: abs(get_position(t).DotProduct(right_dir) - ref_pos.DotProduct(right_dir)))
    left.sort(key=lambda t: abs(get_position(t).DotProduct(right_dir) - ref_pos.DotProduct(right_dir)))

    t = Transaction(doc, "Top alignment")
    t.Start()

    # Move tags à direita
    for i, tag in enumerate(right):
        pos = get_position(tag)
        offset = (i + 1) * spacing
        new_point = ref_pos + (right_dir.Normalize() * offset)
        tag.TagHeadPosition = XYZ(new_point.X, pos.Y, pos.Z)

    # Move tags à esquerda
    for i, tag in enumerate(left):
        pos = get_position(tag)
        offset = -(i + 1) * spacing
        new_point = ref_pos + (right_dir.Normalize() * offset)
        tag.TagHeadPosition = XYZ(new_point.X, pos.Y, pos.Z)

    t.Commit()


###### Main Execution ########
allowed_views = [ViewType.CeilingPlan, ViewType.FloorPlan, ViewType.Elevation, ViewType.Section]
if active_view.ViewType in allowed_views:

    tags = select_tags()
    if tags:
        ref_tag = get_topmost_tag(tags, active_view)
        if ref_tag:
            align_tags(ref_tag, tags, active_view, spacing=3.0)
