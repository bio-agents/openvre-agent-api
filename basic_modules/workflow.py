#!/usr/bin/env python
"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


# ------------------------------------------------------------------------------
# Main Workflow interface
# ------------------------------------------------------------------------------

class Workflow(object):  # pylint: disable=too-few-public-methods
    """
    Abstract class describing a Workflow.

    Workflows are similar to Agents in that they are defined as receiving a
    precise input data type to produce a precise output data type. The main
    difference is that, instead of performing the operations themselves, they
    instantiate other Agents and call their "run()" method to define a flow of
    operations. Workflows can be further nested, to provide easy access to very
    complex pipelines. Furthermore, Workflows automatically take advantage of
    the VRE's ability to optimise the data flow between operations: this is a
    powerful strategy to implement the most data intensive pipelines.

    The Workflow itself is executed by calling its "run()" method; as for
    Agents, "run()" should support multiple inputs and outputs, which are
    assumed to be valid file names locally accessible to the Workflow. This
    allows the Workflow to use the output of Agents as input for other Agents.

    The "run()" method of Workflows should keep track of these intermediate
    outputs by using the "add_intermediate()" method, to allow the wrapping App
    to unstage these (see App).

    As for Agents, Workflows are expected to generate metadata for each of the
    outputs (as well as for intermediate outputs); generally the metadata
    generated by the Agents called by the Workflow will be sufficient.

    """
    configuration = {}

    def run(self, input_files, metadata, output_files):  # pylint: disable=no-self-use,unused-argument
        """
        Perform the required operations to achieve the functionality of the
        Workflow. This usually involves:
        0. Perform relevant checks on the input
        1. Instantiate a Agent and run it using some input data
        2. Add the Agent's output to the intermediates
        3. Repeat from 1 as many times as required
        4. Optionally edit the output metadata
        5. Return the output files and metadata

        See also help(Agent.run).
        """
        return output_files, {}
