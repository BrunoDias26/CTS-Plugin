# -*- coding: utf-8 -*-
__title__ = "Spool Transport"
__doc__ = """How to use:

Author: Bruno Dias
"""

__author__ = "Bruno Dias"
__min_revit_ver__ = 2023
__max_revit_ver__ = 2026

from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
active_view = doc.ActiveView


#  Definição dos Caminhões (L, W, H) - medidas em pés decimais
trucks = {
    "Standard Flatbed Box <br> (48' x 8.5' x 8.5')": [48.0, 8.5, 8.5],
    "Drop Deck Box <br> (48' x 8.5'x 10.5')": [48.0, 8.5, 10.5],
    "Double-Drop \"Lowboy\" Box <br> (48' x 8.5'x 11.5')": [48.0, 8.5, 11.5]
}


def get_assembly_dimensions(assembly):
    bbox = assembly.get_BoundingBox(active_view)
    
    if not bbox:
        return None
        
    # Cálculo das dimensões brutas (em Decimal Feet)
    dx = round(abs(bbox.Max.X - bbox.Min.X), 2)
    dy = round(abs(bbox.Max.Y - bbox.Min.Y),2)
    dz = round(abs(bbox.Max.Z - bbox.Min.Z),2)
    
    # Retornamos uma lista simples com as 3 medidas
    return [dx, dy, dz]


def sort_dimensions_descending(dims):
    #Recebe [dx, dy, dz] e retorna ordenado do MAIOR para o MENOR.

    if not dims:
        return None
        
    return sorted(dims, reverse=True)


def check_fit(spool_dims, truck_dims):

    s = sort_dimensions_descending(spool_dims)
    t = sort_dimensions_descending(truck_dims)

    # 2. Compara Maior com Maior, Médio com Médio e Menor com Menor
    if s[0] <= t[0] and s[1] <= t[1] and s[2] <= t[2]:
        return True
    
    else:
        return False


# Limitação da API. Apenas permite gerar Bbox de Assemblies a partir de uma vista.

all_project_assemblies = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Assemblies).WhereElementIsNotElementType().ToElements()
all_visible_assemblies = FilteredElementCollector(doc,active_view.Id).OfCategory(BuiltInCategory.OST_Assemblies).WhereElementIsNotElementType().ToElements()

fab_pipe_cat_id = ElementId(BuiltInCategory.OST_FabricationPipework)
all_project_assemblies_number = 0
all_visible_assemblies_number = 0

for assembly in all_project_assemblies:
    if assembly.NamingCategoryId == fab_pipe_cat_id:
        all_project_assemblies_number +=1

for assembly in all_visible_assemblies:
    if assembly.NamingCategoryId == fab_pipe_cat_id:
        all_visible_assemblies_number +=1

# Processo de validação para garantir que todas as Assemblies do projeto estarão sendo avaliadas no código.

if all_visible_assemblies_number == 0:
    forms.alert("None 'MEP Fabrication Pipework' assembly visible on Active View!", exitscript=True)
    script.exit()

if all_project_assemblies_number != all_visible_assemblies_number:
    msg = forms.alert("Warning: {} spools were found in the project, but only {} are visible in the current view.\n\nDo you want to proceed with the visible ones only?"\
                      .format(all_project_assemblies_number, all_visible_assemblies_number),ok=False, yes=True, no=True)
    
    if not msg:
        script.exit()

# 1. Definição da Ordem Exata (Coloque aqui a ordem que deseja ver na tabela)
truck_order = [
    "Standard Flatbed Box <br> (48' x 8.5' x 8.5')",
    "Drop Deck Box <br> (48' x 8.5'x 10.5')",
    "Double-Drop \"Lowboy\" Box <br> (48' x 8.5'x 11.5')"
]

## Main ##
final_table = []

t = Transaction(doc, "Update Spool Logistics Info")
t.Start()

for assembly in all_visible_assemblies:
    if assembly.NamingCategoryId == fab_pipe_cat_id:        
        assembly_dim = get_assembly_dimensions(assembly)
        if not assembly_dim:
            continue

        row = []
        row.append(assembly.Name)
        dims_str = "{0}' x {1}' x {2}'".format(assembly_dim[0], assembly_dim[1], assembly_dim[2])
        row.append(dims_str)

        truck_statuses = []
        
        # 2. USANDO A LISTA DE ORDEM DEFINIDA ACIMA
        for truck in truck_order:
            truck_dims = trucks[truck]

            if check_fit(assembly_dim, truck_dims):
                row.append("✅")
                truck_statuses.append("{}:✅".format(truck))
            else:
                row.append("❌")
                truck_statuses.append("{}:❌".format(truck))

        log_string = "Dims: {} | {}".format(dims_str, " | ".join(truck_statuses))
        
        param = assembly.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
        if param:
            param.Set(log_string)

        final_table.append(row)

t.Commit()

# --- criação do Output --- #
output = script.get_output()
output.add_style('h2 { text-align: center; }') 
output.add_style('th, td { text-align: center; border: 1px solid #ddd; padding: 8px; white-space: nowrap; }')
output.add_style('td:first-child { text-align: left; }')

# 3. CABEÇALHO TAMBÉM SEGUINDO A LISTA
head_columns = ["Spool Name", "Dimensions (L x W x H)"] + truck_order

output.print_table(table_data=final_table,
                   title="Spool Transport - Spool vs Truck Size",
                   columns=head_columns)



