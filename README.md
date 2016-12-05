# data_serve

A lightweight app for serving images and spectra over a RESTful API with a simple data-viewing page

First, run the backend:
```
export FLASK_APP=./rest-api/server.py
flask run --host=0.0.0.0 --port=9414
```

Then, start the frontend:
```
cd frontend
npm install
npm run dev
```
