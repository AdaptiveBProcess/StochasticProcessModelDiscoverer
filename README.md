# StochasticProcessModelDiscoverer

This tool is able to extract a stochastic process model via DDS techniques. This code can perform the next tasks:


* Extract a stochastic process model using an event log as input.
* Generate sequences of activities and roles using the stochastic process model.
* Assess the similarity between the original sequences and the generated ones.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

## Requirements
Tested with Python 3.8. Install the necessary packages with
```bash
pip install -r requirements.txt
```
## Getting Started

To install the CLI-tool and the library version from the root directory run:

```shell
$ pip install -e .
```
### CLI tool mode execution
Invoke the CLI tool with either of these:

Once created the environment, you can execute the tool from a terminal specifying the input event log name and any of the following parameters:

**Discovery:**
 
* `--file (required)`: event log in XES format.
* `--evaluate/--no-evaluate (optional, default=True)`: Refers to whether or not you want to perform a final assessment of the accuracy of the final simulation model.
* `--mining_alg (optional, default='sm1')`: version of SplitMiner to use. Available options: 'sm1', 'sm2', 'sm3'.
* `--s_gen_max_eval (optional, default='30')`: Number of trials used by the optimizer in the discovery face.
* `--exp_reps (optional, default='5')`: number of repetition per trial.

**Example of execution:**

```shell
$ sp_model_discoverer discover --file ..\data\Production.xes --exp_reps 10
```
**Generation:**

* `--generative_model (required)` - Stochastic process model (BPMN model enhanced with parameters)
* `--evaluate/--no-evaluate (optional, default=True)`: Refers to whether or not you want to perform a final assessment of the accuracy of the final simulation model.
* `--num_inst` - Number of case instances desired on each execution.
* `--exp_reps (optional, default='5')`: number of repetition per execution.

**Example of execution:**

```shell
$ sp_model_discoverer generate --generative_model ..\data\Production.bpmn --exp_reps 10
```
