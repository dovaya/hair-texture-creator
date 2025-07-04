#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


def save_working_file(image: Gimp.Image, file):
    procedure = Gimp.get_pdb().lookup_procedure("gimp-xcf-save")
    config = procedure.create_config()
    config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
    config.set_property("image", image)
    config.set_property("file", file)
    result = procedure.run(config)
    success = result.index(0)
    return success


def import_dds(file):  # -> tuple:
    procedure = Gimp.get_pdb().lookup_procedure("file-dds-load")
    config = procedure.create_config()
    config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
    config.set_property("file", file)
    config.set_property("load-mipmaps", False)
    config.set_property("flip-image", False)
    result = procedure.run(config)
    success = result.index(0)
    image = result.index(1)
    return success, image


def export_dds(
    image,
    file,
):
    procedure = Gimp.get_pdb().lookup_procedure("file-dds-export")
    config = procedure.create_config()
    config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
    config.set_property("image", image)
    config.set_property("file", file)
    config.set_property("options", None)
    config.set_property("compression-format", "bc3, ")
    config.set_property("perceptual-metric", False)
    config.set_property("format", "default")
    config.set_property("save-type", "layer")
    config.set_property("flip-image", False)
    config.set_property("transparent-color", False)
    config.set_property("transparent-index", 0)
    config.set_property("mipmaps", "generate")
    config.set_property("mipmap-filter", "default")
    config.set_property("mipmap-wrap", "default")
    config.set_property("gamma-correct", False)
    config.set_property("srgb", False)
    config.set_property("gamma", 0)
    config.set_property("preserve-alpha-coverage", False)
    config.set_property("alpha-test-threshold", 0.5)
    result = procedure.run(config)
    success = result.index(0)
    return success
