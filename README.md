# Open source trace fear conditioning apparatus for rodents

## Project Description

The ability to form declarative memories declines with normal aging, as well as with aging-associated cognitive and emotional disorders. Diminished temporal binding capacity, which normally allows for the association of non-overlapping stimuli and events in an experience, is a core process underlying such impairment with aging. This project will identify aging-associated alterations in brain activity functions supporting temporal binding capacity, with the long-term aim of identifying potential targets to slow or alleviate cognitive and emotional impairments in aging and aging-associated neuropsychiatric disorders.

The temporal binding of emotionally salient stimuli and events has long been studied experimentally using trace fear conditioning (tFC). Here, subjects learn to associate a neutral auditory cue (conditioned stimulus, CS) with an aversive unconditioned stimulus (US), despite their separation by a stimulus-free gap of tens of seconds. The ability to form associations across delays on this timescale during tFC is severely diminished with aging. Current models propose that either 'time cell' activity in the hippocampal CA1 area bridges the delay (1), or sparse ensembles of neurons emerge during learning to intermittently encode CS-information for temporal binding (2). However, the neural mechanisms underlying the age-related decline in temporal binding capacity remain unknown, giving rise to fundamental questions. What functional changes in neural activity occur with aging in the particular CA1 circuitry that encodes emotionally salient stimuli for temporal binding? What changes occur with aging in neural processes for consolidation of this information?

To address these questions we have developed a trace fear conditioning apparatus tailored for headfixed rodents. This rig has been engeineered to be both modular and flexible, allowing for easy customization and expansion. The rig is controlled by Arduino microcontrollers equipeed with sensors. The conditioning is done by airpuffs directed toward the snout of the animals. Multiple Arduinos can be used in a daisy-chain manner which allows for paralel data collection of multiple mice. The rigs can also be equipped with video cameras (currently sourced from [White Matter Inc.](https://white-matter.com/products/e3Vision)) to record the mice's facial expression throughout the training sessions. The data collection is controlled by a Python script that interfaces with the hardware via serial communication. The raw data is saved in JSON fromat.

## Repository Structure

The repository is organized as follows:

- The `Components` folder contains all the hardware designs for the rig. These include 3D printable parts, laser cuttable parts, and electronics schematics.
- the `Software` folder contains the Arduino code for the microcontrollers and the Python code for the data collection and analysis.
- the `Analysis` folder contains the code for the analysis of the data collected by the rig.

## Installation and Usage

### Arduino

The Arduino code is written in C++ and can be compiled and uploaded to the microcontrollers using the Arduino IDE. Details of the code are provided in the `README.md` file under the `Software/Rig` folder.

### Analysis source code

See the `README.md` file under the `Software/Analysis` folder for details on how to use the analysis pipeline.

## Local Development

Most of the analysis routies were optimized for running in Google Colaboratory notebooks. However the package can be installed for local development. To create it please download the latest Anaconda distribution. Then clone the repositioy and run the following commands as shown below:

```bash
cd tFC-rig
```

```bash
conda env create -f environment.yml
```

```bash
conda activate cued-fc
```

```bash
cd Analysis
```

```bash
pip install -e .
```

wich will install the custom analysis package in editable mode.

## References

1. Sellami A, Al Abed AS, Brayda-Bruno L, Etchamendy N, Valerio S, Oule M, Pantaleon L, Lamothe V,
Potier M, Bernard K, Jabourian M, Herry C, Mons N, Piazza PV, Eichenbaum H, Marighetto A. Temporal
binding function of dorsal CA1 is critical for declarative memory formation. [Proc Natl Acad Sci U S A.](https://www.pnas.org/doi/10.1073/pnas.1619657114)
2017;114(38):10262-7. doi: 10.1073/pnas.1619657114. PubMed PMID: 28874586; PMCID: PMC5617244.
2. Ahmed MS, Priestley JB, Castro A, Stefanini F, Canales ASS, Balough EM, Lavoie E, Mazzucato L, Fusi
S, Losonczy A. Hippocampal Network Reorganization Underlies the Formation of a Temporal Association
Memory. [Neuron.](https://pubmed.ncbi.nlm.nih.gov/32392472/) 2020;107(2):283-+. doi: 10.1016/j.neuron.2020.04.013. PubMed PMID:
WOS:000551381900002.
