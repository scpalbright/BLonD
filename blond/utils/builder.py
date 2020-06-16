#General imports
import json
import numpy as np
import inspect
import warnings

#BLonD imports
import blond.input_parameters.ring as inputRing
import blond.input_parameters.ring_options as ringOpt
import blond.input_parameters.rf_parameters as inputRF
import blond.trackers.tracker as tracker
import blond.beam.beam as beam
import blond.beam.profile as prof
import blond.beam.distributions as distBeam
import blond.impedances.impedance_sources as impSource
import blond.impedances.impedance as imp
import blond.utils.exceptions as blExcept


class builder:

    def __init__(self, ring=None, RF=None, beam=None, profile=None,
                 cut_options=None, ring_options=None):

        print("ring", ring)
        print("RF", RF)
        print("beam", beam)
        print("profile", profile)
        print("cut_options", cut_options)
        print("ring_options", ring_options)


availableObjects= {
                  'ring': inputRing.Ring,
                  'RF': inputRF.RFStation,
                  'ring_options': ringOpt.RingOptions,
                  'beam': beam.Beam,
                  'profile': prof.Profile,
                  'cut_options': prof.CutOptions
                   }


def load_dict(inputDict):

    if not all([key in availableObjects for key in inputDict]):
        raise blExcept.BuildingError("Attempted to create unrecognised "
                                     +"objects.  The available objects "
                             + f"are {list(availableObjects.keys())}")

    objects = {key: _object_from_dict(inputDict.pop(key),
                      availableObjects[key]) for key in inputDict}

    return builder(**objects)


def load_JSON( file):

    with open(file, 'r') as file:
        inputDict = json.load(file)
    
    return load_dict(inputDict)


def _check_ring(inputDict):

    particleDict = {'Proton': beam.Proton,
                    'Electron': beam.Electron,
                    'Positron': beam.Positron}
    
    if isinstance(inputDict['Particle'], str):
        if inputDict['Particle'] in particleDict:
            inputDict['Particle'] = particleDict[inputDict['Particle']]()

    elif hasattr(inputDict['Particle'], '__iter__'):
        if isinstance(inputDict['Particle'], dict):
            particle = beam.Particle(**inputDict['Particle'])
            if isinstance(particle, tuple):
                raise blExcept.ObjectCreationError("Attempted to create the"
                        +f" Particle object from {inputDict['Particle']} but "
                        +"dict input requires keywords {particle[0]} only.")


def _check_npy(inputDict, objName):

    for k in inputDict:
        if isinstance(inputDict[k], str):
            if str[-4:] == '.npy':
                try:
                    inputDict[k] = np.load(inputDict[k])
                except FileNotFoundError:
                    raise FileNotFoundError(f"Attempted to load parameter {k}"
                                            + "for object " + objName + "as a"
                                            + f".npy file from {inputDict[k]}"
                                            + " but the file was not found.")


def _object_from_dict(inputDict, obj, returnRequired = False):

    arguments = inspect.signature(obj).parameters.items()

    requiredArgs = [k for k, v in arguments if v.default is
                                                inspect.Parameter.empty]

    if not all([k in inputDict for k in requiredArgs]):
        undefined = [k for k in requiredArgs if k not in inputDict]
        if returnRequired:
            return requiredArgs, undefined
        else:
            raise blExcept.ObjectCreationError(f"Creating {obj.__name__} "
                                               +"requires the following "
                                               +"parameters to be "
                                               +f"defined: {requiredArgs}, but"
                                               +f" {undefined} were not found")

    required = {k: inputDict.pop(k) for k, v in arguments if v.default is
                                                inspect.Parameter.empty}

    optional = {k: inputDict.pop(k, v.default) for k, v in arguments if
                                v.default is not inspect.Parameter.empty}

    if inputDict:
        warnings.Warn("Unrecognised members will be passed as kwargs.  "
                      + "The unknown arguments are: "
                      + f"{list(inputDict.keys())}")

    return obj(**required, **optional, **inputDict)


if __name__ == '__main__':
    
    # with open('../../devel/testFile.json', 'r') as file:
    #     test = json.load(file)

    # for t in test:
    #     print(test[t])
    load_JSON('../../devel/testFile.json')