from fastapi import FastAPI, HTTPException, Path, Query, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

class StudentCreateUpdate(BaseModel):
    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    age: int = Field(..., gt=0)

students = [
    {"id": 1, "code": "SV001", "name": "Nguyen Van A", "email": "a@gmail.com", "age": 20},
    {"id": 2, "code": "SV002", "name": "Tran Thi B", "email": "b@gmail.com", "age": 22},
    {"id": 3, "code": "SV003", "name": "Le Van C", "email": "c@gmail.com", "age": 18}
]

@app.get("/students")
def get_students(
    keyword: Optional[str] = Query(None),
    min_age: Optional[int] = Query(None),
    max_age: Optional[int] = Query(None)
):
    result = students.copy()
    
    if keyword:
        kw_lower = keyword.lower()
        result = [
            s for s in result 
            if kw_lower in s["name"].lower() 
            or kw_lower in s["code"].lower() 
            or kw_lower in s["email"].lower()
        ]
        
    if min_age is not None:
        result = [s for s in result if s["age"] >= min_age]
        
    if max_age is not None:
        result = [s for s in result if s["age"] <= max_age]
        
    return result

@app.get("/students/{student_id}")
def get_student_detail(student_id: int = Path(...)):
    for s in students:
        if s["id"] == student_id:
            return s
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

@app.post("/students", status_code=status.HTTP_201_CREATED)
def create_student(student_in: StudentCreateUpdate):
    for s in students:
        if s["code"] == student_in.code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã học viên đã tồn tại")
            
    new_id = max(s["id"] for s in students) + 1 if students else 1
    
    new_student = {
        "id": new_id,
        "code": student_in.code,
        "name": student_in.name,
        "email": student_in.email,
        "age": student_in.age
    }
    students.append(new_student)
    return {"message": "Thêm học viên thành công", "student": new_student}

@app.put("/students/{student_id}")
def update_student(student_in: StudentCreateUpdate, student_id: int = Path(...)):
    target_student = None
    for s in students:
        if s["id"] == student_id:
            target_student = s
            break
            
    if not target_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        
    for s in students:
        if s["code"] == student_in.code and s["id"] != student_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mã học viên đã bị trùng")
            
    target_student["code"] = student_in.code
    target_student["name"] = student_in.name
    target_student["email"] = student_in.email
    target_student["age"] = student_in.age
    
    return {"message": "Cập nhật học viên thành công", "student": target_student}

@app.delete("/students/{student_id}")
def delete_student(student_id: int = Path(...)):
    for index, s in enumerate(students):
        if s["id"] == student_id:
            students.pop(index)
            return {"message": "Xóa học viên thành công"}
            
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)