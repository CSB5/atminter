#!/usr/bin/env python3
from pybuilder.core import use_plugin

use_plugin("python.core")
use_plugin("install_dependencies")

default_task = "publish"

@init
def initialize(project):
    project.build_depends_on('segtok')
    project.build_depends_on('nltk')