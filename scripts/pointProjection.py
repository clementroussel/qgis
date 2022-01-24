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
                       QgsWkbTypes)
from qgis import processing


class PointProjection(QgsProcessingAlgorithm):
    """
    Here is the class documentation.
    """

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PointProjection()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'point projection'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Point Projection')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('rtm-tools')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'rtm-tools'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        help = """
        <html><body>
        <h2>Description<\h2>
        <p>Orthogonal projection of a point layer onto a line or multiline vector layer.<\p>
        <h2>Inputs<\h2>
        <p>Axis layer : Should contain a single line or multiline feature onto which points will be projected.<\p>
        <p>Projected layer : Point layer to be projected.<\p>
        <p>Fields to keep : Fields from the projected layer to be kept in the output layer.<\p>
        <p>Digital Terrain Model (DTM) : If provided, point layer features' Z value will be extracted from it. Else, the algorithm will try to extract the Z value of the point layer features' geometry.<\p>
        <p><\p>
        <h2>Output<\h2>
        <p>The output layer is a copy of the projected layer provided whose attribute table contains a new field 'dist' which corresponds to the curvilinear distance of the projected points onto the axis.<\p>
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
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterField(
                'KEPT_FIELDS',
                self.tr('Fields to keep'),
                allowMultiple=True,
                defaultValue=[],
                optional=True,
                parentLayerParameterName='PROJECTED_LAYER'
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

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
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

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        #source = self.parameterAsSource(
        #    parameters,
        #    self.INPUT,
        #    context
        #)

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        #if source is None:
        #    raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        #(sink, dest_id) = self.parameterAsSink(
        #    parameters,
        #    self.OUTPUT,
        #    context,
        #    source.fields(),
        #    source.wkbType(),
        #    source.sourceCrs()
        #)

        # Send some information to the user
        #feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        # If sink was not created, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSinkError method to return a standard
        # helper text for when a sink cannot be evaluated
        #if sink is None:
        #    raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Compute the number of steps to display within the progress bar and
        # get features from source
        #total = 100.0 / source.featureCount() if source.featureCount() else 0
        #features = source.getFeatures()

        #for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
        #    if feedback.isCanceled():
        #        break

            # Add a feature in the sink
        #    sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
        #    feedback.setProgress(int(current * total))

        # To run another Processing algorithm as part of this algorithm, you can use
        # processing.run(...). Make sure you pass the current context and feedback
        # to processing.run to ensure that all temporary layer outputs are available
        # to the executed algorithm, and that the executed algorithm can send feedback
        # reports to the user (and correctly handle cancellation and progress reports!)
        
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
        
        projected_layer = self.parameterAsVectorLayer(parameters, 'PROJECTED_LAYER', context)        
        
        # keep only fields in KEPT_FIELDS from PROJECTED_LAYER's attribute table
        fields = []
        for field in projected_layer.fields():
            fields.append(field.name())
            
        removed_fields = [field for field in fields if field not in parameters['KEPT_FIELDS']]
        if len(removed_fields) > 0:
            projected_layer = processing.run("qgis:deletecolumn",
                                             {'INPUT':projected_layer,
                                              'COLUMN':removed_fields,
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
                                         
        # if DTM's been set, set PROJECTED_LAYER's Z value from it
        dtm = self.parameterAsRasterLayer(parameters, 'DTM', context)
        
        if not parameters['DTM'] == None:
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
                                         
        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {'OUTPUT':projected_layer}
