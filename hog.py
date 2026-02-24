import arcpy

arcpy.env.overwriteOutput = True # if the output already exists replace it 

arcpy.management.XYTableToPoint(arcpy.GetParameterAsText(0), arcpy.GetParameterAsText(3), arcpy.GetParameterAsText(1), arcpy.GetParameterAsText(2)) # converts csv to coordinate points
arcpy.AddMessage("Your CSV file was successfully converted to points")
arcpy.management.Project(arcpy.GetParameterAsText(3), arcpy.GetParameterAsText(10), arcpy.GetParameterAsText(11)) # reprojects data to the desired coordinate system
arcpy.management.PointsToLine(arcpy.GetParameterAsText(10), arcpy.GetParameterAsText(4), arcpy.GetParameterAsText(6), arcpy.GetParameterAsText(5)) # takes the points and draws lines specified to by field
arcpy.management.Delete(arcpy.GetParameterAsText(3)) # fixed duplicate points
arcpy.AddMessage("Your points are connected through a poly line")

output = arcpy.GetParameterAsText(4) # sets a variable equal to the lines output
output2 = arcpy.GetParameterAsText(10)

aprx = arcpy.mp.ArcGISProject("CURRENT") # expects CURRENT keyword, connects to the 'current' project the tool is being run from
map = aprx.listMaps(arcpy.GetParameterAsText(7))[0] # assuming you are generating the feature classes in the first map, list at 0. Could add error handling for this in the future
map.addDataFromPath(output)
map.addDataFromPath(output2)
arcpy.AddMessage("Your data has been added to the project")

layer_name = output.split("\\")[-1] # error thrown from trying to list the layers with the full file path, the feature class name is simply preserved with this
arcpy.AddMessage("Getting output name behind split position")

lyr = map.listLayers(layer_name)[0] # finding layer at first position
arcpy.AddMessage(f"Map layer {lyr} setting show labels to")
lyr.showLabels = True # setting the layer as visible
arcpy.AddMessage("TRUE")
label = lyr.listLabelClasses()[0] # finding label classes at first position
label.expression = f"$feature.{arcpy.GetParameterAsText(8)}" # you have to include the $feature. section, otherwise it will have a fit, because that is how it reads it in it's arcade language
label.visible = True # setting the label as visible
arcpy.AddMessage("Hog names are now visible")

sym = lyr.symbology # setting the symbol equal to the symbology function with the layer
sym.updateRenderer("UniqueValueRenderer")
sym.renderer.fields = [arcpy.GetParameterAsText(9)]
lyr.symbology = sym
arcpy.AddMessage("Hog symbology set to unique value fields")
# https://pro.arcgis.com/en/pro-app/latest/arcpy/mapping/symbology-class.htm
aprx.save()

new_layout = aprx.createLayout(11, 8.5, 'INCH') # default page margins in landscape
extent = arcpy.Extent(0.5, 0.5, 10.5, 8) # setting extent to be offset by 0.5 for map frame
map_frame = new_layout.createMapFrame(extent, map) # passing in extent and processed map data
map_frame.camera.setExtent(map_frame.getLayerExtent(lyr, False)) # setting frames extent to the layer extent
arcpy.AddMessage("Layout and map frame extent created")

aprx.createTextElement(new_layout, arcpy.Point(4.5, 7.5), 'POINT', "Hog Paths", 30) # creates title at point location at font specified font size

north_arrow = aprx.listStyleItems('ArcGIS 2D', 'North_Arrow')[0] # grabs first north arrow in ArcGIS 2D folder of north arrows
new_layout.createMapSurroundElement(arcpy.Point(0.3, 0.4), 'North_Arrow', map_frame, north_arrow) # creates north arrow at point

scale_bar = aprx.listStyleItems('ArcGIS 2D', 'Scale_Bar')[0] # grabs first scale bar
new_layout.createMapSurroundElement(arcpy.Point(1.0, 0.5), 'Scale_Bar', map_frame, scale_bar)

# https://pro.arcgis.com/en/pro-app/3.4/arcpy/mapping/textelement-class.htm
# https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/point.htm
# https://pro.arcgis.com/en/pro-app/latest/arcpy/mapping/layout-class.htm

new_layout.exportToTIFF(arcpy.GetParameterAsText(12), 300, "24-BIT_TRUE_COLOR", "LZW", False) # (filename, resolution, color mode, compression type, background visibility)
arcpy.AddMessage("Your TIFF has been exported to your output location")