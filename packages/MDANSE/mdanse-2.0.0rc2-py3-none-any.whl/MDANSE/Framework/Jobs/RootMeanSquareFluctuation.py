#    This file is part of MDANSE.
#
#    MDANSE is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
from __future__ import annotations

import collections

from MDANSE.Framework.Jobs.IJob import IJob
from MDANSE.MolecularDynamics.Analysis import mean_square_fluctuation


class RootMeanSquareFluctuation(IJob):
    """Calculates the Root Mean Square Fluctuation of atom positions.

    The root mean square fluctuation (RMSF) for a set of atoms is similar to the
    square root of the mean square displacement (MSD), except that it is spatially
    resolved (by atom/residue/etc) rather than time resolved. It reveals the
    dynamical heterogeneity of the molecule over the course of a MD simulation.

    As opposed to most analysis types, the result is a single number per atom index.
    """

    label = "Root Mean Square Fluctuation"

    category = (
        "Analysis",
        "Dynamics",
    )

    ancestor = ["hdf_trajectory", "molecular_viewer"]

    settings = collections.OrderedDict()
    settings["trajectory"] = ("HDFTrajectoryConfigurator", {})
    settings["frames"] = (
        "FramesConfigurator",
        {"dependencies": {"trajectory": "trajectory"}},
    )
    settings["grouping_level"] = (
        "GroupingLevelConfigurator",
        {
            "choices": ["each atom", "each molecule"],
            "default": "each atom",
            "dependencies": {
                "trajectory": "trajectory",
            },
        },
    )
    settings["atom_selection"] = (
        "AtomSelectionConfigurator",
        {"dependencies": {"trajectory": "trajectory"}},
    )
    settings["output_files"] = ("OutputFilesConfigurator", {})
    settings["running_mode"] = ("RunningModeConfigurator", {})

    def initialize(self):
        """
        Initialize the input parameters and analysis self variables
        """
        super().initialize()

        self.group_molecules = (
            self.configuration["grouping_level"]["value"] != "each atom"
        )

        # Will store the indices.
        if not self.group_molecules:
            self._outputData.add(
                "rmsf/axes/indices",
                "LineOutputVariable",
                self.trajectory.atom_indices,
            )
            self.numberOfSteps = len(self.trajectory.atom_indices)
        else:
            self._outputData.add(
                "rmsf/axes/indices",
                "LineOutputVariable",
                list(range(len(self.trajectory.group_lookup))),
            )
            self.numberOfSteps = len(self.trajectory.group_lookup)
            self.cluster_lookup = list(self.trajectory.group_lookup.values())

        # Will store the mean square fluctuation evolution.
        self._outputData.add(
            "rmsf/rmsf",
            "LineOutputVariable",
            (self.numberOfSteps,),
            axis="rmsf/axes/indices",
            units="nm",
            main_result=True,
        )

        self._atoms = self.trajectory.atom_names

    def run_step(self, index):
        """
        Runs a single step of the job.\n

        :Parameters:
            #. index (int): The index of the step.
        :Returns:
            #. index (int): The index of the step.
            #. rmsf (np.array): the calculated root mean square fluctuation for atom index
        """
        # read the particle trajectory
        if not self.group_molecules:
            atom_index = self.trajectory.atom_indices[index]

            series = self.trajectory.read_atomic_trajectory(
                atom_index,
                first=self.configuration["frames"]["first"],
                last=self.configuration["frames"]["last"] + 1,
                step=self.configuration["frames"]["step"],
            )
        else:
            cluster_indices = self.cluster_lookup[index]

            series = self.trajectory.read_com_trajectory(
                cluster_indices,
                first=self.configuration["frames"]["first"],
                last=self.configuration["frames"]["last"] + 1,
                step=self.configuration["frames"]["step"],
            )

        rmsf = mean_square_fluctuation(series, root=True)

        return index, rmsf

    def combine(self, index, x):
        """
        Combines returned results of run_step.\n
        :Parameters:
            #. index (int): The index of the step.\n
            #. x (any): The returned result(s) of run_step
        """

        self._outputData["rmsf/rmsf"][index] = x

    def finalize(self):
        """
        Finalizes the calculations (e.g. averaging the total term, output files creations ...).
        """

        # Write the output variables.
        self._outputData.write(
            self.configuration["output_files"]["root"],
            self.configuration["output_files"]["formats"],
            str(self),
            self,
        )

        self.trajectory.close()
        super().finalize()
