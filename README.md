# Posio

Show visitors geolocation on a leaflet map and update them using Flask-SocketIO.

Visit [https://map.abrenaut.com/](https://map.abrenaut.com/) for a live demo.
    
## Developing

To download the project:

    git clone https://github.com/abrenaut/posio.git
    cd posio
    
To download dependencies:
    
    python setup.py install
    
Mapbox tokens are stored in a config.py file in the root folder. Example config.py file:
    
    DEBUG = True    
    MAPBOX_TOKEN = 'token'
    MAPBOX_ID = 'id'

   
To run the application :
    
    python run.py

## Features

* Show your location and the one of other users on a leaflet map
* Send updates to users location through a web socket