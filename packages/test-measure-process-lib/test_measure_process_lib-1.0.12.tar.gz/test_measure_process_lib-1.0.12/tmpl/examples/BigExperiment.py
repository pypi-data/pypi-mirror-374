"""
Module: BigExperiment
================================================================
<Description of module>

SetupCondition classes:
* Temperature :
* Humidity :
* Pressure :

Measurement classes:
* VoltageSweep :
* CurrentSweep :
* PostProcess :

TestManager classes:
* Calibrate :
* MainMeasure :



This module is based on the "Test, Measure, Process Library" (TMPL)
framework for organising measurement code.
See: https://pypi.org/project/test-measure-process-lib/

"""

#================================================================
#%% Imports
#================================================================
# Standard library
import os
import time

# Third party libraries
import numpy as np
import pandas as pd
import tmpl

#================================================================
#%% SetupCondition classes
#================================================================

class Temperature(tmpl.AbstractSetupConditions):
    """
    <Description of condition>
    """
    #name = '<name_in_dataset' # Name used in ds_results dataset (optional)

    def initialise(self):
        """
        Initialise default values and any other setup
        """

        # Set default values
        self.values = [<values>]


    @property
    def actual(self):
        return <Return value code>

    @property
    def setpoint(self):
        return <Return setpoint code>

    @setpoint.setter
    def setpoint(self,value):
        self.log(f'Setpoint = {value} ')
        # TODO :<Setpoint code>
        return <Setpoint value>



class Humidity(tmpl.AbstractSetupConditions):
    """
    <Description of condition>
    """
    #name = '<name_in_dataset' # Name used in ds_results dataset (optional)

    def initialise(self):
        """
        Initialise default values and any other setup
        """

        # Set default values
        self.values = [<values>]


    @property
    def actual(self):
        return <Return value code>

    @property
    def setpoint(self):
        return <Return setpoint code>

    @setpoint.setter
    def setpoint(self,value):
        self.log(f'Setpoint = {value} ')
        # TODO :<Setpoint code>
        return <Setpoint value>



class Pressure(tmpl.AbstractSetupConditions):
    """
    <Description of condition>
    """
    #name = '<name_in_dataset' # Name used in ds_results dataset (optional)

    def initialise(self):
        """
        Initialise default values and any other setup
        """

        # Set default values
        self.values = [<values>]


    @property
    def actual(self):
        return <Return value code>

    @property
    def setpoint(self):
        return <Return setpoint code>

    @setpoint.setter
    def setpoint(self,value):
        self.log(f'Setpoint = {value} ')
        # TODO :<Setpoint code>
        return <Setpoint value>



#================================================================
#%% Measurement classes
#================================================================

class VoltageSweep(tmpl.AbstractMeasurement):
    """
    <Description of measurement>

    """

    def initialise(self):
        # Run conditions (optional)
        # self.run_on_startup(True)
        # self.run_on_teardown(True)
        # self.run_on_error(True)
        # self.run_on_setup(condition_label,value=None)
        # self.run_after(condition_label,value=None)

        # Set up configuration values
        self.config.<param> = <value>
        

    def meas_sequence(self):
        """
        <More description (optional)>
        """
        # TODO: Measurement code goes here
        pass
        
        


class CurrentSweep(tmpl.AbstractMeasurement):
    """
    <Description of measurement>

    """

    def initialise(self):
        # Run conditions (optional)
        # self.run_on_startup(True)
        # self.run_on_teardown(True)
        # self.run_on_error(True)
        # self.run_on_setup(condition_label,value=None)
        # self.run_after(condition_label,value=None)

        # Set up configuration values
        self.config.<param> = <value>
        

    def meas_sequence(self):
        """
        <More description (optional)>
        """
        # TODO: Measurement code goes here
        pass
        
        


class PostProcess(tmpl.AbstractMeasurement):
    """
    <Description of measurement>

    """

    def initialise(self):
        # Run conditions (optional)
        # self.run_on_startup(True)
        # self.run_on_teardown(True)
        # self.run_on_error(True)
        # self.run_on_setup(condition_label,value=None)
        # self.run_after(condition_label,value=None)

        # Set up configuration values
        self.config.<param> = <value>
        

    def meas_sequence(self):
        """
        <More description (optional)>
        """
        # TODO: Measurement code goes here
        pass
        
        


#================================================================
#%% TestManager classes
#================================================================

class Calibrate(tmpl.AbstractTestManager):
    """
    <Description of test sequence>
    """

    def define_setup_conditions(self):
        """
        Add the setup conditions here in the order that they should be set
        """
        self.add_setup_condition(Temperature)
        self.add_setup_condition(Humidity)
        self.add_setup_condition(Pressure)


    def define_measurements(self):
        """
        Add measurements here in the order of execution
        """

        # Setup links to all the measurements
        self.add_measurement(VoltageSweep)
        self.add_measurement(CurrentSweep)
        self.add_measurement(PostProcess)


    def initialise(self):
        """
        Add custom information here
        """
        
        self.information.serial_number = 'example_sn'
        self.information.part_number = 'example_pn'
        # Add more here ...
 


class MainMeasure(tmpl.AbstractTestManager):
    """
    <Description of test sequence>
    """

    def define_setup_conditions(self):
        """
        Add the setup conditions here in the order that they should be set
        """
        self.add_setup_condition(Temperature)
        self.add_setup_condition(Humidity)
        self.add_setup_condition(Pressure)


    def define_measurements(self):
        """
        Add measurements here in the order of execution
        """

        # Setup links to all the measurements
        self.add_measurement(VoltageSweep)
        self.add_measurement(CurrentSweep)
        self.add_measurement(PostProcess)


    def initialise(self):
        """
        Add custom information here
        """
        
        self.information.serial_number = 'example_sn'
        self.information.part_number = 'example_pn'
        # Add more here ...
 

