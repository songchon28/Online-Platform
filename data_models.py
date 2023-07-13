from pydantic import BaseModel

# Mockup class
class MockupData(BaseModel):
    first_name : str # Not null and must be a string value
    surname : str | None = None # Could be null and expect string as an input
    age : int | None = 25 # Expect an int to be the input, but if none passed then return 25 instead of null
    salary : float # Expect float as input

class RegisterData(BaseModel):
    permission : int
    email : str
    firstname : str
    surname : str
    password : str

class LoginData(BaseModel):
    email : str
    password : str

class BillData(BaseModel):
    course_id : int
    bill_total : int

class CourseData(BaseModel):
    c_name : str
    c_price : int
    c_description : str
    c_video : str

class Question(BaseModel):
    q_name : str
    q : str
    a1 : str
    a2 : str
    a3 : str
    a4 : str
    correct_answer : str

class CourseM2M(BaseModel):
    course_id : int
    user_email: str

class BillM2M(BaseModel):
    bill_id : int
    user_email: str

class Qrpay(BaseModel):
    course_id : int
    user_email : str
    amount : int

class userCredentialData(BaseModel):
    user_email : str

