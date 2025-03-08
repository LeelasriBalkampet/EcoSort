from flask import Flask, request, render_template, jsonify, url_for
import os
import uuid
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image
import tensorflow as tf

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Initialize model - this is placeholder code for a pre-trained waste classification model
# In a real implementation, you would load your trained model here
def load_model():
    # Placeholder for model loading
    # In production, replace this with actual model loading code
    # model = tf.keras.models.load_model('path_to_your_model')
    # return model
    return "model_placeholder"

# Global model instance
waste_model = load_model()

# Define waste categories and recycling information
waste_categories = {
    "Recyclable - Paper": {
        "recommendation": "Place in paper recycling bin. Make sure it's clean and dry.",
        "recycling_contact": "Paper Recycling Inc.: 555-123-4567 or visit www.paperrecycling.com"
    },
    "Recyclable - Plastic": {
        "recommendation": "Check for recycling symbol and place in plastic recycling bin.",
        "recycling_contact": "Plastic Recyclers United: 555-234-5678 or visit www.plasticrecyclers.com"
    },
    "Recyclable - Glass": {
        "recommendation": "Place in glass recycling bin. Remove any caps or lids.",
        "recycling_contact": "Glass Recycling Association: 555-345-6789 or visit www.glassrecycling.org"
    },
    "Recyclable - Metal": {
        "recommendation": "Place in metal recycling bin. Make sure it's clean.",
        "recycling_contact": "Metal Scrap Recyclers: 555-456-7890 or visit www.metalrecyclers.net"
    },
    "Compostable": {
        "recommendation": "Add to compost bin or green waste collection.",
        "recycling_contact": "Community Composting Program: 555-567-8901 or visit www.communitycompost.org"
    },
    "Hazardous Waste": {
        "recommendation": "Take to a hazardous waste collection center. Do not place in regular trash.",
        "recycling_contact": "Hazardous Waste Facility: 555-678-9012 or visit www.hazwastefacility.org"
    },
    "Non-Recyclable": {
        "recommendation": "This item cannot be recycled. Place in general waste.",
        "recycling_contact": "Waste Management: 555-789-0123 or visit www.wastemanagement.com"
    },
    "General Waste": {
        "recommendation": "Place in general waste bin if it cannot be recycled or composted.",
        "recycling_contact": "City Waste Services: 555-890-1234 or visit www.citywasteservices.gov"
    }
}

# Inspirational quotes about recycling
recycling_quotes = [
    "The greatest threat to our planet is the belief that someone else will save it.",
    "We don't need a handful of people doing zero waste perfectly. We need millions doing it imperfectly.",
    "There is no such thing as 'away'. When we throw anything away, it must go somewhere.",
    "Small acts, when multiplied by millions of people, can transform the world.",
    "Waste isn't waste until we waste it.",
    "The Earth is what we all have in common.",
    "Every time you recycle, the earth smiles a little.",
    "Recycling turns things into other things. Which is like magic!",
    "Nature never rushes, yet everything gets accomplished.",
    "Today's wasteful choices become tomorrow's problems.",
    "Be part of the solution, not part of the pollution.",
    "Reduce, reuse, recycle - it's not just a slogan, it's a way of life."
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_waste_from_image(image_path):
    """
    Predict waste category from image using ML model.
    This is a placeholder for actual image recognition.
    """
    # In a real implementation, you would:
    # 1. Load and preprocess the image
    # 2. Run it through your model
    # 3. Return the predicted class and confidence

    try:
        # Placeholder for image preprocessing
        img = Image.open(image_path)
        img = img.resize((224, 224))  # Example resize for model input
        
        # Simulate prediction (replace with actual model prediction)
        # In a real app, you would use your model:
        # prediction = waste_model.predict(processed_image)
        
        # For demonstration, we'll randomly select a category
        # In production, replace this with actual prediction logic
        import random
        categories = list(waste_categories.keys())
        category = random.choice(categories)
        confidence = random.uniform(0.7, 0.95)
        
        return category, confidence
        
    except Exception as e:
        print(f"Error in image prediction: {e}")
        return "General Waste", 0.6

def classify_waste(description, image_path=None):
    """
    Classify waste based on text description or image.
    Returns waste category, confidence score, and recycling contact.
    """
    # If image path is provided, use image classification
    if image_path:
        category, confidence = predict_waste_from_image(image_path)
        
    # Otherwise use text-based classification
    else:
        description = description.lower().strip()  # Normalize input

        # Classification rules with keywords
        categories = {
            "Recyclable - Paper": ["paper", "cardboard", "newspaper", "book", "magazine", "mail", "envelope", "flyer"],
            "Recyclable - Plastic": ["plastic", "bottle", "container", "packaging", "wrapper", "jug", "cup", "tub"],
            "Compostable": ["food", "vegetable", "fruit", "leftover", "peel", "coffee", "tea", "grain", "bread", "eggshell"],
            "Hazardous Waste": ["battery", "electronic", "phone", "computer", "chemical", "paint", "oil", "bulb", "medication"],
            "Recyclable - Glass": ["glass", "jar", "wine", "bottle", "vase", "mirror"],
            "Recyclable - Metal": ["metal", "aluminum", "can", "tin", "foil", "steel", "copper", "brass"],
            "Non-Recyclable": ["styrofoam", "bubble wrap", "tape", "wax paper", "straw", "plastic bag"],
            "General Waste": ["diaper", "tissue", "napkin", "towel", "cloth", "fabric"]
        }

        matched_category = None
        highest_match_count = 0  # To check which category has the most keyword matches
        confidence = 0.75  # Default confidence

        # Check for category match
        for category, keywords in categories.items():
            match_count = sum(1 for keyword in keywords if keyword in description)  # Count matches
            if match_count > highest_match_count:
                highest_match_count = match_count
                matched_category = category
                confidence = min(0.65 + (match_count * 0.1), 0.95)  # Increase confidence with more matches

        # If no match is found, default to General Waste
        category = matched_category if matched_category else "General Waste"

    # Get recycling information for the category
    category_info = waste_categories.get(category, waste_categories["General Waste"])
    
    # Return the result with recommendation and contact info
    return {
        "category": category, 
        "confidence": confidence,
        "recommendation": category_info["recommendation"],
        "recycling_contact": category_info["recycling_contact"]
    }

@app.route('/')
def home():
    # Get a random inspirational quote
    import random
    quote = random.choice(recycling_quotes)
    return render_template('index.html', quote=quote)

@app.route('/classify', methods=['POST'])
def classify():
    # For text-based classification
    if request.content_type == 'application/json':
        data = request.json
        waste_description = data.get('description', '')
        
        if not waste_description:
            return jsonify({"error": "No description provided"}), 400
        
        result = classify_waste(waste_description)
        return jsonify(result)
    
    # For image-based classification
    elif 'file' in request.files:
        file = request.files['file']
        
        # If no file selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        if file and allowed_file(file.filename):
            # Create unique filename
            original_filename = secure_filename(file.filename)
            extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{extension}"
            
            # Save the file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Use image for classification
            result = classify_waste(original_filename, file_path)
            
            # Add the image URL to the result
            result['image_url'] = url_for('static', filename=f'uploads/{unique_filename}')
            
            return jsonify(result)
        else:
            return jsonify({"error": "File type not allowed. Please upload a PNG, JPG, JPEG, or GIF"}), 400
    
    return jsonify({"error": "Invalid request"}), 400

if __name__ == '__main__':
    app.run(debug=True)