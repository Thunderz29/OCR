import cv2


def preprocess_image(image_path):

    image = cv2.imread(image_path)

    # grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # resize 2x
    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    output_path = image_path.replace(".", "_processed.")

    cv2.imwrite(output_path, gray)

    return output_path