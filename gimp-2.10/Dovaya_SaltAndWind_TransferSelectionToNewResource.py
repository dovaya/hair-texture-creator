#!/usr/bin/env python

# GIMP Python plug-in to transfer the alpha mask of the selection of a layer to a newly loaded layer.
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
import os
import os.path


def dovaya_saltandwind_transfer_alpha_mask_of_selection_to_new_resource(
    file_hair_resource, img, layer_alpha
):

    # load resource and add as layer
    layer_resource = pdb.gimp_file_load_layer(img, file_hair_resource)
    img.add_layer(layer_resource, 1)

    # transfer the alpha values from the hair texture layer to the hair resource layer
    mask_original = layer_alpha.create_mask(2)  # alpha channel mask
    layer_resource.add_mask(mask_original)
    layer_resource.remove_mask(0)

    # clear the selection in the original texture and clear the inverted selection in the new texture
    pdb.gimp_drawable_edit_clear(layer_alpha)
    pdb.gimp_selection_invert(img)
    pdb.gimp_drawable_edit_clear(layer_resource)
    pdb.gimp_selection_none(img)

    # save
    img_path = pdb.gimp_image_get_filename(img)
    pdb.gimp_xcf_save(0, img, img.active_layer, img_path, img_path)


register(
    "dovaya_saltandwind_transfer_alpha_mask_of_selection_to_new_resource",
    "Transfer alpha mask of selection to new resource",
    "Transfer alpha mask of selection to new resource.",
    "dovaya",
    "dovaya",
    "2022",
    "Transfer alpha mask of selection to new resource",
    "",
    [
        (PF_FILE, "file_hair_resource", "Hair resource file:", os.path.expanduser("~")),
        (PF_IMAGE, "img", "Image to use:", None),
        (PF_LAYER, "layer_alpha", "Layer with alpha to use:", None),
    ],
    [],
    dovaya_saltandwind_transfer_alpha_mask_of_selection_to_new_resource,
    menu="<Image>/Tools/dovaya",
)

main()
