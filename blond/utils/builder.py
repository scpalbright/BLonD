#General imports
import json
import numpy as np
import inspect
import warnings
import sys

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

        if ring is not None:
            _check_ring(ring)
        self.ringDict = ring

        if RF is not None:
            _check_rf(RF)
        self.RFDict = RF
        self.beamDict = beam
        self.profileDict = profile
        self.cut_optionsDict = cut_options
        self.ring_optionsDict = ring_options

        self.make_simulation()


    def _make_ring(self):
        self.ring = _object_from_dict(self.ringDict, inputRing.Ring)


    def _make_RF(self):

        rfkwargs = {**self.RFDict}

        print(rfkwargs)

        try:
            self.RF = _object_from_dict({**rfkwargs, 'Ring': self.ring},
                                         inputRF.RFStation)
        except AttributeError:
            raise AttributeError("Cannot make RF object with ring object.")


    def _make_beam(self):
        self.beam = _object_from_dict(self.beamDict, beam.Beam)


    def _make_profile(self):
        self.profile = _object_from_dict(self.profileDict, prof.Profile)

    def _make_ring_options(self):
        self.ring_options = _object_from_dict(self.ring_optionsDict,
                                              ringOpt.RingOptions)


    def _make_cut_options(self):
        self.cut_options = _object_from_dict(self.cut_optionsDict,
                                             prof.CutOptions)


    def _make_tracker(self):
        self.long_tracker = tracker.RingAndRFTracker(self.RF, self.beam)


    def _make_full_ring(self):
        self.full_ring = tracker.FullRingAndRF([self.long_tracker])


    def make_simulation(self):

        try:
            self._make_ring_options()
        except AttributeError:
            self.ring_options = ringOpt.RingOptions()
        self.ringDict['RingOptions'] = self.ring_options
        self._make_ring()

        self._make_RF()

        try:
            self._make_cut_options()
        except AttributeError:
            self.cut_options = prof.CutOptions()
        self.profileDict['CutOptions'] = self.cut_options

        self._make_beam()
        self._make_profile()
        self._make_tracker()
        self._make_full_ring()


def load_dict(inputDict):
    return _object_from_dict(inputDict, builder)


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
            try:
                inputDict['Particle'] = particleDict[inputDict['Particle']]()
            except KeyError:
                pass

    elif hasattr(inputDict['Particle'], '__iter__'):
        if isinstance(inputDict['Particle'], dict):
            particle = _object_from_dict(inputDict['Particle'], beam.Particle,
                                                                         True)
            if isinstance(particle, tuple):
                raise blExcept.ObjectCreationError("Attempted to create the"
                        +f" Particle object from {inputDict['Particle']} but "
                        +"dict input requires keywords {particle[0]} only.")
        else:
            try:
                particle = beam.Particle(*inputDict['Particle'])
            except TypeError:
                raise blExcept.ObjectCreationError("Attempted to create the "
                           +f"Particle object from {inputDict['Particle']} but"
                           +f" the input was invalid.  Two elements are "
                           +"required, interpreted as [mass, charge].")

            inputDict['Particle'] = particle

    _check_npy(inputDict, 'ring')

    if isinstance(inputDict['synchronous_data'], np.ndarray):
        if inputDict['synchronous_data'].shape[0] == 2:
            inputDict['synchronous_data'] = (inputDict['synchronous_data'][0],
                                             inputDict['synchronous_data'][1])


def _check_rf(inputDict):
    _check_npy(inputDict, 'RFStation')
    _check_npy(inputDict['voltage'], 'voltage')
    for k in inputDict['voltage']:
        if hasattr(inputDict['voltage'][k], '__iter__'):
            inputDict['voltage'][k] = np.array(inputDict['voltage'][k])
            if inputDict['voltage'][k].shape[0] == 2:
                inputDict['voltage'][k] = [inputDict['voltage'][k][0],
                                           inputDict['voltage'][k][1]]
    _check_npy(inputDict['phi_rf_d'], 'phi_rf_d')
    for k in inputDict['phi_rf_d']:
        if hasattr(inputDict['phi_rf_d'][k], '__iter__'):
            inputDict['phi_rf_d'][k] = np.array(inputDict['phi_rf_d'][k])
            if inputDict['phi_rf_d'][k].shape[0] == 2:
                inputDict['phi_rf_d'][k] = [inputDict['phi_rf_d'][k][0],
                                            inputDict['phi_rf_d'][k][1]]

    voltage = []
    for h in inputDict['harmonic']:
        voltage.append(inputDict['voltage'][str(h)])
    if any(hasattr(v, '__iter__') for v in voltage):
        shapes = [len(v) for v in voltage if hasattr(v, '__iter__')]
        if len(shapes) != len(voltage):
            raise RuntimeError("Cannot mix single and multi-valued input"
                               + " for voltage.")
        elif not all(s == shapes[0] for s in shapes):
            raise RuntimeError("trying to combine turn and time based input")

        inputDict['voltage'] = tuple(voltage)
    else:
        inputDict['voltage'] = voltage

    phase = []
    for h in inputDict['phi_rf_d']:
        phase.append(inputDict['phi_rf_d'][str(h)])
    if any(hasattr(p, '__iter__') for p in phase):
        shapes = [len(v) for v in phase if hasattr(v, '__iter__')]
        if len(shapes) != len(phase):
            raise RuntimeError("Cannot mix single and multi-valued input"
                               + " for phase.")
        elif not all(s == shapes[0] for s in shapes):
            raise RuntimeError("trying to combine turn and time based input")

        inputDict['phi_rf_d'] = tuple(phase)
    else:
        inputDict['phi_rf_d'] = phase


def _check_npy(inputDict, objName):

    for k in inputDict:
        if isinstance(inputDict[k], str):
            if inputDict[k][-4:] == '.npy':
                try:
                    inputDict[k] = np.load(inputDict[k])
                except FileNotFoundError:
                    raise FileNotFoundError(f"Attempted to load parameter '{k}'"
                                            + " for '" + objName + "' as a "
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
        warnings.warn("Unrecognised members will be passed as kwargs.  "
                      + "The unknown arguments are: "
                      + f"{list(inputDict.keys())}")

    try:
        retObj = obj(**required, **optional, **inputDict)
    except TypeError as e:
        raise blExcept.ObjectCreationError(f"Attempting to create "
                                           +f"{obj.__name__} when a TypeError "
                                           +"was raised with message"
                                           + f" {e.args[0]}") from e
    else:
        return retObj


if __name__ == '__main__':
    
    # with open('../../devel/testFile.json', 'r') as file:
    #     test = json.load(file)

    # for t in test:
    #     print(test[t])
    load_JSON('../../devel/testFile.json')