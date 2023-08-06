from pydantic import BaseModel

# Mockup class

class RegisterData(BaseModel):
    permission : int = 1
    email : str
    firstname : str
    surname : str
    password : str

class LoginData(BaseModel):
    email : str
    password : str

class adminLoginData(BaseModel):
    email : str
    password : str

class BillData(BaseModel):
    course_id : int
    bill_total : int

class CourseData(BaseModel):
    c_name : str
    c_price : int
    c_description : str
    c_video : bytes
    c_open : int = 1

class Question(BaseModel):
    q_name : str
    q : str
    a1 : str
    a2 : str
    a3 : str
    a4 : str
    correct_answer : str
    course_id : int

class Questions(BaseModel):
    questions : list[dict]

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
    source_id : str

class userCredentialData(BaseModel):
    user_email : str

class Updatedata(BaseModel):
    firstname : str
    surname : str
    email : str

class CourseControl(BaseModel):
    course_id : int
    course_open : int

class Charge(BaseModel):
    charge_id : str
    course_id : int
    user_email : str
    amount : int

class UpdateQuizdata(BaseModel):
    question_id : int
    q_name : str
    a1 : str
    a2 : str
    a3 : str
    a4 : str
    correct_answer : str
class EditCoursedata(BaseModel):
    course_id : int
    course_name : str
    course_price : int
    course_descript : str