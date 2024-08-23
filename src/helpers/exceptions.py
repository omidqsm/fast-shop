from fastapi import HTTPException, status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)

entity_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="entity not found",
)

access_forbidden_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="access forbidden",
)