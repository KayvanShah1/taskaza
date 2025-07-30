from fastapi import APIRouter

router = APIRouter()


@router.post("/signup")
def signup():
    pass


@router.post("/token")
def login():
    pass
