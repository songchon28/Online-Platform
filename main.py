from fastapi import FastAPI, Request, status
import uvicorn
from data_models import *
from db_manager import *
from cryptography.fernet import Fernet
import omise
import logging, sys
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

origins = [
    "*"
]
#from time import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=[""],
    expose_headers=["*"]
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

@app.get("/")
async def root():
    return {'message': 'Test'}

@app.post('/register/')
async def register(data: RegisterData) -> dict:
    
    db_manager = CRUD('db.sqlite')
    with open('key.pem', 'r') as key_file:
        key = key_file.readline()
    cipher = Fernet(key)
    db_manager.insert(f'INSERT INTO User VALUES("{data.permission}", "{data.email}", "{cipher.encrypt(data.firstname.encode())}", "{cipher.encrypt(data.surname.encode())}", "{cipher.encrypt(data.password.encode())}")')
    return {
        'status': 'Successful'
    }

@app.post('/login/')
async def login(data: LoginData) -> dict:
    db_manager = CRUD('db.sqlite')
    result = db_manager.login_read(f''' SELECT user_password FROM User WHERE user_email = "{data.email}"''', data.password)
    if result:
        return {'message' : 'Log in completed!'}
    else :
        return {'message' : 'The user is not existed or the password or email is incorrect!'}

@app.post('/course/')
async def course(data: CourseData) -> dict:
    db_manager = CRUD('db.sqlite')
    db_manager.insert(f'''INSERT INTO Course (course_name, course_price, course_descript, course_video) VALUES ("{data.c_name}", "{data.c_price}", "{data.c_description}", "{data.c_video}")''')
    return{
        'status': 'Successful'
    }

@app.post('/question/')
async def question(data: Question) -> dict:
    db_manager = CRUD('db.sqlite')
    db_manager.insert(f'''INSERT INTO Question 
                               (question_name, question_title, question_ans1, question_ans2, question_ans3, question_ans4, question_correct) 
                        VALUES ("{data.q_name}", "{data.q}", "{data.a1}", "{data.a2}", "{data.a3}", "{data.a4}", "{data.correct_answer}")''')
    return {
        'status': 'Successful'
    }

@app.post('/bill/')
async def bill(data: BillData) -> dict:
    db_manager = CRUD('db.sqlite')
    db_manager.insert(f'INSERT INTO Bill (course_id, bill_total) VALUES("{data.course_id}", "{data.bill_total}")')
    return {
        'status': 'Successful'
    }

@app.post('/billm2m/')
async def billm2m(data: BillM2M) -> dict:
    db_manager = CRUD('db.sqlite')
    db_manager.insert(f'INSERT INTO Bill_M2M VALUES("{data.bill_id}", "{data.user_email}")')
    return data

@app.post('/coursem2m/')
async def coursem2m(data: CourseM2M) -> dict:
    db_manager = CRUD('db.sqlite')
    db_manager.insert(f'INSERT INTO Course_M2M VALUES("{data.course_id}", "{data.user_email}")')
    return data

@app.post('/qrpay/')
async def qrpay(data: Qrpay) -> dict:
    db_manager = CRUD('db.sqlite')
    db_manager.insert(f'INSERT INTO Bill(course_id, bill_total) VALUES("{data.course_id}", "{data.amount}")')
    bill_data = db_manager.read('SELECT bill_id FROM Bill') #[1, 2, 3, 4, 5]
    bill_id = bill_data[-1] # Want the last one -> index -1 (last)
    db_manager.insert(f'INSERT INTO Course_M2M VALUES("{data.course_id}", "{data.user_email}")')
    db_manager.insert(f'INSERT INTO Bill_M2M VALUES("{bill_id}", "{data.user_email}")')
    return data

@app.get('/userGet/')
async def userGetData():
    db_manager = CRUD('db.sqlite')
    result = db_manager.read(f'SELECT * FROM User')
    return result

@app.get('/userData/')
async def getUserData(data: userCredentialData):
    db_manager = CRUD('db.sqlite')
    result = db_manager.read(f'SELECT * FROM User WHERE user_email = "{data.user_email}"')
    courses = db_manager.read(f'''
    SELECT course_id FROM Course_M2M WHERE user_email = "{data.user_email}"
    ''')
    course_data = {}
    for course_id in courses:
        course_data[course_id] = db_manager.read(f'''
    SELECT * FROM Course WHERE course_id = {course_id}
    ''')
        
    '''
    {
        1: 
            {
                'course_name': 'sldka;ldkas;dkl;asd',
                'course_price': 169.00
            }
    }
    '''
    courses_name = []
    for key, value in course_data.items():
        courses_name.append(value['course_name'])
    if result:
        return {
            'status': 'Successful',
            'data': {
                'email': f'{result[1]}',
                'fname': f'{result[2]}',
                'lname': f'{result[3]}',
                'courses': courses_name
            }
        }
    return {
            'status': 'Failed',
            'data': {
                'message': 'User is not found in the database!'
            }
        }


# @app.post('/register/')
# async def register(data: RegisterData) -> dict:
    
#     db_manager = CRUD('db.sqlite')
#     with open('key.pem', 'r') as key_file:
#         key = key_file.readline()
#     cipher = Fernet(key)
#     db_manager.insert(f'INSERT INTO User VALUES(1, {"dad@gmail.com"}, {"Forname"}, {"Forlastname"}, {"Forapss123"})')
#     return {
#         'status': 'Successful'
#     }

if __name__ == '__main__':
    uvicorn.run(app)