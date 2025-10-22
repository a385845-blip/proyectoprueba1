import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import requests
from utils.calculos_nutricionales import CalculadorNutricional
from utils.reglas_clinicas import ReglasClinicas

# Configuración de la página
st.set_page_config(
    page_title="Asistente Dietas Terapéuticas",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar estilos CSS
def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #FFF3CD;
        border-left: 5px solid #FFC107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #D1ECF1;
        border-left: 5px solid #17A2B8;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

class AsistenteDietasTerapeuticas:
    def _init_(self):
        self.calculador = CalculadorNutricional()
        self.reglas_clinicas = ReglasClinicas()
        self.load_data()
    
    def load_data(self):
        """Cargar datos de enfermedades, alimentos e interacciones"""
        try:
            # Datos de enfermedades y restricciones
            self.enfermedades_data = {
                "diabetes": {
                    "nombre": "Diabetes Mellitus",
                    "restricciones": ["azucar", "carbohidratos_simples"],
                    "nutrientes_control": ["carbohidratos", "azucar"],
                    "recomendaciones": "Control de carbohidratos, fibra alta"
                },
                "hipertension": {
                    "nombre": "Hipertensión Arterial",
                    "restricciones": ["sodio", "alcohol"],
                    "nutrientes_control": ["sodio", "potasio"],
                    "recomendaciones": "Dieta baja en sodio, rica en potasio"
                },
                "enfermedad_cardiaca": {
                    "nombre": "Enfermedad Cardíaca",
                    "restricciones": ["grasas_saturadas", "colesterol", "sodio"],
                    "nutrientes_control": ["grasas_saturadas", "colesterol", "fibra"],
                    "recomendaciones": "Grasas saludables, fibra alta"
                },
                "enfermedad_renal": {
                    "nombre": "Enfermedad Renal Crónica",
                    "restricciones": ["potasio", "fosforo", "proteina", "sodio"],
                    "nutrientes_control": ["proteina", "potasio", "fosforo"],
                    "recomendaciones": "Control de proteínas, potasio y fósforo"
                },
                "celiaquia": {
                    "nombre": "Enfermedad Celíaca",
                    "restricciones": ["gluten"],
                    "nutrientes_control": ["gluten"],
                    "recomendaciones": "Dieta sin gluten estricta"
                }
            }
            
            # Base de datos de alimentos (simplificada)
            self.alimentos_data = pd.DataFrame([
                {"alimento": "Manzana", "categoria": "fruta", "calorias": 52, "carbohidratos": 14, 
                 "proteina": 0.3, "grasa": 0.2, "fibra": 2.4, "azucar": 10, "sodio": 1, 
                 "potasio": 107, "fosforo": 11, "gluten": False},
                 
                {"alimento": "Pechuga de pollo", "categoria": "proteina", "calorias": 165, 
                 "carbohidratos": 0, "proteina": 31, "grasa": 3.6, "fibra": 0, "azucar": 0, 
                 "sodio": 74, "potasio": 256, "fosforo": 228, "gluten": False},
                 
                {"alimento": "Arroz integral", "categoria": "cereal", "calorias": 112, 
                 "carbohidratos": 23, "proteina": 2.6, "grasa": 0.9, "fibra": 1.8, "azucar": 0.4, 
                 "sodio": 1, "potasio": 43, "fosforo": 83, "gluten": False},
                 
                {"alimento": "Pan integral", "categoria": "cereal", "calorias": 265, 
                 "carbohidratos": 43, "proteina": 13, "grasa": 4.4, "fibra": 7.4, "azucar": 6.4, 
                 "sodio": 530, "potasio": 254, "fosforo": 310, "gluten": True},
                 
                {"alimento": "Salmón", "categoria": "proteina", "calorias": 208, 
                 "carbohidratos": 0, "proteina": 20, "grasa": 13, "fibra": 0, "azucar": 0, 
                 "sodio": 59, "potasio": 384, "fosforo": 250, "gluten": False},
                 
                {"alimento": "Espinacas", "categoria": "verdura", "calorias": 23, 
                 "carbohidratos": 3.6, "proteina": 2.9, "grasa": 0.4, "fibra": 2.2, "azucar": 0.4, 
                 "sodio": 79, "potasio": 558, "fosforo": 49, "gluten": False}
            ])
            
            # Interacciones alimento-medicamento
            self.interacciones_data = {
                "warfarina": ["espinacas", "brócoli", "col", "aguacate"],
                "digoxina": ["regaliz", "suplementos_potasio"],
                "litio": ["cafeina", "alcohol"],
                "estatinas": ["pomelo", "jugo_pomelo"],
                "levotiroxina": ["soja", "suplementos_fibra", "cafe"]
            }
            
        except Exception as e:
            st.error(f"Error cargando datos: {e}")
    
    def mostrar_interfaz_principal(self):
        """Interfaz principal de la aplicación"""
        st.markdown('<div class="main-header">🏥 Asistente para Dietas Terapéuticas</div>', 
                   unsafe_allow_html=True)
        
        # Sidebar con información del paciente
        with st.sidebar:
            st.header("👤 Información del Paciente")
            self.obtener_datos_paciente()
        
        # Pestañas principales
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Plan Alimentario", 
            "💊 Interacciones", 
            "🛒 Lista de Compras", 
            "📊 Seguimiento"
        ])
        
        with tab1:
            self.mostrar_plan_alimentario()
        
        with tab2:
            self.mostrar_interacciones()
        
        with tab3:
            self.mostrar_lista_compras()
        
        with tab4:
            self.mostrar_seguimiento()
    
    def obtener_datos_paciente(self):
        """Obtener información del paciente"""
        self.paciente = {}
        
        self.paciente['nombre'] = st.text_input("Nombre del paciente")
        self.paciente['edad'] = st.number_input("Edad", min_value=1, max_value=120, value=30)
        self.paciente['peso'] = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0)
        self.paciente['altura'] = st.number_input("Altura (cm)", min_value=100, max_value=220, value=170)
        self.paciente['actividad'] = st.selectbox(
            "Nivel de actividad",
            ["Sedentario", "Ligero", "Moderado", "Activo", "Muy activo"]
        )
        
        st.markdown("---")
        st.subheader("🩺 Condiciones de Salud")
        
        # Selección de enfermedades
        enfermedades_opciones = list(self.enfermedades_data.keys())
        self.paciente['enfermedades'] = st.multiselect(
            "Enfermedades diagnosticadas",
            options=enfermedades_opciones,
            format_func=lambda x: self.enfermedades_data[x]['nombre']
        )
        
        # Medicamentos
        medicamentos_opciones = list(self.interacciones_data.keys())
        self.paciente['medicamentos'] = st.multiselect(
            "Medicamentos actuales",
            options=medicamentos_opciones
        )
        
        # Preferencias alimentarias
        st.subheader("🍽️ Preferencias Alimentarias")
        self.paciente['preferencias'] = st.multiselect(
            "Preferencias dietéticas",
            ["Vegetariano", "Vegano", "Sin lactosa", "Bajo en sodio", "Sin gluten", "Ovolactovegetariano"]
        )
        
        # Alergias e intolerancias
        self.paciente['alergias'] = st.text_input("Alergias o intolerancias conocidas")
        
        # Disponibilidad local
        st.subheader("📍 Disponibilidad Local")
        self.paciente['region'] = st.selectbox(
            "Región/País",
            ["América Latina", "Europa", "Norteamérica", "Asia", "Oceanía", "África"]
        )
        
        if st.button("🔄 Generar Plan Alimentario", type="primary"):
            self.generar_plan_alimentario()
    
    def generar_plan_alimentario(self):
        """Generar plan alimentario personalizado"""
        if not hasattr(self, 'paciente') or not self.paciente.get('enfermedades'):
            st.warning("Por favor, complete la información del paciente y seleccione al menos una condición de salud.")
            return
        
        # Calcular requerimientos calóricos
        calorias = self.calculador.calcular_calorias(
            self.paciente['peso'], 
            self.paciente['altura'], 
            self.paciente['edad'],
            self.paciente['actividad']
        )
        
        # Aplicar restricciones según enfermedades
        alimentos_filtrados = self.alimentos_data.copy()
        restricciones = []
        
        for enfermedad in self.paciente['enfermedades']:
            info_enfermedad = self.enfermedades_data[enfermedad]
            restricciones.extend(info_enfermedad['restricciones'])
            
            # Aplicar filtros específicos por enfermedad
            if enfermedad == "diabetes":
                alimentos_filtrados = alimentos_filtrados[alimentos_filtrados['azucar'] <= 5]
            elif enfermedad == "hipertension":
                alimentos_filtrados = alimentos_filtrados[alimentos_filtrados['sodio'] <= 100]
            elif enfermedad == "enfermedad_renal":
                alimentos_filtrados = alimentos_filtrados[alimentos_filtrados['potasio'] <= 200]
        
        # Aplicar preferencias
        if "Sin gluten" in self.paciente.get('preferencias', []):
            alimentos_filtrados = alimentos_filtrados[~alimentos_filtrados['gluten']]
        
        if "Vegetariano" in self.paciente.get('preferencias', []):
            alimentos_filtrados = alimentos_filtrados[alimentos_filtrados['categoria'] != 'proteina_animal']
        
        self.plan_alimentario = {
            'calorias_diarias': calorias,
            'alimentos_recomendados': alimentos_filtrados,
            'restricciones': list(set(restricciones)),
            'fecha_generacion': datetime.now()
        }
        
        st.success("✅ Plan alimentario generado exitosamente!")
    
    def mostrar_plan_alimentario(self):
        """Mostrar el plan alimentario generado"""
        st.markdown('<div class="section-header">📋 Plan Alimentario Personalizado</div>', 
                   unsafe_allow_html=True)
        
        if not hasattr(self, 'plan_alimentario'):
            st.info("Complete la información del paciente y genere un plan alimentario.")
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Calorías diarias", f"{self.plan_alimentario['calorias_diarias']} kcal")
        
        with col2:
            st.metric("Alimentos recomendados", len(self.plan_alimentario['alimentos_recomendados']))
        
        with col3:
            st.metric("Restricciones aplicadas", len(self.plan_alimentario['restricciones']))
        
        # Mostrar alimentos recomendados por categoría
        st.subheader("🍎 Alimentos Recomendados")
        
        categorias = self.plan_alimentario['alimentos_recomendados']['categoria'].unique()
        
        for categoria in categorias:
            with st.expander(f"📁 {categoria.title()}"):
                alimentos_categoria = self.plan_alimentario['alimentos_recomendados'][
                    self.plan_alimentario['alimentos_recomendados']['categoria'] == categoria
                ]
                st.dataframe(alimentos_categoria, use_container_width=True)
        
        # Mostrar menú diario de ejemplo
        st.subheader("🍽️ Menú Diario de Ejemplo")
        self.mostrar_menu_ejemplo()
    
    def mostrar_menu_ejemplo(self):
        """Mostrar un menú diario de ejemplo"""
        if not hasattr(self, 'plan_alimentario'):
            return
        
        comidas = {
            "Desayuno": ["Manzana", "Avena", "Yogur"],
            "Almuerzo": ["Pechuga de pollo", "Arroz integral", "Espinacas"],
            "Cena": ["Salmón", "Ensalada verde", "Quinoa"],
            "Meriendas": ["Nueces", "Yogur griego", "Frutos rojos"]
        }
        
        for comida, alimentos in comidas.items():
            with st.expander(f"🍴 {comida}"):
                for alimento in alimentos:
                    if alimento in self.plan_alimentario['alimentos_recomendados']['alimento'].values:
                        st.write(f"✅ {alimento}")
                    else:
                        st.write(f"❌ {alimento} (no recomendado)")
    
    def mostrar_interacciones(self):
        """Mostrar interacciones alimento-medicamento"""
        st.markdown('<div class="section-header">💊 Interacciones Alimento-Medicamento</div>', 
                   unsafe_allow_html=True)
        
        if not hasattr(self, 'paciente') or not self.paciente.get('medicamentos'):
            st.info("No se han seleccionado medicamentos o no hay información del paciente.")
            return
        
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.subheader("⚠️ Advertencias de Interacciones")
        
        for medicamento in self.paciente['medicamentos']:
            if medicamento in self.interacciones_data:
                alimentos_interaccion = self.interacciones_data[medicamento]
                st.write(f"*{medicamento.title()}*: Evitar o limitar: {', '.join(alimentos_interaccion)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Recomendaciones generales
        st.subheader("📚 Recomendaciones Generales")
        st.write("""
        - Consulte siempre con su médico o farmacéutico sobre interacciones
        - Mantenga un horario consistente para medicamentos y alimentos
        - Reporte cualquier efecto secundario inmediatamente
        - No modifique su medicación sin supervisión médica
        """)
    
    def mostrar_lista_compras(self):
        """Generar lista de compras personalizada"""
        st.markdown('<div class="section-header">🛒 Lista de Compras Inteligente</div>', 
                   unsafe_allow_html=True)
        
        if not hasattr(self, 'plan_alimentario'):
            st.info("Genere primero un plan alimentario para ver la lista de compras.")
            return
        
        # Agrupar alimentos por categoría para la lista de compras
        categorias_compras = {
            "Frutas y Verduras": ["Manzana", "Espinacas", "Zanahoria", "Brócoli"],
            "Proteínas": ["Pechuga de pollo", "Salmón", "Huevos", "Tofu"],
            "Cereales y Granos": ["Arroz integral", "Quinoa", "Avena"],
            "Lácteos y Alternativas": ["Yogur griego", "Leche almendras", "Queso bajo en sodio"],
            "Grasas Saludables": ["Aguacate", "Nueces", "Aceite de oliva"]
        }
        
        for categoria, alimentos in categorias_compras.items():
            with st.expander(f"📦 {categoria}"):
                for alimento in alimentos:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(alimento)
                    with col2:
                        st.checkbox("Comprado", key=f"comprado_{alimento}")
        
        # Opción para exportar lista
        if st.button("📄 Exportar Lista de Compras"):
            st.success("Lista exportada (funcionalidad en desarrollo)")
    
    def mostrar_seguimiento(self):
        """Sistema de seguimiento del progreso"""
        st.markdown('<div class="section-header">📊 Seguimiento y Progreso</div>', 
                   unsafe_allow_html=True)
        
        st.subheader("📈 Métricas de Seguimiento")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            peso_actual = st.number_input("Peso actual (kg)", 
                                        min_value=30.0, 
                                        max_value=200.0, 
                                        value=70.0)
        
        with col2:
            presion_arterial = st.text_input("Presión arterial", "120/80")
        
        with col3:
            glucosa_ayunas = st.number_input("Glucosa en ayunas (mg/dL)", 
                                           min_value=50, 
                                           max_value=300, 
                                           value=90)
        
        # Registro de síntomas
        st.subheader("📝 Registro de Síntomas")
        sintomas = st.text_area("Describe cómo te sientes, síntomas, etc.")
        
        if st.button("💾 Guardar Registro"):
            st.success("Registro guardado exitosamente!")
        
        # Gráficos de progreso (placeholder)
        st.subheader("📊 Progreso en el Tiempo")
        st.info("Aquí se mostrarán gráficos de progreso (peso, niveles, etc.)")

def main():
    load_css()
    asistente = AsistenteDietasTerapéuticas()
    asistente.mostrar_interfaz_principal()

if _name_ == "_main_":
    main()
