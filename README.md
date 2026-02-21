# Photo Gallery (SSR)

## Run the application

1. **Setup:** Copy `.env.example` to `.env` and set `SECRET_KEY` (and optionally other vars). Use `uv` for dependencies:
   ```bash
   uv sync
   uv run alembic upgrade head
   ```
2. **Start server:**
   ```bash
   uv run uvicorn app.main:app --reload
   ```
3. Open http://127.0.0.1:8000

---

# Technical Specification

## 1. Project Overview

Server-side rendered (SSR) web application for managing a personal photo gallery. It focuses on secure uploads, metadata management, and sorted visualization of image data.

### Technical Stack

* **Framework:** FastAPI (Python)
* **Template Engine:** Jinja2
* **Database ORM:** SQLAlchemy
* **Migration Tool:** Alembic
* **Database:** SQLite
* **Authentication:** OAuth2 (Password bearer) with JWT.
* **Use uv for dependency management**

---

## 2. Functional Requirements

### 2.1 User Management

* **Registration:** Users can create an account with a unique username and hashed password.
* **Authentication:** Secure Login/Logout functionality.
* **Authorization:** * **Public:** Any guest can view the list of photos and open them.
* **Private:** Only logged-in users can access `POST /upload` and `DELETE /photo/{id}` endpoints.


### 2.2 Photo Management

* **Upload:**
* **Name:** Required string, maximum **40 characters**.
* **Timestamp:** Automatically generated upon upload (`YYYY-MM-DD HH:mm`).
* **File Handling:** Images are saved to a local `static/uploads` directory; the file path is stored in the database.

* **Deletion:** Authorized users can remove a photo entry and its associated file from the server.
* **View:** Clicking a list item displays the image in a dedicated view or modal.

### 2.3 Listing & Sorting

The main dashboard displays a table of photos.

* **Attributes shown:** Photo Name and Upload Date.
* **Sorting:** Users can toggle sorting via URL parameters (`?sort=name` or `?sort=date`).

---

## 3. Data Schema

The database consists of two primary tables linked by a one-to-many relationship.

| Table | Column | Type | Constraints |
| --- | --- | --- | --- |
| **Users** | `id` | Integer | Primary Key |
|  | `username` | String | Unique, Indexed |
|  | `hashed_password` | String | Not Null |
| **Photos** | `id` | Integer | Primary Key |
|  | `name` | String(40) | Not Null |
|  | `file_name` | String | Not Null |
|  | `created_at` | DateTime | Default: Now |
|  | `user_id` | Integer | Foreign Key (Users.id) |
