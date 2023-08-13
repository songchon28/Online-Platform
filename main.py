from fastapi import FastAPI, Request, status,File, UploadFile,Form
from datetime import datetime
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
from typing import Annotated
import os

omise.api_secret = "skey_test_5tcxiqb1cmfq8ykdw3x"
omise.api_version = "2017-11-02"

origins = [
    "http://20.205.2.101:8080",
    "http://127.0.0.1:5500"
]
#from time import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    time = datetime.now()
    db_manager = CRUD('db.sqlite')
    with open('key.pem', 'r') as key_file:
        key = key_file.readline()
    cipher = Fernet(key)
    db_manager.insert(f'INSERT INTO User VALUES("{data.permission}", "{data.email}", "{cipher.encrypt(data.firstname.encode()).decode()}", "{cipher.encrypt(data.surname.encode()).decode()}", "{cipher.encrypt(data.password.encode()).decode()}","{time}")')
    return {'status': 'Successful', 'email' : f'{data.email}'}

@app.post('/login/')
async def login(data: LoginData) -> dict:
    db_manager = CRUD('db.sqlite')
    with open('key.pem', 'r') as key_file:
        key = key_file.readline()
    cipher = Fernet(key)
    result = db_manager.read(f'SELECT * FROM User WHERE user_email = "{data.email}"')
    # return {
    #     'status' : 'Succesful'
    # }
    if result:
        if data.password == cipher.decrypt(result[0][4]).decode():
            
         # For testing only and Don't forget to delete it!!!
            return {'message' : 'Login completed!', 'email' : {data.email}}
        
    return {'message' : 'The user is not existed or the password or email is incorrect!'}

@app.post('/adminLogin/')
async def login(data: adminLoginData) -> dict:
    db_manager = CRUD('db.sqlite')
    with open('key.pem', 'r') as key_file:
        key = key_file.readline()
    cipher = Fernet(key)

    result = db_manager.read(f'SELECT * FROM User WHERE user_email = "{data.email}"')
    if result:
        if data.password == cipher.decrypt(result[0][4]).decode() and result[0][0] == 0:

            return {'message' : 'Login completed!', 'email' : {data.email}}

    return {'message' : 'The user is not existed or the password or email is incorrect!'}

@app.post('/course/')
async def course(filevideo: Annotated[bytes, File()], fileimage: Annotated[bytes, File()], c_name: Annotated[str, Form()], c_price: Annotated[str, Form()], c_descript: Annotated[str, Form()], c_open:Annotated[str,Form()], filevideoname:Annotated[str,Form()], fileimagename:Annotated[str,Form()]):
    db_manager = CRUD('db.sqlite')

    dirname = os.path.dirname(__file__)
    headpath, tailpath = os.path.split(dirname)

    path_img = 'img/'
    relativepathimage = 'Front-End/User/img'
    fullimagepath = os.path.join(headpath, relativepathimage, fileimagename) 
    fullimagename = os.path.join(path_img,fileimagename)

    path_video = 'Video/'
    relativepath = 'Front-End/User/Video'
    fullvideopath = os.path.join(headpath, relativepath, filevideoname) 
    fullvideoname = os.path.join(path_video,filevideoname)

    db_manager.insert(f'''INSERT INTO Course (course_name, course_price, course_descript, course_video, course_open, course_image) VALUES ("{c_name}", "{c_price}", "{c_descript}", "{fullvideoname}", "{c_open}", "{fullimagename}")''')
    
    with open(fullvideopath,'wb') as vfile:
        vfile.write(filevideo)

    if fileimagename != "default.jpg" :
        with open(fullimagepath, "wb") as imagefile:
            imagefile.write(fileimage)

    return{
        'status': '200',
        'name': c_name,
        'price': c_price,
        'description': c_descript,
    }

@app.post('/question/')
async def question(data: Question) -> dict:
    db_manager = CRUD('db.sqlite')
    db_manager.insert(f'''INSERT INTO Question 
                    (question_name, question_title, question_ans1, question_ans2, question_ans3, question_ans4, question_correct, course_id) 
                    VALUES ("{data.q_name}", "{data.q}", "{data.a1}", "{data.a2}", "{data.a3}", "{data.a4}", "{data.correct_answer}", "{data.course_id}")''')
    return {
        'status': 'Successful'
    }

@app.post('/bill/')
async def bill(data: BillData) -> dict:
    time = datetime.now()
    db_manager = CRUD('db.sqlite')
    db_manager.insert(f'INSERT INTO Bill (course_id, bill_total,bill_date) VALUES("{data.course_id}", "{data.bill_total}"), "{time}")')
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
    charge = omise.Charge.create(
        amount=data.amount,
        currency="THB",
        source=data.source_id
    )
    return {
        "data":{"Qrimage" : charge.source.scannable_code.image.download_uri,
                "charge_id" : charge.id}
            }


@app.post('/userData/')
async def getUserData(data: userCredentialData):
    db_manager = CRUD('db.sqlite')
    result = db_manager.read(f'SELECT * FROM User WHERE user_email = "{data.user_email}"')
    with open('key.pem', 'r') as key_file:
        key = key_file.readline()
    cipher = Fernet(key)
    if result:
        return {
            'status': 'Successful',
            'data': {
                'email': f'{result[0][1]}',
                'fname': f'{cipher.decrypt(result[0][2]).decode()}',
                'lname': f'{cipher.decrypt(result[0][3]).decode()}',
            }
        }
    return {
            'status': 'Failed',
            'data': {
                'message': 'User is not found in the database!'
            }
        }

@app.post('/Updatedata/')
async def register(data: Updatedata) -> dict:
    db_manager = CRUD('db.sqlite')
    with open('key.pem', 'r') as key_file:
        key = key_file.readline()
    cipher = Fernet(key)
    db_manager.insert(f'UPDATE User SET user_fname = "{cipher.encrypt(data.firstname.encode()).decode()}", user_lname = "{cipher.encrypt(data.surname.encode()).decode()}" WHERE user_email = "{data.email}"')
    return{
        'status': 'Edit completed'
    }

@app.get('/GetAllUserData/')
async def getAllUser():
    db_manager = CRUD('db.sqlite')
    with open('key.pem', 'r') as key_file:
        key = key_file.readline()
    cipher = Fernet(key)
    
    result = db_manager.read(f'SELECT User.user_email,user_fname,user_lname,user_date,course_name,Course.course_id FROM User JOIN Course_M2M ON User.user_email = Course_M2M.user_email JOIN Course ON Course_M2M.course_id = Course.course_id WHERE user_priority = 1 ORDER BY user_date DESC')
    
    data = [list(data) for data in result]
    user_visited = {}
    for user in data:
        for i in range(1,3):
            
            user[i] = cipher.decrypt(user[i]).decode()

    for i in range(len(data)):
        data[i] = {
                'email': f'{data[i][0]}',
                'fname': f'{data[i][1]}',
                'lname': f'{data[i][2]}',
                'date' : f'{data[i][3]}',
                'course': f'{data[i][4]}',
                'course_id': f'{data[i][5]}'              
            }
    for i in range(len(data)):
        if data[i]['email'] in user_visited:
            data[user_visited[data[i]['email']]]['course'].append({'course_name':data[i]['course'],'course_id':data[i]['course_id']})
            data[i] = None
        else:
            data[i]['course'] = [{'course_name':data[i]['course'],'course_id':data[i]['course_id']}]
            user_visited[data[i]['email']] = i
    while None in data:
        data.remove(None)
    for item in data:
        item.pop('course_id')
    return {
            'status': 'Successful',
            'data': data
        }

@app.get('/AllCourseData/')
async def getallcourse():
    db_manager = CRUD('db.sqlite')

    result = db_manager.read(f'SELECT course_id, course_name, course_price, course_descript, course_open FROM Course ORDER BY course_id DESC')
    data = [list(data) for data in result]
    for i in range(len(data)):
        data[i] = {
                'course_id': f'{data[i][0]}',
                'course_name': f'{data[i][1]}',
                'course_price': f'{data[i][2]}',
                'course_descript': f'{data[i][3]}',
                'course_open': f'{data[i][4]}'

            }
    return {
            'status': 'Successful',
            'data': data,
        }

@app.get('/AllQuestionData/')
async def getallquestion():
    db_manager = CRUD('db.sqlite')
    result = db_manager.read(f'SELECT question_name,Question.course_id,course_name FROM Question JOIN Course ON Question.course_id =  Course.course_id ORDER BY Course.course_id DESC')
    counts = {}
    order = []
    data = [list(data) for data in result]
    for i in range(len(data)):
        course_id = data[i][1]
        if course_id in counts:
            counts[course_id] += 1
        else:
            counts[course_id] = 1
    
    for i in range(len(data)):
        if data[i][1] not in order:
            order.append(data[i][1])

        

    for i in range(len(data)):
        data[i] = {
                'question_name': f'{data[i][0]}',
                'course_id' :f'{data[i][1]}',
                'course_name' : f'{data[i][2]}'
            }

    return {
            'status': 'Successful',
            'data': data,
            'count' : counts,
            'order' : order
        }

@app.get('/AllBillData/')
async def getallbill():
    db_manager = CRUD('db.sqlite')
    result = db_manager.read(f'SELECT bill_id, Bill.course_id, bill_total, bill_date, course_name FROM Bill JOIN Course ON Bill.course_id =  Course.course_id ORDER BY bill_date DESC')

    data = [list(data) for data in result]
    date_counts = {}
    
    
    for i in range(len(data)):
        total = 0
        total_course = 0
        d = datetime.fromisoformat(data[i][3]).date()
        course_count = {}
        for j in range(len(data)):
            if d == datetime.fromisoformat(data[j][3]).date():
                i +=1
                total += data[j][2]
                total_course += 1
                if data[j][1] in course_count:
                    course_count[data[j][1]]['count'] += 1
                else:
                    course_count[data[j][1]] = {'course_name': f'{data[j][4]}','count':1}
        date_counts[d] = {}
        date_counts[d]['course'] = course_count
        date_counts[d]['bill_total'] = total
        date_counts[d]['course_total']  = total_course
    for i in range(len(data)):
        data[i] = {
                    'bill_id': f'{data[i][0]}',
                    'course_id': f'{data[i][1]}',
                    'bill_total': f'{data[i][2]}',
                    'bill_date' : f'{data[i][3]}',
                    'course_name': f'{data[i][4]}'


            }
    return {
            'status': 'Successful',
            'data': data,
            'course_count' : date_counts
        }

@app.post('/Updatecourse/')
async def updatecourse(data: CourseControl) -> dict:
    db_manager = CRUD('db.sqlite')
    db_manager.insert(f'UPDATE Course SET course_open = "{data.course_open}" WHERE course_id = "{data.course_id}"')
    return{
        'status': 'Edit completed'
    }

@app.get('/CheckQuizCourse/')
async def getallcourse():
    db_manager = CRUD('db.sqlite')

    result = db_manager.read(f'SELECT course_id,course_name FROM Course WHERE NOT EXISTS (SELECT course_id FROM Question WHERE Question.course_id = Course.course_id)')

    data = [list(data) for data in result]
    for i in range(len(data)):
        data[i] = {
                'course_id': f'{data[i][0]}',
                'course_name': f'{data[i][1]}'

            }
    return {
            'status': 'Successful',
            'data': data
        }

@app.get('/ShowCourseOpen/')
async def showcourse():
    db_manager = CRUD('db.sqlite')

    result = db_manager.read(f'SELECT course_id, course_name, course_price, course_descript, course_image FROM Course WHERE course_open = 1 ORDER BY course_id DESC')

    data = [list(data) for data in result]
    for i in range(len(data)):
        data[i] = {
                'course_id': f'{data[i][0]}',
                'course_name': f'{data[i][1]}',
                'course_price': f'{data[i][2]}',
                'course_descript': f'{data[i][3]}',
                'course_image': f'{data[i][4]}'
            }
    return {
            'status': 'Successful',
            'data': data
        }

@app.get('/ShowCourseVideo/{course_id}')
async def Showvideo(course_id : int):
    db_manager = CRUD('db.sqlite')
    result = db_manager.read(f'SELECT course_id,course_name , course_video , course_price ,course_descript FROM Course WHERE course_id = "{course_id}"')
    data = {
            'course_id': f'{result[0][0]}',
            'course_name': f'{result[0][1]}',
            'course_video': f'{result[0][2]}', 
            'course_price': f'{result[0][3]}',
            'course_descript': f'{result[0][4]}'
            }
    return{
        'data': data,
    }

@app.get('/whopaythiscourse/{course_id}')
async def whopay(course_id : int):
    db_manager = CRUD('db.sqlite')
    c_data = db_manager.read(f'SELECT course_id,user_email FROM Course_M2M WHERE course_id = "{course_id}"')
    c_open = [list(c_open) for c_open in c_data]
    for i in range(len(c_open)):
         c_open[i] = {
                 'course_id':f'{c_data[i][0]}',
                 'user_email': f'{c_data[i][1]}'
         }
    
    return{
        'c_open': c_open
    }
@app.get('/CourseHaveQuiz/{course_id}')
async def coursequiz(course_id : int):
    db_manager = CRUD('db.sqlite')

    result = db_manager.read(f'SELECT course_id,course_name FROM Course WHERE EXISTS (SELECT course_id FROM Question WHERE Question.course_id = "{course_id}")')

    if result:
        return {
            'have_quiz': 'true'
        }
    else : 
        return{
            'have_quiz': 'false'
    }

@app.get('/ShowCourseTest/{course_id}')
async def Showtest(course_id : int):
    db_manager = CRUD('db.sqlite')
    result = db_manager.read(f'SELECT question_title, question_ans1, question_ans2, question_ans3, question_ans4, question_correct FROM Question WHERE course_id = "{course_id}"')
    data = [list(data) for data in result]
    for i in range(len(data)):
        data[i] = {
                'question_title': f'{data[i][0]}',
                'question_ans1': f'{data[i][1]}', 
                'question_ans2': f'{data[i][2]}',
                'question_ans3': f'{data[i][3]}',
                'question_ans4': f'{data[i][4]}',
                'question_correct': f'{data[i][5]}'
            }
    return{
        'data': data,
    }

@app.post('/checkpay/')
async def qrpay(data: Charge) -> dict:
    time = datetime.now()
    charge = omise.Charge.retrieve(data.charge_id)
    if charge.status == "successful":
        db_manager = CRUD('db.sqlite')
        price = data.amount/100
        db_manager.insert(f'INSERT INTO Bill(course_id, bill_total, bill_date) VALUES("{data.course_id}", "{price}","{time}")')
        bill_data = db_manager.read('SELECT bill_id FROM Bill') #[1, 2, 3, 4, 5]
        bill_read = [list(bill_read) for bill_read in bill_data]
        bill_id = bill_read[-1][0] # Want the last one -> index -1 (last)
        db_manager.insert(f'INSERT INTO Course_M2M(course_id,user_email) VALUES("{data.course_id}", "{data.user_email}")')
        db_manager.insert(f'INSERT INTO Bill_M2M(bill_id,user_email)VALUES("{bill_id}", "{data.user_email}")')
        return  {
            'status' : 'Successful'
        }
    else:
        return  {
            'status' : 'Failed'
        } 

@app.post('/UserCourse/')
async def usercourse(data: userCredentialData):
    db_manager = CRUD('db.sqlite')

    course = db_manager.read(f'SELECT course_id FROM Course_M2M WHERE user_email = "{data.user_email}"')
    bill = db_manager.read(f'SELECT bill_id FROM Bill_M2M WHERE user_email = "{data.user_email}"')
    arr_c = "("

    for item in course:
        arr_c += "'" + str(item[0]) + "'" + ","
  
    arr_c = arr_c[:-1]
    arr_c += ")"
    
    arr_b = "("
    for item in bill:
        arr_b += "'" + str(item[0]) + "'" + ","
  
    arr_b = arr_b[:-1]
    arr_b += ")"
    result = db_manager.read(f'''SELECT Course.course_id, course_name, course_price, course_descript,bill_date FROM Course 
                             JOIN Bill ON Course.course_id = Bill.course_id
                             WHERE Course.course_id in {arr_c} AND bill_id in {arr_b} ORDER BY bill_date DESC''')
    data=[]
    for i in range(len(result)):
        data.append({'course_id': f'{result[i][0]}',
                    'course_name': f'{result[i][1]}',
                    'course_price': f'{result[i][2]}',
                    'course_descript': f'{result[i][3]}',
                    'bill_date': f'{result[i][4]}'})
    return {
            'status': 'Successful',
            'data': data,
        }
@app.post('/UserBill/')
async def userbill(data: userCredentialData):
    db_manager = CRUD('db.sqlite')

    bill = db_manager.read(f'SELECT bill_id FROM Bill_M2M WHERE user_email = "{data.user_email}"')
    arr = "("

    for item in bill:
        arr += "'" + str(item[0]) + "'" + ","
  
    arr = arr[:-1]
    arr += ")"
    result = db_manager.read(f'SELECT bill_id, Bill.course_id , Course.course_name, bill_total, bill_date FROM Bill JOIN Course ON Bill.course_id =  Course.course_id WHERE bill_id IN {arr} ORDER BY bill_date DESC')
    data=[]
    for i in range(len(result)):
        data.append({'bill_id': f'{result[i][0]}',
                    'course_id': f'{result[i][1]}',
                    'course_name':f'{result[i][2]}',
                    'bill_total': f'{result[i][3]}',
                    'bill_date': f'{result[i][4]}'})
    return {
            'status': 'Successful',
            'data': data
        }
@app.get('/GetEditQuizCourse/')
async def getallcourse():
    db_manager = CRUD('db.sqlite')

    result = db_manager.read(f'SELECT Course.course_id, course_name, question_title, question_name, question_ans1, question_ans2, question_ans3, question_ans4,question_correct, question_id FROM Question JOIN Course ON Question.course_id = Course.course_id WHERE EXISTS (SELECT course_id FROM Course WHERE Course.course_id = Question.course_id)')

    data = [list(data) for data in result]

    for i in range(len(data)):
        data[i] = {
                'course_id': f'{data[i][0]}',
                'course_name' : f'{data[i][1]}',
                'question_title': f'{data[i][2]}',
                'question_name': f'{data[i][3]}',
                'question_ans1': f'{data[i][4]}',
                'question_ans2': f'{data[i][5]}',
                'question_ans3': f'{data[i][6]}',
                'question_ans4': f'{data[i][7]}',
                'question_correct': f'{data[i][8]}',
                'question_id': f'{data[i][9]}'
            }
    return {
            'status': 'Successful',
            'data': data
        }

@app.post('/EditCoursedata/')
async def editcourse(data: EditCoursedata) -> dict:
    db_manager = CRUD('db.sqlite')
    db_manager.insert(f'UPDATE Course SET course_name = "{data.course_name}", course_price = "{data.course_price}" ,course_descript = "{data.course_descript}" WHERE course_id = "{data.course_id}"')
    return{
        'status': 'Edit completed'
    }

@app.post('/UpdateQuizdata/')
async def updatequiz(data: UpdateQuizdata) -> dict:
    db_manager = CRUD('db.sqlite')
    db_manager.insert(f'UPDATE Question SET question_name = "{data.q_name}" WHERE course_id = "{data.course_id}"')
    db_manager.insert(f'UPDATE Question SET question_title = "{data.q_title}", question_ans1 = "{data.a1}" ,question_ans2 = "{data.a2}" ,question_ans3 = "{data.a3}" ,question_ans4 = "{data.a4}" ,question_correct = "{data.correct_answer}" WHERE question_id = "{data.question_id}"')
    return{
        'status': 'Edit completed'
    }
@app.delete('/DeleteCourse/{course_id}')
async def deleteCourse(course_id : int) -> dict:
    db_manager = CRUD('db.sqlite')
    db_manager.delete(f'DELETE FROM Course WHERE course_id = {course_id}')
    return{
        'message' : 'Delete Completed'
    }

if __name__ == '__main__':
    uvicorn.run(app)