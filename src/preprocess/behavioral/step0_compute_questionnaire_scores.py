"""
This script computes the scores for the initial questionnaires according to the
each test's instructions.

Inputs:  - excel file with the answers 

Outputs: - excel file with the computed scores 

@author: ana.trianahoyos@aalto.fi
Created: 07.06.2023
"""

import pandas as pd
from datetime import datetime

################################# MODIFY ######################################
path = "/m/cs/archive/networks-pm/behavioral/questionnaires/questionnaires.xlsx"
savepath = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/questionnaires"
###############################################################################

def compute_phq_gad(df):
    df.drop(columns=['id','question'],inplace=True)
    data = df.sum(skipna=False)
    return data

def remap(row):
    mapping = {0:4, 1:3, 2:2, 3:1, 4:0}
    if row.name in [4,5,7,8]:
        return row.map(mapping)
    else:
        return row

def compute_pss(df):
    df.set_index("id",inplace=True)
    df.drop(columns=["question"], inplace=True)
    df2 = df.apply(remap, axis=1)
    df2 = df2.sum(skipna=False)
    return df2

def reverse_value(val):
    return 6-val

def compute_average(df, rows):
    df_copy = df.copy()
    for row in rows:
        if "R" in row:
            row = int(row.replace("R", ""))  # remove "R" and convert to int
            df_copy.loc[row] = df_copy.loc[row].apply(reverse_value)
    average = df_copy.loc[[int(r.replace("R", "")) for r in rows]].mean()
    return average

def compute_big_five(df):
    df.set_index("id",inplace=True)
    df.drop(columns=['question', 'Unnamed: 3', 'Unnamed: 4'], inplace=True)
    
    extraversion_avg = compute_average(df, ['1', '6R', '11', '16', '21R', '26', '31R', '36'])
    agreeableness_avg = compute_average(df, ['2R', '7', '12R', '17', '22', '27R', '32', '37R', '42'])
    conscientiousness_avg = compute_average(df, ['3', '8R', '13', '18R', '23R', '28', '33', '38', '43R'])
    neuroticism_avg = compute_average(df, ['4', '9R', '14', '19', '24R', '29', '34R', '39'])
    openness_avg = compute_average(df, ['5', '10', '15', '20', '25', '30', '35R', '40', '41R', '44'])
    
    traits = pd.Series(["extraversion", "agreeableness", "conscientiousness", "neuroticism", "openness"])
    
    result = pd.concat([extraversion_avg, agreeableness_avg, conscientiousness_avg, neuroticism_avg, openness_avg]).reset_index() 
    result = pd.concat([result,traits], axis=1)
    result.drop(columns=['index'], inplace=True)
    return result

def compute_psqi(df):
    df['id'] = df["id"].astype(str)
    def calculate_C2(row):
        if row <= 15:
            return 0
        elif 16 <= row <= 30:
            return 1
        elif 31 <= row <= 60:
            return 2
        else:
            return 3

    def calculate_C3(row):
        if row > 7:
            return 0
        elif 6 <= row <= 7:
            return 1
        elif 5 <= row <= 6:
            return 2
        else:
            return 3

    def calculate_C4(asleep, in_bed):
        ratio = asleep/in_bed * 100
        if ratio > 85:
            return 0
        elif 75 <= ratio <= 84:
            return 1
        elif 65 <= ratio <= 74:
            return 2
        else:
            return 3

    def calculate_C5(row):
        if row == 0:
            return 0
        elif 1 <= row <= 9:
            return 1
        elif 10 <= row <= 18:
            return 2
        else:
            return 3

    def calculate_C7(row):
        if row == 0:
            return 0
        elif 1 <= row <= 2:
            return 1
        elif 3 <= row <= 4:
            return 2
        else:
            return 3

    # Create a dictionary mapping the ids to the corresponding answers
    answers = df.set_index('id')['answer'].to_dict()

    # Calculate the components
    C1 = answers['9']

    C2 = calculate_C2(int(answers['2'])) + int(answers['a'])

    C3 = calculate_C3(int(answers['4']))

    bed_time = answers['1'].hour
    wake_up_time = answers['3'].hour
    in_bed = (wake_up_time - bed_time) % 24
    asleep = int(answers['4'])
    C4 = calculate_C4(asleep, in_bed)

    C5_scores = [int(answers[key]) for key in ['b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']]
    C5 = calculate_C5(sum(C5_scores))

    C6 = int(answers['6'])

    C7 = calculate_C7(int(answers['7']) + int(answers['8']))

    # Compute global score
    global_score = C1 + C2 + C3 + C4 + C5 + C6 + C7
    
    data = [('C1', C1),('C2', C2),('C3', C3),('C4', C4),('C5', C5),('C6', C6),('C7', C7),('Global Score', global_score)]

    # Create a DataFrame using the list of tuples
    result = pd.DataFrame(data, columns = ['Component', 'Score'])

    return result

################### Computation starts here ###################################    
#Compute the scores
df = pd.read_excel(path, sheet_name="Big Five Inventory", skiprows=[0,1,2,3,4,5])
big_five = compute_big_five(df)

df = pd.read_excel(path, sheet_name="PSS", skiprows=[0,1,2])
pss = compute_pss(df)

df = pd.read_excel(path, sheet_name="PHQ9", skiprows=[0,1,2])
phq = compute_phq_gad(df)

df = pd.read_excel(path, sheet_name="GAD7", skiprows=[0,1,2])
gad = compute_phq_gad(df)

df = pd.read_excel(path, sheet_name="PSQI", skiprows=[0,1,2])
psqi = compute_psqi(df)

with pd.ExcelWriter(f'{savepath}/scores.xlsx') as writer:  
    big_five.to_excel(writer, sheet_name='big5')
    pss.to_excel(writer, sheet_name='pss')
    phq.to_excel(writer, sheet_name='phq9')
    gad.to_excel(writer, sheet_name='gad7')
    psqi.to_excel(writer, sheet_name='psqi')