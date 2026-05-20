# -*- coding: utf-8 -*-
__title__ = "Left alignment"
__doc__ = """How to use:

- Select tags in the view
- Run the command to align all tags to the leftmost one

Author: Bruno Dias
"""

__author__ = "Bruno Dias"
__min_revit_ver__ = 2023
__max_revit_ver__ = 2026


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
        BuiltInCategory.OST_MechanicalEquipmentTags,
        BuiltInCategory.OST_StructuralFramingTags,

    }

    selected_ids = uidoc.Selection.GetElementIds()
    
    if not selected_ids:
        return None

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


def get_horizontal_axis(view):
    """
    Retorna qual eixo (X, Y ou Z) representa o eixo horizontal visível na vista,
    usando a View.RightDirection.
    """
    rd = view.RightDirection

    # maior componente define qual eixo esta direção usa mais
    comps = {
        'X': abs(rd.X),
        'Y': abs(rd.Y),
        'Z': abs(rd.Z)
    }

    return max(comps, key=comps.get)


def get_leftmost_tag(tags, view):
    axis = get_horizontal_axis(view)
    rd = view.RightDirection

    # Detecta se a direita da vista corresponde ao valor crescente ou decrescente no eixo
    direction = getattr(rd, axis)

    # Se for positivo → valores maiores estão à direita → menor = mais à esquerda
    # Se for negativo → valores menores estão à direita → maior = mais à esquerda
    looking_for_min = direction > 0

    best_tag = None
    best_value = None

    for t in tags:
        try:
            pos = t.TagHeadPosition
            val = getattr(pos, axis)

            if best_tag is None:
                best_tag = t
                best_value = val
                continue

            if looking_for_min:
                # eixo normal
                if val < best_value:
                    best_value = val
                    best_tag = t
            else:
                # eixo invertido
                if val > best_value:
                    best_value = val
                    best_tag = t

        except:
            pass

    return best_tag


def align_tags(reference_tag, tag_list, view, spacing=None):
    """
    Alinha tags mudando somente o eixo horizontal correto,
    movendo também o LeaderElbow para preservar o design da seta.
    """
    axis = get_horizontal_axis(view)

    ref_pos = get_position(reference_tag)
    ref_val = getattr(ref_pos, axis)

    t = Transaction(doc, "Left alignment with Elbow")
    t.Start()

    for tag in tag_list:
        if tag.Id == reference_tag.Id:
            continue

        current_pos = get_position(tag)

        # 1. Calcular o deslocamento (Delta) horizontal
        # O delta é um vetor que aponta o quanto a tag deve mover
        
        # O valor do eixo horizontal (axis) deve ser ajustado para ref_val
        current_val = getattr(current_pos, axis)
        
        # Cria o vetor de deslocamento (apenas no eixo horizontal)
        if axis == 'X':
            delta = XYZ(ref_val - current_val, 0, 0)
        elif axis == 'Y':
            delta = XYZ(0, ref_val - current_val, 0)
        else:  # axis == 'Z' (em cortes/elevações profundas)
            delta = XYZ(0, 0, ref_val - current_val)
            
        # 2. Mover a Cabeça da Tag
        tag.TagHeadPosition = current_pos.Add(delta)

        # 3. Ajustar o Cotovelo (Elbow) - Condicional LeaderEndCondition.Free
        if tag.HasLeader and tag.LeaderEndCondition == LeaderEndCondition.Free:
            refs = tag.GetTaggedReferences()
            for r in refs:
                # Verifica se a tag permite cotovelo para esta referência
                if tag.HasLeaderElbow(r):
                    old_elbow = tag.GetLeaderElbow(r)
                    tag.SetLeaderElbow(r, old_elbow.Add(delta))



    t.Commit()

###### Main ########

allowed_views = [
    ViewType.CeilingPlan,
    ViewType.FloorPlan,
    ViewType.Elevation,
    ViewType.Section
]

if active_view.ViewType in allowed_views:
    
    tags = select_tags()
    if tags:
        ref_tag = get_leftmost_tag(tags, active_view)
        if ref_tag:
            align_tags(ref_tag, tags, active_view, spacing=2.0)
