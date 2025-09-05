import pandas as pd
from labdata.schema import SpikeSorting,SpikeSortingParams,Session,EphysRecording,UnitCount,UnitMetrics
import streamlit as st
import numpy as np

def sorting_tab():
    pars = SpikeSortingParams().fetch(format='frame')[['algorithm_name','parameters_dict']]
    pars.insert(0, "Select", False)
    edited_df = st.data_editor(pars.sort_index(),
                               hide_index=False,
                               disabled = ['parameter_set_num',
                                           'algorithm_name',
                                           'parameters_dict'])
    sessions = SpikeSorting().fetch(format = 'frame').reset_index()
    par_sets = edited_df[edited_df.Select == 1].reset_index()
    colors = ['#1f77b4',
              '#ff7f0e',
              '#d62728',
              '#2ca02c',
              '#9467bd',
              '#8c564b',
              '#e377c2',
              '#7f7f7f',
              '#bcbd22']
    selected_subjects = []
    if len(par_sets):
        sess = []
        for p in par_sets.parameter_set_num.values:
            sess.append(sessions[sessions.parameter_set_num == p])
        sess = pd.concat(sess)
        subjects  = np.unique(sess.subject_name.values)
        sesdict = []
        for p in par_sets.parameter_set_num.values:
            for subj in subjects:
                sub = sessions[(sessions.subject_name == subj) & (sessions.parameter_set_num == p)]
                sesdict.append({'subject_name' : subj,
                                'number_of_sessions': len(sub),
                                'parameter_set_num': p,
                                'number_of_probes':len(np.unique(sub.probe_num.values))})
        sesdict = pd.DataFrame(sesdict)
        # st.bar_chart(sesdict.set_index('subject_name'),y='number_of_sessions')
        import altair as alt
        ch = (alt.Chart(sesdict).mark_bar().encode(
            y = 'subject_name:N', #alt.Y(,type = 'nominal'),
            x = 'number_of_sessions:Q',#alt.X(,type = 'quantitative'),
        color='parameter_set_num:N').configure_axis(labelLimit=3000))#alt.Color('color',type = 'nominal')))
        st.altair_chart(ch,use_container_width = True)
        selected_subjects = st.multiselect('Select subject:',subjects)
    
    @st.cache_data
    def get_unit_counts(s,p):
        print(s,p)
        return pd.DataFrame(UnitCount()*Session()*EphysRecording.ProbeSetting() & dict(
                        subject_name = s,
                        parameter_set_num = p,
                        unit_criteria_id = 1))
        
    if len(selected_subjects):   
        units = []
        for p in par_sets.parameter_set_num.values:
            for s in selected_subjects:
                units.append(get_unit_counts(s,p))
        unit_counts = pd.concat(units).set_index('subject_name')
        
        # make the probe color
        N = len(colors)
        cc = np.array([colors[0] for c in np.arange(len(unit_counts.probe_id.values))])
        for i,p in enumerate(np.unique(unit_counts.probe_id)):
            idx = np.where(unit_counts.probe_id.values == p)[0]
            cc[idx] = colors[np.mod(i,N)]
        unit_counts['probe_color'] = cc
        st.scatter_chart(unit_counts,x = 'session_datetime',y = 'all',color = 'probe_color',size = 30)
        st.scatter_chart(unit_counts,x = 'session_datetime',y = 'sua',color = 'probe_color',size = 30)

 