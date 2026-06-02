# API Reference

## Base URL
```
http://localhost:8000/api/
Production: https://your-domain.com/api/
```

## Authentication

All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 429 Too Many Requests
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Pagination

List endpoints support pagination:
```
GET /api/papers/?page=1&page_size=20
```

Response:
```json
{
  "count": 145,
  "next": "http://api.example.com/papers/?page=2",
  "previous": null,
  "results": [...]
}
```

## Filtering

### Papers
- `visibility`: private, peer_review, institution, public
- `status`: draft, published, peer_review, archived
- `researcher`: researcher ID
- `search`: full-text search on title, abstract, keywords

Example:
```
GET /api/papers/?visibility=public&status=published&search=quantum
```

### Datasets
- `visibility`: private, peer_review, public
- `status`: draft, published, deprecated
- `file_format`: CSV, JSON, HDF5, etc.
- `researcher`: researcher ID

## Ordering

Papers support ordering:
```
GET /api/papers/?ordering=-publication_date
GET /api/papers/?ordering=created_at
```

## Field-Level Access Control

Responses vary by user tier:

### Unauthenticated
- `abstract` ✓
- `pdf_file` ✗
- `raw_data_file` ✗

### Basic Tier
- `abstract` ✓
- `pdf_file` ✓
- `raw_data_file` ✗

### Premium Tier
- `abstract` ✓
- `pdf_file` ✓
- `raw_data_file` ✓ (with permission)

### Admin Tier
- All fields ✓
