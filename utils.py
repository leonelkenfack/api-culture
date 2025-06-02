from SPARQLWrapper import SPARQLWrapper, JSON
import json
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

class RotationManager:
    def __init__(self, endpoint_url=None):
        """
        Initialise le gestionnaire de rotation
        
        Args:
            endpoint_url (str, optional): URL de l'endpoint SPARQL de GraphDB. Si non spécifié, utilise la variable d'environnement GRAPHDB_URL.
        """
        if endpoint_url is None:
            endpoint_url = os.getenv('GRAPHDB_URL')
            if endpoint_url is None:
                raise ValueError("GRAPHDB_URL n'est pas définie dans le fichier .env")
        
        self.sparql = SPARQLWrapper(endpoint_url)
        self.sparql.setReturnFormat(JSON)

    def get_next_family(self, family_name):
        """
        Obtient la famille suivante d'une famille donnée
        
        Args:
            family_name (str): Nom de la famille (ex: "Fabacees")
        
        Returns:
            str: Nom de la famille suivante ou None si non trouvée
        """

        query = f"""
            PREFIX cultures: <http://example.org/cultures#>
            SELECT ?nextFamily
            WHERE {{
                cultures:{family_name} cultures:isFollowedBy ?nextFamily .
            }}
        """
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        
        for result in results["results"]["bindings"]:
            next_family = result["nextFamily"]["value"].split("#")[-1]
            return next_family
        return None

    def get_culture_family(self, culture_name):
        """
        Obtient la famille d'une culture donnée
        
        Args:
            culture_name (str): Nom de la culture (ex: "Mais")
        
        Returns:
            str: Nom de la famille ou None si non trouvée
        """
        query = f"""
            PREFIX cultures: <http://example.org/cultures#>
            SELECT ?family
            WHERE {{
                cultures:{culture_name} cultures:belongsToFamily ?family .
            }}
        """
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        
        for result in results["results"]["bindings"]:
            family = result["family"]["value"].split("#")[-1]
            return family
        return None

    def get_family_crops(self, family_name):
        """
        Obtient toutes les cultures appartenant à une famille donnée
        
        Args:
            family_name (str): Nom de la famille (ex: "Fabacees")
        
        Returns:
            list: Liste des noms des cultures appartenant à la famille
        """
        query = f"""
            PREFIX cultures: <http://example.org/cultures#>
            SELECT ?crop
            WHERE {{
                ?crop cultures:belongsToFamily cultures:{family_name} .
            }}
            ORDER BY ?crop
        """
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        
        crops = []
        for result in results["results"]["bindings"]:
            crop = result["crop"]["value"].split("#")[-1]
            crops.append(crop)
        return crops

    def get_family_crops_in_region(self, family_name, region_name):
        """
        Obtient les cultures d'une famille dans une région spécifique
        
        Args:
            family_name (str): Nom de la famille (ex: "Fabacees")
            region_name (str): Nom de la région (ex: "Nord")
        
        Returns:
            list: Liste des noms des cultures appartenant à la famille dans la région
        """
        query = f"""
            PREFIX cultures: <http://example.org/cultures#>
            SELECT ?crop
            WHERE {{
                ?crop cultures:belongsToFamily cultures:{family_name} ;
                      cultures:grownInRegion cultures:{region_name} .
            }}
            ORDER BY ?crop
        """
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        
        crops = []
        for result in results["results"]["bindings"]:
            crop = result["crop"]["value"].split("#")[-1]
            crops.append(crop)
        return crops

    def get_family_crops_in_region_and_climate(self, family_name, region_name, climate_name):
        """
        Obtient les cultures d'une famille dans une région et un climat spécifiques
        
        Args:
            family_name (str): Nom de la famille (ex: "Fabacees")
            region_name (str): Nom de la région (ex: "Nord")
            climate_name (str): Nom du climat (ex: "TropicalSec")
        
        Returns:
            list: Liste des noms des cultures appartenant à la famille dans la région et le climat
        """
        query = f"""
            PREFIX cultures: <http://example.org/cultures#>
            SELECT ?crop
            WHERE {{
                ?crop cultures:belongsToFamily cultures:{family_name} ;
                      cultures:grownInRegion cultures:{region_name} ;
                      cultures:hasClimate cultures:{climate_name} .
            }}
            ORDER BY ?crop
        """
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        
        crops = []
        for result in results["results"]["bindings"]:
            crop = result["crop"]["value"].split("#")[-1]
            crops.append(crop)
        return crops

    def get_nutrient_percentage_adds_to_consumes(self, crop1_name, crop2_name):
        """
        Calcule le pourcentage de nutriments ajoutés par rapport aux nutriments consommés entre deux cultures
        
        Args:
            crop1_name (str): Nom de la première culture (qui consomme des nutriments)
            crop2_name (str): Nom de la deuxième culture (qui ajoute des nutriments)
        
        Returns:
            float: Pourcentage de nutriments ajoutés par rapport aux nutriments consommés
        """
        query = f"""
            PREFIX cultures: <http://example.org/cultures#>

            SELECT 
                   ((COUNT(DISTINCT ?nutrient2) * 100.0 / COUNT(DISTINCT ?nutrient1)) as ?percentage)
            WHERE {{
                # Première culture et ses nutriments consommés
                ?crop1 cultures:consumesNutrient ?nutrient1 .
                
                # Deuxième culture et ses nutriments ajoutés
                ?crop2 cultures:addsNutrient ?nutrient2 .
                
                # On filtre nutrient2 pour garder uniquement ceux qui sont dans nutrient1
                ?crop1 cultures:consumesNutrient ?nutrient2 .
                
                # On spécifie les deux cultures
                VALUES ?crop1 {{ cultures:{crop1_name} }}
                VALUES ?crop2 {{ cultures:{crop2_name} }}
            }}
            GROUP BY ?crop1 ?crop2
        """
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        
        for result in results["results"]["bindings"]:
            percentage = float(result["percentage"]["value"])
            return percentage
        return 0.0

    def get_nutrient_percentage_consumes_to_adds(self, crop1_name, crop2_name):
        """
        Calcule le pourcentage de nutriments consommés par rapport aux nutriments ajoutés entre deux cultures
        
        Args:
            crop1_name (str): Nom de la première culture (qui ajoute des nutriments)
            crop2_name (str): Nom de la deuxième culture (qui consomme des nutriments)
        
        Returns:
            float: Pourcentage de nutriments consommés par rapport aux nutriments ajoutés
        """
        query = f"""
            PREFIX cultures: <http://example.org/cultures#>

            SELECT 
                   ((COUNT(DISTINCT ?nutrient1) * 100.0 / COUNT(DISTINCT ?nutrient2)) as ?percentage)
            WHERE {{
                # Première culture et ses nutriments ajoutés
                ?crop1 cultures:addsNutrient ?nutrient1 .
                
                # Deuxième culture et ses nutriments consommés
                ?crop2 cultures:consumesNutrient ?nutrient2 .
                
                # On filtre nutrient2 pour garder uniquement ceux qui sont dans nutrient1
                ?crop1 cultures:consumesNutrient ?nutrient2 .
                
                # On spécifie les deux cultures
                VALUES ?crop1 {{ cultures:{crop1_name} }}
                VALUES ?crop2 {{ cultures:{crop2_name} }}
            }}
            GROUP BY ?crop1 ?crop2
        """
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        
        for result in results["results"]["bindings"]:
            percentage = float(result["percentage"]["value"])
            return percentage
        return 0.0

    def get_disease_created_impact_percentage(self, crop1_name, crop2_name):
        """
        Calcule le pourcentage de maladies communes entre deux cultures
        
        Args:
            crop1_name (str): Nom de la première culture (qui peut créer des maladies)
            crop2_name (str): Nom de la deuxième culture (qui est sensible aux maladies)
        
        Returns:
            float: Pourcentage de maladies communes (arrondi à 2 décimales)
        """
        query = f"""
            PREFIX cultures: <http://example.org/cultures#>

            SELECT (ROUND((COUNT(DISTINCT ?commonDisease) * 100.0 / COUNT(DISTINCT ?diseaseCreated)) * 100) / 100 AS ?percentage)
            WHERE {{
                # Première culture qui peut créer des maladies
                ?crop1 cultures:canCreateDisease ?diseaseCreated .
                
                # Deuxième culture qui est sensible à certaines maladies
                ?crop2 cultures:sensitiveToDisease ?commonDisease .
                
                # Les maladies en commun (créées par la première et auxquelles la deuxième est sensible)
                ?crop1 cultures:canCreateDisease ?commonDisease .
                
                # Paramètres pour les cultures spécifiques
                VALUES ?crop1 {{ cultures:{crop1_name} }}
                VALUES ?crop2 {{ cultures:{crop2_name} }}
            }}
            GROUP BY ?crop1 ?crop2
        """
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        
        for result in results["results"]["bindings"]:
            percentage = float(result["percentage"]["value"])
            return (-1)*percentage
        return 0.0

    def get_disease_correction_percentage(self, crop1_name, crop2_name):
        """
        Calcule le pourcentage de maladies créées par une culture que l'autre peut corriger
        
        Args:
            crop1_name (str): Nom de la première culture (qui peut créer des maladies)
            crop2_name (str): Nom de la deuxième culture (qui peut corriger des maladies)
        
        Returns:
            float: Pourcentage de maladies corrigées (arrondi à 2 décimales)
        """
        query = f"""
            PREFIX cultures: <http://example.org/cultures#>

            SELECT (ROUND((COUNT(DISTINCT ?commonDisease) * 100.0 / COUNT(DISTINCT ?diseaseCreated)) * 100) / 100 AS ?percentage)
            WHERE {{
                # Première culture qui peut créer des maladies
                ?crop1 cultures:canCreateDisease ?diseaseCreated .
                
                # Deuxième culture qui peut corriger certaines maladies
                ?crop2 cultures:canCorrectDisease ?commonDisease .
                
                # Les maladies en commun (créées par la première et que la deuxième peut corriger)
                ?crop1 cultures:canCreateDisease ?commonDisease .
                
                # Paramètres pour les cultures spécifiques
                VALUES ?crop1 {{ cultures:{crop1_name} }}
                VALUES ?crop2 {{ cultures:{crop2_name} }}
            }}
            GROUP BY ?crop1 ?crop2
        """
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        
        for result in results["results"]["bindings"]:
            percentage = float(result["percentage"]["value"])
            return percentage
        return 0.0


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le gestionnaire
    rotation_manager = RotationManager(endpoint_url="http://localhost:7200/repositories/cultures")
    
    # Test 6: Calculer le pourcentage de nutriments
    percentage = rotation_manager.get_nutrient_percentage_adds_to_consumes("Mais", "Melon")
    print(f"Le pourcentage de nutriments ajoutés par le Mil par rapport aux nutriments consommés par le Mais est : {percentage:.2f}%")
    
    # Test 7: Calculer le pourcentage inverse de nutriments
    inverse_percentage = rotation_manager.get_nutrient_percentage_consumes_to_adds("Mais", "Melon")
    print(f"Le pourcentage de nutriments consommés par le Mil par rapport aux nutriments ajoutés par le Mais est : {inverse_percentage:.2f}%")
    
    # Test 8: Calculer le pourcentage de maladies communes
    disease_percentage = rotation_manager.get_disease_created_impact_percentage("Mais", "Melon")
    print(f"Le pourcentage de maladies communes entre le Mais et le Mil est : {disease_percentage:.2f}%")
    
    # Test 9: Calculer le pourcentage de maladies corrigées
    correction_percentage = rotation_manager.get_disease_correction_percentage("Mais", "Melon")
    print(f"Le pourcentage de maladies créées par le Mais que le Mil peut corriger est : {correction_percentage:.2f}%")
    