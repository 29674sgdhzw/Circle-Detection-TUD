import matplotlib.pyplot as plt
import cv2
import os

# Input validation for the highest l value
while True:
    try:
        highest_l_value = int(input("Enter the highest value of l: "))
        if highest_l_value < 0:
            raise ValueError("Value must be non-negative.")
        break
    except ValueError as e:
        print(f"Invalid input: {e}. Please enter a valid integer.")

# Input validation for crop dimensions
while True:
    try:
        desired_width = int(input("Enter the desired width (pixels) for cropping: "))
        desired_height = int(input("Enter the desired height (pixels) for cropping: "))
        if desired_width <= 0 or desired_height <= 0:
            raise ValueError("Width and height must be positive integers.")
        break
    except ValueError as e:
        print(f"Invalid input: {e}. Please enter valid positive integers.")

# Calculate the range of l values
l_range = range(-highest_l_value, highest_l_value + 1)

# Define the paths
image_path = (r'C:\Users\chauh\Documents\SCRIPTIE\18-09-2024 Manual'
              r'\OAM beam\l={}.bmp')
output_path = (r'C:\Users\chauh\Documents\SCRIPTIE\18-09-2024 Manual'
               r'\Results\OAM beam')
base_directory = (r'C:\Users\chauh\Documents\SCRIPTIE\18-09-2024 Manual'
                  r'\Interference')
output_directory = (r'C:\Users\chauh\Documents\SCRIPTIE\18-09-2024 Manual'
                    r'\Results\Interference')

# Initialize variables to store bounding box coordinates
x_min = float('inf')
x_max = float('-inf')
y_min = float('inf')
y_max = float('-inf')

# Load the image with the highest l value
image = cv2.imread(image_path.format(highest_l_value), cv2.IMREAD_GRAYSCALE)
if image is None:
    print(f"Error: Image for l={highest_l_value} could not be loaded. Check the file path.")
else:
    # Generate threshold values from 0 to 250 in steps of 10
    threshold_values = list(range(0, 251, 10))
    print(f"Threshold values: {threshold_values}")
    
    # Prepare to store results for each threshold value
    circle_centers = []
    circle_radii = []

    for threshold_value in threshold_values:
        # Apply the threshold
        _, binary_image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            print(f"No contours found for threshold {threshold_value}.")
            continue

        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        max_contour = contours[0]

        (x, y), radius = cv2.minEnclosingCircle(max_contour)
        circle_centers.append((int(x), int(y)))
        circle_radii.append(int(radius))

        # Mark the detected circle
        marked_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        cv2.circle(marked_image, (int(x), int(y)), int(radius), (0, 0, 255), 2)
        
        plt.imshow(marked_image)
        plt.axis('off')
        plt.title(f"Threshold = {threshold_value}")
        plt.show()

        # Prompt user to select a threshold value based on the detected circles
    while True:
        print("Detected circles:")
        for i, threshold_value in enumerate(threshold_values):
            print(f"Threshold = {threshold_value}")
    
        print("Select a threshold value from the above options or type 'no' to proceed with manual cropping.")
        
        user_input = input(f"Select a threshold value from {threshold_values} or type 'no': ").strip().lower()
        
        if user_input == 'no':
            print("Proceeding to manual cropping...")
            break
        else:
            try:
                selected_threshold = int(user_input)
                if selected_threshold in threshold_values:
                    break
                else:
                    print(f"Invalid input. Please select a threshold value from {threshold_values} or type 'no'.")
            except ValueError:
                print("Invalid input. Please select a threshold value from {threshold_values} or type 'no'.")
    
    print(f"Using threshold value: {selected_threshold}" if selected_threshold in threshold_values else "Manual cropping will be used.")

    # Use the selected threshold for final processing
    _, binary_image = cv2.threshold(image, selected_threshold, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        print(f"No contours found in the image for l={highest_l_value}. Skipping...")
    else:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        max_contour = contours[0]

        (x, y), radius = cv2.minEnclosingCircle(max_contour)
        center = (int(x), int(y))
        radius = int(radius)

        # Mark the detected circle
        marked_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        cv2.circle(marked_image, center, radius, (0, 0, 255), 2)
        plt.imshow(marked_image)
        plt.axis('off')
        plt.title(f"Final Detection with Threshold = {selected_threshold}")
        plt.show()

        # Confirm with the user
        while True:
            user_input = input("Are you happy with the circle? (yes/no): ").strip().lower()
            if user_input in ['yes', 'no']:
                break
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

        if user_input == 'yes':
            # Bounding box coordinates based on the selected circle
            x_min = min(x_min, int(x - desired_width / 2))
            x_max = max(x_max, int(x + desired_width / 2))
            y_min = min(y_min, int(y - desired_height / 2))
            y_max = max(y_max, int(y + desired_height / 2))

            # Create the "OAM beam" folder if it doesn't exist
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            # Crop and save images with error handling
            for l in l_range:
                image = cv2.imread(image_path.format(l), cv2.IMREAD_GRAYSCALE)
                if image is None:
                    print(f"Error: Image for l={l} could not be loaded. Skipping...")
                    continue
                cropped_image = image[y_min:y_max, x_min:x_max]
                output_file = os.path.join(output_path, f'l={l}.bmp')
                try:
                    cv2.imwrite(output_file, cropped_image)
                except Exception as e:
                    print(f"Error saving image for l={l}: {e}")
                    continue

                plt.imshow(cropped_image, cmap='gray')
                plt.axis('off')
                plt.title(f"l={l}")
                plt.show()

            # Process Interference images
            for mask_num in range(5):
                mask_directory = os.path.join(base_directory, f'MASK{mask_num}')
                output_mask_directory = os.path.join(output_directory, f'MASK{mask_num}')
                if not os.path.exists(output_mask_directory):
                    os.makedirs(output_mask_directory)

                for i in l_range:
                    filename = f'l={i}.bmp'
                    input_filepath = os.path.join(mask_directory, filename)
                    if os.path.exists(input_filepath):
                        image = cv2.imread(input_filepath, cv2.IMREAD_GRAYSCALE)
                        if image is None:
                            print(f"Error reading image '{filename}' in MASK{mask_num}.")
                            continue
                        cropped_image = image[y_min:y_max, x_min:x_max]
                        output_filepath = os.path.join(output_mask_directory, filename)
                        try:
                            cv2.imwrite(output_filepath, cropped_image)
                        except Exception as e:
                            print(f"Error saving image '{filename}' in MASK{mask_num}: {e}")
                            continue

                        plt.imshow(cropped_image, cmap='gray')
                        plt.axis('off')
                        plt.title(f'MASK{mask_num} - {filename}')
                        plt.show()
                    else:
                        print(f"Image '{filename}' not found in MASK{mask_num}.")
        else:
            # Manual cropping code
                if user_input == 'no':
                    # User opted for manual cropping
                    crop_width, crop_height = desired_width, desired_height  # User-defined crop size
                    initial_image_path = image_path.format(highest_l_value)
                    image = cv2.imread(initial_image_path)
                    
                    if image is None:
                        print(f"Error: Initial image for manual cropping could not be loaded.")
                    else:
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB for Matplotlib
                
                        def draw_rectangle(event, x, y, flags, param):
                            global x_min, y_min, x_max, y_max, crop_width, crop_height, image, img_copy
                            if event == cv2.EVENT_LBUTTONDOWN:
                                x_min = max(0, x - crop_width // 2)
                                y_min = max(0, y - crop_height // 2)
                                x_max = min(image.shape[1], x + crop_width // 2)
                                y_max = min(image.shape[0], y + crop_height // 2)
                
                                # Adjust for boundaries
                                if x_min == 0:
                                    x_max = crop_width
                                if y_min == 0:
                                    y_max = crop_height
                                if x_max == image.shape[1]:
                                    x_min = image.shape[1] - crop_width
                                if y_max == image.shape[0]:
                                    y_min = image.shape[0] - crop_height
                
                                cropped_image = image[y_min:y_max, x_min:x_max]
                                plt.imshow(cropped_image)
                                plt.title(f'Cropped Image: ({x_min}, {y_min}) to ({x_max}, {y_max})')
                                plt.show()
                                print(f'Crop coordinates: ({x_min}, {y_min}) to ({x_max}, {y_max})')
                                
                                img_copy = image.copy()
                                cv2.rectangle(img_copy, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
                                cv2.imshow('image', img_copy)
                
                        cv2.namedWindow('image')
                        cv2.setMouseCallback('image', draw_rectangle)
                
                        while True:
                            cv2.imshow('image', image)
                            if cv2.waitKey(20) & 0xFF == 27:  # Press 'ESC' to exit
                                break
                
                        cv2.destroyAllWindows()
                
                        # Now, crop and save the images using manual coordinates
                        for l in l_range:
                            image = cv2.imread(image_path.format(l), cv2.IMREAD_GRAYSCALE)
                            if image is None:
                                print(f"Error: Image for l={l} could not be loaded. Skipping...")
                                continue
                
                            x_min_valid = max(0, x_min)
                            y_min_valid = max(0, y_min)
                            x_max_valid = min(image.shape[1], x_max)
                            y_max_valid = min(image.shape[0], y_max)
                
                            cropped_image = image[y_min_valid:y_max_valid, x_min_valid:x_max_valid]
                            output_file = os.path.join(output_path, f'l={l}.bmp')
                            cv2.imwrite(output_file, cropped_image)
                            plt.imshow(cropped_image, cmap='gray')
                            plt.axis('off')
                            plt.title(f'l={l}')
                            plt.show()
                
                        for mask_num in range(5):
                            mask_directory = os.path.join(base_directory, f'MASK{mask_num}')
                            output_mask_directory = os.path.join(output_directory, f'MASK{mask_num}')
                            if not os.path.exists(output_mask_directory):
                                os.makedirs(output_mask_directory)
                
                            for i in l_range:
                                filename = f'l={i}.bmp'
                                input_filepath = os.path.join(mask_directory, filename)
                                if os.path.exists(input_filepath):
                                    image = cv2.imread(input_filepath, cv2.IMREAD_GRAYSCALE)
                                    if image is None:
                                        print(f"Error reading image '{filename}' in MASK{mask_num}.")
                                        continue
                                    
                                    cropped_image = image[y_min_valid:y_max_valid, x_min_valid:x_max_valid]
                                    output_filepath = os.path.join(output_mask_directory, filename)
                                    cv2.imwrite(output_filepath, cropped_image)
                                    plt.imshow(cropped_image, cmap='gray')
                                    plt.axis('off')
                                    plt.title(f'MASK{mask_num} - {filename}')
                                    plt.show()
                                else:
                                    print(f"Image '{filename}' not found in MASK{mask_num}.")