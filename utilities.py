def get_teacher_timetable(timetable_dict, faculty_id, free_periods=False, subject_map=None, subject_name_map=None):
    dfs = []
    class_names = []
    for class_id, df in timetable_dict.items():
        filtered_df = pd.DataFrame("", index=df.index, columns=df.columns)
        for day in df.index:
            for period in df.columns:
                cell = df.at[day, period]
                if pd.isna(cell) or cell == "":
                    if free_periods:
                        filtered_df.at[day, period] = "Free"
                elif isinstance(cell, str) and ":" in cell:
                    sid, fid = cell.split(":")
                    if fid == faculty_id:
                        name = subject_name_map.get(sid, sid) if subject_name_map else sid
                        filtered_df.at[day, period] = name
                    elif free_periods:
                        filtered_df.at[day, period] = "Free"
        if (filtered_df != "").any().any():
            dfs.append(filtered_df)
            class_names.append(class_id)

    if not dfs:
        return pd.DataFrame()

    if len(dfs) == 1:
        return dfs[0]

    # Combine vertically with MultiIndex columns showing class names
    combined_df = pd.concat(dfs, axis=1, keys=class_names)
    return combined_df
  
