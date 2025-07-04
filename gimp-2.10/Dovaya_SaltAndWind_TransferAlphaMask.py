#!/usr/bin/env python

# GIMP Python plug-in to transfer the alpha mask of one layer to another.
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


def dovaya_saltandwind_transfer_alpha_mask(
    use_selection, img, layer_alpha, layer_resource
):

    # transfer the alpha values from the hair texture layer to the hair resource layer
    mask_alpha = layer_alpha.create_mask(2)  # alpha channel mask
    layer_resource.add_mask(mask_alpha)
    layer_resource.remove_mask(0)

    # clear the layer outside of the selection (if desired)
    if use_selection:
        pdb.gimp_selection_invert(img)
        pdb.gimp_drawable_edit_clear(layer_resource)
        pdb.gimp_selection_none(img)

    return


register(
    "dovaya_saltandwind_transfer_alpha_mask",
    "Transfer Alpha Mask.",
    "Transfer Alpha Mask.",
    "dovaya",
    "dovaya",
    "2022",
    "Transfer alpha mask",
    "",
    [
        (
            PF_BOOL,
            "use_selection",
            "Clear everything in resource layer outside of selection?",
            False,
        ),
        (PF_IMAGE, "img", "Image to use:", None),
        (PF_LAYER, "layer_alpha", "Layer with alpha to use:", None),
        (PF_LAYER, "layer_resource", "Layer with hair resource:", None),
    ],
    [],
    dovaya_saltandwind_transfer_alpha_mask,
    menu="<Image>/Tools/dovaya",
)

main()
