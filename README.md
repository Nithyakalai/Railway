# RailOps - Railway Operational Management System

A web-based railway management system for passengers and employees. Normalized database schema design, authentication, reservation management and backend integration using Flask and SQLite.

## Features

- Passenger: Search trains, book tickets, view reservations
- Employee: View profile, role details, and assigned trains
- Role-based login (Passenger / Employee)

## Tech Stack

- **Backend**: Python, Flask, SQLite
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Templating**: Jinja2

## Project Structure

```
Railway/
├── backend/
│   ├── app.py          # Flask routes and logic
│   └── seed_data.py    # Database schema and seed data
└── frontend/
    ├── static/         # CSS and JS
    └── templates/      # HTML templates
```
