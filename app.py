import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIGURATION & STYLING ---
st.set_page_config(layout="wide")

st.markdown("""
    <style>
        .stApp {
            background-color: #f0f2f6;
        }
        .main-container {
            background-color: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        h1, h2, h3 {
            color: #2e7d32;
        }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS (INCLUDED IN THIS FILE for simplicity) ---
def generate_timetable(classes_df, subjects_df, faculty_df, labs_df):
    """Generates a raw timetable for all classes."""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    periods = [f"Period {i}" for i in range(1, 7)]
    subject_faculty = {}
    for _, row in faculty_df.iterrows():
        subj_str = str(row['subject_ids']).strip()
        if subj_str and subj_str.lower() != 'nan':
            for sid in subj_str.split(','):
                sid = sid.strip()
                if sid:
                    subject_faculty[sid] = str(row['faculty_id']).strip()

    timetable = {}
    for _, row in classes_df.iterrows():
        class_id = row['class_id']
        subs = subjects_df[subjects_df['class_id'] == class_id]['subject_id'].tolist()
        df = pd.DataFrame(index=periods, columns=days)

        if not subs:
            df.fillna("", inplace=True)
        else:
            for i, period in enumerate(periods):
                for j, day in enumerate(days):
                    sid = subs[(i + j) % len(subs)]
                    fid = subject_faculty.get(sid, "")
                    df.at[period, day] = f"{sid}:{fid}"
        timetable[str(class_id)] = df
    return timetable

def get_teacher_timetable(timetable_dict, faculty_id):
    """Filters the timetable for a specific teacher."""
    fid = str(faculty_id).strip()
    result = {}
    for class_id, df in timetable_dict.items():
        def has_fac(cell):
            if pd.isna(cell) or cell == "":
                return False
            if isinstance(cell, str) and ":" in cell:
                return cell.split(":", 1)[1].strip() == fid
            return False
        
        mask = df.applymap(has_fac)
        filtered = df.where(mask)
        filtered = filtered.dropna(how='all').dropna(axis=1, how='all')
        if not filtered.empty:
            result[class_id] = filtered
    return result

# --- SESSION STATE & DATA LOADING ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.faculty_id = None

# Check for data directory and files
if not os.path.exists("data/"):
    st.error("Data directory 'data/' not found. Please run data.py to generate the required CSV files.")
    st.stop()
try:
    faculty_df = pd.read_csv("data/faculty.csv")
    subjects_df = pd.read_csv("data/subjects.csv")
    labs_df = pd.read_csv("data/labs.csv")
    classes_df = pd.read_csv("data/classes.csv")
    users_df = pd.read_csv("data/users.csv")
except FileNotFoundError:
    st.error("One or more data files are missing. Please ensure all required CSVs are in the 'data/' directory.")
    st.stop()

st.title("Timetable App")

# Map IDs to names for display
subject_map = pd.Series(subjects_df['subject_name'].values, index=subjects_df['subject_id']).to_dict()
faculty_map = pd.Series(faculty_df['faculty_name'].values, index=faculty_df['faculty_id']).to_dict()

def format_cell(cell):
    if pd.isna(cell) or cell == "":
        return ""
    if ":" in cell:
        sid, fid = [x.strip() for x in cell.split(":", 1)]
        sub_name = subject_map.get(sid, sid)
        fac_name = faculty_map.get(fid, fid)
        return f"{sub_name} ({fac_name})"
    else:
        return cell

def replace_ids(df):
    return df.applymap(format_cell)

# --- LOGIN UI ---
if not st.session_state.logged_in:
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        user = users_df[(users_df['user_id'] == username) & (users_df['password'] == password)]
        if user.empty:
            st.sidebar.error("Invalid credentials")
            st.session_state.logged_in = False
        else:
            st.session_state.logged_in = True
            st.session_state.role = user.iloc[0]['role']
            st.session_state.faculty_id = str(user.iloc[0].get('faculty_id', '')).strip()
            st.experimental_rerun()

# --- MAIN APP CONTENT ---
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.role}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.experimental_rerun()

    timetable_raw = generate_timetable(classes_df, subjects_df, faculty_df, labs_df)

    # Format timetable for display
    timetable_formatted = {}
    for cls_id, df in timetable_raw.items():
        timetable_formatted[cls_id] = replace_ids(df).T

    if st.session_state.role == "admin":
        st.subheader("Class Timetables")
        for cls in classes_df['class_id']:
            st.markdown(f"### Class {cls}")
            st.table(timetable_formatted.get(str(cls), pd.DataFrame()))

    elif st.session_state.role == "teacher":
        st.subheader("Your Weekly Timetable Across Classes")
        teacher_tt_dict = get_teacher_timetable(timetable_raw, st.session_state.faculty_id)

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        periods = [f"Period {i}" for i in range(1, 7)]
        combined_df = pd.DataFrame("", index=periods, columns=days)

        if isinstance(teacher_tt_dict, dict):
            for class_id, df in teacher_tt_dict.items():
                for day in days:
                    for period in periods:
                        if day in df.columns and period in df.index and not pd.isna(df.at[period, day]):
                            combined_df.at[period, day] += f"{df.at[period, day]}\n"
        
        for day in days:
            for period in periods:
                if combined_df.at[period, day].strip() == "":
                    combined_df.at[period, day] = "Free"
        
        st.table(combined_df)
        
        # --- Download Feature ---
        csv_data = combined_df.to_csv(index=True).encode('utf-8')
        
        st.download_button(
            label="Download My Timetable as CSV",
            data=csv_data,
            file_name=f"{st.session_state.faculty_id}_timetable.csv",
            mime="text/csv",
        )
