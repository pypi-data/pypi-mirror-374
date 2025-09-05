from .general import *

@dataschema
class Weighing(dj.Manual):
    '''Table for tracking subject weights.
    
    This table stores weight measurements for experimental subjects. Each entry includes:
    - Subject
    - Date and time of weighing
    - Weight in grams
    
    '''
    definition = """
    -> Subject
    weighing_datetime : datetime
    ---
    weight : float  # (g)
    """

@dataschema
class ProcedureType(dj.Lookup):
    '''Table defining types of experimental procedures.
    
    This lookup table enumerates the different types of experimental procedures, including:
    - Surgical procedures (surgery, implants, craniotomy)
    - Behavioral procedures (handling, training) 
    - Other manipulations (injections)
    
    The procedure types are used by the Procedure table to categorize and track all
    procedures performed.
    '''
    definition = """
    procedure_type : varchar(52)       #  Defines procedures that are not an experimental session
    """
    contents = zip(['surgery',
                    'chronic implant',
                    'chronic explant', 
                    'injection',
                    'window implant',
                    'window replacement',
                    'handling',
                    'training',
                    'craniotomy'])

@dataschema
class Procedure(dj.Manual):
    '''Table for tracking experimental procedures performed on subjects.
    
    Each procedure entry includes:
    - Subject
    - ProcedureType
    - Date and time
    - Lab member who performed it
    - Optional metadata: weight, and notes
    '''
    definition = """
    -> Subject
    -> ProcedureType
    procedure_datetime            : datetime
    ---
    -> LabMember
    procedure_metadata = NULL     : longblob   
    -> [nullable] Weighing
    -> [nullable] Note
    """

@dataschema
class Watering(dj.Manual):
    '''Table for tracking water administration to subjects.
    
    This table records water consumed, including:
    - Subject receiving water
    - Date and time
    - Volume of water, in microliters
    
    '''
    definition = """
    -> Subject
    watering_datetime : datetime
    ---
    water_volume : float  # (uL)
    """
    
@dataschema
class WaterRestriction(dj.Manual):
    definition = """
    -> Subject
    water_restriction_start_date : date
    ---
    -> LabMember
    water_restriction_end_date : date
   -> Weighing
    """

@dataschema
class Death(dj.Manual):
    definition = """
    -> Subject
    ---
    death_date :          datetime       # death date
    -> [nullable] Note
    """
