# openvre-agent-api

## Introduction
This library implements the specifications of a new agent in the 
[openVRE](https://github.com/inab/openVRE.git) enviroment.
It provides a simple programming paradigm to develop agents for the VRE.

The main goals that this proposal aims to achieve are:

1. Achieve horizontal interoperability by defining a "Agent" as a specific
functionality with precise inputs and outputs, which must both comply with the
Data Management Plan (DMP). Agents are implemented as a thin wrappers over
existing software, in order to facilitate integrating existing agents in the
VRE.

2. Achieve vertical interoperability by using PyCOMPSs, and allowing
developers to specify the execution enviroment requirements for each agent by
using PyCOMPSs "constraints" decorator. Although written with task-based
programming in mind, this library allows execution of Agents outside of the
COMPSs runtime.

3. Simplify the construction of workflows, by conceiving agents such that it is
straightforward to combine them in Workflows; in particular by using PyCOMPSs
"task" decorator and the PyCOMPSs runtime as the workflow scheduler.

## Implementation overview
The 'basic_modules' contains the basic entities of openvre-agent-api:
1. Agent:
	Is the top-level wrapper for agents within the VRE; each agent is defined
	by its input and output formats, and by its specific requirements on the
	execution environment. Agents should implement a "run" method, that defines
	operations needed to get from input to output. The "run" method calls other
	methods which are decorated using PyCOMPSs "@task" and "@constraints",
	allowing agent developers to define the workflow and execution environment.
    See also Workflow.
2. App:
	Is the main entry point to the agents layer of the VRE; it deals with heterogeneity
	in the way Agents are run, in terms of filesystem access, runtime environment,
	error reporting, and more. Therefore, Apps are compatible with all Agents.
	Apps implement a "launch" method, which prepares and runs a single instance of Agent.
	The "apps" module provides some example Apps for straightforward cases:

	- *LocalApp*: assumes files to be locally accessible;

	- *PyCOMPSsApp*: specific for Agents using PyCOMPSs;

	- *WorkflowApp*: inherits from both of the above, and implements the ability
	  to run Workflows.

	- *JSONApp*: inherits from WorkflowApp, and implements the ability to read
	  run configuration from JSON files, and write results in a JSON file; JSON
      formats used are those provided, and accepted, by the VRE.

3. Metadata:
   Class that contains extra information about files.

The 'utils' module contains useful functions for performing common tasks in Agent
execution. In particular it contains 'logger', the logging facility of openvre-agent-api;
it provides a unified way of sending messages to the VRE.

See the documentation for the classes for more information.

## Installation

Directly from GitHub:

```bash
pip install git+https://github.com/inab/openvre-agent-api.git
```

## Examples

The repository [vre_sample_agent](https://github.com/inab/vre_sample_agent.git) showcase 
the functionalities of this wrapper by implementing a simple application. 
It consists on a CWL agent execution.

