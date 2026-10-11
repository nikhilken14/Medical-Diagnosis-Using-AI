from datetime import datetime, timezone
from html import escape
import json
import streamlit as st
from screenings import ROOT, SPECS, load_model, sample_values, predict

st.set_page_config(page_title='MediCareAI | Health screening demo',page_icon='⚕',layout='wide')
st.markdown('<style>'+ (ROOT/'assets/style.css').read_text()+'</style>',unsafe_allow_html=True)
if 'page' not in st.session_state: st.session_state.page='Home'

def go(page, disease=None):
    st.session_state.page=page
    if disease: st.session_state.disease=disease

@st.cache_resource
def get_model(name): return load_model(name)

def html(content): st.markdown(content,unsafe_allow_html=True)

nav=st.columns([3,1,1.2,1,1.5])
with nav[0]: html('<div class="brand"><b>∿</b>MediCare<span>AI</span></div>')
for col,label in zip(nav[1:],['Home','Health info','About','Get started']):
    with col: st.button(label,key='nav_'+label,use_container_width=True,type='primary' if label=='Get started' else 'tertiary',on_click=go,args=('Screening' if label=='Get started' else label,))
st.divider()
page=st.session_state.page
if page=='Home':
    left,right=st.columns([1.15,1])
    with left:
        html('<div class="hero"><div class="eyebrow">Health insights, thoughtfully designed</div><h1>A clearer view of<br>your <span>health.</span></h1><p>Explore five machine learning screening tools in one simple space. Enter your measurements and understand what the model predicts.</p><div class="tags"><span>5 screening tools</span><span>Your original ML models</span><span>No account needed</span></div></div>')
        st.button('Explore screenings →',type='primary',on_click=go,args=('Screening',))
    with right: html('<div class="hero-art"><div class="orbit"><div class="core">⚕</div></div><div class="float one"><strong>♡ Heart health</strong>Insights from clinical data</div><div class="float two"><strong>◈ Five models. One space.</strong>A simpler screening experience</div><div class="float three"><strong>∿ Clear results</strong>Download your summary</div></div>')
    html('<div class="section-heading"><h2>Our AI screening services</h2><p>Choose a tool to explore your health data</p></div>')
    names=list(SPECS)+['Detailed reports']
    for row in [names[:3],names[3:]]:
        for col,name in zip(st.columns(3),row):
            with col:
                with st.container(border=True):
                    spec=SPECS.get(name,dict(icon='▤',color='#4bb995',description='Save a readable summary of your inputs and model result.'))
                    html(f'<div class="service"><span class="icon" style="color:{spec["color"]}">{spec["icon"]}</span><h3>{escape(name)}</h3><p>{escape(spec["description"])}</p></div>')
                    st.button('Open screening →' if name in SPECS else 'View report details →',key='card_'+name,type='tertiary',on_click=go,args=('Screening',name) if name in SPECS else ('About',))
    html('<div class="section-heading"><h2>How it works</h2><p>From your measurements to a model result in four steps</p></div>')
    for col,(title,desc) in zip(st.columns(4),[('Choose a screening','Select the model you want to explore.'),('Enter your data','Use measurements from your records.'),('Run the model','Review the classification and its limitations.'),('Save your summary','Download the result and entered values.')]):
        with col: html(f'<div class="step"><b>0{["Choose a screening","Enter your data","Run the model","Save your summary"].index(title)+1}</b><h3>{title}</h3><p>{desc}</p></div>')
    html('<div class="cta"><h2>Make your health data easier to explore.</h2><p>Start with a screening tool and review the results at your own pace.</p></div>')
    st.button('Start a screening →',key='bottom_start',type='primary',use_container_width=True,on_click=go,args=('Screening',))
elif page=='Screening':
    st.caption('HOME / SCREENING TOOLS')
    st.title('Your screening workspace')
    name=st.selectbox('Choose a screening',list(SPECS),key='disease')
    spec=SPECS[name]
    html(f'<div class="intro"><p><strong>{escape(name)}</strong> · {escape(spec["description"])}</p></div>')
    st.caption('Educational model demo. A result is not a diagnosis or an all-clear. No clinical accuracy claim is made.')
    if name=='Parkinson’s': st.info('These inputs require measured acoustic features. This tool does not record or analyze microphone audio.')
    if name=='Heart disease': st.caption('Use the categorical codes in the supplied dataset. The original app’s thal descriptions did not match its training data; codes are shown explicitly here.')
    if name=='Thyroid': st.caption('Use the same laboratory units as the training dataset. The project does not document unit conversions.')
    action1,action2,_=st.columns([1,1,3])
    with action1: demo=st.button('Load sample data',use_container_width=True)
    with action2: reset=st.button('Clear inputs',use_container_width=True)
    if demo or reset:
        sample=sample_values(name) if demo else {}
        for f in spec['fields']:
            key=name+'_'+f['key']
            if 'options' in f:
                st.session_state[key]=next((label for label,value in f['options'].items() if value==sample.get(f['key'])),None)
            else: st.session_state[key]=sample.get(f['key'])
        st.session_state.pop('result_'+name,None)
        st.session_state['demo_'+name]=demo
    if st.session_state.get('demo_'+name): st.warning('Sample mode: values come from a training dataset record, not your health records. Edit or clear them before entering personal measurements.')
    with st.form('form_'+name):
        st.subheader('Enter health parameters')
        st.caption('All fields are required. Decimals are supported; help text explains the expected input.')
        columns=st.columns(3)
        values={}
        for i,f in enumerate(spec['fields']):
            with columns[i%3]:
                key=name+'_'+f['key']
                if 'options' in f:
                    label=st.selectbox(f['label'],list(f['options']),index=None,placeholder='Choose an option',key=key,help='Options are converted to the codes used when this model was trained.')
                    values[f['key']]=f['options'].get(label)
                else:
                    values[f['key']]=st.number_input(f['label'],min_value=f['lo'],max_value=f['hi'],step=f['step'],value=None,key=key,format='%.5f' if f['step']<.001 else ('%.3f' if f['step']<.1 else ('%.1f' if f['step']<1 else '%.0f')),help='Enter a measured value, not a guess. Allowed input range is a form limit, not a clinical reference range.')
        submitted=st.form_submit_button('Analyze my inputs →',type='primary',use_container_width=True)
    if submitted:
        st.session_state.pop('result_'+name,None)
        missing=[f['label'] for f in spec['fields'] if values[f['key']] is None]
        if missing: st.error('Complete the following fields: '+', '.join(missing))
        else:
            try:
                with st.spinner('Running the saved model…'): label=predict(name,values,get_model(name))
                st.session_state['result_'+name]=dict(screening=name,model=spec['model'],classification=label,result='Positive model classification' if label==1 else 'Negative model classification',created_at=datetime.now(timezone.utc).isoformat(),sample_mode=st.session_state.get('demo_'+name,False),inputs=values,notice='Educational demo only. Not a medical diagnosis or an all-clear. A qualified clinician must interpret actual health concerns.')
            except Exception:
                st.error('The model could not run. Check the installed dependencies and the bundled model file. See README.md for compatibility guidance.')
    result=st.session_state.get('result_'+name)
    if result:
        with st.container(border=True):
            st.subheader('Your model result')
            if values!=result['inputs']:st.warning('Inputs have changed since this result. Run the analysis again to update it.')
            (st.warning if result['classification']==1 else st.info)(result['result'])
            st.write('The model assigned class '+str(result['classification'])+' to the submitted values. This does not establish whether you have a disease.')
            st.caption('No probability is shown: the original models do not all provide calibrated probabilities.')
            with st.expander('Review the inputs used for this result'): st.json(result['inputs'])
            text='MediCareAI — screening summary\n\n'+ '\n'.join([f'Screening: {name}',f'Result: {result["result"]}',f'Created (UTC): {result["created_at"]}',f'Sample mode: {result["sample_mode"]}','\nINPUTS']+[f'{k}: {v}' for k,v in result['inputs'].items()])+ '\n\n'+result['notice']
            c1,c2=st.columns(2)
            with c1: st.download_button('Download summary (.txt)',text,file_name=name.replace(' ','-')+'-summary.txt',mime='text/plain',use_container_width=True)
            with c2: st.download_button('Download data (.json)',json.dumps(result,indent=2),file_name=name.replace(' ','-')+'-summary.json',mime='application/json',use_container_width=True)
elif page=='Health info':
    st.title('Know your inputs')
    st.write('Each screening uses a different dataset and a fixed set of features. Enter measurements from your records using the units shown. Sample records are available to demonstrate the interface.')
    for name,spec in SPECS.items():
        with st.expander(name):
            st.write(spec['description'])
            st.write('Required inputs: '+', '.join(f['label'] for f in spec['fields']))
    st.info('These models are educational project artifacts. Dataset population, preprocessing and clinical validation limit how their predictions can be interpreted.')
elif page=='About':
    st.title('Built around your original models')
    st.write('MediCareAI brings five saved machine learning models into a clearer Streamlit experience. The original model files, datasets and notebooks are included in this project.')
    st.subheader('Readable, downloadable results')
    st.write('Every completed screening provides its classification, submitted inputs and timestamp. Download a text summary or JSON file. Reports do not include treatment advice or invented confidence scores.')
    st.subheader('Privacy')
    st.write('This app does not write screening inputs to a database or project file. Inputs and results are held in the active Streamlit session and sent to the server to run the model. Hosting infrastructure may have its own logging policies. Downloaded reports contain your entered data.')
html('<div class="footer"><div><strong>∿ MediCareAI</strong>Machine learning screening, made approachable.<br>Educational project · Built with Streamlit</div><div><strong>Screening tools</strong>Diabetes · Heart disease · Parkinson’s<br>Lung cancer · Thyroid</div><div><strong>Your next step</strong>Explore the models.<br>Discuss actual health concerns with a qualified clinician.</div></div><div class="notice">Educational demo only. Model predictions are not medical diagnoses.</div>')
