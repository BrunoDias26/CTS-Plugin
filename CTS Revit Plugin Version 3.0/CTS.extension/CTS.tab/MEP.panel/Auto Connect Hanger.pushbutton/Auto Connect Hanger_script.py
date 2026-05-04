# -*- coding: utf-8 -*-
__title__ = "Auto-Connect Hanger"
__author__ = "Bruno Dias"
__doc__ = """How to use:

- Select 1 Fabrication Hanger and 1 Fabrication Pipe (Straight).
- Run the script.
- The Hanger will be automatically connected and hosted to the Pipe.

Author: Bruno Dias
"""
from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

doc = revit.doc
selection = revit.get_selection()

if len(selection) != 2:
    forms.alert("Please select exactly 2 elements.", title="Selection Error")
    script.exit()

hanger = None
pipe = None

for el in selection:
    cat_id = el.Category.Id.IntegerValue
    if cat_id == int(BuiltInCategory.OST_FabricationHangers):
        hanger = el
    elif cat_id == int(BuiltInCategory.OST_FabricationPipework):
        pipe = el

if not hanger or not pipe:
    forms.alert("Selection must contain 1 Fabrication Hanger and 1 Fabrication Pipe.", title="Category Mismatch")
    script.exit()

# --- VERIFICAÇÃO IS A STRAIGHT ---
# Hangers só devem ser conectados em trechos retos
if not pipe.IsAStraight:
    forms.alert("The selected Fabrication Part is not a Straight pipe. Please select a straight segment.", title="Not a Straight")
    script.exit()

# --- CHECK DE CONEXÃO EXISTENTE ---
hosted_info = hanger.GetHostedInfo()
if hosted_info and hosted_info.HostId == pipe.Id:
    forms.alert("These elements are already connected.", title="Already Connected")
    script.exit()

# 3. Validação de Service
if hanger.ServiceId != pipe.ServiceId:
    forms.alert("Different Fabrication Services detected.", title="Service Mismatch")
    script.exit()

# 4. Ajuste de Size (Considerando Overall Size/Insulation)
pipe_size_raw = pipe.get_Parameter(BuiltInParameter.RBS_REFERENCE_OVERALLSIZE).AsString()
clean_size = pipe_size_raw.replace('"', '').strip() if pipe_size_raw else ""
success_size = False

# TRANSACTION 1: SIZE ADJUSTMENT
t_size = Transaction(doc, "Adjust Hanger Size")
t_size.Start()
try:
    size_param = hanger.get_Parameter(BuiltInParameter.FABRICATION_PRODUCT_ENTRY)
    if size_param and clean_size:
        # Tenta setar o valor limpo sem aspas
        size_param.Set(clean_size)
        success_size = True
    t_size.Commit()
except:
    t_size.RollBack()

if not success_size:
    forms.alert("The Hanger does not have a matching Size (DN) for: {}".format(pipe_size_raw), title="Size Mismatch")
    script.exit()

# TRANSACTION 2: POSITION & HOSTING
t_host = Transaction(doc, "Connect Hanger to Pipe")
t_host.Start()
try:
    # 1. Alinhamento Geométrico
    pipe_curve = pipe.Location.Curve
    bbox = hanger.get_BoundingBox(None)
    h_center = (bbox.Max + bbox.Min) / 2
    
    projection = pipe_curve.Project(h_center)
    target_xyz = projection.XYZPoint
    
    move_vec = XYZ(target_xyz.X - h_center.X, target_xyz.Y - h_center.Y, 0)
    if not move_vec.IsZeroLength():
        ElementTransformUtils.MoveElement(doc, hanger.Id, move_vec)
    
    # 2. Hospedagem (PlaceOnHost com 3 argumentos)
    hosted_info = hanger.GetHostedInfo()
    if hosted_info:
        # Pega o primeiro conector do pipe para referência de distância
        pipe_connectors = pipe.ConnectorManager.Connectors
        ref_conn = None
        for c in pipe_connectors:
            ref_conn = c
            break
            
        if ref_conn:
            # Calcula a distância do conector até o ponto projetado
            dist = ref_conn.Origin.DistanceTo(target_xyz)
            # Executa o método correto da API
            hosted_info.PlaceOnHost(pipe.Id, ref_conn, dist)
    
    t_host.Commit()
    print("SUCCESS: Connected to Pipe ID {}".format(pipe.Id))

except Exception as ex:
    t_host.RollBack()
    print("Connection Error: {}".format(ex))