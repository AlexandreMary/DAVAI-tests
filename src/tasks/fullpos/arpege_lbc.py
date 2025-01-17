# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, unicode_literals, division

import footprints.util
from footprints import FPDict, FPList

import vortex
from vortex import toolbox
from vortex.layout.nodes import Task, Driver
import davai
from davai_taskutil.mixins import DavaiIALTaskMixin, IncludesTaskMixin


class ArpegeLBCbyFullpos(Task, DavaiIALTaskMixin, IncludesTaskMixin):

    experts = [FPDict({'kind':'fields_in_file'}), FPDict({'kind':'norms'})] + davai.util.default_experts()

    def process(self):
        self._wrapped_init()
        self._notify_start_inputs()

        # 0./ Promises
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._wrapped_promise(**self._promised_listing())
            self._wrapped_promise(**self._promised_expertise())
            #-------------------------------------------------------------------------------

        # 1.1.0/ Reference resources, to be compared to:
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._wrapped_input(**self._reference_continuity_expertise())
            self._wrapped_input(**self._reference_continuity_listing())
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Reference',  # LBC files
                block          = self.output_block(),
                experiment     = self.conf.ref_xpid,
                fatal          = False,
                format         = 'fa',
                geometry       = self.conf.target_geometries,
                kind           = 'boundary',
                local          = 'ref.[geometry::tag]/MODELSTATE_[model]_[term::fmthm].[geometry::area::upper].out',
                source_app     = self.conf.source_vapp,
                source_conf    = self.conf.source_vconf,
                source_cutoff  = self.conf.cutoff,
                term           = self.conf.terms,
            )
            #-------------------------------------------------------------------------------

        # 1.1.1/ Static Resources:
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._load_usual_tools()  # LFI tools, ecCodes defs, ...
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Initial Clim',
                format         = 'fa',
                genv           = self.conf.appenv,
                kind           = 'clim_model',
                local          = 'Const.Clim.m[month]',
                month          = [self.conf.rundate.month, self.conf.rundate.month + 1],
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Target Clim',
                format         = 'fa',
                genv           = self.conf.appenv,
                geometry       = self.conf.target_geometries,
                kind           = 'clim_model',
                local          = 'const.clim.[geometry::area::upper].m[month]',
                model          = 'aladin',
                month          = [self.conf.rundate.month, self.conf.rundate.month +1],
            )
            #-------------------------------------------------------------------------------

        # 1.1.2/ Static Resources (namelist(s) & config):
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._wrapped_input(
                role           = 'ObjectNamelist',
                binary         = 'aladin',
                format         = 'ascii',
                fp_terms       = {'geotag':{g.tag:FPList(self.conf.terms) for g in self.conf.target_geometries}},
                genv           = self.conf.appenv,
                geotag         = [g.tag for g in self.conf.target_geometries],
                intent         = 'inout',
                kind           = 'namelist_fpobject',
                local          = 'namelist_obj_[geotag]',
                source         = 'geometries/[geotag]_[cutoff].nam',
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Namelist',
                binary         = 'aladin',
                format         = 'ascii',
                genv           = self.conf.appenv,
                intent         = 'inout',
                kind           = 'namelist',
                local          = 'fort.4',
                source         = 'e903_noMCUF.nam',
            )
            #-------------------------------------------------------------------------------

        # 1.1.3/ Static Resources (executables):
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            #-------------------------------------------------------------------------------
            tbx = self._wrapped_executable(
                role           = 'Binary',
                binmap         = 'gmap',
                format         = 'bullx',
                kind           = 'mfmodel',
                local          = 'ARPEGE.EX',
                remote         = self.guess_pack(),
                setcontent     = 'binaries',
            )
            #-------------------------------------------------------------------------------

        # 1.2/ Initial Flow Resources: theoretically flow-resources, but statically stored in input_shelf
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._wrapped_input(
                role           = 'Model State',
                block          = 'forecast',
                experiment     = self.conf.input_shelf,
                format         = 'fa',
                kind           = 'historic',
                local          = 'MODELSTATE_[model]_[term::fmthm]',
                term           = self.conf.terms,
                vapp           = self.conf.shelves_vapp,
                vconf          = self.conf.shelves_vconf,
            )
            #-------------------------------------------------------------------------------

        # 2.1/ Flow Resources: produced by another task of the same job
        if 'fetch' in self.steps:
            pass
            #-------------------------------------------------------------------------------

        # 2.2/ Compute step
        if 'compute' in self.steps:
            self._notify_start_compute()
            self.sh.title('Toolbox algo = tbalgo')
            tbalgo = toolbox.algo(
                crash_witness  = True,
                drhookprof     = self.conf.drhook_profiling,
                engine         = 'parallel',
                kind           = 'fpserver',
                outdirectories = [g.tag for g in self.conf.target_geometries],
            )
            print(self.ticket.prompt, 'tbalgo =', tbalgo)
            print()
            self.component_runner(tbalgo, tbx)
            #-------------------------------------------------------------------------------
            self.run_expertise()
            #-------------------------------------------------------------------------------

        # 2.3/ Flow Resources: produced by this task and possibly used by a subsequent flow-dependant task
        if 'backup' in self.steps:
            self._wrapped_output(
                role           = 'LBC files',
                block          = self.output_block(),
                experiment     = self.conf.xpid,
                format         = 'fa',
                geometry       = self.conf.target_geometries,
                kind           = 'boundary',
                local          = '[geometry::tag]/MODELSTATE_[model]_[term::fmthm].[geometry::area::upper].out',
                namespace      = self.REF_OUTPUT,
                source_app     = self.conf.source_vapp,
                source_conf    = self.conf.source_vconf,
                source_cutoff  = self.conf.cutoff,
                term           = self.conf.terms,
            )
            #-------------------------------------------------------------------------------

        # 3.0.1/ Davai expertise:
        if 'late-backup' in self.steps or 'backup' in self.steps:
            self._wrapped_output(**self._output_expertise())
            self._wrapped_output(**self._output_comparison_expertise())
            #-------------------------------------------------------------------------------

        # 3.0.2/ Other output resources of possible interest:
        if 'late-backup' in self.steps or 'backup' in self.steps:
            self._wrapped_output(**self._output_listing())
            self._wrapped_output(**self._output_stdeo())
            self._wrapped_output(**self._output_drhook_profiles())
            #-------------------------------------------------------------------------------

