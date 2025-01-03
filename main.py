import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.transform_utils import transform_image
from app.config import Configuration
from app.forms.classification_form import ClassificationForm
from app.ml.classification_utils import classify_image
from app.utils import list_images


app = FastAPI()
config = Configuration()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/info")
def info() -> dict[str, list[str]]:
    """Returns a dictionary with the list of models and
    the list of available image files."""
    list_of_images = list_images()
    list_of_models = Configuration.models
    data = {"models": list_of_models, "images": list_of_images}
    return data


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """The home page of the service."""
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/classifications")
def create_classify(request: Request):
    return templates.TemplateResponse(
        "classification_select.html",
        {"request": request, "images": list_images(), "models": Configuration.models},
    )


@app.post("/classifications")
async def request_classification(request: Request):
    form = ClassificationForm(request)
    await form.load_data()
    image_id = form.image_id
    model_id = form.model_id
    classification_scores = classify_image(model_id=model_id, img_id=image_id)
    return templates.TemplateResponse(
        "classification_output.html",
        {
            "request": request,
            "image_id": image_id,
            "classification_scores": json.dumps(classification_scores),
        },
    )

# New feature: Image Transformation
@app.get("/transform", response_class=HTMLResponse)
def transform_form(request: Request):
    """
    Renders a form to select an image and specify transformation parameters.
    """
    return templates.TemplateResponse(
        "transform_select.html", {"request": request, "images": list_images()}
    )

@app.post("/transform")
async def transform_post(
    request: Request,
    image_id: str = Form(...),
    brightness: float = Form(1.0),
    contrast: float = Form(1.0),
    color: float = Form(1.0),
    sharpness: float = Form(1.0),
):
    """
    Handles the POST request for applying image transformations.
    Delegates processing to the `transform_image` function.
    """
    # Call the helper function to apply transformations
    transformed_image_url = transform_image(
        image_id=image_id,
        brightness=brightness,
        contrast=contrast,
        color=color,
        sharpness=sharpness,
    )

    # Return the result page with the transformed image
    return templates.TemplateResponse(
        "transform_output.html",
        {
            "request": request,
            "image_id": image_id,
            "transformed_image_url": transformed_image_url,
        },
    )