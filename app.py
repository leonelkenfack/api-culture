from flask import Flask, jsonify, request
from utils import RotationManager

app = Flask(__name__)
rotation_manager = RotationManager()

def get_cultures(family_name, region_name, climate_name):
    cultures_0 = rotation_manager.get_family_crops_in_region_and_climate(family_name, region_name, climate_name)
    cultures = [{'culture': culture, 'score': 3} for culture in cultures_0]
    if len(cultures) < 3:
        cultures_1 = rotation_manager.get_family_crops_in_region(family_name, region_name)
        for culture in cultures_1:
            if not any(c['culture'] == culture for c in cultures):
                cultures.append({'culture': culture, 'total_score': 2})
        if len(cultures) < 3:
            cultures_2 = rotation_manager.get_family_crops(family_name)     
            for culture in cultures_2:
                if not any(c['culture'] == culture for c in cultures):
                    cultures.append({'culture': culture, 'total_score': 1})
    return cultures

@app.route('/')
def home():
    return jsonify({
        "message": "Bienvenue sur l'API",
        "status": "success"
    })

@app.route('/api/rotation', methods=['POST'])
def get_rotation():
    data = request.json
    culture_name = data.get('culture_name')
    region_name = data.get('region_name')
    climate_name = data.get('climate_name')

    if not culture_name or not region_name or not climate_name:
        return jsonify({
            "message": "Les champs culture_name, region_name et climate_name sont requis",
            "status": "error"
        })

    family = rotation_manager.get_culture_family(culture_name)
    next_family = rotation_manager.get_next_family(family)
    cultures = get_cultures(next_family, region_name, climate_name)
    
    for culture in cultures:
        # culture['score'] = 0
        disease_created_percentage = rotation_manager.get_disease_created_impact_percentage(culture_name, culture['culture'])
        culture['total_score'] += disease_created_percentage/10
        culture['sensitivity_to_disease_created_percentage'] = disease_created_percentage
        disease_correction_percentage = rotation_manager.get_disease_correction_percentage(culture_name, culture['culture'])
        culture['total_score'] += disease_correction_percentage/10
        culture['created_disease_can_be_corrected_percentage'] = disease_correction_percentage
        nutrient_percentage_adds_to_consumes = rotation_manager.get_nutrient_percentage_adds_to_consumes(culture_name, culture['culture'])
        culture['total_score'] += nutrient_percentage_adds_to_consumes/20
        culture['nutrient_adds_can_be_consumed_percentage'] = nutrient_percentage_adds_to_consumes
        nutrient_percentage_consumes_to_adds = rotation_manager.get_nutrient_percentage_consumes_to_adds(culture_name, culture['culture'])
        culture['total_score'] += nutrient_percentage_consumes_to_adds/10
        culture['nutrient_consumes_can_be_added_percentage'] = nutrient_percentage_consumes_to_adds


    return jsonify({
        "cultures": cultures,
        "status": "success" if family else "not_found"
    })



if __name__ == '__main__':
    app.run(debug=True) 