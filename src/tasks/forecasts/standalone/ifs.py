# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, unicode_literals, division

from footprints import FPDict

import vortex
from vortex import toolbox
from vortex.layout.nodes import Task, Family, Driver
from common.util.hooks import update_namelist
import davai

from davai_taskutil.mixins import DavaiIALTaskMixin, IncludesTaskMixin


class StandaloneIFSForecast(Task, DavaiIALTaskMixin, IncludesTaskMixin):

    experts = [FPDict({'kind':'norms', 'plot_spectral':True}), FPDict({'kind':'fields_in_file'})] + davai.util.default_experts()

    def output_block(self):
        return '-'.join([self.conf.prefix,
                         self.tag])

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
                role           = 'Reference',  # ModelState gp atm
                block          = self.output_block(),
                experiment     = self.conf.ref_xpid,
                fatal          = False,
                format         = '[nativefmt]',
                kind           = 'historic',
                local          = 'ref.ICMUAFCST+{:06d}'.format(int(self.conf.expertise_term)),
                nativefmt      = 'grib',
                subset         = 'gpatm',
                term           = self.conf.expertise_term,
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Reference',  # ModelState spec atm
                block          = self.output_block(),
                experiment     = self.conf.ref_xpid,
                fatal          = False,
                format         = '[nativefmt]',
                kind           = 'historic',
                local          = 'ref.ICMSHFCST+{:06d}'.format(int(self.conf.expertise_term)),
                nativefmt      = 'grib',
                subset         = 'specatm',
                term           = self.conf.expertise_term,
            )
            #-------------------------------------------------------------------------------

        # 1.1.1/ Static Resources:
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._load_usual_tools()  # LFI tools, ecCodes defs, ...
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'RrtmConst',
                format         = 'unknown',
                genv           = self.conf.commonenv,
                kind           = 'rrtm',
                local          = 'rrtm.const.tgz',
            )
            #-------------------------------------------------------------------------------

        # 1.1.2/ Static Resources (namelist(s) & config):
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            #-------------------------------------------------------------------------------
            tbport = self._wrapped_input(
                role           = 'PortabilityNamelist',
                binary         = 'arpifs',
                format         = 'ascii',
                genv           = self.conf.appenv,
                intent         = 'in',
                kind           = 'namelist',
                local          = 'portability.nam',
                source         = 'portability/{}'.format(self.conf.target_host),
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Namelist',
                binary         = 'arpifs',
                format         = 'ascii',
                genv           = self.conf.appenv,
                hook_port      = (update_namelist, tbport),
                intent         = 'inout',
                kind           = 'namelist',
                local          = 'fort.4',
                source         = 'IFS/namelist_fc',
            )
            #-------------------------------------------------------------------------------

        # 1.1.3/ Static Resources (executables):
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            #-------------------------------------------------------------------------------
            tbx = self._wrapped_executable(
                role           = 'Binary',
                binmap         = 'gmap',
                format         = 'bullx',
                kind           = 'ifsmodel',
                local          = 'IFS.X',
                remote         = self.guess_pack(),
                setcontent     = 'binaries',
            )
            #-------------------------------------------------------------------------------

        # 1.2/ Flow Resources (initial): theoretically flow-resources, but statically stored in input_shelf
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'ModelStateIn # spec atm',
                block          = 'init',
                date           = self.conf.rundate,
                experiment     = self.conf.input_shelf,
                format         = '[nativefmt]',
                kind           = 'historic',
                local          = 'ICMSHFCSTINIT',
                namespace      = self.REF_OUTPUT,
                nativefmt      = 'grib',
                subset         = 'specatm',
                term           = 0,
                vapp           = self.conf.shelves_vapp,
                vconf          = self.conf.shelves_vconf,
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'ModelStateIn # gp atm',
                block          = 'init',
                date           = self.conf.rundate,
                experiment     = self.conf.input_shelf,
                format         = '[nativefmt]',
                kind           = 'historic',
                local          = 'ICMGGFCSTINIUA',
                namespace      = self.REF_OUTPUT,
                nativefmt      = 'grib',
                subset         = 'gpatm',
                term           = 0,
                vapp           = self.conf.shelves_vapp,
                vconf          = self.conf.shelves_vconf,
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'ModelStateIn # surf',
                block          = 'init',
                date           = self.conf.rundate,
                experiment     = self.conf.input_shelf,
                format         = '[nativefmt]',
                kind           = 'historic',
                local          = 'ICMGGFCSTINIT',
                namespace      = self.REF_OUTPUT,
                nativefmt      = 'grib',
                subset         = 'gpsurf',
                term           = 0,
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
                kind           = 'forecast',
            )
            print(self.ticket.prompt, 'tbalgo =', tbalgo)
            print()
            self.component_runner(tbalgo, tbx)
            #-------------------------------------------------------------------------------
            self.run_expertise()
            #-------------------------------------------------------------------------------

        # 2.3/ Flow Resources: produced by this task and possibly used by a subsequent flow-dependant task
        if 'backup' in self.steps:
            #-------------------------------------------------------------------------------
            self._wrapped_output(
                role           = 'ModelStateOut # gp atm',
                block          = self.output_block(),
                experiment     = self.conf.xpid,
                format         = '[nativefmt]',
                kind           = 'historic',
                local          = 'ICMUAFCST+{glob:term:\d+}',
                nativefmt      = 'grib',
                subset         = 'gpatm',
                term           = '[glob:term]',
            )
            #-------------------------------------------------------------------------------
            self._wrapped_output(
                role           = 'ModelStateOut # spec atm',
                block          = self.output_block(),
                experiment     = self.conf.xpid,
                format         = '[nativefmt]',
                kind           = 'historic',
                local          = 'ICMSHFCST+{glob:term:\d+}',
                nativefmt      = 'grib',
                subset         = 'specatm',
                term           = '[glob:term]',
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

