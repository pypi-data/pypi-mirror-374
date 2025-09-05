from fm2prof import Project
from fm2prof.utils import VisualiseOutput

# # Run if there is no configuration file available yet
# inifile = IniFile().print_configuration()
# ini_path = f"fm2prof_Test_v23.ini"
#
# with open(ini_path, "w") as f:
#     f.write(inifile)

# Run FM2Prof
# load project
#project = Project(r"p:/11211534-002-25mad09-maas/C_Work/486_sobek-maas-j25_6-v1a1/643_Derive_CSS/2_fm2prof/sobek-maas-j25.ini")
project = Project(r"c:\Users\berend_kn\fm2prof_maas_test\2_fm2prof\sobek-maas-j25.ini")

# overwrite = True overwrites any existing output
project.run(overwrite=True)

# to visualize cross-section output:
"""
vis = VisualiseOutput(
            project.get_output_directory(),
            logger=project.get_logger()
        )

for css in vis.cross_sections:
    vis.figure_cross_section(css)
"""
