from config import config, models
import os

# Function to create directories
def create_directories(config, models):
    # Create main directories from config
    main_directories = [
        config['dir_data_processed'],
        config['dir_data_raw'],
        config['dir_output'],
        config['dir_temp']
    ]
    
    for directory in main_directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory created: {directory}")
        else:
            print(f"Directory already exists: {directory}")

    # Create directories for each model in the config file
    for model, details in models.items():
        model_dir = details['data_path']
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
            print(f"Model directory created: {model_dir}")
        else:
            print(f"Model directory already exists: {model_dir}")

# Call the function with your config settings
create_directories(config, models)
