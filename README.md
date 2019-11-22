# -Project-mongodb-geospatial-queries-

A.Introduction 

The project is about finding the right location for our gaming company based on a series of initial criteria. 

Out of the given initial criteria I have choosen the following:

- Developers like to be near successful tech startups that have raised at least 1 Million dollars. I have 
- Executives like Starbucks A LOT. Ensure there's a starbucks not to far. Criteria is at least at 500 meters.
- Account managers need to travel a lot. Find airports close to the office. Criteria is at least 30 km from office

- The CEO is Vegan. Find vengan restaurants close the office. Criteria is at least at 1 km from office.

We have been given a MongoDB based on Crunchbase data of over 17.000 companies around the world.

I have decided to approach the project by finding the city where to locate the office and base my gaming company office in the existing office where a successful company already exists based on additional criteria plus narrow the search with initial criteria. 

B. Structure of folders

SRC. Folders with code

Main.py execute code and gives the name of company and its location where you will place your offices as well

Output map of location

C. Development of project

I have divided the project in three steps. 

First step. 

Utilize the API of YELP to get information about location for vegan restaurants, airports and Starbucks in the area of San Francisco

Information about first step in folder SCR and in file YELP.apy

Second step 

To find out the city where the company will be placed I have define successful a company as a company that has not been deadpooled already, has at least 50 employees and total funding is equal or more than 1 Million USD

I have filtered the initial Crunchbase list removing companies which did not match the selection. I have counted the amount of companies for each city that were not removed and San Francisco resulted in the winner

Once I know the city is San Francisco and the companies which fullfill successful criteria, I will use a geoquery with near, max distance and SON to put a one or a cero for the companies which did or did not match the initial criteria for Starbucks, airports and vegan restaurants. By weighting with ones or ceros and sum the results, I will then try to find the selected location

Information about first step is in folder SCR and in file Mongo.apy

Third step. 

Since with weighting exercise may not solve having one company office with more points than the rest, to resolve potential 'ties' I have utilized number of employees to use the offices of the company with more employees 

Information about third step is in Mongo.apy, visualization of where the office is located as well as weighting exercise is in a visualization jupyter notebook file.

A file with a map where the office is located in SanFran is in folder output

D. Execution of project

In terminal you can call main.py with python3 -m main and it will come with the name of company and coordinates
In visualization you can check some parts of the intermediate results and also the map with follium
In output folder I hosted a picture of the map 
