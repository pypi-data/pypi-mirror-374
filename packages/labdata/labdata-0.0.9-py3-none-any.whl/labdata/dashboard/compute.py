import pandas as pd
import streamlit as st
import numpy as np

def compute_tab():
    from labdata.schema import ComputeTask
    df = pd.DataFrame(ComputeTask().fetch())[['job_id',
                                              'task_name',
                                              'task_status',
                                              'task_host',
                                              'task_target',
                                              'task_waiting',
                                              'task_log',
                                              'subject_name',
                                              'session_name',
                                              'task_starttime',
                                              'task_endtime']]
    if len(df):
        tx = '## Compute tasks'
        histcounts = []
        stat = ''
        states = ['COMPLETED','WORKING','WAITING','FAILED','CANCELED']
        for t in states:
            stat += f'\n {t} [{len(df[df.task_status == t])}]'
        st.write(tx)
        df = df.set_index('job_id')
        selected_indices = st.multiselect('Select task status:',states,default = states[1:])
        idx = np.zeros(len(df),dtype = bool)
        for s in selected_indices:
            idx = idx | [s in a for a in df.task_status.values]
        st.write(stat,df.iloc[(idx==1)])
       
        # Summary per queue
        targets = [d if not d is None else 'unknown' for d in df.task_target.values]
        df.task_target = targets
        qcounts = []
        for t in np.unique(targets):
            for tt,c in zip(states,['#01D186','#48CAE4','#F3A21C','#FF5733','#F3A21C']):
                qcounts.append({'Task status':f'{tt}|{t}',
                                   'Compute tasks':len(df[([tt in a for a in df.task_status.values]) & (df.task_target.values == t)]),
                                  'color' : c})
        qcounts = pd.DataFrame(qcounts)
        import altair as alt
        ch = (alt.Chart(qcounts).mark_bar().encode(
            y = 'Task status:N', #alt.Y(,type = 'nominal'),
            x = 'Compute tasks:Q',#alt.X(,type = 'quantitative'),
            color = alt.Color('color:N').scale(None)).configure_axis(labelLimit=3000))#alt.Color('color',type = 'nominal')))
                
        st.altair_chart(ch,use_container_width = True)
        
    else:
        st.write('### There are no tasks in the table')
