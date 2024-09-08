from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
# import pandas as pd
import preprocess
import logging

# Initialize FastAPI app
app = FastAPI()


from fastapi.middleware.cors import CORSMiddleware

app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up the template directory
templates = Jinja2Templates(directory="templates")

# Load datasets
try:
    athlete_data = pd.read_csv('templates/datasets/athlete_events.csv')
    region_data = pd.read_csv('templates/datasets/noc_regions.csv')
except Exception as e:
    logging.error(f"Error loading datasets: {e}")

# Preprocess the data
try:
    df = preprocess.preprocess(athlete_data, region_data)
    medal_tally_df = preprocess.medal_tally(df)
except Exception as e:
    logging.error(f"Error preprocessing data: {e}")

def dictere(names):
    try:
        country_medal_count = preprocess.charts_over_time(df, names)
        data = country_medal_count.to_dict(orient='records')
        return data
    except Exception as e:
        logging.error(f"Error in dictere function: {e}")

def country_wise_medal(country):
    try:
        country_medal_count = preprocess.countries_medal(df, country)
        data = country_medal_count.to_dict(orient='records')
        return data
    except Exception as e:
        logging.error(f"Error in dictere function: {e}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        years = sorted(df['Year'].unique().tolist())
        years.insert(0, 'Overall')
        countries = sorted(df['region'].dropna().unique().tolist())
        countries.insert(0, 'Overall')
        return templates.TemplateResponse('index.html', {'request': request, 'years': years, 'countries': countries})
    except Exception as e:
        logging.error(f"Error in index route: {e}")

@app.get("/medal_tally", response_class=HTMLResponse)
async def medal_tally(request: Request):
    try:
        filtered_df = preprocess.fetch_medal_tally("Overall", "Overall")
        table_html = filtered_df.to_html(classes='table table-striped', index=True)
        years, countries = preprocess.country_year_list(df)
        return templates.TemplateResponse('medal_tally.html', {'request': request, 'years': years, 'countries': countries, 'table': table_html})
    except Exception as e:
        logging.error(f"Error in medal_tally route: {e}")


@app.get("/overall_analysis", response_class=HTMLResponse)
async def overall_analysis(request: Request):
    try:
        athlets_over_time = dictere('Name')
        event_over_time = dictere('Event')
        sports_over_time = dictere('Sport')
        city_over_time = dictere('City')
        region_over_time = dictere('region')
        temp_df = preprocess.heatmap_df(df)
        
        pivot_json = temp_df.to_dict(orient='split')

        editions, cities, sports, events, athlets, nations = preprocess.top_statics(df)
        return templates.TemplateResponse('overall_analysis.html', {
            'request': request,
            'editions': editions,
            'cities': cities,
            'sports': sports,
            'events': events,
            'athlets': athlets,
            'nations': nations,
            'athlets_over_time': athlets_over_time,
            'event_over_time': event_over_time,
            'sports_over_time': sports_over_time,
            'region_over_time': region_over_time,
            'city_over_time': city_over_time,
            'table_data': pivot_json
        })
    except Exception as e:
            logging.error(f"Error in medal_tally route: {e}")


@app.get("/most_successful", response_class=HTMLResponse)
async def most_successful(request: Request):
    try:
        sports_list = df['Sport'].unique().tolist()
        sports_list.sort()
        sports_list.insert(0, 'Overall')

        dataset = preprocess.most_succesful(df, 'Overall')
        table_html = dataset.to_html(classes='table table-striped', index=True)
        vv = f'<h2> Overall Table </h2><br>{table_html}'
        return templates.TemplateResponse('most_successful.html', {'request': request, 'sports_list': sports_list, 'table': table_html})
    except Exception as e:
        logging.error(f"Error in medal_tally route: {e}")


@app.get("/countryWise", response_class=HTMLResponse)
async def countryWise(request: Request):
    try:
        # Fetch country medal data
        # country_medal_data = country_wise_medaal('India')

        country_list = df['region'].unique().tolist()
        # country_list.sort()
        country_medal_data = preprocess.countries_medal(df,'India')
        
        
        # Handle case where no data is found
        if country_medal_data is not None:
            country_medal_data = country_medal_data.to_dict(orient='records')
        else:
            country_medal_data = []  # Return an empty list if no data

        # Get the list of unique regions
        # country_list = df1['region'].dropna().unique().tolist()
        # country_list = df1['region'].dropna().unique().tolist()

        return templates.TemplateResponse('countryWise.html', {
            'request': request, 
            'country_medal_data': country_medal_data, 
            'country_list': country_list
        })
    except Exception as e:
        print(f"Error in country_wise route: {e}")
        return HTMLResponse(content=f"Error: {e}", status_code=500)


@app.post("/submit-json", response_class=JSONResponse)
async def submit_json(data: dict):
    try:
        name = data.get('name')
        print(data)
        dataset = preprocess.most_succesful(df, name)
        table_html = dataset.to_html(classes='table table-striped', index=True)
        vv = f'<h2>You Selected {name} </h2><br>{table_html}'
        return {"name": vv}
    except Exception as e:
        logging.error(f"Error in submit_json route: {e}")


# Define your route for the overall analysis submit
@app.post("/overall_analysis_submit", response_class=JSONResponse)
async def overall_analysis_submit(request: Request):
    try:
        form_data = await request.json()
        # Process form data as needed
        # Example: year = form_data.get('year')
        # Example: country = form_data.get('country')
        year = form_data.get('year')
        country = form_data.get('country')
        
        filtered_df = preprocess.fetch_medal_tally(year, country)
        table_html = filtered_df.to_html(classes='table table-striped', index=True)
        return {"status": "success", "data": table_html}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})




# Example DataFrame for demonstration
df2 = pd.DataFrame({
    'region': ['India', 'USA', 'China', 'India', 'USA', 'China'],
    'Year': [2000, 2000, 2000, 2004, 2004, 2004],
    'Medal': [10, 12, 15, 20, 22, 25]
})

# Route to handle the update request for a specific country
@app.post("/update_graph")
async def update_graph(request: Request):
    try:
        # Get the country name from the request
        body = await request.json()
        country = body.get("country")
        print('country----------------',country)
        # Fetch the data for the given country
        country_data = df[df['region'] == country]
        c_data = preprocess.countries_medal(df,country)

        if country_data.empty:
            return JSONResponse(content={"error": f"No data found for {country}"}, status_code=404)

        # Convert the data to a list of dictionaries for JSON response
        # result = country_data.to_dict(orient='records')
        result = c_data.to_dict(orient='records')
        # print(result)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    





@app.get("/heatmap_data")
async def heatmap_data(request: Request):
    try:
        # Prepare your data for the heatmap
        # Example: Pivot data for heatmap
        body = await request.json()
        print(body)
        heatmap_df = preprocess.heatmap_countries_game(df,'India')
        heatmap_data = heatmap_df.to_dict(orient='split')
        print(heatmap_data)
        return JSONResponse(content=heatmap_data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == '__main__':
    import uvicorn
    # uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
    port = int(os.getenv("PORT", 8000))  # Use PORT env variable, default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
