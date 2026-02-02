# API Reference

This project uses [FastAPI](https://fastapi.tiangolo.com/), which automatically generates internal documentation using the OpenAPI standard.

## Interactive Documentation

When the server is running locally (e.g., at `http://localhost:8000`), you can access:

- **Swagger UI**: [`http://localhost:8000/docs`](http://localhost:8000/docs)  
  *Recommended for testing endpoints interactively.*

- **ReDoc**: [`http://localhost:8000/redoc`](http://localhost:8000/redoc)  
  *Alternative, more readable documentation format.*

## API Resources (v1)

The API is organized into several key resources. All endpoints are prefixed with `/api/v1` by default.

### 🔐 Authentication (`/auth`)
- Login and token management.
- Uses Firebase Authentication integration.

### 🤖 Bots (`/bots`)
- Manage bot instances.
- Connect instances to the n8n webhook hub.
- Retrieve instance status.

### 📅 Appointments (`/appointments`)
- **Booking**: Schedule new appointments.
- **Availability**: Check available slots based on business hours.
- **Management**: List upcoming appointments for contacts.

### 🏢 Business Hours (`/business-hours`)
- Configure operating hours for the system.
- Defines when appointments can be scheduled.

### 🚫 Blocked Periods (`/blocked-periods`)
- Manage specific dates or times when appointments cannot be booked (e.g., holidays, breaks).

### 👥 Contacts (`/contacts`)
- Create and manage customer profiles.
- Retrieve contact history and details.

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Request succeeded.
- `201 Created`: Resource successfully created.
- `400 Bad Request`: Invalid input or validation error.
- `401 Unauthorized`: Authentication missing or invalid.
- `403 Forbidden`: Authenticated but not authorized to perform the action.
- `404 Not Found`: Resource does not exist.
- `500 Internal Server Error`: Server-side issue.

Errors typically return a JSON body with a `detail` message explaining the issue.
