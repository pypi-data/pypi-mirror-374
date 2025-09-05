import pandas as pd
import streamlit as st
from labdata.schema import DatasetVideo,Session
import numpy as np

def video_tab():
    import streamlit as st
    def get_subjects():
        df = np.unique((DatasetVideo()).fetch('subject_name'))
        df = pd.DataFrame(df,columns = ['subject_name'])
        
        df.insert(0, "Select", False)
        return df.set_index("subject_name").sort_index()
        
    def get_sessions(keys):
        if len(keys):
            keys = keys.reset_index()
            dfs = []
            for i in range(len(keys)):
                dfs.append(pd.DataFrame((Session*DatasetVideo.proj() &
                                         f'subject_name = "{keys["subject_name"].iloc[i]}"').fetch()))
                df = pd.concat([d for d in dfs if len(d)])
            return df.set_index("session_datetime").sort_index()
        return None
    subjects = get_subjects() 
    st.write("### Subjects", )
    edited_df = st.data_editor(subjects.sort_index(),
                               hide_index=False,
                               disabled = ['subject_name'])
                               #column_config={"Select":
                               #               st.column_config.CheckboxColumn(required=True)},)
    sessions = get_sessions(edited_df[edited_df['Select'] == True])

    if sessions is None:
        st.write('No subjects selected.')
    else:
        tx = f'### Sessions ({len(sessions)})'
        st.write(tx)        
        def update():
            st.write('hello')
        selection = st.dataframe(sessions,
                    on_select='rerun',
                    selection_mode="multi-row",)
        if len(selection.selection.rows):
            frames = (DatasetVideo.Frame & [dict(s) for i,s in sessions.iloc[selection.selection.rows].iterrows()]).proj().fetch(as_dict = True)
            slide = st.slider(label = 'Frame',min_value = 0, 
                              max_value = len(frames)-1,
                                               value = 0)
            im = (DatasetVideo.Frame() & frames[slide]).fetch1('frame')
            st.image(im)
