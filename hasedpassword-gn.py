from app.utils.security import hash_password

new_password = "1010"
hashed_password = hash_password(new_password)
print(hashed_password)

# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# hashed = "$2b$12$GcSQVPeDXzpLv7H3/pgKDuKKcP06DzVIXLcDwftmnM3Q8jyicWM46"

# # Try checking against possible plain passwords:
# print(pwd_context.verify("`\m.g=;f?_x,", "$2b$12$9obuvM7nCTaezmJJVybqyuETslXUSxqRN.fvEPsKN0s9nEoWXWw7W"))  # replace with actual guess
