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
import json
import iteragents
import os

from apps.workflowapp import WorkflowApp
from basic_modules.metadata import Metadata
from utils import logger
from collections import defaultdict
from typing import (
    MutableMapping,
    MutableSequence,
    NamedTuple,
    Optional,
)

# -----------------------------------------------------------------------------
# JSON-configured App
# -----------------------------------------------------------------------------

# Order DOES MATTER for backward compatibility!!!!
class InputMeta(NamedTuple):
    input_type: str
    meta: Metadata

class JSONApp(WorkflowApp):  # pylint: disable=too-few-public-methods
    """
    JSON-configured App.

    Redefines launch to the following signature (see launch for details)

    launch(agent_class, config_path, input_metadata_path, output_metadata_path)

    """

    # The arguments deffer between this function and the supeclass in
    # basic_modules.app to provide a common interface and so that the JSON
    # configuration files can be provided to generate the parameters required
    # by App.
    def launch(self, agent_class,  # pylint: disable=too-many-locals,arguments-differ
               config_path, input_metadata_path, output_metadata_path):
        """
        Run a Agent with the specified inputs and configuration.


        Parameters
        ----------
        agent_class : class
            the subclass of Agent to be run;
        config_path : str
            path to a valid JSON file containing information on how the agent
            should be executed. The schema for this JSON string is the
            "config.json".
        input_metadata_path : str
            path to a valid JSON file containing information on agent inputs.
            The schema for this JSON string is the "input_metadata.json".
        output_metadata_path : str
            path to write the JSON file containing information on agent outputs.
            The schema for this JSON string is the "output_metadata.json".


        Returns
        -------
        bool


        Example
        -------
        >>> import App, Agent
        >>> app = JSONApp()
        >>> # expects to find valid config.json and input_metadata.json
        >>> app.launch(
        ...     Agent, "/path/to/config.json",
        ...     "/path/to/input_metadata.json", "/path/to/results.json")
        >>> # writes /path/to/results.json
        """

        logger.info("0) Unpack information from JSON")
        input_ids, arguments, output_files, output_metadata = self._read_config(
            config_path)
        
        input_metadata: MutableMapping[str, Union[InputMeta, MutableSequence[InputMeta]]]
        input_metadata_ids, input_metadata = self._read_metadata(
            input_metadata_path)

        # input files arrange by role
        input_files_tmp = {}
        for role, input_id in input_ids.items():
            if isinstance(input_id, (list, tuple)):
                input_files_tmp[role] = [input_metadata_ids[el] for el in input_id]
            else:
                input_files_tmp[role] = input_metadata_ids[input_id]

        # input metadata arrange by role
        for role, input_id_l in input_ids.items():
            convert_back = not isinstance(input_id_l, list)
            if convert_back:
                input_id_l = [ input_id_l ]

            input_meta_l: MutableSequence[InputMeta] = []
            for input_id in input_id_l:
                if input_id in input_metadata:
                    input_meta_l.append(input_metadata.pop(input_id))
            if len(input_meta_l) > 0:
                input_metadata[role] = input_meta_l[0]  if convert_back  else  input_meta_l
        #    for key in list(input_metadata.keys()):
        #        if key == input_id:
        #            input_metadata[role] = input_metadata.pop(key)

        # get paths from IDs
        input_files = {}
        for role, metadata in input_files_tmp.items():
            if isinstance(metadata, (list, tuple)):
                input_files[role] = [el.file_path for el in metadata]
            else:
                input_files[role] = metadata.file_path

        # Run launch from the superclass
        output_files, output_metadata = super(JSONApp, self).launch(
            agent_class, input_files, input_metadata,
            output_files, arguments, output_metadata)

        logger.info("4) Pack information to JSON")
        return self._write_results(
            input_files, input_metadata,
            output_files, output_metadata,
            output_metadata_path)

    @staticmethod
    def _read_config(json_path):  # pylint: disable=no-self-use
        """
        Read config.json to obtain:

            - input_ids: dict containing IDs of agent input files
            - arguments: dict containing agent arguments
            - output_files: dict containing absolute paths of agent outputs
            - output_metadata: dict containing metadata of agent outputs

        Note that values of input_ids may be either str or list,
        according to whether "allow_multiple" is True for the role;
        in which case, the VRE will have accepted multiple input files
        for that role.

        For output files with "allow_multiple" True nothing changes
        here: it is up to the Agent developer to handle this.

        For more information see the schema for config.json.
        """
        configuration = json.load(open(json_path))
        input_ids = {}
        for input_config_id in configuration["input_files"]:
            role = input_config_id["name"]
            input_id = input_config_id["value"]
            allow_multiple = input_config_id["allow_multiple"]
            if role not in input_ids:
                if allow_multiple:  # allow multiple input files is True
                    input_ids[role] = [input_id]

                else:  # allow multiple input files is False
                    input_ids[role] = input_id

            else:
                # if not isinstance(input_ids[role], list):
                #     input_ids[role] = [input_ids[role]]
                input_ids[role].append(input_id)

        output_configuration = configuration["output_files"]
        output_metadata = output_configuration

        output_files = {}
        # TODO delete in the future
        for output_file in output_configuration:
            file_path = output_file["file"].get("file_path", None)
            output_files[output_file["name"]] = file_path
            #if file_path is not None:  # exists file path
            #    output_files[output_file["name"]] = file_path
            #else:  # not exists file path
            #    output_files[output_file["name"]] = None

        arguments = {}
        for argument in configuration["arguments"]:
            arguments[argument["name"]] = argument["value"]

        return input_ids, arguments, output_files, output_metadata

    @staticmethod
    def _read_metadata(json_path):  # pylint: disable=no-self-use
        """
        Read input_metadata.json to obtain input_metadata_ids, a dict
        containing metadata on each of the agent input files,
        arranged by their ID.

        For more information see the schema for input_metadata.json.
        """
        metadata = json.load(open(json_path))
        input_metadata_ids = {}
        input_metadata = {}
        for input_file in metadata:
            input_id = input_file["_id"]
            input_type = input_file.get("type", "file")
            meta = Metadata(
                type=input_type,
                data_type=input_file["data_type"],
                file_type=input_file["file_type"],
                file_path=input_file["file_path"],
                meta_data=input_file["meta_data"],
                compressed=input_file.get("compressed"),
                sources=input_file["sources"]
            )
            input_metadata_ids[input_id] = meta
            input_metadata[input_id] = InputMeta(input_type=input_type, meta=meta)

        return input_metadata_ids, input_metadata

    @staticmethod
    def _write_results(  # pylint: disable=no-self-use,too-many-arguments
            input_files, input_metadata,  # pylint: disable=unused-argument
            output_files, output_metadata, json_path):
        """
        Write results.json using information from input_files and output_files:

            - input_files: dict containing absolute paths of input files
            - input_metadata: dict containing metadata on input files
            - output_files: dict containing absolute paths of output files
            - output_metadata: dict containing metadata on output files

        Note that values of output_files may be either str or list,
        according to whether "allow_multiple" is True for the role;
        in which case, the Agent may have generated multiple output
        files for that role.

        Values of output_metadata for roles for which "allow_multiple"
        is True can be either a list of instances of Metadata, or a
        single instance. In the former case, the list is assumed to be
        the same length as that in output_files. In the latter, the same
        instance of Metadata is used for all outputs for that role.

        For more information see the schema for results.json.
        """
        results = []

        def _newresult(role, path, metadata):

            result = {
                "name": role,
                "type": path[1],
                "file_path": path[0],
                "data_type": metadata.data_type,
                "file_type": metadata.file_type,
                "compressed": metadata.compressed,
                "sources": metadata.sources,
                "meta_data": metadata.meta_data
            }
            if result["compressed"] is None:
                del result["compressed"]
            if result["sources"] is None:
                del result["sources"]

            return result
        
        if isinstance(output_metadata, dict):
            # Old school
            for role, path in output_files.items():
                metadata = output_metadata[role]
                if isinstance(path, (list, tuple)):  # check allow_multiple?
                    assert (isinstance(metadata, (list, tuple)) and len(metadata) == len(path)) \
                           or isinstance(metadata, Metadata), """Wrong number of metadata entries for role {role}: either 
                           1 or {np}, not {nm}""".format(role=role, np=len(path), nm=len(metadata))

                    if not isinstance(metadata, (list, tuple)):
                        metadata = [metadata] * len(path)

                    results.extend([_newresult(role, (pa, md.type), md) for pa, md in zip(path, metadata)])

                else:
                    results.append(
                        _newresult(role, (path, metadata.type), metadata))
        elif isinstance(output_metadata, list):
            for role, path in (iteragents.chain.from_iterable(
                    [iteragents.product((k,), v) for k, v in output_files.items() if v is not None])):

                for metadata in output_metadata:
                    if isinstance(metadata, dict):
                        name = metadata["name"]
                    elif isinstance(metadata, (list, tuple)):
                        # Assuming name and 
                        name = metadata[0]
                        metadata = metadata[1]
                    if name == role:
                        if isinstance(metadata, Metadata):
                            meta = metadata
                        else:
                            meta = Metadata()
                            meta.type = path[1]  # Set type
                            meta.file_path = path[0]  # Set file_path

                            # Set data_type and file_type
                            meta.data_type = metadata["file"].get("data_type", None)
                            meta.file_type = metadata["file"].get("file_type", None)

                            # Set compressed
                            meta.compressed = metadata["file"].get("compressed", None)

                            # Set input sources
                            if meta.data_type == "provenance_data":  # execution provenance
                                meta.sources = list()   # FIXME: this is for RO-Crate hack

                            else:
                                # Set input sources
                                meta_sources_list = list()
                                for input_name, input_val in input_metadata.items():
                                    if isinstance(input_val, InputMeta):
                                        meta_sources_list.append(input_val.meta.file_path)
                                    elif isinstance(input_val, list):
                                        meta_sources_list.extend(map(lambda i_v: i_v.meta.file_path, input_val))
                                    else:
                                        raise Exception("This exception should NEVER happen!!!!")

                                meta.sources = meta_sources_list

                            # Set metadata
                            meta.meta_data = metadata["file"].get("meta_data", None)
                        
                        results.append(_newresult(role, path, meta))
        else:
            # logger should complain A LOT HERE
            return False

        # Create JSON output_metadata file
        with open(json_path, mode='w', encoding='utf-8') as jH:
            json.dump({"output_files": results}, jH, indent=2, separators=(',', ': '))
        
        return os.path.isfile(json_path)
        #if os.path.isfile(json_path):  # check if results was created, if not execution stops
        #    return True
        #else:
        #    return False
