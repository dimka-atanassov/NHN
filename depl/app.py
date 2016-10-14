from flask import Flask, render_template, request, redirect
import pandas as pd
#from IPython.display import HTML
import folium
import simplejson as json
from bokeh.models.widgets import Panel, Tabs
from bokeh.layouts import widgetbox
from bokeh.plotting import figure
from bokeh.embed import components

app = Flask(__name__)

@app.route('/')
def main():
    return redirect('/index')


def my_color_function(feature, color_dict, year = 2016):
    """Maps low values to green and hugh values to red."""
    #print feature['properties']
    _zip = feature['properties']['ZCTA5CE00']
    if _zip in color_dict[year].keys():
        return color_dict[year][feature['properties']['ZCTA5CE00']]
    else:
        return '#FFFFFF'
    

@app.route('/index', methods  = ['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('/index.html')
        

@app.route('/historic', methods  = ['GET','POST'])
#@app.route('/index')
def historic():
  
    if request.method == 'GET':
        return render_template('/historic.html')
    elif request.method =='POST':
        selected_features =  request.form.get('drop-down')
        if selected_features:
            #print selected_features
            year = str(int(selected_features)+1)
            #print >> sys.stderr, 'here'
            SFZipsJson_big_file =open('SFJson.txt').read()
            SFZipsJson_big = json.loads(SFZipsJson_big_file)
            #ByZipcodeYearlyBack2 = pd.read_csv('../BeatMarket.csv')
    
            color_dict_file = open('Colors.txt').read()
            color_dict = json.loads(color_dict_file)
            SF_COORDINATES = (37.76, -122.45)

            sf_map = folium.Map(location=SF_COORDINATES, zoom_start=12)

            folium.GeoJson(
                SFZipsJson_big,
                style_function=lambda feature: {
                    'fillColor': my_color_function(feature, color_dict, year),
                    'color' : 'black',
                    'weight' : 2,
                    'dashArray' : '5, 5'
                    }
                ).add_to(sf_map)

               
            return render_template('/show.html', show_map = sf_map._repr_html_(), year = str(int(year)-1))
            #return render_template('small_zips.html')

@app.route('/predict',  methods  = ['GET','POST']) 
def predict():
    if request.method == 'GET':
        return render_template('/predict.html')
    else:
        result_text = 'Aw snap! Looks like we don\'t have information about this zipcode. Try another one!'
        zipcode =  request.form['zipcode']
        #print zipcode 
        predictions = pd.read_csv('2016_predict.csv')
        try:
            zipcode = int(zipcode)
            if predictions['BM'][predictions['Zipcode']==zipcode].values[0]==1:
                result_text = 'Congratulations! This zipcode is predicted to beat the market!'
            else:
                result_text = 'This zipcode is not predicted to beat the market.'
        except:
            result_text = 'Aw snap! Looks like we don\'t have information about this zipcode. Try another one!'
            
        return render_template('/predict_show.html', zipcode = zipcode ,result_text = result_text)
        

@app.route('/zipcode', methods  = ['GET','POST']) 
def zipcode():
    
    from bokeh.plotting import figure
    from bokeh.embed import components

    if request.method == 'GET':
        return render_template('/zipcode.html')
    else:
        #print 'here'
        zipcode =  request.form['zipcode']
        #print zipcode
        if zipcode:
            zipcode = int (zipcode)
            PriceChange = pd.read_csv('useful.csv')
            zipcode_data = PriceChange[PriceChange['Zipcode'] == zipcode]
            p1 = figure(plot_width=500, plot_height=300)
            zipcode_data['Year'] = zipcode_data['Year'].apply(lambda x: int(x)-1)
            p1.line(zipcode_data['Year'].values, zipcode_data['Value'].values, line_width=3, color="navy", alpha=0.5, legend = str(zipcode))
            p1.line(zipcode_data['Year'].values, zipcode_data['mean'].values, line_width=5, color="pink", alpha=0.4, legend = 'Mean')

            tab1 = Panel(child=p1, title="Yearly Price Change")

            p2 = figure(plot_width=500, plot_height=300)
            zipcode_data['Year2'] = zipcode_data['Year'].apply(lambda x: x+1)
            p2.line(zipcode_data['Year2'].values, (zipcode_data['percentage'].values)*100, line_width=3, color="navy", alpha=0.5, legend = str(zipcode))
            #tab2 = Panel(child=p2, title="Percentage of Crime in Zipcode")
            
            #tabs = Tabs(tabs=[ tab1, tab2])
            script1, div1 = components(p1)
            script2, div2 = components(p2)
            return render_template('/show_zipcode.html', zipcode = zipcode ,script1 = script1, div1= div1, script2 = script2, div2 = div2)
        
    
if __name__ == '__main__':
    #app.run('localhost', port=8883)
    
    app.run(port=33507)
