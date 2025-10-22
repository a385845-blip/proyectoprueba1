class CalculadorNutricional:
    """Clase para cálculos nutricionales personalizados"""
    
    def calcular_calorias(self, peso, altura, edad, actividad):
        """Calcular requerimientos calóricos basales"""
        # Fórmula Mifflin-St Jeor (aproximada)
        calorias_basal = 10 * peso + 6.25 * altura - 5 * edad + 5
        
        # Factor de actividad
        factores_actividad = {
            "Sedentario": 1.2,
            "Ligero": 1.375,
            "Moderado": 1.55,
            "Activo": 1.725,
            "Muy activo": 1.9
        }
        
        factor = factores_actividad.get(actividad, 1.2)
        return int(calorias_basal * factor)
    
    def calcular_macronutrientes(self, calorias, enfermedades):
        """Calcular distribución de macronutrientes según condiciones"""
        base_ratio = {"proteinas": 0.20, "carbohidratos": 0.50, "grasas": 0.30}
        
        # Ajustes según enfermedades
        if "diabetes" in enfermedades:
            base_ratio["carbohidratos"] = 0.40
            base_ratio["grasas"] = 0.35
            base_ratio["proteinas"] = 0.25
        
        if "enfermedad_renal" in enfermedades:
            base_ratio["proteinas"] = 0.15
            base_ratio["carbohidratos"] = 0.60
        
        return {
            "proteinas_g": int((calorias * base_ratio["proteinas"]) / 4),
            "carbohidratos_g": int((calorias * base_ratio["carbohidratos"]) / 4),
            "grasas_g": int((calorias * base_ratio["grasas"]) / 9)
        }
