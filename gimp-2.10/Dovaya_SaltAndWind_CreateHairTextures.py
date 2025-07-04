#!/usr/bin/env python

# GIMP Python plug-in to automatically create hair textures using pre-made resources.
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
import sys


def dovaya_saltandwind_create_hair_textures(
    dir_original_hair_textures,
    file_hair_resource,
    img_height,
    img_width,
    exp_dds,
    exp_png,
    dir_logs,
):

    # set log routes
    sys.stderr = open(os.path.join(dir_logs, "gimpstderr.txt"), "w")
    sys.stdout = open(os.path.join(dir_logs, "gimpstdout.txt"), "w")

    # get all the hair textures in the specified folder
    hair_textures = []
    for texture_name in os.listdir(dir_original_hair_textures):
        texture = os.path.join(dir_original_hair_textures, texture_name)
        if os.path.isfile(texture) and os.path.splitext(texture)[1].lower() == ".dds":
            hair_textures.append(texture)

    # create hair textures
    for hair_texture in hair_textures:
        try:
            # get file name without extension
            filename = os.path.join(
                dir_original_hair_textures, os.path.splitext(hair_texture)[0]
            )

            # -------------------------------------------------------------------------------------
            # Step 1: Set up the picture
            # -------------------------------------------------------------------------------------
            # Create a new image and image window
            img = gimp.Image(img_height, img_width, 0)  # RGB image
            disp = gimp.Display(img)

            # load both the hair texture and the resource as layers
            layer_texture = pdb.gimp_file_load_layer(img, hair_texture)
            layer_resource = pdb.gimp_file_load_layer(img, file_hair_resource)

            # add them to the image
            img.add_layer(layer_texture, 1)
            img.add_layer(layer_resource, 1)

            # -------------------------------------------------------------------------------------
            # Step 2: Create the new texture
            # -------------------------------------------------------------------------------------
            # get the offsets and dimensions of the hair texture layer
            offset_x, offset_y = pdb.gimp_drawable_offsets(layer_texture)
            layer_texture_height = layer_texture.height
            layer_texture_width = layer_texture.width

            # resize the hair texture layer to the image size
            pdb.gimp_layer_resize_to_image_size(layer_texture)

            # transfer the alpha values from the hair texture layer to the hair resource layer
            mask_texture = layer_texture.create_mask(2)  # alpha channel mask
            layer_resource.add_mask(mask_texture)
            layer_resource.remove_mask(0)

            # save everything to a .xcf (standard gimp) file
            xcf = filename + ".xcf"
            pdb.gimp_xcf_save(0, img, img.active_layer, xcf, xcf)

            # -------------------------------------------------------------------------------------
            # Step 3: Export the new texture (if desired)
            # -------------------------------------------------------------------------------------
            if exp_dds or exp_png:
                # remove the original texture
                img.remove_layer(layer_texture)

                # resize the new texture and the image to the dimensions of the original texture
                pdb.gimp_layer_resize(
                    layer_resource,
                    layer_texture_height,
                    layer_texture_width,
                    offset_x,
                    offset_y,
                )
                pdb.gimp_image_resize(
                    img, layer_texture_height, layer_texture_width, offset_x, offset_y
                )

                # save the new texture as a .dds file
                if exp_dds:
                    pdb.file_dds_save(
                        img,
                        img.active_layer,
                        hair_texture,
                        hair_texture,
                        3,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                    )

                # save the new texture as a .png file
                if exp_png:
                    png = filename + ".png"
                    pdb.file_png_save(
                        img, img.active_layer, png, png, 0, 9, 0, 0, 0, 0, 1
                    )
            # -------------------------------------------------------------------------------------
            # Step 4: Clean up
            # -------------------------------------------------------------------------------------
            # show the new image window
            gimp.displays_flush()

            # clean the edit history s.t. no notification about unsaved changes pops up
            pdb.gimp_image_clean_all(img)

            # delete the image display
            pdb.gimp_display_delete(disp)

            # write success to the log
            print(hair_texture + ": successfully created")

        except:
            # write failure to the log
            print(hair_texture + ": skipped due to error")

    return


register(
    "dovaya_saltandwind_create_hair_textures",
    "Create hair textures for all hair textures in the specified folder using a specified source texture.",
    "Create hair textures for all hair textures in the specified folder using a specified source texture.",
    "dovaya",
    "dovaya",
    "2022",
    "Create hair textures",
    "",
    [
        (
            PF_DIRNAME,
            "dir_original_hair_textures",
            "Location of original textures:",
            os.path.expanduser("~"),
        ),
        (PF_FILE, "file_hair_resource", "Hair resource file:", os.path.expanduser("~")),
        (PF_INT, "img_height", "Height in px of hair resource:", 1024),
        (PF_INT, "img_width", "Width in px of hair resource:", 1024),
        (PF_BOOL, "exp_dds", "Export as .dds?", True),
        (PF_BOOL, "exp_png", "Export as .png?", True),
        (PF_DIRNAME, "dir_logs", "Desired location for logs:", os.path.expanduser("~")),
    ],
    [],
    dovaya_saltandwind_create_hair_textures,
    menu="<Image>/Tools/dovaya",
)

main()
