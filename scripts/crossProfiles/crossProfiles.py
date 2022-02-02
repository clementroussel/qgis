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

- latest changes : 2022-02-01
- https://github.com/clementroussel/qgis/tree/main/scripts/crossProfiles
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterBand,
                       QgsProcessingParameterFeatureSink,
                       QgsVectorLayer)
from qgis import processing


class CrossProfiles(QgsProcessingAlgorithm):
    """
    Here is the (missing) class documentation.
    """

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CrossProfiles()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm.
        """
        return 'cross profiles'

    def displayName(self):
        """
        Returns the translated algorithm name.
        """
        return self.tr('Cross Profiles')

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
        <p>Generate regularly spaced cross-profiles along an axis.<\p>
        <h2>Inputs<\h2>
        <p>Axis layer : Should contain a single line or multiline feature.<\p>
        <p>Distance between two profiles : self-explained.<\p>
        <p>Profiles length : self-explained.<\p>
        <p>Extent layer : If provided, cross-profiles will be ajusted according to this layer.<\p>
        <p>Profiles subdivision length : Cross-profiles geometries are densified by adding additional vertices. This value indicates the maximum distance between two consecutive vertices.<\p>
        <p>Digital Terrain Model (DTM) : Cross-profiles vertices Z value will be extracted from it.<\p>
        <h2>Output<\h2>
        <p>A cross-profiles layer whose attribute table contains a field 'dist' and a field 'z min' that can be used to approximate a longitudinal profile.<\p>
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
            QgsProcessingParameterDistance(
                'DIST_BETWEEN_PROFILES',
                self.tr('Distance between two profiles'),
                defaultValue=100,
                parentParameterName='AXIS_LAYER'
            )
        )
        
        self.addParameter(
            QgsProcessingParameterDistance(
                'PROFILES_LENGTH',
                self.tr('Profiles length'),
                defaultValue=50,
                parentParameterName='AXIS_LAYER'
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'EXTENT',
                self.tr('Extent layer'),
                [QgsProcessing.TypeVectorPolygon],
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterDistance(
                'SUBDIVISIONS',
                self.tr('Profiles subdivision length'),
                defaultValue=0.25,
                parentParameterName='AXIS_LAYER'
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                'DTM',
                self.tr('Digital Terrain Model (DTM)'),
                optional=False
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

        # create the cross-profiles layer
        cross_profiles = processing.run("saga:crossprofiles",
                                        {'DEM':parameters['DTM'],
                                         'LINES':axis_layer,
                                         'PROFILES':'TEMPORARY_OUTPUT',
                                         'DIST_LINE':parameters['DIST_BETWEEN_PROFILES'],
                                         'DIST_PROFILE':parameters['PROFILES_LENGTH'],
                                         'NUM_PROFILE':3,
                                         'INTERPOLATION':3,
                                         'OUTPUT':0},
                                        is_child_algorithm=True,
                                        context=context,
                                        feedback=feedback)['PROFILES']

        # create a new field 'dist' in cross-profiles layer attribute table
        cross_profiles = processing.run("native:fieldcalculator",
                                        {'INPUT':cross_profiles,
                                         'FIELD_NAME':'dist',
                                         'FIELD_TYPE':0,
                                         'FIELD_LENGTH':10,
                                         'FIELD_PRECISION':3,
                                         'FORMULA':' (\"ID\" - 1) * '+str(parameters['DIST_BETWEEN_PROFILES']),
                                         'OUTPUT':'TEMPORARY_OUTPUT'},
                                        is_child_algorithm=True,
                                        context=context,
                                        feedback=feedback)['OUTPUT']
        
        # clip the cross-profiles with the extent layer
        extent_layer = self.parameterAsVectorLayer(parameters, 'EXTENT', context)

        if isinstance(extent_layer, QgsVectorLayer):
            cross_profiles = processing.run("native:clip",
                                            {'INPUT':cross_profiles,
                                             'OVERLAY':extent_layer,
                                             'OUTPUT':'TEMPORARY_OUTPUT'},
                                            is_child_algorithm=True,
                                            context=context,
                                            feedback=feedback)['OUTPUT']

        # add regularly spaced vertices to the cross-profiles
        cross_profiles = processing.run("native:densifygeometriesgivenaninterval",
                                        {'INPUT':cross_profiles,
                                         'INTERVAL':parameters['SUBDIVISIONS'],
                                         'OUTPUT':'TEMPORARY_OUTPUT'},
                                        is_child_algorithm=True,
                                        context=context,
                                        feedback=feedback)['OUTPUT']

        # set ;cross-profiles vertices' Z value from the DTM
        cross_profiles = processing.run("native:setzfromraster",
                                        {'INPUT':cross_profiles,
                                         'RASTER':parameters['DTM'],
                                         'BAND':parameters['DTM_BAND'],
                                         'NODATA':0,
                                         'SCALE':1,
                                         'OUTPUT':'TEMPORARY_OUTPUT'},
                                        is_child_algorithm=True,
                                        context=context,
                                        feedback=feedback)['OUTPUT'] 

        # create a new field 'z min'
        cross_profiles = processing.run("native:fieldcalculator",
                                        {'INPUT':cross_profiles,
                                         'FIELD_NAME':'z min',
                                         'FIELD_TYPE':0,
                                         'FIELD_LENGTH':10,
                                         'FIELD_PRECISION':3,
                                         'FORMULA':'z_min($geometry)',
                                         'OUTPUT':parameters['OUTPUT']},
                                        is_child_algorithm=True,
                                        context=context,
                                        feedback=feedback)['OUTPUT']                            
                                             
        # return the results of the algorithm
        return {'OUTPUT':cross_profiles}
