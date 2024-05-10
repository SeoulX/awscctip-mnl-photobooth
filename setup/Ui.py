import os
from PIL import Image

def process_image(input_image_path, template_image_path, output_image_path):

    # Load images
    original_img = Image.open(input_image_path)
    template_img = Image.open(template_image_path)

    # Resize template if needed
    template_img = template_img.resize(original_img.size)

    # Create a mask from the template (assuming the background is white)
    mask = template_img.convert('L').point(lambda p: 255 if p > 128 else 0)  # Modified mask

    # Correctly paste the template as foreground
    original_img.paste(template_img, (0, 0), mask) 

    # Save edited image 
    original_img.save(output_image_path, format="PNG")

if __name__ == "__main__":
    input_image = "images/capture.png"  # Replace with your input image
    template_image = "images/background (1).png"  # Replace with your template
    output_image = "C:/Users/Drian/Desktop/Final_InfoSec/images/output.png"  # Replace with desired output path

    process_image(input_image, template_image, output_image)
