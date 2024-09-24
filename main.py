import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from fastapi.middleware.cors import CORSMiddleware
from emotion_analysis_nrc import process_text_list
from vision_api_google import detect_safe_search_uri

app = FastAPI()

origins = [
    "http://localhost:5173", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# *********************************************************************************************** #

# # FastAPI endpoint
# @app.post("/Emotion-Analysis/")
# async def process_texts(text_list: list[str]):
#     output_json = process_text_list(text_list)  # Process the input text list
#     return json.loads(output_json)  # Return the JSON response

@app.post("/Emotion-Analysis/")
async def process_texts(request: Request):
    try:
        data = await request.json()
        text_list = data.get("text_list", [])
        output_json = process_text_list(text_list)
        return JSONResponse(content=json.loads(output_json))
    except ValidationError as e:
        return JSONResponse(status_code=422, content={"detail": e.errors()})
    
@app.get("/Explicit-Image-Filter/")
async def process_image(request: Request):
    try:
        data = await request.json()
        url = data.get("url", "")
        output_json = detect_safe_search_uri(url)
        return JSONResponse(content=json.loads(output_json))
    except ValidationError as e:
        return JSONResponse(status_code=422, content={"detail": e.errors()})


# Test function
# def test_process_text_list():
#     example_text_list = [
#         "I feel very stressed out.",
#         "I feel happy and joyful today!",
#         "This is a test sentence for processing."
#     ]

#     output_json = process_text_list(example_text_list)

#     output_file_path = "output.json"
#     with open(output_file_path, "w") as json_file:
#         json_file.write(output_json)

#     print("JSON file created")

# test_process_text_list()

# *********************************************************************************************** #