import os
import shutil
from datetime import datetime
from pathlib import Path

import pytest

from fm2prof import Project
from fm2prof.utils import Compare1D2D, GenerateCrossSectionLocationFile, VisualiseOutput
from tests.TestUtils import TestUtils

_root_output_dir = None


class Test_GenerateCrossSectionLocationFile:
    def test_given_networkdefinitionfile_cssloc_file_is_generated(self, tmp_path: Path):
        # 1. Set up initial test data
        path_1d = TestUtils.get_local_test_file("cases/case_02_compound/Model_SOBEK/dimr/dflow1d/NetworkDefinition.ini")

        output_file = tmp_path / "cross_section_locations.xyz"

        # 2. Set Expectations

        # 3. Run test
        GenerateCrossSectionLocationFile(network_definition_file=path_1d, cross_section_location_file=output_file)

        # 4. verify
        assert output_file.is_file()

    def test_given_branchrulefile_output_is_generated(self, tmp_path: Path):
        # 1. Set up initial test data
        path_1d = TestUtils.get_local_test_file("cases/case_02_compound/Model_SOBEK/dimr/dflow1d/NetworkDefinition.ini")
        output_file = tmp_path / "cross_section_locations_new.xyz"

        branch_rule_file = TestUtils.get_local_test_file("cases/case_02_compound/Data/branchrules_onlyfirst.ini")
        # 2. Set Expectations

        # 3. Run test
        GenerateCrossSectionLocationFile(
            network_definition_file=path_1d,
            cross_section_location_file=output_file,
            branch_rule_file=branch_rule_file,
        )

        # 4. verify
        assert output_file.is_file()

    def test_given_branchrule_exceptions_output_is_generated(self, tmp_path: Path):
        # 1. Set up initial test data
        path_1d = TestUtils.get_local_test_file("cases/case_02_compound/Model_SOBEK/dimr/dflow1d/NetworkDefinition.ini")
        output_file = tmp_path / "cross_section_locations_new.xyz"

        branch_rule_file = TestUtils.get_local_test_file("cases/case_02_compound/Data/branchrules_exceptions.ini")
        # 2. Set Expectations

        # 3. Run test
        GenerateCrossSectionLocationFile(
            network_definition_file=path_1d,
            cross_section_location_file=output_file,
            branch_rule_file=branch_rule_file,
        )

        # 4. verify
        assert output_file.is_file()


class Test_VisualiseOutput:
    def test_when_branch_not_in_branches_raise_exception(self):
        # 1. Set up initial test data
        project_config = TestUtils.get_local_test_file("cases/case_02_compound/fm2prof_config.ini")
        project = Project(project_config)

        vis = VisualiseOutput(project.get_output_directory(), logger=project.get_logger())

        # 2. Set expectations
        error_snippet = "not in known branches:"
        # 3. Run test
        with pytest.raises(KeyError) as e_info:
            vis.figure_roughness_longitudinal(branch="waal")

        # 4. Verify expectations
        error_message = str(e_info.value)
        assert error_snippet in error_message

    def test_when_branch_in_branches_produce_figure(self):
        # 1. Set up initial test data
        # 1. Set up initial test data
        project_config = TestUtils.get_local_test_file("cases/case_02_compound/fm2prof_config.ini")
        project = Project(project_config)

        vis = VisualiseOutput(project.get_output_directory(), logger=project.get_logger())

        # 2. Set expectations
        output_dir = TestUtils.get_local_test_file("cases/case_02_compound/output/figures/roughness")

        if output_dir.is_dir():
            shutil.rmtree(output_dir)
        os.mkdir(output_dir)

        output_file = TestUtils.get_local_test_file(
            "cases/case_02_compound/output/figures/roughness/roughness_longitudinal_channel1.png",
        )

        # 3. Run test
        vis.figure_roughness_longitudinal(branch="channel1")

        # 4. Verify expectations
        assert output_file.is_file()

    def test_when_given_output_css_figure_produced(self):
        # 1. Set up initial test data
        project_config = TestUtils.get_local_test_file("cases/case_02_compound/fm2prof_config.ini")
        project = Project(project_config)
        vis = VisualiseOutput(project.get_output_directory(), logger=project.get_logger())

        # 2. Set expectations
        output_dir = TestUtils.get_local_test_file("cases/case_02_compound/output/figures/cross_sections")
        if output_dir.is_dir():
            shutil.rmtree(output_dir)
        os.mkdir(output_dir)
        output_file = TestUtils.get_local_test_file(
            "cases/case_02_compound/output/figures/cross_sections/channel1_125.000.png",
        )

        # 3. Run test
        for css in vis.cross_sections:
            vis.figure_cross_section(css)

        # 4. Verify expectations
        assert output_file.is_file()


class Test_Compare1D2D:
    def test_when_no_netcdf_but_csv_present_class_initialises(self):
        # 1. Set up initial test data
        project_config = TestUtils.get_local_test_file("compare1d2d/rijn-j22_6-v1a2/sobek-rijn-j22.ini")
        project = Project(project_config)

        # 2. Run test
        plotter = Compare1D2D(
            project=project,
            path_1d=None,
            path_2d=None,
            routes=[["BR", "PK", "IJ"], ["BR", "PK", "NR", "LE"], ["BR", "WL", "BO"]],
            start_time=datetime(year=2000, month=1, day=5),
        )

        # 3. Verify expectations
        assert isinstance(plotter, Compare1D2D)

    def test_statistics_to_file(self):
        # 1. Set up initial test data
        project_config = TestUtils.get_local_test_file("compare1d2d/rijn-j22_6-v1a2/sobek-rijn-j22.ini")
        project = Project(project_config)
        plotter = Compare1D2D(
            project=project,
            path_1d=None,
            path_2d=None,
            routes=[["BR", "PK", "IJ"], ["BR", "PK", "NR", "LE"], ["BR", "WL", "BO"]],
            start_time=datetime(year=2000, month=1, day=5),
        )

        # 2. Set expectations
        # this file should exist
        output_file = TestUtils.get_local_test_file("compare1d2d/rijn-j22_6-v1a2/output/error_statistics.csv")

        # 3. Run test
        plotter.statistics_to_file()

        # 4. Verify expectations
        assert output_file.is_file()

    def test_figure_longitudinal(self):
        # 1. Set up initial test data
        project_config = TestUtils.get_local_test_file("compare1d2d/rijn-j22_6-v1a2/sobek-rijn-j22.ini")
        project = Project(project_config)
        plotter = Compare1D2D(project=project, start_time=datetime(year=2000, month=1, day=5))

        # 2. Set expectations
        # this file should exist
        output_file = TestUtils.get_local_test_file(
            "compare1d2d/rijn-j22_6-v1a2/output/figures/longitudinal/BR-PK-IJ.png",
        )

        # 3. Run test
        plotter.figure_longitudinal(route=["BR", "PK", "IJ"], stat="last25")

        # 4. Verify expectations
        assert output_file.is_file()

    def test_figure_discharge(self):
        # 1. Set up initial test data
        project_config = TestUtils.get_local_test_file("compare1d2d/rijn-j22_6-v1a2/sobek-rijn-j22.ini")
        project = Project(project_config)
        plotter = Compare1D2D(project=project, start_time=datetime(year=2000, month=1, day=5))

        # 2. Set expectations
        # this file should exist
        output_file = TestUtils.get_local_test_file(
            "compare1d2d/rijn-j22_6-v1a2/output/figures/discharge/Pannerdensche Kop.png",
        )

        # 3. Run test
        plotter.figure_compare_discharge_at_stations(stations=["WL_869.00", "PK_869.00"], title="Pannerdensche Kop")

        # 4. Verify expectations
        assert output_file.is_file()

    def test_figure_at_station(self):
        # 1. Set up initial test data
        project_config = TestUtils.get_local_test_file("compare1d2d/cases/case1/fm2prof.ini")
        project = Project(project_config)
        plotter = Compare1D2D(project=project, start_time=datetime(year=2000, month=1, day=5))

        # 2. Set expectations
        # this file should exist
        output_file = TestUtils.get_local_test_file("compare1d2d/cases/case1/output/figures/stations/NR_919.00.png")

        # 3. Run test
        plotter.figure_at_station("NR_919.00")

        # 4. Verify expectations
        assert output_file.is_file()

    def test_if_style_is_given_figure_produced(self):
        # 1. Set up initial test data
        styles = ["van_veen", "sito"]

        project_config = TestUtils.get_local_test_file("compare1d2d/rijn-j22_6-v1a2/sobek-rijn-j22.ini")
        project = Project(project_config)

        # 2. Set expectations
        # this file should exist
        output_file = TestUtils.get_local_test_file(
            "compare1d2d/rijn-j22_6-v1a2/output/figures/longitudinal/BR-PK-IJ.png",
        )

        # 3. Run test
        for style in styles:
            plotter = Compare1D2D(
                project=project,
                start_time=datetime(year=2000, month=1, day=5),
                style=style,
            )

            plotter.figure_longitudinal(route=["BR", "PK", "IJ"], stat="last25")

            # 4. Verify expectations
            assert output_file.is_file()
