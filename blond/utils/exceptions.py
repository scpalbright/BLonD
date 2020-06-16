#==============
#Base Exception
#==============

class BLonDException(Exception):
    pass


#===============
#Beam Exceptions
#===============

class MassError(BLonDException):
    pass

class AllParticlesLost(BLonDException):
    pass

class ParticleAdditionError(BLonDException):
    pass


#==================================
#Distribution Generation Exceptions
#==================================

class DistributionError(BLonDException):
    pass

class GenerationError(BLonDException):
    pass


#==================
#Profile Exceptions
#==================

class CutError(BLonDException):
    pass

class ProfileDerivativeError(BLonDException):
    pass


#====================
#Impedance Exceptions
#====================

class WakeLengthError(BLonDException):
    pass

class FrequencyResolutionError(BLonDException):
    pass

class ResonatorError(BLonDException):
    pass

class WrongCalcError(BLonDException):
    pass

class MissingParameterError(BLonDException):
    pass


#===========================
#Input Parameters Exceptions
#===========================

class MomentumError(BLonDException):
    pass


#===============
#LLRF Exceptions
#===============

class PhaseLoopError(BLonDException):
    pass

class PhaseNoiseError(BLonDException):
    pass

class FeedbackError(BLonDException):
    pass

class ImpulseError(BLonDException):
    pass


#==================
#Toolbox Exceptions
#==================

class PhaseSpaceError(BLonDException):
    pass

class NoiseDiffusionError(BLonDException):
    pass


#==================
#Tracker Exceptions
#==================

class PotentialWellError(BLonDException):
    pass

class SolverError(BLonDException):
    pass

class PeriodicityError(BLonDException):
    pass

class ProfileError(BLonDException):
    pass

class SynchrotronMotionError(BLonDException):
    pass


#===============
#Util Exceptions
#===============

class ConvolutionError(BLonDException):
    pass

class IntegrationError(BLonDException):
    pass

class SortError(BLonDException):
    pass

class ObjectCreationError(BLonDException):
    pass



#=================
#Global Exceptions
#=================
    
class InterpolationError(BLonDException):
    pass

class InputDataError(BLonDException):
    pass