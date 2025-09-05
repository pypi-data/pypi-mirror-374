from .general import *
from .procedures import Watering
@analysisschema
class DecisionTask(dj.Imported): # imported because if comes from data but there is no 'make'
    '''Table for behavioral decision task data.
    
    This table serves as a general schema for decision-making behavioral tasks,
    abstracting common features that can be inherited by specific task tables
    defined in plugins. Each entry includes:
    - Total trial counts (assisted, self-performed, initiated, with choice)
    - Performance metrics (rewarded, punished trials)
    - Optional reference to water intake during session
    
    The table includes a Part table (TrialSet) that stores detailed sets of trials within a session, 
    dependent on the modality or condition and includes including:
    - Trial conditions and modalities
    - Performance metrics per condition
    - Timing data (initiation times, reaction times) 
    - Response and subject feedback values
    - Stimulus parameters (intensity, block)
    
    This data can be used to compute:
    - Psychometric curves
    - Learning curves
    - Reaction time distributions
    - Choice biases and strategies
    - ...
    
    The schema is designed to be flexible and is meant to be populated by specific task tables (defined as plugins) 
    while maintaining a consistent interface for analysis and visualization.
    '''
    definition = '''
    -> Dataset
    ---
    n_total_trials              : int            # number of trials in the session
    n_total_assisted = NULL     : int            # number of assisted trials in the session
    n_total_performed = NULL    : int            # number of self-performed trials
    n_total_initiated = NULL    : int            # number of initiated trials
    n_total_with_choice = NULL  : int            # number of self-initiated with choice
    n_total_rewarded = NULL     : int            # number of rewarded trials
    n_total_punished = NULL     : int            # number of punished trials
    -> [nullable] Watering                       # water intake during the session (ml) 
    '''
        
    class TrialSet(dj.Part):
        definition = '''
        -> master
        trialset_description     : varchar(54) # e.g. trial modality, unique condition
        ---
        n_trials                 : int         # total number of trials
        n_performed              : int         # number of self-performed trials
        n_with_choice            : int         # number of self-initiated trials with choice 
        n_correct                : int         # number of correct trials
        performance_easy = NULL  : float       # performance on easy trials
        performance = NULL       : float       # performance on all trials
        trial_num                : longblob    # trial number because TrialSets can be intertwined
        initiation_times = NULL  : longblob    # time between trial start and stim onset
        assisted = NULL          : longblob    # wether the trial was assisted
        response_values = NULL   : longblob    # left=1;no response=0; right=-1        
        correct_values = NULL    : longblob    # correct = 1; no_response  = NaN; wrong = 0        
        intensity_values = NULL  : longblob    # value of the stim (left-right)
        reaction_times = NULL    : longblob    # between onset of the response period and reporting  
        block_values = NULL      : longblob    # block number for each trial
        '''

        
