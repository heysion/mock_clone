# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:textwidth=0:
# License: GPL2 or later see COPYING
# Written by Clark Williams
# Copyright (C) 2013 Clark Williams <clark.williams@gmail.com>

# python library imports
import re
import os
import os.path
import subprocess

# our imports

from mockbuild.trace_decorator import traceLog, getLog

import mockbuild.util

requires_api_version = "1.1"

# plugin entry point
@traceLog()
def init(plugins, conf, buildroot):
    ChrootScan(plugins, conf, buildroot)

# classes
class ChrootScan(object):
    """scan chroot for files of interest, copying to resultdir with relative paths"""
    @traceLog()
    def __init__(self, plugins, conf, buildroot):
        self.buildroot = buildroot
        self.config = buildroot.config
        self.state = buildroot.state
        self.scan_opts = conf
        self.regexes = self.config['plugin_conf']['chroot_scan_opts']['regexes']
        self.resultdir = os.path.join(buildroot.resultdir, "chroot_scan")
        plugins.add_hook("postbuild", self._scanChroot)
        getLog().info("chroot_scan: initialized")

    @traceLog()
    def _scanChroot(self):
        regexstr = "|".join(self.regexes)
        regex = re.compile(regexstr)
        chroot = self.buildroot.make_chroot_path()
        mockbuild.util.mkdirIfAbsent(self.resultdir)
        count = 0
        logger = getLog()
        logger.debug("chroot_scan: Starting scan of %s" % chroot)
        copied = []
        for root, _, files in os.walk(chroot):
            for f in files:
                m = regex.search(f)
                if m:
                    srcpath = os.path.join(root, f)
                    subprocess.call("cp --parents %s %s" % (srcpath, self.resultdir), shell=True)
                    count += 1
                    copied.append(srcpath)
        logger.debug("chroot_scan: finished with %d files found" % count)
        if count:
            logger.info("chroot_scan: %d files copied to %s" % (count, self.resultdir))
            logger.info("%s" % "\n".join(copied))
