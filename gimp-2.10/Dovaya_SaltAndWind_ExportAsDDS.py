#!/usr/bin/env python

# GIMP Python plug-in to quickly export the image as a .dds file.
# Copyright 2022 dovaya <dovaya.creations@gmail.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gimpfu import *
import os.path
import os


def dovaya_saltandwind_export_as_dds(img):

    # get file path
    img_path = pdb.gimp_image_get_filename(img)
    dds = os.path.splitext(img_path)[0] + ".dds"

    # merge all layers
    pdb.gimp_image_merge_visible_layers(img, 1)

    # export
    pdb.file_dds_save(
        img, img.active_layer, dds, dds, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    )


register(
    "dovaya_saltandwind_export_as_dds",
    "Export as DDS.",
    "Export as DDS.",
    "dovaya",
    "dovaya",
    "2022",
    "Export as DDS",
    "",
    [
        (PF_IMAGE, "img", "Image to export:", None),
    ],
    [],
    dovaya_saltandwind_export_as_dds,
    menu="<Image>/Tools/dovaya",
)

main()
