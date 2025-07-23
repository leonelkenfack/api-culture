from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from utils import RotationManager
import numpy as np
import joblib
import pickle
from sklearn.preprocessing import OneHotEncoder


import pandas as pd

app = Flask(__name__)
api = Api(
    app,
    version='1.0',
    title='API de Rotation des Cultures',
    description='API pour analyser les rotations de cultures agricoles',
    doc='/api/doc'
)

ns = api.namespace('api/v1', description='Chemin api')

rotation_input = api.model('RotationInput', {
    'culture_name': fields.String(required=True, description='''Nom de la culture actuelle:
- Mais
- Mil
- Arachide
- Haricots
- Plantain
- Banane
- Manioc
- Igname
- Tomate
- Piment
- Aubergine
- Coton
- Tabac
- Sorgho
- Riz
- Niebe
- Voandzou
- Sesame
- Patate
- Taro
- Brachiaria
- Soja
- Mucuna
- Crotalaria
- Dolichos
- PalmierHuile
- Caoutchouc
- PommeDeTerre
- Poivre
- Okra
- Macabo
- Cacao
- Tournesol
- Ndole
- Mangue
- Papaye
- Ananas
- Avocat
- Basilic
- Gingembre
- Citronnelle
- Goyave
- Melon
- Pastèque
- Corossol
- Rambutan
- Mangoustan
'''),
    'region_name': fields.String(required=True, description='''Nom de la région :
- Nord (Adamaoua compris)
- Sud
- Centre
- Ouest
- Est
- NordOuest
- SudOuest
- ExtremeNord
- Littoral
- ZonesIrriguees'''),
    'climate_name': fields.String(required=True, 
        description="""Type de climat
- Tropical
- TropicalHumide
- TropicalSec
- SemiAride
- Temperé
- TemperéChaud
TropicalTemperé""")
})

culture_model = api.model('Culture', {
    'culture': fields.String(description='Nom de la culture'),
    'total_score': fields.Float(description='Score total de compatibilité'),
    'sensitivity_to_disease_created_percentage': fields.Float(description='Pourcentage de sensibilité aux maladies créées'),
    'created_disease_can_be_corrected_percentage': fields.Float(description='Pourcentage de maladies pouvant être corrigées'),
    'nutrient_adds_can_be_consumed_percentage': fields.Float(description='Pourcentage de nutriments ajoutés pouvant être consommés'),
    'nutrient_consumes_can_be_added_percentage': fields.Float(description='Pourcentage de nutriments consommés pouvant être ajoutés')
})

rotation_response = api.model('RotationResponse', {
    'cultures': fields.List(fields.Nested(culture_model)),
    'status': fields.String(description='Statut de la requête')
})

rotation_manager = RotationManager()

@ns.route('/rotation')
class Rotation(Resource):
    @ns.expect(rotation_input)
    @ns.marshal_with(rotation_response)
    @ns.doc('get_rotation',
            description='Obtient les cultures recommandées pour la rotation',
            responses={
                200: 'Succès',
                400: 'Paramètres invalides',
                404: 'Culture non trouvée'
            })
    def post(self):
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
        cultures = rotation_manager.get_cultures(next_family, region_name, climate_name)
        
        for culture in cultures:
            disease_created_percentage = rotation_manager.get_disease_created_impact_percentage(culture_name, culture['culture'])
            culture['total_score'] += (1 - disease_created_percentage/100)*0.325
            culture['sensitivity_to_disease_created_percentage'] = disease_created_percentage
            disease_correction_percentage = rotation_manager.get_disease_correction_percentage(culture_name, culture['culture'])
            culture['total_score'] += (disease_correction_percentage/100)*0.225
            culture['created_disease_can_be_corrected_percentage'] = disease_correction_percentage
            nutrient_percentage_adds_to_consumes = rotation_manager.get_nutrient_percentage_adds_to_consumes(culture_name, culture['culture'])
            culture['total_score'] += (nutrient_percentage_adds_to_consumes/100)*0.1
            culture['nutrient_adds_can_be_consumed_percentage'] = nutrient_percentage_adds_to_consumes
            nutrient_percentage_consumes_to_adds = rotation_manager.get_nutrient_percentage_consumes_to_adds(culture_name, culture['culture'])
            culture['total_score'] += (nutrient_percentage_consumes_to_adds/100)*0.15
            culture['nutrient_consumes_can_be_added_percentage'] = nutrient_percentage_consumes_to_adds

        return {
            "cultures": cultures,
            "status": "success" if family else "not_found"
        }

    
model = joblib.load('model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    
    # Convertir en DataFrame pour garder les noms de colonnes
    input_df = pd.DataFrame([data])

    # Prédiction
    prediction = model.predict(input_df)
    
    return jsonify({'prediction': prediction.tolist()})

if __name__ == '__main__':
    app.run(debug=True)