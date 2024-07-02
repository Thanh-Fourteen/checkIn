from Final1.detection import functions
import os

if __name__ == "__main__":
    folder = "D:\\FPT\\AI\\9.5 AI\\Check In\\Final1"
    f = functions(folder)
    f.warmup()

    ## Save features in database
    # directory = os.path.join(folder, 'img')
    # f.process_images_from_directory(directory)

    img_path = os.path.join(folder, "my_image.png")
    f.Recognition(img_path)
    print("Done!")