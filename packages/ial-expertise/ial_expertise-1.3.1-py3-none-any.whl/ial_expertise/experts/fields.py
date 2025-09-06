#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fields parsers."""
import io
import numpy
import os
import re

from footprints import FPList, proxy as fpx
from bronx.fancies import loggers
from taylorism import Worker, batch_main

from . import OutputExpert, ExpertError
from .thresholds import NORMALIZED_FIELDS_DIFF, EPSILON

logger = loggers.getLogger(__name__)


class FieldsInFileExpert(OutputExpert):

    _footprint = dict(
        info = 'Read and compare the fields present in files.',
        attr = dict(
            expert = dict(
                values = ['fields_in_file',],  # just a way of picking this very expert
            ),
            kind = dict(
                info = "Vortex resources kinds addressed.",
                type = str,
            ),
            filename_re_pattern = dict(
                info = "Filename regular expression pattern.",
                type = str,
                optional = True,
                default = None,
            ),
            filenames = dict(
                info = "Filenames to process. If absent, will be determined " +
                       "according to reference resources and/or regular expressions on filenames.",
                type=FPList,
                optional = True,
                default=FPList([]),
            ),
            validate_if_bit_repro_only=dict(
                info="If True, Validated == Bit-repro; else, use normalized_validation_threshold.",
                type=bool,
                optional = True,
                default = True
            ),
            normalized_validation_threshold = dict(
                info = "Threshold on normalized distance for validation. " +
                       "Normalized distance is computed as normalized(test, ref) - normalized(ref, ref) " +
                       "where " +
                       "normalized(test, ref) == (test-ref.min()) / (ref.max()-ref.min())",
                type = float,
                optional = True,
                default = NORMALIZED_FIELDS_DIFF,
            ),
            ignore_meta = dict(
                info = "Ignore fields metadata in comparison.",
                type = bool,
                optional = True,
                default = False
            ),
            ignore_orphan_fields = dict(
                info = "Ignore fields that are present in only one of the resources.",
                type = bool,
                optional = True,
                default = False
            ),
            hide_bit_repro_fields = dict(
                info = "Do not show bit-reproducible fields in comparison summary.",
                type = bool,
                optional = True,
                default = True,
            ),
            compute_stats = dict(
                info = "Compute (min, avg, max) when parsing fields.",
                type = bool,
                optional = True,
                default = False
            ),
            parallel = dict(
                info = "Compute comparisons with multiple processes using taylorism.",
                type = bool,
                optional = True,
                default = False
            )
        )
    )

    # reference prefixes
    ref_prefix = 'ref.'
    cnty_prefix = 'continuity.'
    csty_prefix = 'consistency.'

    _filename_re_patterns = {
        # historic
        'historic':r'(?P<prefix>ICM(SH)|(UA))(?P<cnmexp>\w{4})(?P<area>.+)?\+(?P<term_h>\d+)(\:(?P<term_m>\d{2}))?(?P<sfx>\.sfx)?$',
        # post-processed
        'gridpoint':r'(?P<prefix>(PF)|(GRIBPF))(?P<cnmexp>\w{4})(?P<area>.+)?\+(?P<term_h>\d+)(\:(?P<term_m>\d{2}))?$',
        # coupling
        'boundary':r'(?P<prefix>CPLOUT)\+(?P<term_h>\d+)(\:(?P<term_m>\d{2}))?$',
        # pgd
        'pgdfa':r'(?P<prefix>PGD)\.fa$',
        # prep
        'initial_condition':r'(?P<prefix>PREP1_interpolated)\.fa$',
        # clim (c923)
        'clim_model':r'(?P<prefix>Const\.Clim)(\..*)?$',
        # DDH
        'ddh':r'((?P<prefix>.+)\.lfa)|(DHF(?P<scope>\w{2})(?P<exp>\w{4})+(?P<term_h>\d+)(\:(?P<term_m>\d{2}))?)$',
        }

    def __init__(self, *args, **kwargs):
        super(FieldsInFileExpert, self).__init__(*args, **kwargs)
        if not self.filename_re_pattern:
            assert self.kind in self._filename_re_patterns, \
            f"Unknown kind={self.kind}, please change or specify 'filename_re_pattern'."
            self._attributes['filename_re_pattern'] = self._filename_re_patterns[self.kind]
        self._filename_re = re.compile(self.filename_re_pattern)

    def _find_files_to_parse(self):
        self.files = {}
        if len(self.filenames) > 0:
            for f in self.filenames:
                if f not in os.listdir(os.getcwd()):
                    message = "Output file not found: {}".format(f)
                    if self.fatal_exceptions:
                        raise IOError(message)
                    else:
                        logger.warning(' '.join([message," => ignored in comparison."]))
                else:
                    self.files[f] = {}
        else:
            # find files in working directory
            filenames = os.listdir(os.getcwd())
            for f in filenames:
                if self.filename_re.match(f):
                    self.files[f] = {}

    def _parse(self):
        """Parse file, list fields."""
        import epygram
        epygram.init_env()
        self._find_files_to_parse()
        for filename in self.files:
            r = epygram.formats.resource(filename, 'r')
            self.files[filename] = {str(f):{} for f in r.listfields()}
            if self.compute_stats:
                for f in r.listfields():
                    fld = r.readfield(f)
                    self.files[filename][str(f)]['min'] = fld.min()
                    self.files[filename][str(f)]['avg'] = fld.mean()
                    self.files[filename][str(f)]['max'] = fld.max()

    def summary(self):
        summary = {'Number of files':len(self.files),
                   'Files':{f:{'Number of fields':len(self.files[f]),}
                            for f in self.files}
                   }
        if self.compute_stats:
            for f in self.files:
                summary['Files'][f]['Stats'] = self.files[f]
        return summary

    def _make_pairs(self, references):
        ref_handlers = [r for r in references
                        if r.resource.kind == self.kind]
        ref_filenames = [r.container.localpath() for r in ref_handlers]
        if len(self.filenames) == 0:
            pairs = self._make_pairs_from_references(ref_filenames)
        else:
            pairs = self._make_pairs_from_attribute(ref_filenames)
        return pairs

    def _make_pairs_from_references(self, ref_filenames):
        pairs = []
        # find local files matching references
        for ref in ref_filenames:
            if not os.path.exists(ref):
                message = "Reference file: '{}' not found'.".format(ref)
                if self.fatal_exceptions:
                    raise ExpertError(message)
                else:
                    logger.warning(' '.join([message," => ignored in comparison."]))
                    continue
            # find test filename from ref
            f = ref
            for prefix in (self.ref_prefix, self.cnty_prefix, self.csty_prefix):
                if f.startswith(prefix):
                    f = f[len(prefix):]
            if not os.path.exists(f):
                message = "Reference file: '{}' has no local output equivalent '{}'.".format(ref, f)
                if self.fatal_exceptions:
                    raise ExpertError(message)
                else:
                    logger.warning(' '.join([message," => ignored in comparison."]))
            else:
                pairs.append((f, ref))
        return pairs

    def _make_pairs_from_attribute(self, ref_filenames):
        pairs = []
        # start from list of asked files
        for f in self.filenames:
            if f not in os.listdir(os.getcwd()):
                message = "Output file not found: {}".format(f)
                if self.fatal_exceptions:
                    raise ExpertError(message)
                else:
                    logger.warning(' '.join([message," => ignored in comparison."]))
                    continue
            ref = None
            for p in (self.ref_prefix, self.cnty_prefix, self.csty_prefix):
                if p + f in ref_filenames:
                    ref = p + f
                    break
            if ref is None:
                message = "Reference file: '{}' not found.".format(ref)
                if self.fatal_exceptions:
                    raise ExpertError(message)
                else:
                    logger.warning(' '.join([message," => ignored in comparison."]))
            else:
                pairs.append((f, ref))
        return pairs

    def _compare(self, references):
        """
        Compare to a reference.

        :param references: the list of reference resource handlers
        """
        pairs = self._make_pairs(references)
        comp = {}
        if len(pairs) > 0:
            if not self.parallel:
                for (test, ref) in pairs:
                    logger.info('{} // {}'.format(test, ref))
                    comp[test] = compare_2_files(test, ref,
                                                 ignore_meta=self.ignore_meta,
                                                 ignore_orphan_fields=self.ignore_orphan_fields,
                                                 hide_bit_repro_fields=self.hide_bit_repro_fields,
                                                 validate_if_bit_repro_only=self.validate_if_bit_repro_only,
                                                 normalized_validation_threshold=self.normalized_validation_threshold,
                                                 fatal_exceptions=self.fatal_exceptions)
            else:
                report = batch_main(common_instructions=dict(ignore_meta=self.ignore_meta,
                                                             ignore_orphan_fields=self.ignore_orphan_fields,
                                                             hide_bit_repro_fields=self.hide_bit_repro_fields,
                                                             validate_if_bit_repro_only=self.validate_if_bit_repro_only,
                                                             normalized_validation_threshold=self.normalized_validation_threshold,
                                                             fatal_exceptions=self.fatal_exceptions),
                                    individual_instructions=dict(test=[p[0] for p in pairs],
                                                                 ref=[p[1] for p in pairs]),
                                    scheduler=fpx.scheduler(limit='threads', max_threads=0, binded=False),  # issue with nmipt
                                    #scheduler=fpx.scheduler(limit='threads', max_threads=0, binded=True),
                                    print_report=lambda arg: None)
                for file_report in report['workers_report']:
                    test_filename = file_report['report'][0]
                    file_comparison = file_report['report'][1]
                    comp[test_filename] = file_comparison
            overall = {}
            overall['Validated'] = all([c.get('Validated') for c in comp.values()])
            overall['Bit-reproducible'] = all([c.get('Bit-reproducible') for c in comp.values()])
            overall['Validated means'] = comp[pairs[0][0]].get('Validated means')
            overall['mainMetrics'] = comp[pairs[0][0]].get('mainMetrics')
            overall['Max normalized diff'] = '{:%}'.format(
                max([float(c.get('Max normalized diff').strip('%')) / 100.
                     for c in comp.values()]))
            comp.update(overall)
        else:
            msg = f"No kind={self.kind} reference resources provided"
            if self.fatal_exceptions:
                raise ExpertError(msg)
            else:
                logger.warning(' '.join([msg," => ignored in comparison."]))
                comp['comparisonStatus'] = {'symbol':'0',
                                            'short':'- No ref -',
                                            'text':f'No adequate reference available (kind={self.kind})'}
        return comp


def compare_2_files(test, ref,
                    ignore_meta=False,
                    ignore_orphan_fields=False,
                    hide_bit_repro_fields=True,
                    validate_if_bit_repro_only=True,
                    normalized_validation_threshold=NORMALIZED_FIELDS_DIFF,
                    fatal_exceptions=True,
                    verbose=False):
    """
    Compare 2 files containing fields.

    Normalized distance is computed as normalized(test, ref) - normalized(ref, ref)
    where
    normalized(test, ref) == (test-ref.min()) / (ref.max()-ref.min())

    :param ignore_meta: Ignore metadata in comparison.
    :param ignore_orphan_fields: Ignore fields present in only one of the resources.
    :param hide_bit_repro_fields: Do not show bit-reproducible fields in comparison.
    :param validate_if_bit_repro_only: If True, Validated == Bit-repro; else, use normalized_validation_threshold.
    :param normalized_validation_threshold: Threshold on normalized distance for validation.
    :param fatal_exceptions: Raise comparing errors.
    """
    import epygram
    epygram.init_env()
    t = epygram.formats.resource(test, 'r')
    r = epygram.formats.resource(ref, 'r')
    comp = {}
    # list fields
    test_list = list(t.listfields())
    ref_list = list(r.listfields())
    # new and lost
    new_fields = [f for f in test_list if f not in ref_list]
    lost_fields = [f for f in ref_list if f not in test_list]
    # errors
    uncompared_fields = []
    # common fields: comparison
    intersection = [f for f in test_list if f in ref_list]
    if len(intersection) > 0 and isinstance(intersection[0], str):
        intersection = sorted(intersection)
    fields_status = {}
    max_normalized_diff = 0.
    for f in intersection:
        if ignore_field(f):
            continue
        try:
            (status,
             max_normalized_diff) = compare_2_fields(t, r, f, max_normalized_diff,
                                                     ignore_meta=ignore_meta,
                                                     normalized_validation_threshold=normalized_validation_threshold)
        except Exception as e:
            if fatal_exceptions:
                raise
            else:
                uncompared_fields.append(f)
            status = {'Error during comparison':str(e)}
        if not status.get('Data bit-repro', False) or not hide_bit_repro_fields:
            fields_status[str(f)] = status
    # status over all fields
    comp['Validated'] = all([status.get('Validated', False) for status in fields_status.values()])
    if validate_if_bit_repro_only:
        comp['Validated means'] = 'All fields have identical shape/mask than reference, and data is bit-repro'
    else:
        comp['Validated means'] = ' '.join(['All fields have identical shape/mask than reference,',
                                            'and normalized errors lower than {}'.format(
                                                normalized_validation_threshold)])
    if not ignore_orphan_fields:  # check that there is no orphan
        if len(new_fields + lost_fields) > 0:
            comp['Validated'] = False
        comp['Validated means'] += ', and no field is orphan on one or the other side.'
    # bit-repro status
    comp['Bit-reproducible'] = all([(status.get('Data bit-repro', False) and
                                     status.get('Validity diff', None) is None and
                                     status.get('Geometry diff', None) is None)
                                    for status in fields_status.values()])
    comp['Common fields differences'] = fields_status
    comp['Max normalized diff'] = '{:%}'.format(max_normalized_diff)
    comp['mainMetrics'] = 'Max normalized diff'
    comp['New fields'] = new_fields if len(new_fields) > 0 else None
    comp['Lost fields'] = lost_fields if len(lost_fields) > 0 else None
    comp['Unable to compare fields'] = uncompared_fields if len(uncompared_fields) > 0 else None
    return comp


def compare_2_fields(test_resource, ref_resource, fid,
                     max_normalized_diff=0.,
                     ignore_meta=False,
                     validate_if_bit_repro_only=True,
                     normalized_validation_threshold=NORMALIZED_FIELDS_DIFF):
    """
    Compare two same fields from different resources.

    Normalized distance is computed as normalized(test, ref) - normalized(ref, ref)
    where
    normalized(test, ref) == (test-ref.min()) / (ref.max()-ref.min())

    :param max_normalized_diff: maximum normalized difference to be updated
    :param ignore_meta: Ignore metadata in comparison.
    :param validate_if_bit_repro_only: If True, Validated == Bit-repro; else, use normalized_validation_threshold.
    :param normalized_validation_threshold: Threshold on normalized distance for validation.
    """
    import epygram
    from epygram.formats.DDHLFA import DDHLFA
    status = {}
    validated = True
    tfld = test_resource.readfield(fid)
    rfld = ref_resource.readfield(fid)
    if not isinstance(tfld, epygram.fields.MiscField):
        if isinstance(ref_resource, DDHLFA):
            # fields in DDHLFA are gathered as FieldSet, one per DDH domain; here we gather them into one field, using
            # temporal dimension for that matter
            tfld0 = tfld[0]
            for f in tfld[1:]:
                tfld0.extend(f)
            tfld = tfld0
            rfld0 = rfld[0]
            for f in rfld[1:]:
                rfld0.extend(f)
            rfld = rfld0
        for fld in (tfld, rfld):  # would not be sure of the meaning of errors in spectral space
            if fld.spectral:
                fld.sp2gp()
    # metadata
    if not isinstance(tfld, epygram.fields.MiscField) and not ignore_meta:
        status['Validity diff'] = tfld.validity.recursive_diff(rfld.validity)
        status['Geometry diff'] = tfld.geometry.recursive_diff(rfld.geometry)
        if any([status.get('Validity diff', None),
                status.get('Geometry diff', None)]):
            validated = False
    # data
    if tfld.data.shape != rfld.data.shape:
        status['Normalized data diff'] = 'Comparison not possible: dimensions differ'
        validated = False
        status['Data bit-repro'] = False
    else:
        if isinstance(tfld.data.dtype, (int, float)):
            status['Data bit-repro'] = bool(numpy.all(tfld.data - rfld.data <= EPSILON))
        else:
            status['Data bit-repro'] = bool(numpy.all(tfld.data == rfld.data))
        if not status['Data bit-repro']:
            data_diff, common_mask = tfld.normalized_comparison(rfld)
            status['Normalized data diff'] = data_diff
            status['Mask is common'] = common_mask
            if not common_mask:
                validated = False
            loc_max = max([abs(v) for v in data_diff.values()])
            if loc_max > max_normalized_diff:
                max_normalized_diff = loc_max
        # if not bit-repro, check differences are under thresholds
        if not status['Data bit-repro']:
            if validate_if_bit_repro_only:
                validated = False
            else:
                if any([abs(v) >= normalized_validation_threshold
                        for v in data_diff.values()]):
                    validated = False
    status['Validated'] = validated
    return status, max_normalized_diff


def ignore_field(fid):
    """Test if field is to be ignored in comparison."""
    ignore = False
    if isinstance(fid, str):
        if fid.startswith('SFX._FBUF_'):
            ignore = True
    return ignore


class FieldComparer(Worker):
    """
    Compares 2 files.
    """

    _footprint = dict(
        info = "Compares 2 files.",
        attr = dict(
            test=dict(
                info="Test file.",
            ),
            ref=dict(
                info="Ref file.",
            ),
            ignore_meta=dict(
                type=bool,
                optional=True,
                default=False
            ),
            ignore_orphan_fields=dict(
                type=bool,
                optional=True,
                default=False
            ),
            hide_bit_repro_fields=dict(
                type=bool,
                optional=True,
                default=True
            ),
            normalized_validation_threshold=dict(
                type=float,
                optional=True,
                default=NORMALIZED_FIELDS_DIFF
            ),
            fatal_exceptions=dict(
                type=bool,
                optional=True,
                default=True
            ),
        )
    )

    def _task(self):
        return (self.test,
                compare_2_files(self.test, self.ref,
                               ignore_meta=self.ignore_meta,
                               ignore_orphan_fields=self.ignore_orphan_fields,
                               hide_bit_repro_fields=self.hide_bit_repro_fields,
                               normalized_validation_threshold=self.normalized_validation_threshold,
                               fatal_exceptions=self.fatal_exceptions))


def scatter_fields_process_summary(report_file, all_in_one=False):
    """
    Process a taskinfo summary file, and plot comparisons.

    :param report_file: taskinfo comparison summary file name
    :param all_in_one: to save all plot into one html file (does not work)
    """
    import json
    from bokeh.io import save, output_file  # @UnresolvedImport
    from bokeh.layouts import column  # @UnresolvedImport
    with open(report_file, 'r') as f:
        report = json.load(f)
    report = report['fields_in_file']
    if all_in_one:
        output_file("{}.html".format(report_file),
                    title="Comparison of Fields")
    plots = []
    for filename, r in report.items():
        if isinstance(r, dict):
            plots.append(scatter_fields_comparison(filename, r,
                                                   save_html=not all_in_one))
    if all_in_one:
        save(column(*plots))


def scatter_fields_comparison0(grid_point_file_name,
                               report,
                               save_html=False):
    """
    Make a 'bokeh' scatter plot of fields comparison from 1 file.

    :param grid_point_file_name: name of the gridpoint file (for Labelling)
    :param report: a dict, as returned by function **compare_2_files()**
    :param save_html: to save plot in a html file or just return it
    """
    from bokeh.io import output_file, save  # @UnresolvedImport
    from bokeh.plotting import figure  # @UnresolvedImport
    # print new/lost
    print('-' * (len(grid_point_file_name) + 6))
    print("File: " + grid_point_file_name)
    print("  Lost fields:", report['Lost fields'])
    print("  New fields:", report['New fields'])
    # prepare diffs
    diffs = report['Common fields differences']
    flds = []
    biases = []
    stds = []
    errmaxs = []
    masks = []
    for fld, status in diffs.items():
        flds.append(fld.replace("'", ""))
        biases.append(status['Normalized data diff']['bias'])
        stds.append(status['Normalized data diff']['std'])
        errmaxs.append(status['Normalized data diff']['errmax'])
        masks.append(status.get('Mask is common', True))
    src = {'bias':biases, 'std':stds, 'errmax':errmaxs, 'fid':flds, 'mask': masks,
           'std1':[6.+min(s*2e2, 1e2) for s in stds],
           'errmax1':[6.+min(e*2e2, 1e2) for e in errmaxs],
           'mask_as_color':['blue' if m else 'red' for m in masks]}
    title = "{} : Normalized errors of fields in file".format(grid_point_file_name)
    tools = "hover,pan,wheel_zoom,box_zoom,reset,save"
    # plot
    p = figure(tools=tools, toolbar_location="above", plot_width=1200, title=title,
               y_axis_type="log")
    p.background_fill_color = "#dddddd"
    p.xaxis.axis_label = "Bias"
    p.yaxis.axis_label = "Max error"
    p.grid.grid_line_color = "white"
    p.hover.tooltips = [
        ("Field id", "@fid"),
        ("Bias", "@bias"),
        ("Errors Stdev", "@std"),
        ("Max error", "@errmax"),
        ("Mask OK", "@mask")
    ]
    p.scatter('bias', 'errmax', source=src, size='std1',
              color='mask_as_color', line_color="black", fill_alpha=0.8)
    p.x_range.start = min(biases) - abs(min(biases)) * 0.05
    p.x_range.end = max(biases) + abs(max(biases)) * 0.05
    p.y_range.start = min(errmaxs) - abs(min(errmaxs)) * 0.05
    p.y_range.end = max(errmaxs) + abs(max(errmaxs)) * 0.05
    if save_html:
        html_name = "{}.html".format(grid_point_file_name)
        print("=>", html_name)
        output_file(html_name,
                    title=title)
        save(p)
    return p


def scatter_fields_comparison(grid_point_file_name,
                              report,
                              save_html=False):
    """
    Make a 'bokeh' scatter plot of fields comparison from 1 file.

    :param grid_point_file_name: name of the gridpoint file (for Labelling)
    :param report: a dict, as returned by function **compare_2_files()**
    :param save_html: to save plot in a html file or just return it
    """
    from bokeh.io import output_file, save, show  # @UnresolvedImport
    from bokeh.plotting import figure  # @UnresolvedImport
    from bokeh.layouts import column, row
    # print new/lost
    print('-' * (len(grid_point_file_name) + 6))
    print("File: " + grid_point_file_name)
    print("  Lost fields:", report['Lost fields'])
    print("  New fields:", report['New fields'])
    # prepare diffs
    diffs = report['Common fields differences']
    flds = []
    biases = []
    stds = []
    errmaxs = []
    masks = []
    for fld, status in diffs.items():
        flds.append(fld.replace("'", ""))
        biases.append(status['Normalized data diff']['bias'])
        stds.append(status['Normalized data diff']['std'])
        errmaxs.append(status['Normalized data diff']['errmax'])
        masks.append(status.get('Mask is common', True))
    src = {'bias':biases, 'std':stds, 'errmax':errmaxs, 'fid':flds, 'mask': masks,
           'std1':[6.+min(s*2e2, 0.5*1e2) for s in stds],
           'errmax1':[6.+min(e*2e2, 0.5*1e2) for e in errmaxs],
           'mask_as_color':['blue' if m else 'red' for m in masks]}
    title = "{} : Normalized errors of fields in file".format(grid_point_file_name)
    tools = "hover,pan,wheel_zoom,box_zoom,reset,save"

    def subplot(on_x='bias', on_y='errmax', size='std1',
                y_range=['min', 'max'],
                plot_width=600, plot_height=400,
                **other_figure_kwargs):
        """
        Subfunction to plot.

        :param on_x: choice for x coordinate
        :param on_y: choice for y coordinate
        :param size: choice for size coordinate
        :param y_range: kind of y axis range
            ('min', 'max'), (0, 'max'), ...
        :param other_figure_kwargs: passed to figure()
        :return: the figure object
        """
        p = figure(plot_width=plot_width, plot_height=plot_height,
                   tools=tools, toolbar_location="above",
                   **other_figure_kwargs)
        p.background_fill_color = "#dddddd"
        p.grid.grid_line_color = "white"
        p.hover.tooltips = [
            ("Field id", "@fid"),
            ("Bias", "@bias"),
            ("Errors Stdev", "@std"),
            ("Max error", "@errmax"),
            ("Mask OK", "@mask")
        ]
        p.scatter(on_x, on_y, size=size, source=src,
                  color='mask_as_color',
                  line_color="black",
                  fill_alpha=0.8)
        p.x_range.start = min(src[on_x]) - abs(min(src[on_x])) * 0.05
        p.x_range.end = max(src[on_x]) + abs(max(src[on_x])) * 0.05
        if y_range[0] == 'min':
            y_range[0] = min(src[on_y])
        p.y_range.start = y_range[0] - abs(y_range[0]) * 0.05
        if y_range[1] == 'max':
            y_range[1] = max(y_range[0] * 2, max(src[on_y]))
        p.y_range.end = y_range[1] + abs(y_range[1]) * 0.05
        return p

    if len(diffs) > 0:
        # --- max errors ---
        y_range = (1e-4, 1)
        # plot Above
        p1 = subplot(y_range=[y_range[1], 'max'], y_axis_type="log",
                     title="Max errors")
        p1.yaxis.axis_label = "Max Normalized error > {}".format(y_range[1])
        # plot Middle
        p2 = subplot(y_range=y_range, y_axis_type="log")
        p2.yaxis.axis_label = "Max Normalized error in {}".format(y_range)
        # plot Below
        p3 = subplot(y_range=(0, y_range[0]))
        p3.yaxis.axis_label = "Max Normalized error < {}".format(y_range[0])
        p3.xaxis.axis_label = "Bias"
        c1 = column(p1, p2, p3)

        # --- std ---
        # plot Above
        p1 = subplot(on_y='std', size='errmax1',
                     y_range=[y_range[1], 'max'], y_axis_type="log",
                     title="Std.dev")
        p1.yaxis.axis_label = "Normalized Std.dev > {}".format(y_range[1])
        # plot Middle
        p2 = subplot(on_y='std', size='errmax1',
                     y_range=y_range, y_axis_type="log")
        p2.yaxis.axis_label = "Normalized Std.dev in {}".format(y_range)
        # plot Below
        p3 = subplot(on_y='std', size='errmax1',
                     y_range=(0, y_range[0]))
        p3.yaxis.axis_label = "Normalized Std.dev < {}".format(y_range[0])
        p3.xaxis.axis_label = "Bias"
        c2 = column(p1, p2, p3)

        r = row(c1, c2)

        if save_html:
            html_name = "{}.html".format(grid_point_file_name)
            print("=>", html_name)
            output_file(html_name,
                        title=title)
            save(r)
    else:
        r = None
        print("All fields are bit-reproducible !")
    return r
