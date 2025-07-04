#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   dovaya-hair-texture-creator.py
#   Plugin that allows for the automatic creation of DDS hair texture files using pre-made resources.
#   Copyright (C) 2025 dovaya
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
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi

gi.require_version("Gegl", "0.4")
from gi.repository import Gegl
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import sys
import os

from utils import utils


def N_(message):
    return message


def _(message):
    return GLib.dgettext(None, message)


class DovayaHairTextureCreator(Gimp.PlugIn):
    def do_query_procedures(self):
        return [
            "dovaya-hair-texture-creator-process-textures",
            "dovaya-hair-texture-creator-transfer-alpha",
        ]

    def do_set_i18n(self, name):
        return False

    def do_create_procedure(self, name):
        if name == "dovaya-hair-texture-creator-process-textures":
            procedure = Gimp.ImageProcedure.new(
                self, name, Gimp.PDBProcType.PLUGIN, self.run_process_textures, None
            )

            procedure.set_image_types("*")
            procedure.set_menu_label("Process Textures")
            procedure.set_documentation(
                "Create DDS hair textures from existing assets.",
                "Create DDS hair textures from existing assets.",
                name,
            )

            procedure.add_file_argument(
                "textures",
                _("Original textures"),
                _("The original DDS textures."),
                Gimp.FileChooserAction.SELECT_FOLDER,
                False,
                None,
                GObject.ParamFlags.READWRITE,
            )

        else:  # name == "dovaya-hair-texture-creator-transfer-alpha":
            procedure = Gimp.ImageProcedure.new(
                self, name, Gimp.PDBProcType.PLUGIN, self.run_transfer_alpha, None
            )

            procedure.set_image_types("*")
            procedure.set_menu_label("Transfer Alpha")
            procedure.set_documentation(
                "Create hair textures from existing assets.",
                "Create DDS hair textures from existing assets.",
                name,
            )

            procedure.add_boolean_argument(
                "use_selection",
                _("Use Selection"),
                _("Determines whether to use selection."),
                False,
                GObject.ParamFlags.READWRITE,
            )

            procedure.add_layer_argument(
                "layer_alpha",
                _("Alpha Layer"),
                _("The alpha layer."),
                False,
                GObject.ParamFlags.READWRITE,
            )

            procedure.add_layer_argument(
                "layer_resource",
                _("Resource Layer"),
                _("The resource layer."),
                False,
                GObject.ParamFlags.READWRITE,
            )

        procedure.add_menu_path("<Image>/Tools/dovaya/")
        procedure.set_attribution("dovaya", "dovaya", "2025")

        return procedure

    def run_process_textures(
        self, procedure, run_mode, image, drawables, config, run_data
    ):

        GimpUi.init(procedure.get_name())

        dialog = GimpUi.ProcedureDialog.new(procedure, config)

        dialog.fill()

        # if dialog is cancelled
        if not dialog.run():
            dialog.destroy()
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())

        textures_folder = config.get_property("textures")

        # return if no textures_folder is given
        if textures_folder is None:
            error = "No folder given"
            return procedure.new_return_values(
                Gimp.PDBStatusType.CALLING_ERROR, GLib.Error(error)
            )

        textures_folder_path = textures_folder.peek_path()
        log_path = os.path.join(textures_folder_path, "dovaya-hair-texture-creator.log")

        # cancellable = Gio.Cancellable.new()

        with open(log_path, "a") as log:
            try:
                # get dimensions of image
                image_width = image.get_width()
                image_height = image.get_height()

                # get resource layer
                resource_drawable = drawables[0]
                resource_drawable_name = resource_drawable.get_name()

                # remove layer from image
                image.remove_layer(resource_drawable)

                # get file iterator over original textures
                texture_file_iterator = textures_folder.enumerate_children(
                    "standard::*",
                    Gio.FileQueryInfoFlags.NONE,
                    None,
                )

                Gimp.progress_init(
                    "Processing textures in '" + textures_folder_path + "'..."
                )
                log.write("Processing textures in '" + textures_folder_path + "'...\n")

                # process original textures
                while True:
                    status = None
                    texture_file_info = None
                    texture_file = None
                    texture_image_layer = None
                    texture_image = None
                    texture_layer = None
                    resource_layer = None
                    resource_layer_copy = None
                    layer_mask = None

                    # get next file
                    status, texture_file_info, texture_file = (
                        # texture_file_iterator.iterate(cancellable)
                        texture_file_iterator.iterate()
                    )
                    if status == False:
                        # error handling
                        return procedure.new_return_values(
                            Gimp.PDBStatusType.EXECUTION_ERROR,
                            GLib.Error(_("Malformed DDS file.")),
                        )
                    elif (texture_file_info is None) or (texture_file is None):
                        # no more files to process
                        break
                    else:
                        # get file name
                        file_name = texture_file_info.get_attribute_as_string(
                            Gio.FILE_ATTRIBUTE_STANDARD_NAME
                        )

                        # skip non-dds files
                        if not file_name.lower().endswith(".dds"):
                            continue

                        # load texture image
                        import_dds_status, texture_image = utils.import_dds(
                            texture_file
                        )

                        # if there was an error with importing, skip
                        if import_dds_status != Gimp.PDBStatusType.SUCCESS:
                            continue

                        # skip texture images that do not have the same dimension as resource image
                        if not (
                            texture_image.get_width() == image_width
                            and texture_image.get_height() == image_height
                        ):
                            continue

                        # log name of file
                        log.write("Processing '" + file_name + "'...\n")

                        # get display name of texture
                        file_display_name = texture_file_info.get_attribute_as_string(
                            Gio.FILE_ATTRIBUTE_STANDARD_DISPLAY_NAME
                        )

                        # get texture layer from texture image
                        texture_image_layer = texture_image.get_layers()[0]

                        # create new texture layer in target image from texture layer
                        texture_layer = Gimp.Layer.new_from_drawable(
                            texture_image_layer, image
                        )
                        texture_layer.set_name(file_display_name + "_original")
                        image.insert_layer(texture_layer, None, -1)

                        # add resource layer
                        resource_layer = Gimp.Layer.new_from_drawable(
                            resource_drawable, image
                        )
                        resource_layer.set_name(resource_drawable_name)
                        image.insert_layer(resource_layer, None, -1)

                        # add new texture layer resource
                        resource_layer_copy = Gimp.Layer.new_from_drawable(
                            resource_drawable, image
                        )
                        resource_layer_copy.set_name(
                            file_display_name + "_" + resource_drawable_name
                        )
                        image.insert_layer(resource_layer_copy, None, -1)

                        # apply mask
                        layer_mask = texture_layer.create_mask(Gimp.AddMaskType.ALPHA)
                        resource_layer_copy.add_mask(layer_mask)
                        resource_layer_copy.remove_mask(Gimp.MaskApplyMode.APPLY)

                        # save file as xcf
                        file_path_xcf = (
                            texture_file.peek_path().removesuffix(".dds") + ".xcf"
                        )
                        file_xcf = Gio.File.new_for_path(file_path_xcf)
                        Gimp.file_save(
                            Gimp.RunMode.NONINTERACTIVE,
                            image,
                            file_xcf,
                            None,
                        )

                        # save file as dds
                        image.remove_layer(resource_layer)
                        image.remove_layer(texture_layer)
                        export_dds_status = utils.export_dds(image, texture_file)
                        image.remove_layer(resource_layer_copy)

                        if export_dds_status == Gimp.PDBStatusType.SUCCESS:
                            log.write("Successfully exported '" + file_name + "'!\n")
                        else:
                            log.write(
                                "Error: '" + file_name + "' could not be exported!\n"
                            )

                # add original resource layer back
                resource_layer = Gimp.Layer.new_from_drawable(resource_drawable, image)
                resource_layer.set_name(resource_drawable_name)
                image.insert_layer(resource_layer, None, -1)

                # clean image
                image.clean_all()

                Gimp.progress_end()

                log.write("Processed textures in '" + textures_folder_path + "'!\n")

                return procedure.new_return_values(
                    Gimp.PDBStatusType.SUCCESS, GLib.Error()
                )

            except IsADirectoryError:
                log.write("File is either a directory or file name is empty.\n")
                return procedure.new_return_values(
                    Gimp.PDBStatusType.EXECUTION_ERROR,
                    GLib.Error(_("File is either a directory or file name is empty.")),
                )
            except FileNotFoundError:
                log.write("Directory not found.\n")
                return procedure.new_return_values(
                    Gimp.PDBStatusType.EXECUTION_ERROR,
                    GLib.Error(_("Directory not found.")),
                )
            except PermissionError:
                log.write("You do not have permissions to write that file.\n")
                return procedure.new_return_values(
                    Gimp.PDBStatusType.EXECUTION_ERROR,
                    GLib.Error("You do not have permissions to write that file."),
                )

    def run_transfer_alpha(
        self, procedure, run_mode, image, drawables, config, run_data
    ):

        GimpUi.init(procedure.get_name())

        dialog = GimpUi.ProcedureDialog.new(procedure, config)

        dialog.fill()

        # if dialog is cancelled
        if not dialog.run():
            dialog.destroy()
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())

        use_selection = config.get_property("use_selection")
        layer_alpha = config.get_property("layer_alpha")
        layer_resource = config.get_property("layer_resource")

        if layer_alpha is None:
            error = "No alpha layer given."
            return procedure.new_return_values(
                Gimp.PDBStatusType.CALLING_ERROR, GLib.Error(error)
            )

        if layer_resource is None:
            error = "No resource layer given."
            return procedure.new_return_values(
                Gimp.PDBStatusType.CALLING_ERROR, GLib.Error(error)
            )

        Gimp.progress_init("Processing...")

        # create new texture layer in target image from texture layer
        layer_resource_copy = layer_resource.copy()
        image.insert_layer(
            layer_resource_copy, None, image.get_item_position(layer_resource)
        )

        # apply mask
        layer_mask = layer_alpha.create_mask(Gimp.AddMaskType.ALPHA)
        layer_resource_copy.add_mask(layer_mask)
        layer_resource_copy.remove_mask(Gimp.MaskApplyMode.APPLY)

        if use_selection:
            if not Gimp.Selection.is_empty(image):
                layer_resource.edit_clear()
                Gimp.Selection.invert(image)
                layer_resource_copy.edit_clear()

        Gimp.progress_end()

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(DovayaHairTextureCreator.__gtype__, sys.argv)
