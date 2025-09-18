import pandas as pd
import os

def create_data_files():
    """Generates the required CSV data files for the Timetable app."""
    if not os.path.exists("data"):
        os.makedirs("data")

    faculty_data = {
        'faculty_id': ['F1', 'F2', 'F3', 'F4'],
        'faculty_name': ['Dr. Alex Smith', 'Dr. Jane Doe', 'Prof. Bob Johnson', 'Ms. Emily White'],
        'subject_ids': ['S1,S2', 'S3,S4', 'S5,S6', 'S7']
    }
    faculty_df = pd.DataFrame(faculty_data)
    faculty_df.to_csv("data/faculty.csv", index=False)

    subjects_data = {
        'subject_id': ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7'],
        'subject_name': ['Physics', 'Chemistry', 'Math', 'Biology', 'History', 'Geography', 'CS'],
        'class_id': ['1', '1', '2', '2', '3', '3', '1']
    }
    subjects_df = pd.DataFrame(subjects_data)
    subjects_df.to_csv("data/subjects.csv", index=False)

    labs_data = {
        'lab_id': ['L1', 'L2'],
        'lab_name': ['Physics Lab', 'Chemistry Lab']
    }
    labs_df = pd.DataFrame(labs_data)
    labs_df.to_csv("data/labs.csv", index=False)

    classes_data = {
        'class_id': ['1', '2', '3'],
        'class_name': ['1st Year - CS', '2nd Year - EE', '3rd Year - ME']
    }
    classes_df = pd.DataFrame(classes_data)
    classes_df.to_csv("data/classes.csv", index=False)

    users_data = {
        'user_id': ['admin', 'F1', 'F2'],
        'password': ['admin123', 'fac123', 'fac123'],
        'role': ['admin', 'teacher', 'teacher'],
        'faculty_id': ['', 'F1', 'F2']
    }
    users_df = pd.DataFrame(users_data)
    users_df.to_csv("data/users.csv", index=False)
    
    print("Data files generated successfully in the 'data/' directory.")

if __name__ == '__main__':
    create_data_files()
