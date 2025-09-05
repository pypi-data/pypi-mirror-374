import streamlit as st
import pandas as pd
import numpy as np

def parse_procedure(procedure_dict):
    from datetime import datetime
    note_insert = None
    weight_insert = None
    insert = dict(subject_name = procedure_dict['subject_name'],
                    procedure_datetime = datetime.combine(procedure_dict['date'],procedure_dict['time']),
                    procedure_type = procedure_dict['procedure_type'])
    if not procedure_dict['user_name'] is None:
        insert['user_name'] = procedure_dict['user_name']
        if not procedure_dict['note'] is None:
            note_insert = dict(notetaker = insert['user_name'],
                                note_datetime = insert['procedure_datetime'],
                                notes = procedure_dict['note'])
            insert['note_datetime'] = note_insert['note_datetime']
            insert['notetaker'] = note_insert['notetaker']
    if procedure_dict['user_name'] is None and not procedure_dict['note'] is None: 
        raise(ValueError('Need to specify a user_name for adding notes.'))
    if not procedure_dict['weight'] is None:
        weight_insert = dict(weight = procedure_dict['weight'],
                                subject_name = procedure_dict['subject_name'],
                                weighing_datetime = insert['procedure_datetime'])
        insert['weighing_datetime'] = weight_insert['weighing_datetime']
        
    return insert,note_insert,weight_insert


def procedures_tab():
    from labdata.schema import LabMember, Subject, Dataset, Session, Strain, ProcedureType, Procedure, Note, Weighing
    st.cache_resource()
    def get_users_and_subjects():
        return LabMember.fetch('user_name'),Subject.fetch('subject_name')
    
    users,subjects = get_users_and_subjects()
    st.cache_resource()
    def get_procedure_types():
        return ProcedureType.fetch('procedure_type')
    
    st.cache_resource()
    def get_procedures(subject_name):
        return pd.DataFrame((Procedure*Note & dict(subject_name = subject_name)).fetch())
    
    procedure_types = get_procedure_types()
    
    procedure_dict = dict()
    procedure_dict['subject_name'] = st.selectbox('__Subject__', subjects,index = None)

    if not procedure_dict['subject_name'] is None:
        procedures = get_procedures(procedure_dict['subject_name'])
        if len(procedures):
            edited_procedures = st.data_editor(procedures,column_config={
            "Select":st.column_config.CheckboxColumn(required=True)})
        else:
            st.write('There are no procedures for this subject.')
        # st.write(procedure_dict)
        st.write('### Add procedure:')
        with st.form('add procedure'):
            procedure_dict['user_name'] = st.selectbox('__Experimenter__', users,index = None)
            procedure_dict['date'] = st.date_input('__Date__', value = "today")
            procedure_dict['time'] = st.time_input('__Procedure start time__', value = "now")
            procedure_dict['procedure_type'] = st.selectbox('__Procedure type__', procedure_types, index = None)
            procedure_dict['procedure_metadata'] = st.text_input('__Metadata__', value = None)
            procedure_dict['weight'] = st.number_input('__Weight__', value = None)
            procedure_dict['note'] = st.text_area('__Notes__', value = None)
            submitted = st.form_submit_button('Add Procedure', type='primary')
            if submitted:
                
                for a in ['date','time','procedure_type','user_name']:
                    if not procedure_dict[a]:
                        st.error(f"Specify a {a}")
                # merge the procedure date and time
                proc_dict,note_dict,weigh_dict = parse_procedure(procedure_dict)
                st.write(proc_dict),st.write(note_dict),st.write(weigh_dict)
                
                if not note_dict is None:
                    Note.insert1(note_dict)
                if not weigh_dict is None:
                    Weighing.insert1(weigh_dict)
                Procedure.insert1(proc_dict)
                st.write('Added procedure to database')
    # select a proceedure

def notes_tab():
    pass

def intro_tab(user_name = None):
    from labdata.schema import Subject, Dataset, Session, Strain
    @st.cache_data
    def get_subjects():
        if not user_name is None:
            df = pd.DataFrame((Subject() & f'user_name = {user_name}').fetch())
        else:        
            df = pd.DataFrame(Subject().fetch())
        df.insert(0, "Select", False)
        return df.set_index("subject_name").sort_index()
        
    @st.cache_data
    def get_sessions(keys):
        if len(keys):
            keys = keys.reset_index()
            dfs = []
            for i in range(len(keys)):
                dfs.append(pd.DataFrame((Session()*Dataset() &
                                            f'subject_name = "{keys["subject_name"].iloc[i]}"').fetch()))
            if len(dfs):
                d = [d for d in dfs if len(d)]
                if not len(d):
                    return None
                df = pd.concat(d)
                return df.set_index("session_datetime").sort_index()
            else:
                return None
        return None
    subjects = get_subjects() 
    st.write("### Subjects", )
    edited_df = st.data_editor(subjects.sort_index(),
                                hide_index=False,
                                disabled = ['subject_name',
                                            'subject_dob',
                                            'subject_sex',
                                            'strain_name',
                                            'user_name'])
                                #column_config={"Select":
                                #               st.column_config.CheckboxColumn(required=True)},)
    sessions = get_sessions(edited_df[edited_df['Select'] == True])
    if sessions is None:
        st.write('No subjects selected.')
    else:
        uniqueds = np.unique([s for s in sessions.dataset_type.values if not s is None])
        tx = f'### Sessions ({len(sessions)})'
        for d in uniqueds:
            if not d is None:
                tx += f' - {d}: {len(sessions[sessions.dataset_type == d])}'
        st.write(tx,sessions)

    st.write('### Add a subject')
    insert_dict = dict()

    st.cache_resource()
    def get_users():
        return LabMember.fetch('user_name')
    
    with st.form('add subject'):
        from labdata.schema import LabMember, Strain, Subject
        users = get_users()
        insert_dict['user_name'] = st.selectbox('__User Name__', users)
        insert_dict['subject_name'] = st.text_input('__Subject ID__',value=None)
        insert_dict['subject_dob'] = st.date_input('__Date of Birth__')
        insert_dict['subject_sex'] = st.selectbox('__Sex__', ['M', 'F', 'Unknown'])
        if insert_dict['subject_sex'] == 'Unknown':
            insert_dict['subject_sex'] = 'U'
        available_strains = [s for s in Strain().fetch('strain_name')]
        insert_dict['strain_name'] = st.selectbox('__Strain__', available_strains)
        submitted = st.form_submit_button('Add Subject', type='primary')
        if submitted:
            st.write('Adding subject to database')
            st.write(insert_dict)
            Subject().insert1(insert_dict)

    selected_subject = edited_df[edited_df['Select'] == True]
    if len(selected_subject):
        selected_subject = selected_subject.reset_index()
        selected_subject = selected_subject['subject_name'].iloc[0]
        edit_dict = dict(subject_name = selected_subject)
        st.write(f'### Edit subject: {selected_subject}')
        with st.form('edit subject'):
            from labdata.schema import LabMember, Strain, Subject
            edit_dict = (Subject & edit_dict).fetch1()
            st.write(edit_dict)
            
            edit_dict['subject_dob'] = st.date_input('__Date of Birth__', value = edit_dict['subject_dob'])
            edit_dict['subject_sex'] = st.selectbox('__Sex__', ['M', 'F', 'U'], index = ['M', 'F', 'U'].index(edit_dict['subject_sex']))
            edit_dict['strain_name'] = st.selectbox('__Strain__', available_strains, index = available_strains.index(edit_dict['strain_name']))
            submitted = st.form_submit_button('Edit', type='primary')
            if submitted:
                st.write('Adding subject to database')
                st.write(edit_dict)
                Subject().update1(edit_dict)
                st.write(f'Updated {edit_dict["subject_name"]}')
                get_subjects.clear()
                import time
                for i in range(10):
                    time.sleep(0.2)
                    st.write(f'.')
                st.rerun()
st.set_page_config(
    page_title="labdata dashboard",
    page_icon="🧪",
    layout="wide",
      initial_sidebar_state="auto")

from compute import compute_tab
from sorting import sorting_tab
from video import video_tab

page_names_to_funcs = {
    "**Subjects**": intro_tab,
    "**Procedures**": procedures_tab,
    "**Notes**": notes_tab,
    "**Compute tasks**": compute_tab,
    "**Spike sorting**": sorting_tab,
     "**Video**": video_tab,
}

from labdata import *
for p in plugins.keys():
    if hasattr(plugins[p],'dashboard_function'):
        page_names_to_funcs[plugins[p].dashboard_name] = plugins[p].dashboard_function

tab_name = st.sidebar.radio(
    "### labdata dashboard",
    page_names_to_funcs.keys())

page_names_to_funcs[tab_name]()