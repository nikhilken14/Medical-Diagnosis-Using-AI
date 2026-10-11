from pathlib import Path
from streamlit.testing.v1 import AppTest
from screenings import SPECS

def main():
    app=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=30).run()
    assert not app.exception
    app.button(key='nav_Get started').click().run()
    for name in SPECS:
        app.selectbox(key='disease').select(name).run()
        next(b for b in app.button if b.label=='Analyze my inputs →').click().run()
        assert len(app.error)>0, name
        next(b for b in app.button if b.label=='Load sample data').click().run()
        next(b for b in app.button if b.label=='Analyze my inputs →').click().run()
        assert not app.exception, name
        assert 'result_'+name in app.session_state, name
        next(b for b in app.button if b.label=='Clear inputs').click().run()
        assert 'result_'+name not in app.session_state, name
        print(name+': passed')
    for page in ['Health info','About','Home']:
        app.button(key='nav_'+page).click().run()
        assert not app.exception, page
    print('All application smoke checks passed.')

if __name__=='__main__':main()
