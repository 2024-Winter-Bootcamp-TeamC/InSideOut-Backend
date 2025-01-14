import io
from PIL import Image, ImageOps
from fastapi import UploadFile, HTTPException, status

# 이미지 확장자 검증
async def validate_image_type(file: UploadFile) -> UploadFile:
    if file.filename.split(".")[-1].lower() not in ["jpg", "jpeg", "png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="업로드 불가능한 이미지 확장자입니다.",
        )
    return file

# 이미지 크기 검증
async def validate_image_size(file: UploadFile) -> UploadFile:
    file_size = len(await file.read())
    if file_size > 150 * 1024 * 1024:  # 150MB 제한
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지 파일은 150MB 이하만 업로드 가능합니다.",
        )
    file.file.seek(0)  # 파일 포인터 초기화
    return file

# 이미지 크기 조정
def resize_image(file: UploadFile, max_size: int = 1024):
    try:
        read_image = Image.open(file.file)
        original_width, original_height = read_image.size

        # 크기 조정
        if original_width > max_size or original_height > max_size:
            if original_width > original_height:
                new_width = max_size
                new_height = int((new_width / original_width) * original_height)
            else:
                new_height = max_size
                new_width = int((new_height / original_height) * original_width)
            read_image = read_image.resize((new_width, new_height))

        read_image = read_image.convert("RGB")
        read_image = ImageOps.exif_transpose(read_image)

        return read_image
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미지 처리 중 오류가 발생했습니다: {str(e)}",
        )

# 파일 저장
def save_image_to_filesystem(image: Image, file_path: str):
    image.save(file_path, "jpeg", quality=70)
    return file_path
