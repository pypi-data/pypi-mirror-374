import os
from zlib import crc32

from .reporter import set_func_coverage
from .reporter import set_line_coverage


class ToffeeRequest:
    def __init__(self, request):
        self.dut = None
        self.args = None
        self.request = request
        self.cov_groups = []

        self.waveform_filename = None
        self.coverage_filename = None

    def __add_cov_sample(self, cov_groups):
        """
        Add the coverage sample to the DUT.
        """

        assert self.dut is not None, "The DUT has not been set."
        assert self.cov_groups is not None, "The coverage group has not been set."

        if not isinstance(cov_groups, list):
            cov_groups = [cov_groups]

        def sample_helper(cov_point):
            return lambda _: cov_point.sample()

        for g in cov_groups:
            self.dut.xclock.StepRis(sample_helper(g))

    def __need_report(self):
        """
        Whether to generate the report
        """

        return self.request.config.getoption("--toffee-report")

    def create_dut(
        self,
        dut_cls,
        clock_name=None,
        waveform_filename=None,
        coverage_filename=None,
        dut_extra_args=(),
        dut_extra_kwargs={},
    ):
        """
        Create the DUT.

        Args:
            dut_cls: The DUT class.
            clock_name: The clock pin name.
            waveform_filename: The waveform filename. If not set, it will be auto-generated.
            coverage_filename: The coverage filename. If not set, it will be auto-generated.
            dut_extra_args: Extra positional arguments for the DUT. e.g., ("arg1", "args2")
            dut_extra_kwargs: Extra keyword arguments for the DUT. e.g., {"arg1": 1, "arg2": 2}
        Returns:
            The DUT instance.
        """

        final_kwargs = dict(dut_extra_kwargs)

        if self.__need_report():
            report_dir = os.path.dirname(self.request.config.option.report[0])
            request_name = self.request.node.name
            path_bytes = str(self.request.path).encode("utf-8")
            path_hash = format(crc32(path_bytes), 'x')
            export_filename = "_".join((dut_cls.__name__, request_name, path_hash))

            self.waveform_filename = (
                f"{report_dir}/{export_filename}.fst"
            )
            self.coverage_filename = (
                f"{report_dir}/{export_filename}.dat"
            )

            if waveform_filename is not None:
                self.waveform_filename = waveform_filename
            if coverage_filename is not None:
                self.coverage_filename = coverage_filename

            final_kwargs["waveform_filename"] = self.waveform_filename
            final_kwargs["coverage_filename"] = self.coverage_filename

            self.dut = dut_cls(*dut_extra_args, **final_kwargs)

            if self.cov_groups is not None:
                self.__add_cov_sample(self.cov_groups)
        else:
            if waveform_filename is not None:
                final_kwargs["waveform_filename"] = waveform_filename
            if coverage_filename is not None:
                final_kwargs["coverage_filename"] = coverage_filename

            self.dut = dut_cls(*dut_extra_args, **final_kwargs)

        if clock_name:
            self.dut.InitClock(clock_name)

        return self.dut

    def add_cov_groups(self, cov_groups, periodic_sample=True):
        """
        Add the coverage groups to the list.

        Args:
            cov_groups: The coverage groups to be added.
            periodic_sample: Whether to sample the coverage periodically.
        """

        if not isinstance(cov_groups, list):
            cov_groups = [cov_groups]
        self.cov_groups.extend(cov_groups)

        if self.dut is not None and periodic_sample:
            self.__add_cov_sample(cov_groups)

    def finish(self, request):
        """
        Finish the request.
        """

        if self.dut is not None:
            self.dut.Finish()

            if self.__need_report():
                set_func_coverage(request, self.cov_groups)
                set_line_coverage(request, self.coverage_filename)

        for g in self.cov_groups:
            g.clear()

        self.cov_groups.clear()


PreRequest = ToffeeRequest
