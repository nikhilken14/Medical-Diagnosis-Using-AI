from pathlib import Path
import pickle
import pandas as pd

ROOT = Path(__file__).resolve().parent
# Numeric spec: (feature, user-facing label, minimum, maximum, step).
def num(key, label, lo=0.0, hi=1000.0, step=1.0):
    return dict(key=key, label=label, lo=float(lo), hi=float(hi), step=float(step))
def choice(key, label, options):
    return dict(key=key, label=label, options=options)
YES = {"No": 0, "Yes": 1}
SPECS = {
 "Diabetes": dict(icon="◈", color="#4c83d3", description="Explore patterns in glucose, body measurements and health history.", model="diabetes_model.sav", data="diabetes_data.csv", fields=[
 num("Pregnancies","Pregnancies",0,30),num("Glucose","Glucose (mg/dL)",1,600),num("BloodPressure","Diastolic blood pressure (mmHg)",1,250),num("SkinThickness","Skin thickness (mm)",0,150),num("Insulin","Insulin (µU/mL)",0,3000),num("BMI","Body mass index (kg/m²)",1,100,.1),num("DiabetesPedigreeFunction","Diabetes pedigree function",0,5,.001),num("Age","Age (years)",1,120)]),
 "Heart disease": dict(icon="♡",color="#df7294",description="Assess patterns in cardiovascular measurements and clinical test data.",model="heart_disease_model.sav",data="heart_disease_data.csv",fields=[
 num("age","Age (years)",1,120),choice("sex","Sex recorded for model",{"Female":0,"Male":1}),choice("cp","Chest pain type (dataset code)",{str(i):i for i in range(4)}),num("trestbps","Resting blood pressure (mmHg)",1,300),num("chol","Cholesterol (mg/dL)",1,1000),choice("fbs","Fasting blood sugar above 120 mg/dL",YES),choice("restecg","Resting ECG (dataset code)",{str(i):i for i in range(3)}),num("thalach","Maximum heart rate (bpm)",1,300),choice("exang","Exercise-induced angina",YES),num("oldpeak","ST depression (oldpeak)",0,10,.1),choice("slope","ST slope (dataset code)",{str(i):i for i in range(3)}),choice("ca","Major vessels (dataset code)",{str(i):i for i in range(5)}),choice("thal","Thal test (dataset code)",{str(i):i for i in range(4)})]),
 "Parkinson’s": dict(icon="♧",color="#9565d4",description="Analyze measured voice features from an acoustic assessment.",model="parkinsons_model.sav",data="parkinson_data.csv",fields=[]),
 "Lung cancer":dict(icon="⌁",color="#37b4ad",description="Explore associations in lifestyle and symptom survey responses.",model="lungs_disease_model.sav",data="prepocessed_lungs_data.csv",fields=[choice("GENDER","Sex recorded for model",{"Female":0,"Male":1}),num("AGE","Age (years)",1,120)]),
 "Thyroid":dict(icon="◇",color="#d5aa45",description="Evaluate patterns in thyroid laboratory values and treatment history.",model="Thyroid_model.sav",data="prepocessed_hypothyroid.csv",fields=[num("age","Age (years)",1,120),choice("sex","Sex recorded for model",{"Male":0,"Female":1}),choice("on thyroxine","Taking thyroxine",YES),num("TSH","TSH (dataset laboratory units)",0,500,.01),choice("T3 measured","T3 measured",YES),num("T3","T3 (dataset laboratory units)",0,30,.01),num("TT4","Total T4 (dataset laboratory units)",0,1000,.1)])
}
for key in ['MDVP:Fo(Hz)','MDVP:Fhi(Hz)','MDVP:Flo(Hz)','MDVP:Jitter(%)','MDVP:Jitter(Abs)','MDVP:RAP','MDVP:PPQ','Jitter:DDP','MDVP:Shimmer','MDVP:Shimmer(dB)','Shimmer:APQ3','Shimmer:APQ5','MDVP:APQ','Shimmer:DDA','NHR','HNR','RPDE','DFA','spread1','spread2','D2','PPE']:
 SPECS['Parkinson’s']['fields'].append(num(key,key,-100 if key=='spread1' else 0,1000,.00001))
for key in ['SMOKING','YELLOW_FINGERS','ANXIETY','PEER_PRESSURE','CHRONIC DISEASE','FATIGUE ','ALLERGY ','WHEEZING','ALCOHOL CONSUMING','COUGHING','SHORTNESS OF BREATH','SWALLOWING DIFFICULTY','CHEST PAIN']:
 SPECS['Lung cancer']['fields'].append(choice(key,key.strip().replace('_',' ').capitalize(),{"No":1,"Yes":2}))

def load_model(name):
    # Only load the bundled, trusted project artifacts; never user uploads.
    with (ROOT/'model'/SPECS[name]['model']).open('rb') as handle:
        return pickle.load(handle)

def sample_values(name):
    spec=SPECS[name]
    row=pd.read_csv(ROOT/'datasets'/spec['data']).iloc[0]
    return {f['key']:float(row[f['key']]) for f in spec['fields']}

def predict(name, values, model):
    keys=[f['key'] for f in SPECS[name]['fields']]
    if hasattr(model,'feature_names_in_'):
        if list(model.feature_names_in_) != keys:
            raise ValueError('The saved model feature order does not match this form.')
        data=pd.DataFrame([[values[k] for k in keys]],columns=keys)
    else:
        data=[[values[k] for k in keys]]
    return int(model.predict(data)[0])
