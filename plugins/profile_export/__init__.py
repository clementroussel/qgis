# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ProfileExport
                                 A QGIS plugin
 This plugin exports a longitudinal profile as a text file to be used with pyLong software.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-02-02
        copyright            : (C) 2022 by ONF-RTM
        email                : clement.roussel@onf.fr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ProfileExport class from file ProfileExport.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .profile_export import ProfileExport
    return ProfileExport(iface)
