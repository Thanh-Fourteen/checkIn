def register(self, camera_index=0, frame_skip=30, num_images=5):
        """
        Registers a person by capturing images from a camera, analyzing them, and saving them to a database.

        Args:
            camera_index (int): Index of the camera to use.
            frame_skip (int): Number of frames to skip between captures.
            num_images (int): Number of images to capture for registration.
        """
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        captured_images = []
        frame_count = 0

        while len(captured_images) < num_images:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture image.")
                break

            if frame_count % frame_skip == 0:
                img_name = f"capture_{len(captured_images)+1}.png"
                cv2.imwrite(img_name, frame)
                captured_images.append(img_name)
                #print(f"Captured image {len(captured_images)}/{num_images}")

            frame_count += 1
            cv2.imshow('Capturing', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        person_name = input("Enter the name of the person: ")
        features_tensor = torch.tensor([]).to("cuda")
        names = []

        for img_path in captured_images:
            try:
                response = self.analyze_image(img_path)
            except:
                print(f"Don't analysis {img_path}")
                continue

            if len(response.faces) == 0:
                print(f"No faces detected in the image {img_path}.")
                continue

            features = response.faces[0].preds['verify'].logits.unsqueeze(0)
            names.append(person_name)
            features_tensor = torch.concat((features_tensor, features), dim=0)

        if len(names) > 0:
            existing_features = torch.load(self.database_path)
            features_tensor = torch.concat((existing_features, features_tensor), dim=0)
            torch.save(features_tensor, self.database_path)
            df = pd.DataFrame({'name': names})
            df.to_csv(self.name_path, mode='a', header=False, index=False)
            print("Registration completed and data saved.")
        else:
            print("No valid images captured for registration.")