# Potato Disease Predictor  

This repository hosts the complete codebase and assets for the **Potato Disease Predictor** project, an end-to-end machine learning application that identifies the health status of potato leaves. The project is structured into four folders: `training`, `model`, `api`, and `web`, each containing essential components for development, deployment, and showcasing the application.  

## Folder Structure  

### 1. **Training**  
- **Dataset:** Contains the `PlantVillage` dataset, which is organized into three subfolders representing different classes (e.g., Early Blight, Late Blight, Healthy).  
- **Jupyter Notebook:** Includes the entire workflow for data preprocessing, model development, and training. The notebook demonstrates the application of TensorFlow to create a robust classification model.  

### 2. **Model**  
- **Saved Model:** Includes the trained TensorFlow model saved as `1.keras`. This model is ready for inference and powers the backend prediction functionality.  

### 3. **API**  
- **`main.py`:** The main backend script, built with FastAPI, handles image uploads, processes input data, and delivers predictions using the trained model.  
- **`requirements.txt`:** Lists all dependencies required to run the backend code.  
- **Support Files:** Includes auto-generated files like `.ipynb_checkpoints` and `__pycache__`.  

### 4. **Web**  
- **Frontend Components:**  
  - `index.html`: The primary webpage for users to interact with the application.  
  - `style.css`: Defines the styling for a visually appealing and responsive design.  
  - `script.js`: Handles interactions between the user interface and the backend.  
  - Background image: Enhances the visual appeal of the application.  

## Key Features  
- **Model Training:** The Jupyter Notebook in the `training` folder demonstrates the full ML workflow from preprocessing to model creation and evaluation.  
- **Web Application:** A user-friendly interface for uploading potato leaf images and viewing predictions.  
- **Backend Integration:** Seamless connection between the frontend and the machine learning model via FastAPI.  
- **Trained Model:** The pre-trained model is optimized for classifying potato leaf health with high accuracy.  

## How to Use  
1. **Clone the Repository:**  
   ```bash  
   git clone https://github.com/Pooja1236/Potatoes-Disease-Prediction.git  
   cd Potato-Disease-Predictor  
2. **Install Dependencies:**
   Navigate to the api folder and install required libraries using:
   ```bash
   pip install -r requirements.txt  
3. **Run the Backend:**
   Start the FastAPI server by running main.py: 
   ```bash
   python main.py  
4. **Launch the Web Application:**
   Open index.html in a web browser to use the frontend interface.
   
## **Applications**
This project demonstrates the use of machine learning in agriculture, offering a practical solution for identifying diseases in potato crops. It can be adapted for other plant species and diseases with appropriate datasets.
