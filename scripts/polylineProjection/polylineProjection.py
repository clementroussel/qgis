# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************

- latest changes : 2022-02-02
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterField,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterBand,
                       QgsProcessingParameterFeatureSink,
                       QgsWkbTypes,
                       QgsVectorLayer)
from qgis import processing


class PolylineProjection(QgsProcessingAlgorithm):
    """
    Here is the class documentation.
    """

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PolylineProjection()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm.
        """
        return 'polyline projection'

    def displayName(self):
        """
        Returns the translated algorithm name.
        """
        return self.tr('Polyline Projection')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to.
        """
        return self.tr('onf-rtm-tools')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to.
        """
        return 'onf-rtm-tools'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm.
        """
        help = """
        <html><body>
        <h2>Description<\h2>
        <p>Orthogonal projection of a line or multiline layer onto another line or multiline vector layer.<\p>
        <h2>Inputs<\h2>
        <p>Axis layer : Should contain a single line or multiline feature onto which points will be projected.<\p>
        <p>Projected layer : Should contain a single line or multiline layer to be projected.<\p>
        <p>Digital Terrain Model (DTM) : If provided, projected layer vertices' Z value will be extracted from it. Else, the algorithm will try to extract the Z value of the projected layer vertices' geometry.<\p>
        <p>Interpolate : If checked, the projected layer will be interpolated on the DTM and, consequently, new vertices will be created.<\p>
        <h2>Output<\h2>
        <p>The output layer is a point layer whose attribute table contains a field 'dist' which corresponds to the curvilinear distance of the projected vertices onto the axis.<\p>
        <\body><\html>
        """
        return self.tr(help)

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'AXIS_LAYER',
                self.tr('Axis layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterBoolean(
                'INVERT_AXIS',
                self.tr('Invert axis'),
                False
            )
        )
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'PROJECTED_LAYER',
                self.tr('Projected layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                'DTM',
                self.tr('Digital Terrain Model (DTM)'),
                optional=True
            )
        )
        
        self.addParameter(
            QgsProcessingParameterBand(
                'DTM_BAND',
                self.tr('DTM Raster Band'),
                defaultValue=1,
                parentLayerParameterName='DTM'
            )
        )
        
        self.addParameter(
            QgsProcessingParameterBoolean(
                'INTERPOLATE',
                self.tr('Interpolate'),
                False
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                'OUTPUT',
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """        
        axis_layer = self.parameterAsVectorLayer(parameters, 'AXIS_LAYER', context)
        
        # delete all fields from AXIS_LAYER's attribute table
        fields = []
        for field in axis_layer.fields():
            fields.append(field.name())
            
        axis_layer = processing.run("qgis:deletecolumn",
                                    {'INPUT':axis_layer,
                                     'COLUMN':fields,
                                     'OUTPUT':'TEMPORARY_OUTPUT'},
                                    is_child_algorithm=True,
                                    context=context,
                                    feedback=feedback)['OUTPUT']
                                     
        
        invert_axis = self.parameterAsBool(parameters, 'INVERT_AXIS', context)
        
        # if asked, invert the direction of the axis' line or polyline
        if invert_axis:
            axis_layer = processing.run("native:reverselinedirection",
                                        {'INPUT':axis_layer,
                                         'OUTPUT':'TEMPORARY_OUTPUT'},
                                        is_child_algorithm=True,
                                        context=context,
                                        feedback=feedback)['OUTPUT']
        
        projected_line_layer = self.parameterAsVectorLayer(parameters, 'PROJECTED_LAYER', context)        
        
        # remove all fields from PROJECTED_LAYER's attribute table
        fields = []
        for field in projected_line_layer.fields():
            fields.append(field.name())
            
        if len(fields) > 0:
            projected_line_layer = processing.run("qgis:deletecolumn",
                                                  {'INPUT':projected_line_layer,
                                                   'COLUMN':fields,
                                                   'OUTPUT':'TEMPORARY_OUTPUT'},
                                                  is_child_algorithm=True,
                                                  context=context,
                                                  feedback=feedback)['OUTPUT']
                                                  
        dtm = self.parameterAsRasterLayer(parameters, 'DTM', context)
        
        # if no DTM
        if parameters['DTM'] == None:
            # extract the vertices
            projected_layer = processing.run("native:extractvertices",
                                             {'INPUT':projected_line_layer,
                                              'OUTPUT':'TEMPORARY_OUTPUT'},
                                             is_child_algorithm=True,
                                             context=context,
                                             feedback=feedback)['OUTPUT']
                                     
            # convert the result (which is a str id) as a vector layer
            projected_layer = context.takeResultLayer(projected_layer)
                                         
            # remove all fields created by the previous algorithm
            fields = []
            for field in projected_layer.fields():
                fields.append(field.name())
            
            if len(fields) > 0:
                projected_layer = processing.run("qgis:deletecolumn",
                                                 {'INPUT':projected_layer,
                                                  'COLUMN':fields,
                                                  'OUTPUT':'TEMPORARY_OUTPUT'},
                                                 is_child_algorithm=True,
                                                 context=context,
                                                 feedback=feedback)['OUTPUT']
                                             
            # add a new field "dist" to PROJECTED_LAYER's attribute table
            projected_layer = processing.run("native:addfieldtoattributestable",
                                             {'INPUT':projected_layer,
                                              'FIELD_NAME':'dist',
                                              'FIELD_TYPE':1,
                                              'FIELD_LENGTH':10,
                                              'FIELD_PRECISION':3,
                                              'OUTPUT':'TEMPORARY_OUTPUT'},
                                             is_child_algorithm=True,
                                             context=context,
                                             feedback=feedback)['OUTPUT']
                                                  
            # add a new field "Z" to PROJECTED_LAYER's attribute table
            projected_layer = processing.run("native:fieldcalculator",
                                         {'INPUT':projected_layer,
                                          'FIELD_NAME':'Z',
                                          'FIELD_TYPE':0,
                                          'FIELD_LENGTH':10,
                                          'FIELD_PRECISION':3,
                                          'FORMULA':'z($geometry)',
                                          'OUTPUT':'TEMPORARY_OUTPUT'},
                                         is_child_algorithm=True,
                                         context=context,
                                         feedback=feedback)['OUTPUT']
                                    
            # execute v.distance algorithm
            projected_layer = processing.run("grass7:v.distance",
                                             {'from':projected_layer,
                                              'from_type':[0],
                                              'to':axis_layer,
                                              'to_type':[1],
                                              'dmax':-1,
                                              'dmin':-1,
                                              'upload':[4],
                                              'column':['dist'],
                                              'to_column':'',
                                              'from_output':parameters['OUTPUT'],
                                              'output':'TEMPORARY_OUTPUT',
                                              'GRASS_REGION_PARAMETER':None,
                                              'GRASS_SNAP_TOLERANCE_PARAMETER':-1,
                                              'GRASS_MIN_AREA_PARAMETER':0.0001,
                                              'GRASS_OUTPUT_TYPE_PARAMETER':1,
                                              'GRASS_VECTOR_DSCO':'',
                                              'GRASS_VECTOR_LCO':'',
                                              'GRASS_VECTOR_EXPORT_NOCAT':False},
                                             is_child_algorithm=True,
                                             context=context,
                                             feedback=feedback)['from_output']
                                                  
        else:
            interpolate = self.parameterAsBool(parameters, 'INTERPOLATE', context)
            
            if not interpolate:
                feedback.pushInfo("No interpolation")
                # extract the vertices
                projected_layer = processing.run("native:extractvertices",
                                                 {'INPUT':projected_line_layer,
                                                  'OUTPUT':'TEMPORARY_OUTPUT'},
                                                 is_child_algorithm=True,
                                                 context=context,
                                                 feedback=feedback)['OUTPUT']
                                                 
            else:
                # add an id field
                projected_layer = processing.run("native:addautoincrementalfield",
                                                 {'INPUT':projected_line_layer,
                                                  'FIELD_NAME':'ID',
                                                  'START':0,
                                                  'GROUP_FIELDS':[],
                                                  'SORT_EXPRESSION':'',
                                                  'SORT_ASCENDING':True,
                                                  'SORT_NULLS_FIRST':False,
                                                  'OUTPUT':'TEMPORARY_OUTPUT'},
                                                 is_child_algorithm=True,
                                                 context=context,
                                                 feedback=feedback)['OUTPUT']

                # execute "Profiles from Lines" algorithm
                projected_layer = processing.run("saga:profilesfromlines",
                                                 {'DEM':parameters['DTM'],
                                                  'VALUES':None,
                                                  'LINES':projected_layer,
                                                  'NAME':'ID',
                                                  'PROFILE':'TEMPORARY_OUTPUT',
                                                  'PROFILES':'TEMPORARY_OUTPUT',
                                                  'SPLIT':False},
                                                 is_child_algorithm=True,
                                                 context=context,
                                                 feedback=feedback)['PROFILE']
                   
                # delete duplicates by attribute
                projected_layer = processing.run("native:removeduplicatesbyattribute", 
                                                 {'INPUT':projected_layer,
                                                  'FIELDS':['X','Y','Z'],
                                                  'OUTPUT':'TEMPORARY_OUTPUT'},
                                                 is_child_algorithm=True,
                                                 context=context,
                                                 feedback=feedback)['OUTPUT']
                
            # convert the result (which is a str id) as a vector layer
            projected_layer = context.takeResultLayer(projected_layer)
                                         
            # remove all fields created by the previous algorithm
            fields = []
            for field in projected_layer.fields():
                fields.append(field.name())
                
            if len(fields) > 0:
                projected_layer = processing.run("qgis:deletecolumn",
                                                 {'INPUT':projected_layer,
                                                  'COLUMN':fields,
                                                  'OUTPUT':'TEMPORARY_OUTPUT'},
                                                 is_child_algorithm=True,
                                                 context=context,
                                                 feedback=feedback)['OUTPUT']
                                                
            # add a new field "dist" to PROJECTED_LAYER's attribute table
            projected_layer = processing.run("native:addfieldtoattributestable",
                                                {'INPUT':projected_layer,
                                                'FIELD_NAME':'dist',
                                                'FIELD_TYPE':1,
                                                'FIELD_LENGTH':10,
                                                'FIELD_PRECISION':3,
                                                'OUTPUT':'TEMPORARY_OUTPUT'},
                                                is_child_algorithm=True,
                                                context=context,
                                                feedback=feedback)['OUTPUT']

            # DTM has been set, set PROJECTED_LAYER's Z value from it
            projected_layer = processing.run("native:setzfromraster",
                                             {'INPUT':projected_layer,
                                              'RASTER':dtm,
                                              'BAND':parameters['DTM_BAND'],
                                              'NODATA':0,
                                              'SCALE':1,
                                              'OUTPUT':'TEMPORARY_OUTPUT'},
                                             is_child_algorithm=True,
                                             context=context,
                                             feedback=feedback)['OUTPUT']

            # add a new field "Z" to PROJECTED_LAYER's attribute table                                  
            projected_layer = processing.run("native:fieldcalculator",
                                             {'INPUT':projected_layer,
                                              'FIELD_NAME':'Z',
                                              'FIELD_TYPE':0,
                                              'FIELD_LENGTH':10,
                                              'FIELD_PRECISION':3,
                                              'FORMULA':'z($geometry)',
                                              'OUTPUT':'TEMPORARY_OUTPUT'},
                                             is_child_algorithm=True,
                                             context=context,
                                             feedback=feedback)['OUTPUT']

            # execute v.distance algorithm                                 
            projected_layer = processing.run("grass7:v.distance",
                                             {'from':projected_layer,
                                              'from_type':[0],
                                              'to':axis_layer,
                                              'to_type':[1],
                                              'dmax':-1,
                                              'dmin':-1,
                                              'upload':[4],
                                              'column':['dist'],
                                              'to_column':'',
                                              'from_output':parameters['OUTPUT'],
                                              'output':'TEMPORARY_OUTPUT',
                                              'GRASS_REGION_PARAMETER':None,
                                              'GRASS_SNAP_TOLERANCE_PARAMETER':-1,
                                              'GRASS_MIN_AREA_PARAMETER':0.0001,
                                              'GRASS_OUTPUT_TYPE_PARAMETER':1,
                                              'GRASS_VECTOR_DSCO':'',
                                              'GRASS_VECTOR_LCO':'',
                                              'GRASS_VECTOR_EXPORT_NOCAT':False},
                                             is_child_algorithm=True,
                                             context=context,
                                             feedback=feedback)['from_output']
        
        # return the results of the algorithm
        return {'OUTPUT':projected_layer}
