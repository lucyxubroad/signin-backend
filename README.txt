# confessions-ios-backend

Backend Implementation for Confessions iOS App

# Specified Routes

## 1. Get all posts: GET /api/posts

### Response on Success
```
{
  "success": True,
  "data": [
    {
      "id" 0,
      "score": 0,
      "text": "My First Post!",
      "username": "Young",
    },
    {
      "id": 1,
      "score": 0,
      "text": "My Second Post!",
      "username": "Young",
    }
  ]
}
```

## 2. Create a post: POST /api/posts

### Post Body
```
{
  "text": <USER INPUT>,
  "username": <USER INPUT>,
}
```

### Response on Success
```
{
  "success": True,
  "data": {
    "id": <ID>
    "score": 0,
    "text": <USER INPUT FOR TEXT>,
    "username": <USER INPUT FOR USERNAME>,
  }
}
```

## 3. Get a specific post: GET /api/post/{id}/
### Response on Success
```
{
  "success": True,
  "data": <POST WITH ID {id}>
} 
```

## 4. Get comments for post: GET /api/post/{id}/comments/
### Response on Success
```
{
  "success": True,
  "data":
    [
      {
        "id": 0,
        "score": 0,
        "text": "My First Comment!",
        "username": "Young",
      }
    ]
}
```

## 5. Post a comment: POST /api/post/{id}/comment/
### Post Body
```
{
  "text": <USER INPUT>,
  "username": <USER INPUT>,
}
```

### Response on Success
```
{
  "success": true,
  "data": {
    "id": <ID>,
    "score": 0,
    "text": <USER INPUT FOR TEXT>,
    "username": <USER INPUT FOR USERNAME>,
  }
}
```

## 6. Like a post: POST /api/post/{id}/vote/
### Post Body
```
{
  "vote": <true for like> 
}
```

### Response on Success
```
{
  "success": True,
  "data": <POST WITH ID {id} WHERE THE SCORE IS ADJUSTED ACCORDINGLY>
} 
```
## 7. Like a comment  POST /api/comment/{id}/vote/
### Post Body
```
{
  "vote": <true for like> 
}
```
### Response on Success
```
{
  "success": True,
  "data": <COMMENT WITH ID {id} WHERE THE SCORE IS ADJUSTED ACCORDINGLY>
} 
```
