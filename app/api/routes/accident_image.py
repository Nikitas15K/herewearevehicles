# @router.post("/new")
# async def create_new_accident_image(user_id: int = Form(...),
#  accident_id:  int = Form(...),
#  image: UploadFile = File(...),
#  current_user: UserPublic = Depends(get_current_active_user),
#  accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
#     ) -> Accident_Image_Public:

#     accident_stmt = await accident_stmt_repo.get_accident_statement_by_accident_id_user_id(accident_id= accident_id, user_id = current_user.id)
#     if not accident_stmt:
#         raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You can not add image")
#     contentsImage = await image.read()
#     new_accident_image = Accident_Image_Create(statement_id=accident_stmt.id, image = contentsImage)
#     accident_image = await accident_stmt_repo.create_new_accident_image(new_accident_image = new_accident_image)
#     return accident_image

# @router.post("/accident_sketch/add/{accident_id}",response_model=Accident_Sketch_Public, name="accident:add-sketch", status_code=HTTP_201_CREATED)
# async def create_new_accident_sketch(
#     accident_id: int,
#     new_accident_sketch: Accident_Sketch_Create = Body(..., embed=True),
#     current_user: UserPublic = Depends(get_current_active_user),
#     sketch_repo: AccidentSketchRepository = Depends(get_repository(AccidentSketchRepository)),
#     accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
#     ) -> Accident_Sketch_Public:
  

#     created_sketch = await sketch_repo.create_new_accident_sketch(new_accident_sketch=new_accident_sketch, statement_id= accident_stmt.id)
#     return created_sketch
