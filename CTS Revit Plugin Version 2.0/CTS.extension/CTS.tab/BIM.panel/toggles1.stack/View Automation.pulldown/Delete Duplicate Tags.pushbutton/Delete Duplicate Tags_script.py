# -*- coding: utf-8 -*-
__title__ = "Delete Duplicate Tags"
__doc__ = """ How to use:

- Run the application
- Select the Tag Type you want to check for duplicates
- Select elements 

Author: Bruno Dias"""

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

###### Safety Check ########
if active_view.ViewType in [ViewType.ThreeD, ViewType.Rendering]:
    forms.alert("This application can only be used in 2D views (plans, sections, elevations).")
    script.exit()

###### Functions ########

def get_type_name(el):
    # Retorna o nome do tipo de família (mesmo se .Name não estiver acessível)."""
    try:
        return el.Name  # funciona na maioria dos casos
    except:
        p = el.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        if p:
            return p
        else:
            return "<sem nomme>"


def check_category_and_type(elements,tag_types):
    # comparar e filtra a categoria e tipo de uma  lista de tags com os demais elementos na lista
    cleaned_list = []
    tag_type_ids = [tt.Id for tt in tag_types]
    tag_cat_ids = [tt.Category.Id for tt in tag_types]

    for ele in elements:
        try:
            if ele.Category.Id in tag_cat_ids:
                if ele.GetTypeId() in tag_type_ids:
                    cleaned_list.append(ele)
        except:
            continue

    return cleaned_list


###### Main ########


allowed_cats = [
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
]

# Coleta todos os tipos de tag do projeto
visible_tags = []
for cat in allowed_cats:
    types = FilteredElementCollector(doc,active_view.Id).OfCategory(cat).WhereElementIsNotElementType().ToElements()
    visible_tags.extend(types)

if not visible_tags:
    forms.alert("No tags found in the active view.", title="Delete Duplicate Tags")
    script.exit()


# Monta dicionário apenas com TIPOS usados na vista
tag_dict = {}

for tag in visible_tags:
    try:
        tag_type = doc.GetElement(tag.GetTypeId())
        fam_name = tag_type.Family.Name
        type_name = get_type_name(tag_type)
        display_name = "{} : {}".format(fam_name, type_name)
        tag_dict[display_name] = tag_type
    except:
        continue

# Exibe para o usuário
selected_display_name = forms.SelectFromList.show(sorted(tag_dict.keys()), title="Select Tag Type", multiselect=True)

# Retorna o elemento selecionado
if selected_display_name:
    selected_tags = [tag_dict[name] for name in selected_display_name]
    # print("Você selecionou:")

    # caixa de seleção para o usuário
    with forms.WarningBar(title="Select Elements"):
        elements_selection = revit.pick_elements()

        if elements_selection:
            filtered_ele_selecion = check_category_and_type(elements_selection,selected_tags)
            # print(filtered_ele_selecion)

            if filtered_ele_selecion:
                # dicionário agrupando elementos com o valor de TagTex(chave)
                tag_text_dic = {}

                for tag in filtered_ele_selecion:
                    try:
                        tag_text = tag.TagText.strip()

                        if not tag_text:
                            continue  # ignora tags vazias
                        
                        if tag_text in tag_text_dic:
                            tag_text_dic[tag_text].append(tag)

                        else:
                            tag_text_dic[tag_text] = [tag]

                    except:
                        continue
                    
                ##### Transaction ########

                t = Transaction(doc,"Delete Duplicate Tags")
                t.Start()

                deleted_count = 0

                for tag_text, tag_list in tag_text_dic.items():

                    if len(tag_list) > 1:
                        for tag_to_delete in tag_list[1:]:
                            try:
                                doc.Delete(tag_to_delete.Id)
                                deleted_count +=1
                            except:
                                continue
                
                forms.alert("Deleted {} duplicated Tags".format(deleted_count))
                t.Commit()
                    
            else:
                forms.alert("No Tags <{}> found in your selection".format(selected_display_name))





